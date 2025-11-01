#!/usr/bin/env python3
"""
ConvHi Widgets System - Sistema de widgets personalitzables
Suport per integració HTML, personalització visual i variables dinàmiques
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime
from enum import Enum\n\nfrom .convhi_widget import DEFAULT_BACKEND_URL

logger = logging.getLogger("veuplus.widgets")

router = APIRouter(prefix="/api/convhi/widgets", tags=["ConvHi Widgets"])

# Enums
class WidgetVariant(str, Enum):
    COMPACT = "compact"
    EXPANDED = "expanded"
    FULLSCREEN = "fullscreen"

class WidgetMode(str, Enum):
    VOICE_ONLY = "voice_only"
    VOICE_TEXT = "voice_text"
    CHAT_ONLY = "chat_only"

# Models
class WidgetConfig(BaseModel):
    agent_id: str
    variant: WidgetVariant = WidgetVariant.COMPACT
    mode: WidgetMode = WidgetMode.VOICE_ONLY
    
    # Personalització visual
    avatar_image_url: Optional[str] = None
    avatar_orb_color_1: str = "#6DB035"
    avatar_orb_color_2: str = "#F5CABB"
    primary_color: str = "#3B82F6"
    secondary_color: str = "#1E40AF"
    
    # Personalització de text
    action_text: str = "Need assistance?"
    start_call_text: str = "Begin conversation"
    end_call_text: str = "End call"
    expand_text: str = "Open chat"
    listening_text: str = "Listening..."
    speaking_text: str = "Assistant speaking"
    
    # Configuració avançada
    dynamic_variables: Dict[str, Any] = {}
    overrides: Dict[str, Any] = {}
    language: Optional[str] = None
    server_location: str = "us"
    
    # Funcionalitats
    feedback_enabled: bool = True
    terms_enabled: bool = False
    terms_content: Optional[str] = None
    terms_storage_key: Optional[str] = None
    mute_enabled: bool = True
    
    created_at: str
    updated_at: str

class WidgetEmbedRequest(BaseModel):
    agent_id: str
    config: Optional[Dict[str, Any]] = None
    domain: Optional[str] = None
    payload: Optional[str] = None
    signature: Optional[str] = None
    backend_url: Optional[str] = None

class WidgetEmbedResponse(BaseModel):
    embed_code: str
    widget_config: Dict[str, Any]
    preview_url: str

# In-memory storage
widget_configs = {}

class WidgetEngine:
    def __init__(self):
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Inicialitzar configuracions de widget per defecte"""
        logger.info("✅ Widget Engine inicialitzat")
    
    async def create_widget_config(self, config: WidgetConfig) -> bool:
        """Crear configuració de widget"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            widget_configs[config.agent_id] = config.dict()
            
            logger.info(f"✅ Widget configurat per agent: {config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant configuració de widget: {e}")
            return False
    
    async def generate_embed_code(self, request: WidgetEmbedRequest) -> WidgetEmbedResponse:
        """Generar codi d'integració HTML"""
        try:
            # Obtenir configuració de l'agent
            config_data = widget_configs.get(request.agent_id, {})
            if not config_data:
                # Crear configuració per defecte
                default_config = WidgetConfig(
                    agent_id=request.agent_id,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                config_data = default_config.dict()
                widget_configs[request.agent_id] = config_data
            
            # Aplicar configuracions personalitzades
            if request.config:
                config_data.update(request.config)
            
            # Generar codi HTML
            embed_code = self._generate_html_code(config_data, request.domain, request.payload, request.signature, request.backend_url)
            
            # Generar URL de preview
            preview_url = f"https://veuplus.com/widget/preview/{request.agent_id}"
            
            return WidgetEmbedResponse(
                embed_code=embed_code,
                widget_config=config_data,
                preview_url=preview_url
            )
            
        except Exception as e:
            logger.error(f"Error generant codi d'integració: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _generate_html_code(
        self,
        config: Dict[str, Any],
        domain: Optional[str] = None,
        payload: Optional[str] = None,
        signature: Optional[str] = None,
        backend_url: Optional[str] = None,
    ) -> str:
        """Generar codi HTML del widget amb dades signades."""

        backend = (backend_url or domain or DEFAULT_BACKEND_URL).rstrip("/")

        widget_attrs = [
            f'agent-id="{config["agent_id"]}"',
            f'variant="{config["variant"]}"',
            f'mode="{config["mode"]}"',
            f'primary-color="{config["primary_color"]}"',
            f'secondary-color="{config["secondary_color"]}"',
            f'action-text="{config["action_text"]}"',
            f'start-call-text="{config["start_call_text"]}"',
            f'end-call-text="{config["end_call_text"]}"',
            f'expand-text="{config["expand_text"]}"',
            f'listening-text="{config["listening_text"]}"',
            f'speaking-text="{config["speaking_text"]}"',
        ]

        if config.get("avatar_image_url"):
            widget_attrs.append(f'avatar-image-url="{config["avatar_image_url"]}"')
        else:
            widget_attrs.append(f'avatar-orb-color-1="{config["avatar_orb_color_1"]}"')
            widget_attrs.append(f'avatar-orb-color-2="{config["avatar_orb_color_2"]}"')

        if config.get("dynamic_variables"):
            dynamic_vars = json.dumps(config["dynamic_variables"])
            widget_attrs.append(f'dynamic-variables=\'{dynamic_vars}\'')

        if config.get("overrides"):
            for key, value in config["overrides"].items():
                widget_attrs.append(f'override-{key}="{value}"')

        if config.get("language"):
            widget_attrs.append(f'language="{config["language"]}"')

        data_attrs = [
            f'data-backend-url="{backend}"',
            f'data-agent-id="{config["agent_id"]}"',
        ]
        if payload and signature:
            data_attrs.append(f'data-payload="{payload}"')
            data_attrs.append(f'data-signature="{signature}"')

        script_candidates = [
            f"{backend}/static/convhi-widget.js",
            f"{backend}/static/dist/convhi-widget.js",
            "http://localhost:3000/convhi-widget.js",
        ]

        loader_lines = [
            "<script>",
            "  (function(){",
            "    var urls = [" + ",".join(f'\"{url}\"' for url in script_candidates) + "];",
            "    for (var i = 0; i < urls.length; i++){",
            "      var src = urls[i];",
            "      if (!src) continue;",
            "      var script = document.createElement('script');",
            "      script.src = src;",
            "      script.async = true;",
            "      script.type = 'text/javascript';",
            "      document.head.appendChild(script);",
            "      break;",
            "    }",
            "  })();",
            "</script>",
        ]

        html_code = (
            "<!-- VeuPlus ConvHi Widget -->\n"
            f"<veuplus-convhi {' '.join(widget_attrs)} {' '.join(data_attrs)}></veuplus-convhi>\n"
            + "\n".join(loader_lines)
            + "\n<!-- End VeuPlus ConvHi Widget -->"
        )

        return html_code
    
    def get_widget_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir configuració de widget per agent"""
        return widget_configs.get(agent_id)
    
    async def update_widget_config(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Actualitzar configuració de widget"""
        try:
            if agent_id not in widget_configs:
                return False
            
            config_data = widget_configs[agent_id]
            config_data.update(updates)
            config_data["updated_at"] = datetime.now().isoformat()
            
            widget_configs[agent_id] = config_data
            
            logger.info(f"✅ Widget actualitzat per agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualitzant widget: {e}")
            return False

# Instància global
widget_engine = WidgetEngine()

# Endpoints
@router.post("/config")
async def create_widget_config(config: WidgetConfig):
    """Crear configuració de widget"""
    try:
        success = await widget_engine.create_widget_config(config)
        
        if success:
            return {
                "success": True,
                "message": f"Widget configurat per agent {config.agent_id}",
                "config": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant configuració de widget")
        
    except Exception as e:
        logger.error(f"Error creant configuració de widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed")
async def generate_embed_code(request: WidgetEmbedRequest):
    """Generar codi d'integració HTML"""
    try:
        response = await widget_engine.generate_embed_code(request)
        
        return {
            "success": True,
            "embed_code": response.embed_code,
            "widget_config": response.widget_config,
            "preview_url": response.preview_url
        }
        
    except Exception as e:
        logger.error(f"Error generant codi d'integració: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/{agent_id}")
async def get_widget_config(agent_id: str):
    """Obtenir configuració de widget"""
    try:
        config = widget_engine.get_widget_config(agent_id)
        
        if config:
            return {
                "success": True,
                "config": config
            }
        else:
            return {
                "success": False,
                "message": "Configuració de widget no trobada"
            }
        
    except Exception as e:
        logger.error(f"Error obtenint configuració de widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/{agent_id}")
async def update_widget_config(agent_id: str, updates: Dict[str, Any]):
    """Actualitzar configuració de widget"""
    try:
        success = await widget_engine.update_widget_config(agent_id, updates)
        
        if success:
            return {
                "success": True,
                "message": f"Widget actualitzat per agent {agent_id}",
                "config": widget_engine.get_widget_config(agent_id)
            }
        else:
            raise HTTPException(status_code=404, detail="Configuració de widget no trobada")
        
    except Exception as e:
        logger.error(f"Error actualitzant configuració de widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{agent_id}")
async def widget_preview(agent_id: str):
    """Preview del widget"""
    try:
        config = widget_engine.get_widget_config(agent_id)
        
        if not config:
            # Crear configuració per defecte
            default_config = WidgetConfig(
                agent_id=agent_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            config = default_config.dict()
        
        # Generar HTML de preview
        preview_html = f'''
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeuPlus ConvHi Widget Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .preview-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .widget-demo {{
            border: 2px dashed #ccc;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h1>VeuPlus ConvHi Widget Preview</h1>
        <p>Agent ID: <strong>{agent_id}</strong></p>
        
        <div class="widget-demo">
            <h3>Widget Demo</h3>
            <p>Aquí apareixeria el widget ConvHi</p>
            <div style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(45deg, {config['avatar_orb_color_1']}, {config['avatar_orb_color_2']});
                margin: 20px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            ">
                🤖
            </div>
            <button style="
                background: {config['primary_color']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            ">
                {config['action_text']}
            </button>
        </div>
        
        <h3>Configuració Actual</h3>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto;">
{json.dumps(config, indent=2, ensure_ascii=False)}
        </pre>
    </div>
</body>
</html>'''
        
        return {
            "success": True,
            "preview_html": preview_html
        }
        
    except Exception as e:
        logger.error(f"Error generant preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def widget_health():
    """Health check del sistema de widgets"""
    return {
        "status": "ok",
        "message": "Sistema de widgets funcionant",
        "stats": {
            "total_configs": len(widget_configs),
            "available_variants": [variant.value for variant in WidgetVariant],
            "available_modes": [mode.value for mode in WidgetMode]
        }
    }



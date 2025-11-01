#!/usr/bin/env python3
"""
VeuPlus Server - Net i Funcional
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("veuplus")

# Crear app FastAPI
app = FastAPI(
    title="VeuPlus API",
    description="Plataforma completa de síntesi de veu i agents conversacionals",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
try:
    from api.edge_tts import edge_router
    app.include_router(edge_router)
    logger.info("✅ Edge-TTS router carregat")
except ImportError as e:
    logger.warning(f"⚠️ Edge-TTS router no disponible: {e}")

try:
    from api.catalan_tts import catalan_router
    app.include_router(catalan_router)
    logger.info("✅ Catalan router carregat")
except ImportError as e:
    logger.warning(f"⚠️ Catalan router no disponible: {e}")

try:
    from api.alia import router as alia_router
    app.include_router(alia_router)
    logger.info("✅ ALIA router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ALIA router no disponible: {e}")

try:
    from api.unified_voices import router as unified_voices_router
    app.include_router(unified_voices_router)
    logger.info("✅ Unified voices router carregat")
except ImportError as e:
    logger.warning(f"⚠️ Unified voices router no disponible: {e}")

try:
    from api.voicebots_external import router as voicebots_router
    app.include_router(voicebots_router)
    logger.info("✅ Voicebots router carregat")
except ImportError as e:
    logger.warning(f"⚠️ Voicebots router no disponible: {e}")

try:
    from api.simple_chatbots import router as simple_chatbots_router
    app.include_router(simple_chatbots_router)
    logger.info("✅ Simple chatbots router carregat")
except ImportError as e:
    logger.warning(f"⚠️ Simple chatbots router no disponible: {e}")

try:
    from api.llm_providers import router as llm_providers_router
    app.include_router(llm_providers_router)
    logger.info("✅ LLM providers router carregat")
except ImportError as e:
    logger.warning(f"⚠️ LLM providers router no disponible: {e}")

try:
    from api.convhi_agents import router as convhi_router
    app.include_router(convhi_router)
    logger.info("✅ ConvHi agents router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi agents router no disponible: {e}")

try:
    from api.convhi_analytics import router as convhi_analytics_router
    app.include_router(convhi_analytics_router)
    logger.info("✅ ConvHi analytics router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi analytics router no disponible: {e}")

try:
    from api.convhi_knowledge import router as convhi_knowledge_router
    app.include_router(convhi_knowledge_router)
    logger.info("✅ ConvHi knowledge router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi knowledge router no disponible: {e}")

try:
    from api.convhi_tools import router as convhi_tools_router
    app.include_router(convhi_tools_router)
    logger.info("✅ ConvHi tools router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi tools router no disponible: {e}")

try:
    from api.llm_config import router as llm_config_router
    app.include_router(llm_config_router)
    logger.info("✅ LLM config router carregat")
except ImportError as e:
    logger.warning(f"⚠️ LLM config router no disponible: {e}")

try:
    from api.convhi_workflows import router as convhi_workflows_router
    app.include_router(convhi_workflows_router)
    logger.info("✅ ConvHi workflows router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi workflows router no disponible: {e}")

try:
    from api.convhi_connections import router as convhi_connections_router
    app.include_router(convhi_connections_router)
    logger.info("✅ ConvHi connections router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi connections router no disponible: {e}")

try:
    from api.convhi_voice_config import router as convhi_voice_config_router
    app.include_router(convhi_voice_config_router)
    logger.info("✅ ConvHi voice config router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi voice config router no disponible: {e}")

try:
    from api.convhi_language import router as convhi_language_router
    app.include_router(convhi_language_router)
    logger.info("✅ ConvHi language router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi language router no disponible: {e}")

try:
    from api.convhi_widgets import router as convhi_widgets_router
    app.include_router(convhi_widgets_router)
    logger.info("✅ ConvHi widgets router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi widgets router no disponible: {e}")

try:
    from api.convhi_sip import router as convhi_sip_router
    app.include_router(convhi_sip_router)
    logger.info("✅ ConvHi SIP router carregat")
except ImportError as e:
    logger.warning(f"⚠️ ConvHi SIP router no disponible: {e}")

try:
    from api.sip_endpoints import sip_router
    app.include_router(sip_router)
    logger.info("✅ SIP endpoints router carregat")
except ImportError as e:
    logger.warning(f"⚠️ SIP endpoints router no disponible: {e}")

# Endpoints bàsics
@app.get("/")
async def root():
    return {"message": "VeuPlus API funcionant", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "VeuPlus funcionant"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "message": "VeuPlus API funcionant"}

@app.post("/api/edge-tts/synthesize-direct")
async def synthesize_edge_tts_direct(request: Request):
    """Endpoint directe Edge-TTS"""
    try:
        data = await request.json()
        text = data.get("text", "Hola prova")
        voice_id = data.get("voice_id", "es-ES-ElviraNeural")
        
        print(f"🎵 DIRECT: Generant '{text}' amb '{voice_id}'")
        
        import edge_tts
        import base64
        import tempfile
        import os
        
        communicate = edge_tts.Communicate(text, voice_id)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        await communicate.save(temp_path)
        
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
        audio_base64 = base64.b64encode(audio_data).decode()
            os.unlink(temp_path)
            
        print(f"✅ DIRECT: Àudio generat {len(audio_data)} bytes")
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "text": text,
                "voice_id": voice_id,
            "size": len(audio_data)
            }
                
        except Exception as e:
        print(f"❌ DIRECT Error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    logger.info("🚀 Arrencant VeuPlus Server...")
    logger.info("📍 URL: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
API Unificada de Veus
Endpoints per obtenir totes les veus disponibles de tots els sistemes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from pathlib import Path
import json

logger = logging.getLogger("veuplus.unified_voices")

router = APIRouter(prefix="/api/voices", tags=["Unified Voices"])

@router.get("/all")
async def get_all_voices():
    """Obtenir totes les veus disponibles de tots els sistemes"""
    try:
        all_voices = []
        
        # Sistema 1: Edge-TTS (561 veus)
        try:
            import edge_tts
            edge_voices = await edge_tts.list_voices()
            
            for voice in edge_voices:
                all_voices.append({
                    "id": voice.get("ShortName", voice.get("Name", "")),
                    "name": voice.get("DisplayName", voice.get("FriendlyName", voice.get("LocalName", ""))),
                    "gender": voice.get("Gender", "Unknown"),
                    "language": voice.get("Locale", "").split("-")[0] if voice.get("Locale") else "unknown",
                    "locale": voice.get("Locale", ""),
                    "system": "edge-tts",
                    "system_name": "Sistema 1: Edge-TTS Standard",
                    "description": f"{voice.get('LocalName', '')} - {voice.get('Locale', '')}",
                    "voice_type": "edge_standard",
                    "source": "microsoft_edge_tts",
                    "quality": "standard"
                })
        except Exception as e:
            logger.warning(f"Error getting Edge-TTS voices: {e}")
        
        # Sistema 2: Català Hiperrealista (4 veus)
        catalan_voices = [
            {
                "id": "senyor_catala_1",
                "name": "Senyor Català Hiperrealista 1",
                "gender": "male",
                "language": "ca",
                "locale": "ca-ES",
                "system": "catalan",
                "system_name": "Sistema 2: Català Edge+SEGRE",
                "description": "Voz masculina catalana natural, acento Barcelona",
                "voice_type": "catalan_hyperrealistic",
                "source": "edge_tts_catalan_segre",
                "quality": "catalan_optimized_segre",
                "segre_enabled": True
            },
            {
                "id": "dona_catalana",
                "name": "Dona Catalana Hiperrealista",
                "gender": "female",
                "language": "ca",
                "locale": "ca-ES",
                "system": "catalan",
                "system_name": "Sistema 2: Català Edge+SEGRE",
                "description": "Voz femenina catalana natural, acento Barcelona",
                "voice_type": "catalan_hyperrealistic",
                "source": "edge_tts_catalan_segre",
                "quality": "catalan_optimized_segre",
                "segre_enabled": True
            },
            {
                "id": "senyor_catala_2",
                "name": "Senyor Català Hiperrealista 2",
                "gender": "male",
                "language": "ca",
                "locale": "ca-ES",
                "system": "catalan",
                "system_name": "Sistema 2: Català Edge+SEGRE",
                "description": "Voz masculina catalana expresiva, acento Barcelona",
                "voice_type": "catalan_hyperrealistic",
                "source": "edge_tts_catalan_segre",
                "quality": "catalan_optimized_segre",
                "segre_enabled": True
            },
            {
                "id": "senyor_catala_extended",
                "name": "Senyor Català Hiperrealista Extended",
                "gender": "male",
                "language": "ca",
                "locale": "ca-ES",
                "system": "catalan",
                "system_name": "Sistema 2: Català Edge+SEGRE",
                "description": "Voz masculina catalana política, acento Barcelona, tono formal",
                "voice_type": "catalan_hyperrealistic",
                "source": "edge_tts_catalan_segre",
                "quality": "catalan_optimized_segre",
                "segre_enabled": True
            }
        ]
        all_voices.extend(catalan_voices)
        
        # Sistema 3: ALIA BSC Premium (4 veus)
        alia_voices = [
            {
                "id": "ca-ES-AlbaNeural",
                "name": "Alba Premium (Català)",
                "gender": "female",
                "language": "ca",
                "locale": "ca-ES",
                "system": "alia",
                "system_name": "Sistema 3: ALIA BSC Premium",
                "description": "Voz femenina catalana premium con SEGRE",
                "voice_type": "alia_premium",
                "source": "alia_bsc_premium",
                "quality": "alia_premium_cooficial",
                "segre_enabled": True,
                "dialects": ["central", "valencian"]
            },
            {
                "id": "es-ES-AlvaroNeural",
                "name": "Álvaro Premium (Español)",
                "gender": "male",
                "language": "es",
                "locale": "es-ES",
                "system": "alia",
                "system_name": "Sistema 3: ALIA BSC Premium",
                "description": "Voz masculina española premium",
                "voice_type": "alia_premium",
                "source": "alia_bsc_premium",
                "quality": "alia_premium_cooficial",
                "segre_enabled": False
            },
            {
                "id": "eu-ES-AinhoaNeural",
                "name": "Ainhoa Premium (Euskera)",
                "gender": "female",
                "language": "eu",
                "locale": "eu-ES",
                "system": "alia",
                "system_name": "Sistema 3: ALIA BSC Premium",
                "description": "Voz femenina vasca premium",
                "voice_type": "alia_premium",
                "source": "alia_bsc_premium",
                "quality": "alia_premium_cooficial",
                "segre_enabled": False
            },
            {
                "id": "gl-ES-SabelaNeural",
                "name": "Sabela Premium (Galego)",
                "gender": "female",
                "language": "gl",
                "locale": "gl-ES",
                "system": "alia",
                "system_name": "Sistema 3: ALIA BSC Premium",
                "description": "Voz femenina gallega premium",
                "voice_type": "alia_premium",
                "source": "alia_bsc_premium",
                "quality": "alia_premium_cooficial",
                "segre_enabled": False
            }
        ]
        all_voices.extend(alia_voices)

        # Trained voices (published only)
        try:
            publish_file = Path("backend/voice_models/published.json")
            published_ids: List[str] = []
            if publish_file.exists():
                with open(publish_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        published_ids = [str(x) for x in data.get('published', [])]
                    elif isinstance(data, list):
                        published_ids = [str(x) for x in data]

            for vid in published_ids:
                meta_path = Path("backend/training_data") / vid / "metadata.json"
                metadata = {}
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r', encoding='utf-8') as mf:
                            metadata = json.load(mf)
                    except Exception:
                        metadata = {}
                all_voices.append({
                    "id": vid,
                    "name": f"{metadata.get('id', vid).replace('_',' ').title()} (Entrenada)",
                    "gender": metadata.get("gender", "unknown"),
                    "language": metadata.get("language", "ca"),
                    "locale": metadata.get("locale", "ca-ES"),
                    "system": "catalan",
                    "system_name": "Sistema 2: Catal�� Edge+SEGRE",
                    "description": metadata.get("description", "Voz catalana entrenada"),
                    "voice_type": "trained_real",
                    "source": "real_recordings",
                    "quality": "hyperrealistic_trained",
                    "trained": True
                })
        except Exception as e:
            logger.warning(f"Failed to add published trained voices: {e}")
        
        # Estadístiques
        stats = {
            "total_voices": len(all_voices),
            "by_system": {
                "edge-tts": len([v for v in all_voices if v["system"] == "edge-tts"]),
                "catalan": len([v for v in all_voices if v["system"] == "catalan"]),
                "alia": len([v for v in all_voices if v["system"] == "alia"])
            },
            "by_language": {},
            "by_gender": {
                "male": len([v for v in all_voices if v["gender"] == "male"]),
                "female": len([v for v in all_voices if v["gender"] == "female"])
            }
        }
        
        # Comptar per idioma
        for voice in all_voices:
            lang = voice["language"]
            stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1
        
        logger.info(f"✅ Totes les veus obtingudes: {len(all_voices)} veus totals")
        
        return {
            "success": True,
            "voices": all_voices,
            "stats": stats,
            "systems": {
                "edge-tts": "Sistema 1: Edge-TTS Standard (~561 veus globals)",
                "catalan": "Sistema 2: Català Edge+SEGRE (4 veus catalanes)",
                "alia": "Sistema 3: ALIA BSC Premium (4 veus cooficials)"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-system/{system}")
async def get_voices_by_system(system: str):
    """Obtenir veus per sistema específic"""
    try:
        if system not in ["edge-tts", "catalan", "alia"]:
            raise HTTPException(status_code=400, detail="Invalid system. Use: edge-tts, catalan, or alia")
        
        all_voices_response = await get_all_voices()
        all_voices = all_voices_response["voices"]
        
        system_voices = [voice for voice in all_voices if voice["system"] == system]
        
        return {
            "success": True,
            "system": system,
            "voices": system_voices,
            "count": len(system_voices)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voices by system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-language/{language}")
async def get_voices_by_language(language: str):
    """Obtenir veus per idioma específic"""
    try:
        all_voices_response = await get_all_voices()
        all_voices = all_voices_response["voices"]
        
        language_voices = [voice for voice in all_voices if voice["language"] == language]
        
        return {
            "success": True,
            "language": language,
            "voices": language_voices,
            "count": len(language_voices)
        }
        
    except Exception as e:
        logger.error(f"Error getting voices by language: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_voices(query: str = "", system: str = "", language: str = "", gender: str = ""):
    """Cercar veus per criteris"""
    try:
        all_voices_response = await get_all_voices()
        all_voices = all_voices_response["voices"]
        
        filtered_voices = all_voices
        
        # Filtrar per query
        if query:
            filtered_voices = [
                voice for voice in filtered_voices
                if query.lower() in voice["name"].lower() or 
                   query.lower() in voice["description"].lower()
            ]
        
        # Filtrar per sistema
        if system:
            filtered_voices = [voice for voice in filtered_voices if voice["system"] == system]
        
        # Filtrar per idioma
        if language:
            filtered_voices = [voice for voice in filtered_voices if voice["language"] == language]
        
        # Filtrar per gènere
        if gender:
            filtered_voices = [voice for voice in filtered_voices if voice["gender"] == gender]
        
        return {
            "success": True,
            "query": query,
            "filters": {
                "system": system,
                "language": language,
                "gender": gender
            },
            "voices": filtered_voices,
            "count": len(filtered_voices)
        }
        
    except Exception as e:
        logger.error(f"Error searching voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]

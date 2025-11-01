"""
API per SIP Trunk i Agent Intel·ligent
Endpoints per integració telefònica completa
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import base64
import tempfile
import os

logger = logging.getLogger("veuplus.sip_agent")

router = APIRouter(prefix="/api/sip", tags=["SIP Agent"])

# Imports
try:
    from sip_trunk_integration import sip_trunk_integration
    from knowledge_base_agent import knowledge_base_agent
    SIP_AVAILABLE = True
except ImportError as e:
    logger.error(f"SIP integration not available: {e}")
    SIP_AVAILABLE = False


class SIPCallRequest(BaseModel):
    caller_id: str
    called_number: str
    language: str = "ca"
    voice_system: str = "catalan"
    greeting_text: Optional[str] = None


class SIPVoiceRequest(BaseModel):
    call_id: str
    audio_base64: str
    language: str = "ca"
    voice_system: str = "catalan"


class SIPContinueRequest(BaseModel):
    call_id: str


@router.post("/handle-call")
async def handle_incoming_call(request: SIPCallRequest):
    """
    Gestionar trucada entrant
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        logger.info(f"📞 Trucada entrant: {request.caller_id} -> {request.called_number}")
        
        result = await sip_trunk_integration.handle_incoming_call(
            caller_id=request.caller_id,
            called_number=request.called_number,
            language=request.language,
            voice_system=request.voice_system,
            greeting_text=request.greeting_text
        )
        
        if result.get("success"):
            # Llegir àudio generat i retornar com base64
            audio_path = result.get("greeting_audio_path", "")
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                
                audio_base64 = base64.b64encode(audio_data).decode()
                
                return {
                    "success": True,
                    "call_id": result["call_id"],
                    "greeting_audio_base64": audio_base64,
                    "language": result["language"],
                    "voice_system": result["voice_system"],
                    "greeting_text": result["greeting_text"]
                }
            else:
                raise HTTPException(status_code=500, detail="Greeting audio not generated")
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SIP call handling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-voice")
async def process_voice_input(request: SIPVoiceRequest):
    """
    Processar entrada de veu (ASR + LLM + TTS)
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        logger.info(f"🎤 Processant veu: {request.call_id}")
        
        # Guardar àudio temporalment
        audio_data = base64.b64decode(request.audio_base64)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)
        
        try:
            result = await sip_trunk_integration.process_voice_input(
                call_id=request.call_id,
                audio_file_path=temp_path,
                language=request.language,
                voice_system=request.voice_system
            )
            
            if result.get("success"):
                # Llegir àudio de resposta i retornar com base64
                response_audio_path = result.get("response_audio_path", "")
                if response_audio_path and os.path.exists(response_audio_path):
                    with open(response_audio_path, "rb") as f:
                        response_audio_data = f.read()
                    
                    response_audio_base64 = base64.b64encode(response_audio_data).decode()
                    
                    return {
                        "success": True,
                        "call_id": result["call_id"],
                        "user_input": result["user_input"],
                        "agent_response": result["agent_response"],
                        "response_audio_base64": response_audio_base64,
                        "language": result["language"],
                        "voice_system": result["voice_system"]
                    }
                else:
                    raise HTTPException(status_code=500, detail="Response audio not generated")
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
                
        finally:
            # Netejar fitxer temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SIP voice processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/should-continue")
async def should_continue_conversation(request: SIPContinueRequest):
    """
    Determinar si continuar conversa
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        logger.info(f"🤔 Verificant si continuar: {request.call_id}")
        
        # Obtenir històric de conversa
        conversation_history = knowledge_base_agent.get_conversation_history(request.call_id)
        
        # Lògica simple: continuar si hi ha menys de 10 intercanvis
        should_continue = len(conversation_history) < 10
        
        # Verificar si l'última resposta indica finalització
        if conversation_history:
            last_response = conversation_history[-1]["agent_response"].lower()
            end_indicators = ["adeu", "fins aviat", "que tinguis", "adiós", "hasta luego", "goodbye"]
            
            if any(indicator in last_response for indicator in end_indicators):
                should_continue = False
        
        return {
            "success": True,
            "continue": should_continue,
            "conversation_turns": len(conversation_history),
            "call_id": request.call_id
        }
        
    except Exception as e:
        logger.error(f"SIP continue check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuration")
async def get_sip_configuration():
    """
    Obtenir configuració SIP
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        config = sip_trunk_integration.get_sip_configuration()
        return {
            "success": True,
            "configuration": config
        }
    except Exception as e:
        logger.error(f"SIP configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-knowledge")
async def add_knowledge(
    category: str,
    question: str,
    answer: str,
    language: str = "ca",
    confidence: float = 1.0
):
    """
    Afegir coneixement a la base
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        success = knowledge_base_agent.add_knowledge(
            category=category,
            question=question,
            answer=answer,
            language=language,
            confidence=confidence
        )
        
        if success:
            return {
                "success": True,
                "message": "Coneixement afegit correctament"
            }
        else:
            raise HTTPException(status_code=500, detail="Error afegint coneixement")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge addition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-stats")
async def get_knowledge_stats():
    """
    Obtenir estadístiques de coneixement
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        stats = knowledge_base_agent.get_knowledge_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Knowledge stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation-history/{call_id}")
async def get_conversation_history(call_id: str):
    """
    Obtenir històric de conversa
    """
    if not SIP_AVAILABLE:
        raise HTTPException(status_code=503, detail="SIP integration not available")
    
    try:
        history = knowledge_base_agent.get_conversation_history(call_id)
        return {
            "success": True,
            "call_id": call_id,
            "conversation_history": history,
            "total_turns": len(history)
        }
    except Exception as e:
        logger.error(f"Conversation history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]

# Optional: in-memory IP allowlist management endpoints
@router.get("/allowlist")
async def get_allowlist():
    try:
        items = [s.strip() for s in os.environ.get("SIP_IP_ALLOWLIST", "").split(",") if s.strip()]
        return {"success": True, "allowlist": items}
    except Exception as e:
        logger.error(f"SIP allowlist get error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class AllowlistUpdate(BaseModel):
    items: Optional[list[str]] = None

@router.post("/allowlist")
async def set_allowlist(update: AllowlistUpdate):
    try:
        items = update.items or []
        os.environ["SIP_IP_ALLOWLIST"] = ",".join(items)
        return {"success": True, "allowlist": items}
    except Exception as e:
        logger.error(f"SIP allowlist set error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

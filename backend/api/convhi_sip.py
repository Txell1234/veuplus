#!/usr/bin/env python3
"""
ConvHi SIP Trunking System - Sistema de connexió SIP
Suport per integració amb sistemes telefònics existents
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger("veuplus.sip")

router = APIRouter(prefix="/api/convhi/sip", tags=["ConvHi SIP Trunking"])

# Enums
class TransportType(str, Enum):
    TCP = "tcp"
    TLS = "tls"

class MediaEncryption(str, Enum):
    DISABLED = "disabled"
    ALLOWED = "allowed"
    REQUIRED = "required"

class AuthenticationType(str, Enum):
    DIGEST = "digest"
    ACL = "acl"

# Models
class SIPTrunkConfig(BaseModel):
    id: str
    label: str
    phone_number: str  # E.164 format
    agent_id: str
    
    # Configuració de transport
    transport_type: TransportType = TransportType.TCP
    media_encryption: MediaEncryption = MediaEncryption.ALLOWED
    
    # Configuració sortint
    outbound_address: str
    outbound_transport: TransportType = TransportType.TCP
    outbound_media_encryption: MediaEncryption = MediaEncryption.ALLOWED
    
    # Autenticació
    auth_type: AuthenticationType = AuthenticationType.ACL
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Headers personalitzats
    custom_headers: Dict[str, str] = {}
    
    # Configuració avançada
    codec_preference: List[str] = ["G711", "G722"]
    max_concurrent_calls: int = 10
    call_timeout: int = 300  # segons
    
    # Metadades
    created_at: str
    updated_at: str
    status: str = "active"

class SIPCallRequest(BaseModel):
    from_number: str
    to_number: str
    agent_id: str
    custom_headers: Dict[str, str] = {}
    dynamic_variables: Dict[str, Any] = {}

class SIPCallResponse(BaseModel):
    call_id: str
    status: str
    sip_uri: str
    estimated_duration: Optional[int] = None

# In-memory storage
sip_trunks = {}
active_calls = {}

class SIPEngine:
    def __init__(self):
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Inicialitzar configuracions SIP per defecte"""
        logger.info("✅ SIP Engine inicialitzat")
    
    async def create_sip_trunk(self, config: SIPTrunkConfig) -> bool:
        """Crear configuració de trunk SIP"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            sip_trunks[config.id] = config.dict()
            
            logger.info(f"✅ Trunk SIP creat: {config.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant trunk SIP: {e}")
            return False
    
    async def initiate_call(self, request: SIPCallRequest) -> SIPCallResponse:
        """Iniciar trucada SIP"""
        try:
            import uuid
            
            call_id = str(uuid.uuid4())
            
            # Generar SIP URI
            sip_uri = f"sip:{request.to_number}@sip.veuplus.com:5060"
            
            # Registrar trucada activa
            active_calls[call_id] = {
                "call_id": call_id,
                "from_number": request.from_number,
                "to_number": request.to_number,
                "agent_id": request.agent_id,
                "status": "initiating",
                "started_at": datetime.now().isoformat(),
                "custom_headers": request.custom_headers,
                "dynamic_variables": request.dynamic_variables
            }
            
            # Simular inici de trucada
            logger.info(f"📞 Iniciant trucada SIP: {call_id}")
            
            return SIPCallResponse(
                call_id=call_id,
                status="initiating",
                sip_uri=sip_uri,
                estimated_duration=300
            )
            
        except Exception as e:
            logger.error(f"Error iniciant trucada SIP: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_sip_trunk(self, trunk_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir configuració de trunk SIP"""
        return sip_trunks.get(trunk_id)
    
    def get_all_trunks(self) -> List[Dict[str, Any]]:
        """Obtenir tots els trunks SIP"""
        return list(sip_trunks.values())
    
    async def update_sip_trunk(self, trunk_id: str, updates: Dict[str, Any]) -> bool:
        """Actualitzar configuració de trunk SIP"""
        try:
            if trunk_id not in sip_trunks:
                return False
            
            config_data = sip_trunks[trunk_id]
            config_data.update(updates)
            config_data["updated_at"] = datetime.now().isoformat()
            
            sip_trunks[trunk_id] = config_data
            
            logger.info(f"✅ Trunk SIP actualitzat: {trunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualitzant trunk SIP: {e}")
            return False
    
    def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir estat de trucada"""
        return active_calls.get(call_id)
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Obtenir trucades actives"""
        return list(active_calls.values())

# Instància global
sip_engine = SIPEngine()

# Endpoints
@router.post("/trunks")
async def create_sip_trunk(config: SIPTrunkConfig):
    """Crear configuració de trunk SIP"""
    try:
        success = await sip_engine.create_sip_trunk(config)
        
        if success:
            return {
                "success": True,
                "message": f"Trunk SIP creat: {config.id}",
                "config": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant trunk SIP")
        
    except Exception as e:
        logger.error(f"Error creant trunk SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trunks")
async def get_sip_trunks():
    """Obtenir tots els trunks SIP"""
    try:
        trunks = sip_engine.get_all_trunks()
        
        return {
            "success": True,
            "trunks": trunks,
            "total": len(trunks)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint trunks SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trunks/{trunk_id}")
async def get_sip_trunk(trunk_id: str):
    """Obtenir configuració de trunk SIP"""
    try:
        config = sip_engine.get_sip_trunk(trunk_id)
        
        if config:
            return {
                "success": True,
                "config": config
            }
        else:
            raise HTTPException(status_code=404, detail="Trunk SIP no trobat")
        
    except Exception as e:
        logger.error(f"Error obtenint trunk SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/trunks/{trunk_id}")
async def update_sip_trunk(trunk_id: str, updates: Dict[str, Any]):
    """Actualitzar configuració de trunk SIP"""
    try:
        success = await sip_engine.update_sip_trunk(trunk_id, updates)
        
        if success:
            return {
                "success": True,
                "message": f"Trunk SIP actualitzat: {trunk_id}",
                "config": sip_engine.get_sip_trunk(trunk_id)
            }
        else:
            raise HTTPException(status_code=404, detail="Trunk SIP no trobat")
        
    except Exception as e:
        logger.error(f"Error actualitzant trunk SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calls")
async def initiate_sip_call(request: SIPCallRequest):
    """Iniciar trucada SIP"""
    try:
        response = await sip_engine.initiate_call(request)
        
        return {
            "success": True,
            "call_id": response.call_id,
            "status": response.status,
            "sip_uri": response.sip_uri,
            "estimated_duration": response.estimated_duration
        }
        
    except Exception as e:
        logger.error(f"Error iniciant trucada SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calls")
async def get_active_calls():
    """Obtenir trucades actives"""
    try:
        calls = sip_engine.get_active_calls()
        
        return {
            "success": True,
            "calls": calls,
            "total": len(calls)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint trucades actives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calls/{call_id}")
async def get_call_status(call_id: str):
    """Obtenir estat de trucada"""
    try:
        call_status = sip_engine.get_call_status(call_id)
        
        if call_status:
            return {
                "success": True,
                "call": call_status
            }
        else:
            raise HTTPException(status_code=404, detail="Trucada no trobada")
        
    except Exception as e:
        logger.error(f"Error obtenint estat de trucada: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trunks/{trunk_id}/test")
async def test_trunk(trunk_id: str):
    """Provar trunk SIP"""
    try:
        config = sip_engine.get_sip_trunk(trunk_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Trunk SIP no trobat")
        
        # Simular test de connexió
        import asyncio
        await asyncio.sleep(0.5)  # Simular latency
        
        # Check if trunk exists and is active
        if config.get("status") == "active":
            return {
                "success": True,
                "trunk_id": trunk_id,
                "status": "connected",
                "latency": 25,  # ms simulated
                "message": "Trunk SIP connectat correctament"
            }
        else:
            return {
                "success": False,
                "error": "Trunk SIP inactiu",
                "trunk_id": trunk_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error provant trunk SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/trunks/{trunk_id}")
async def delete_sip_trunk(trunk_id: str):
    """Eliminar trunk SIP"""
    try:
        if trunk_id in sip_trunks:
            del sip_trunks[trunk_id]
            logger.info(f"Trunk SIP eliminat: {trunk_id}")
            return {
                "success": True,
                "message": f"Trunk SIP eliminat: {trunk_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="Trunk SIP no trobat")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminant trunk SIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def sip_health():
    """Health check del sistema SIP"""
    return {
        "status": "ok",
        "message": "Sistema SIP funcionant",
        "stats": {
            "total_trunks": len(sip_trunks),
            "active_calls": len(active_calls),
            "supported_transports": [transport.value for transport in TransportType],
            "supported_encryption": [encryption.value for encryption in MediaEncryption]
        }
    }

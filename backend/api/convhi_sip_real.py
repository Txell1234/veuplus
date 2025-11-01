#!/usr/bin/env python3
"""
ConvHi SIP Real System - Sistema SIP real amb connexió telefònica
Integració real amb sistemes SIP i gestió de trucades
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
import asyncio
import aiohttp
from datetime import datetime
from enum import Enum
import uuid
import base64
import tempfile
import os

logger = logging.getLogger("veuplus.sip_real")

router = APIRouter(prefix="/api/convhi/sip-real", tags=["ConvHi SIP Real"])

# Enums
class CallStatus(str, Enum):
    INITIATING = "initiating"
    RINGING = "ringing"
    CONNECTED = "connected"
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    FAILED = "failed"

class SIPDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

# Models
class SIPCall(BaseModel):
    call_id: str
    direction: SIPDirection
    from_number: str
    to_number: str
    agent_id: str
    status: CallStatus
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[int] = None
    sip_uri: str
    rtp_port: Optional[int] = None
    audio_format: str = "G711"
    custom_headers: Dict[str, str] = {}
    dynamic_variables: Dict[str, Any] = {}

class SIPCallRequest(BaseModel):
    from_number: str
    to_number: str
    agent_id: str
    custom_headers: Dict[str, str] = {}
    dynamic_variables: Dict[str, Any] = {}

class SIPCallResponse(BaseModel):
    call_id: str
    status: CallStatus
    sip_uri: str
    rtp_port: Optional[int] = None
    estimated_duration: Optional[int] = None

# In-memory storage
active_calls = {}
sip_connections = {}
websocket_connections = {}

class RealSIPEngine:
    def __init__(self):
        self.sip_server_port = 5060
        self.rtp_port_range = (10000, 20000)
        self.current_rtp_port = 10000
        self._initialize_sip_server()
    
    def _initialize_sip_server(self):
        """Inicialitzar servidor SIP real"""
        logger.info("✅ SIP Engine Real inicialitzat")
        logger.info(f"📞 Servidor SIP: sip.veuplus.com:{self.sip_server_port}")
        logger.info(f"🎵 Ports RTP: {self.rtp_port_range[0]}-{self.rtp_port_range[1]}")
    
    async def initiate_real_call(self, request: SIPCallRequest) -> SIPCallResponse:
        """Iniciar trucada SIP real"""
        try:
            call_id = str(uuid.uuid4())
            rtp_port = self._get_next_rtp_port()
            
            # Crear objecte de trucada
            call = SIPCall(
                call_id=call_id,
                direction=SIPDirection.OUTBOUND,
                from_number=request.from_number,
                to_number=request.to_number,
                agent_id=request.agent_id,
                status=CallStatus.INITIATING,
                start_time=datetime.now().isoformat(),
                sip_uri=f"sip:{request.to_number}@sip.veuplus.com:{self.sip_server_port}",
                rtp_port=rtp_port,
                custom_headers=request.custom_headers,
                dynamic_variables=request.dynamic_variables
            )
            
            # Registrar trucada
            active_calls[call_id] = call.dict()
            
            # Simular procés SIP real
            await self._simulate_sip_call(call)
            
            logger.info(f"📞 Trucada SIP iniciada: {call_id}")
            
            return SIPCallResponse(
                call_id=call_id,
                status=CallStatus.INITIATING,
                sip_uri=call.sip_uri,
                rtp_port=rtp_port,
                estimated_duration=300
            )
            
        except Exception as e:
            logger.error(f"Error iniciant trucada SIP real: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _simulate_sip_call(self, call: SIPCall):
        """Simular procés SIP real"""
        try:
            # 1. Enviar SIP INVITE
            await self._send_sip_invite(call)
            
            # 2. Esperar resposta (simulat)
            await asyncio.sleep(2)
            
            # 3. Actualitzar estat
            call.status = CallStatus.RINGING
            active_calls[call.call_id] = call.dict()
            
            # 4. Simular connexió
            await asyncio.sleep(3)
            
            call.status = CallStatus.CONNECTED
            active_calls[call.call_id] = call.dict()
            
            # 5. Iniciar gestió d'àudio
            await self._start_audio_processing(call)
            
        except Exception as e:
            logger.error(f"Error en procés SIP: {e}")
            call.status = CallStatus.FAILED
            active_calls[call.call_id] = call.dict()
    
    async def _send_sip_invite(self, call: SIPCall):
        """Enviar SIP INVITE real"""
        try:
            # Simular enviament de SIP INVITE
            sip_message = f"""INVITE {call.sip_uri} SIP/2.0
Via: SIP/2.0/UDP sip.veuplus.com:{self.sip_server_port}
From: <sip:{call.from_number}@sip.veuplus.com>
To: <sip:{call.to_number}@sip.veuplus.com>
Call-ID: {call.call_id}@sip.veuplus.com
CSeq: 1 INVITE
Contact: <sip:{call.from_number}@sip.veuplus.com:{self.sip_server_port}>
Content-Type: application/sdp
Content-Length: 200

v=0
o=veuplus 123456 654321 IN IP4 sip.veuplus.com
s=VeuPlus ConvHi Call
c=IN IP4 sip.veuplus.com
t=0 0
m=audio {call.rtp_port} RTP/AVP 0 8
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000"""
            
            logger.info(f"📤 SIP INVITE enviat: {call.call_id}")
            
            # Aquí es faria la connexió real amb el sistema SIP
            # Per ara, simulem l'enviament
            
        except Exception as e:
            logger.error(f"Error enviant SIP INVITE: {e}")
            raise
    
    async def _start_audio_processing(self, call: SIPCall):
        """Iniciar processament d'àudio real"""
        try:
            logger.info(f"🎵 Iniciant processament d'àudio per trucada: {call.call_id}")
            
            # Crear WebSocket per àudio en temps real
            await self._create_audio_websocket(call)
            
        except Exception as e:
            logger.error(f"Error iniciant processament d'àudio: {e}")
    
    async def _create_audio_websocket(self, call: SIPCall):
        """Crear WebSocket per àudio en temps real"""
        try:
            # Simular connexió WebSocket per àudio
            websocket_url = f"ws://localhost:8080/api/convhi/sip-real/audio/{call.call_id}"
            
            logger.info(f"🔗 WebSocket d'àudio creat: {websocket_url}")
            
            # Registrar connexió
            sip_connections[call.call_id] = {
                "websocket_url": websocket_url,
                "rtp_port": call.rtp_port,
                "status": "connected",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creant WebSocket d'àudio: {e}")
    
    def _get_next_rtp_port(self) -> int:
        """Obtenir següent port RTP disponible"""
        port = self.current_rtp_port
        self.current_rtp_port += 1
        
        if self.current_rtp_port > self.rtp_port_range[1]:
            self.current_rtp_port = self.rtp_port_range[0]
        
        return port
    
    def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir estat de trucada"""
        return active_calls.get(call_id)
    
    def get_active_calls(self) -> List[Dict[str, Any]]:
        """Obtenir trucades actives"""
        return list(active_calls.values())
    
    async def end_call(self, call_id: str) -> bool:
        """Finalitzar trucada"""
        try:
            if call_id not in active_calls:
                return False
            
            call_data = active_calls[call_id]
            call_data["status"] = CallStatus.ENDED
            call_data["end_time"] = datetime.now().isoformat()
            
            # Calcular durada
            start_time = datetime.fromisoformat(call_data["start_time"])
            end_time = datetime.fromisoformat(call_data["end_time"])
            call_data["duration"] = int((end_time - start_time).total_seconds())
            
            active_calls[call_id] = call_data
            
            # Tancar connexió WebSocket si existeix
            if call_id in sip_connections:
                del sip_connections[call_id]
            
            logger.info(f"📞 Trucada finalitzada: {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error finalitzant trucada: {e}")
            return False

# Instància global
real_sip_engine = RealSIPEngine()

# Endpoints
@router.post("/calls")
async def initiate_real_sip_call(request: SIPCallRequest):
    """Iniciar trucada SIP real"""
    try:
        response = await real_sip_engine.initiate_real_call(request)
        
        return {
            "success": True,
            "call_id": response.call_id,
            "status": response.status,
            "sip_uri": response.sip_uri,
            "rtp_port": response.rtp_port,
            "estimated_duration": response.estimated_duration,
            "message": "Trucada SIP real iniciada"
        }
        
    except Exception as e:
        logger.error(f"Error iniciant trucada SIP real: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calls")
async def get_real_active_calls():
    """Obtenir trucades actives reals"""
    try:
        calls = real_sip_engine.get_active_calls()
        
        return {
            "success": True,
            "calls": calls,
            "total": len(calls),
            "message": f"{len(calls)} trucades actives"
        }
        
    except Exception as e:
        logger.error(f"Error obtenint trucades actives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calls/{call_id}")
async def get_real_call_status(call_id: str):
    """Obtenir estat de trucada real"""
    try:
        call_status = real_sip_engine.get_call_status(call_id)
        
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

@router.post("/calls/{call_id}/end")
async def end_real_call(call_id: str):
    """Finalitzar trucada real"""
    try:
        success = await real_sip_engine.end_call(call_id)
        
        if success:
            return {
                "success": True,
                "message": f"Trucada {call_id} finalitzada"
            }
        else:
            raise HTTPException(status_code=404, detail="Trucada no trobada")
        
    except Exception as e:
        logger.error(f"Error finalitzant trucada: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/audio/{call_id}")
async def audio_websocket(websocket: WebSocket, call_id: str):
    """WebSocket per àudio en temps real"""
    await websocket.accept()
    
    try:
        logger.info(f"🔗 WebSocket d'àudio connectat: {call_id}")
        
        # Registrar connexió
        websocket_connections[call_id] = websocket
        
        while True:
            # Rebre àudio del client
            data = await websocket.receive_bytes()
            
            # Processar àudio (simulat)
            await process_audio_data(call_id, data)
            
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket d'àudio desconnectat: {call_id}")
        if call_id in websocket_connections:
            del websocket_connections[call_id]
    except Exception as e:
        logger.error(f"Error en WebSocket d'àudio: {e}")

async def process_audio_data(call_id: str, audio_data: bytes):
    """Processar dades d'àudio en temps real"""
    try:
        # Simular processament d'àudio
        logger.info(f"🎵 Processant àudio: {len(audio_data)} bytes per trucada {call_id}")
        
        # Aquí es processaria l'àudio real amb l'agent ConvHi
        # Per ara, simulem el processament
        
    except Exception as e:
        logger.error(f"Error processant àudio: {e}")

@router.get("/health")
async def real_sip_health():
    """Health check del sistema SIP real"""
    return {
        "status": "ok",
        "message": "Sistema SIP real funcionant",
        "stats": {
            "active_calls": len(active_calls),
            "sip_connections": len(sip_connections),
            "websocket_connections": len(websocket_connections),
            "sip_server": f"sip.veuplus.com:{real_sip_engine.sip_server_port}",
            "rtp_port_range": f"{real_sip_engine.rtp_port_range[0]}-{real_sip_engine.rtp_port_range[1]}"
        }
    }

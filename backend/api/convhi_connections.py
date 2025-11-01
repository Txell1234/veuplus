#!/usr/bin/env python3
"""
ConvHi Connections System - Sistema de connexions externes i internes
Suport per connexió amb mòduls externs, altres ConvHi i APIs externes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import aiohttp
import json
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger("veuplus.connections")

router = APIRouter(prefix="/api/convhi/connections", tags=["ConvHi Connections"])

# Enums
class ConnectionType(str, Enum):
    EXTERNAL_API = "external_api"
    CONVHI_AGENT = "convhi_agent"
    WEBHOOK = "webhook"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"

class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

# Models
class ConnectionConfig(BaseModel):
    id: str
    name: str
    type: ConnectionType
    description: str
    endpoint: str
    authentication: Dict[str, Any] = {}
    headers: Dict[str, str] = {}
    timeout: int = 30
    retry_count: int = 3
    status: ConnectionStatus = ConnectionStatus.INACTIVE
    agent_id: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}

class ConnectionRequest(BaseModel):
    connection_id: str
    method: str = "POST"  # GET, POST, PUT, DELETE
    path: str = ""
    data: Dict[str, Any] = {}
    headers: Dict[str, str] = {}
    timeout: Optional[int] = None

class ConnectionResponse(BaseModel):
    success: bool
    status_code: int
    data: Optional[Any] = None
    error: Optional[str] = None
    response_time: float
    connection_id: str

class ConvHiAgentCall(BaseModel):
    source_agent_id: str
    target_agent_id: str
    message: str
    context: Dict[str, Any] = {}
    priority: str = "normal"  # low, normal, high, urgent

# In-memory storage
connections_storage = {
    "configs": {},
    "active_connections": {},
    "call_history": []
}

class ConnectionsEngine:
    def __init__(self):
        self.session = None
        self._initialize_default_connections()
    
    def _initialize_default_connections(self):
        """Inicialitzar connexions per defecte"""
        
        # Connexió amb sistema de veus
        voice_connection = ConnectionConfig(
            id="voice_system_connection",
            name="Sistema de Veus VeuPlus",
            type=ConnectionType.EXTERNAL_API,
            description="Connexió amb el sistema de síntesi de veu",
            endpoint="http://localhost:8000/api",
            authentication={},
            headers={"Content-Type": "application/json"},
            timeout=30,
            retry_count=3,
            status=ConnectionStatus.ACTIVE,
            agent_id="default",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={
                "service": "voice_synthesis",
                "supported_formats": ["wav", "mp3"],
                "languages": ["es", "ca", "en", "fr"]
            }
        )
        
        # Connexió amb base de dades
        database_connection = ConnectionConfig(
            id="database_connection",
            name="Base de Dades Principal",
            type=ConnectionType.DATABASE,
            description="Connexió amb la base de dades principal",
            endpoint="sqlite:///veuplus.db",
            authentication={},
            headers={},
            timeout=10,
            retry_count=2,
            status=ConnectionStatus.ACTIVE,
            agent_id="default",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={
                "db_type": "sqlite",
                "tables": ["conversations", "agents", "knowledge", "analytics"]
            }
        )
        
        # Connexió amb webhook extern
        webhook_connection = ConnectionConfig(
            id="external_webhook",
            name="Webhook Extern",
            type=ConnectionType.WEBHOOK,
            description="Webhook per notificacions externes",
            endpoint="https://api.external-service.com/webhook",
            authentication={
                "type": "bearer",
                "token": "your-webhook-token"
            },
            headers={"Content-Type": "application/json"},
            timeout=15,
            retry_count=2,
            status=ConnectionStatus.INACTIVE,
            agent_id="default",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={
                "events": ["conversation_start", "conversation_end", "transfer"],
                "format": "json"
            }
        )
        
        # Guardar connexions per defecte
        default_connections = [voice_connection, database_connection, webhook_connection]
        for connection in default_connections:
            connections_storage["configs"][connection.id] = connection.dict()
        
        logger.info(f"✅ {len(default_connections)} connexions per defecte inicialitzades")
    
    async def get_session(self):
        """Obtenir sessió HTTP reutilitzable"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Tancar sessió HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def create_connection(self, config: ConnectionConfig) -> bool:
        """Crear nova connexió"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            connections_storage["configs"][config.id] = config.dict()
            
            logger.info(f"✅ Connexió creada: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant connexió: {e}")
            return False
    
    async def test_connection(self, connection_id: str) -> bool:
        """Provar connexió"""
        try:
            if connection_id not in connections_storage["configs"]:
                return False
            
            config_data = connections_storage["configs"][connection_id]
            config = ConnectionConfig(**config_data)
            
            # Actualitzar estat a testing
            config.status = ConnectionStatus.TESTING
            connections_storage["configs"][connection_id] = config.dict()
            
            success = False
            
            if config.type == ConnectionType.EXTERNAL_API:
                success = await self._test_external_api(config)
            elif config.type == ConnectionType.WEBHOOK:
                success = await self._test_webhook(config)
            elif config.type == ConnectionType.DATABASE:
                success = await self._test_database(config)
            elif config.type == ConnectionType.CONVHI_AGENT:
                success = await self._test_convhi_agent(config)
            else:
                success = True  # Altres tipus sempre passen
            
            # Actualitzar estat final
            config.status = ConnectionStatus.ACTIVE if success else ConnectionStatus.ERROR
            connections_storage["configs"][connection_id] = config.dict()
            
            return success
            
        except Exception as e:
            logger.error(f"Error provant connexió {connection_id}: {e}")
            if connection_id in connections_storage["configs"]:
                config_data = connections_storage["configs"][connection_id]
                config = ConnectionConfig(**config_data)
                config.status = ConnectionStatus.ERROR
                connections_storage["configs"][connection_id] = config.dict()
            return False
    
    async def _test_external_api(self, config: ConnectionConfig) -> bool:
        """Provar API externa"""
        try:
            session = await self.get_session()
            
            headers = config.headers.copy()
            if config.authentication.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {config.authentication.get('token', '')}"
            elif config.authentication.get("type") == "api_key":
                headers[config.authentication.get("key_name", "X-API-Key")] = config.authentication.get("key_value", "")
            
            async with session.get(
                config.endpoint,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                return response.status < 400
                
        except Exception as e:
            logger.error(f"Error provant API externa: {e}")
            return False
    
    async def _test_webhook(self, config: ConnectionConfig) -> bool:
        """Provar webhook"""
        try:
            session = await self.get_session()
            
            headers = config.headers.copy()
            if config.authentication.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {config.authentication.get('token', '')}"
            
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "veuplus_convhi"
            }
            
            async with session.post(
                config.endpoint,
                headers=headers,
                json=test_payload,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                return response.status < 400
                
        except Exception as e:
            logger.error(f"Error provant webhook: {e}")
            return False
    
    async def _test_database(self, config: ConnectionConfig) -> bool:
        """Provar base de dades"""
        try:
            # Implementació bàsica per SQLite
            if config.endpoint.startswith("sqlite:///"):
                import sqlite3
                db_path = config.endpoint.replace("sqlite:///", "")
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT 1")
                conn.close()
                return True
            else:
                # Altres tipus de BD - implementar segons necessitat
                return True
                
        except Exception as e:
            logger.error(f"Error provant base de dades: {e}")
            return False
    
    async def _test_convhi_agent(self, config: ConnectionConfig) -> bool:
        """Provar agent ConvHi intern"""
        try:
            # Verificar que l'agent existeix
            from .convhi_agents import convhi_agents
            
            target_agent_id = config.metadata.get("target_agent_id")
            if target_agent_id and target_agent_id in convhi_agents:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error provant agent ConvHi: {e}")
            return False
    
    async def call_connection(self, request: ConnectionRequest) -> ConnectionResponse:
        """Cridar connexió externa"""
        start_time = datetime.now()
        
        try:
            if request.connection_id not in connections_storage["configs"]:
                raise ValueError(f"Connexió {request.connection_id} no trobada")
            
            config_data = connections_storage["configs"][request.connection_id]
            config = ConnectionConfig(**config_data)
            
            if config.status != ConnectionStatus.ACTIVE:
                raise ValueError(f"Connexió {request.connection_id} no està activa")
            
            # Executar segons el tipus
            if config.type == ConnectionType.EXTERNAL_API:
                result = await self._call_external_api(config, request)
            elif config.type == ConnectionType.WEBHOOK:
                result = await self._call_webhook(config, request)
            elif config.type == ConnectionType.CONVHI_AGENT:
                result = await self._call_convhi_agent(config, request)
            else:
                raise ValueError(f"Tipus de connexió {config.type} no suportat per crides")
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return ConnectionResponse(
                success=True,
                status_code=200,
                data=result,
                response_time=response_time,
                connection_id=request.connection_id
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error cridant connexió {request.connection_id}: {e}")
            
            return ConnectionResponse(
                success=False,
                status_code=500,
                error=str(e),
                response_time=response_time,
                connection_id=request.connection_id
            )
    
    async def _call_external_api(self, config: ConnectionConfig, request: ConnectionRequest) -> Any:
        """Cridar API externa"""
        session = await self.get_session()
        
        headers = config.headers.copy()
        headers.update(request.headers)
        
        # Afegir autenticació
        if config.authentication.get("type") == "bearer":
            headers["Authorization"] = f"Bearer {config.authentication.get('token', '')}"
        elif config.authentication.get("type") == "api_key":
            headers[config.authentication.get("key_name", "X-API-Key")] = config.authentication.get("key_value", "")
        
        url = f"{config.endpoint}{request.path}"
        timeout = request.timeout or config.timeout
        
        async with session.request(
            request.method,
            url,
            headers=headers,
            json=request.data if request.data else None,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status < 400:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"API error {response.status}: {error_text}")
    
    async def _call_webhook(self, config: ConnectionConfig, request: ConnectionRequest) -> Any:
        """Cridar webhook"""
        session = await self.get_session()
        
        headers = config.headers.copy()
        headers.update(request.headers)
        
        # Afegir autenticació
        if config.authentication.get("type") == "bearer":
            headers["Authorization"] = f"Bearer {config.authentication.get('token', '')}"
        
        timeout = request.timeout or config.timeout
        
        async with session.post(
            config.endpoint,
            headers=headers,
            json=request.data,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status < 400:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Webhook error {response.status}: {error_text}")
    
    async def _call_convhi_agent(self, config: ConnectionConfig, request: ConnectionRequest) -> Any:
        """Cridar agent ConvHi intern"""
        try:
            target_agent_id = config.metadata.get("target_agent_id")
            if not target_agent_id:
                raise ValueError("target_agent_id requerit per connexions ConvHi")
            
            # Crear missatge per l'agent
            from .convhi_agents import ConversationMessage
            
            message = ConversationMessage(
                agent_id=target_agent_id,
                message=request.data.get("message", ""),
                message_type="text",
                timestamp=datetime.now()
            )
            
            # Cridar l'agent
            from .convhi_agents import chat_with_agent
            
            response = await chat_with_agent(target_agent_id, message)
            
            return {
                "agent_response": response.get("response", ""),
                "audio_base64": response.get("audio_base64", ""),
                "knowledge_used": response.get("knowledge_used", 0),
                "tools_executed": response.get("tools_executed", []),
                "workflow_active": response.get("workflow_active", False)
            }
            
        except Exception as e:
            logger.error(f"Error cridant agent ConvHi: {e}")
            raise
    
    async def call_convhi_agent_direct(self, call: ConvHiAgentCall) -> Dict[str, Any]:
        """Cridar agent ConvHi directament"""
        try:
            from .convhi_agents import convhi_agents, ConversationMessage
            
            # Verificar que l'agent destí existeix
            if call.target_agent_id not in convhi_agents:
                raise ValueError(f"Agent {call.target_agent_id} no trobat")
            
            # Crear missatge
            message = ConversationMessage(
                agent_id=call.target_agent_id,
                message=call.message,
                message_type="text",
                timestamp=datetime.now()
            )
            
            # Cridar l'agent
            from .convhi_agents import chat_with_agent
            
            response = await chat_with_agent(call.target_agent_id, message)
            
            # Registrar crida
            call_record = {
                "id": str(uuid.uuid4()),
                "source_agent_id": call.source_agent_id,
                "target_agent_id": call.target_agent_id,
                "message": call.message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "priority": call.priority
            }
            
            connections_storage["call_history"].append(call_record)
            
            return {
                "success": True,
                "call_id": call_record["id"],
                "response": response,
                "timestamp": call_record["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error cridant agent ConvHi directament: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_connections(self, agent_id: Optional[str] = None) -> List[ConnectionConfig]:
        """Obtenir connexions"""
        connections = []
        for config_data in connections_storage["configs"].values():
            config = ConnectionConfig(**config_data)
            if not agent_id or config.agent_id == agent_id:
                connections.append(config)
        return connections
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionConfig]:
        """Obtenir connexió específica"""
        if connection_id in connections_storage["configs"]:
            return ConnectionConfig(**connections_storage["configs"][connection_id])
        return None
    
    def get_call_history(self, agent_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtenir històric de crides"""
        history = connections_storage["call_history"]
        
        if agent_id:
            history = [call for call in history if call.get("source_agent_id") == agent_id or call.get("target_agent_id") == agent_id]
        
        return history[-limit:]

# Instància global
connections_engine = ConnectionsEngine()

# Endpoints
@router.get("/")
async def get_connections(agent_id: Optional[str] = None):
    """Obtenir connexions"""
    try:
        connections = connections_engine.get_connections(agent_id)
        
        return {
            "success": True,
            "connections": [conn.dict() for conn in connections],
            "total": len(connections)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint connexions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{connection_id}")
async def get_connection(connection_id: str):
    """Obtenir connexió específica"""
    try:
        connection = connections_engine.get_connection(connection_id)
        
        if connection:
            return {
                "success": True,
                "connection": connection.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Connexió no trobada")
        
    except Exception as e:
        logger.error(f"Error obtenint connexió: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_connection(config: ConnectionConfig):
    """Crear nova connexió"""
    try:
        success = await connections_engine.create_connection(config)
        
        if success:
            return {
                "success": True,
                "message": f"Connexió {config.name} creada correctament",
                "connection": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant connexió")
        
    except Exception as e:
        logger.error(f"Error creant connexió: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/{connection_id}")
async def test_connection(connection_id: str):
    """Provar connexió"""
    try:
        success = await connections_engine.test_connection(connection_id)
        
        return {
            "success": success,
            "connection_id": connection_id,
            "status": "active" if success else "error",
            "message": "Connexió provada correctament" if success else "Error provant connexió"
        }
        
    except Exception as e:
        logger.error(f"Error provant connexió: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call")
async def call_connection(request: ConnectionRequest):
    """Cridar connexió"""
    try:
        response = await connections_engine.call_connection(request)
        
        return {
            "success": response.success,
            "status_code": response.status_code,
            "data": response.data,
            "error": response.error,
            "response_time": response.response_time,
            "connection_id": response.connection_id
        }
        
    except Exception as e:
        logger.error(f"Error cridant connexió: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/call-convhi")
async def call_convhi_agent(call: ConvHiAgentCall):
    """Cridar agent ConvHi directament"""
    try:
        result = await connections_engine.call_convhi_agent_direct(call)
        
        return result
        
    except Exception as e:
        logger.error(f"Error cridant agent ConvHi: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_call_history(agent_id: Optional[str] = None, limit: int = 100):
    """Obtenir històric de crides"""
    try:
        history = connections_engine.get_call_history(agent_id, limit)
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint històric: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def connections_health():
    """Health check del sistema de connexions"""
    return {
        "status": "ok",
        "message": "Sistema de connexions funcionant",
        "stats": {
            "total_connections": len(connections_storage["configs"]),
            "active_connections": len([c for c in connections_storage["configs"].values() if c.get("status") == "active"]),
            "total_calls": len(connections_storage["call_history"])
        }
    }

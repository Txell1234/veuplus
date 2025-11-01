#!/usr/bin/env python3
"""
ConvHi Tools System - Sistema complet d'eines per agents
Suport per Client Tools, Server Tools i System Tools
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Callable, Union
import logging
import asyncio
import json
import aiohttp
from datetime import datetime
from enum import Enum
import inspect

logger = logging.getLogger("veuplus.tools")

router = APIRouter(prefix="/api/convhi/tools", tags=["ConvHi Tools"])

# Enums
class ToolType(str, Enum):
    CLIENT = "client"
    SERVER = "server"
    SYSTEM = "system"

class ToolCategory(str, Enum):
    COMMUNICATION = "communication"
    DATA = "data"
    INTEGRATION = "integration"
    UTILITY = "utility"
    BUSINESS = "business"

# Models
class ToolParameter(BaseModel):
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None
    pattern: Optional[str] = None

class ToolDefinition(BaseModel):
    id: str
    name: str
    description: str
    type: ToolType
    category: ToolCategory
    parameters: List[ToolParameter]
    returns: Dict[str, Any]
    enabled: bool = True
    agent_id: Optional[str] = None
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}

class ToolExecutionRequest(BaseModel):
    tool_id: str
    agent_id: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class ToolExecutionResult(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = {}

# In-memory storage
tools_storage = {
    "definitions": {},
    "agent_tools": {},  # agent_id -> [tool_ids]
    "executions": []
}

class ToolsEngine:
    def __init__(self):
        self.client_tools = {}
        self.server_tools = {}
        self.system_tools = {}
        self._initialize_system_tools()
    
    def _initialize_system_tools(self):
        """Inicialitzar eines del sistema"""
        
        # Tool: End Call
        end_call_tool = ToolDefinition(
            id="system_end_call",
            name="End Call",
            description="Terminar la conversa actual",
            type=ToolType.SYSTEM,
            category=ToolCategory.COMMUNICATION,
            parameters=[
                ToolParameter(
                    name="reason",
                    type="string",
                    description="Raó per acabar la conversa",
                    required=False,
                    default="Conversation completed"
                )
            ],
            returns={"type": "object", "properties": {"message": {"type": "string"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Tool: Transfer to Human
        transfer_tool = ToolDefinition(
            id="system_transfer_human",
            name="Transfer to Human",
            description="Transferir la conversa a un agent humà",
            type=ToolType.SYSTEM,
            category=ToolCategory.COMMUNICATION,
            parameters=[
                ToolParameter(
                    name="department",
                    type="string",
                    description="Departament al qual transferir",
                    required=True,
                    enum=["support", "sales", "technical", "billing"]
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="Prioritat de la transferència",
                    required=False,
                    default="normal",
                    enum=["low", "normal", "high", "urgent"]
                ),
                ToolParameter(
                    name="reason",
                    type="string",
                    description="Raó de la transferència",
                    required=False
                )
            ],
            returns={"type": "object", "properties": {"transfer_id": {"type": "string"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Tool: Transfer to Phone Number
        transfer_number_tool = ToolDefinition(
            id="system_transfer_number",
            name="Transfer to Number",
            description="Transferir la trucada a un número concret (SIP/RTC)",
            type=ToolType.SYSTEM,
            category=ToolCategory.COMMUNICATION,
            parameters=[
                ToolParameter(
                    name="phone_number",
                    type="string",
                    description="Número de destí (E.164 o extensió interna)",
                    required=True
                ),
                ToolParameter(
                    name="reason",
                    type="string",
                    description="Motiu de la transferència",
                    required=False,
                    default="User requested transfer"
                ),
                ToolParameter(
                    name="mode",
                    type="string",
                    description="Tipus de transferència (blind, attended)",
                    required=False,
                    default="blind",
                    enum=["blind", "attended"]
                )
            ],
            returns={"type": "object", "properties": {"transfer_id": {"type": "string"}, "status": {"type": "string"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Tool: Language Detection
        language_detection_tool = ToolDefinition(
            id="system_language_detection",
            name="Language Detection",
            description="Detectar l'idioma del text",
            type=ToolType.SYSTEM,
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text per detectar l'idioma",
                    required=True
                )
            ],
            returns={"type": "object", "properties": {"language": {"type": "string"}, "confidence": {"type": "number"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Tool: Skip Turn
        skip_turn_tool = ToolDefinition(
            id="system_skip_turn",
            name="Skip Turn",
            description="No parlar en aquest torn i esperar més informació",
            type=ToolType.SYSTEM,
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="reason",
                    type="string",
                    description="Motiu pel qual es salta el torn",
                    required=False,
                    default="Awaiting more user input"
                )
            ],
            returns={"type": "object", "properties": {"action": {"type": "string"}, "message": {"type": "string"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        # Tool: Voicemail Detection
        voicemail_tool = ToolDefinition(
            id="system_voicemail_detection",
            name="Voicemail Detection",
            description="Detectar si el sistema està parlant amb un contestador automàtic",
            type=ToolType.SYSTEM,
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="silence_duration",
                    type="number",
                    description="Durada de silenci detectada (segons)",
                    required=False,
                    default=0.0
                ),
                ToolParameter(
                    name="audio_level",
                    type="number",
                    description="Nivell d'àudio mitjà detectat (0-1)",
                    required=False,
                    default=0.0
                ),
                ToolParameter(
                    name="keywords",
                    type="array",
                    description="Llista de paraules detectades a l'àudio transcrit",
                    required=False,
                    default=[]
                )
            ],
            returns={"type": "object", "properties": {"voicemail": {"type": "boolean"}, "confidence": {"type": "number"}}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Tool: Knowledge Search
        knowledge_search_tool = ToolDefinition(
            id="system_knowledge_search",
            name="Knowledge Search",
            description="Cercar informació a la base de coneixement",
            type=ToolType.SYSTEM,
            category=ToolCategory.DATA,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Consulta de cerca",
                    required=True
                ),
                ToolParameter(
                    name="max_results",
                    type="number",
                    description="Nombre màxim de resultats",
                    required=False,
                    default=5
                )
            ],
            returns={"type": "array", "items": {"type": "object"}},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Registrar eines del sistema
        system_tools = [
            end_call_tool,
            transfer_tool,
            transfer_number_tool,
            language_detection_tool,
            skip_turn_tool,
            voicemail_tool,
            knowledge_search_tool
        ]
        for tool in system_tools:
            tools_storage["definitions"][tool.id] = tool.dict()
            self.system_tools[tool.id] = tool
        
        logger.info(f"✅ {len(system_tools)} eines del sistema inicialitzades")
    
    async def register_client_tool(self, tool_definition: ToolDefinition, handler: Callable) -> bool:
        """Registrar eina del client"""
        try:
            if tool_definition.type != ToolType.CLIENT:
                raise ValueError("Només es poden registrar eines del tipus CLIENT")
            
            tools_storage["definitions"][tool_definition.id] = tool_definition.dict()
            self.client_tools[tool_definition.id] = {
                "definition": tool_definition,
                "handler": handler
            }
            
            logger.info(f"🔧 Eina del client registrada: {tool_definition.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrant eina del client: {e}")
            return False
    
    async def register_server_tool(self, tool_definition: ToolDefinition, handler: Callable) -> bool:
        """Registrar eina del servidor"""
        try:
            if tool_definition.type != ToolType.SERVER:
                raise ValueError("Només es poden registrar eines del tipus SERVER")
            
            tools_storage["definitions"][tool_definition.id] = tool_definition.dict()
            self.server_tools[tool_definition.id] = {
                "definition": tool_definition,
                "handler": handler
            }
            
            logger.info(f"🔧 Eina del servidor registrada: {tool_definition.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registrant eina del servidor: {e}")
            return False
    
    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Executar eina"""
        start_time = datetime.now()
        
        try:
            tool_id = request.tool_id
            
            # Verificar que l'eina existeix
            if tool_id not in tools_storage["definitions"]:
                raise ValueError(f"Eina {tool_id} no trobada")
            
            tool_def = ToolDefinition(**tools_storage["definitions"][tool_id])
            
            # Verificar que l'eina està habilitada
            if not tool_def.enabled:
                raise ValueError(f"Eina {tool_id} deshabilitada")
            
            # Verificar que l'agent té accés a l'eina
            if tool_def.agent_id and tool_def.agent_id != request.agent_id:
                raise ValueError(f"Agent {request.agent_id} no té accés a l'eina {tool_id}")
            
            # Validar paràmetres
            self._validate_parameters(tool_def, request.parameters)
            
            # Executar segons el tipus
            if tool_id in self.system_tools:
                result = await self._execute_system_tool(tool_id, request.parameters, request.context)
            elif tool_id in self.server_tools:
                result = await self._execute_server_tool(tool_id, request.parameters, request.context)
            elif tool_id in self.client_tools:
                result = await self._execute_client_tool(tool_id, request.parameters, request.context)
            else:
                raise ValueError(f"Handler per l'eina {tool_id} no trobat")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Registrar execució
            tools_storage["executions"].append({
                "tool_id": tool_id,
                "agent_id": request.agent_id,
                "success": True,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return ToolExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executant eina {request.tool_id}: {e}")
            
            # Registrar execució fallida
            tools_storage["executions"].append({
                "tool_id": request.tool_id,
                "agent_id": request.agent_id,
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return ToolExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _validate_parameters(self, tool_def: ToolDefinition, parameters: Dict[str, Any]):
        """Validar paràmetres de l'eina"""
        for param in tool_def.parameters:
            param_name = param.name
            
            # Verificar paràmetres requerits
            if param.required and param_name not in parameters:
                raise ValueError(f"Paràmetre requerit '{param_name}' no proporcionat")
            
            # Aplicar valor per defecte
            if param_name not in parameters and param.default is not None:
                parameters[param_name] = param.default
            
            # Validar tipus
            if param_name in parameters:
                value = parameters[param_name]
                if param.type == "string" and not isinstance(value, str):
                    raise ValueError(f"Paràmetre '{param_name}' ha de ser string")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Paràmetre '{param_name}' ha de ser number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Paràmetre '{param_name}' ha de ser boolean")
                
                # Validar enum
                if param.enum and value not in param.enum:
                    raise ValueError(f"Paràmetre '{param_name}' ha de ser un de: {param.enum}")
    
    async def _execute_system_tool(self, tool_id: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Executar eina del sistema"""
        try:
            if tool_id == "system_end_call":
                reason = parameters.get('reason', 'Conversation completed')
                
                # Registrar finalització de conversa
                if context and "conversation_id" in context:
                    try:
                        from .convhi_analytics import analytics_engine
                        await analytics_engine.log_conversation({
                            "id": context["conversation_id"],
                            "agent_id": context.get("agent_id"),
                            "status": "completed",
                            "end_time": datetime.now().isoformat(),
                            "metadata": {"end_reason": reason}
                        })
                    except Exception as e:
                        logger.warning(f"Error registrant finalització de conversa: {e}")
                
                return {
                    "action": "end_call",
                    "message": f"Conversa finalitzada: {reason}",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif tool_id == "system_transfer_human":
                department = parameters.get("department", "support")
                priority = parameters.get("priority", "normal")
                reason = parameters.get("reason", "Transferència sol·licitada per l'usuari")
                
                transfer_id = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Simular transferència (en producció integrar amb sistema real)
                transfer_result = {
                    "transfer_id": transfer_id,
                    "department": department,
                    "priority": priority,
                    "reason": reason,
                    "status": "initiated",
                    "estimated_wait_time": self._calculate_wait_time(department, priority),
                    "message": f"Transferència a {department} iniciada. Temps d'espera estimat: {self._calculate_wait_time(department, priority)} minuts"
                }
                
                # Registrar transferència
                if context and "conversation_id" in context:
                    try:
                        from .convhi_analytics import analytics_engine
                        await analytics_engine.log_conversation({
                            "id": context["conversation_id"],
                            "agent_id": context.get("agent_id"),
                            "status": "transferred",
                            "end_time": datetime.now().isoformat(),
                            "metadata": {
                                "transfer_id": transfer_id,
                                "department": department,
                                "priority": priority,
                                "reason": reason
                            }
                        })
                    except Exception as e:
                        logger.warning(f"Error registrant transferència: {e}")
                
                return transfer_result
            
            elif tool_id == "system_transfer_number":
                phone_number = parameters.get("phone_number")
                if not phone_number:
                    raise ValueError("Cal indicar el paràmetre phone_number per fer la transferència")
                reason = parameters.get("reason", "Transferència sol·licitada per l'usuari")
                mode = parameters.get("mode", "blind")
                transfer_id = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                transfer_payload = {
                    "transfer_id": transfer_id,
                    "phone_number": phone_number,
                    "mode": mode,
                    "reason": reason,
                    "status": "initiated",
                    "message": f"Transferència al número {phone_number} iniciada en mode {mode}"
                }
                
                if context and "conversation_id" in context:
                    try:
                        from .convhi_analytics import analytics_engine
                        await analytics_engine.log_conversation({
                            "id": context["conversation_id"],
                            "agent_id": context.get("agent_id"),
                            "status": "transferred",
                            "end_time": datetime.now().isoformat(),
                            "metadata": {
                                "transfer_id": transfer_id,
                                "phone_number": phone_number,
                                "mode": mode,
                                "reason": reason
                            }
                        })
                    except Exception as e:
                        logger.warning(f"Error registrant transferència a número: {e}")
                
                return transfer_payload
            
            elif tool_id == "system_language_detection":
                text = parameters.get("text", "")
                if not text:
                    raise ValueError("Text no proporcionat per detectar idioma")
                
                language = None
                confidence = 0.0
                detection_method = "basic"
                llm_success = False
                
                # Intentar detecció via LLM
                try:
                    from .llm_integration import generate_llm_response
                    
                    llm_response = await generate_llm_response(
                        provider=parameters.get("llm_provider", "openai"),
                        model=parameters.get("llm_model", "gpt-4o-mini"),
                        messages=[
                            {
                                "role": "system", 
                                "content": "Detecta l'idioma del text i respon només amb el codi ISO (ca, es, en, fr, etc.). No afegeixis text extra."
                            },
                            {
                                "role": "user", 
                                "content": text
                            }
                        ],
                        max_tokens=10,
                        temperature=0.0
                    )
                    
                    if llm_response.success and llm_response.content:
                        language = llm_response.content.strip().lower().split()[0]
                        confidence = 0.9
                        detection_method = "llm"
                        llm_success = True
                except Exception as e:
                    logger.warning(f"Error en detecció d'idioma amb LLM: {e}")
                
                if not language:
                    language = self._detect_language_basic(text)
                    confidence = 0.7 if language != "unknown" else 0.4
                    detection_method = "basic"
                
                return {
                    "language": language,
                    "confidence": confidence,
                    "text_length": len(text),
                    "detection_method": detection_method,
                    "llm_used": llm_success
                }
            
            elif tool_id == "system_skip_turn":
                reason = parameters.get("reason", "Esperant més informació de l'usuari")
                return {
                    "action": "skip_turn",
                    "message": reason,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif tool_id == "system_voicemail_detection":
                silence_duration = float(parameters.get("silence_duration", 0.0) or 0.0)
                audio_level = float(parameters.get("audio_level", 0.0) or 0.0)
                keywords = parameters.get("keywords", []) or []
                
                voicemail, confidence = self._detect_voicemail(silence_duration, audio_level, keywords)
                
                return {
                    "voicemail": voicemail,
                    "confidence": confidence,
                    "silence_duration": silence_duration,
                    "audio_level": audio_level,
                    "keywords": keywords
                }
            
            elif tool_id == "system_knowledge_search":
                query = parameters.get("query", "")
                max_results = parameters.get("max_results", 5)
                
                # Integrar amb el sistema de coneixement
                try:
                    from .convhi_knowledge import knowledge_engine, KnowledgeSearchRequest
                    
                    if context and "agent_id" in context:
                        search_request = KnowledgeSearchRequest(
                            agent_id=context["agent_id"],
                            query=query,
                            max_results=max_results
                        )
                        
                        search_results = await knowledge_engine.search_knowledge(search_request)
                        
                        # Formatejar resultats per l'eina
                        formatted_results = []
                        for result in search_results:
                            formatted_results.append({
                                "id": result.item.id,
                                "title": result.item.title,
                                "content": result.item.content[:200] + "..." if len(result.item.content) > 200 else result.item.content,
                                "relevance_score": result.relevance_score,
                                "category": result.item.category,
                                "tags": result.item.tags,
                                "matched_snippets": result.matched_snippets
                            })
                        
                        return {
                            "query": query,
                            "results": formatted_results,
                            "total_found": len(formatted_results),
                            "search_time": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "query": query,
                            "results": [],
                            "total_found": 0,
                            "error": "Agent ID no proporcionat"
                        }
                        
                except Exception as e:
                    logger.warning(f"Error cercant coneixement: {e}")
                    return {
                        "query": query,
                        "results": [],
                        "total_found": 0,
                        "error": str(e)
                    }
            
            else:
                raise ValueError(f"Eina del sistema {tool_id} no implementada")
                
        except Exception as e:
            logger.error(f"Error executant eina del sistema {tool_id}: {e}")
            raise
    
    def _calculate_wait_time(self, department: str, priority: str) -> int:
        """Calcular temps d'espera estimat"""
        base_times = {
            "support": 5,
            "sales": 3,
            "technical": 8,
            "billing": 4
        }
        
        priority_multipliers = {
            "low": 1.5,
            "normal": 1.0,
            "high": 0.7,
            "urgent": 0.3
        }
        
        base_time = base_times.get(department, 5)
        multiplier = priority_multipliers.get(priority, 1.0)
        
        return int(base_time * multiplier)
    
    async def _execute_server_tool(self, tool_id: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Executar eina del servidor"""
        try:
            tool_info = self.server_tools[tool_id]
            handler = tool_info["handler"]
            
            # Executar handler
            if inspect.iscoroutinefunction(handler):
                result = await handler(parameters, context)
            else:
                result = handler(parameters, context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executant eina del servidor {tool_id}: {e}")
            raise
    
    async def _execute_client_tool(self, tool_id: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Executar eina del client (retorna instruccions per al client)"""
        try:
            tool_info = self.client_tools[tool_id]
            handler = tool_info["handler"]
            
            # Per eines del client, retornem les instruccions
            return {
                "tool_id": tool_id,
                "action": "client_execution",
                "parameters": parameters,
                "instructions": f"Executar eina del client: {tool_info['definition'].name}"
            }
            
        except Exception as e:
            logger.error(f"Error preparant eina del client {tool_id}: {e}")
            raise
    
    def _detect_language_basic(self, text: str) -> str:
        """Detecció bàsica d'idioma"""
        text_lower = text.lower()
        
        # Paraules clau per idiomes
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le']
        catalan_words = ['el', 'la', 'de', 'que', 'i', 'a', 'en', 'un', 'és', 'se', 'no', 'te', 'lo', 'le']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        catalan_count = sum(1 for word in catalan_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if spanish_count > catalan_count and spanish_count > english_count:
            return "es"
        elif catalan_count > spanish_count and catalan_count > english_count:
            return "ca"
        elif english_count > spanish_count and english_count > catalan_count:
            return "en"
        else:
            return "unknown"
    
    def get_available_tools(self, agent_id: Optional[str] = None, tool_type: Optional[ToolType] = None) -> List[ToolDefinition]:
        """Obtenir eines disponibles"""
        tools = []
        
        for tool_id, tool_data in tools_storage["definitions"].items():
            tool_def = ToolDefinition(**tool_data)
            
            # Filtrar per tipus
            if tool_type and tool_def.type != tool_type:
                continue
            
            # Filtrar per agent
            if tool_def.agent_id and tool_def.agent_id != agent_id:
                continue
            
            # Filtrar per habilitació
            if not tool_def.enabled:
                continue
            
            tools.append(tool_def)
        
        return tools
    
    def assign_tool_to_agent(self, agent_id: str, tool_id: str) -> bool:
        """Assignar eina a agent"""
        try:
            if tool_id not in tools_storage["definitions"]:
                return False
            
            if agent_id not in tools_storage["agent_tools"]:
                tools_storage["agent_tools"][agent_id] = []
            
            if tool_id not in tools_storage["agent_tools"][agent_id]:
                tools_storage["agent_tools"][agent_id].append(tool_id)
            
            logger.info(f"🔧 Eina {tool_id} assignada a agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assignant eina a agent: {e}")
            return False

# Instància global
tools_engine = ToolsEngine()

# Endpoints
@router.get("/")
async def get_tools(
    agent_id: Optional[str] = None,
    tool_type: Optional[ToolType] = None
):
    """Obtenir eines disponibles"""
    try:
        tools = tools_engine.get_available_tools(agent_id, tool_type)
        
        return {
            "success": True,
            "tools": [tool.dict() for tool in tools],
            "total": len(tools)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint eines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Executar eina"""
    try:
        result = await tools_engine.execute_tool(request)
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Error executant eina: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register/client")
async def register_client_tool(
    tool_definition: ToolDefinition,
    handler_code: Optional[str] = None
):
    """Registrar eina del client"""
    try:
        # En un entorn real, el handler_code seria compilat i executat de manera segura
        # Aquí fem una simulació
        
        def dummy_handler(parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
            return {"message": f"Eina del client {tool_definition.name} executada", "parameters": parameters}
        
        success = await tools_engine.register_client_tool(tool_definition, dummy_handler)
        
        if success:
            return {
                "success": True,
                "message": f"Eina del client {tool_definition.name} registrada correctament",
                "tool_id": tool_definition.id
            }
        else:
            raise HTTPException(status_code=400, detail="Error registrant eina del client")
        
    except Exception as e:
        logger.error(f"Error registrant eina del client: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register/server")
async def register_server_tool(
    tool_definition: ToolDefinition,
    handler_code: Optional[str] = None
):
    """Registrar eina del servidor"""
    try:
        # En un entorn real, el handler_code seria compilat i executat de manera segura
        # Aquí fem una simulació
        
        def dummy_handler(parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
            return {"message": f"Eina del servidor {tool_definition.name} executada", "parameters": parameters}
        
        success = await tools_engine.register_server_tool(tool_definition, dummy_handler)
        
        if success:
            return {
                "success": True,
                "message": f"Eina del servidor {tool_definition.name} registrada correctament",
                "tool_id": tool_definition.id
            }
        else:
            raise HTTPException(status_code=400, detail="Error registrant eina del servidor")
        
    except Exception as e:
        logger.error(f"Error registrant eina del servidor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign")
async def assign_tool_to_agent(
    agent_id: str,
    tool_id: str
):
    """Assignar eina a agent"""
    try:
        success = tools_engine.assign_tool_to_agent(agent_id, tool_id)
        
        if success:
            return {
                "success": True,
                "message": f"Eina {tool_id} assignada a agent {agent_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="Eina o agent no trobat")
        
    except Exception as e:
        logger.error(f"Error assignant eina a agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions")
async def get_tool_executions(
    agent_id: Optional[str] = None,
    tool_id: Optional[str] = None,
    limit: int = 100
):
    """Obtenir històric d'execucions d'eines"""
    try:
        executions = tools_storage["executions"]
        
        # Filtrar per agent i eina
        if agent_id:
            executions = [e for e in executions if e["agent_id"] == agent_id]
        
        if tool_id:
            executions = [e for e in executions if e["tool_id"] == tool_id]
        
        # Limitar resultats
        executions = executions[-limit:]
        
        return {
            "success": True,
            "executions": executions,
            "total": len(executions)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint execucions d'eines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def tools_health():
    """Health check del sistema d'eines"""
    return {
        "status": "ok",
        "message": "Sistema d'eines funcionant",
        "stats": {
            "total_tools": len(tools_storage["definitions"]),
            "client_tools": len(tools_engine.client_tools),
            "server_tools": len(tools_engine.server_tools),
            "system_tools": len(tools_engine.system_tools),
            "total_executions": len(tools_storage["executions"])
        }
    }

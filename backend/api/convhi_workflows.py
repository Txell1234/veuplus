#!/usr/bin/env python3
"""
ConvHi Workflows System - Sistema complet de workflows visuals
Suport per nodes, edges, fluxos complexos i execució dinàmica
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
import asyncio
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger("veuplus.workflows")

router = APIRouter(prefix="/api/convhi/workflows", tags=["ConvHi Workflows"])

# Enums
class NodeType(str, Enum):
    START = "start"
    SUBAGENT = "subagent"
    TOOL = "tool"
    TRANSFER = "transfer"
    END = "end"
    EXTERNAL_API = "external_api"
    CONVHI_CALL = "convhi_call"
    WEBHOOK = "webhook"
    DATABASE = "database"

class EdgeType(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    CONDITIONAL = "conditional"

class TransitionType(str, Enum):
    UNCONDITIONAL = "unconditional"
    LLM_CONDITION = "llm_condition"
    TOOL_RESULT = "tool_result"

# Models
class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    name: str
    description: str
    position: Dict[str, float]  # x, y coordinates
    config: Dict[str, Any] = {}
    created_at: str
    updated_at: str

class WorkflowEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    type: EdgeType
    transition_type: TransitionType
    condition: Optional[str] = None  # For LLM conditions
    label: str = ""
    created_at: str
    updated_at: str

class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str
    agent_id: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    enabled: bool = True
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}

class WorkflowExecution(BaseModel):
    id: str
    workflow_id: str
    agent_id: str
    current_node_id: str
    conversation_id: str
    state: Dict[str, Any] = {}
    history: List[Dict[str, Any]] = []
    status: str = "running"  # running, completed, failed, paused
    created_at: str
    updated_at: str

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    agent_id: str
    conversation_id: str
    initial_state: Dict[str, Any] = {}
    user_input: str = ""

# In-memory storage
workflows_storage = {
    "definitions": {},
    "executions": {},
    "active_executions": {}  # conversation_id -> execution_id
}

class WorkflowEngine:
    def __init__(self):
        self._initialize_default_workflows()
    
    def _initialize_default_workflows(self):
        """Inicialitzar workflows per defecte"""
        
        # Workflow bàsic de suport
        support_workflow = WorkflowDefinition(
            id="basic_support_workflow",
            name="Workflow de Suport Bàsic",
            description="Workflow bàsic per atenció al client",
            agent_id="default",
            nodes=[
                WorkflowNode(
                    id="start_node",
                    type=NodeType.START,
                    name="Inici",
                    description="Punt d'inici del workflow",
                    position={"x": 100, "y": 100},
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="greeting_node",
                    type=NodeType.SUBAGENT,
                    name="Salutació",
                    description="Saludar l'usuari i identificar el problema",
                    position={"x": 300, "y": 100},
                    config={
                        "system_prompt": "Saluda cordialment l'usuari i pregunta en què pots ajudar.",
                        "llm_provider": "openai",
                        "llm_model": "gpt-4o-mini"
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="problem_analysis_node",
                    type=NodeType.SUBAGENT,
                    name="Anàlisi del Problema",
                    description="Analitzar el problema de l'usuari",
                    position={"x": 500, "y": 100},
                    config={
                        "system_prompt": "Analitza el problema de l'usuari i determina si pots resoldre'l o cal transferir a un agent humà.",
                        "llm_provider": "openai",
                        "llm_model": "gpt-4o-mini"
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="knowledge_search_node",
                    type=NodeType.TOOL,
                    name="Cerca de Coneixement",
                    description="Cercar informació rellevant",
                    position={"x": 500, "y": 250},
                    config={
                        "tool_id": "system_knowledge_search",
                        "parameters": {
                            "query": "{{user_problem}}",
                            "max_results": 5
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="solution_node",
                    type=NodeType.SUBAGENT,
                    name="Proporcionar Solució",
                    description="Proporcionar solució basada en el coneixement",
                    position={"x": 700, "y": 100},
                    config={
                        "system_prompt": "Proporciona una solució clara i útil basada en la informació trobada.",
                        "llm_provider": "openai",
                        "llm_model": "gpt-4o-mini"
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="transfer_node",
                    type=NodeType.TRANSFER,
                    name="Transferir a Agent Humà",
                    description="Transferir a un agent humà si cal",
                    position={"x": 700, "y": 250},
                    config={
                        "tool_id": "system_transfer_human",
                        "parameters": {
                            "department": "support",
                            "priority": "normal"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="end_node",
                    type=NodeType.END,
                    name="Final",
                    description="Finalitzar la conversa",
                    position={"x": 900, "y": 100},
                    config={
                        "tool_id": "system_end_call",
                        "parameters": {
                            "reason": "Conversa completada"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            ],
            edges=[
                WorkflowEdge(
                    id="start_to_greeting",
                    source_node_id="start_node",
                    target_node_id="greeting_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Iniciar conversa",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="greeting_to_analysis",
                    source_node_id="greeting_node",
                    target_node_id="problem_analysis_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Analitzar problema",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="analysis_to_knowledge",
                    source_node_id="problem_analysis_node",
                    target_node_id="knowledge_search_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.LLM_CONDITION,
                    condition="El problema requereix informació específica",
                    label="Cercar informació",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="knowledge_to_solution",
                    source_node_id="knowledge_search_node",
                    target_node_id="solution_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Proporcionar solució",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="analysis_to_transfer",
                    source_node_id="problem_analysis_node",
                    target_node_id="transfer_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.LLM_CONDITION,
                    condition="El problema requereix atenció humana",
                    label="Transferir a agent humà",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="solution_to_end",
                    source_node_id="solution_node",
                    target_node_id="end_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Finalitzar",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="transfer_to_end",
                    source_node_id="transfer_node",
                    target_node_id="end_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Finalitzar transferència",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            ],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Workflow avançat amb connexions externes
        advanced_workflow = WorkflowDefinition(
            id="advanced_support_workflow",
            name="Workflow de Suport Avançat",
            description="Workflow amb connexions externes i crides entre agents",
            agent_id="default",
            nodes=[
                WorkflowNode(
                    id="start_node_advanced",
                    type=NodeType.START,
                    name="Inici Avançat",
                    description="Punt d'inici del workflow avançat",
                    position={"x": 100, "y": 100},
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="greeting_node_advanced",
                    type=NodeType.SUBAGENT,
                    name="Salutació Intel·ligent",
                    description="Saludar i analitzar l'usuari",
                    position={"x": 300, "y": 100},
                    config={
                        "system_prompt": "Saluda cordialment l'usuari i analitza el seu problema. Determina la seva urgència i tipus.",
                        "llm_provider": "openai",
                        "llm_model": "gpt-4o-mini"
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="external_api_node",
                    type=NodeType.EXTERNAL_API,
                    name="Consultar API Externa",
                    description="Consultar informació externa",
                    position={"x": 500, "y": 100},
                    config={
                        "connection_id": "voice_system_connection",
                        "method": "GET",
                        "path": "/voices",
                        "data": {
                            "language": "{{user_language}}",
                            "query": "{{user_problem}}"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="convhi_call_node",
                    type=NodeType.CONVHI_CALL,
                    name="Cridar Agent Especialista",
                    description="Cridar agent especialista en el problema",
                    position={"x": 500, "y": 250},
                    config={
                        "target_agent_id": "specialist_agent",
                        "message_template": "L'usuari té aquest problema: {{user_problem}}. Pots ajudar?",
                        "priority": "{{urgency_level}}"
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="webhook_node",
                    type=NodeType.WEBHOOK,
                    name="Notificar Sistema Extern",
                    description="Notificar a sistema extern",
                    position={"x": 700, "y": 100},
                    config={
                        "connection_id": "external_webhook",
                        "event_type": "support_request",
                        "data": {
                            "user_id": "{{user_id}}",
                            "problem": "{{user_problem}}",
                            "urgency": "{{urgency_level}}",
                            "agent_response": "{{specialist_response}}"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="database_node",
                    type=NodeType.DATABASE,
                    name="Guardar a Base de Dades",
                    description="Guardar informació de la conversa",
                    position={"x": 700, "y": 250},
                    config={
                        "connection_id": "database_connection",
                        "operation": "insert",
                        "query": "INSERT INTO conversations (user_id, problem, solution, timestamp) VALUES (?, ?, ?, ?)",
                        "data": {
                            "user_id": "{{user_id}}",
                            "problem": "{{user_problem}}",
                            "solution": "{{final_solution}}",
                            "timestamp": "{{current_timestamp}}"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowNode(
                    id="end_node_advanced",
                    type=NodeType.END,
                    name="Final Avançat",
                    description="Finalitzar workflow avançat",
                    position={"x": 900, "y": 175},
                    config={
                        "tool_id": "system_end_call",
                        "parameters": {
                            "reason": "Workflow avançat completat"
                        }
                    },
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            ],
            edges=[
                WorkflowEdge(
                    id="start_to_greeting_advanced",
                    source_node_id="start_node_advanced",
                    target_node_id="greeting_node_advanced",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Iniciar conversa avançada",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="greeting_to_external_api",
                    source_node_id="greeting_node_advanced",
                    target_node_id="external_api_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.LLM_CONDITION,
                    condition="El problema requereix informació externa",
                    label="Consultar API externa",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="greeting_to_convhi_call",
                    source_node_id="greeting_node_advanced",
                    target_node_id="convhi_call_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.LLM_CONDITION,
                    condition="El problema requereix especialista",
                    label="Cridar agent especialista",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="external_api_to_webhook",
                    source_node_id="external_api_node",
                    target_node_id="webhook_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Notificar sistema extern",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="convhi_call_to_database",
                    source_node_id="convhi_call_node",
                    target_node_id="database_node",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Guardar a base de dades",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="webhook_to_end",
                    source_node_id="webhook_node",
                    target_node_id="end_node_advanced",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Finalitzar",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                WorkflowEdge(
                    id="database_to_end",
                    source_node_id="database_node",
                    target_node_id="end_node_advanced",
                    type=EdgeType.FORWARD,
                    transition_type=TransitionType.UNCONDITIONAL,
                    label="Finalitzar",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
            ],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Guardar workflows per defecte
        workflows_storage["definitions"][support_workflow.id] = support_workflow.dict()
        workflows_storage["definitions"][advanced_workflow.id] = advanced_workflow.dict()
        
        logger.info(f"✅ {len([support_workflow, advanced_workflow])} workflows per defecte inicialitzats")
    
    async def create_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Crear nou workflow"""
        try:
            workflow.created_at = datetime.now().isoformat()
            workflow.updated_at = datetime.now().isoformat()
            
            workflows_storage["definitions"][workflow.id] = workflow.dict()
            
            logger.info(f"✅ Workflow creat: {workflow.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant workflow: {e}")
            return False
    
    async def execute_workflow(self, request: WorkflowExecutionRequest) -> WorkflowExecution:
        """Executar workflow"""
        try:
            # Verificar que el workflow existeix
            if request.workflow_id not in workflows_storage["definitions"]:
                raise ValueError(f"Workflow {request.workflow_id} no trobat")
            
            workflow_data = workflows_storage["definitions"][request.workflow_id]
            workflow = WorkflowDefinition(**workflow_data)
            
            # Crear execució
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=request.workflow_id,
                agent_id=request.agent_id,
                current_node_id=self._get_start_node_id(workflow),
                conversation_id=request.conversation_id,
                state=request.initial_state.copy(),
                status="running",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Guardar execució
            workflows_storage["executions"][execution_id] = execution.dict()
            workflows_storage["active_executions"][request.conversation_id] = execution_id
            
            # Executar primer node
            await self._execute_node(execution, request.user_input)
            
            logger.info(f"✅ Workflow executat: {workflow.name}")
            return execution
            
        except Exception as e:
            logger.error(f"Error executant workflow: {e}")
            raise
    
    async def continue_workflow(self, conversation_id: str, user_input: str) -> Optional[WorkflowExecution]:
        """Continuar execució de workflow"""
        try:
            if conversation_id not in workflows_storage["active_executions"]:
                return None
            
            execution_id = workflows_storage["active_executions"][conversation_id]
            if execution_id not in workflows_storage["executions"]:
                return None
            
            execution_data = workflows_storage["executions"][execution_id]
            execution = WorkflowExecution(**execution_data)
            
            if execution.status != "running":
                return execution
            
            # Continuar execució
            await self._execute_node(execution, user_input)
            
            return execution
            
        except Exception as e:
            logger.error(f"Error continuant workflow: {e}")
            return None
    
    async def _execute_node(self, execution: WorkflowExecution, user_input: str):
        """Executar node específic"""
        try:
            workflow_data = workflows_storage["definitions"][execution.workflow_id]
            workflow = WorkflowDefinition(**workflow_data)
            
            # Trobar node actual
            current_node = None
            for node in workflow.nodes:
                if node.id == execution.current_node_id:
                    current_node = node
                    break
            
            if not current_node:
                raise ValueError(f"Node {execution.current_node_id} no trobat")
            
            # Executar segons el tipus de node
            if current_node.type == NodeType.START:
                result = await self._execute_start_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.SUBAGENT:
                result = await self._execute_subagent_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.TOOL:
                result = await self._execute_tool_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.TRANSFER:
                result = await self._execute_transfer_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.END:
                result = await self._execute_end_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.EXTERNAL_API:
                result = await self._execute_external_api_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.CONVHI_CALL:
                result = await self._execute_convhi_call_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.WEBHOOK:
                result = await self._execute_webhook_node(current_node, user_input, execution.state)
            elif current_node.type == NodeType.DATABASE:
                result = await self._execute_database_node(current_node, user_input, execution.state)
            else:
                raise ValueError(f"Tipus de node {current_node.type} no suportat")
            
            # Actualitzar estat
            execution.state.update(result.get("state_updates", {}))
            execution.history.append({
                "node_id": current_node.id,
                "node_name": current_node.name,
                "input": user_input,
                "output": result.get("output", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            # Determinar següent node
            next_node_id = await self._determine_next_node(workflow, current_node, result, execution.state)
            
            if next_node_id:
                execution.current_node_id = next_node_id
            else:
                execution.status = "completed"
                # Eliminar de execucions actives
                if execution.conversation_id in workflows_storage["active_executions"]:
                    del workflows_storage["active_executions"][execution.conversation_id]
            
            execution.updated_at = datetime.now().isoformat()
            
            # Actualitzar execució
            workflows_storage["executions"][execution.id] = execution.dict()
            
        except Exception as e:
            logger.error(f"Error executant node: {e}")
            execution.status = "failed"
            execution.updated_at = datetime.now().isoformat()
            workflows_storage["executions"][execution.id] = execution.dict()
    
    async def _execute_start_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node d'inici"""
        return {
            "output": "Workflow iniciat",
            "state_updates": {"workflow_started": True}
        }
    
    async def _execute_subagent_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de subagent"""
        try:
            config = node.config
            system_prompt = config.get("system_prompt", "Ets un assistent útil.")
            llm_provider = config.get("llm_provider", "openai")
            llm_model = config.get("llm_model", "gpt-4o-mini")
            
            # Substituir variables dinàmiques
            system_prompt = self._substitute_variables(system_prompt, state)
            
            # Generar resposta amb LLM
            from .llm_integration import generate_llm_response
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            llm_response = await generate_llm_response(
                provider=llm_provider,
                model=llm_model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            if llm_response.success:
                return {
                    "output": llm_response.content,
                    "state_updates": {
                        f"{node.id}_response": llm_response.content,
                        "last_llm_provider": llm_provider,
                        "last_llm_model": llm_model
                    }
                }
            else:
                return {
                    "output": "Ho sento, hi ha hagut un error processant la teva petició.",
                    "state_updates": {f"{node.id}_error": llm_response.error}
                }
                
        except Exception as e:
            logger.error(f"Error executant subagent node: {e}")
            return {
                "output": "Error executant node de subagent",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_tool_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node d'eina"""
        try:
            config = node.config
            tool_id = config.get("tool_id")
            parameters = config.get("parameters", {})
            
            if not tool_id:
                raise ValueError("tool_id requerit per node d'eina")
            
            # Substituir variables dinàmiques en paràmetres
            processed_parameters = {}
            for key, value in parameters.items():
                if isinstance(value, str):
                    processed_parameters[key] = self._substitute_variables(value, state)
                else:
                    processed_parameters[key] = value
            
            # Executar eina
            from .convhi_tools import tools_engine, ToolExecutionRequest
            
            tool_request = ToolExecutionRequest(
                tool_id=tool_id,
                agent_id=state.get("agent_id", "default"),
                parameters=processed_parameters,
                context=state
            )
            
            tool_result = await tools_engine.execute_tool(tool_request)
            
            if tool_result.success:
                return {
                    "output": f"Eina executada: {tool_result.result}",
                    "state_updates": {
                        f"{node.id}_result": tool_result.result,
                        f"{node.id}_success": True
                    }
                }
            else:
                return {
                    "output": f"Error executant eina: {tool_result.error}",
                    "state_updates": {
                        f"{node.id}_error": tool_result.error,
                        f"{node.id}_success": False
                    }
                }
                
        except Exception as e:
            logger.error(f"Error executant tool node: {e}")
            return {
                "output": f"Error executant node d'eina: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_transfer_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de transferència"""
        try:
            config = node.config
            tool_id = config.get("tool_id", "system_transfer_human")
            parameters = config.get("parameters", {})
            
            # Substituir variables dinàmiques
            processed_parameters = {}
            for key, value in parameters.items():
                if isinstance(value, str):
                    processed_parameters[key] = self._substitute_variables(value, state)
                else:
                    processed_parameters[key] = value
            
            # Executar transferència
            from .convhi_tools import tools_engine, ToolExecutionRequest
            
            tool_request = ToolExecutionRequest(
                tool_id=tool_id,
                agent_id=state.get("agent_id", "default"),
                parameters=processed_parameters,
                context=state
            )
            
            tool_result = await tools_engine.execute_tool(tool_request)
            
            return {
                "output": f"Transferència iniciada: {tool_result.result}",
                "state_updates": {
                    f"{node.id}_transfer_result": tool_result.result,
                    "transfer_initiated": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error executant transfer node: {e}")
            return {
                "output": f"Error en transferència: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_end_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de finalització"""
        try:
            config = node.config
            tool_id = config.get("tool_id", "system_end_call")
            parameters = config.get("parameters", {})
            
            # Executar finalització
            from .convhi_tools import tools_engine, ToolExecutionRequest
            
            tool_request = ToolExecutionRequest(
                tool_id=tool_id,
                agent_id=state.get("agent_id", "default"),
                parameters=parameters,
                context=state
            )
            
            tool_result = await tools_engine.execute_tool(tool_request)
            
            return {
                "output": f"Conversa finalitzada: {tool_result.result}",
                "state_updates": {
                    "conversation_ended": True,
                    "end_reason": parameters.get("reason", "Workflow completed")
                }
            }
            
        except Exception as e:
            logger.error(f"Error executant end node: {e}")
            return {
                "output": f"Error finalitzant conversa: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    def _substitute_variables(self, text: str, state: Dict[str, Any]) -> str:
        """Substituir variables dinàmiques en text"""
        try:
            import re
            
            # Trobar variables en format {{variable_name}}
            pattern = r'\{\{([^}]+)\}\}'
            
            def replace_variable(match):
                var_name = match.group(1).strip()
                return str(state.get(var_name, f"{{{{{var_name}}}}}"))
            
            return re.sub(pattern, replace_variable, text)
            
        except Exception as e:
            logger.error(f"Error substituint variables: {e}")
            return text
    
    async def _determine_next_node(self, workflow: WorkflowDefinition, current_node: WorkflowNode, 
                                 result: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
        """Determinar següent node basat en edges"""
        try:
            # Trobar edges sortints del node actual
            outgoing_edges = []
            for edge in workflow.edges:
                if edge.source_node_id == current_node.id:
                    outgoing_edges.append(edge)
            
            if not outgoing_edges:
                return None
            
            # Si només hi ha un edge, seguir-lo
            if len(outgoing_edges) == 1:
                return outgoing_edges[0].target_node_id
            
            # Si hi ha múltiples edges, avaluar condicions
            for edge in outgoing_edges:
                if edge.transition_type == TransitionType.UNCONDITIONAL:
                    return edge.target_node_id
                elif edge.transition_type == TransitionType.LLM_CONDITION:
                    # Avaluar condició amb LLM
                    if await self._evaluate_llm_condition(edge.condition, result, state):
                        return edge.target_node_id
                elif edge.transition_type == TransitionType.TOOL_RESULT:
                    # Avaluar resultat d'eina
                    if self._evaluate_tool_result(edge.condition, result, state):
                        return edge.target_node_id
            
            # Si cap condició es compleix, agafar el primer edge
            return outgoing_edges[0].target_node_id
            
        except Exception as e:
            logger.error(f"Error determinant següent node: {e}")
            return None
    
    async def _evaluate_llm_condition(self, condition: str, result: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """Avaluar condició amb LLM"""
        try:
            from .llm_integration import generate_llm_response
            
            context = {
                "condition": condition,
                "result": result,
                "state": state
            }
            
            prompt = f"""
            Avàlua si aquesta condició es compleix basant-te en el context:
            
            Condició: "{condition}"
            
            Context:
            - Resultat de l'última acció: {result.get('output', '')}
            - Estat actual: {state}
            
            Respon només "true" o "false".
            """
            
            llm_response = await generate_llm_response(
                provider="openai",
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ets un evaluador de condicions. Respon només 'true' o 'false'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            if llm_response.success:
                return llm_response.content.strip().lower() == "true"
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error avaluant condició LLM: {e}")
            return False
    
    def _evaluate_tool_result(self, condition: str, result: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """Avaluar resultat d'eina"""
        try:
            # Implementació bàsica - en producció millorar
            if "success" in condition:
                return result.get("state_updates", {}).get("success", False)
            elif "error" in condition:
                return "error" in result.get("state_updates", {})
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error avaluant resultat d'eina: {e}")
            return False
    
    def _get_start_node_id(self, workflow: WorkflowDefinition) -> str:
        """Obtenir ID del node d'inici"""
        for node in workflow.nodes:
            if node.type == NodeType.START:
                return node.id
        raise ValueError("No s'ha trobat node d'inici al workflow")
    
    async def _execute_external_api_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node d'API externa"""
        try:
            config = node.config
            connection_id = config.get("connection_id")
            method = config.get("method", "POST")
            path = config.get("path", "")
            data_template = config.get("data", {})
            
            if not connection_id:
                raise ValueError("connection_id requerit per node d'API externa")
            
            # Substituir variables dinàmiques en dades
            processed_data = {}
            for key, value in data_template.items():
                if isinstance(value, str):
                    processed_data[key] = self._substitute_variables(value, state)
                else:
                    processed_data[key] = value
            
            # Afegir input de l'usuari si cal
            if "user_input" in processed_data:
                processed_data["user_input"] = user_input
            
            # Cridar connexió externa
            from .convhi_connections import connections_engine, ConnectionRequest
            
            connection_request = ConnectionRequest(
                connection_id=connection_id,
                method=method,
                path=path,
                data=processed_data
            )
            
            connection_response = await connections_engine.call_connection(connection_request)
            
            if connection_response.success:
                return {
                    "output": f"API externa cridada correctament: {connection_response.data}",
                    "state_updates": {
                        f"{node.id}_api_response": connection_response.data,
                        f"{node.id}_success": True,
                        "last_external_api": connection_id
                    }
                }
            else:
                return {
                    "output": f"Error cridant API externa: {connection_response.error}",
                    "state_updates": {
                        f"{node.id}_error": connection_response.error,
                        f"{node.id}_success": False
                    }
                }
                
        except Exception as e:
            logger.error(f"Error executant external API node: {e}")
            return {
                "output": f"Error executant node d'API externa: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_convhi_call_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de crida ConvHi"""
        try:
            config = node.config
            target_agent_id = config.get("target_agent_id")
            message_template = config.get("message_template", "{{user_input}}")
            priority = config.get("priority", "normal")
            
            if not target_agent_id:
                raise ValueError("target_agent_id requerit per node de crida ConvHi")
            
            # Substituir variables dinàmiques en el missatge
            processed_message = self._substitute_variables(message_template, state)
            if "{{user_input}}" in processed_message:
                processed_message = processed_message.replace("{{user_input}}", user_input)
            
            # Cridar agent ConvHi
            from .convhi_connections import connections_engine, ConvHiAgentCall
            
            convhi_call = ConvHiAgentCall(
                source_agent_id=state.get("agent_id", "workflow"),
                target_agent_id=target_agent_id,
                message=processed_message,
                context=state.copy(),
                priority=priority
            )
            
            call_result = await connections_engine.call_convhi_agent_direct(convhi_call)
            
            if call_result["success"]:
                return {
                    "output": f"Agent ConvHi cridat correctament: {call_result['response']['response']}",
                    "state_updates": {
                        f"{node.id}_convhi_response": call_result["response"],
                        f"{node.id}_call_id": call_result["call_id"],
                        f"{node.id}_success": True,
                        "last_convhi_call": target_agent_id
                    }
                }
            else:
                return {
                    "output": f"Error cridant agent ConvHi: {call_result['error']}",
                    "state_updates": {
                        f"{node.id}_error": call_result["error"],
                        f"{node.id}_success": False
                    }
                }
                
        except Exception as e:
            logger.error(f"Error executant ConvHi call node: {e}")
            return {
                "output": f"Error executant node de crida ConvHi: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_webhook_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de webhook"""
        try:
            config = node.config
            connection_id = config.get("connection_id")
            event_type = config.get("event_type", "workflow_event")
            data_template = config.get("data", {})
            
            if not connection_id:
                raise ValueError("connection_id requerit per node de webhook")
            
            # Substituir variables dinàmiques
            processed_data = {}
            for key, value in data_template.items():
                if isinstance(value, str):
                    processed_data[key] = self._substitute_variables(value, state)
                else:
                    processed_data[key] = value
            
            # Afegir dades de l'event
            processed_data.update({
                "event_type": event_type,
                "user_input": user_input,
                "timestamp": datetime.now().isoformat(),
                "workflow_state": state
            })
            
            # Cridar webhook
            from .convhi_connections import connections_engine, ConnectionRequest
            
            webhook_request = ConnectionRequest(
                connection_id=connection_id,
                method="POST",
                data=processed_data
            )
            
            webhook_response = await connections_engine.call_connection(webhook_request)
            
            if webhook_response.success:
                return {
                    "output": f"Webhook enviat correctament: {webhook_response.data}",
                    "state_updates": {
                        f"{node.id}_webhook_response": webhook_response.data,
                        f"{node.id}_success": True,
                        "last_webhook_event": event_type
                    }
                }
            else:
                return {
                    "output": f"Error enviant webhook: {webhook_response.error}",
                    "state_updates": {
                        f"{node.id}_error": webhook_response.error,
                        f"{node.id}_success": False
                    }
                }
                
        except Exception as e:
            logger.error(f"Error executant webhook node: {e}")
            return {
                "output": f"Error executant node de webhook: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    async def _execute_database_node(self, node: WorkflowNode, user_input: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executar node de base de dades"""
        try:
            config = node.config
            connection_id = config.get("connection_id")
            operation = config.get("operation", "select")  # select, insert, update, delete
            query_template = config.get("query", "")
            data_template = config.get("data", {})
            
            if not connection_id:
                raise ValueError("connection_id requerit per node de base de dades")
            
            # Substituir variables dinàmiques
            processed_query = self._substitute_variables(query_template, state)
            processed_data = {}
            for key, value in data_template.items():
                if isinstance(value, str):
                    processed_data[key] = self._substitute_variables(value, state)
                else:
                    processed_data[key] = value
            
            # Simular operació de base de dades (en producció implementar real)
            if operation == "select":
                # Simular SELECT
                result = {
                    "operation": "select",
                    "query": processed_query,
                    "results": [
                        {"id": 1, "name": "Example", "value": "Test"},
                        {"id": 2, "name": "Another", "value": "Data"}
                    ],
                    "count": 2
                }
            elif operation == "insert":
                # Simular INSERT
                result = {
                    "operation": "insert",
                    "data": processed_data,
                    "inserted_id": 123,
                    "success": True
                }
            elif operation == "update":
                # Simular UPDATE
                result = {
                    "operation": "update",
                    "query": processed_query,
                    "data": processed_data,
                    "affected_rows": 1,
                    "success": True
                }
            elif operation == "delete":
                # Simular DELETE
                result = {
                    "operation": "delete",
                    "query": processed_query,
                    "affected_rows": 1,
                    "success": True
                }
            else:
                raise ValueError(f"Operació de base de dades {operation} no suportada")
            
            return {
                "output": f"Operació de base de dades executada: {result}",
                "state_updates": {
                    f"{node.id}_db_result": result,
                    f"{node.id}_success": True,
                    "last_db_operation": operation
                }
            }
            
        except Exception as e:
            logger.error(f"Error executant database node: {e}")
            return {
                "output": f"Error executant node de base de dades: {e}",
                "state_updates": {f"{node.id}_error": str(e)}
            }
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Obtenir workflow específic"""
        if workflow_id in workflows_storage["definitions"]:
            return WorkflowDefinition(**workflows_storage["definitions"][workflow_id])
        return None
    
    def get_all_workflows(self, agent_id: Optional[str] = None) -> List[WorkflowDefinition]:
        """Obtenir tots els workflows"""
        workflows = []
        for workflow_data in workflows_storage["definitions"].values():
            workflow = WorkflowDefinition(**workflow_data)
            if not agent_id or workflow.agent_id == agent_id:
                workflows.append(workflow)
        return workflows
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtenir execució específica"""
        if execution_id in workflows_storage["executions"]:
            return WorkflowExecution(**workflows_storage["executions"][execution_id])
        return None

# Instància global
workflow_engine = WorkflowEngine()

# Endpoints
@router.get("/")
async def get_workflows(agent_id: Optional[str] = None):
    """Obtenir tots els workflows"""
    try:
        workflows = workflow_engine.get_all_workflows(agent_id)
        
        return {
            "success": True,
            "workflows": [workflow.dict() for workflow in workflows],
            "total": len(workflows)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Obtenir workflow específic"""
    try:
        workflow = workflow_engine.get_workflow(workflow_id)
        
        if workflow:
            return {
                "success": True,
                "workflow": workflow.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Workflow no trobat")
        
    except Exception as e:
        logger.error(f"Error obtenint workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_workflow(workflow: WorkflowDefinition):
    """Crear nou workflow"""
    try:
        success = await workflow_engine.create_workflow(workflow)
        
        if success:
            return {
                "success": True,
                "message": f"Workflow {workflow.name} creat correctament",
                "workflow": workflow.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant workflow")
        
    except Exception as e:
        logger.error(f"Error creant workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_workflow(request: WorkflowExecutionRequest):
    """Executar workflow"""
    try:
        execution = await workflow_engine.execute_workflow(request)
        
        return {
            "success": True,
            "execution": execution.dict(),
            "message": "Workflow executat correctament"
        }
        
    except Exception as e:
        logger.error(f"Error executant workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/continue/{conversation_id}")
async def continue_workflow(conversation_id: str, user_input: str):
    """Continuar execució de workflow"""
    try:
        execution = await workflow_engine.continue_workflow(conversation_id, user_input)
        
        if execution:
            return {
                "success": True,
                "execution": execution.dict(),
                "message": "Workflow continuat correctament"
            }
        else:
            raise HTTPException(status_code=404, detail="Execució de workflow no trobada")
        
    except Exception as e:
        logger.error(f"Error continuant workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Obtenir execució específica"""
    try:
        execution = workflow_engine.get_execution(execution_id)
        
        if execution:
            return {
                "success": True,
                "execution": execution.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Execució no trobada")
        
    except Exception as e:
        logger.error(f"Error obtenint execució: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def workflows_health():
    """Health check del sistema de workflows"""
    return {
        "status": "ok",
        "message": "Sistema de workflows funcionant",
        "stats": {
            "total_workflows": len(workflows_storage["definitions"]),
            "total_executions": len(workflows_storage["executions"]),
            "active_executions": len(workflows_storage["active_executions"])
        }
    }

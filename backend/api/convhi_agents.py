#!/usr/bin/env python3
"""
ConvHi Agents API - Conversacionals Hiperrealistes
Sistema complet per agents de veu conversacionals amb:
- ASR (Speech to Text)
- LLM (Language Model)
- TTS (Text to Speech)
- Turn Taking Model
- Knowledge Base
- Monitoring
"""

from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import asyncio
import json
import base64
import tempfile
import os
import re
from datetime import datetime
from pathlib import Path

from .convhi_tools import tools_engine, ToolExecutionRequest


def apply_dynamic_variables(text: str, variables: Dict[str, Any]) -> str:
    """Replace {{variable}} placeholders in text using provided variables."""
    if not text or not variables:
        return text

    def resolver(match: re.Match) -> str:
        key = match.group(1).strip()
        parts = key.split(".")
        value: Any = variables
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return match.group(0)
        return str(value)

    return re.sub(r"\{\{([\w\.\-]+)\}\}", resolver, text)


def merge_overrides(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Return copy of base dict updated with overrides."""
    if not overrides:
        return dict(base)
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_overrides(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged

logger = logging.getLogger("veuplus.convhi")

router = APIRouter(prefix="/api/convhi", tags=["ConvHi Agents"])

# Models
class ConvHiAgent(BaseModel):
    id: str
    name: str
    description: str
    llm_provider: str  # openai, gemini, claude, local
    llm_model: str
    api_key: Optional[str] = None
    voice_system: str  # edge-tts, catalan, alia, external
    voice_id: str
    external_voice_api: Optional[str] = None
    language: str
    knowledge_base_enabled: bool = True
    turn_taking_enabled: bool = True
    asr_enabled: bool = True
    monitoring_enabled: bool = True
    temperature: float = 0.7
    max_tokens: int = 1000
    voice_speed: float = 1.0
    settings: Optional[Dict[str, Any]] = None
    dynamic_variables: Dict[str, Any] = {}
    overrides: Dict[str, Any] = {}
    rag_enabled: bool = True
    rag_top_k: int = 5
    
    # 🆕 NOVES FUNCIONALITATS
    first_message: Optional[str] = None
    disable_interruptions: bool = False
    enabled_tools: List[str] = []
    additional_languages: List[str] = []
    language_auto_detect: bool = False
    max_response_length: int = 500
    stop_sequences: List[str] = []
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class ConversationMessage(BaseModel):
    agent_id: str
    message: str
    audio_data: Optional[str] = None  # base64 audio
    message_type: str = "text"  # text, audio
    timestamp: Optional[datetime] = None

class TurnTakingRequest(BaseModel):
    agent_id: str
    conversation_context: List[Dict[str, Any]]
    current_speaker: str
    silence_duration: float
    audio_level: float

# Importar base de dades persistent
from database_sql import db

# In-memory storage (caché - backup a SQLite)
convhi_agents = {}
conversations = {}
knowledge_base = {}

# Carregar agents des de la base de dades al iniciar
def load_agents_from_db():
    """Carregar tots els agents des de la base de dades"""
    try:
        agents = db.get_all_convhi_agents()
        for agent in agents:
            convhi_agents[agent['id']] = agent
        logger.info(f"✅ {len(agents)} agents carregats des de la base de dades")
    except Exception as e:
        logger.error(f"Error carregant agents: {e}")

# Carregar agents a l'importar el mòdul
load_agents_from_db()

# ASR Engine
class ASREngine:
    def __init__(self):
        self.whisper_available = False
        self._initialize_whisper()
    
    def _initialize_whisper(self):
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            self.whisper_available = True
            logger.info("âœ… Whisper ASR inicialitzat")
        except ImportError:
            logger.warning("âš ï¸ Whisper no disponible")
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "auto") -> str:
        """Transcriure Ã udio a text"""
        if not self.whisper_available:
            raise HTTPException(status_code=500, detail="ASR no disponible")
        
        try:
            # Guardar Ã udio temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Transcriure amb Whisper amb timeout de 60 segons
            import asyncio
            def run_transcription():
                return self.whisper_model.transcribe(tmp_path, language=language if language != "auto" else None)
            
            # Executar en thread pool per permetre timeout
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, run_transcription),
                timeout=60.0
            )
            transcription = result["text"].strip()
            
            # Netejar fitxer temporal
            os.unlink(tmp_path)
            
            logger.info(f"ðŸŽ¤ ASR: '{transcription[:50]}...'")
            return transcription
            
        except asyncio.TimeoutError:
            logger.error("ASR timeout després de 60 segons")
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
            raise HTTPException(status_code=408, detail="ASR timeout: l'àudio és massa llarg o complex")
        except Exception as e:
            logger.error(f"Error en ASR: {e}")
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            raise HTTPException(status_code=500, detail=f"Error en transcripció: {e}")

# Turn Taking Model
class TurnTakingModel:
    def __init__(self):
        self.silence_threshold = 1.5  # segons
        self.audio_threshold = 0.1    # nivell d'Ã udio mÃ­nim
    
    async def should_speak(self, request: TurnTakingRequest) -> Dict[str, Any]:
        """Determinar si l'agent hauria de parlar"""
        try:
            # AnÃ lisi bÃ sic de torns conversacionals
            should_speak = False
            confidence = 0.0
            reason = ""
            
            # Regla 1: Silenci prolongat
            if request.silence_duration > self.silence_threshold:
                should_speak = True
                confidence = 0.8
                reason = "Silenci prolongat detectat"
            
            # Regla 2: Pregunta directa
            last_message = request.conversation_context[-1] if request.conversation_context else {}
            if "?" in last_message.get("content", ""):
                should_speak = True
                confidence = 0.9
                reason = "Pregunta detectada"
            
            # Regla 3: Nivell d'Ã udio baix
            if request.audio_level < self.audio_threshold and request.silence_duration > 0.5:
                should_speak = True
                confidence = 0.7
                reason = "Nivell d'Ã udio baix"
            
            return {
                "should_speak": should_speak,
                "confidence": confidence,
                "reason": reason,
                "silence_duration": request.silence_duration,
                "audio_level": request.audio_level
            }
            
        except Exception as e:
            logger.error(f"Error en turn taking: {e}")
            return {
                "should_speak": False,
                "confidence": 0.0,
                "reason": f"Error: {e}",
                "silence_duration": request.silence_duration,
                "audio_level": request.audio_level
            }

# Knowledge Base
class KnowledgeBase:
    def __init__(self):
        self.kb_data = {}
    
    async def add_knowledge(self, agent_id: str, knowledge: Dict[str, Any]):
        """Afegir coneixement a l'agent"""
        if agent_id not in self.kb_data:
            self.kb_data[agent_id] = []
        
        knowledge_item = {
            "id": len(self.kb_data[agent_id]) + 1,
            "content": knowledge.get("content", ""),
            "category": knowledge.get("category", "general"),
            "tags": knowledge.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "confidence": knowledge.get("confidence", 1.0)
        }
        
        self.kb_data[agent_id].append(knowledge_item)
        logger.info(f"ðŸ“š Coneixement afegit a agent {agent_id}")
        return knowledge_item
    
    async def search_knowledge(self, agent_id: str, query: str) -> List[Dict[str, Any]]:
        """Cercar coneixement rellevant"""
        if agent_id not in self.kb_data:
            return []
        
        results = []
        query_lower = query.lower()
        
        for item in self.kb_data[agent_id]:
            # Cerca simple per contingut i tags
            if (query_lower in item["content"].lower() or 
                any(query_lower in tag.lower() for tag in item["tags"])):
                results.append(item)
        
        # Ordenar per confianÃ§a
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:5]  # Top 5 resultats

# Monitoring - ✅ MILLORAT: Persistent amb SQLite
class MonitoringSystem:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "veuplus.db"
        self._init_database()
    
    def _init_database(self):
        """Inicialitzar taula de monitoring a SQLite"""
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN DEFAULT 1,
                response_time REAL DEFAULT 0.0,
                user_message TEXT,
                agent_response TEXT,
                metadata TEXT
            )
        """)
        
        # Índex per millorar consultes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_timestamp 
            ON agent_interactions(agent_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Monitoring database inicialitzat")
    
    async def log_interaction(self, agent_id: str, interaction: Dict[str, Any]):
        """Registrar interacció a SQLite (PERSISTENT)"""
        import sqlite3
        import uuid
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO agent_interactions 
                (id, agent_id, timestamp, success, response_time, user_message, agent_response, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                agent_id,
                datetime.now().isoformat(),
                1 if interaction.get("success", False) else 0,
                interaction.get("response_time", 0.0),
                interaction.get("user_message", "")[:500],
                interaction.get("agent_response", "")[:500],
                json.dumps(interaction.get("metadata", {}))
            ))
            conn.commit()
            logger.info(f"📊 Interacció registrada per agent {agent_id}")
        except Exception as e:
            logger.error(f"Error registrant interacció: {e}")
        finally:
            conn.close()
    
    async def get_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Obtenir mètriques de l'agent (PERSISTENT)"""
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Total interaccions
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                    AVG(response_time) as avg_response_time,
                    MAX(timestamp) as last_interaction
                FROM agent_interactions 
                WHERE agent_id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            return {
                "total_interactions": row[0] or 0,
                "successful_interactions": row[1] or 0,
                "failed_interactions": row[2] or 0,
                "average_response_time": float(row[3]) if row[3] else 0.0,
                "last_interaction": row[4]
            }
        except Exception as e:
            logger.error(f"Error obtenint mètriques: {e}")
            return {
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "average_response_time": 0.0,
                "last_interaction": None
            }
        finally:
            conn.close()

# Inicialitzar components
asr_engine = ASREngine()
turn_taking_model = TurnTakingModel()
knowledge_base_system = KnowledgeBase()
monitoring_system = MonitoringSystem()

# Endpoints
@router.get("/agents")
async def get_convhi_agents():
    """Obtenir tots els agents ConvHi"""
    return {
        "success": True,
        "agents": list(convhi_agents.values()),
        "total": len(convhi_agents)
    }

@router.post("/agents")
async def create_convhi_agent(agent: ConvHiAgent):
    """Crear nou agent ConvHi"""
    try:
        agent.id = f"convhi_{len(convhi_agents) + 1}"
        agent.timestamp = datetime.now().isoformat()
        
        # Guardar a base de dades persistent
        db.save_convhi_agent(agent.dict())
        
        # També guardar en memòria (caché)
        convhi_agents[agent.id] = agent.dict()
        
        # Inicialitzar conversaciÃ³
        conversations[agent.id] = []
        
        logger.info(f"✅ Agent ConvHi creat: {agent.name}")
        return {
            "success": True,
            "agent": agent.dict(),
            "message": f"Agent {agent.name} creat correctament"
        }
        
    except Exception as e:
        logger.error(f"Error creant agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/chat")
async def chat_with_agent(agent_id: str, message: ConversationMessage):
    """Xatejar amb agent ConvHi"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        agent = convhi_agents[agent_id]
        agent_config = merge_overrides(agent, agent.get("overrides"))
        dynamic_variables = agent_config.get("dynamic_variables", {}) or {}
        start_time = datetime.now()
        
        # 1. ASR si Ã©s Ã udio I està habilitat (verificació explícita)
        asr_enabled = agent_config.get("asr_enabled", False)
        
        if asr_enabled and message.message_type == "audio" and message.audio_data:
            audio_bytes = base64.b64decode(message.audio_data)
            transcribed_text = await asr_engine.transcribe_audio(audio_bytes, agent["language"])
            message.message = transcribed_text
            logger.info(f"🎤 ASR: Transcripció completada - '{transcribed_text[:50]}...'")
        elif message.message_type == "audio" and not asr_enabled:
            logger.warning(f"🎤 ASR deshabilitat per l'agent {agent_id} però s'ha rebut àudio")
            message.message = ""
            message.message_type = "text"
        
        # 1.5. Deteccio automatica d'idioma

        tool_context = {"agent_id": agent_id, "conversation_id": f"conv_{agent_id}_{len(conversations[agent_id])}"}
        tool_results: List[Dict[str, Any]] = []

        async def execute_tool(tool_id: str, params: Dict[str, Any]):
            """Executar eina del sistema amb retry logic (ReAct pattern segons imatges)."""
            try:
                tool_request = ToolExecutionRequest(
                    tool_id=tool_id,
                    agent_id=agent_id,
                    parameters=params,
                    context=tool_context
                )
                
                # Retry logic (màxim 3 intents segons imatges MCP)
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        result = await tools_engine.execute_tool(tool_request)
                        if result.success:
                            tool_results.append({
                                "tool_id": tool_id, 
                                "success": True, 
                                "result": result.result, 
                                "error": None,
                                "attempts": attempt + 1
                            })
                            return result
                        else:
                            logger.warning(f"Tool {tool_id} retornà success=False (attempt {attempt + 1})")
                    except Exception as attempt_error:
                        if attempt < max_attempts - 1:
                            logger.warning(f"Error en intent {attempt + 1}/{max_attempts}: {attempt_error}")
                            await asyncio.sleep(0.5 * (attempt + 1))  # Backoff exponencial
                        else:
                            raise
                
                # Tots els intents fallaren
                tool_results.append({
                    "tool_id": tool_id, 
                    "success": False, 
                    "error": "Tots els intents de crida fallaren",
                    "attempts": max_attempts
                })
                return None
                
            except Exception as exc:
                logger.error(f"Error executant eina {tool_id}: {exc}")
                tool_results.append({
                    "tool_id": tool_id, 
                    "success": False, 
                    "error": str(exc)
                })
                return None

        detected_language = agent["language"]  # Per defecte
        language_confidence = None
        language_result = await execute_tool("system_language_detection", {"text": message.message})
        if language_result and language_result.success and isinstance(language_result.result, dict):
            lang_payload = language_result.result
            lang_code = lang_payload.get("language")
            if lang_code and lang_code != "unknown":
                detected_language = lang_code
                language_confidence = lang_payload.get("confidence")
                logger.info(f"[language] Detectat {detected_language} (confidence: {language_confidence})")

        final_message_override: Optional[str] = None
        conversation_should_end = False
        skip_turn_triggered = False
        message_lower = message.message.lower()

        if not message.message.strip():
            skip_result = await execute_tool("system_skip_turn", {"reason": "Entrada buida o sense transcripcio"})
            if skip_result and skip_result.success and isinstance(skip_result.result, dict):
                final_message_override = skip_result.result.get("message")
                skip_turn_triggered = True

        if message.message_type == "audio":
            keywords = re.findall(r"[a-z]+", message_lower)
            silence_guess = 4.0 if not message.message.strip() else 0.5
            audio_level_guess = 0.05 if not message.message.strip() else 0.4
            voicemail_result = await execute_tool("system_voicemail_detection", {"silence_duration": silence_guess, "audio_level": audio_level_guess, "keywords": keywords})
            if voicemail_result and voicemail_result.success and isinstance(voicemail_result.result, dict) and voicemail_result.result.get("voicemail"):
                end_result = await execute_tool("system_end_call", {"reason": "Contestador automatic detectat"})
                if end_result and end_result.success and isinstance(end_result.result, dict):
                    final_message_override = end_result.result.get("message")
                else:
                    final_message_override = "He detectat un contestador automatic. Tanco la conversa."
                conversation_should_end = True

        if not conversation_should_end and not skip_turn_triggered:
            if any(trigger in message_lower for trigger in ["acabar", "finalitzar", "end call", "penja"]):
                end_result = await execute_tool("system_end_call", {"reason": "Usuari ha sol licitat finalitzar la conversa"})
                if end_result and end_result.success and isinstance(end_result.result, dict):
                    final_message_override = end_result.result.get("message")
                conversation_should_end = True

        if not conversation_should_end and not skip_turn_triggered:
            if "transferir" in message_lower or "agent huma" in message_lower:
                number_match = re.search(r"(\+?\d[\d\s\-\.]{5,})", message_lower)
                transfer_success = False

                if number_match:
                    clean_number = re.sub(r"\D+", "", number_match.group(0))
                    transfer_number = f"+{clean_number}" if clean_number and not clean_number.startswith("0") else clean_number
                    transfer_result = await execute_tool("system_transfer_number", {"phone_number": transfer_number, "reason": "Usuari ha demanat transferencia a numero concret", "mode": "blind"})
                    if transfer_result and transfer_result.success and isinstance(transfer_result.result, dict):
                        final_message_override = transfer_result.result.get("message")
                        transfer_success = True
                        conversation_should_end = True

                if not transfer_success:
                    transfer_result = await execute_tool("system_transfer_human", {"department": "support", "priority": "normal", "reason": "Usuari ha demanat parlar amb un agent huma"})
                    if transfer_result and transfer_result.success and isinstance(transfer_result.result, dict):
                        final_message_override = transfer_result.result.get("message")
                        conversation_should_end = True

# 2. Cercar coneixement rellevant (Advanced RAG segons imatge 3)
        knowledge_results = []
        
        # Verificar explícitament que KB està habilitada
        kb_enabled = agent_config.get("knowledge_base_enabled", False)
        rag_enabled = agent_config.get("rag_enabled", False)
        
        if kb_enabled and rag_enabled:
            try:
                from .convhi_knowledge import knowledge_engine, KnowledgeSearchRequest
                
                # Step 1: Query Rewriting (Tècnica RAG avançada)
                # Expandir query per millorar la cerca
                expanded_query = message.message
                if len(message.message) < 20:
                    # Si la query és massa curta, expandir-la
                    expanded_query = f"{message.message} informació detallada document"
                
                search_request = KnowledgeSearchRequest(
                    agent_id=agent_id,
                    query=expanded_query,  # Query reescrita
                    max_results=agent_config.get("rag_top_k", 5),
                    min_confidence=0.3
                )
                
                # Step 2: Cerca semàntica
                search_results = await knowledge_engine.search_knowledge(search_request)
                knowledge_results = [result.item.dict() for result in search_results]
                
                # Step 3: Relevance Check (Corrective RAG segons imatge)
                if not knowledge_results or len(knowledge_results) == 0:
                    logger.info(f"No s'han trobat resultats per '{message.message}', provant web search fallback...")
                    # Aquí podríem implementar web search com a fallback
                    # (per ara, continuar sense coneixement)
                
                logger.info(f"✅ Knowledge Base: {len(knowledge_results)} resultats rellevants trobats")
                
            except Exception as e:
                logger.warning(f"Error cercant coneixement avançat: {e}")
                # Fallback al sistema bàsic
                try:
                    knowledge_results = await knowledge_base_system.search_knowledge(agent_id, message.message)
                    logger.info(f"Fallback KB: {len(knowledge_results)} resultats")
                except Exception as fallback_error:
                    logger.error(f"Error en fallback KB: {fallback_error}")
                    knowledge_results = []
        else:
            if not kb_enabled:
                logger.info(f"📚 Knowledge Base deshabilitada per l'agent {agent_id}")
            if not rag_enabled:
                logger.info(f"🔍 RAG deshabilitat per l'agent {agent_id}")
            knowledge_results = []

        # 3. Verificar si hi ha workflow actiu
        workflow_response = None
        try:
            from .convhi_workflows import workflow_engine
            if agent_id in conversations and len(conversations[agent_id]) > 0:
                workflow_response = await workflow_engine.continue_workflow(
                    conversation_id=f"conv_{agent_id}_{len(conversations[agent_id])}",
                    user_input=message.message
                )
        except Exception as exc:
            logger.warning(f"Error verificant workflow: {exc}")

        # 4. Verificar si cal executar eines addicionals (si no hi ha workflow)
        tools_to_execute: List[Dict[str, Any]] = []
        if not workflow_response and not conversation_should_end:
            try:
                message_lower = message.message.lower()
                if "acabar" in message_lower or "finalitzar" in message_lower or "end call" in message_lower:
                    tools_to_execute.append({"tool_id": "system_end_call", "parameters": {"reason": "Usuari ha sol licitat finalitzar la conversa"}})
                if "transferir" in message_lower or "agent huma" in message_lower:
                    tools_to_execute.append({"tool_id": "system_transfer_human", "parameters": {"department": "support", "priority": "normal"}})
            except Exception as exc:
                logger.warning(f"Error verificant eines addicionals: {exc}")

        # 5. Generar resposta amb LLM o workflow
        if final_message_override:
            response_text = apply_dynamic_variables(final_message_override, dynamic_variables)
        elif workflow_response:
            response_text = apply_dynamic_variables(
                workflow_response.history[-1].get("output", "Workflow executat"),
                dynamic_variables
            )
        else:
            response_text = await generate_llm_response(
                agent_config,
                message.message,
                knowledge_results,
                personalization={"variables": dynamic_variables, "language": detected_language, "knowledge_count": len(knowledge_results)}
            )
            response_text = apply_dynamic_variables(response_text, dynamic_variables)

        # 5. Executar eines si cal
        for tool_info in tools_to_execute:
            try:
                tool_request = ToolExecutionRequest(
                    tool_id=tool_info["tool_id"],
                    agent_id=agent_id,
                    parameters=tool_info["parameters"],
                    context=tool_context
                )
                tool_result = await tools_engine.execute_tool(tool_request)
                tool_results.append({
                    "tool_id": tool_info["tool_id"],
                    "success": tool_result.success,
                    "result": tool_result.result,
                    "error": tool_result.error
                })

                if tool_info["tool_id"] == "system_end_call" and tool_result.success:
                    if isinstance(tool_result.result, dict):
                        response_text = apply_dynamic_variables(tool_result.result.get("message", response_text), dynamic_variables)
                    else:
                        response_text = "Gràcies per la conversa. Fins aviat!"
                    conversation_should_end = True

                if tool_info["tool_id"] == "system_transfer_human" and tool_result.success:
                    conversation_should_end = True

            except Exception as e:
                logger.error(f"Error executant eina {tool_info['tool_id']}: {e}")
                tool_results.append({
                    "tool_id": tool_info["tool_id"],
                    "success": False,
                    "error": str(e)
                })

        # 6. SÃ­ntesi de veu amb suport multi-veu i idioma detectat
        audio_response = await synthesize_voice_response_advanced(agent, response_text, workflow_response, detected_language)
        
        # 5. Registrar interacciÃ³ (només si monitoring està habilitat)
        response_time = (datetime.now() - start_time).total_seconds()
        monitoring_enabled = agent_config.get("monitoring_enabled", False)
        
        if monitoring_enabled:
            await monitoring_system.log_interaction(agent_id, {
                "success": True,
                "response_time": response_time,
                "message_length": len(message.message),
                "response_length": len(response_text)
            })
            logger.info(f"📊 Monitoring: Interacció registrada per l'agent {agent_id}")
        else:
            logger.info(f"📊 Monitoring deshabilitat per l'agent {agent_id}")
        
        # 6. Registrar per anÃ lisi
        try:
            from .convhi_analytics import analytics_engine
            
            # Registrar interacciÃ³ per anÃ lisi
            await analytics_engine.log_interaction({
                "conversation_id": f"conv_{agent_id}_{len(conversations[agent_id])}",
                "agent_id": agent_id,
                "user_message": message.message,
                "agent_response": response_text,
                "response_time": response_time,
                "success": True,
                "knowledge_used": len(knowledge_results),
                "message_type": message.message_type
            })
        except Exception as e:
            logger.warning(f"Error registrant per anÃ lisi: {e}")
        
        # 6. Guardar conversaciÃ³
        conversations[agent_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message.message,
            "agent_response": response_text,
            "knowledge_used": len(knowledge_results)
        })
        
        return {"success": True, "response": response_text, "audio_base64": audio_response, "mime_type": "audio/mpeg" if audio_response else None, "knowledge_used": len(knowledge_results), "tools_executed": tool_results, "workflow_active": workflow_response is not None, "workflow_status": getattr(workflow_response, "status", None) if workflow_response else None, "response_time": response_time}
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        # Només registrar error si monitoring està habilitat
        monitoring_enabled = agent_config.get("monitoring_enabled", False) if 'agent_config' in locals() else False
        if monitoring_enabled:
            await monitoring_system.log_interaction(agent_id, {
                "success": False,
                "error": str(e)
            })
        raise HTTPException(status_code=500, detail=str(e))

async def synthesize_voice_response_advanced(agent: Dict[str, Any], text: str, workflow_response=None, detected_language: str = None) -> str:
    """Sintetitzar resposta de veu amb suport multi-veu"""
    try:
        # Verificar si hi ha tags de veu en el text
        import re
        voice_pattern = r'<([^>]+)>(.*?)</\1>'
        has_voice_tags = bool(re.search(voice_pattern, text))
        
        if has_voice_tags:
            # Usar sistema multi-veu
            try:
                from .convhi_voice_config import voice_config_engine, VoiceSwitchRequest
                
                switch_request = VoiceSwitchRequest(
                    agent_id=agent.get('id', 'default'),
                    text=text,
                    context={
                        "conversation_id": f"conv_{agent.get('id', 'default')}",
                        "workflow_active": workflow_response is not None,
                        "detected_language": detected_language
                    }
                )
                
                switch_response = await voice_config_engine.switch_voices(switch_request)
                
                if switch_response.success and switch_response.total_audio_base64:
                    return switch_response.total_audio_base64
                else:
                    logger.warning(f"Error en multi-veu: {switch_response.error}")
                    # Fallback a sÃ­ntesi normal
                    
            except Exception as e:
                logger.warning(f"Error en sistema multi-veu: {e}")
                # Fallback a sÃ­ntesi normal
        
        # SÃ­ntesi normal amb idioma detectat
        return await synthesize_voice_response_with_language(agent, text, detected_language)
        
    except Exception as e:
        logger.error(f"Error en sÃ­ntesi de veu avanÃ§ada: {e}")
        return await synthesize_voice_response(agent, text)

async def synthesize_voice_response_with_language(agent: Dict[str, Any], text: str, detected_language: str = None) -> str:
    """Sintetitzar resposta de veu amb idioma detectat"""
    try:
        # Si s'ha detectat un idioma diferent, obtenir configuraciÃ³ de veu per aquest idioma
        if detected_language and detected_language != agent.get('language', 'en'):
            try:
                from .convhi_language import language_engine
                
                voice_config = await language_engine.get_language_voice(agent.get('id', 'default'), detected_language)
                
                if voice_config:
                    # Crear agent temporal amb la configuraciÃ³ de veu detectada
                    temp_agent = agent.copy()
                    temp_agent['voice_system'] = voice_config['voice_system']
                    temp_agent['voice_id'] = voice_config['voice_id']
                    temp_agent['language'] = detected_language
                    
                    logger.info(f"ðŸŽ¤ Usant veu {voice_config['voice_system']} per idioma {detected_language}")
                    return await synthesize_voice_response(temp_agent, text)
                    
            except Exception as e:
                logger.warning(f"Error obtenint configuraciÃ³ de veu per idioma: {e}")
        
        # Usar configuraciÃ³ original de l'agent
        return await synthesize_voice_response(agent, text)
        
    except Exception as e:
        logger.error(f"Error en sÃ­ntesi amb idioma detectat: {e}")
        return await synthesize_voice_response(agent, text)

@router.post("/agents/{agent_id}/turn-taking")
async def check_turn_taking(agent_id: str, request: TurnTakingRequest):
    """Verificar si l'agent hauria de parlar"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        agent = convhi_agents[agent_id]
        
        if not agent["turn_taking_enabled"]:
            return {
                "should_speak": False,
                "reason": "Turn taking deshabilitat"
            }
        
        result = await turn_taking_model.should_speak(request)
        return result
        
    except Exception as e:
        logger.error(f"Error en turn taking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/knowledge")
async def add_knowledge(agent_id: str, knowledge: Dict[str, Any]):
    """Afegir coneixement a l'agent"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        knowledge_item = await knowledge_base_system.add_knowledge(agent_id, knowledge)
        
        return {
            "success": True,
            "knowledge": knowledge_item,
            "message": "Coneixement afegit correctament"
        }
        
    except Exception as e:
        logger.error(f"Error afegint coneixement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/knowledge")
async def search_knowledge(agent_id: str, q: str):
    """Cercar coneixement de l'agent"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        results = await knowledge_base_system.search_knowledge(agent_id, q)
        
        return {
            "success": True,
            "results": results,
            "query": q,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error cercant coneixement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Obtenir mÃ¨triques de l'agent"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        metrics = await monitoring_system.get_metrics(agent_id)
        
        return {
            "success": True,
            "metrics": metrics,
            "agent_id": agent_id
        }
        
    except Exception as e:
        logger.error(f"Error obtenint mÃ¨triques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/conversation")
async def get_conversation_history(agent_id: str):
    """Obtenir histÃ²ric de conversaciÃ³"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        history = conversations.get(agent_id, [])
        
        return {
            "success": True,
            "conversation": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint conversaciÃ³: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}")
async def get_single_agent(agent_id: str):
    """Obtenir un agent específic"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        return {
            "success": True,
            "agent": convhi_agents[agent_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/agents/{agent_id}")
async def update_agent(agent_id: str, updates: Dict[str, Any]):
    """Actualitzar configuració d'un agent"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        # Actualitzar configuració
        convhi_agents[agent_id].update(updates)
        convhi_agents[agent_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Agent {agent_id} actualitzat")
        
        return {
            "success": True,
            "agent": convhi_agents[agent_id],
            "message": "Agent actualitzat correctament"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualitzant agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/asr/test")
async def test_asr_transcription(agent_id: str, file: UploadFile = File(...)):
    """Provar transcripció ASR"""
    try:
        if agent_id not in convhi_agents:
            raise HTTPException(status_code=404, detail="Agent no trobat")
        
        agent = convhi_agents[agent_id]
        language = agent.get("language", "auto")
        
        # Leer audio data
        audio_data = await file.read()
        
        # Transcriure
        if not asr_engine.whisper_available:
            raise HTTPException(status_code=503, detail="ASR no disponible (Whisper no instal·lat)")
        
        transcribed_text = await asr_engine.transcribe_audio(audio_data, language)
        
        return {
            "success": True,
            "transcription": transcribed_text,
            "confidence": 0.95,  # Placeholder
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en test ASR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}/asr/transcriptions")
async def get_asr_transcriptions(agent_id: str):
    """Obtenir transcripcions ASR recents"""
    try:
        # Per ara retornem llista buida, es pot implementar persistència
        return {
            "success": True,
            "transcriptions": []
        }
        
    except Exception as e:
        logger.error(f"Error obtenint transcriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Funcions auxiliars
async def generate_llm_response(
    agent: Dict[str, Any],
    message: str,
    knowledge: List[Dict[str, Any]],
    personalization: Optional[Dict[str, Any]] = None,
) -> str:
    """Generar resposta amb LLM amb suport de personalització."""
    try:
        from .llm_integration import generate_llm_response as llm_generate

        language = personalization.get('language') if personalization else None
        if not language:
            language = agent.get('language', 'català')

        knowledge_context = ''
        if knowledge:
            snippets = []
            for item in knowledge[:3]:
                summary = item.get('summary') or item.get('content', '')
                snippets.append(f"- {summary[:280]}")
            knowledge_context = '\n'.join(snippets)

        variables_context = ''
        if personalization and personalization.get('variables'):
            formatted = [
                f"{key}: {value}"
                for key, value in personalization['variables'].items()
                if not isinstance(value, (dict, list))
            ]
            if formatted:
                variables_context = '\n'.join(formatted)

        # 🎯 CONTEXT ENGINEERING: Construir prompt integral per agent conversacional
        # Component 1: Identitat i veu
        system_prompt = f"""Ets un agent conversacional expert de veu per a VeuPlus.
        
🎤 Context de Veu:
- Idioma: {language}
- Persona: {agent.get('name', 'Agent')} - {agent.get('description', 'Assistant intel·ligent')}
- Estil: Natural, clar, empàtic i professional

📚 Coneixement Especialitzat:"""

        # Component 2: Knowledge Base (el més important per RAG)
        if knowledge_context:
            system_prompt += f"""

{knowledge_context}

⚠️ INSTRUCCIONS DE CONEIXEMENT:
- PRIMERA PRIORITAT: Baseu-vos en EL coneixement de sobre per donar respostes precises
- Si el coneixement té la informació demanada → DONA la informació específica del coneixement
- Si el coneixement NO cobreix el tema → diu honestament "No tinc informació específica sobre això" i ofereix alternatives
- NO inventis informació si no està al coneixement proporcionat
- Cita fonts o documentació quan sigui rellevant"""
        else:
            system_prompt += "\n- No tens coneixement especialitzat pre-carregat. Respon de manera general i honesta."
        
        # Component 3: Personalització contextual
        if variables_context:
            system_prompt += f"""

👤 Context Personalitzat:
{variables_context}"""
        
        # Component 4: Eines i capacitats
        system_prompt += """

🛠️ Eines Disponibles:
- Transferir crida a agent humà
- Finalitzar conversa
- Consultar base de dades
- Programar recordatoris

💡 Directrius de Resposta:
1. Respon NATURALMENT en """ + language + """ - com una conversa real
2. Utilitza el coneixement quan sigui rellevant per a la pregunta
3. Si no tens la informació, sé honest i ofereix alternatives
4. Mantén respostes concises però completes (max 2-3 frases per idea)
5. Fes preguntes de seguiment quan calgui per ajudar millor"""


        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Timeout per LLM: 30 segons
        try:
            llm_response = await asyncio.wait_for(
                llm_generate(
                    provider=agent.get('llm_provider', 'openai'),
                    model=agent.get('llm_model', 'gpt-4o-mini'),
                    messages=messages,
                    temperature=agent.get('temperature', 0.7),
                    max_tokens=agent.get('max_tokens', 1000),
                ),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.error("LLM timeout després de 30 segons")
            return "Ho sento, la resposta està tardant massa. Posa't en contacte de nou."

        if llm_response.success:
            return llm_response.content

        logger.error(f"Error LLM: {llm_response.error}")
        return f"Ho sento, hi ha hagut un error processant el teu missatge: {llm_response.error}"

    except Exception as e:
        logger.error(f"Error generant resposta LLM: {e}")
        return "Ho sento, hi ha hagut un error processant el teu missatge."



async def synthesize_voice_response(agent: Dict[str, Any], text: str) -> str:
    """Sintetitzar resposta de veu"""
    try:
        voice_system = agent.get('voice_system', 'edge-tts')
        voice_id = agent.get('voice_id', 'es-ES-ElviraNeural')
        external_voice_api = agent.get('external_voice_api', '')
        voice_speed = agent.get('voice_speed', 1.0)
        
        if voice_system == 'edge-tts':
            import edge_tts
            import base64
            import tempfile

            chosen_voice = voice_id or 'en-US-JennyNeural'

            async def synthesize_edge_edge(voice_to_use: str) -> str:
                communicate = edge_tts.Communicate(text, voice_to_use)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    temp_path = tmp_file.name

                await communicate.save(temp_path)

                with open(temp_path, "rb") as f:
                    audio_data_local = f.read()

                audio_base64_local = base64.b64encode(audio_data_local).decode()
                os.unlink(temp_path)
                return audio_base64_local

            try:
                audio_base64 = await synthesize_edge_edge(chosen_voice)
                logger.info("✅ Edge-TTS sintetitzat amb veu %s", chosen_voice)
                return audio_base64
            except Exception as first_error:
                logger.warning("⚠️ Error Edge-TTS amb %s: %s", chosen_voice, first_error)
                fallback_voice = 'en-US-JennyNeural'
                if fallback_voice == chosen_voice:
                    logger.error("❌ Edge-TTS sense veus disponibles")
                    return ""
                try:
                    audio_base64 = await synthesize_edge_edge(fallback_voice)
                    logger.info("✅ Edge-TTS sintetitzat amb veu fallback %s", fallback_voice)
                    return audio_base64
                except Exception as fallback_error:
                    logger.error("❌ Error Edge-TTS en fallback %s: %s", fallback_voice, fallback_error)
                    return ""

        elif voice_system in ('catalan', 'alia'):
            # Temporary fallback to Edge-TTS while dedicated engines are unavailable
            try:
                import edge_tts
                import base64
                import tempfile

                fallback_voice = 'ca-ES-AlbaNeural' if voice_system == 'catalan' else 'es-ES-ElviraNeural'
                communicate = edge_tts.Communicate(text, fallback_voice)

                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    temp_path = tmp_file.name

                await communicate.save(temp_path)

                with open(temp_path, 'rb') as f:
                    audio_data = f.read()

                audio_base64 = base64.b64encode(audio_data).decode()
                os.unlink(temp_path)

                logger.info("[ConvHi] Edge-TTS fallback used for %s -> %s", voice_system, fallback_voice)
                return audio_base64
            except Exception as fallback_error:
                logger.error("[ConvHi] Edge-TTS fallback failed for %s: %s", voice_system, fallback_error)
                return ''

        elif voice_system == 'external':
            # Usar API externa
            return await synthesize_external_voice(text, voice_id, external_voice_api, voice_speed)
            
        else:
            logger.error(f"Sistema de veu {voice_system} no suportat")
            return ""
        
    except Exception as e:
        logger.error(f"Error sintetitzant veu: {e}")
        return ""

async def synthesize_external_voice(text: str, voice_id: str, api_url: str, speed: float = 1.0) -> str:
    """Sintetitzar veu amb API externa"""
    try:
        import aiohttp
        import base64
        
        if not api_url:
            # Fallback a ElevenLabs si no s'especifica API
            api_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        # Preparar dades per l'API
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": voice_id  # Usar voice_id com a API key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "speed": speed
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{api_url}/{voice_id}", json=data, headers=headers) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    audio_base64 = base64.b64encode(audio_data).decode()
                    logger.info(f"âœ… Ã€udio generat amb API externa: {len(audio_data)} bytes")
                    return audio_base64
                else:
                    logger.error(f"Error API externa: {response.status} - {await response.text()}")
                    return ""
                    
    except Exception as e:
        logger.error(f"Error sintetitzant amb API externa: {e}")
        return ""

@router.get("/llm-providers")
async def get_llm_providers():
    """Obtenir llista de proveÃ¯dors LLM disponibles"""
    try:
        from .llm_integration import get_llm_providers
        providers = get_llm_providers()
        
        return {
            "success": True,
            "providers": providers,
            "total": len(providers)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint proveÃ¯dors LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm-providers/test")
async def test_llm_provider(request: Dict[str, Any]):
    """Provar connexiÃ³ amb proveÃ¯dor LLM"""
    try:
        from .llm_integration import generate_llm_response
        
        provider = request.get("provider", "openai")
        model = request.get("model", "gpt-4o-mini")
        
        test_messages = [
            {
                "role": "system",
                "content": "Ets un assistent Ãºtil. Respon breument."
            },
            {
                "role": "user",
                "content": "Hola! Com estÃ s?"
            }
        ]
        
        response = await generate_llm_response(
            provider=provider,
            model=model,
            messages=test_messages,
            max_tokens=50
        )
        
        return {
            "success": response.success,
            "provider": provider,
            "model": model,
            "response": response.content if response.success else None,
            "error": response.error,
            "response_time": response.response_time,
            "tokens_used": response.tokens_used
        }
        
    except Exception as e:
        logger.error(f"Error provant proveÃ¯dor LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def convhi_health():
    """Health check ConvHi"""
    try:
        from .llm_integration import get_llm_providers
        llm_providers = get_llm_providers()
        
        return {
            "status": "ok",
            "message": "ConvHi Agents funcionant",
            "components": {
                "asr": asr_engine.whisper_available,
                "turn_taking": True,
                "knowledge_base": True,
                "monitoring": True,
                "llm_integration": True
            },
            "llm_providers": len(llm_providers),
            "available_providers": list(llm_providers.keys())
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "message": f"Error en health check: {e}",
            "components": {
                "asr": asr_engine.whisper_available,
                "turn_taking": True,
                "knowledge_base": True,
                "monitoring": True,
                "llm_integration": False
            }
        }

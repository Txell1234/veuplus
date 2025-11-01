"""
Agent Intel·ligent amb Base de Coneixement
Sistema per voicebots amb memòria i coneixement especialitzat
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeBaseAgent:
    """
    Agent intel·ligent amb base de coneixement
    """
    
    def __init__(self):
        self.name = "Knowledge Base Agent"
        self.kb_dir = Path("backend/knowledge_base")
        self.kb_dir.mkdir(exist_ok=True)
        
        # Base de dades per coneixement
        self.db_path = self.kb_dir / "knowledge.db"
        self._init_database()
        
        logger.info("✅ Knowledge Base Agent initialized")
    
    def _init_database(self):
        """Inicialitzar base de dades de coneixement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Taula de coneixement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    language TEXT DEFAULT 'ca',
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Taula de converses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    language TEXT DEFAULT 'ca',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Taula de context
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Carregar coneixement inicial
            self._load_initial_knowledge()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def _load_initial_knowledge(self):
        """Carregar coneixement inicial"""
        try:
            # Coneixement bàsic en català
            basic_knowledge = [
                {
                    "category": "benvinguda",
                    "question": "hola",
                    "answer": "Hola! Gràcies per trucar. Com puc ajudar-te avui?",
                    "language": "ca"
                },
                {
                    "category": "benvinguda",
                    "question": "bon dia",
                    "answer": "Bon dia! És un plaer atendre't. En què puc ser-te útil?",
                    "language": "ca"
                },
                {
                    "category": "informació",
                    "question": "horaris",
                    "answer": "Els nostres horaris són de dilluns a divendres de 9:00 a 18:00. Dissabtes de 9:00 a 14:00.",
                    "language": "ca"
                },
                {
                    "category": "informació",
                    "question": "contacte",
                    "answer": "Pots contactar-nos al telèfon 93 123 45 67 o per correu electrònic a info@empresa.cat",
                    "language": "ca"
                },
                {
                    "category": "serveis",
                    "question": "serveis",
                    "answer": "Ofereixem serveis de consultoria, desenvolupament web, i suport tècnic especialitzat.",
                    "language": "ca"
                },
                {
                    "category": "despedida",
                    "question": "adeu",
                    "answer": "Adeu! Ha estat un plaer ajudar-te. Que tinguis un bon dia!",
                    "language": "ca"
                }
            ]
            
            # Coneixement bàsic en castellà
            basic_knowledge_es = [
                {
                    "category": "bienvenida",
                    "question": "hola",
                    "answer": "¡Hola! Gracias por llamar. ¿Cómo puedo ayudarte hoy?",
                    "language": "es"
                },
                {
                    "category": "bienvenida",
                    "question": "buenos días",
                    "answer": "¡Buenos días! Es un placer atenderte. ¿En qué puedo serte útil?",
                    "language": "es"
                },
                {
                    "category": "información",
                    "question": "horarios",
                    "answer": "Nuestros horarios son de lunes a viernes de 9:00 a 18:00. Sábados de 9:00 a 14:00.",
                    "language": "es"
                },
                {
                    "category": "información",
                    "question": "contacto",
                    "answer": "Puedes contactarnos al teléfono 93 123 45 67 o por correo electrónico a info@empresa.cat",
                    "language": "es"
                },
                {
                    "category": "servicios",
                    "question": "servicios",
                    "answer": "Ofrecemos servicios de consultoría, desarrollo web, y soporte técnico especializado.",
                    "language": "es"
                },
                {
                    "category": "despedida",
                    "question": "adiós",
                    "answer": "¡Adiós! Ha sido un placer ayudarte. ¡Que tengas un buen día!",
                    "language": "es"
                }
            ]
            
            # Inserir coneixement
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in basic_knowledge + basic_knowledge_es:
                cursor.execute('''
                    INSERT OR IGNORE INTO knowledge (category, question, answer, language)
                    VALUES (?, ?, ?, ?)
                ''', (item["category"], item["question"], item["answer"], item["language"]))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Coneixement inicial carregat")
            
        except Exception as e:
            logger.error(f"Initial knowledge loading failed: {e}")
    
    async def process_conversation(
        self,
        call_id: str,
        user_input: str,
        language: str = "ca",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processar conversa amb agent intel·ligent
        """
        try:
            logger.info(f"🤖 Agent processant: '{user_input[:30]}...' (call: {call_id})")
            
            # 1. Buscar en base de coneixement
            kb_response = await self._search_knowledge_base(user_input, language)
            
            # 2. Si no troba res, usar LLM
            if not kb_response.get("found"):
                llm_response = await self._process_with_llm(user_input, language, context)
                agent_response = llm_response.get("response", "Ho sento, no puc ajudar-te amb això.")
                response_source = "llm"
            else:
                agent_response = kb_response["answer"]
                response_source = "knowledge_base"
            
            # 3. Guardar conversa
            await self._save_conversation(call_id, user_input, agent_response, language)
            
            # 4. Actualitzar context
            if context:
                await self._update_context(call_id, context)
            
            return {
                "success": True,
                "response": agent_response,
                "source": response_source,
                "confidence": kb_response.get("confidence", 0.8),
                "call_id": call_id,
                "language": language,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Conversation processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_knowledge_base(self, user_input: str, language: str) -> Dict[str, Any]:
        """Buscar en base de coneixement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar per paraules clau
            keywords = user_input.lower().split()
            
            # Buscar coincidències
            for keyword in keywords:
                cursor.execute('''
                    SELECT question, answer, confidence FROM knowledge
                    WHERE language = ? AND (question LIKE ? OR answer LIKE ?)
                    ORDER BY confidence DESC
                    LIMIT 1
                ''', (language, f"%{keyword}%", f"%{keyword}%"))
                
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return {
                        "found": True,
                        "question": result[0],
                        "answer": result[1],
                        "confidence": result[2]
                    }
            
            conn.close()
            return {"found": False}
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return {"found": False}
    
    async def _process_with_llm(
        self,
        user_input: str,
        language: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Processar amb LLM"""
        try:
            from llm_service import LLMService
            
            # Crear prompt contextual
            prompt = self._create_llm_prompt(user_input, language, context)
            
            # Generar resposta
            llm_service = LLMService()
            
            result = await llm_service.generate_response(
                prompt=prompt,
                provider="openai",
                model="gpt-3.5-turbo",
                max_tokens=150,
                temperature=0.7
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return {"response": "Ho sento, hi ha hagut un error processant la teva consulta."}
    
    def _create_llm_prompt(
        self,
        user_input: str,
        language: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Crear prompt per LLM"""
        if language == "ca":
            base_prompt = f"""Ets un assistent virtual professional que atén trucades telefòniques.
Respon de manera amable, professional i útil en català.
Mantingues les respostes curtes i directes (màxim 2 frases).

Usuari: {user_input}

Resposta:"""
        
        elif language == "es":
            base_prompt = f"""Eres un asistente virtual profesional que atiende llamadas telefónicas.
Responde de manera amable, profesional y útil en español.
Mantén las respuestas cortas y directas (máximo 2 frases).

Usuario: {user_input}

Respuesta:"""
        
        else:
            base_prompt = f"""You are a professional virtual assistant handling phone calls.
Respond in a friendly, professional and helpful manner in English.
Keep responses short and direct (maximum 2 sentences).

User: {user_input}

Response:"""
        
        # Afegir context si existeix
        if context:
            context_info = ", ".join([f"{k}: {v}" for k, v in context.items()])
            base_prompt += f"\n\nContext: {context_info}"
        
        return base_prompt
    
    async def _save_conversation(
        self,
        call_id: str,
        user_input: str,
        agent_response: str,
        language: str
    ):
        """Guardar conversa"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (call_id, user_input, agent_response, language)
                VALUES (?, ?, ?, ?)
            ''', (call_id, user_input, agent_response, language))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Conversation save failed: {e}")
    
    async def _update_context(self, call_id: str, context: Dict[str, Any]):
        """Actualitzar context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for key, value in context.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO context (call_id, key, value)
                    VALUES (?, ?, ?)
                ''', (call_id, key, str(value)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Context update failed: {e}")
    
    def add_knowledge(
        self,
        category: str,
        question: str,
        answer: str,
        language: str = "ca",
        confidence: float = 1.0
    ) -> bool:
        """Afegir coneixement a la base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO knowledge (category, question, answer, language, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, question, answer, language, confidence))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Coneixement afegit: {category} - {question}")
            return True
            
        except Exception as e:
            logger.error(f"Knowledge addition failed: {e}")
            return False
    
    def get_conversation_history(self, call_id: str) -> List[Dict[str, Any]]:
        """Obtenir històric de conversa"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_input, agent_response, timestamp
                FROM conversations
                WHERE call_id = ?
                ORDER BY timestamp ASC
            ''', (call_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "user_input": row[0],
                    "agent_response": row[1],
                    "timestamp": row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Conversation history retrieval failed: {e}")
            return []
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Obtenir estadístiques de coneixement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total coneixement
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            total_knowledge = cursor.fetchone()[0]
            
            # Per idioma
            cursor.execute('SELECT language, COUNT(*) FROM knowledge GROUP BY language')
            by_language = dict(cursor.fetchall())
            
            # Per categoria
            cursor.execute('SELECT category, COUNT(*) FROM knowledge GROUP BY category')
            by_category = dict(cursor.fetchall())
            
            # Total converses
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_knowledge": total_knowledge,
                "by_language": by_language,
                "by_category": by_category,
                "total_conversations": total_conversations
            }
            
        except Exception as e:
            logger.error(f"Knowledge stats retrieval failed: {e}")
            return {}


# Instància global
knowledge_base_agent = KnowledgeBaseAgent()

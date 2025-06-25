# VeuPlus Call Center AI System
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from database_sql import db
import statistics

# Setup logging
logger = logging.getLogger(__name__)

# Call Center Router
call_center_router = APIRouter(prefix="/api/call-center", tags=["Call Center Management"])

# Call Center Models
class CallCenterConfig(BaseModel):
    name: str
    description: str
    languages: List[str] = ["ca", "es", "en"]
    business_hours: Dict[str, Any] = {
        "timezone": "Europe/Madrid",
        "monday": {"start": "09:00", "end": "18:00"},
        "tuesday": {"start": "09:00", "end": "18:00"},
        "wednesday": {"start": "09:00", "end": "18:00"},
        "thursday": {"start": "09:00", "end": "18:00"},
        "friday": {"start": "09:00", "end": "18:00"},
        "saturday": {"start": "10:00", "end": "14:00"},
        "sunday": {"closed": True}
    }
    escalation_rules: Dict[str, Any] = {
        "max_ai_attempts": 3,
        "escalation_keywords": ["agent", "human", "person", "operator"],
        "escalation_phone": "+34900000000",
        "escalation_email": "support@company.com"
    }
    integration_settings: Dict[str, Any] = {}

class CallAgent(BaseModel):
    name: str
    voice_model_id: str
    specialization: str  # "general", "technical", "sales", "support"
    languages: List[str]
    knowledge_base_ids: List[str]
    escalation_threshold: float = 0.7
    personality_prompt: str = "You are a professional and helpful call center agent."

class CallSession(BaseModel):
    session_id: str
    call_center_id: str
    agent_id: str
    caller_number: str
    call_start: str
    call_end: Optional[str] = None
    language: str = "ca"
    conversation_history: List[Dict[str, str]] = []
    sentiment_scores: List[float] = []
    satisfaction_rating: Optional[int] = None
    resolution_status: str = "pending"  # pending, resolved, escalated
    call_duration: float = 0.0
    cost_per_minute: float = 0.02

class CallAnalytics(BaseModel):
    total_calls: int
    avg_call_duration: float
    resolution_rate: float
    satisfaction_score: float
    cost_savings: float
    language_distribution: Dict[str, int]
    peak_hours: List[str]

# Call Center Management
@call_center_router.post("/create")
async def create_call_center(config: CallCenterConfig):
    """Create a new call center configuration"""
    try:
        call_center_id = str(uuid.uuid4())
        
        # Create call center record
        center_data = {
            "id": call_center_id,
            "name": config.name,
            "description": config.description,
            "languages": json.dumps(config.languages),
            "business_hours": json.dumps(config.business_hours),
            "escalation_rules": json.dumps(config.escalation_rules),
            "integration_settings": json.dumps(config.integration_settings),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "total_calls": 0,
            "total_minutes": 0.0,
            "cost_savings": 0.0
        }
        
        # Insert into database
        db.execute_insert("call_centers", center_data)
        
        # Create default agents for each language
        default_agents = []
        for lang in config.languages:
            agent_data = await create_default_agent(call_center_id, lang)
            default_agents.append(agent_data)
        
        return {
            "call_center_id": call_center_id,
            "name": config.name,
            "languages": config.languages,
            "default_agents": default_agents,
            "sip_number": f"+34-{call_center_id[:8]}",
            "webhook_url": f"/api/call-center/webhook/{call_center_id}",
            "dashboard_url": f"/call-center/dashboard/{call_center_id}",
            "setup_complete": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create call center: {str(e)}")

async def create_default_agent(call_center_id: str, language: str) -> Dict[str, Any]:
    """Create default AI agent for language"""
    try:
        # Get available voice models for language
        voices = db.execute_query(
            "SELECT * FROM voice_models WHERE language = ? AND status = 'ready'", 
            (language,)
        )
        
        # Select best voice for call center (prefer hyperrealistic)
        voice_model_id = "default_system_voice"
        if voices:
            # Prefer hyperrealistic Catalan voices
            hyperrealistic = [v for v in voices if v.get('quality') == 'hyperrealistic']
            if hyperrealistic:
                voice_model_id = hyperrealistic[0]['id']
            else:
                voice_model_id = voices[0]['id']
        
        # Language-specific agent configuration
        agent_configs = {
            "ca": {
                "name": "Maria - Agent Català",
                "specialization": "general",
                "personality": "Ets una agent professional de call center que parla català nadiu. Ets amable, eficient i sempre disposta a ajudar els clients. Utilitzes un to professional però càlid."
            },
            "es": {
                "name": "Carmen - Agente Español", 
                "specialization": "general",
                "personality": "Eres una agente profesional de call center que habla español nativo. Eres amable, eficiente y siempre dispuesta a ayudar a los clientes. Utilizas un tono profesional pero cálido."
            },
            "en": {
                "name": "Emma - English Agent",
                "specialization": "general", 
                "personality": "You are a professional call center agent who speaks native English. You are friendly, efficient, and always ready to help customers. You use a professional but warm tone."
            },
            "fr": {
                "name": "Sophie - Agent Français",
                "specialization": "general",
                "personality": "Vous êtes un agent professionnel de centre d'appels qui parle français natif. Vous êtes aimable, efficace et toujours prête à aider les clients. Vous utilisez un ton professionnel mais chaleureux."
            }
        }
        
        config = agent_configs.get(language, agent_configs["en"])
        
        agent_id = str(uuid.uuid4())
        agent_data = {
            "id": agent_id,
            "call_center_id": call_center_id,
            "name": config["name"],
            "voice_model_id": voice_model_id,
            "specialization": config["specialization"],
            "languages": json.dumps([language]),
            "knowledge_base_ids": json.dumps([]),
            "escalation_threshold": 0.7,
            "personality_prompt": config["personality"],
            "created_at": datetime.now().isoformat(),
            "total_calls": 0,
            "avg_satisfaction": 0.0,
            "status": "active"
        }
        
        db.execute_insert("call_center_agents", agent_data)
        
        return {
            "agent_id": agent_id,
            "name": config["name"],
            "language": language,
            "voice_model_id": voice_model_id,
            "specialization": config["specialization"]
        }
        
    except Exception as e:
        logger.error(f"Failed to create default agent: {str(e)}")
        return {}

@call_center_router.post("/agents")
async def create_call_agent(agent: CallAgent, call_center_id: str):
    """Create a new call center agent"""
    try:
        agent_id = str(uuid.uuid4())
        
        agent_data = {
            "id": agent_id,
            "call_center_id": call_center_id,
            "name": agent.name,
            "voice_model_id": agent.voice_model_id,
            "specialization": agent.specialization,
            "languages": json.dumps(agent.languages),
            "knowledge_base_ids": json.dumps(agent.knowledge_base_ids),
            "escalation_threshold": agent.escalation_threshold,
            "personality_prompt": agent.personality_prompt,
            "created_at": datetime.now().isoformat(),
            "total_calls": 0,
            "avg_satisfaction": 0.0,
            "status": "active"
        }
        
        db.execute_insert("call_center_agents", agent_data)
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "specialization": agent.specialization,
            "languages": agent.languages,
            "message": "Call center agent created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@call_center_router.post("/webhook/{call_center_id}")
async def call_center_webhook(call_center_id: str, request: Request, background_tasks: BackgroundTasks):
    """Handle incoming calls to call center"""
    try:
        # Get call center configuration
        centers = db.execute_query("SELECT * FROM call_centers WHERE id = ?", (call_center_id,))
        if not centers:
            raise HTTPException(status_code=404, detail="Call center not found")
        
        call_center = centers[0]
        
        # Parse incoming call data
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            call_data = await request.json()
        else:
            form_data = await request.form()
            call_data = dict(form_data)
        
        # Extract call information
        caller_number = call_data.get('From', call_data.get('caller_number', 'unknown'))
        called_number = call_data.get('To', call_data.get('called_number', call_center_id))
        user_message = call_data.get('SpeechResult', call_data.get('speech', call_data.get('message', '')))
        
        # Detect language (simple detection based on keywords or caller preference)
        detected_language = detect_caller_language(user_message, caller_number)
        
        # Get appropriate agent for language
        agent = await get_best_agent(call_center_id, detected_language, user_message)
        
        if not agent:
            # Fallback to default response
            return generate_fallback_response(detected_language)
        
        # Create or get call session
        session_id = call_data.get('CallSid', call_data.get('session_id', str(uuid.uuid4())))
        call_session = await get_or_create_call_session(
            session_id, call_center_id, agent['id'], caller_number, detected_language
        )
        
        # Process the call
        if user_message:
            # Existing conversation
            response = await process_call_conversation(call_session, user_message, agent)
        else:
            # Initial call - welcome message
            response = await generate_welcome_message(call_center, agent, detected_language)
        
        # Update call analytics
        background_tasks.add_task(update_call_analytics, call_center_id, call_session, user_message, response)
        
        # Return appropriate response format
        return generate_call_response(response, detected_language, call_data.get('provider', 'twilio'))
        
    except Exception as e:
        logger.error(f"Call center webhook error: {str(e)}")
        return generate_error_response()

def detect_caller_language(message: str, caller_number: str) -> str:
    """Detect caller's preferred language"""
    # Simple language detection based on keywords
    catalan_keywords = ['bon dia', 'bona tarda', 'hola', 'gràcies', 'si us plau', 'ajuda']
    spanish_keywords = ['buenos días', 'buenas tardes', 'hola', 'gracias', 'por favor', 'ayuda']
    english_keywords = ['good morning', 'hello', 'thank you', 'please', 'help']
    
    if message:
        message_lower = message.lower()
        
        if any(word in message_lower for word in catalan_keywords):
            return 'ca'
        elif any(word in message_lower for word in spanish_keywords):
            return 'es'
        elif any(word in message_lower for word in english_keywords):
            return 'en'
    
    # Default to Catalan for Spanish phone numbers
    if caller_number.startswith('+34'):
        return 'ca'
    
    return 'ca'  # Default to Catalan

async def get_best_agent(call_center_id: str, language: str, user_message: str = "") -> Optional[Dict[str, Any]]:
    """Get best available agent for the call"""
    try:
        # Get agents that speak the detected language
        agents = db.execute_query("""
            SELECT * FROM call_center_agents 
            WHERE call_center_id = ? AND status = 'active'
            ORDER BY avg_satisfaction DESC, total_calls ASC
        """, (call_center_id,))
        
        # Filter agents by language capability
        suitable_agents = []
        for agent in agents:
            agent_languages = json.loads(agent.get('languages', '[]'))
            if language in agent_languages:
                suitable_agents.append(agent)
        
        if suitable_agents:
            # Return agent with highest satisfaction and lowest call count (load balancing)
            return suitable_agents[0]
        
        # Fallback: return any available agent
        if agents:
            return agents[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting best agent: {str(e)}")
        return None

async def get_or_create_call_session(session_id: str, call_center_id: str, agent_id: str, 
                                   caller_number: str, language: str) -> Dict[str, Any]:
    """Get existing call session or create new one"""
    try:
        # Check if session exists
        sessions = db.execute_query("SELECT * FROM call_sessions WHERE session_id = ?", (session_id,))
        
        if sessions:
            session = sessions[0]
            # Parse conversation history
            if session.get('conversation_history'):
                session['conversation_history'] = json.loads(session['conversation_history'])
            else:
                session['conversation_history'] = []
            return session
        
        # Create new session
        session_data = {
            "session_id": session_id,
            "call_center_id": call_center_id,
            "agent_id": agent_id,
            "caller_number": caller_number,
            "call_start": datetime.now().isoformat(),
            "language": language,
            "conversation_history": "[]",
            "sentiment_scores": "[]",
            "resolution_status": "pending",
            "call_duration": 0.0,
            "cost_per_minute": 0.02
        }
        
        db.execute_insert("call_sessions", session_data)
        session_data['conversation_history'] = []
        session_data['sentiment_scores'] = []
        
        return session_data
        
    except Exception as e:
        logger.error(f"Error managing call session: {str(e)}")
        return {}

async def process_call_conversation(call_session: Dict[str, Any], user_message: str, 
                                  agent: Dict[str, Any]) -> str:
    """Process conversation with AI agent"""
    try:
        # Add user message to conversation history
        call_session['conversation_history'].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze sentiment
        sentiment_score = analyze_sentiment(user_message)
        call_session['sentiment_scores'].append(sentiment_score)
        
        # Check for escalation triggers
        if should_escalate_call(user_message, sentiment_score, call_session, agent):
            response = await escalate_to_human(call_session, agent)
        else:
            # Generate AI response
            response = await generate_ai_response(call_session, user_message, agent)
        
        # Add AI response to conversation
        call_session['conversation_history'].append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update session in database
        db.execute_update(
            "call_sessions",
            {
                "conversation_history": json.dumps(call_session['conversation_history']),
                "sentiment_scores": json.dumps(call_session['sentiment_scores']),
                "call_duration": (datetime.now() - datetime.fromisoformat(call_session['call_start'])).total_seconds() / 60
            },
            "session_id = ?",
            (call_session['session_id'],)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")
        return "Ho sento, hi ha hagut un problema tècnic. Un moment, si us plau."

def analyze_sentiment(message: str) -> float:
    """Simple sentiment analysis (in production, use proper NLP)"""
    positive_words = ['gràcies', 'perfecte', 'excel·lent', 'bé', 'fantastic', 'genial']
    negative_words = ['malament', 'horrible', 'problema', 'enfadat', 'disgust', 'error']
    
    message_lower = message.lower()
    positive_count = sum(1 for word in positive_words if word in message_lower)
    negative_count = sum(1 for word in negative_words if word in message_lower)
    
    if positive_count > negative_count:
        return 0.7 + (positive_count * 0.1)
    elif negative_count > positive_count:
        return 0.3 - (negative_count * 0.1)
    else:
        return 0.5

def should_escalate_call(user_message: str, sentiment_score: float, call_session: Dict[str, Any], 
                        agent: Dict[str, Any]) -> bool:
    """Determine if call should be escalated to human"""
    # Check escalation keywords
    escalation_keywords = ['agent', 'persona', 'humà', 'human', 'operator', 'supervisor']
    if any(keyword in user_message.lower() for keyword in escalation_keywords):
        return True
    
    # Check sentiment threshold
    if sentiment_score < agent.get('escalation_threshold', 0.7):
        return True
    
    # Check conversation length (escalate after too many turns)
    if len(call_session.get('conversation_history', [])) > 10:
        return True
    
    return False

async def escalate_to_human(call_session: Dict[str, Any], agent: Dict[str, Any]) -> str:
    """Escalate call to human agent"""
    # Update call session status
    db.execute_update(
        "call_sessions",
        {"resolution_status": "escalated"},
        "session_id = ?",
        (call_session['session_id'],)
    )
    
    language = call_session.get('language', 'ca')
    
    escalation_messages = {
        'ca': "Entenc que necessites parlar amb una persona. Et passaré amb un dels nostres agents humans. Un moment, si us plau.",
        'es': "Entiendo que necesitas hablar con una persona. Te paso con uno de nuestros agentes humanos. Un momento, por favor.",
        'en': "I understand you need to speak with a person. I'll transfer you to one of our human agents. One moment, please.",
        'fr': "Je comprends que vous devez parler à une personne. Je vous transfère vers l'un de nos agents humains. Un moment, s'il vous plaît."
    }
    
    return escalation_messages.get(language, escalation_messages['ca'])

async def generate_ai_response(call_session: Dict[str, Any], user_message: str, 
                              agent: Dict[str, Any]) -> str:
    """Generate AI response using agent's configuration"""
    try:
        # In production, integrate with OpenAI or other LLM
        # For now, generate contextual responses
        
        language = call_session.get('language', 'ca')
        specialization = agent.get('specialization', 'general')
        
        # Get knowledge base context if available
        knowledge_context = ""
        if agent.get('knowledge_base_ids'):
            kb_ids = json.loads(agent['knowledge_base_ids'])
            for kb_id in kb_ids:
                kb_items = db.execute_query("SELECT content FROM knowledge_base WHERE id = ?", (kb_id,))
                if kb_items:
                    knowledge_context += kb_items[0]['content'][:500] + "\n"
        
        # Generate contextual response based on message intent
        intent = classify_message_intent(user_message)
        
        response_templates = {
            'ca': {
                'greeting': "Bon dia! Sóc {agent_name}, com puc ajudar-te avui?",
                'information': "Deixa'm que busqui aquesta informació per tu. {context}",
                'support': "Entenc el teu problema. Puc ajudar-te amb això. {context}",
                'complaint': "Ho sento molt per les molèsties. Farem tot el possible per resoldre-ho.",
                'closing': "És tot el que necessites? Ha estat un plaer ajudar-te!",
                'default': "Entenc. Pots donar-me més detalls per poder ajudar-te millor?"
            },
            'es': {
                'greeting': "¡Buenos días! Soy {agent_name}, ¿cómo puedo ayudarte hoy?",
                'information': "Déjame buscar esa información para ti. {context}",
                'support': "Entiendo tu problema. Puedo ayudarte con eso. {context}",
                'complaint': "Lo siento mucho por las molestias. Haremos todo lo posible para resolverlo.",
                'closing': "¿Es todo lo que necesitas? ¡Ha sido un placer ayudarte!",
                'default': "Entiendo. ¿Puedes darme más detalles para poder ayudarte mejor?"
            }
        }
        
        templates = response_templates.get(language, response_templates['ca'])
        template = templates.get(intent, templates['default'])
        
        response = template.format(
            agent_name=agent.get('name', 'Agent IA'),
            context=knowledge_context[:200] if knowledge_context else ""
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "Ho sento, pots repetir la pregunta?"

def classify_message_intent(message: str) -> str:
    """Classify message intent for appropriate response"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hola', 'bon dia', 'bona tarda']):
        return 'greeting'
    elif any(word in message_lower for word in ['informació', 'saber', 'pregunta']):
        return 'information'
    elif any(word in message_lower for word in ['problema', 'ajuda', 'suport']):
        return 'support'
    elif any(word in message_lower for word in ['queixa', 'malament', 'disgust']):
        return 'complaint'
    elif any(word in message_lower for word in ['gràcies', 'adéu', 'prou']):
        return 'closing'
    else:
        return 'default'

async def generate_welcome_message(call_center: Dict[str, Any], agent: Dict[str, Any], 
                                 language: str) -> str:
    """Generate welcome message for new calls"""
    welcome_messages = {
        'ca': f"Bon dia! Us ha trucat a {call_center['name']}. Sóc {agent['name']}, la vostra assistent virtual. Com puc ajudar-vos avui?",
        'es': f"¡Buenos días! Ha llamado a {call_center['name']}. Soy {agent['name']}, su asistente virtual. ¿Cómo puedo ayudarle hoy?",
        'en': f"Good morning! You've reached {call_center['name']}. I'm {agent['name']}, your virtual assistant. How can I help you today?",
        'fr': f"Bonjour! Vous avez appelé {call_center['name']}. Je suis {agent['name']}, votre assistant virtuel. Comment puis-je vous aider aujourd'hui?"
    }
    
    return welcome_messages.get(language, welcome_messages['ca'])

def generate_call_response(message: str, language: str, provider: str = 'twilio'):
    """Generate appropriate call response format"""
    if provider == 'twilio':
        return generate_twilio_response(message, language)
    elif provider == 'vonage':
        return generate_vonage_response(message, language)
    else:
        return {"response": message, "language": language}

def generate_twilio_response(message: str, language: str = 'ca'):
    """Generate TwiML response"""
    voice_mapping = {
        'ca': 'woman',
        'es': 'woman', 
        'en': 'woman',
        'fr': 'woman'
    }
    
    language_mapping = {
        'ca': 'ca-ES',
        'es': 'es-ES',
        'en': 'en-US',
        'fr': 'fr-FR'
    }
    
    voice = voice_mapping.get(language, 'woman')
    lang_code = language_mapping.get(language, 'ca-ES')
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{voice}" language="{lang_code}">{message}</Say>
    <Gather input="speech" timeout="10" speechTimeout="3" language="{lang_code}">
        <Say voice="{voice}" language="{lang_code}">Parli ara, l'escolto.</Say>
    </Gather>
    <Say voice="{voice}" language="{lang_code}">Gràcies per trucar. Que tingui un bon dia!</Say>
    <Hangup/>
</Response>"""
    
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")

def generate_vonage_response(message: str, language: str = 'ca'):
    """Generate Vonage NCCO response"""
    language_mapping = {
        'ca': 'ca-ES',
        'es': 'es-ES', 
        'en': 'en-US',
        'fr': 'fr-FR'
    }
    
    lang_code = language_mapping.get(language, 'ca-ES')
    
    ncco = [
        {
            "action": "talk",
            "text": message,
            "language": lang_code,
            "style": 1
        },
        {
            "action": "input",
            "type": ["speech"],
            "speech": {
                "timeout": 10,
                "max_duration": 30,
                "language": lang_code
            }
        }
    ]
    
    return {"ncco": ncco}

def generate_fallback_response(language: str = 'ca'):
    """Generate fallback response when no agent available"""
    fallback_messages = {
        'ca': "Ho sentim, tots els nostres agents estan ocupats. Si us plau, torneu a trucar més tard.",
        'es': "Lo sentimos, todos nuestros agentes están ocupados. Por favor, vuelva a llamar más tarde.",
        'en': "We're sorry, all our agents are busy. Please call back later.",
        'fr': "Nous sommes désolés, tous nos agents sont occupés. Veuillez rappeler plus tard."
    }
    
    message = fallback_messages.get(language, fallback_messages['ca'])
    return generate_call_response(message, language)

def generate_error_response():
    """Generate error response"""
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman" language="ca-ES">Ho sentim, hi ha hagut un error tècnic. Si us plau, torneu a trucar.</Say>
    <Hangup/>
</Response>"""
    
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")

async def update_call_analytics(call_center_id: str, call_session: Dict[str, Any], 
                               user_message: str, ai_response: str):
    """Update call center analytics in background"""
    try:
        # Update call center metrics
        db.execute_update(
            "call_centers",
            {
                "total_calls": db.execute_query("SELECT total_calls FROM call_centers WHERE id = ?", (call_center_id,))[0]['total_calls'] + 1,
                "total_minutes": db.execute_query("SELECT total_minutes FROM call_centers WHERE id = ?", (call_center_id,))[0]['total_minutes'] + call_session.get('call_duration', 0),
                "cost_savings": db.execute_query("SELECT cost_savings FROM call_centers WHERE id = ?", (call_center_id,))[0]['cost_savings'] + (call_session.get('call_duration', 0) * 0.02)
            },
            "id = ?",
            (call_center_id,)
        )
        
        # Update agent metrics
        db.execute_update(
            "call_center_agents",
            {
                "total_calls": db.execute_query("SELECT total_calls FROM call_center_agents WHERE id = ?", (call_session['agent_id'],))[0]['total_calls'] + 1
            },
            "id = ?", 
            (call_session['agent_id'],)
        )
        
    except Exception as e:
        logger.error(f"Error updating analytics: {str(e)}")

# Analytics and Reporting
@call_center_router.get("/analytics/{call_center_id}")
async def get_call_center_analytics(call_center_id: str, period: str = "7d"):
    """Get call center analytics"""
    try:
        # Calculate date range
        now = datetime.now()
        if period == "1d":
            start_date = now - timedelta(days=1)
        elif period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "30d":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=7)
        
        # Get call sessions in period
        sessions = db.execute_query("""
            SELECT * FROM call_sessions 
            WHERE call_center_id = ? AND call_start >= ?
        """, (call_center_id, start_date.isoformat()))
        
        if not sessions:
            return {"analytics": CallAnalytics(
                total_calls=0, avg_call_duration=0, resolution_rate=0,
                satisfaction_score=0, cost_savings=0, language_distribution={},
                peak_hours=[]
            )}
        
        # Calculate metrics
        total_calls = len(sessions)
        avg_duration = sum(s.get('call_duration', 0) for s in sessions) / total_calls if total_calls > 0 else 0
        resolved_calls = len([s for s in sessions if s.get('resolution_status') == 'resolved'])
        resolution_rate = resolved_calls / total_calls if total_calls > 0 else 0
        
        # Calculate satisfaction score
        all_ratings = [s.get('satisfaction_rating', 3) for s in sessions if s.get('satisfaction_rating')]
        satisfaction_score = sum(all_ratings) / len(all_ratings) if all_ratings else 3.0
        
        # Cost savings calculation (assuming $0.50/minute for human agent)
        ai_minutes = sum(s.get('call_duration', 0) for s in sessions)
        cost_savings = ai_minutes * 0.48  # $0.50 human cost - $0.02 AI cost
        
        # Language distribution
        language_dist = {}
        for session in sessions:
            lang = session.get('language', 'ca')
            language_dist[lang] = language_dist.get(lang, 0) + 1
        
        # Peak hours analysis
        hour_counts = {}
        for session in sessions:
            if session.get('call_start'):
                hour = datetime.fromisoformat(session['call_start']).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.keys(), key=lambda x: hour_counts[x], reverse=True)[:3]
        peak_hours = [f"{h:02d}:00" for h in peak_hours]
        
        analytics = CallAnalytics(
            total_calls=total_calls,
            avg_call_duration=round(avg_duration, 2),
            resolution_rate=round(resolution_rate, 2),
            satisfaction_score=round(satisfaction_score, 1),
            cost_savings=round(cost_savings, 2),
            language_distribution=language_dist,
            peak_hours=peak_hours
        )
        
        return {"analytics": analytics, "period": period}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@call_center_router.get("/dashboard/{call_center_id}")
async def get_call_center_dashboard(call_center_id: str):
    """Get call center dashboard data"""
    try:
        # Get call center info
        centers = db.execute_query("SELECT * FROM call_centers WHERE id = ?", (call_center_id,))
        if not centers:
            raise HTTPException(status_code=404, detail="Call center not found")
        
        call_center = centers[0]
        
        # Get agents
        agents = db.execute_query("SELECT * FROM call_center_agents WHERE call_center_id = ?", (call_center_id,))
        
        # Get recent calls
        recent_calls = db.execute_query("""
            SELECT * FROM call_sessions 
            WHERE call_center_id = ? 
            ORDER BY call_start DESC 
            LIMIT 20
        """, (call_center_id,))
        
        # Get today's analytics
        today = datetime.now().date()
        today_calls = db.execute_query("""
            SELECT COUNT(*) as count FROM call_sessions 
            WHERE call_center_id = ? AND DATE(call_start) = ?
        """, (call_center_id, today.isoformat()))
        
        return {
            "call_center": call_center,
            "agents": agents,
            "recent_calls": recent_calls,
            "today_calls": today_calls[0]['count'] if today_calls else 0,
            "status": "operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@call_center_router.get("/")
async def list_call_centers():
    """List all call centers"""
    try:
        centers = db.execute_query("SELECT * FROM call_centers ORDER BY created_at DESC")
        return {"call_centers": centers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list call centers: {str(e)}")

# Initialize database tables for call center
def init_call_center_tables():
    """Initialize call center specific tables"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Call Centers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_centers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                languages TEXT,
                business_hours TEXT,
                escalation_rules TEXT,
                integration_settings TEXT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                total_calls INTEGER DEFAULT 0,
                total_minutes REAL DEFAULT 0.0,
                cost_savings REAL DEFAULT 0.0
            )
        """)
        
        # Call Center Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_center_agents (
                id TEXT PRIMARY KEY,
                call_center_id TEXT NOT NULL,
                name TEXT NOT NULL,
                voice_model_id TEXT NOT NULL,
                specialization TEXT DEFAULT 'general',
                languages TEXT,
                knowledge_base_ids TEXT,
                escalation_threshold REAL DEFAULT 0.7,
                personality_prompt TEXT,
                created_at TEXT NOT NULL,
                total_calls INTEGER DEFAULT 0,
                avg_satisfaction REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (call_center_id) REFERENCES call_centers (id)
            )
        """)
        
        # Call Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS call_sessions (
                session_id TEXT PRIMARY KEY,
                call_center_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                caller_number TEXT,
                call_start TEXT NOT NULL,
                call_end TEXT,
                language TEXT DEFAULT 'ca',
                conversation_history TEXT,
                sentiment_scores TEXT,
                satisfaction_rating INTEGER,
                resolution_status TEXT DEFAULT 'pending',
                call_duration REAL DEFAULT 0.0,
                cost_per_minute REAL DEFAULT 0.02,
                FOREIGN KEY (call_center_id) REFERENCES call_centers (id),
                FOREIGN KEY (agent_id) REFERENCES call_center_agents (id)
            )
        """)
        
        conn.commit()

# Initialize tables on import
init_call_center_tables()
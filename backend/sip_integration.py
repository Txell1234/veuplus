# SIP Trunk Integration for VeuPlus Phone Calls
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import uuid
import asyncio
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
from database_sql import db

# Setup logging
logger = logging.getLogger(__name__)

# SIP Router
sip_router = APIRouter(prefix="/api/sip", tags=["SIP Integration"])

# SIP Models
class SipConfig(BaseModel):
    bot_id: str
    bot_type: str  # 'chatbot' or 'voicebot'
    sip_provider: str  # 'twilio', 'vonage', 'telnyx', 'custom'
    sip_number: str
    webhook_url: Optional[str] = None
    provider_config: Dict[str, Any] = {}

class CallSession(BaseModel):
    call_id: str
    bot_id: str
    bot_type: str
    caller_number: str
    sip_number: str
    status: str = "active"
    start_time: str
    conversation_history: List[Dict[str, str]] = []
    total_duration: float = 0.0

# SIP Provider Configurations
SIP_PROVIDERS = {
    "twilio": {
        "name": "Twilio",
        "webhook_format": "twiml",
        "required_config": ["account_sid", "auth_token", "phone_number"],
        "documentation": "https://www.twilio.com/docs/voice/twiml"
    },
    "vonage": {
        "name": "Vonage (Nexmo)",
        "webhook_format": "ncco",
        "required_config": ["api_key", "api_secret", "phone_number"],
        "documentation": "https://developer.vonage.com/voice/voice-api/ncco-reference"
    },
    "telnyx": {
        "name": "Telnyx",
        "webhook_format": "json",
        "required_config": ["api_key", "phone_number"],
        "documentation": "https://developers.telnyx.com/docs/api/v2/call-control"
    },
    "custom": {
        "name": "Custom SIP Trunk",
        "webhook_format": "json",
        "required_config": ["sip_server", "username", "password"],
        "documentation": "Custom SIP integration"
    }
}

# Active call sessions (in production, use Redis or database)
active_calls: Dict[str, CallSession] = {}

@sip_router.post("/configure")
async def configure_sip_integration(config: SipConfig):
    """Configure SIP integration for a bot"""
    try:
        # Verify bot exists
        if config.bot_type == "chatbot":
            bot = db.get_chatbot(config.bot_id)
        elif config.bot_type == "voicebot":
            bot = db.get_voicebot(config.bot_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid bot type")
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Validate provider
        if config.sip_provider not in SIP_PROVIDERS:
            raise HTTPException(status_code=400, detail="Unsupported SIP provider")
        
        # Generate SIP integration ID
        sip_id = str(uuid.uuid4())
        
        # Create webhook URL if not provided
        if not config.webhook_url:
            config.webhook_url = f"/api/sip/webhook/{sip_id}"
        
        # Store SIP configuration
        sip_data = {
            "id": sip_id,
            "bot_id": config.bot_id,
            "bot_type": config.bot_type,
            "sip_provider": config.sip_provider,
            "sip_number": config.sip_number,
            "sip_config": json.dumps(config.provider_config),
            "webhook_url": config.webhook_url,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "total_calls": 0,
            "total_minutes": 0.0
        }
        
        db.create_sip_integration(sip_data)
        
        # Update bot to enable SIP
        if config.bot_type == "chatbot":
            db.execute_update(
                "chatbots",
                {"sip_enabled": True, "sip_number": config.sip_number},
                "id = ?",
                (config.bot_id,)
            )
        else:
            db.execute_update(
                "voicebots", 
                {"sip_enabled": True, "sip_number": config.sip_number},
                "id = ?",
                (config.bot_id,)
            )
        
        return {
            "sip_integration_id": sip_id,
            "webhook_url": f"https://veuplus.com{config.webhook_url}",
            "provider": SIP_PROVIDERS[config.sip_provider]["name"],
            "phone_number": config.sip_number,
            "status": "configured",
            "setup_instructions": generate_setup_instructions(config.sip_provider, sip_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure SIP: {str(e)}")

def generate_setup_instructions(provider: str, sip_id: str) -> Dict[str, Any]:
    """Generate setup instructions for SIP provider"""
    base_url = "https://veuplus.com"
    webhook_url = f"{base_url}/api/sip/webhook/{sip_id}"
    
    instructions = {
        "twilio": {
            "steps": [
                "1. Go to your Twilio Console (https://console.twilio.com/)",
                "2. Navigate to Phone Numbers > Manage > Active numbers",
                "3. Click on your phone number",
                f"4. Set the webhook URL to: {webhook_url}",
                "5. Set HTTP method to POST",
                "6. Save configuration"
            ],
            "webhook_url": webhook_url,
            "method": "POST",
            "content_type": "application/x-www-form-urlencoded"
        },
        "vonage": {
            "steps": [
                "1. Go to your Vonage Dashboard (https://dashboard.nexmo.com/)",
                "2. Navigate to Voice > Your numbers",
                "3. Click Edit next to your number",
                f"4. Set the Answer URL to: {webhook_url}",
                f"5. Set the Event URL to: {webhook_url}/events",
                "6. Set HTTP method to POST",
                "7. Save configuration"
            ],
            "webhook_url": webhook_url,
            "method": "POST",
            "content_type": "application/json"
        },
        "telnyx": {
            "steps": [
                "1. Go to your Telnyx Portal (https://portal.telnyx.com/)",
                "2. Navigate to Numbers > My Numbers",
                "3. Click on your phone number",
                "4. Go to Voice Settings",
                f"5. Set the Webhook URL to: {webhook_url}",
                "6. Enable Webhook Failover URL (optional)",
                "7. Save configuration"
            ],
            "webhook_url": webhook_url,
            "method": "POST",
            "content_type": "application/json"
        },
        "custom": {
            "steps": [
                "1. Configure your SIP server to forward calls to the webhook",
                f"2. Set the webhook URL to: {webhook_url}",
                "3. Ensure your SIP server sends proper call events",
                "4. Test the integration with a test call"
            ],
            "webhook_url": webhook_url,
            "method": "POST",
            "content_type": "application/json"
        }
    }
    
    return instructions.get(provider, instructions["custom"])

@sip_router.post("/webhook/{sip_id}")
async def sip_webhook(sip_id: str, request: Request, background_tasks: BackgroundTasks):
    """Handle incoming SIP webhooks from providers"""
    try:
        # Get SIP integration
        sip_integrations = db.execute_query("SELECT * FROM sip_integrations WHERE id = ?", (sip_id,))
        if not sip_integrations:
            raise HTTPException(status_code=404, detail="SIP integration not found")
        
        sip_integration = sip_integrations[0]
        
        # Parse request based on provider
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            webhook_data = await request.json()
        else:
            # Form data (Twilio)
            form_data = await request.form()
            webhook_data = dict(form_data)
        
        logger.info(f"SIP webhook received for {sip_integration['sip_provider']}: {webhook_data}")
        
        # Handle based on provider
        if sip_integration['sip_provider'] == 'twilio':
            return await handle_twilio_webhook(sip_integration, webhook_data, background_tasks)
        elif sip_integration['sip_provider'] == 'vonage':
            return await handle_vonage_webhook(sip_integration, webhook_data, background_tasks)
        elif sip_integration['sip_provider'] == 'telnyx':
            return await handle_telnyx_webhook(sip_integration, webhook_data, background_tasks)
        else:
            return await handle_custom_webhook(sip_integration, webhook_data, background_tasks)
            
    except Exception as e:
        logger.error(f"SIP webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

async def handle_twilio_webhook(sip_integration: Dict[str, Any], webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle Twilio webhook"""
    call_sid = webhook_data.get('CallSid')
    from_number = webhook_data.get('From')
    to_number = webhook_data.get('To')
    speech_result = webhook_data.get('SpeechResult', '')
    
    # Create or get call session
    if call_sid not in active_calls:
        active_calls[call_sid] = CallSession(
            call_id=call_sid,
            bot_id=sip_integration['bot_id'],
            bot_type=sip_integration['bot_type'],
            caller_number=from_number,
            sip_number=to_number,
            start_time=datetime.now().isoformat()
        )
    
    call_session = active_calls[call_sid]
    
    # Process speech if available
    if speech_result:
        # Add user message to conversation
        call_session.conversation_history.append({
            "user": speech_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get bot response
        bot_response = await get_bot_response(
            sip_integration['bot_id'], 
            sip_integration['bot_type'], 
            speech_result,
            call_session.conversation_history
        )
        
        # Add bot response to conversation
        call_session.conversation_history.append({
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate TwiML response
        twiml_response = generate_twilio_response(bot_response)
    else:
        # Initial call - welcome message
        welcome_message = await get_welcome_message(sip_integration['bot_id'], sip_integration['bot_type'])
        twiml_response = generate_twilio_response(welcome_message)
    
    return Response(content=twiml_response, media_type="application/xml")

def generate_twilio_response(message: str) -> str:
    """Generate TwiML response for Twilio"""
    webhook_url = "/api/sip/webhook"  # Continue conversation
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman" language="ca-ES">{message}</Say>
    <Gather input="speech" timeout="5" speechTimeout="2" action="{webhook_url}" method="POST">
        <Say voice="woman" language="ca-ES">Parla ara, t'escolto.</Say>
    </Gather>
    <Say voice="woman" language="ca-ES">No t'he sentit. Adéu!</Say>
    <Hangup/>
</Response>"""
    
    return twiml

async def handle_vonage_webhook(sip_integration: Dict[str, Any], webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle Vonage (Nexmo) webhook"""
    conversation_uuid = webhook_data.get('conversation_uuid')
    
    # For incoming calls, return NCCO
    if webhook_data.get('status') == 'started':
        welcome_message = await get_welcome_message(sip_integration['bot_id'], sip_integration['bot_type'])
        
        ncco = [
            {
                "action": "talk",
                "text": welcome_message,
                "language": "ca-ES",
                "style": 1
            },
            {
                "action": "input",
                "type": ["speech"],
                "speech": {
                    "timeout": 5,
                    "max_duration": 10,
                    "language": "ca-ES"
                },
                "eventUrl": [f"/api/sip/webhook/{sip_integration['id']}/input"]
            }
        ]
        
        return {"ncco": ncco}
    
    return {"ncco": [{"action": "talk", "text": "Gràcies per trucar. Adéu!"}]}

async def handle_telnyx_webhook(sip_integration: Dict[str, Any], webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle Telnyx webhook"""
    call_control_id = webhook_data.get('payload', {}).get('call_control_id')
    event_type = webhook_data.get('event_type')
    
    if event_type == 'call.initiated':
        # Answer the call
        return {
            "command": "answer",
            "call_control_id": call_control_id
        }
    elif event_type == 'call.answered':
        # Start conversation
        welcome_message = await get_welcome_message(sip_integration['bot_id'], sip_integration['bot_type'])
        
        return {
            "command": "speak",
            "call_control_id": call_control_id,
            "payload": welcome_message,
            "voice": "female",
            "language": "ca-ES"
        }
    
    return {"status": "ok"}

async def handle_custom_webhook(sip_integration: Dict[str, Any], webhook_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle custom SIP webhook"""
    # Generic handler for custom SIP implementations
    call_id = webhook_data.get('call_id', str(uuid.uuid4()))
    user_message = webhook_data.get('message', webhook_data.get('speech', ''))
    
    if user_message:
        # Process user message
        bot_response = await get_bot_response(
            sip_integration['bot_id'],
            sip_integration['bot_type'],
            user_message
        )
        
        return {
            "response": bot_response,
            "action": "speak",
            "language": "ca-ES",
            "continue_listening": True
        }
    else:
        # Initial call
        welcome_message = await get_welcome_message(sip_integration['bot_id'], sip_integration['bot_type'])
        
        return {
            "response": welcome_message,
            "action": "speak", 
            "language": "ca-ES",
            "continue_listening": True
        }

async def get_bot_response(bot_id: str, bot_type: str, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """Get response from bot"""
    try:
        # Import here to avoid circular imports
        import requests
        
        # Call the appropriate bot endpoint
        endpoint = f"/api/{bot_type}s/chat"
        
        response = requests.post(f"http://localhost:8001{endpoint}", json={
            "bot_id": bot_id,
            "message": user_message,
            "chat_history": conversation_history or [],
            "source": "sip_call"
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Ho sento, no puc respondre ara mateix.')
        else:
            logger.error(f"Bot response error: {response.status_code}")
            return "Ho sento, hi ha hagut un problema tècnic."
            
    except Exception as e:
        logger.error(f"Error getting bot response: {str(e)}")
        return "Ho sento, no puc processar la teva sol·licitud ara mateix."

async def get_welcome_message(bot_id: str, bot_type: str) -> str:
    """Get welcome message for bot"""
    try:
        if bot_type == "chatbot":
            bot = db.get_chatbot(bot_id)
        else:
            bot = db.get_voicebot(bot_id)
        
        if bot:
            return f"Hola! Sóc {bot['name']}, el teu assistent per telèfon. Com et puc ajudar avui?"
        else:
            return "Hola! Benvingut a VeuPlus. Com et puc ajudar?"
            
    except Exception as e:
        logger.error(f"Error getting welcome message: {str(e)}")
        return "Hola! Com et puc ajudar avui?"

@sip_router.get("/integrations")
async def list_sip_integrations():
    """List all SIP integrations"""
    try:
        integrations = db.get_sip_integrations()
        return {"integrations": integrations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch integrations: {str(e)}")

@sip_router.get("/integrations/{bot_id}")
async def get_bot_sip_integrations(bot_id: str):
    """Get SIP integrations for a specific bot"""
    try:
        integrations = db.get_sip_integrations(bot_id)
        return {"integrations": integrations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bot integrations: {str(e)}")

@sip_router.delete("/integrations/{sip_id}")
async def delete_sip_integration(sip_id: str):
    """Delete SIP integration"""
    try:
        # Get integration first
        integrations = db.execute_query("SELECT * FROM sip_integrations WHERE id = ?", (sip_id,))
        if not integrations:
            raise HTTPException(status_code=404, detail="SIP integration not found")
        
        integration = integrations[0]
        
        # Delete integration
        db.execute_delete("sip_integrations", "id = ?", (sip_id,))
        
        # Update bot to disable SIP
        if integration['bot_type'] == "chatbot":
            db.execute_update(
                "chatbots",
                {"sip_enabled": False, "sip_number": None},
                "id = ?",
                (integration['bot_id'],)
            )
        else:
            db.execute_update(
                "voicebots",
                {"sip_enabled": False, "sip_number": None}, 
                "id = ?",
                (integration['bot_id'],)
            )
        
        return {"message": "SIP integration deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete integration: {str(e)}")

@sip_router.get("/providers")
async def get_sip_providers():
    """Get available SIP providers"""
    return {"providers": SIP_PROVIDERS}

@sip_router.get("/call-stats")
async def get_call_statistics():
    """Get call statistics"""
    try:
        # Total calls and minutes
        stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_integrations,
                SUM(total_calls) as total_calls,
                SUM(total_minutes) as total_minutes,
                sip_provider,
                COUNT(*) as provider_count
            FROM sip_integrations 
            GROUP BY sip_provider
        """)
        
        return {
            "statistics": stats,
            "active_calls": len(active_calls),
            "summary": {
                "total_integrations": sum(s['provider_count'] for s in stats),
                "total_calls": sum(s['total_calls'] or 0 for s in stats),
                "total_minutes": sum(s['total_minutes'] or 0 for s in stats)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get call statistics: {str(e)}")
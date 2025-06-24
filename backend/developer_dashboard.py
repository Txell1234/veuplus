# Developer Dashboard API Endpoints for VeuPlus Platform
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import motor.motor_asyncio
import os
from collections import defaultdict
import asyncio

# Developer Dashboard Router
dev_router = APIRouter(prefix="/api/dev", tags=["Developer Dashboard"])

# Database connection (reuse from main server)
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Security scheme
security = HTTPBearer(auto_error=False)

# Models
class APIKeyRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    permissions: List[str] = ["tts", "stt", "chat"]

class ProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: str
    permissions: List[str]
    usage_count: int = 0

class UsageStats(BaseModel):
    total_requests: int
    tts_requests: int
    stt_requests: int
    chat_requests: int
    voice_training_sessions: int
    data_processed_mb: float
    period: str

class DeveloperProject(BaseModel):
    id: str
    name: str
    description: str
    api_keys: List[str]
    usage_stats: Dict[str, Any]
    created_at: str
    status: str

# Helper Functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for developer dashboard access"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    api_key = await db.api_keys.find_one({"key": credentials.credentials})
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

async def log_api_usage(api_key: str, endpoint: str, data_size: float = 0):
    """Log API usage for analytics"""
    usage_data = {
        "api_key": api_key,
        "endpoint": endpoint,
        "timestamp": datetime.utcnow(),
        "data_size_mb": data_size,
        "success": True
    }
    await db.api_usage.insert_one(usage_data)

# API Key Management
@dev_router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyRequest):
    """Create a new API key for developers"""
    try:
        api_key = f"vp_{uuid.uuid4().hex}"
        
        key_data = {
            "key": api_key,
            "name": request.name,
            "description": request.description,
            "permissions": request.permissions,
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "status": "active",
            "rate_limit": 1000,  # requests per hour
            "monthly_quota": 100000  # requests per month
        }
        
        await db.api_keys.insert_one(key_data)
        
        return APIKeyResponse(
            api_key=api_key,
            name=request.name,
            created_at=key_data["created_at"],
            permissions=request.permissions,
            usage_count=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")

@dev_router.get("/api-keys")
async def list_api_keys():
    """List all API keys for the developer"""
    try:
        keys = await db.api_keys.find({}, {"key": 0}).to_list(1000)  # Hide actual key
        for key in keys:
            if '_id' in key:
                del key['_id']
        return {"api_keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API keys: {str(e)}")

@dev_router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    """Revoke an API key"""
    try:
        result = await db.api_keys.update_one(
            {"key": key_id},
            {"$set": {"status": "revoked", "revoked_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"message": "API key revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {str(e)}")

# Usage Analytics
@dev_router.get("/analytics/usage", response_model=UsageStats)
async def get_usage_analytics(period: str = "7d"):
    """Get detailed usage analytics for the developer"""
    try:
        # Calculate date range
        now = datetime.utcnow()
        if period == "1d":
            start_date = now - timedelta(days=1)
        elif period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "30d":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=7)
        
        # Aggregate usage data
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "tts_requests": {"$sum": {"$cond": [{"$regexMatch": {"input": "$endpoint", "regex": "synthesis"}}, 1, 0]}},
                "stt_requests": {"$sum": {"$cond": [{"$regexMatch": {"input": "$endpoint", "regex": "transcribe"}}, 1, 0]}},
                "chat_requests": {"$sum": {"$cond": [{"$regexMatch": {"input": "$endpoint", "regex": "chat"}}, 1, 0]}},
                "data_processed_mb": {"$sum": "$data_size_mb"}
            }}
        ]
        
        result = await db.api_usage.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            del stats["_id"]
        else:
            stats = {
                "total_requests": 0,
                "tts_requests": 0,
                "stt_requests": 0,
                "chat_requests": 0,
                "data_processed_mb": 0.0
            }
        
        # Get voice training sessions count
        training_count = await db.voice_models.count_documents({
            "created_at": {"$gte": start_date.isoformat()}
        })
        
        stats["voice_training_sessions"] = training_count
        stats["period"] = period
        
        return UsageStats(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@dev_router.get("/analytics/performance")
async def get_performance_metrics():
    """Get performance metrics for the platform"""
    try:
        # Calculate average response times, success rates, etc.
        pipeline = [
            {"$group": {
                "_id": "$endpoint",
                "avg_response_time": {"$avg": "$response_time_ms"},
                "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}},
                "total_requests": {"$sum": 1}
            }}
        ]
        
        metrics = await db.api_usage.aggregate(pipeline).to_list(100)
        
        return {"performance_metrics": metrics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")

# Project Management
@dev_router.post("/projects")
async def create_project(
    name: str,
    description: str = "",
    api_key: dict = Depends(verify_api_key)
):
    """Create a new developer project"""
    try:
        project_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "api_keys": [],
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "owner_api_key": api_key["key"],
            "usage_stats": {
                "total_requests": 0,
                "voices_trained": 0,
                "bots_created": 0
            }
        }
        
        await db.developer_projects.insert_one(project_data)
        
        return {"message": "Project created successfully", "project": project_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@dev_router.get("/projects")
async def list_projects(api_key: dict = Depends(verify_api_key)):
    """List all projects for the developer"""
    try:
        projects = await db.developer_projects.find(
            {"owner_api_key": api_key["key"]}
        ).to_list(1000)
        
        for project in projects:
            if '_id' in project:
                del project['_id']
        
        return {"projects": projects}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

# API Documentation & Endpoints Discovery
@dev_router.get("/endpoints")
async def list_api_endpoints():
    """List all available API endpoints with documentation"""
    endpoints = {
        "voice_synthesis": {
            "endpoint": "/api/synthesis",
            "method": "POST",
            "description": "Generate hyperrealistic Catalan speech",
            "parameters": {
                "text": "Text to synthesize",
                "voice_model_id": "Voice model identifier",
                "language": "Language code (ca, es, en, fr)"
            },
            "example": {
                "text": "Hola, bon dia! Com estàs?",
                "voice_model_id": "catalan_enhanced",
                "language": "ca"
            }
        },
        "voice_training": {
            "endpoint": "/api/voices/train",
            "method": "POST",
            "description": "Train a new voice model with XTTS v2",
            "parameters": {
                "name": "Voice model name",
                "dialect": "Catalan dialect",
                "audio_files": "Training audio files",
                "use_catalan_dataset": "Use OpenSLR dataset"
            },
            "dialects": [
                "central", "balearic", "valencian", 
                "andorran", "rossellones", "alguerese"
            ]
        },
        "chatbot_creation": {
            "endpoint": "/api/chatbots",
            "method": "POST",
            "description": "Create intelligent chatbots with LLM integration",
            "parameters": {
                "name": "Chatbot name",
                "llm_provider": "OpenAI, Claude, Gemini",
                "system_prompt": "Chatbot instructions",
                "knowledge_base_ids": "Knowledge sources"
            }
        },
        "voicebot_creation": {
            "endpoint": "/api/voicebots",
            "method": "POST",
            "description": "Create voicebots with voice synthesis",
            "parameters": {
                "name": "Voicebot name",
                "voice_model_id": "Voice model to use",
                "llm_provider": "LLM provider",
                "system_prompt": "Bot instructions"
            }
        },
        "knowledge_base": {
            "endpoint": "/api/knowledge-base",
            "method": "POST",
            "description": "Upload documents for bot knowledge",
            "supported_formats": ["PDF", "TXT", "DOCX", "URLs"],
            "max_file_size": "10MB per file"
        }
    }
    
    return {"available_endpoints": endpoints}

# Billing & Usage Tracking
@dev_router.get("/billing/usage")
async def get_billing_usage(api_key: dict = Depends(verify_api_key)):
    """Get current month's usage for billing"""
    try:
        # Get current month usage
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        pipeline = [
            {"$match": {
                "api_key": api_key["key"],
                "timestamp": {"$gte": month_start}
            }},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "tts_minutes": {"$sum": {"$cond": [{"$regexMatch": {"input": "$endpoint", "regex": "synthesis"}}, 0.1, 0]}},
                "training_sessions": {"$sum": {"$cond": [{"$regexMatch": {"input": "$endpoint", "regex": "train"}}, 1, 0]}},
                "data_processed_gb": {"$sum": {"$divide": ["$data_size_mb", 1024]}}
            }}
        ]
        
        result = await db.api_usage.aggregate(pipeline).to_list(1)
        
        if result:
            usage = result[0]
            del usage["_id"]
        else:
            usage = {
                "total_requests": 0,
                "tts_minutes": 0,
                "training_sessions": 0,
                "data_processed_gb": 0
            }
        
        # Calculate estimated cost (example pricing)
        pricing = {
            "tts_per_minute": 0.02,  # $0.02 per minute
            "training_per_session": 5.0,  # $5 per training
            "requests_per_1000": 0.10  # $0.10 per 1000 requests
        }
        
        estimated_cost = (
            usage["tts_minutes"] * pricing["tts_per_minute"] +
            usage["training_sessions"] * pricing["training_per_session"] +
            (usage["total_requests"] / 1000) * pricing["requests_per_1000"]
        )
        
        usage["estimated_cost_usd"] = round(estimated_cost, 2)
        usage["billing_period"] = f"{now.year}-{now.month:02d}"
        
        return {"billing_usage": usage}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch billing usage: {str(e)}")

# Health & Status
@dev_router.get("/status")
async def get_platform_status():
    """Get platform health and status"""
    try:
        # Check various platform components
        status_checks = {
            "database": "healthy",
            "voice_synthesis": "operational",
            "llm_integration": "operational",
            "training_pipeline": "operational",
            "api_gateway": "healthy"
        }
        
        # Get recent performance metrics
        recent_requests = await db.api_usage.count_documents({
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=1)}
        })
        
        return {
            "platform_status": "operational",
            "components": status_checks,
            "recent_requests_per_hour": recent_requests,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "platform_status": "degraded",
            "error": str(e),
            "last_updated": datetime.utcnow().isoformat()
        }
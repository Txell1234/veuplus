# Developer Dashboard for VeuPlus - SQLite Version
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging

# SQLite Database connection - NO MORE MONGO!
try:
    from backend.database_sql import db as sql_db
except ImportError:
    from database_sql import db as sql_db

# Developer Dashboard Router
dev_router = APIRouter(prefix="/api/dev", tags=["Developer Dashboard"])

# Security scheme
security = HTTPBearer(auto_error=False)

# Models
class APIKeyRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    permissions: List[str] = ["tts", "stt", "chat"]

class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: str
    permissions: List[str]
    usage_count: int = 0

class UsageStats(BaseModel):
    period: str
    total_requests: int = 0
    data_processed_mb: float = 0.0
    tts_requests: int = 0
    stt_requests: int = 0
    chat_requests: int = 0
    voice_training_sessions: int = 0

class ProjectRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    api_keys: List[str]
    created_at: str
    usage_stats: Dict[str, Any]
    status: str

# Helper Functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for developer dashboard access"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # SQLite query
    api_keys = sql_db.execute_query("SELECT * FROM api_keys WHERE key = ? AND status = 'active'", (credentials.credentials,))
    if not api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_keys[0]

async def log_api_usage(api_key: str, endpoint: str, data_size: float = 0):
    """Log API usage for analytics"""
    usage_data = {
        "api_key": api_key,
        "endpoint": endpoint,
        "timestamp": datetime.utcnow().isoformat(),
        "data_size_mb": data_size,
        "success": True,
        "response_time_ms": 100,  # Default value
        "user_agent": "VeuPlus Developer Dashboard",
        "ip_address": "127.0.0.1"
    }
    sql_db.log_api_usage(usage_data)

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
            "permissions": ",".join(request.permissions),
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "status": "active",
            "rate_limit": 1000,  # requests per hour
            "monthly_quota": 100000  # requests per month
        }
        
        sql_db.execute_insert("api_keys", key_data)
        
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
        keys = sql_db.execute_query("SELECT name, description, permissions, created_at, usage_count, status, rate_limit, monthly_quota FROM api_keys ORDER BY created_at DESC")
        
        # Convert permissions back to list
        for key in keys:
            if key.get('permissions'):
                key['permissions'] = key['permissions'].split(',')
            else:
                key['permissions'] = []
        
        return {"api_keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API keys: {str(e)}")

@dev_router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    """Revoke an API key"""
    try:
        updates = {
            "status": "revoked",
            "updated_at": datetime.utcnow().isoformat()
        }
        rows_affected = sql_db.execute_update("api_keys", updates, "key = ?", (key_id,))
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return {"message": "API key revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {str(e)}")

# Usage Analytics - Simplified for SQLite
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
            start_date = now - timedelta(days=7)  # default

        start_date_str = start_date.isoformat()
        
        # Get usage analytics from SQLite
        try:
            analytics = sql_db.get_usage_analytics(start_date_str, None)
            total_requests = analytics.get('total_requests', 0)
        except:
            total_requests = 0
        
        # Get voice training count
        try:
            voice_models = sql_db.execute_query(
                "SELECT COUNT(*) as count FROM voice_models WHERE created_at >= ?", 
                (start_date_str,)
            )
            training_count = voice_models[0]['count'] if voice_models else 0
        except:
            training_count = 0
        
        # Get specific endpoint counts (basic implementation)
        try:
            tts_requests = sql_db.execute_query(
                "SELECT COUNT(*) as count FROM api_usage WHERE endpoint LIKE '%synthesis%' AND timestamp >= ?", 
                (start_date_str,)
            )
            tts_count = tts_requests[0]['count'] if tts_requests else 0
        except:
            tts_count = 0
            
        try:
            chat_requests = sql_db.execute_query(
                "SELECT COUNT(*) as count FROM api_usage WHERE endpoint LIKE '%chat%' AND timestamp >= ?", 
                (start_date_str,)
            )
            chat_count = chat_requests[0]['count'] if chat_requests else 0
        except:
            chat_count = 0
        
        return UsageStats(
            period=period,
            total_requests=total_requests,
            data_processed_mb=0.0,  # Will be enhanced later
            tts_requests=tts_count,
            stt_requests=0,  # Will be enhanced later
            chat_requests=chat_count,
            voice_training_sessions=training_count
        )
        
    except Exception as e:
        logging.error(f"Analytics error: {str(e)}")
        # Return default stats if there's an error
        return UsageStats(
            period=period,
            total_requests=0,
            data_processed_mb=0.0,
            tts_requests=0,
            stt_requests=0,
            chat_requests=0,
            voice_training_sessions=0
        )

# Projects Management - Simplified
@dev_router.post("/projects", response_model=ProjectResponse)
async def create_project(request: ProjectRequest):
    """Create a new developer project"""
    try:
        project_id = str(uuid.uuid4())
        
        project_data = {
            "id": project_id,
            "name": request.name,
            "description": request.description,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "api_keys": "[]",  # JSON string
            "usage_stats": "{}"  # JSON string
        }
        
        # Create projects table if it doesn't exist
        try:
            sql_db.execute_query("""
                CREATE TABLE IF NOT EXISTS developer_projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    api_keys TEXT DEFAULT '[]',
                    usage_stats TEXT DEFAULT '{}'
                )
            """)
        except:
            pass
        
        sql_db.execute_insert("developer_projects", project_data)
        
        return ProjectResponse(
            id=project_id,
            name=request.name,
            description=request.description,
            api_keys=[],
            created_at=project_data["created_at"],
            usage_stats={},
            status="active"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@dev_router.get("/projects")
async def list_projects():
    """List all developer projects"""
    try:
        projects = sql_db.execute_query("SELECT * FROM developer_projects ORDER BY created_at DESC")
        
        # Convert JSON strings back to objects
        for project in projects:
            try:
                import json
                project['api_keys'] = json.loads(project.get('api_keys', '[]'))
                project['usage_stats'] = json.loads(project.get('usage_stats', '{}'))
            except:
                project['api_keys'] = []
                project['usage_stats'] = {}
        
        return {"projects": projects}
    except Exception as e:
        # Return empty list if table doesn't exist yet
        return {"projects": []}

# Health check for developer dashboard
@dev_router.get("/health")
async def dev_health_check():
    """Developer dashboard health check"""
    try:
        # Test SQLite connection
        test_query = sql_db.execute_query("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        
        return {
            "status": "healthy",
            "database": "sqlite",
            "timestamp": datetime.utcnow().isoformat(),
            "tables_available": len(test_query) > 0,
            "version": "2.0.0-sqlite"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "sqlite",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Placeholder endpoints for compatibility
@dev_router.get("/metrics")
async def get_metrics():
    """Get platform metrics"""
    return {
        "platform_status": "operational",
        "total_users": 0,
        "active_bots": 0,
        "tts_minutes_today": 0,
        "api_calls_today": 0
    }

@dev_router.get("/quota")
async def get_quota_usage():
    """Get quota usage information"""
    return {
        "current_usage": {
            "api_calls": 0,
            "tts_minutes": 0,
            "storage_mb": 0
        },
        "limits": {
            "api_calls": 100000,
            "tts_minutes": 1000,
            "storage_mb": 10000
        },
        "reset_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

#!/usr/bin/env python3
"""
Endpoints SIP per evitar errors 404
"""
import logging
from fastapi import APIRouter

logger = logging.getLogger("veuplus.sip_endpoints")

# Router SIP
sip_router = APIRouter(prefix="/api/sip", tags=["SIP Endpoints"])

@sip_router.get("/configuration")
async def sip_configuration():
    """Configuració SIP (placeholder)"""
    return {
        "success": True,
        "configuration": {
            "enabled": False,
            "status": "not_configured"
        }
    }

@sip_router.get("/knowledge-stats")
async def sip_knowledge_stats():
    """Estadístiques de coneixement SIP (placeholder)"""
    return {
        "success": True,
        "stats": {
            "total_documents": 0,
            "total_queries": 0,
            "status": "not_configured"
        }
    }

@sip_router.get("/health")
async def sip_health():
    """Health check SIP"""
    return {"status": "ok", "message": "SIP endpoints funcionant"}

#!/usr/bin/env python3
"""
ConvHi Widget Management - Sistema de gestió de widgets i dominis
Gestió d'allowlist, configuració de dominis i administració de widgets
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import os
import json
from datetime import datetime

logger = logging.getLogger("veuplus.widget-management")

router = APIRouter(prefix="/api/convhi/widget-management", tags=["ConvHi Widget Management"])

# Models
class DomainAllowlistRequest(BaseModel):
    domains: List[str]
    action: str  # "add", "remove", "replace"

class DomainAllowlistResponse(BaseModel):
    success: bool
    domains: List[str]
    message: str

class WidgetStatsResponse(BaseModel):
    total_widgets: int
    active_domains: int
    total_requests: int
    last_24h_requests: int

class WidgetManagementEngine:
    def __init__(self):
        self.allowlist_file = "backend/widget_allowlist.json"
        self.stats_file = "backend/widget_stats.json"
        self._load_allowlist()
        self._load_stats()
    
    def _load_allowlist(self):
        """Carregar llista de dominis permesos"""
        try:
            if os.path.exists(self.allowlist_file):
                with open(self.allowlist_file, 'r') as f:
                    data = json.load(f)
                    self.allowed_domains = data.get('domains', [])
            else:
                # Dominis per defecte
                self.allowed_domains = [
                    "localhost",
                    "127.0.0.1",
                    "localhost:3000",
                    "localhost:5173",
                    "localhost:8080"
                ]
                self._save_allowlist()
        except Exception as e:
            logger.error(f"Error loading allowlist: {e}")
            self.allowed_domains = ["localhost", "127.0.0.1"]
    
    def _save_allowlist(self):
        """Guardar llista de dominis permesos"""
        try:
            data = {
                'domains': self.allowed_domains,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.allowlist_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving allowlist: {e}")
    
    def _load_stats(self):
        """Carregar estadístiques de widgets"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            else:
                self.stats = {
                    'total_widgets': 0,
                    'active_domains': 0,
                    'total_requests': 0,
                    'last_24h_requests': 0,
                    'requests_by_domain': {},
                    'last_updated': datetime.now().isoformat()
                }
                self._save_stats()
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
            self.stats = {
                'total_widgets': 0,
                'active_domains': 0,
                'total_requests': 0,
                'last_24h_requests': 0,
                'requests_by_domain': {},
                'last_updated': datetime.now().isoformat()
            }
    
    def _save_stats(self):
        """Guardar estadístiques"""
        try:
            self.stats['last_updated'] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Verificar si un domini està permès"""
        if not domain:
            return False
        
        # Verificar coincidències exactes
        if domain in self.allowed_domains:
            return True
        
        # Verificar coincidències parcials (per subdominis)
        for allowed in self.allowed_domains:
            if domain.endswith(allowed) or allowed.endswith(domain):
                return True
        
        return False
    
    def add_domains(self, domains: List[str]) -> bool:
        """Afegir dominis a l'allowlist"""
        try:
            new_domains = []
            for domain in domains:
                domain = domain.strip().lower()
                if domain and domain not in self.allowed_domains:
                    self.allowed_domains.append(domain)
                    new_domains.append(domain)
            
            if new_domains:
                self._save_allowlist()
                logger.info(f"Added domains to allowlist: {new_domains}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding domains: {e}")
            return False
    
    def remove_domains(self, domains: List[str]) -> bool:
        """Eliminar dominis de l'allowlist"""
        try:
            removed_domains = []
            for domain in domains:
                domain = domain.strip().lower()
                if domain in self.allowed_domains:
                    self.allowed_domains.remove(domain)
                    removed_domains.append(domain)
            
            if removed_domains:
                self._save_allowlist()
                logger.info(f"Removed domains from allowlist: {removed_domains}")
            
            return True
        except Exception as e:
            logger.error(f"Error removing domains: {e}")
            return False
    
    def replace_domains(self, domains: List[str]) -> bool:
        """Reemplaçar tots els dominis de l'allowlist"""
        try:
            self.allowed_domains = [d.strip().lower() for d in domains if d.strip()]
            self._save_allowlist()
            logger.info(f"Replaced allowlist with domains: {self.allowed_domains}")
            return True
        except Exception as e:
            logger.error(f"Error replacing domains: {e}")
            return False
    
    def record_widget_request(self, domain: str, agent_id: str):
        """Registrar una petició de widget"""
        try:
            self.stats['total_requests'] += 1
            self.stats['last_24h_requests'] += 1
            
            if domain not in self.stats['requests_by_domain']:
                self.stats['requests_by_domain'][domain] = 0
            self.stats['requests_by_domain'][domain] += 1
            
            self._save_stats()
        except Exception as e:
            logger.error(f"Error recording widget request: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir estadístiques"""
        return {
            'total_widgets': self.stats.get('total_widgets', 0),
            'active_domains': len(self.allowed_domains),
            'total_requests': self.stats.get('total_requests', 0),
            'last_24h_requests': self.stats.get('last_24h_requests', 0),
            'requests_by_domain': self.stats.get('requests_by_domain', {}),
            'allowed_domains': self.allowed_domains
        }

# Instància global
widget_manager = WidgetManagementEngine()

# Endpoints
@router.get("/allowlist")
async def get_allowlist():
    """Obtenir llista de dominis permesos"""
    try:
        return {
            "success": True,
            "domains": widget_manager.allowed_domains,
            "total": len(widget_manager.allowed_domains)
        }
    except Exception as e:
        logger.error(f"Error getting allowlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/allowlist", response_model=DomainAllowlistResponse)
async def manage_allowlist(request: DomainAllowlistRequest):
    """Gestionar llista de dominis permesos"""
    try:
        success = False
        
        if request.action == "add":
            success = widget_manager.add_domains(request.domains)
            message = f"Added {len(request.domains)} domains to allowlist"
        elif request.action == "remove":
            success = widget_manager.remove_domains(request.domains)
            message = f"Removed {len(request.domains)} domains from allowlist"
        elif request.action == "replace":
            success = widget_manager.replace_domains(request.domains)
            message = f"Replaced allowlist with {len(request.domains)} domains"
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'remove', or 'replace'")
        
        if success:
            return DomainAllowlistResponse(
                success=True,
                domains=widget_manager.allowed_domains,
                message=message
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update allowlist")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error managing allowlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=WidgetStatsResponse)
async def get_widget_stats():
    """Obtenir estadístiques de widgets"""
    try:
        stats = widget_manager.get_stats()
        return WidgetStatsResponse(
            total_widgets=stats['total_widgets'],
            active_domains=stats['active_domains'],
            total_requests=stats['total_requests'],
            last_24h_requests=stats['last_24h_requests']
        )
    except Exception as e:
        logger.error(f"Error getting widget stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/detailed")
async def get_detailed_stats():
    """Obtenir estadístiques detallades"""
    try:
        return {
            "success": True,
            "stats": widget_manager.get_stats()
        }
    except Exception as e:
        logger.error(f"Error getting detailed stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-domain")
async def validate_domain(request: Request):
    """Validar si un domini està permès"""
    try:
        domain = request.headers.get("origin", "").replace("http://", "").replace("https://", "")
        is_allowed = widget_manager.is_domain_allowed(domain)
        
        return {
            "success": True,
            "domain": domain,
            "allowed": is_allowed,
            "message": f"Domain {domain} is {'allowed' if is_allowed else 'not allowed'}"
        }
    except Exception as e:
        logger.error(f"Error validating domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-request")
async def record_widget_request(request: Request):
    """Registrar una petició de widget"""
    try:
        data = await request.json()
        domain = data.get("domain", "")
        agent_id = data.get("agent_id", "")
        
        widget_manager.record_widget_request(domain, agent_id)
        
        return {
            "success": True,
            "message": "Request recorded successfully"
        }
    except Exception as e:
        logger.error(f"Error recording request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def widget_management_health():
    """Health check del sistema de gestió de widgets"""
    return {
        "status": "ok",
        "message": "Widget management system funcionant",
        "stats": {
            "allowed_domains": len(widget_manager.allowed_domains),
            "total_requests": widget_manager.stats.get('total_requests', 0),
            "last_updated": widget_manager.stats.get('last_updated', 'unknown')
        }
    }

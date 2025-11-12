#!/usr/bin/env python3
"""
ConvHi CRM Connectors - Sistema de connectors CRM
Suport per Salesforce, HubSpot, i altres sistemes CRM
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

logger = logging.getLogger("veuplus.crm-connectors")

router = APIRouter(prefix="/api/convhi/crm-connectors", tags=["ConvHi CRM Connectors"])

# Enums
class ConnectorType(str, Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    PIPEDRIVE = "pipedrive"
    ZENDESK = "zendesk"
    CUSTOM = "custom"

class ConnectorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"

class SyncStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Models
class CRMConnector(BaseModel):
    id: str
    name: str
    connector_type: ConnectorType
    status: ConnectorStatus = ConnectorStatus.INACTIVE
    config: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    last_sync_at: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    total_contacts: int = 0
    last_error: Optional[str] = None

class ConnectorConfig(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    sync_settings: Dict[str, Any] = {}

class ContactRecord(BaseModel):
    id: str
    connector_id: str
    external_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    last_updated: datetime
    sync_status: SyncStatus = SyncStatus.PENDING

class SyncJob(BaseModel):
    id: str
    connector_id: str
    status: SyncStatus = SyncStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_records: int = 0
    processed_records: int = 0
    error_message: Optional[str] = None
    sync_type: str = "full"  # full, incremental

# In-memory storage
connectors = {}
contacts = {}
sync_jobs = {}

class CRMConnectorEngine:
    def __init__(self):
        self.active_syncs = set()
        logger.info("✅ CRM Connector Engine inicialitzat")
    
    async def create_connector(self, name: str, connector_type: ConnectorType, config: ConnectorConfig) -> CRMConnector:
        """Crear un connector CRM"""
        try:
            connector_id = str(uuid.uuid4())
            
            connector = CRMConnector(
                id=connector_id,
                name=name,
                connector_type=connector_type,
                config=config.dict(),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            connectors[connector_id] = connector
            
            logger.info(f"✅ Connector CRM creat: {name} ({connector_type})")
            return connector
            
        except Exception as e:
            logger.error(f"Error creant connector CRM: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def test_connection(self, connector_id: str) -> bool:
        """Provar connexió amb CRM"""
        try:
            if connector_id not in connectors:
                raise HTTPException(status_code=404, detail="Connector no trobat")
            
            connector = connectors[connector_id]
            
            # Simular test de connexió basat en el tipus
            if connector.connector_type == ConnectorType.SALESFORCE:
                return await self._test_salesforce_connection(connector)
            elif connector.connector_type == ConnectorType.HUBSPOT:
                return await self._test_hubspot_connection(connector)
            elif connector.connector_type == ConnectorType.PIPEDRIVE:
                return await self._test_pipedrive_connection(connector)
            else:
                return await self._test_custom_connection(connector)
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error provant connexió: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _test_salesforce_connection(self, connector: CRMConnector) -> bool:
        """Provar connexió Salesforce"""
        # Simular test de connexió
        await asyncio.sleep(1)
        
        config = connector.config
        if not config.get('api_key') or not config.get('api_secret'):
            connector.status = ConnectorStatus.ERROR
            connector.last_error = "API key o secret mancants"
            return False
        
        connector.status = ConnectorStatus.ACTIVE
        connector.last_error = None
        return True
    
    async def _test_hubspot_connection(self, connector: CRMConnector) -> bool:
        """Provar connexió HubSpot"""
        await asyncio.sleep(1)
        
        config = connector.config
        if not config.get('api_key'):
            connector.status = ConnectorStatus.ERROR
            connector.last_error = "API key mancant"
            return False
        
        connector.status = ConnectorStatus.ACTIVE
        connector.last_error = None
        return True
    
    async def _test_pipedrive_connection(self, connector: CRMConnector) -> bool:
        """Provar connexió Pipedrive"""
        await asyncio.sleep(1)
        
        config = connector.config
        if not config.get('api_key'):
            connector.status = ConnectorStatus.ERROR
            connector.last_error = "API key mancant"
            return False
        
        connector.status = ConnectorStatus.ACTIVE
        connector.last_error = None
        return True
    
    async def _test_custom_connection(self, connector: CRMConnector) -> bool:
        """Provar connexió custom"""
        await asyncio.sleep(1)
        
        config = connector.config
        if not config.get('base_url'):
            connector.status = ConnectorStatus.ERROR
            connector.last_error = "Base URL mancant"
            return False
        
        connector.status = ConnectorStatus.ACTIVE
        connector.last_error = None
        return True
    
    async def sync_connector(self, connector_id: str, sync_type: str = "full") -> str:
        """Sincronitzar connector CRM"""
        try:
            if connector_id not in connectors:
                raise HTTPException(status_code=404, detail="Connector no trobat")
            
            connector = connectors[connector_id]
            
            if connector.status != ConnectorStatus.ACTIVE:
                raise HTTPException(status_code=400, detail="Connector no actiu")
            
            # Crear job de sincronització
            job_id = str(uuid.uuid4())
            sync_job = SyncJob(
                id=job_id,
                connector_id=connector_id,
                sync_type=sync_type,
                started_at=datetime.now()
            )
            
            sync_jobs[job_id] = sync_job
            connector.sync_status = SyncStatus.IN_PROGRESS
            self.active_syncs.add(job_id)
            
            # Executar sincronització en background
            asyncio.create_task(self._execute_sync(job_id))
            
            logger.info(f"✅ Sincronització iniciada: {connector.name}")
            return job_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error iniciant sincronització: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _execute_sync(self, job_id: str):
        """Executar sincronització en background"""
        try:
            sync_job = sync_jobs[job_id]
            connector = connectors[sync_job.connector_id]
            
            # Simular sincronització
            await asyncio.sleep(5)
            
            # Simular dades de contactes
            contacts_data = self._generate_sample_contacts(sync_job.connector_id)
            
            # Processar contactes
            for contact_data in contacts_data:
                contact = ContactRecord(
                    id=str(uuid.uuid4()),
                    connector_id=sync_job.connector_id,
                    external_id=contact_data['external_id'],
                    name=contact_data['name'],
                    email=contact_data.get('email'),
                    phone=contact_data.get('phone'),
                    company=contact_data.get('company'),
                    custom_fields=contact_data.get('custom_fields', {}),
                    last_updated=datetime.now(),
                    sync_status=SyncStatus.COMPLETED
                )
                contacts[contact.id] = contact
                sync_job.processed_records += 1
            
            # Finalitzar job
            sync_job.status = SyncStatus.COMPLETED
            sync_job.completed_at = datetime.now()
            sync_job.total_records = len(contacts_data)
            
            connector.sync_status = SyncStatus.COMPLETED
            connector.last_sync_at = datetime.now()
            connector.total_contacts = len([c for c in contacts.values() if c.connector_id == connector.id])
            
            logger.info(f"✅ Sincronització completada: {job_id}")
            
        except Exception as e:
            logger.error(f"Error executant sincronització {job_id}: {e}")
            sync_job.status = SyncStatus.FAILED
            sync_job.error_message = str(e)
            connector.sync_status = SyncStatus.FAILED
            connector.last_error = str(e)
        finally:
            self.active_syncs.discard(job_id)
    
    def _generate_sample_contacts(self, connector_id: str) -> List[Dict[str, Any]]:
        """Generar contactes de mostra"""
        sample_contacts = [
            {
                'external_id': 'sf_001',
                'name': 'Joan Garcia',
                'email': 'joan.garcia@empresa.com',
                'phone': '+34123456789',
                'company': 'Empresa A',
                'custom_fields': {'industry': 'Technology', 'lead_score': 85}
            },
            {
                'external_id': 'sf_002',
                'name': 'Maria Lopez',
                'email': 'maria.lopez@empresa.com',
                'phone': '+34987654321',
                'company': 'Empresa B',
                'custom_fields': {'industry': 'Finance', 'lead_score': 92}
            },
            {
                'external_id': 'sf_003',
                'name': 'Pere Martinez',
                'email': 'pere.martinez@empresa.com',
                'phone': '+34555666777',
                'company': 'Empresa C',
                'custom_fields': {'industry': 'Healthcare', 'lead_score': 78}
            }
        ]
        return sample_contacts
    
    def get_connector_contacts(self, connector_id: str, limit: int = 100) -> List[ContactRecord]:
        """Obtenir contactes d'un connector"""
        connector_contacts = [
            contact for contact in contacts.values() 
            if contact.connector_id == connector_id
        ]
        return connector_contacts[:limit]
    
    def get_connector_stats(self, connector_id: str) -> Dict[str, Any]:
        """Obtenir estadístiques del connector"""
        if connector_id not in connectors:
            return {}
        
        connector = connectors[connector_id]
        connector_contacts = self.get_connector_contacts(connector_id)
        
        return {
            'total_contacts': len(connector_contacts),
            'last_sync': connector.last_sync_at.isoformat() if connector.last_sync_at else None,
            'sync_status': connector.sync_status,
            'status': connector.status,
            'last_error': connector.last_error
        }

# Instància global
crm_engine = CRMConnectorEngine()

# Endpoints
@router.post("/connectors")
async def create_connector(
    name: str,
    connector_type: ConnectorType,
    config: ConnectorConfig
):
    """Crear connector CRM"""
    try:
        connector = await crm_engine.create_connector(name, connector_type, config)
        return {
            "success": True,
            "connector": connector.dict(),
            "message": f"Connector {name} creat correctament"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creant connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_connectors():
    """Llistar connectors CRM"""
    try:
        connector_list = []
        for connector in connectors.values():
            stats = crm_engine.get_connector_stats(connector.id)
            connector_list.append({
                "connector": connector.dict(),
                "stats": stats
            })
        
        return {
            "success": True,
            "connectors": connector_list,
            "total": len(connector_list)
        }
    except Exception as e:
        logger.error(f"Error llistant connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors/{connector_id}")
async def get_connector(connector_id: str):
    """Obtenir connector CRM"""
    try:
        if connector_id not in connectors:
            raise HTTPException(status_code=404, detail="Connector no trobat")
        
        connector = connectors[connector_id]
        stats = crm_engine.get_connector_stats(connector_id)
        
        return {
            "success": True,
            "connector": connector.dict(),
            "stats": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connectors/{connector_id}/test")
async def test_connector(connector_id: str):
    """Provar connexió connector"""
    try:
        success = await crm_engine.test_connection(connector_id)
        
        return {
            "success": success,
            "message": "Connexió provada correctament" if success else "Error en la connexió"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error provant connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connectors/{connector_id}/sync")
async def sync_connector(connector_id: str, sync_type: str = "full"):
    """Sincronitzar connector CRM"""
    try:
        job_id = await crm_engine.sync_connector(connector_id, sync_type)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Sincronització iniciada"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sincronitzant connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors/{connector_id}/contacts")
async def get_connector_contacts(connector_id: str, limit: int = 100):
    """Obtenir contactes del connector"""
    try:
        if connector_id not in connectors:
            raise HTTPException(status_code=404, detail="Connector no trobat")
        
        contacts_list = crm_engine.get_connector_contacts(connector_id, limit)
        
        return {
            "success": True,
            "contacts": [contact.dict() for contact in contacts_list],
            "total": len(contacts_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint contactes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync-jobs/{job_id}")
async def get_sync_job(job_id: str):
    """Obtenir estat del job de sincronització"""
    try:
        if job_id not in sync_jobs:
            raise HTTPException(status_code=404, detail="Job de sincronització no trobat")
        
        sync_job = sync_jobs[job_id]
        
        return {
            "success": True,
            "job": sync_job.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync-jobs")
async def list_sync_jobs():
    """Llistar jobs de sincronització"""
    try:
        jobs_list = []
        for job in sync_jobs.values():
            connector = connectors.get(job.connector_id)
            jobs_list.append({
                "job": job.dict(),
                "connector_name": connector.name if connector else "Unknown"
            })
        
        return {
            "success": True,
            "jobs": jobs_list,
            "total": len(jobs_list)
        }
    except Exception as e:
        logger.error(f"Error llistant jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connectors/{connector_id}")
async def delete_connector(connector_id: str):
    """Eliminar connector CRM"""
    try:
        if connector_id not in connectors:
            raise HTTPException(status_code=404, detail="Connector no trobat")
        
        # Eliminar connector i contactes associats
        del connectors[connector_id]
        
        # Eliminar contactes del connector
        contacts_to_delete = [cid for cid, contact in contacts.items() if contact.connector_id == connector_id]
        for cid in contacts_to_delete:
            del contacts[cid]
        
        logger.info(f"✅ Connector eliminat: {connector_id}")
        
        return {
            "success": True,
            "message": "Connector eliminat correctament"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminant connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def crm_connectors_health():
    """Health check del sistema de connectors CRM"""
    return {
        "status": "ok",
        "message": "Sistema de connectors CRM funcionant",
        "stats": {
            "total_connectors": len(connectors),
            "total_contacts": len(contacts),
            "active_syncs": len(crm_engine.active_syncs),
            "total_sync_jobs": len(sync_jobs)
        }
    }




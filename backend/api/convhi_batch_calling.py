#!/usr/bin/env python3
"""
ConvHi Batch Calling System - Sistema de trucades massives
Suport per CSV, validació, monitorització de progrés i reintentos
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import csv
import json
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import uuid
import os

logger = logging.getLogger("veuplus.batch-calling")

router = APIRouter(prefix="/api/convhi/batch-calling", tags=["ConvHi Batch Calling"])

# Enums
class CallStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BatchStatus(str, Enum):
    CREATED = "created"
    VALIDATING = "validating"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Models
class BatchCallRequest(BaseModel):
    agent_id: str
    batch_name: str
    description: Optional[str] = None
    max_concurrent_calls: int = Field(default=5, ge=1, le=20)
    retry_attempts: int = Field(default=2, ge=0, le=5)
    retry_delay_seconds: int = Field(default=30, ge=10, le=300)
    scheduled_time: Optional[datetime] = None
    dynamic_variables: Dict[str, Any] = {}
    call_settings: Dict[str, Any] = {}

class CallRecord(BaseModel):
    id: str
    batch_id: str
    phone_number: str
    recipient_name: Optional[str] = None
    custom_variables: Dict[str, Any] = {}
    status: CallStatus = CallStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    call_result: Optional[Dict[str, Any]] = None

class BatchCall(BaseModel):
    id: str
    agent_id: str
    batch_name: str
    description: Optional[str] = None
    status: BatchStatus = BatchStatus.CREATED
    total_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    success_rate: float = 0.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    max_concurrent_calls: int = 5
    retry_attempts: int = 2
    retry_delay_seconds: int = 30
    scheduled_time: Optional[datetime] = None
    dynamic_variables: Dict[str, Any] = {}
    call_settings: Dict[str, Any] = {}
    call_records: List[CallRecord] = []

class BatchCallResponse(BaseModel):
    success: bool
    batch_id: str
    message: str
    total_records: int
    valid_records: int
    invalid_records: int

class BatchProgressResponse(BaseModel):
    batch_id: str
    status: BatchStatus
    progress_percentage: float
    total_calls: int
    completed_calls: int
    failed_calls: int
    in_progress_calls: int
    success_rate: float
    estimated_completion: Optional[datetime] = None

# In-memory storage (en producció seria una base de dades)
batch_calls = {}
call_records = {}
batch_jobs = {}

class BatchCallingEngine:
    def __init__(self):
        self.active_batches = set()
        self.max_concurrent_batches = 3
        logger.info("✅ Batch Calling Engine inicialitzat")
    
    async def create_batch_call(self, request: BatchCallRequest, records: List[Dict[str, Any]]) -> BatchCallResponse:
        """Crear una trucada massiva"""
        try:
            batch_id = str(uuid.uuid4())
            
            # Validar registres
            valid_records, invalid_records = self._validate_records(records)
            
            if not valid_records:
                raise HTTPException(status_code=400, detail="No hi ha registres vàlids per processar")
            
            # Crear registres de trucada
            call_records_list = []
            for i, record in enumerate(valid_records):
                call_record = CallRecord(
                    id=f"{batch_id}_{i}",
                    batch_id=batch_id,
                    phone_number=record.get('phone_number', ''),
                    recipient_name=record.get('name', record.get('recipient_name')),
                    custom_variables=record.get('variables', {}),
                    created_at=datetime.now()
                )
                call_records_list.append(call_record)
                call_records[call_record.id] = call_record
            
            # Crear batch call
            batch_call = BatchCall(
                id=batch_id,
                agent_id=request.agent_id,
                batch_name=request.batch_name,
                description=request.description,
                status=BatchStatus.CREATED,
                total_calls=len(valid_records),
                created_at=datetime.now(),
                max_concurrent_calls=request.max_concurrent_calls,
                retry_attempts=request.retry_attempts,
                retry_delay_seconds=request.retry_delay_seconds,
                scheduled_time=request.scheduled_time,
                dynamic_variables=request.dynamic_variables,
                call_settings=request.call_settings,
                call_records=call_records_list
            )
            
            batch_calls[batch_id] = batch_call
            
            logger.info(f"✅ Batch call creat: {batch_id} amb {len(valid_records)} trucades")
            
            return BatchCallResponse(
                success=True,
                batch_id=batch_id,
                message=f"Batch call creat amb {len(valid_records)} trucades vàlides",
                total_records=len(records),
                valid_records=len(valid_records),
                invalid_records=len(invalid_records)
            )
            
        except Exception as e:
            logger.error(f"Error creant batch call: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _validate_records(self, records: List[Dict[str, Any]]) -> tuple:
        """Validar registres de trucada"""
        valid_records = []
        invalid_records = []
        
        for i, record in enumerate(records):
            try:
                # Validar número de telèfon
                phone = record.get('phone_number', '').strip()
                if not phone or len(phone) < 10:
                    invalid_records.append({
                        'index': i,
                        'record': record,
                        'error': 'Número de telèfon invàlid'
                    })
                    continue
                
                # Validar altres camps opcionals
                validated_record = {
                    'phone_number': phone,
                    'name': record.get('name', record.get('recipient_name', '')),
                    'variables': record.get('variables', {})
                }
                
                valid_records.append(validated_record)
                
            except Exception as e:
                invalid_records.append({
                    'index': i,
                    'record': record,
                    'error': str(e)
                })
        
        return valid_records, invalid_records
    
    async def start_batch_call(self, batch_id: str, background_tasks: BackgroundTasks) -> bool:
        """Iniciar una trucada massiva"""
        try:
            if batch_id not in batch_calls:
                raise HTTPException(status_code=404, detail="Batch call no trobat")
            
            batch_call = batch_calls[batch_id]
            
            if batch_call.status != BatchStatus.CREATED:
                raise HTTPException(status_code=400, detail="Batch call ja ha estat processat")
            
            # Verificar límit de batches concurrents
            if len(self.active_batches) >= self.max_concurrent_batches:
                raise HTTPException(status_code=429, detail="Massa batches actius. Espera que acabin alguns.")
            
            # Actualitzar estat
            batch_call.status = BatchStatus.RUNNING
            batch_call.started_at = datetime.now()
            self.active_batches.add(batch_id)
            
            # Programar execució en background
            background_tasks.add_task(self._execute_batch_call, batch_id)
            
            logger.info(f"✅ Batch call iniciat: {batch_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error iniciant batch call: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _execute_batch_call(self, batch_id: str):
        """Executar trucada massiva en background"""
        try:
            batch_call = batch_calls[batch_id]
            call_records_list = [cr for cr in call_records.values() if cr.batch_id == batch_id]
            
            # Processar trucades en lots
            semaphore = asyncio.Semaphore(batch_call.max_concurrent_calls)
            
            async def process_call(call_record: CallRecord):
                async with semaphore:
                    await self._make_call(call_record, batch_call)
            
            # Executar totes les trucades
            tasks = [process_call(cr) for cr in call_records_list]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Finalitzar batch
            await self._finalize_batch(batch_id)
            
        except Exception as e:
            logger.error(f"Error executant batch call {batch_id}: {e}")
            batch_calls[batch_id].status = BatchStatus.FAILED
        finally:
            self.active_batches.discard(batch_id)
    
    async def _make_call(self, call_record: CallRecord, batch_call: BatchCall):
        """Fer una trucada individual"""
        try:
            call_record.status = CallStatus.IN_PROGRESS
            call_record.started_at = datetime.now()
            
            # Simular trucada (en producció seria una trucada real)
            await asyncio.sleep(2)  # Simular durada de trucada
            
            # Simular resultat
            success = call_record.retry_count < batch_call.retry_attempts
            
            if success:
                call_record.status = CallStatus.COMPLETED
                call_record.completed_at = datetime.now()
                call_record.duration_seconds = 120  # Simular durada
                call_record.call_result = {
                    "transcript": "Trucada completada amb èxit",
                    "sentiment": "positive",
                    "intent": "information_request"
                }
            else:
                call_record.status = CallStatus.FAILED
                call_record.error_message = "Trucada fallida després de reintentos"
            
            # Actualitzar estadístiques del batch
            self._update_batch_stats(batch_call.id)
            
        except Exception as e:
            logger.error(f"Error fent trucada {call_record.id}: {e}")
            call_record.status = CallStatus.FAILED
            call_record.error_message = str(e)
            self._update_batch_stats(batch_call.id)
    
    def _update_batch_stats(self, batch_id: str):
        """Actualitzar estadístiques del batch"""
        batch_call = batch_calls[batch_id]
        call_records_list = [cr for cr in call_records.values() if cr.batch_id == batch_id]
        
        batch_call.completed_calls = len([cr for cr in call_records_list if cr.status == CallStatus.COMPLETED])
        batch_call.failed_calls = len([cr for cr in call_records_list if cr.status == CallStatus.FAILED])
        
        if batch_call.total_calls > 0:
            batch_call.success_rate = (batch_call.completed_calls / batch_call.total_calls) * 100
    
    async def _finalize_batch(self, batch_id: str):
        """Finalitzar batch call"""
        batch_call = batch_calls[batch_id]
        batch_call.status = BatchStatus.COMPLETED
        batch_call.completed_at = datetime.now()
        
        logger.info(f"✅ Batch call finalitzat: {batch_id} - Èxit: {batch_call.success_rate:.1f}%")
    
    def get_batch_progress(self, batch_id: str) -> Optional[BatchProgressResponse]:
        """Obtenir progrés del batch"""
        if batch_id not in batch_calls:
            return None
        
        batch_call = batch_calls[batch_id]
        call_records_list = [cr for cr in call_records.values() if cr.batch_id == batch_id]
        
        in_progress_calls = len([cr for cr in call_records_list if cr.status == CallStatus.IN_PROGRESS])
        
        progress_percentage = 0
        if batch_call.total_calls > 0:
            progress_percentage = ((batch_call.completed_calls + batch_call.failed_calls) / batch_call.total_calls) * 100
        
        estimated_completion = None
        if batch_call.status == BatchStatus.RUNNING and in_progress_calls > 0:
            # Estimar temps de finalització basat en trucades restants
            remaining_calls = batch_call.total_calls - batch_call.completed_calls - batch_call.failed_calls
            avg_call_duration = 120  # segons
            estimated_seconds = remaining_calls * avg_call_duration / batch_call.max_concurrent_calls
            estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
        
        return BatchProgressResponse(
            batch_id=batch_id,
            status=batch_call.status,
            progress_percentage=progress_percentage,
            total_calls=batch_call.total_calls,
            completed_calls=batch_call.completed_calls,
            failed_calls=batch_call.failed_calls,
            in_progress_calls=in_progress_calls,
            success_rate=batch_call.success_rate,
            estimated_completion=estimated_completion
        )
    
    def cancel_batch_call(self, batch_id: str) -> bool:
        """Cancel·lar batch call"""
        try:
            if batch_id not in batch_calls:
                return False
            
            batch_call = batch_calls[batch_id]
            
            if batch_call.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]:
                return False
            
            batch_call.status = BatchStatus.CANCELLED
            self.active_batches.discard(batch_id)
            
            # Cancel·lar trucades pendents
            call_records_list = [cr for cr in call_records.values() if cr.batch_id == batch_id]
            for call_record in call_records_list:
                if call_record.status == CallStatus.PENDING:
                    call_record.status = CallStatus.CANCELLED
            
            logger.info(f"✅ Batch call cancel·lat: {batch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancel·lant batch call: {e}")
            return False

# Instància global
batch_engine = BatchCallingEngine()

# Endpoints
@router.post("/create", response_model=BatchCallResponse)
async def create_batch_call(request: BatchCallRequest, records: List[Dict[str, Any]]):
    """Crear una trucada massiva"""
    try:
        response = await batch_engine.create_batch_call(request, records)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creant batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-csv")
async def upload_csv_file(
    agent_id: str,
    batch_name: str,
    file: UploadFile = File(...),
    max_concurrent_calls: int = 5,
    retry_attempts: int = 2,
    description: Optional[str] = None
):
    """Pujar fitxer CSV per trucades massives"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Només es permeten fitxers CSV")
        
        # Llegir i parsejar CSV
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        records = []
        csv_reader = csv.DictReader(csv_content.splitlines())
        
        for row in csv_reader:
            # Netejar i validar dades
            record = {
                'phone_number': row.get('phone_number', '').strip(),
                'name': row.get('name', row.get('recipient_name', '')).strip(),
                'variables': {}
            }
            
            # Afegir variables personalitzades
            for key, value in row.items():
                if key not in ['phone_number', 'name', 'recipient_name']:
                    record['variables'][key] = value.strip()
            
            records.append(record)
        
        # Crear batch call
        batch_request = BatchCallRequest(
            agent_id=agent_id,
            batch_name=batch_name,
            description=description,
            max_concurrent_calls=max_concurrent_calls,
            retry_attempts=retry_attempts
        )
        
        response = await batch_engine.create_batch_call(batch_request, records)
        
        return {
            "success": True,
            "message": f"Fitxer CSV processat correctament",
            "batch_id": response.batch_id,
            "total_records": response.total_records,
            "valid_records": response.valid_records,
            "invalid_records": response.invalid_records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processant CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start/{batch_id}")
async def start_batch_call(batch_id: str, background_tasks: BackgroundTasks):
    """Iniciar una trucada massiva"""
    try:
        success = await batch_engine.start_batch_call(batch_id, background_tasks)
        
        if success:
            return {
                "success": True,
                "message": f"Batch call {batch_id} iniciat correctament"
            }
        else:
            raise HTTPException(status_code=400, detail="No s'ha pogut iniciar el batch call")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciant batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/progress/{batch_id}", response_model=BatchProgressResponse)
async def get_batch_progress(batch_id: str):
    """Obtenir progrés d'una trucada massiva"""
    try:
        progress = batch_engine.get_batch_progress(batch_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Batch call no trobat")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint progrés: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{batch_id}")
async def get_batch_call(batch_id: str):
    """Obtenir detalls d'una trucada massiva"""
    try:
        if batch_id not in batch_calls:
            raise HTTPException(status_code=404, detail="Batch call no trobat")
        
        batch_call = batch_calls[batch_id]
        call_records_list = [cr for cr in call_records.values() if cr.batch_id == batch_id]
        
        return {
            "success": True,
            "batch_call": batch_call.dict(),
            "call_records": [cr.dict() for cr in call_records_list]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obtenint batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batches")
async def list_batch_calls():
    """Llistar totes les trucades massives"""
    try:
        batches = []
        for batch_id, batch_call in batch_calls.items():
            progress = batch_engine.get_batch_progress(batch_id)
            batches.append({
                "batch_call": batch_call.dict(),
                "progress": progress.dict() if progress else None
            })
        
        return {
            "success": True,
            "batches": batches,
            "total": len(batches)
        }
        
    except Exception as e:
        logger.error(f"Error llistant batch calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{batch_id}")
async def cancel_batch_call(batch_id: str):
    """Cancel·lar una trucada massiva"""
    try:
        success = batch_engine.cancel_batch_call(batch_id)
        
        if success:
            return {
                "success": True,
                "message": f"Batch call {batch_id} cancel·lat correctament"
            }
        else:
            raise HTTPException(status_code=400, detail="No s'ha pogut cancel·lar el batch call")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancel·lant batch call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def batch_calling_health():
    """Health check del sistema de trucades massives"""
    return {
        "status": "ok",
        "message": "Sistema de trucades massives funcionant",
        "stats": {
            "total_batches": len(batch_calls),
            "active_batches": len(batch_engine.active_batches),
            "max_concurrent_batches": batch_engine.max_concurrent_batches
        }
    }

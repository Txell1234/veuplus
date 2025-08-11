# Storage Module for VeuPlus
"""
Storage abstraction layer for VeuPlus platform
Supports local filesystem and S3/MinIO storage
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Storage configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")  # local, s3
STORAGE_BASE_PATH = os.getenv("STORAGE_BASE_PATH", "voice_models")

# Dynamic base directory (local/Docker compatibility)
if Path("/app/backend").exists():
    BASE_DIR = Path("/app/backend")
else:
    BASE_DIR = Path(__file__).parent

VOICE_MODELS_DIR = BASE_DIR / STORAGE_BASE_PATH
VOICE_MODELS_DIR.mkdir(exist_ok=True, parents=True)

class StorageManager:
    """Manages file storage operations"""
    
    def __init__(self):
        self.storage_type = STORAGE_TYPE
        self.base_path = VOICE_MODELS_DIR
        
    def store_file(self, source_path: Union[str, Path], target_key: str) -> str:
        """Store a file and return the storage path"""
        try:
            source_path = Path(source_path)
            target_path = self.base_path / target_key
            
            # Ensure target directory exists
            target_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            logger.info(f"File stored: {source_path} -> {target_path}")
            return str(target_path)
            
        except Exception as e:
            logger.error(f"Failed to store file {source_path}: {e}")
            raise
    
    def get_file_path(self, file_key: str) -> Optional[str]:
        """Get the full path to a stored file"""
        file_path = self.base_path / file_key
        if file_path.exists():
            return str(file_path)
        return None
    
    def delete_file(self, file_key: str) -> bool:
        """Delete a stored file"""
        try:
            file_path = self.base_path / file_key
            if file_path.exists():
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """List files with optional prefix filter"""
        try:
            search_path = self.base_path / prefix if prefix else self.base_path
            if search_path.exists():
                return [str(p.relative_to(self.base_path)) for p in search_path.rglob("*") if p.is_file()]
            return []
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

# Global storage manager instance
storage = StorageManager()

# Helper functions for backward compatibility
def store_model_artifact(model_id: str, artifact_path: Union[str, Path], artifact_type: str = "model") -> str:
    """Store a model artifact (model file, checkpoint, etc.)"""
    try:
        artifact_path = Path(artifact_path)
        file_extension = artifact_path.suffix
        target_key = f"{model_id}/{artifact_type}{file_extension}"
        
        return storage.store_file(artifact_path, target_key)
    except Exception as e:
        logger.error(f"Failed to store model artifact {artifact_path}: {e}")
        raise

def store_audio_sample(model_id: str, audio_path: Union[str, Path], sample_name: str = "sample") -> str:
    """Store an audio sample for a voice model"""
    try:
        audio_path = Path(audio_path)
        file_extension = audio_path.suffix
        target_key = f"{model_id}/{sample_name}{file_extension}"
        
        return storage.store_file(audio_path, target_key)
    except Exception as e:
        logger.error(f"Failed to store audio sample {audio_path}: {e}")
        raise

def get_model_path(model_id: str) -> Optional[str]:
    """Get the path to a voice model directory"""
    model_dir = VOICE_MODELS_DIR / model_id
    if model_dir.exists():
        return str(model_dir)
    return None

def get_model_files(model_id: str) -> Dict[str, Any]:
    """Get information about all files for a voice model"""
    try:
        model_dir = VOICE_MODELS_DIR / model_id
        if not model_dir.exists():
            return {}
        
        files = {}
        for file_path in model_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(model_dir)
                files[str(relative_path)] = {
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
        
        return files
    except Exception as e:
        logger.error(f"Failed to get model files for {model_id}: {e}")
        return {}

def delete_model(model_id: str) -> bool:
    """Delete all files for a voice model"""
    try:
        return storage.delete_file(model_id)
    except Exception as e:
        logger.error(f"Failed to delete model {model_id}: {e}")
        return False

def create_model_directory(model_id: str) -> str:
    """Create a directory for a new voice model"""
    model_dir = VOICE_MODELS_DIR / model_id
    model_dir.mkdir(exist_ok=True, parents=True)
    return str(model_dir)

# Voice management functions for API endpoints
def import_voice_file(voice_id: str, file_path: Union[str, Path], file_type: str = "audio") -> str:
    """Import a voice file for training or synthesis"""
    return store_audio_sample(voice_id, file_path, f"imported_{file_type}")

def export_voice_model(voice_id: str) -> Optional[str]:
    """Get the path to export a voice model"""
    return get_model_path(voice_id)

def list_voice_models() -> list:
    """List all available voice models"""
    try:
        models = []
        for model_dir in VOICE_MODELS_DIR.iterdir():
            if model_dir.is_dir():
                models.append({
                    "id": model_dir.name,
                    "path": str(model_dir),
                    "files": get_model_files(model_dir.name)
                })
        return models
    except Exception as e:
        logger.error(f"Failed to list voice models: {e}")
        return []

# Initialize storage on import
logger.info(f"Storage initialized: {STORAGE_TYPE} storage at {VOICE_MODELS_DIR}")
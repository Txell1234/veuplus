"""
Sistema de Gestión de Voces para VeusPlus
Gestiona todas las voces disponibles en el sistema
"""

import asyncio
import logging
import os
import tempfile
import uuid
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import base64
from datetime import datetime
import threading
import time

logger = logging.getLogger("veuplus.voice_management")

class VoiceManagementSystem:
    """Sistema de gestión de voces"""
    
    def __init__(self):
        self.is_initialized = False
        self.voice_categories = {
            "edge_tts": "Voces Edge-TTS",
            "cloned": "Voces Clonadas",
            "trained": "Voces Entrenadas",
            "mixed": "Voces Mezcladas",
            "custom": "Voces Personalizadas"
        }
        
        self.voice_metadata = {}
        self.voice_statistics = {
            "total_voices": 0,
            "by_category": {},
            "by_language": {},
            "by_quality": {},
            "last_updated": None
        }
        
    async def initialize(self) -> bool:
        """Inicializar el sistema de gestión de voces"""
        try:
            logger.info("🚀 Inicializando sistema de gestión de voces...")
            
            # Crear directorios necesarios
            self.management_dir = Path("backend/voice_management")
            self.management_dir.mkdir(exist_ok=True)
            
            # Cargar metadatos existentes
            await self._load_voice_metadata()
            
            # Actualizar estadísticas
            await self._update_voice_statistics()
            
            self.is_initialized = True
            logger.info("✅ Sistema de gestión de voces inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema de gestión: {e}")
            return False
    
    async def _load_voice_metadata(self):
        """Cargar metadatos de voces existentes"""
        try:
            metadata_file = self.management_dir / "voice_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.voice_metadata = json.load(f)
                    logger.info(f"✅ Cargados metadatos de {len(self.voice_metadata)} voces")
        except Exception as e:
            logger.warning(f"Error cargando metadatos de voces: {e}")
    
    def _save_voice_metadata(self):
        """Guardar metadatos de voces"""
        try:
            metadata_file = self.management_dir / "voice_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando metadatos de voces: {e}")
    
    async def _update_voice_statistics(self):
        """Actualizar estadísticas de voces"""
        try:
            # Recopilar voces de todos los sistemas
            all_voices = await self._collect_all_voices()
            
            # Actualizar estadísticas
            self.voice_statistics = {
                "total_voices": len(all_voices),
                "by_category": {},
                "by_language": {},
                "by_quality": {},
                "last_updated": datetime.now().isoformat()
            }
            
            # Contar por categoría
            for voice in all_voices:
                category = voice.get('type', 'unknown')
                self.voice_statistics["by_category"][category] = \
                    self.voice_statistics["by_category"].get(category, 0) + 1
                
                # Contar por idioma
                language = voice.get('language', 'unknown')
                self.voice_statistics["by_language"][language] = \
                    self.voice_statistics["by_language"].get(language, 0) + 1
                
                # Contar por calidad
                quality = voice.get('quality', 'unknown')
                self.voice_statistics["by_quality"][quality] = \
                    self.voice_statistics["by_quality"].get(quality, 0) + 1
            
            logger.info(f"✅ Estadísticas actualizadas: {len(all_voices)} voces")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    async def _collect_all_voices(self) -> List[Dict[str, Any]]:
        """Recopilar todas las voces de todos los sistemas"""
        try:
            all_voices = []
            
            # Voces Edge-TTS
            try:
                from .edge_tts_engine import edge_tts_engine
                if edge_tts_engine.is_initialized:
                    edge_voices = edge_tts_engine.get_available_voices()
                    for voice in edge_voices.get('voices', []):
                        voice['system'] = 'edge_tts'
                        voice['category'] = 'edge_tts'
                        all_voices.append(voice)
            except:
                pass
            
            # Voces clonadas
            try:
                from .voice_cloning_system import voice_cloning_system
                if voice_cloning_system.is_initialized:
                    cloned_voices = voice_cloning_system.get_cloned_voices()
                    for voice in cloned_voices.get('voices', []):
                        voice['system'] = 'cloning'
                        voice['category'] = 'cloned'
                        all_voices.append(voice)
            except:
                pass
            
            # Voces entrenadas
            try:
                from .voice_training_models import voice_training_system
                if voice_training_system.is_initialized:
                    trained_voices = voice_training_system.get_trained_models()
                    for voice in trained_voices.get('models', []):
                        voice['system'] = 'training'
                        voice['category'] = 'trained'
                        all_voices.append(voice)
            except:
                pass
            
            # Voces mezcladas
            try:
                from .voice_mixing_system import voice_mixing_system
                if voice_mixing_system.is_initialized:
                    mixed_voices = voice_mixing_system.get_mixed_voices()
                    for voice in mixed_voices.get('voices', []):
                        voice['system'] = 'mixing'
                        voice['category'] = 'mixed'
                        all_voices.append(voice)
            except:
                pass
            
            # Voces personalizadas
            try:
                from .advanced_neural_tts import advanced_neural_tts
                if advanced_neural_tts.is_initialized:
                    custom_voices = advanced_neural_tts.get_available_voices()
                    for voice in custom_voices.get('voices', []):
                        voice['system'] = 'neural'
                        voice['category'] = 'custom'
                        all_voices.append(voice)
            except:
                pass
            
            return all_voices
            
        except Exception as e:
            logger.error(f"Error recopilando voces: {e}")
            return []
    
    async def get_all_voices(
        self, 
        category: Optional[str] = None,
        language: Optional[str] = None,
        quality: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener todas las voces con filtros"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Recopilar todas las voces
            all_voices = await self._collect_all_voices()
            
            # Aplicar filtros
            filtered_voices = all_voices
            
            if category:
                filtered_voices = [v for v in filtered_voices if v.get('category') == category]
            
            if language:
                filtered_voices = [v for v in filtered_voices if v.get('language') == language]
            
            if quality:
                filtered_voices = [v for v in filtered_voices if v.get('quality') == quality]
            
            if search_query:
                search_lower = search_query.lower()
                filtered_voices = [
                    v for v in filtered_voices 
                    if search_lower in v.get('name', '').lower() or 
                       search_lower in v.get('description', '').lower()
                ]
            
            # Ordenar por relevancia
            filtered_voices.sort(key=lambda x: (
                x.get('quality', 'standard') == 'ultra_high',
                x.get('quality', 'standard') == 'high',
                x.get('name', '')
            ), reverse=True)
            
            return {
                'voices': filtered_voices,
                'total': len(filtered_voices),
                'filters': {
                    'category': category,
                    'language': language,
                    'quality': quality,
                    'search_query': search_query
                },
                'statistics': self.voice_statistics,
                'categories': self.voice_categories
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo voces: {e}")
            return {
                'voices': [],
                'total': 0,
                'error': str(e)
            }
    
    async def get_voice_details(self, voice_id: str) -> Dict[str, Any]:
        """Obtener detalles de una voz específica"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Buscar en todos los sistemas
            all_voices = await self._collect_all_voices()
            voice = next((v for v in all_voices if v.get('id') == voice_id), None)
            
            if not voice:
                raise Exception(f"Voz no encontrada: {voice_id}")
            
            # Añadir metadatos adicionales
            voice_details = voice.copy()
            voice_details['metadata'] = self.voice_metadata.get(voice_id, {})
            voice_details['usage_count'] = voice_details['metadata'].get('usage_count', 0)
            voice_details['last_used'] = voice_details['metadata'].get('last_used')
            voice_details['rating'] = voice_details['metadata'].get('rating', 0)
            voice_details['tags'] = voice_details['metadata'].get('tags', [])
            
            return voice_details
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de voz: {e}")
            return {
                'error': str(e),
                'voice_id': voice_id
            }
    
    async def update_voice_metadata(
        self, 
        voice_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Actualizar metadatos de una voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Actualizar metadatos
            if voice_id not in self.voice_metadata:
                self.voice_metadata[voice_id] = {}
            
            self.voice_metadata[voice_id].update(metadata)
            self.voice_metadata[voice_id]['last_updated'] = datetime.now().isoformat()
            
            # Guardar metadatos
            self._save_voice_metadata()
            
            logger.info(f"✅ Metadatos actualizados para voz: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando metadatos: {e}")
            return False
    
    async def record_voice_usage(self, voice_id: str) -> bool:
        """Registrar uso de una voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Actualizar contador de uso
            if voice_id not in self.voice_metadata:
                self.voice_metadata[voice_id] = {}
            
            self.voice_metadata[voice_id]['usage_count'] = \
                self.voice_metadata[voice_id].get('usage_count', 0) + 1
            self.voice_metadata[voice_id]['last_used'] = datetime.now().isoformat()
            
            # Guardar metadatos
            self._save_voice_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error registrando uso de voz: {e}")
            return False
    
    async def rate_voice(self, voice_id: str, rating: int) -> bool:
        """Calificar una voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            if rating < 1 or rating > 5:
                raise Exception("La calificación debe estar entre 1 y 5")
            
            # Actualizar calificación
            if voice_id not in self.voice_metadata:
                self.voice_metadata[voice_id] = {}
            
            self.voice_metadata[voice_id]['rating'] = rating
            self.voice_metadata[voice_id]['rated_at'] = datetime.now().isoformat()
            
            # Guardar metadatos
            self._save_voice_metadata()
            
            logger.info(f"✅ Voz calificada: {voice_id} - {rating} estrellas")
            return True
            
        except Exception as e:
            logger.error(f"Error calificando voz: {e}")
            return False
    
    async def add_voice_tag(self, voice_id: str, tag: str) -> bool:
        """Añadir etiqueta a una voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Añadir etiqueta
            if voice_id not in self.voice_metadata:
                self.voice_metadata[voice_id] = {}
            
            if 'tags' not in self.voice_metadata[voice_id]:
                self.voice_metadata[voice_id]['tags'] = []
            
            if tag not in self.voice_metadata[voice_id]['tags']:
                self.voice_metadata[voice_id]['tags'].append(tag)
            
            # Guardar metadatos
            self._save_voice_metadata()
            
            logger.info(f"✅ Etiqueta añadida a voz: {voice_id} - {tag}")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo etiqueta: {e}")
            return False
    
    async def remove_voice_tag(self, voice_id: str, tag: str) -> bool:
        """Eliminar etiqueta de una voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Eliminar etiqueta
            if voice_id in self.voice_metadata and 'tags' in self.voice_metadata[voice_id]:
                if tag in self.voice_metadata[voice_id]['tags']:
                    self.voice_metadata[voice_id]['tags'].remove(tag)
                    
                    # Guardar metadatos
                    self._save_voice_metadata()
                    
                    logger.info(f"✅ Etiqueta eliminada de voz: {voice_id} - {tag}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando etiqueta: {e}")
            return False
    
    async def get_voice_recommendations(
        self, 
        user_preferences: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtener recomendaciones de voces basadas en preferencias"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Recopilar todas las voces
            all_voices = await self._collect_all_voices()
            
            # Calcular puntuación de recomendación
            recommendations = []
            
            for voice in all_voices:
                score = 0
                
                # Puntuación basada en calidad
                quality = voice.get('quality', 'standard')
                if quality == 'ultra_high':
                    score += 10
                elif quality == 'high':
                    score += 8
                elif quality == 'neural':
                    score += 9
                else:
                    score += 5
                
                # Puntuación basada en uso
                usage_count = self.voice_metadata.get(voice.get('id'), {}).get('usage_count', 0)
                score += min(usage_count * 0.1, 5)
                
                # Puntuación basada en calificación
                rating = self.voice_metadata.get(voice.get('id'), {}).get('rating', 0)
                score += rating * 2
                
                # Puntuación basada en preferencias del usuario
                if user_preferences.get('language') == voice.get('language'):
                    score += 3
                
                if user_preferences.get('quality') == voice.get('quality'):
                    score += 2
                
                if user_preferences.get('category') == voice.get('category'):
                    score += 2
                
                # Añadir a recomendaciones
                voice_with_score = voice.copy()
                voice_with_score['recommendation_score'] = score
                recommendations.append(voice_with_score)
            
            # Ordenar por puntuación y devolver top N
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}")
            return []
    
    async def get_voice_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de voces"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Actualizar estadísticas
            await self._update_voice_statistics()
            
            return self.voice_statistics
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    async def export_voice_data(self, format: str = 'json') -> str:
        """Exportar datos de voces"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            # Recopilar todas las voces
            all_voices = await self._collect_all_voices()
            
            export_data = {
                'voices': all_voices,
                'metadata': self.voice_metadata,
                'statistics': self.voice_statistics,
                'exported_at': datetime.now().isoformat(),
                'format': format
            }
            
            if format == 'json':
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            else:
                raise Exception(f"Formato no soportado: {format}")
            
        except Exception as e:
            logger.error(f"Error exportando datos: {e}")
            return ""
    
    async def import_voice_data(self, data: str, format: str = 'json') -> bool:
        """Importar datos de voces"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de gestión no está inicializado")
            
            if format == 'json':
                import_data = json.loads(data)
                
                # Importar metadatos
                if 'metadata' in import_data:
                    self.voice_metadata.update(import_data['metadata'])
                    self._save_voice_metadata()
                
                logger.info("✅ Datos de voces importados correctamente")
                return True
            else:
                raise Exception(f"Formato no soportado: {format}")
            
        except Exception as e:
            logger.error(f"Error importando datos: {e}")
            return False

# Instancia global del sistema de gestión
voice_management_system = VoiceManagementSystem()

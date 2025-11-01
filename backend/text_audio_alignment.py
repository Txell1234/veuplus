"""
Text-Audio Alignment System for VeuPlus
Creates high-quality voice models using text-audio pairs
"""

import os
import logging
import json
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import uuid
import re

logger = logging.getLogger("veuplus.text_audio_alignment")

class TextAudioAligner:
    """Advanced text-audio alignment for voice training"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.voice_models_dir = self.base_dir / "voice_models"
        self.training_data_dir = self.base_dir / "training_data"
        self.voice_models_dir.mkdir(exist_ok=True, parents=True)
        self.training_data_dir.mkdir(exist_ok=True, parents=True)
        
        # Reference recording with known text
        self.reference_audio_path = self.voice_models_dir / "catalan_reference_with_text.mp3"
        self.reference_text = """Ciutadanes i ciutadans de Catalunya,  
Vull desitjar-vos que estigueu passant i passeu unes molt bones festes de Nadal i que tingueu 
una molt bona entrada d'any 2024."""
        
        # Phoneme mapping for Catalan
        self.catalan_phonemes = {
            'a': ['a', 'à'], 'e': ['e', 'è', 'é'], 'i': ['i', 'í'], 'o': ['o', 'ò', 'ó'], 'u': ['u', 'ú', 'ü'],
            'b': ['b'], 'c': ['c', 'ç'], 'd': ['d'], 'f': ['f'], 'g': ['g'], 'h': ['h'],
            'j': ['j'], 'k': ['k'], 'l': ['l', 'll'], 'm': ['m'], 'n': ['n', 'ny'], 'p': ['p'],
            'q': ['qu'], 'r': ['r', 'rr'], 's': ['s'], 't': ['t'], 'v': ['v'], 'w': ['w'],
            'x': ['x'], 'y': ['y'], 'z': ['z']
        }
    
    async def create_aligned_training_data(self) -> Dict[str, Any]:
        """Create training data with text-audio alignment"""
        print("🎤 CREANDO DATOS DE ENTRENAMIENTO CON ALINEACIÓN TEXTO-AUDIO")
        print("=" * 70)
        
        if not self.reference_audio_path.exists():
            raise FileNotFoundError(f"Grabación de referencia no encontrada: {self.reference_audio_path}")
        
        print(f"✅ Grabación encontrada: {self.reference_audio_path.name}")
        print(f"📝 Texto de referencia:")
        print(f"   {self.reference_text}")
        
        try:
            # Cargar y analizar audio
            audio_data, sample_rate = librosa.load(str(self.reference_audio_path), sr=22050)
            print(f"\n🔊 Audio cargado:")
            print(f"   Duración: {len(audio_data)/sample_rate:.2f}s")
            print(f"   Sample rate: {sample_rate}Hz")
            print(f"   Muestras: {len(audio_data)}")
            
            # Preprocesar texto
            processed_text = self.preprocess_text(self.reference_text)
            print(f"\n📝 Texto procesado:")
            print(f"   Palabras: {len(processed_text['words'])}")
            print(f"   Sílabas estimadas: {processed_text['estimated_syllables']}")
            print(f"   Fonemas estimados: {processed_text['estimated_phonemes']}")
            
            # Crear alineación temporal
            alignment = await self.create_temporal_alignment(audio_data, sample_rate, processed_text)
            print(f"\n⏱️ Alineación temporal creada:")
            print(f"   Segmentos: {len(alignment['segments'])}")
            print(f"   Precisión estimada: {alignment['alignment_confidence']:.2f}")
            
            # Extraer características detalladas por segmento
            segment_features = await self.extract_segment_features(audio_data, sample_rate, alignment)
            print(f"\n🎯 Características por segmento extraídas:")
            print(f"   Segmentos analizados: {len(segment_features)}")
            
            # Crear modelo de entrenamiento
            training_model = self.create_training_model(processed_text, alignment, segment_features)
            
            # Guardar datos de entrenamiento
            training_id = str(uuid.uuid4())
            training_path = self.training_data_dir / f"aligned_training_{training_id}.json"
            
            with open(training_path, 'w', encoding='utf-8') as f:
                json.dump(training_model, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Datos de entrenamiento guardados: {training_path.name}")
            
            return training_model
            
        except Exception as e:
            logger.error(f"Text-audio alignment failed: {e}")
            raise
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """Preprocess text for alignment"""
        
        # Limpiar texto
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        
        # Separar en palabras
        words = cleaned_text.lower().split()
        
        # Estimar sílabas
        total_syllables = sum(self.count_syllables_catalan(word) for word in words)
        
        # Estimar fonemas
        total_phonemes = sum(len(self.word_to_phonemes(word)) for word in words)
        
        # Crear estructura de frases
        sentences = [s.strip() for s in re.split(r'[.!?]+', cleaned_text) if s.strip()]
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "words": words,
            "sentences": sentences,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "estimated_syllables": total_syllables,
            "estimated_phonemes": total_phonemes
        }
    
    def count_syllables_catalan(self, word: str) -> int:
        """Count syllables in Catalan word"""
        vowels = "aeiouàèéíòóúü"
        syllables = 0
        prev_was_vowel = False
        
        for char in word.lower():
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        # Special cases for Catalan
        if word.endswith('ia') or word.endswith('ie') or word.endswith('io'):
            syllables += 1
        
        return max(syllables, 1)
    
    def word_to_phonemes(self, word: str) -> List[str]:
        """Convert word to estimated phonemes (simplified)"""
        phonemes = []
        
        i = 0
        while i < len(word):
            char = word[i].lower()
            
            # Handle digraphs
            if i < len(word) - 1:
                digraph = word[i:i+2].lower()
                if digraph in ['ll', 'ny', 'qu', 'ch', 'th']:
                    phonemes.append(digraph)
                    i += 2
                    continue
            
            # Single characters
            if char in 'aeiouàèéíòóúü':
                phonemes.append(char)
            elif char.isalpha():
                phonemes.append(char)
            
            i += 1
        
        return phonemes
    
    async def create_temporal_alignment(self, audio_data: np.ndarray, sample_rate: int, processed_text: Dict[str, Any]) -> Dict[str, Any]:
        """Create temporal alignment between text and audio"""
        
        try:
            # Detectar segmentos de voz
            voice_segments = self.detect_voice_segments(audio_data, sample_rate)
            print(f"   Segmentos de voz detectados: {len(voice_segments)}")
            
            # Alinear palabras con segmentos
            words = processed_text["words"]
            word_alignments = self.align_words_to_segments(words, voice_segments, len(audio_data)/sample_rate)
            
            # Calcular confianza de alineación
            alignment_confidence = self.calculate_alignment_confidence(word_alignments, voice_segments)
            
            alignment = {
                "voice_segments": voice_segments,
                "word_alignments": word_alignments,
                "segments": self.create_aligned_segments(word_alignments, voice_segments),
                "alignment_confidence": alignment_confidence,
                "total_duration": len(audio_data) / sample_rate
            }
            
            return alignment
            
        except Exception as e:
            logger.error(f"Temporal alignment failed: {e}")
            raise
    
    def detect_voice_segments(self, audio_data: np.ndarray, sample_rate: int) -> List[Dict[str, float]]:
        """Detect voice activity segments"""
        try:
            # Usar librosa para detectar onset y offset
            frame_length = 2048
            hop_length = 512
            
            # Calcular energía RMS
            rms = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Detectar actividad de voz
            threshold = np.percentile(rms, 30)  # Umbral adaptativo
            voice_activity = rms > threshold
            
            # Encontrar segmentos continuos
            segments = []
            in_segment = False
            segment_start = 0
            
            for i, is_voice in enumerate(voice_activity):
                time = i * hop_length / sample_rate
                
                if is_voice and not in_segment:
                    # Inicio de segmento
                    segment_start = time
                    in_segment = True
                elif not is_voice and in_segment:
                    # Final de segmento
                    if time - segment_start > 0.1:  # Mínimo 100ms
                        segments.append({
                            "start": segment_start,
                            "end": time,
                            "duration": time - segment_start
                        })
                    in_segment = False
            
            # Cerrar último segmento si está abierto
            if in_segment:
                segments.append({
                    "start": segment_start,
                    "end": len(audio_data) / sample_rate,
                    "duration": (len(audio_data) / sample_rate) - segment_start
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"Voice segment detection failed: {e}")
            return [{"start": 0, "end": len(audio_data) / sample_rate, "duration": len(audio_data) / sample_rate}]
    
    def align_words_to_segments(self, words: List[str], voice_segments: List[Dict[str, float]], total_duration: float) -> List[Dict[str, Any]]:
        """Align words to voice segments"""
        
        if not voice_segments:
            return []
        
        # Calcular duración estimada por palabra
        total_voice_duration = sum(seg["duration"] for seg in voice_segments)
        avg_word_duration = total_voice_duration / len(words) if words else 0.5
        
        word_alignments = []
        current_time = 0
        segment_idx = 0
        
        for i, word in enumerate(words):
            # Estimar duración de la palabra
            syllables = self.count_syllables_catalan(word)
            word_duration = max(syllables * 0.15, 0.1)  # Mínimo 100ms por palabra
            
            # Encontrar segmento apropiado
            while segment_idx < len(voice_segments) and current_time >= voice_segments[segment_idx]["end"]:
                segment_idx += 1
            
            if segment_idx < len(voice_segments):
                segment = voice_segments[segment_idx]
                
                # Asegurar que la palabra está dentro del segmento
                word_start = max(current_time, segment["start"])
                word_end = min(word_start + word_duration, segment["end"])
                
                word_alignments.append({
                    "word": word,
                    "start": word_start,
                    "end": word_end,
                    "duration": word_end - word_start,
                    "syllables": syllables,
                    "segment_idx": segment_idx,
                    "phonemes": self.word_to_phonemes(word)
                })
                
                current_time = word_end + 0.05  # Pequeña pausa entre palabras
            
        return word_alignments
    
    def create_aligned_segments(self, word_alignments: List[Dict[str, Any]], voice_segments: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Create aligned segments for training"""
        
        segments = []
        
        for segment in voice_segments:
            # Encontrar palabras en este segmento
            words_in_segment = [
                wa for wa in word_alignments 
                if wa["start"] >= segment["start"] and wa["end"] <= segment["end"]
            ]
            
            if words_in_segment:
                segment_text = " ".join(wa["word"] for wa in words_in_segment)
                total_syllables = sum(wa["syllables"] for wa in words_in_segment)
                total_phonemes = sum(len(wa["phonemes"]) for wa in words_in_segment)
                
                segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "duration": segment["duration"],
                    "text": segment_text,
                    "words": words_in_segment,
                    "syllable_count": total_syllables,
                    "phoneme_count": total_phonemes,
                    "speech_rate": total_syllables / segment["duration"] if segment["duration"] > 0 else 0
                })
        
        return segments
    
    def calculate_alignment_confidence(self, word_alignments: List[Dict[str, Any]], voice_segments: List[Dict[str, float]]) -> float:
        """Calculate confidence of the alignment"""
        
        if not word_alignments or not voice_segments:
            return 0.0
        
        # Factores de confianza
        factors = []
        
        # 1. Cobertura de palabras
        aligned_words = len(word_alignments)
        coverage = aligned_words / max(aligned_words, 1)
        factors.append(coverage)
        
        # 2. Distribución temporal
        total_word_duration = sum(wa["duration"] for wa in word_alignments)
        total_voice_duration = sum(seg["duration"] for seg in voice_segments)
        temporal_coverage = min(total_word_duration / total_voice_duration, 1.0) if total_voice_duration > 0 else 0
        factors.append(temporal_coverage)
        
        # 3. Consistencia de velocidad de habla
        speech_rates = [wa["syllables"] / wa["duration"] for wa in word_alignments if wa["duration"] > 0]
        if speech_rates:
            rate_consistency = 1.0 / (1.0 + np.std(speech_rates) / np.mean(speech_rates))
            factors.append(rate_consistency)
        
        return float(np.mean(factors))
    
    async def extract_segment_features(self, audio_data: np.ndarray, sample_rate: int, alignment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract detailed features for each aligned segment"""
        
        segment_features = []
        
        for segment in alignment["segments"]:
            try:
                # Extraer audio del segmento
                start_sample = int(segment["start"] * sample_rate)
                end_sample = int(segment["end"] * sample_rate)
                segment_audio = audio_data[start_sample:end_sample]
                
                if len(segment_audio) < 1024:  # Segmento muy corto
                    continue
                
                # Extraer características del segmento
                features = await self.extract_detailed_segment_features(segment_audio, sample_rate, segment)
                
                features.update({
                    "segment_text": segment["text"],
                    "start_time": segment["start"],
                    "end_time": segment["end"],
                    "duration": segment["duration"],
                    "syllable_count": segment["syllable_count"],
                    "phoneme_count": segment["phoneme_count"],
                    "speech_rate": segment["speech_rate"]
                })
                
                segment_features.append(features)
                
            except Exception as e:
                logger.warning(f"Failed to extract features for segment: {e}")
                continue
        
        return segment_features
    
    async def extract_detailed_segment_features(self, segment_audio: np.ndarray, sample_rate: int, segment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed features from audio segment"""
        
        features = {}
        
        try:
            # Características básicas
            features.update({
                "rms_energy": float(np.sqrt(np.mean(segment_audio**2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(segment_audio)[0])),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=segment_audio, sr=sample_rate)[0])),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=segment_audio, sr=sample_rate)[0])),
            })
            
            # Análisis de pitch detallado
            f0, voiced_flag, voiced_probs = librosa.pyin(segment_audio, fmin=80, fmax=400)
            f0_clean = f0[~np.isnan(f0)]
            
            if len(f0_clean) > 0:
                features.update({
                    "f0_mean": float(np.mean(f0_clean)),
                    "f0_std": float(np.std(f0_clean)),
                    "f0_min": float(np.min(f0_clean)),
                    "f0_max": float(np.max(f0_clean)),
                    "f0_range": float(np.max(f0_clean) - np.min(f0_clean)),
                    "voiced_ratio": float(np.mean(voiced_probs)),
                    "f0_contour": [float(x) for x in f0_clean[::max(1, len(f0_clean)//20)]]  # Muestreo del contorno
                })
                
                # Análisis prosódico específico del segmento
                if len(f0_clean) > 5:
                    f0_slope = np.polyfit(range(len(f0_clean)), f0_clean, 1)[0]
                    features["f0_slope"] = float(f0_slope)
                    
                    # Detectar patrones de entonación
                    if f0_slope > 5:
                        features["intonation_pattern"] = "rising"
                    elif f0_slope < -5:
                        features["intonation_pattern"] = "falling"
                    else:
                        features["intonation_pattern"] = "flat"
            
            # MFCC para características tímbricas
            mfccs = librosa.feature.mfcc(y=segment_audio, sr=sample_rate, n_mfcc=13)
            features.update({
                "mfcc_mean": [float(x) for x in np.mean(mfccs, axis=1)],
                "mfcc_std": [float(x) for x in np.std(mfccs, axis=1)]
            })
            
            # Características específicas por fonema/sílaba
            features.update({
                "energy_per_syllable": features["rms_energy"] / segment_info["syllable_count"] if segment_info["syllable_count"] > 0 else 0,
                "duration_per_syllable": segment_info["duration"] / segment_info["syllable_count"] if segment_info["syllable_count"] > 0 else 0,
                "f0_per_syllable": features.get("f0_mean", 0) / segment_info["syllable_count"] if segment_info["syllable_count"] > 0 else 0
            })
            
            return features
            
        except Exception as e:
            logger.warning(f"Detailed segment feature extraction failed: {e}")
            return {"extraction_error": str(e)}
    
    def create_training_model(self, processed_text: Dict[str, Any], alignment: Dict[str, Any], segment_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive training model"""
        
        training_model = {
            "model_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "model_type": "text_audio_aligned",
            "language": "ca",
            "quality": "hyperrealistic_aligned",
            
            # Datos de texto
            "text_data": processed_text,
            
            # Datos de alineación
            "alignment_data": alignment,
            
            # Características por segmento
            "segment_features": segment_features,
            
            # Estadísticas globales
            "global_stats": self.calculate_global_stats(segment_features),
            
            # Metadatos de entrenamiento
            "training_metadata": {
                "reference_audio": str(self.reference_audio_path),
                "alignment_confidence": alignment["alignment_confidence"],
                "segment_count": len(segment_features),
                "total_words": len(processed_text["words"]),
                "total_syllables": processed_text["estimated_syllables"],
                "avg_speech_rate": np.mean([seg.get("speech_rate", 0) for seg in alignment["segments"]]) if alignment["segments"] else 0
            }
        }
        
        return training_model
    
    def calculate_global_stats(self, segment_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate global statistics from all segments"""
        
        if not segment_features:
            return {}
        
        # Recopilar valores
        f0_values = [f.get("f0_mean") for f in segment_features if f.get("f0_mean")]
        energy_values = [f.get("rms_energy") for f in segment_features if f.get("rms_energy")]
        speech_rates = [f.get("speech_rate", 0) for f in segment_features]
        
        stats = {}
        
        if f0_values:
            stats.update({
                "global_f0_mean": float(np.mean(f0_values)),
                "global_f0_std": float(np.std(f0_values)),
                "global_f0_range": float(np.max(f0_values) - np.min(f0_values))
            })
        
        if energy_values:
            stats.update({
                "global_energy_mean": float(np.mean(energy_values)),
                "global_energy_std": float(np.std(energy_values)),
                "global_energy_range": float(np.max(energy_values) - np.min(energy_values))
            })
        
        if speech_rates:
            stats.update({
                "global_speech_rate_mean": float(np.mean(speech_rates)),
                "global_speech_rate_std": float(np.std(speech_rates))
            })
        
        # MFCC globales
        all_mfcc_means = [f.get("mfcc_mean") for f in segment_features if f.get("mfcc_mean")]
        if all_mfcc_means and all(len(mfcc) == len(all_mfcc_means[0]) for mfcc in all_mfcc_means):
            stats["global_mfcc_mean"] = [float(x) for x in np.mean(all_mfcc_means, axis=0)]
            stats["global_mfcc_std"] = [float(x) for x in np.std(all_mfcc_means, axis=0)]
        
        return stats
    
    async def create_enhanced_voice_from_alignment(self, training_model: Dict[str, Any], voice_name: str) -> Dict[str, Any]:
        """Create enhanced voice model from aligned training data"""
        
        voice_id = str(uuid.uuid4())
        
        enhanced_voice = {
            "id": voice_id,
            "name": voice_name,
            "language": "ca",
            "model_type": "enhanced_aligned_voice",
            "quality": "hyperrealistic_text_aligned",
            "created_at": datetime.now().isoformat(),
            
            # Datos de entrenamiento
            "training_model_id": training_model["model_id"],
            "alignment_confidence": training_model["training_metadata"]["alignment_confidence"],
            "segment_count": training_model["training_metadata"]["segment_count"],
            
            # Características de voz
            "voice_characteristics": training_model["global_stats"],
            
            # Configuración de síntesis
            "synthesis_config": {
                "use_aligned_features": True,
                "segment_features": training_model["segment_features"],
                "prosodic_model": self.create_prosodic_model(training_model),
                "phoneme_timing": self.create_phoneme_timing_model(training_model)
            }
        }
        
        # Guardar modelo
        model_path = self.voice_models_dir / f"{voice_id}_aligned.json"
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_voice, f, indent=2, ensure_ascii=False)
        
        return enhanced_voice
    
    def create_prosodic_model(self, training_model: Dict[str, Any]) -> Dict[str, Any]:
        """Create prosodic model from training data"""
        
        segments = training_model.get("segment_features", [])
        
        # Analizar patrones prosódicos
        intonation_patterns = {}
        speech_rates = []
        energy_patterns = []
        
        for segment in segments:
            pattern = segment.get("intonation_pattern", "flat")
            if pattern not in intonation_patterns:
                intonation_patterns[pattern] = 0
            intonation_patterns[pattern] += 1
            
            if segment.get("speech_rate"):
                speech_rates.append(segment["speech_rate"])
            
            if segment.get("rms_energy"):
                energy_patterns.append(segment["rms_energy"])
        
        prosodic_model = {
            "intonation_patterns": intonation_patterns,
            "avg_speech_rate": float(np.mean(speech_rates)) if speech_rates else 3.0,
            "speech_rate_variance": float(np.std(speech_rates)) if speech_rates else 0.5,
            "avg_energy": float(np.mean(energy_patterns)) if energy_patterns else 0.1,
            "energy_variance": float(np.std(energy_patterns)) if energy_patterns else 0.02
        }
        
        return prosodic_model
    
    def create_phoneme_timing_model(self, training_model: Dict[str, Any]) -> Dict[str, Any]:
        """Create phoneme timing model"""
        
        segments = training_model.get("segment_features", [])
        
        # Calcular duraciones promedio por fonema
        phoneme_durations = {}
        
        for segment in segments:
            if segment.get("phoneme_count", 0) > 0 and segment.get("duration", 0) > 0:
                avg_phoneme_duration = segment["duration"] / segment["phoneme_count"]
                
                # Asignar a fonemas del segmento (simplificado)
                segment_text = segment.get("segment_text", "")
                for word in segment_text.split():
                    phonemes = self.word_to_phonemes(word)
                    for phoneme in phonemes:
                        if phoneme not in phoneme_durations:
                            phoneme_durations[phoneme] = []
                        phoneme_durations[phoneme].append(avg_phoneme_duration)
        
        # Calcular estadísticas por fonema
        phoneme_stats = {}
        for phoneme, durations in phoneme_durations.items():
            if durations:
                phoneme_stats[phoneme] = {
                    "avg_duration": float(np.mean(durations)),
                    "std_duration": float(np.std(durations)),
                    "count": len(durations)
                }
        
        return {
            "phoneme_stats": phoneme_stats,
            "avg_phoneme_duration": float(np.mean([stats["avg_duration"] for stats in phoneme_stats.values()])) if phoneme_stats else 0.1
        }

# Global text-audio aligner
text_audio_aligner = TextAudioAligner()

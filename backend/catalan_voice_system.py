"""
Advanced Catalan Voice System for VeuPlus
Creates gender-specific voice models with Barcelona accent
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

logger = logging.getLogger("veuplus.catalan_voices")

class CatalanVoiceSystem:
    """Advanced Catalan voice system with gender-specific models"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.voice_models_dir = self.base_dir / "voice_models"
        self.voice_models_dir.mkdir(exist_ok=True, parents=True)
        
        # Voice recordings with metadata
        self.voice_recordings = {
            "masculine_voice_1": {
                "path": self.voice_models_dir / "user_reference_voice.mp3",
                "gender": "masculine",
                "accent": "barcelona",
                "speaker_id": "male_bcn_1",
                "description": "Voz masculina catalana - Barcelona"
            },
            "feminine_voice_1": {
                "path": self.voice_models_dir / "user_reference_voice_2.mp3", 
                "gender": "feminine",
                "accent": "barcelona",
                "speaker_id": "female_bcn_1",
                "description": "Voz femenina catalana - Barcelona"
            },
            "masculine_voice_2": {
                "path": self.voice_models_dir / "catalan_reference_with_text.mp3",
                "gender": "masculine",
                "accent": "barcelona", 
                "speaker_id": "male_bcn_2",
                "description": "Voz masculina catalana - Barcelona (con texto)",
                "reference_text": """Ciutadanes i ciutadans de Catalunya,  
Vull desitjar-vos que estigueu passant i passeu unes molt bones festes de Nadal i que tingueu 
una molt bona entrada d'any 2024."""
            }
        }
        
        # Características específicas del catalán de Barcelona
        self.barcelona_catalan_features = {
            "phonetic_characteristics": {
                # Vocales catalanas
                "vowels": {
                    "a": {"f1": 730, "f2": 1090, "duration": 0.08},
                    "e": {"f1": 530, "f2": 1840, "duration": 0.07}, 
                    "ɛ": {"f1": 610, "f2": 1900, "duration": 0.08},
                    "i": {"f1": 290, "f2": 2320, "duration": 0.06},
                    "o": {"f1": 520, "f2": 870, "duration": 0.08},
                    "ɔ": {"f1": 590, "f2": 880, "duration": 0.08},
                    "u": {"f1": 320, "f2": 800, "duration": 0.07}
                },
                # Consonantes características
                "consonants": {
                    "ɲ": {"duration": 0.12, "type": "nasal"},  # ny
                    "ʎ": {"duration": 0.10, "type": "lateral"}, # ll
                    "ʃ": {"duration": 0.08, "type": "fricative"}, # x
                    "ʒ": {"duration": 0.07, "type": "fricative"}, # j
                    "r": {"duration": 0.06, "type": "trill"},
                    "rr": {"duration": 0.12, "type": "trill"}
                }
            },
            "prosodic_patterns": {
                "stress_pattern": "penultimate",  # Catalán típicamente paroxítono
                "intonation": {
                    "statement": {"start": 0, "peak": 0.3, "end": -0.2},
                    "question": {"start": 0, "peak": 0.6, "end": 0.4},
                    "exclamation": {"start": 0.2, "peak": 0.8, "end": -0.3}
                },
                "rhythm": "syllable_timed",
                "speech_rate": 4.5  # sílabas por segundo típicas del catalán
            },
            "gender_differences": {
                "masculine": {
                    "f0_range": (80, 250),
                    "formant_shift": 1.0,
                    "voice_quality": "modal",
                    "typical_f0": 130
                },
                "feminine": {
                    "f0_range": (150, 350),
                    "formant_shift": 1.15,
                    "voice_quality": "breathy",
                    "typical_f0": 220
                }
            }
        }
    
    async def analyze_all_recordings(self) -> Dict[str, Dict[str, Any]]:
        """Analyze all voice recordings with gender-specific analysis"""
        print("🎤 ANALIZANDO VOCES CATALANAS POR GÉNERO")
        print("=" * 50)
        
        voice_analyses = {}
        
        for voice_id, voice_info in self.voice_recordings.items():
            if voice_info["path"].exists():
                print(f"\n🔊 Analizando: {voice_info['description']}")
                print(f"   Género: {voice_info['gender']}")
                print(f"   Acento: {voice_info['accent']}")
                
                try:
                    analysis = await self.analyze_voice_with_gender_context(voice_info)
                    voice_analyses[voice_id] = analysis
                    
                    print(f"✅ Análisis completado:")
                    print(f"   F0 media: {analysis.get('f0_mean', 0):.1f} Hz")
                    print(f"   Rango F0: {analysis.get('f0_range', 0):.1f} Hz")
                    print(f"   Calidad de voz: {analysis.get('voice_quality_score', 0):.2f}")
                    
                    if "formants" in analysis:
                        formants = analysis["formants"]
                        print(f"   Formantes: F1={formants.get('f1', 0):.0f} F2={formants.get('f2', 0):.0f} Hz")
                    
                except Exception as e:
                    print(f"❌ Error analizando {voice_id}: {e}")
            else:
                print(f"⚠️ Grabación no encontrada: {voice_info['path']}")
        
        return voice_analyses
    
    async def analyze_voice_with_gender_context(self, voice_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze voice with gender-specific context"""
        
        # Cargar audio
        audio_data, sample_rate = librosa.load(str(voice_info["path"]), sr=22050)
        
        # Análisis básico
        analysis = {
            "voice_id": voice_info["speaker_id"],
            "gender": voice_info["gender"],
            "accent": voice_info["accent"],
            "duration": len(audio_data) / sample_rate,
            "sample_rate": sample_rate
        }
        
        # Preprocesar audio
        audio_clean = self.preprocess_audio_for_analysis(audio_data, sample_rate)
        
        # Análisis de pitch con contexto de género
        f0_analysis = await self.analyze_pitch_with_gender(audio_clean, sample_rate, voice_info["gender"])
        analysis.update(f0_analysis)
        
        # Análisis de formantes con ajuste de género
        formant_analysis = await self.analyze_formants_with_gender(audio_clean, sample_rate, voice_info["gender"])
        analysis.update(formant_analysis)
        
        # Características tímbricas específicas
        timbre_analysis = await self.analyze_timbre_characteristics(audio_clean, sample_rate)
        analysis.update(timbre_analysis)
        
        # Análisis prosódico catalán
        prosodic_analysis = await self.analyze_catalan_prosody(audio_clean, sample_rate, voice_info.get("reference_text"))
        analysis.update(prosodic_analysis)
        
        # Calcular puntuación de calidad
        analysis["voice_quality_score"] = self.calculate_voice_quality_score(analysis)
        
        return analysis
    
    def preprocess_audio_for_analysis(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Preprocess audio specifically for Catalan voice analysis"""
        try:
            # Eliminar silencio
            audio_trimmed, _ = librosa.effects.trim(audio_data, top_db=25)
            
            # Normalizar
            audio_normalized = librosa.util.normalize(audio_trimmed)
            
            # Filtro pasa-banda para voz humana
            from scipy.signal import butter, filtfilt
            nyquist = sample_rate / 2
            low = 80 / nyquist
            high = 8000 / nyquist
            b, a = butter(4, [low, high], btype='band')
            audio_filtered = filtfilt(b, a, audio_normalized)
            
            # Pre-énfasis para análisis de formantes
            pre_emphasis = 0.97
            audio_emphasized = np.append(audio_filtered[0], audio_filtered[1:] - pre_emphasis * audio_filtered[:-1])
            
            return audio_emphasized
            
        except Exception as e:
            logger.warning(f"Audio preprocessing failed: {e}")
            return audio_data
    
    async def analyze_pitch_with_gender(self, audio_data: np.ndarray, sample_rate: int, gender: str) -> Dict[str, Any]:
        """Analyze pitch with gender-specific expectations"""
        
        # Rangos de F0 por género
        f0_ranges = self.barcelona_catalan_features["gender_differences"]
        expected_range = f0_ranges[gender]["f0_range"]
        
        # Análisis de pitch
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio_data, 
            fmin=expected_range[0] * 0.8,  # Ampliar rango ligeramente
            fmax=expected_range[1] * 1.2,
            frame_length=2048
        )
        
        f0_clean = f0[~np.isnan(f0)]
        
        pitch_analysis = {}
        
        if len(f0_clean) > 0:
            pitch_analysis.update({
                "f0_mean": float(np.mean(f0_clean)),
                "f0_median": float(np.median(f0_clean)),
                "f0_std": float(np.std(f0_clean)),
                "f0_min": float(np.min(f0_clean)),
                "f0_max": float(np.max(f0_clean)),
                "f0_range": float(np.max(f0_clean) - np.min(f0_clean)),
                "voiced_ratio": float(np.mean(voiced_probs)),
                "f0_contour": [float(x) for x in f0_clean[::max(1, len(f0_clean)//50)]]  # Contorno muestreado
            })
            
            # Verificar si está en el rango esperado para el género
            mean_f0 = np.mean(f0_clean)
            gender_match = expected_range[0] <= mean_f0 <= expected_range[1]
            pitch_analysis["gender_f0_match"] = gender_match
            
            if not gender_match:
                logger.warning(f"F0 {mean_f0:.1f}Hz outside expected {gender} range {expected_range}")
            
            # Calcular estabilidad de pitch
            f0_stability = 1.0 / (1.0 + np.std(f0_clean) / np.mean(f0_clean))
            pitch_analysis["f0_stability"] = float(f0_stability)
            
            # Análisis de vibrato
            if len(f0_clean) > 100:
                # Detectar modulación periódica (vibrato)
                f0_detrended = f0_clean - np.mean(f0_clean)
                fft_f0 = np.fft.fft(f0_detrended)
                freqs_f0 = np.fft.fftfreq(len(fft_f0), 1/22050)
                
                # Buscar picos en 4-8 Hz (rango típico de vibrato)
                vibrato_range = (freqs_f0 >= 4) & (freqs_f0 <= 8)
                if np.any(vibrato_range):
                    vibrato_power = np.mean(np.abs(fft_f0[vibrato_range]))
                    pitch_analysis["vibrato_strength"] = float(vibrato_power)
        
        return pitch_analysis
    
    async def analyze_formants_with_gender(self, audio_data: np.ndarray, sample_rate: int, gender: str) -> Dict[str, Any]:
        """Analyze formants with gender-specific adjustments"""
        
        # Ajuste de formantes por género
        gender_info = self.barcelona_catalan_features["gender_differences"][gender]
        formant_shift = gender_info["formant_shift"]
        
        formant_analysis = {}
        
        try:
            # Análisis de formantes usando múltiples métodos
            formants_lpc = await self.estimate_formants_lpc_advanced(audio_data, sample_rate)
            formants_spectral = await self.estimate_formants_spectral_advanced(audio_data, sample_rate)
            
            # Combinar métodos con ajuste de género
            combined_formants = {}
            for f in ["f1", "f2", "f3", "f4"]:
                lpc_val = formants_lpc.get(f, 0)
                spec_val = formants_spectral.get(f, 0)
                
                if lpc_val > 0 and spec_val > 0:
                    avg_val = (lpc_val + spec_val) / 2
                elif lpc_val > 0:
                    avg_val = lpc_val
                elif spec_val > 0:
                    avg_val = spec_val
                else:
                    # Valores por defecto ajustados por género
                    defaults = {
                        "masculine": {"f1": 730, "f2": 1090, "f3": 2440, "f4": 3400},
                        "feminine": {"f1": 850, "f2": 1220, "f3": 2810, "f4": 3800}
                    }
                    avg_val = defaults[gender][f]
                
                # Aplicar ajuste de género
                combined_formants[f] = float(avg_val * formant_shift)
            
            formant_analysis["formants"] = combined_formants
            
            # Calcular dispersión de formantes (característica de género)
            f1, f2, f3 = combined_formants["f1"], combined_formants["f2"], combined_formants["f3"]
            formant_dispersion = np.sqrt((f2 - f1)**2 + (f3 - f2)**2)
            formant_analysis["formant_dispersion"] = float(formant_dispersion)
            
            # Ratio de formantes (indicador de género)
            formant_analysis["f1_f0_ratio"] = combined_formants["f1"] / 150  # Aproximación
            formant_analysis["f2_f1_ratio"] = combined_formants["f2"] / combined_formants["f1"]
            
            return formant_analysis
            
        except Exception as e:
            logger.error(f"Gender-specific formant analysis failed: {e}")
            return {"formants": {"f1": 730, "f2": 1090, "f3": 2440, "f4": 3400}}
    
    async def estimate_formants_lpc_advanced(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Advanced LPC-based formant estimation"""
        try:
            from scipy.signal import find_peaks
            
            # Parámetros de ventana
            window_length = int(0.025 * sample_rate)  # 25ms
            hop_length = int(0.01 * sample_rate)      # 10ms
            
            formant_tracks = {"f1": [], "f2": [], "f3": [], "f4": []}
            
            for i in range(0, len(audio_data) - window_length, hop_length):
                frame = audio_data[i:i + window_length]
                
                # Aplicar ventana
                windowed = frame * np.hanning(len(frame))
                
                # FFT para análisis espectral
                fft_frame = np.fft.fft(windowed, n=2048)
                magnitude = np.abs(fft_frame[:1024])
                freqs = np.fft.fftfreq(2048, 1/sample_rate)[:1024]
                
                # Encontrar picos espectrales
                peaks, properties = find_peaks(
                    magnitude,
                    height=np.max(magnitude) * 0.1,
                    distance=20,
                    prominence=np.max(magnitude) * 0.05
                )
                
                # Filtrar a rango de formantes
                peak_freqs = freqs[peaks]
                peak_mags = magnitude[peaks]
                
                # Filtrar por rango de frecuencia de formantes
                valid_peaks = (peak_freqs >= 200) & (peak_freqs <= 4000)
                formant_candidates = peak_freqs[valid_peaks]
                formant_magnitudes = peak_mags[valid_peaks]
                
                # Ordenar por magnitud y tomar los más prominentes
                if len(formant_candidates) > 0:
                    sorted_indices = np.argsort(formant_magnitudes)[::-1]
                    sorted_formants = formant_candidates[sorted_indices]
                    sorted_formants = np.sort(sorted_formants)  # Reordenar por frecuencia
                    
                    # Asignar a formantes
                    for j, formant in enumerate(["f1", "f2", "f3", "f4"]):
                        if j < len(sorted_formants):
                            formant_tracks[formant].append(sorted_formants[j])
            
            # Calcular formantes medianos
            formants = {}
            for formant, values in formant_tracks.items():
                if values:
                    # Usar mediana para robustez
                    formants[formant] = float(np.median(values))
            
            return formants
            
        except Exception as e:
            logger.warning(f"Advanced LPC formant estimation failed: {e}")
            return {}
    
    async def estimate_formants_spectral_advanced(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Advanced spectral formant estimation"""
        try:
            from scipy.signal import welch, find_peaks
            
            # Calcular PSD con ventanas superpuestas
            freqs, psd = welch(audio_data, sample_rate, nperseg=2048, noverlap=1024)
            
            # Suavizar PSD
            from scipy.ndimage import gaussian_filter1d
            psd_smooth = gaussian_filter1d(psd, sigma=2)
            
            # Encontrar picos prominentes
            peaks, properties = find_peaks(
                psd_smooth,
                height=np.max(psd_smooth) * 0.05,
                distance=20,
                prominence=np.max(psd_smooth) * 0.02
            )
            
            peak_freqs = freqs[peaks]
            peak_powers = psd_smooth[peaks]
            
            # Filtrar a rango de formantes
            formant_range = (peak_freqs >= 200) & (peak_freqs <= 4000)
            formant_freqs = peak_freqs[formant_range]
            formant_powers = peak_powers[formant_range]
            
            # Ordenar por potencia y tomar los más prominentes
            if len(formant_freqs) > 0:
                sorted_indices = np.argsort(formant_powers)[::-1]
                sorted_formants = formant_freqs[sorted_indices]
                sorted_formants = np.sort(sorted_formants)  # Reordenar por frecuencia
                
                formants = {}
                for i, formant in enumerate(["f1", "f2", "f3", "f4"]):
                    if i < len(sorted_formants):
                        formants[formant] = float(sorted_formants[i])
                
                return formants
            
            return {}
            
        except Exception as e:
            logger.warning(f"Advanced spectral formant estimation failed: {e}")
            return {}
    
    async def analyze_timbre_characteristics(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze detailed timbre characteristics"""
        
        timbre_analysis = {}
        
        try:
            # MFCC detallado (20 coeficientes)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=20)
            timbre_analysis.update({
                "mfcc_mean": [float(x) for x in np.mean(mfccs, axis=1)],
                "mfcc_std": [float(x) for x in np.std(mfccs, axis=1)],
                "mfcc_delta": [float(x) for x in np.mean(librosa.feature.delta(mfccs), axis=1)]
            })
            
            # Características espectrales avanzadas
            spectral_features = {
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0])),
                "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0])),
                "spectral_contrast": [float(x) for x in np.mean(librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate), axis=1)],
                "spectral_flatness": float(np.mean(librosa.feature.spectral_flatness(y=audio_data)[0])),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]))
            }
            timbre_analysis.update(spectral_features)
            
            # Chroma (contenido armónico)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
            timbre_analysis.update({
                "chroma_mean": [float(x) for x in np.mean(chroma, axis=1)],
                "chroma_std": [float(x) for x in np.std(chroma, axis=1)]
            })
            
            # Tonnetz (red armónica)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
            timbre_analysis["tonnetz_mean"] = [float(x) for x in np.mean(tonnetz, axis=1)]
            
            return timbre_analysis
            
        except Exception as e:
            logger.warning(f"Timbre analysis failed: {e}")
            return {}
    
    async def analyze_catalan_prosody(self, audio_data: np.ndarray, sample_rate: int, reference_text: Optional[str] = None) -> Dict[str, Any]:
        """Analyze Catalan-specific prosodic features"""
        
        prosody_analysis = {}
        
        try:
            # Análisis de tempo
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            prosody_analysis["tempo"] = float(tempo)
            
            # Análisis de energía para detectar acentos
            energy = librosa.feature.rms(y=audio_data, frame_length=2048, hop_length=512)[0]
            prosody_analysis.update({
                "energy_mean": float(np.mean(energy)),
                "energy_std": float(np.std(energy)),
                "energy_range": float(np.max(energy) - np.min(energy)),
                "energy_contour": [float(x) for x in energy[::max(1, len(energy)//30)]]
            })
            
            # Si tenemos texto de referencia, hacer análisis más detallado
            if reference_text:
                prosody_analysis.update(await self.analyze_text_specific_prosody(audio_data, sample_rate, reference_text))
            
            # Características específicas del catalán
            prosody_analysis.update({
                "estimated_speech_rate": self.estimate_catalan_speech_rate(audio_data, sample_rate),
                "stress_pattern": "penultimate",  # Catalán típicamente paroxítono
                "rhythm_type": "syllable_timed"
            })
            
            return prosody_analysis
            
        except Exception as e:
            logger.warning(f"Catalan prosody analysis failed: {e}")
            return {}
    
    def estimate_catalan_speech_rate(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Estimate speech rate for Catalan"""
        try:
            # Detectar onset de sílabas usando onset strength
            onset_frames = librosa.onset.onset_detect(
                y=audio_data, 
                sr=sample_rate, 
                units='time',
                hop_length=512,
                backtrack=True
            )
            
            if len(onset_frames) > 1:
                duration = len(audio_data) / sample_rate
                syllables_per_second = len(onset_frames) / duration
                return float(syllables_per_second)
            else:
                return 4.5  # Valor típico para catalán
                
        except Exception as e:
            logger.warning(f"Speech rate estimation failed: {e}")
            return 4.5
    
    async def analyze_text_specific_prosody(self, audio_data: np.ndarray, sample_rate: int, text: str) -> Dict[str, Any]:
        """Analyze prosody with known text"""
        
        text_prosody = {}
        
        try:
            # Contar elementos del texto
            words = text.lower().split()
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            # Calcular estadísticas de texto
            total_syllables = sum(self.count_syllables_catalan(word) for word in words)
            duration = len(audio_data) / sample_rate
            
            text_prosody.update({
                "words_in_text": len(words),
                "sentences_in_text": len(sentences),
                "syllables_in_text": total_syllables,
                "calculated_speech_rate": total_syllables / duration,
                "words_per_minute": (len(words) / duration) * 60,
                "avg_word_duration": duration / len(words) if words else 0
            })
            
            # Analizar patrones de puntuación para entonación
            punctuation_analysis = {
                "has_questions": "?" in text,
                "has_exclamations": "!" in text,
                "comma_count": text.count(","),
                "period_count": text.count("."),
                "sentence_length_avg": len(words) / len(sentences) if sentences else 0
            }
            text_prosody["punctuation_analysis"] = punctuation_analysis
            
            return text_prosody
            
        except Exception as e:
            logger.warning(f"Text-specific prosody analysis failed: {e}")
            return {}
    
    def calculate_voice_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall voice quality score"""
        
        score_factors = []
        
        # Factor 1: Estabilidad de pitch
        if "f0_stability" in analysis:
            score_factors.append(analysis["f0_stability"])
        
        # Factor 2: Ratio de voz (cuánto del audio es voz)
        if "voiced_ratio" in analysis:
            score_factors.append(analysis["voiced_ratio"])
        
        # Factor 3: Consistencia de energía
        if "energy_std" in analysis and "energy_mean" in analysis:
            energy_consistency = 1.0 / (1.0 + analysis["energy_std"] / analysis["energy_mean"])
            score_factors.append(energy_consistency)
        
        # Factor 4: Correspondencia de género
        if "gender_f0_match" in analysis:
            score_factors.append(1.0 if analysis["gender_f0_match"] else 0.5)
        
        # Factor 5: Riqueza espectral
        if "spectral_contrast" in analysis:
            spectral_richness = np.mean(analysis["spectral_contrast"])
            normalized_richness = min(spectral_richness / 30.0, 1.0)  # Normalizar
            score_factors.append(normalized_richness)
        
        if score_factors:
            return float(np.mean(score_factors))
        else:
            return 0.5  # Score neutral si no hay datos
    
    async def create_gender_specific_models(self) -> Dict[str, Dict[str, Any]]:
        """Create gender-specific voice models"""
        print("\n👥 CREANDO MODELOS ESPECÍFICOS POR GÉNERO")
        print("=" * 50)
        
        # Analizar todas las grabaciones
        voice_analyses = await self.analyze_all_recordings()
        
        # Separar por género
        masculine_voices = {k: v for k, v in voice_analyses.items() if v.get("gender") == "masculine"}
        feminine_voices = {k: v for k, v in voice_analyses.items() if v.get("gender") == "feminine"}
        
        print(f"✅ Voces masculinas: {len(masculine_voices)}")
        print(f"✅ Voces femeninas: {len(feminine_voices)}")
        
        # Crear modelos por género
        gender_models = {}
        
        if masculine_voices:
            masculine_model = await self.create_gender_model(masculine_voices, "masculine")
            gender_models["masculine"] = masculine_model
            print(f"✅ Modelo masculino creado: {masculine_model['name']}")
        
        if feminine_voices:
            feminine_model = await self.create_gender_model(feminine_voices, "feminine")
            gender_models["feminine"] = feminine_model
            print(f"✅ Modelo femenino creado: {feminine_model['name']}")
        
        return gender_models
    
    async def create_gender_model(self, voice_analyses: Dict[str, Dict[str, Any]], gender: str) -> Dict[str, Any]:
        """Create consolidated model for specific gender"""
        
        model_id = str(uuid.uuid4())
        
        # Promediar características por género
        all_features = list(voice_analyses.values())
        averaged_features = self.average_voice_features(all_features)
        
        # Crear modelo
        gender_model = {
            "id": model_id,
            "name": f"Voz Catalana {gender.title()}",
            "gender": gender,
            "language": "ca",
            "accent": "barcelona",
            "quality": "hyperrealistic_gender_specific",
            "created_at": datetime.now().isoformat(),
            "model_type": "gender_specific_catalan",
            
            # Características consolidadas
            "voice_features": averaged_features,
            "source_voices": list(voice_analyses.keys()),
            "voice_count": len(voice_analyses),
            
            # Configuración específica de género
            "gender_config": self.barcelona_catalan_features["gender_differences"][gender],
            "phonetic_config": self.barcelona_catalan_features["phonetic_characteristics"],
            "prosodic_config": self.barcelona_catalan_features["prosodic_patterns"]
        }
        
        # Guardar modelo
        model_path = self.voice_models_dir / f"{model_id}_gender_{gender}.json"
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(gender_model, f, indent=2, ensure_ascii=False)
        
        return gender_model
    
    def average_voice_features(self, features_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Average features across multiple voices"""
        
        if not features_list:
            return {}
        
        averaged = {}
        
        # Características escalares
        scalar_keys = [
            "f0_mean", "f0_std", "f0_range", "voiced_ratio", "f0_stability",
            "rms_energy", "spectral_centroid", "spectral_bandwidth", "spectral_rolloff",
            "energy_mean", "energy_std", "tempo", "voice_quality_score"
        ]
        
        for key in scalar_keys:
            values = [f.get(key) for f in features_list if f.get(key) is not None]
            if values:
                averaged[key] = float(np.mean(values))
                averaged[f"{key}_std"] = float(np.std(values))
        
        # Características de array
        array_keys = ["mfcc_mean", "mfcc_std", "spectral_contrast", "chroma_mean"]
        
        for key in array_keys:
            arrays = [f.get(key) for f in features_list if f.get(key) is not None]
            if arrays and all(len(arr) == len(arrays[0]) for arr in arrays):
                averaged[key] = [float(x) for x in np.mean(arrays, axis=0)]
                averaged[f"{key}_variance"] = [float(x) for x in np.std(arrays, axis=0)]
        
        # Formantes promedio
        formant_data = [f.get("formants") for f in features_list if f.get("formants")]
        if formant_data:
            avg_formants = {}
            for formant in ["f1", "f2", "f3", "f4"]:
                values = [fd.get(formant) for fd in formant_data if fd.get(formant)]
                if values:
                    avg_formants[formant] = float(np.mean(values))
                    avg_formants[f"{formant}_std"] = float(np.std(values))
            averaged["formants"] = avg_formants
        
        return averaged
    
    def count_syllables_catalan(self, word: str) -> int:
        """Count syllables in Catalan word (improved)"""
        vowels = "aeiouàèéíòóúü"
        word = word.lower()
        syllables = 0
        prev_was_vowel = False
        
        i = 0
        while i < len(word):
            char = word[i]
            is_vowel = char in vowels
            
            if is_vowel and not prev_was_vowel:
                syllables += 1
                
                # Manejar diptongos catalanes
                if i < len(word) - 1:
                    next_char = word[i + 1]
                    if next_char in vowels:
                        # Verificar si es diptongo o hiato
                        diphthongs = ["ai", "au", "ei", "eu", "ie", "io", "iu", "oi", "ou", "ua", "ue", "ui", "uo"]
                        if word[i:i+2] in diphthongs:
                            i += 1  # Saltar la segunda vocal del diptongo
            
            prev_was_vowel = is_vowel
            i += 1
        
        return max(syllables, 1)

# Global Catalan voice system
catalan_voice_system = CatalanVoiceSystem()























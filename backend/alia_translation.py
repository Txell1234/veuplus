"""
ALIA Kit Translation - Sistema de traducció multilingüe
Traducció entre llengües cooficials espanyoles
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Verificar disponibilitat de llibreries
try:
    from transformers import MarianMTModel, MarianTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")


class AliaTranslation:
    """
    Sistema de traducció ALIA Kit
    """
    
    def __init__(self):
        self.name = "ALIA Translation"
        self.model_cache = {}
        self.tokenizer_cache = {}
        self.device = "cuda" if torch.cuda.is_available() and TRANSFORMERS_AVAILABLE else "cpu"
        logger.info(f"✅ ALIA Translation initialized on {self.device}")
    
    def get_translation_models(self) -> Dict[str, str]:
        """
        Obtenir models de traducció disponibles
        """
        return {
            # Català <-> Castellà
            "ca-es": "Helsinki-NLP/opus-mt-ca-es",
            "es-ca": "Helsinki-NLP/opus-mt-es-ca",
            
            # Castellà <-> Anglès
            "es-en": "Helsinki-NLP/opus-mt-es-en",
            "en-es": "Helsinki-NLP/opus-mt-en-es",
            
            # Català <-> Anglès (via castellà)
            "ca-en": "Helsinki-NLP/opus-mt-ca-en",
            "en-ca": "Helsinki-NLP/opus-mt-en-ca",
            
            # Gallec <-> Castellà
            "gl-es": "Helsinki-NLP/opus-mt-gl-es",
            "es-gl": "Helsinki-NLP/opus-mt-es-gl",
            
            # Euskera <-> Castellà
            "eu-es": "Helsinki-NLP/opus-mt-eu-es",
            "es-eu": "Helsinki-NLP/opus-mt-es-eu",
        }
    
    def get_supported_languages(self) -> List[str]:
        """
        Obtenir idiomes suportats
        """
        return ["ca", "es", "eu", "gl", "en"]
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_preference: str = "auto"
    ) -> Dict[str, Any]:
        """
        Traduir text entre idiomes
        """
        try:
            logger.info(f"🎯 ALIA Translation: {source_lang} -> {target_lang}")
            
            if not TRANSFORMERS_AVAILABLE:
                return {
                    "success": False,
                    "error": "Transformers not available"
                }
            
            # Verificar idiomes suportats
            supported = self.get_supported_languages()
            if source_lang not in supported or target_lang not in supported:
                return {
                    "success": False,
                    "error": f"Language pair {source_lang}-{target_lang} not supported"
                }
            
            # Si són el mateix idioma, retornar text original
            if source_lang == target_lang:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "model_used": "none (same language)",
                    "method": "passthrough"
                }
            
            # Obtenir model de traducció
            model_key = f"{source_lang}-{target_lang}"
            models = self.get_translation_models()
            
            if model_key in models:
                # Traducció directa
                result = await self._translate_direct(
                    text,
                    source_lang,
                    target_lang,
                    models[model_key]
                )
                if result.get("success"):
                    return result
            else:
                # Traducció indirecta (via castellà)
                result = await self._translate_indirect(
                    text,
                    source_lang,
                    target_lang
                )
                if result.get("success"):
                    return result
            
            # Fallback a resposta template
            return self._translate_template(text, source_lang, target_lang)
            
        except Exception as e:
            logger.error(f"ALIA Translation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _translate_direct(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Traducció directa amb model específic
        """
        try:
            logger.info(f"🔄 Traducció directa: {model_id}")
            
            # Carregar model i tokenizer
            if model_id not in self.model_cache:
                logger.info(f"📥 Carregant model de traducció: {model_id}")
                
                tokenizer = MarianTokenizer.from_pretrained(model_id)
                model = MarianMTModel.from_pretrained(model_id)
                
                if self.device == "cuda":
                    model = model.to("cuda")
                
                self.model_cache[model_id] = model
                self.tokenizer_cache[model_id] = tokenizer
                logger.info(f"✅ Model carregat: {model_id}")
            else:
                model = self.model_cache[model_id]
                tokenizer = self.tokenizer_cache[model_id]
            
            # Traduir
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            translated = model.generate(**inputs, max_length=512)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            logger.info(f"✅ Traducció exitosa: {translated_text[:50]}...")
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model_used": model_id,
                "method": "direct_translation",
                "original_text": text,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Direct translation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _translate_indirect(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Traducció indirecta via castellà
        """
        try:
            logger.info(f"🔄 Traducció indirecta: {source_lang} -> es -> {target_lang}")
            
            models = self.get_translation_models()
            
            # Primer pas: source -> es
            if source_lang != "es":
                step1_key = f"{source_lang}-es"
                if step1_key not in models:
                    return {
                        "success": False,
                        "error": f"No model for {step1_key}"
                    }
                
                step1 = await self._translate_direct(
                    text,
                    source_lang,
                    "es",
                    models[step1_key]
                )
                
                if not step1.get("success"):
                    return step1
                
                intermediate_text = step1["translated_text"]
            else:
                intermediate_text = text
            
            # Segon pas: es -> target
            if target_lang != "es":
                step2_key = f"es-{target_lang}"
                if step2_key not in models:
                    return {
                        "success": False,
                        "error": f"No model for {step2_key}"
                    }
                
                step2 = await self._translate_direct(
                    intermediate_text,
                    "es",
                    target_lang,
                    models[step2_key]
                )
                
                if not step2.get("success"):
                    return step2
                
                final_text = step2["translated_text"]
            else:
                final_text = intermediate_text
            
            logger.info(f"✅ Traducció indirecta exitosa")
            
            return {
                "success": True,
                "translated_text": final_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model_used": f"indirect via es",
                "method": "indirect_translation",
                "original_text": text,
                "intermediate_text": intermediate_text if source_lang != "es" and target_lang != "es" else None,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Indirect translation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _translate_template(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Traducció template (fallback)
        """
        templates = {
            "ca-es": "[Traducció ca->es] {text}",
            "es-ca": "[Traducció es->ca] {text}",
            "ca-en": "[Translation ca->en] {text}",
            "en-ca": "[Traducció en->ca] {text}",
        }
        
        key = f"{source_lang}-{target_lang}"
        template = templates.get(key, f"[Translation {source_lang}->{target_lang}] {{text}}")
        
        return {
            "success": True,
            "translated_text": template.format(text=text),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "model_used": "template",
            "method": "template_fallback",
            "note": "Model real no disponible, usant traducció template",
            "original_text": text,
            "created_at": datetime.now().isoformat()
        }
    
    async def detect_and_translate(
        self,
        text: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Detectar idioma i traduir automàticament
        """
        try:
            # Detectar idioma (simple heurística)
            detected_lang = self._detect_language_simple(text)
            
            # Traduir
            result = await self.translate(text, detected_lang, target_lang)
            
            if result.get("success"):
                result["detected_source_lang"] = detected_lang
            
            return result
            
        except Exception as e:
            logger.error(f"Detect and translate failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _detect_language_simple(self, text: str) -> str:
        """
        Detecció simple d'idioma per heurística
        """
        text_lower = text.lower()
        
        # Paraules clau catalanes
        catalan_words = ["què", "això", "també", "però", "amb", "són", "està"]
        # Paraules clau castellanes
        spanish_words = ["qué", "eso", "también", "pero", "con", "son", "está"]
        # Paraules clau euskera
        basque_words = ["da", "dira", "dut", "dugu", "eta", "baina"]
        # Paraules clau gallec
        galician_words = ["que", "iso", "tamén", "pero", "con", "son", "está"]
        
        ca_score = sum(1 for word in catalan_words if word in text_lower)
        es_score = sum(1 for word in spanish_words if word in text_lower)
        eu_score = sum(1 for word in basque_words if word in text_lower)
        gl_score = sum(1 for word in galician_words if word in text_lower)
        
        scores = {"ca": ca_score, "es": es_score, "eu": eu_score, "gl": gl_score}
        detected = max(scores, key=scores.get)
        
        return detected if scores[detected] > 0 else "es"  # Default castellà


# Instància global
alia_translation = AliaTranslation()


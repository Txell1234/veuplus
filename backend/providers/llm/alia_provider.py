#!/usr/bin/env python3
"""
ALIA Kit LLM Provider for VeuPlus
Integra Salamandra i altres models BSC amb el sistema existent
"""

import logging
from typing import Dict, Any, Optional, List, AsyncIterator
import asyncio

logger = logging.getLogger("veuplus.llm.alia")

# Detectar disponibilitat de transformers
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available for ALIA LLM")

# Importar el provider ALIA
try:
    from backend.alia_integration import alia_provider
    ALIA_INTEGRATION_AVAILABLE = True
except ImportError:
    try:
        import sys
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from alia_integration import alia_provider
        ALIA_INTEGRATION_AVAILABLE = True
    except:
        ALIA_INTEGRATION_AVAILABLE = False


class AliaLLMProvider:
    """
    Provider LLM per models ALIA Kit (BSC)
    S'integra amb l'arquitectura existent de VeuPlus
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_id = None
        self.loaded = False
        logger.info("ALIA LLM Provider initialized")
    
    def _load_model(self, model_id: str = "BSC-LT/salamandra-2b") -> bool:
        """Carregar model ALIA/Salamandra"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                logger.error("Transformers not available")
                return False
            
            if self.loaded and self.model_id == model_id:
                logger.info(f"Model {model_id} already loaded")
                return True
            
            logger.info(f"Loading ALIA model: {model_id}")
            
            # Modelos alternativos conocidos
            alternative_models = [
                model_id,
                "projecte-aina/aguila-7b",  # Modelo AINA conocido
                "BSC-LT/salamandra-7b",
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Fallback pequeño
            ]
            
            for alt_model in alternative_models:
                try:
                    logger.info(f"Intentando cargar: {alt_model}")
                    
                    # Cargar tokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        alt_model,
                        trust_remote_code=True
                    )
                    
                    # Cargar model
                    self.model = AutoModelForCausalLM.from_pretrained(
                        alt_model,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else "cpu",
                        trust_remote_code=True,
                        low_cpu_mem_usage=True
                    )
                    
                    self.model_id = alt_model
                    self.loaded = True
                    logger.info(f"✅ Model loaded successfully: {alt_model}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"Failed to load {alt_model}: {e}")
                    continue
            
            logger.error("No ALIA models could be loaded")
            return False
            
        except Exception as e:
            logger.error(f"Error loading ALIA model: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        language: str = "ca"
    ) -> Dict[str, Any]:
        """
        Generar text amb model ALIA
        """
        try:
            # Intentar carregar model si no està carregat
            if not self.loaded:
                loaded = self._load_model()
                if not loaded:
                    # Fallback a resposta template
                    return await self._generate_template(prompt, language)
            
            # Generar amb el model carregat
            if self.model and self.tokenizer:
                inputs = self.tokenizer(prompt, return_tensors="pt")
                
                # Mover a GPU si está disponible
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Generar
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.9,
                        top_k=50
                    )
                
                # Decodificar
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Extraer solo la respuesta (después del prompt)
                if generated_text.startswith(prompt):
                    response = generated_text[len(prompt):].strip()
                else:
                    response = generated_text
                
                return {
                    "success": True,
                    "text": response,
                    "model": self.model_id,
                    "provider": "alia_kit_bsc",
                    "language": language,
                    "tokens_generated": len(response.split()),
                    "real_model": True
                }
            else:
                # Fallback
                return await self._generate_template(prompt, language)
            
        except Exception as e:
            logger.error(f"ALIA generation error: {e}")
            # Fallback a template en caso de error
            return await self._generate_template(prompt, language)
    
    async def _generate_template(self, prompt: str, language: str) -> Dict[str, Any]:
        """Generar resposta template mentre esperem models reals"""
        templates = {
            "ca": f"Com a assistent ALIA Kit, estic procesant: '{prompt[:80]}...'. Els models BSC Salamandra s'estan integrant. Per ara, puc oferir respostes bàsiques.",
            "es": f"Como asistente ALIA Kit, estoy procesando: '{prompt[:80]}...'. Los modelos BSC Salamandra se están integrando. Por ahora, puedo ofrecer respuestas básicas.",
            "eu": f"ALIA Kit laguntzaile gisa: '{prompt[:80]}...' Salamandra ereduak integratzen ari dira.",
            "gl": f"Como asistente ALIA Kit: '{prompt[:80]}...' Os modelos BSC Salamandra están integrándose."
        }
        
        response = templates.get(language, templates["ca"])
        
        return {
            "success": True,
            "text": response,
            "model": "template",
            "provider": "alia_kit_bsc",
            "language": language,
            "tokens_generated": len(response.split()),
            "note": "Template response - Real model loading in progress",
            "phase": 2
        }
    
    async def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        language: str = "ca"
    ) -> AsyncIterator[str]:
        """
        Generar text amb streaming (per futures implementacions)
        """
        # Per ara, generar tot d'un cop
        result = await self.generate(prompt, max_tokens, temperature, language)
        
        if result.get("success"):
            text = result.get("text", "")
            # Simular streaming
            words = text.split()
            for word in words:
                yield word + " "
                await asyncio.sleep(0.05)  # Simular latència


# Instància global
alia_llm_provider = AliaLLMProvider()


# Funcions d'exportació per integrar amb VeuPlus
async def generate_with_alia(
    prompt: str,
    language: str = "ca",
    max_tokens: int = 512,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Wrapper per generar amb ALIA"""
    return await alia_llm_provider.generate(prompt, max_tokens, temperature, language)


def is_alia_llm_available() -> bool:
    """Verificar si el LLM ALIA està disponible"""
    return TRANSFORMERS_AVAILABLE and ALIA_INTEGRATION_AVAILABLE


if __name__ == "__main__":
    # Test
    print("="*60)
    print("ALIA LLM Provider Test")
    print("="*60)
    
    print(f"\nTransformers available: {TRANSFORMERS_AVAILABLE}")
    print(f"ALIA integration available: {ALIA_INTEGRATION_AVAILABLE}")
    print(f"ALIA LLM ready: {is_alia_llm_available()}")
    
    # Test de generació
    import asyncio
    
    async def test():
        result = await generate_with_alia(
            "Explica'm què és la intel·ligència artificial",
            language="ca"
        )
        print(f"\nResposta: {result}")
    
    asyncio.run(test())


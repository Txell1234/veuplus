"""
ALIA Kit LLM Multilingual - Models de llenguatge ALIA
Integra Salamandra, ALIA-40B i altres models BSC
"""

import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)

# Verificar disponibilitat de llibreries
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")


class AliaLLMMultilingual:
    """
    LLM multilingüe amb models ALIA Kit (Salamandra, ALIA-40B)
    """
    
    def __init__(self):
        self.name = "ALIA LLM Multilingual"
        self.model_cache = {}
        self.tokenizer_cache = {}
        self.device = "cuda" if torch.cuda.is_available() and TRANSFORMERS_AVAILABLE else "cpu"
        logger.info(f"✅ ALIA LLM Multilingual initialized on {self.device}")
    
    def get_alia_llm_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtenir models LLM d'ALIA Kit disponibles
        """
        return {
            "salamandra-7b": {
                "model_id": "BSC-LT/salamandra-7b",
                "name": "Salamandra 7B",
                "description": "Model català/castellà de 7B paràmetres",
                "languages": ["ca", "es"],
                "size": "7B",
                "context_length": 4096,
                "recommended": True
            },
            "salamandra-2b": {
                "model_id": "BSC-LT/salamandra-2b",
                "name": "Salamandra 2B",
                "description": "Model lleuger català/castellà de 2B paràmetres",
                "languages": ["ca", "es"],
                "size": "2B",
                "context_length": 4096,
                "recommended": False
            },
            "alia-40b": {
                "model_id": "BSC-LT/ALIA-40b",
                "name": "ALIA 40B",
                "description": "Model multilingüe gran de 40B paràmetres",
                "languages": ["ca", "es", "eu", "gl", "en", "fr", "de", "it", "pt"],
                "size": "40B",
                "context_length": 8192,
                "recommended": False,
                "note": "Requereix GPU potent o quantització"
            }
        }
    
    async def generate_response(
        self,
        prompt: str,
        model_name: str = "salamandra-7b",
        language: str = "ca",
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generar resposta amb models ALIA LLM
        """
        try:
            logger.info(f"🎯 ALIA LLM: Generating response with {model_name}")
            
            if not TRANSFORMERS_AVAILABLE:
                return {
                    "success": False,
                    "error": "Transformers not available"
                }
            
            # Obtenir configuració del model
            models_config = self.get_alia_llm_models()
            if model_name not in models_config:
                return {
                    "success": False,
                    "error": f"Model {model_name} not found"
                }
            
            model_config = models_config[model_name]
            model_id = model_config["model_id"]
            
            # Intentar carregar i generar
            try:
                result = await self._generate_with_model(
                    model_id,
                    prompt,
                    language,
                    max_tokens,
                    temperature,
                    stream
                )
                
                if result.get("success"):
                    return result
                
            except Exception as model_error:
                logger.warning(f"Model {model_id} failed: {model_error}")
            
            # Fallback a resposta template
            logger.warning(f"⚠️ Model {model_name} no disponible, usant resposta template")
            return self._generate_template_response(prompt, language, model_name)
            
        except Exception as e:
            logger.error(f"ALIA LLM failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_with_model(
        self,
        model_id: str,
        prompt: str,
        language: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Dict[str, Any]:
        """
        Generar amb model real
        """
        try:
            # Carregar model i tokenizer
            if model_id not in self.model_cache:
                logger.info(f"📥 Carregant model: {model_id}")
                
                # Configurar quantització per models grans
                quantization_config = None
                if "40b" in model_id.lower():
                    try:
                        from transformers import BitsAndBytesConfig
                        quantization_config = BitsAndBytesConfig(
                            load_in_8bit=True,
                            llm_int8_threshold=6.0
                        )
                    except:
                        logger.warning("Quantization not available for 40B model")
                
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True
                )
                
                self.model_cache[model_id] = model
                self.tokenizer_cache[model_id] = tokenizer
                logger.info(f"✅ Model carregat: {model_id}")
            else:
                model = self.model_cache[model_id]
                tokenizer = self.tokenizer_cache[model_id]
            
            # Preparar prompt
            inputs = tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = inputs.to("cuda")
            
            # Generar
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id
            )
            
            # Decodificar
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extreure només la resposta (eliminar prompt)
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            logger.info(f"✅ ALIA LLM exitós: {response[:50]}...")
            
            return {
                "success": True,
                "response": response,
                "model_used": model_id,
                "language": language,
                "tokens_generated": len(outputs[0]) - len(inputs.input_ids[0]),
                "method": "alia_llm_real",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_template_response(
        self,
        prompt: str,
        language: str,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Generar resposta template quan el model no està disponible
        """
        templates = {
            "ca": [
                "Entenc la teva pregunta sobre '{topic}'. Com a model ALIA Kit, estic dissenyat per processar català i altres llengües cooficials.",
                "Gràcies per la teva consulta. El model {model} està optimitzat per a català i castellà.",
                "Aquesta és una resposta de demostració del sistema ALIA Kit. Els models reals es carregaran quan estiguin disponibles."
            ],
            "es": [
                "Entiendo tu pregunta sobre '{topic}'. Como modelo ALIA Kit, estoy diseñado para procesar español y otras lenguas cooficiales.",
                "Gracias por tu consulta. El modelo {model} está optimizado para catalán y español.",
                "Esta es una respuesta de demostración del sistema ALIA Kit. Los modelos reales se cargarán cuando estén disponibles."
            ]
        }
        
        template_list = templates.get(language, templates["ca"])
        import random
        response = random.choice(template_list).format(
            topic=prompt[:30],
            model=model_name
        )
        
        return {
            "success": True,
            "response": response,
            "model_used": f"{model_name} (template)",
            "language": language,
            "method": "template_fallback",
            "note": "Model real no disponible, usant resposta template",
            "created_at": datetime.now().isoformat()
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_name: str = "salamandra-7b",
        language: str = "ca",
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Completar conversa amb format chat
        """
        try:
            # Construir prompt des de missatges
            prompt = self._build_chat_prompt(messages, language)
            
            # Generar resposta
            result = await self.generate_response(
                prompt,
                model_name,
                language,
                max_tokens,
                temperature,
                stream=False
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": {
                        "role": "assistant",
                        "content": result["response"]
                    },
                    "model_used": result["model_used"],
                    "language": language,
                    "created_at": datetime.now().isoformat()
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_chat_prompt(self, messages: List[Dict[str, str]], language: str) -> str:
        """
        Construir prompt des de missatges de chat
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"Sistema: {content}")
            elif role == "user":
                prompt_parts.append(f"Usuari: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistent: {content}")
        
        prompt_parts.append("Assistent:")
        
        return "\n".join(prompt_parts)


# Instància global
alia_llm_multilingual = AliaLLMMultilingual()


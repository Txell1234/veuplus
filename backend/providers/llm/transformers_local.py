from __future__ import annotations

import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

_AVAILABLE = False
_MODEL = None
_TOKENIZER = None


def initialize(model_name: str) -> bool:
    global _AVAILABLE, _MODEL, _TOKENIZER
    if os.environ.get("DISABLE_TRANSFORMERS_INIT") == "1":
        logger.info("Transformers init disabled by env")
        _AVAILABLE = False
        return False
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch

        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForCausalLM.from_pretrained(model_name)
        if hasattr(_MODEL, "to"):
            _MODEL = _MODEL.to("cpu")
        _AVAILABLE = True
        logger.info("Transformers local model initialized")
        return True
    except Exception as e:
        logger.warning(f"Failed to init transformers local: {e}")
        _AVAILABLE = False
        return False


def generate(messages: List[Dict[str, str]], max_tokens: int = 256, temperature: float = 0.7) -> str:
    if not _AVAILABLE or _MODEL is None:
        raise RuntimeError("Transformers local model not available")
    import torch

    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages]) + "\nassistant:"
    inputs = _TOKENIZER.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = _MODEL.generate(
            inputs,
            max_length=len(inputs[0]) + max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=_TOKENIZER.eos_token_id,
            eos_token_id=_TOKENIZER.eos_token_id,
        )
    text = _TOKENIZER.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
    return text.strip()



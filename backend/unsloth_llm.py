from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

_MODEL = None
_TOKENIZER = None
_AVAILABLE = False


def is_available() -> bool:
    return _AVAILABLE


def _maybe_import_unsloth():
    global _AVAILABLE
    try:
        from unsloth import FastLanguageModel  # noqa: F401
        from unsloth_zoo import encode_conversations_with_harmony  # noqa: F401
        _AVAILABLE = True
    except Exception:
        _AVAILABLE = False


def load_model(
    model_name: str = os.environ.get("UNSLOTH_MODEL", "unsloth/gpt-oss-20b"),
    max_seq_length: int = int(os.environ.get("UNSLOTH_MAX_SEQ", "16384")),
    load_in_4bit: bool = os.environ.get("UNSLOTH_4BIT", "1") == "1",
    device_map: Optional[str] = os.environ.get("UNSLOTH_DEVICE_MAP", None),
) -> None:
    """Lazy load Unsloth LLM for inference."""
    global _MODEL, _TOKENIZER
    if _MODEL is not None:
        return
    _maybe_import_unsloth()
    if not _AVAILABLE:
        return
    from unsloth import FastLanguageModel
    _MODEL, _TOKENIZER = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
        device_map=device_map,
    )


def generate(
    messages: List[Dict[str, Any]],
    reasoning_effort: str = os.environ.get("UNSLOTH_REASONING", "medium"),
    temperature: float = 1.0,
    top_p: float = 1.0,
    top_k: int = 0,
    max_new_tokens: int = 512,
) -> str:
    """Generate a reply using Unsloth gpt-oss with Harmony encoding."""
    if _MODEL is None:
        load_model()
    if not _AVAILABLE or _MODEL is None:
        raise RuntimeError("Unsloth backend not available. Install unsloth & unsloth_zoo.")

    from unsloth_zoo import encode_conversations_with_harmony

    text = encode_conversations_with_harmony(
        messages,
        reasoning_effort=reasoning_effort,
        add_generation_prompt=True,
    )
    inputs = _TOKENIZER([text], return_tensors="pt").to(_MODEL.device)
    with _MODEL.disable_training():
        output = _MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )
    decoded = _TOKENIZER.decode(output[0], skip_special_tokens=False)
    # Extract final assistant content after <|channel|>final if present
    # Fallback to full decoded text otherwise
    marker = "<|channel|>final"
    if marker in decoded:
        decoded = decoded.split(marker, 1)[-1]
    # Remove potential end token
    decoded = decoded.replace("<|return|>", "").strip()
    return decoded



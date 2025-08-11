"""
Transformers Service Integration for VeuPlus
Provides serving and chat capabilities using Hugging Face Transformers
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import torch
import json
import httpx
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)
from transformers.generation.streamers import TextIteratorStreamer
import threading
from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from starlette.responses import StreamingResponse

# Setup logging
logger = logging.getLogger(__name__)

# Global variables for model caching
_MODEL = None
_TOKENIZER = None
_PIPELINE = None
_AVAILABLE = False
_CURRENT_MODEL_NAME = None

# Configuration
DEFAULT_MODEL = os.environ.get("TRANSFORMERS_MODEL", "openai/gpt-oss-20b")
MAX_LENGTH = int(os.environ.get("TRANSFORMERS_MAX_LENGTH", "1000"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PROVIDER = os.environ.get("TRANSFORMERS_PROVIDER", "local").lower()  # local | vllm
LOAD_IN_4BIT = os.environ.get("TRANSFORMERS_LOAD_IN_4BIT", "0") == "1"
VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000")

# API Router
transformers_router = APIRouter(prefix="/api/transformers", tags=["Transformers Service"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = DEFAULT_MODEL
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int

def is_available() -> bool:
    """Check if transformers service is available"""
    return _AVAILABLE

def load_model(model_name: str = DEFAULT_MODEL) -> bool:
    """Load the specified model for inference"""
    global _MODEL, _TOKENIZER, _PIPELINE, _AVAILABLE, _CURRENT_MODEL_NAME
    
    try:
        # If provider is vLLM, assume remote service handles the model
        if PROVIDER == "vllm":
            _MODEL = None
            _TOKENIZER = None
            _PIPELINE = None
            _CURRENT_MODEL_NAME = model_name
            _AVAILABLE = True
            logger.info(f"Using vLLM provider at {VLLM_BASE_URL} for model {model_name}")
            return True

        if _CURRENT_MODEL_NAME == model_name and _MODEL is not None:
            logger.info(f"Model {model_name} already loaded")
            return True
            
        logger.info(f"Loading transformers model: {model_name}")
        
        # Load tokenizer and model
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if LOAD_IN_4BIT:
            logger.info("Loading model in 4-bit (bitsandbytes)")
            _MODEL = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                load_in_4bit=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
        else:
            _MODEL = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                device_map="auto" if DEVICE == "cuda" else None,
                trust_remote_code=True
            )
        
        # Create text generation pipeline
        _PIPELINE = pipeline(
            "text-generation",
            model=_MODEL,
            tokenizer=_TOKENIZER,
            device=0 if DEVICE == "cuda" else -1
        )
        
        _CURRENT_MODEL_NAME = model_name
        _AVAILABLE = True
        
        logger.info(f"✅ Transformers model loaded successfully: {model_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load transformers model {model_name}: {str(e)}")
        _AVAILABLE = False
        return False

def _render_messages_as_text(messages: List[Dict[str, str]]) -> str:
    conversation_text = ""
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            conversation_text += f"Human: {content}\n"
        elif role == "assistant":
            conversation_text += f"Assistant: {content}\n"
        elif role == "system":
            conversation_text += f"System: {content}\n"
        else:
            conversation_text += f"{role or 'User'}: {content}\n"
    conversation_text += "Assistant:"
    return conversation_text


def _generate_with_vllm(messages: List[Dict[str, str]], model_name: str, max_tokens: int, temperature: float) -> str:
    url = f"{VLLM_BASE_URL.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def generate_response(messages: List[Dict[str, str]], model_name: str = DEFAULT_MODEL, **kwargs) -> str:
    """Generate a response using the loaded model"""
    global _PIPELINE
    
    if not _AVAILABLE or (PROVIDER == "local" and _PIPELINE is None):
        if not load_model(model_name):
            raise RuntimeError("Transformers model not available")
    
    try:
        max_tokens = kwargs.get('max_tokens', MAX_LENGTH)
        temperature = kwargs.get('temperature', 0.7)

        if PROVIDER == "vllm":
            return _generate_with_vllm(messages, model_name, max_tokens, temperature)

        # Local generation
        conversation_text = _render_messages_as_text(messages)
        inputs = _TOKENIZER.encode(conversation_text, return_tensors="pt")

        with torch.no_grad():
            outputs = _MODEL.generate(
                inputs,
                max_length=len(inputs[0]) + max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=_TOKENIZER.eos_token_id,
                eos_token_id=_TOKENIZER.eos_token_id
            )

        response = _TOKENIZER.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        return response.strip()


def stream_response(messages: List[Dict[str, str]], model_name: str = DEFAULT_MODEL, **kwargs):
    """Yield partial responses (token-by-token) for real-time streaming."""
    if not _AVAILABLE or (PROVIDER == "local" and _MODEL is None):
        if not load_model(model_name):
            raise HTTPException(status_code=503, detail="Transformers model not available")

    max_tokens = kwargs.get('max_tokens', MAX_LENGTH)
    temperature = kwargs.get('temperature', 0.7)

    # vLLM streaming: proxy OpenAI-compatible SSE
    if PROVIDER == "vllm":
        url = f"{VLLM_BASE_URL.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        try:
            with httpx.stream("POST", url, json=payload, timeout=None) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    # Relay as-is (already in 'data: ...' format in most vLLM builds)
                    txt = line.decode("utf-8") if isinstance(line, (bytes, bytearray)) else line
                    if txt.startswith("data:"):
                        yield txt + "\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        # done signal (for clients que lo esperan)
        yield "data: [DONE]\n\n"
        return

    # Local streaming (HF): use TextIteratorStreamer
    try:
        conversation_text = _render_messages_as_text(messages)
        inputs = _TOKENIZER(conversation_text, return_tensors="pt")
        inputs = {k: v.to(_MODEL.device) for k, v in inputs.items()}

        streamer = TextIteratorStreamer(_TOKENIZER, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs = dict(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            streamer=streamer,
            pad_token_id=_TOKENIZER.eos_token_id,
            eos_token_id=_TOKENIZER.eos_token_id,
        )

        thread = threading.Thread(target=_MODEL.generate, kwargs=gen_kwargs)
        thread.start()

        for piece in streamer:
            if piece:
                # SSE chunk
                data = json.dumps({"delta": piece})
                yield f"data: {data}\n\n"

        thread.join()
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"


@transformers_router.post("/stream")
async def stream_chat(request: ChatRequest):
    """SSE endpoint: stream token-a-token la respuesta."""
    async def event_generator():
        # wrap sync generator into async by iterating in threadpool would be complex;
        # use simple sync generator inside StreamingResponse iterator.
        for chunk in stream_response(
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
            model_name=request.model or DEFAULT_MODEL,
            max_tokens=request.max_tokens or MAX_LENGTH,
            temperature=request.temperature or 0.7,
        ):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@transformers_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint using transformers model"""
    try:
        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Generate response
        response = generate_response(
            messages, 
            model_name=request.model or DEFAULT_MODEL,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Calculate approximate token usage
        tokens_used = len(response.split()) * 1.3  # Rough approximation
        
        return ChatResponse(
            response=response,
            model=request.model or DEFAULT_MODEL,
            tokens_used=int(tokens_used)
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@transformers_router.get("/models")
async def list_models():
    """List available models"""
    return {
        "available_models": [
            "openai/gpt-oss-20b",  # Tu modelo instalado manualmente
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large", 
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill",
            "microsoft/DialoGPT-small",
            "gpt2",
            "gpt2-medium",
            "distilgpt2"
        ],
        "current_model": _CURRENT_MODEL_NAME,
        "device": DEVICE,
        "available": _AVAILABLE
    }

@transformers_router.post("/load")
async def load_model_endpoint(model_name: str):
    """Load a specific model"""
    try:
        success = load_model(model_name)
        if success:
            return {"message": f"Model {model_name} loaded successfully", "model": model_name}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load model {model_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@transformers_router.get("/status")
async def service_status():
    """Get service status"""
    return {
        "available": _AVAILABLE,
        "current_model": _CURRENT_MODEL_NAME,
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available()
    }

@transformers_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket chat endpoint for real-time conversations"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if "messages" not in data:
                await websocket.send_json({"error": "Missing 'messages' field"})
                continue
                
            try:
                # Generate response
                response = generate_response(
                    data["messages"],
                    model_name=data.get("model", DEFAULT_MODEL),
                    max_tokens=data.get("max_tokens", 512),
                    temperature=data.get("temperature", 0.7)
                )
                
                await websocket.send_json({
                    "response": response,
                    "model": data.get("model", DEFAULT_MODEL),
                    "status": "success"
                })
                
            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "status": "error"
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

# Initialize on import
def initialize_service():
    """Initialize the transformers service"""
    try:
        logger.info("Initializing Transformers Service...")
        # Try to load default model
        load_model(DEFAULT_MODEL)
    except Exception as e:
        logger.warning(f"Could not initialize transformers service: {str(e)}")

# Auto-initialize when module is imported
if __name__ != "__main__":
    initialize_service()

#!/usr/bin/env python3
"""
Transformers Serve Script for VeuPlus
Implementa les comandes: transformers serve i transformers chat
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
import uvicorn
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.transformers_service import transformers_router, load_model, generate_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_serve_app():
    """Create a standalone FastAPI app for transformers serving"""
    app = FastAPI(
        title="VeuPlus Transformers Service",
        description="Standalone transformers serving API",
        version="1.0.0"
    )
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include transformers router
    app.include_router(transformers_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "VeuPlus Transformers Service", 
            "version": "1.0.0",
            "endpoints": ["/api/transformers/chat", "/api/transformers/models", "/api/transformers/status"]
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "transformers"}
    
    return app

def serve_command(args):
    """Implementa la comanda 'transformers serve'"""
    print("🚀 Starting VeuPlus Transformers Service...")
    
    app = create_serve_app()
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )

def chat_command(args):
    """Implementa la comanda 'transformers chat' contra el servidor HTTP"""
    base_url = f"http://{args.server}"
    print(f"🤖 Starting chat with model: {args.model_name_or_path}")
    print(f"💬 Server: {base_url}")
    print("Type 'exit' to quit, 'clear' to clear conversation")
    print("-" * 50)

    # Intentar cargar el modelo en el servidor
    try:
        r = requests.post(f"{base_url}/api/transformers/load", params={"model_name": args.model_name_or_path}, timeout=60)
        if r.status_code >= 400:
            print(f"⚠️ No se pudo cargar el modelo en el servidor: {r.text}")
        else:
            print("✅ Modelo cargado en el servidor")
    except Exception as e:
        print(f"⚠️ Error cargando el modelo en el servidor: {e}")

    conversation_history = []

    try:
        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() == 'exit':
                    print("👋 Goodbye!")
                    break

                if user_input.lower() == 'clear':
                    conversation_history = []
                    print("🗑️ Conversation cleared!")
                    continue

                if not user_input:
                    continue

                conversation_history.append({"role": "user", "content": user_input})

                print("🤔 Thinking...")
                try:
                    r = requests.post(
                        f"{base_url}/api/transformers/chat",
                        json={
                            "messages": conversation_history,
                            "model": args.model_name_or_path,
                            "max_tokens": 512,
                            "temperature": 0.7,
                        },
                        timeout=120,
                    )
                    if r.status_code >= 400:
                        print(f"❌ Error del servidor: {r.status_code} {r.text}")
                        continue
                    data = r.json()
                    response = data.get("response", "(sin respuesta)")
                except Exception as e:
                    print(f"❌ Error durante la petición: {e}")
                    continue

                conversation_history.append({"role": "assistant", "content": response})
                print(f"🤖 Assistant: {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    except Exception as e:
        print(f"❌ Failed to start chat: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="VeuPlus Transformers CLI",
        prog="transformers"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start transformers API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument("server", help="Server URL (e.g., localhost:8000)")
    chat_parser.add_argument("--model-name-or-path", required=True, 
                           help="Model name or path to use for chat")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        serve_command(args)
    elif args.command == "chat":
        chat_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

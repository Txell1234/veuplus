#!/usr/bin/env python3
"""
Prueba rápida del comando transformers chat
"""

import requests
import sys

def test_chat():
    base_url = "http://localhost:8000"
    model_name = "gpt2-medium"
    
    print(f"🤖 Probando chat con modelo: {model_name}")
    print(f"💬 Server: {base_url}")
    print("-" * 50)

    # Cargar el modelo
    try:
        r = requests.post(f"{base_url}/api/transformers/load", params={"model_name": model_name}, timeout=60)
        if r.status_code >= 400:
            print(f"⚠️ No se pudo cargar el modelo: {r.text}")
            return False
        else:
            print("✅ Modelo cargado en el servidor")
    except Exception as e:
        print(f"⚠️ Error cargando el modelo: {e}")
        return False

    # Probar una conversación
    messages = [
        {"role": "user", "content": "Hello! How are you today?"}
    ]
    
    try:
        print("🤔 Enviando mensaje de prueba...")
        r = requests.post(
            f"{base_url}/api/transformers/chat",
            json={
                "messages": messages,
                "model": model_name,
                "max_tokens": 50,
                "temperature": 0.7,
            },
            timeout=30,
        )
        
        if r.status_code >= 400:
            print(f"❌ Error del servidor: {r.status_code} {r.text}")
            return False
            
        data = r.json()
        response = data.get("response", "(sin respuesta)")
        print(f"🤖 Respuesta: {response}")
        print(f"📊 Tokens usados: {data.get('tokens_used', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la petición: {e}")
        return False

if __name__ == "__main__":
    success = test_chat()
    sys.exit(0 if success else 1)


#!/usr/bin/env python3
"""
Prueba del sistema de chat con voicebots usando transformers
"""

import requests
import sys
import json

def test_voicebot_chat():
    """Probar el chat con voicebots"""
    base_url = "http://localhost:8001"
    
    print("🤖 Probando sistema de voicebots...")
    print(f"🌐 Backend: {base_url}")
    print("-" * 50)

    # Obtener lista de bots
    try:
        print("📋 Obteniendo lista de voicebots...")
        response = requests.get(f"{base_url}/api/voicebots", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo bots: {response.status_code}")
            return False
            
        bots_data = response.json()
        bots = bots_data.get("bots", [])
        
        if not bots:
            print("❌ No hay bots disponibles")
            return False
            
        print(f"✅ Encontrados {len(bots)} bots:")
        for bot in bots:
            print(f"  - {bot['name']} (ID: {bot['id'][:8]}...) - Modelo: {bot.get('model_name', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error conectando con el backend: {e}")
        return False

    # Probar chat con el primer bot
    if bots:
        bot = bots[0]
        print(f"\n💬 Probando chat con: {bot['name']}")
        
        # Mensaje de prueba
        test_message = "Hola! ¿Cómo estás?"
        
        chat_request = {
            "message": test_message,
            "bot_id": bot["id"],
            "conversation_history": []
        }
        
        try:
            print(f"📤 Enviando: '{test_message}'")
            response = requests.post(
                f"{base_url}/api/voicebots/chat",
                json=chat_request,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Error en chat: {response.status_code} - {response.text}")
                return False
                
            chat_response = response.json()
            print(f"🤖 Respuesta: {chat_response.get('reply', 'Sin respuesta')}")
            print(f"🎵 Audio URL: {chat_response.get('audio_url', 'N/A')}")
            print(f"🗣️ Modelo de voz: {chat_response.get('voice_model', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en chat: {e}")
            return False
    
    return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba de voicebots...")
    try:
        success = test_voicebot_chat()
        if success:
            print("\n✅ ¡Prueba de voicebots exitosa!")
            print("Los bots están funcionando correctamente con transformers")
        else:
            print("\n❌ Error en la prueba de voicebots")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


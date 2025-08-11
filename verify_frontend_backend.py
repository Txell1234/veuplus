#!/usr/bin/env python3
"""
Verificar que el frontend y backend están completamente conectados
"""

import requests
import sys
import time

def test_backend_endpoints():
    """Probar que todos los endpoints del backend funcionan"""
    base_url = "http://localhost:8001"
    
    print("🔧 VERIFICANDO BACKEND (Sin MongoDB)")
    print("=" * 50)
    
    # Endpoints críticos que el frontend necesita
    critical_endpoints = [
        ("/api/health", "Health check"),
        ("/api/voicebots", "Lista de voicebots"),
        ("/api/chatbots", "Lista de chatbots"), 
        ("/api/voices", "Lista de voces entrenadas"),
        ("/api/knowledge-base", "Base de conocimiento"),
        ("/api/training/system/status", "Estado de entrenamiento"),
    ]
    
    all_good = True
    
    for endpoint, description in critical_endpoints:
        try:
            print(f"  🧪 {description}... ", end="")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("✅")
                
                # Verificar datos específicos
                if "voicebots" in endpoint:
                    print(f"      📊 {len(data.get('bots', []))} voicebots")
                elif "chatbots" in endpoint:
                    print(f"      📊 {len(data.get('bots', []))} chatbots")
                elif "voices" in endpoint:
                    print(f"      📊 {len(data.get('voices', []))} voces")
                elif "knowledge-base" in endpoint:
                    print(f"      📊 {len(data.get('items', []))} items")
                elif "training" in endpoint:
                    print(f"      📊 Sistema: {'✅' if data.get('system_ready') else '❌'}")
                    
            else:
                print(f"❌ Error {response.status_code}")
                all_good = False
                
        except Exception as e:
            print(f"❌ {str(e)}")
            all_good = False
    
    return all_good

def test_transformers_service():
    """Verificar que el servicio transformers funciona"""
    print("\n🤖 VERIFICANDO TRANSFORMERS SERVICE")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Servicio Transformers activo")
            
            # Verificar modelos
            models_response = requests.get("http://localhost:8000/api/transformers/models", timeout=5)
            if models_response.status_code == 200:
                data = models_response.json()
                models = data.get('available_models', [])
                current = data.get('current_model', 'Ninguno')
                
                print(f"  📊 {len(models)} modelos disponibles")
                print(f"  📊 Modelo actual: {current}")
                
                # Verificar si está nuestro modelo GPT-OSS-20B
                if "openai/gpt-oss-20b" in models:
                    print("  🎯 ✅ GPT-OSS-20B disponible")
                else:
                    print("  🎯 ⚠️ GPT-OSS-20B no en la lista")
                
                return True
            else:
                print("  ❌ Error obteniendo modelos")
                return False
        else:
            print(f"  ❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {str(e)}")
        return False

def test_frontend_connection():
    """Verificar que el frontend está ejecutándose"""
    print("\n🎨 VERIFICANDO FRONTEND")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend React activo")
            return True
        else:
            print(f"  ❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Frontend no disponible: {str(e)}")
        return False

def test_gpt_oss_bot():
    """Verificar que el bot GPT-OSS-20B funciona"""
    print("\n🎯 VERIFICANDO BOT GPT-OSS-20B")
    print("=" * 50)
    
    try:
        # Obtener lista de bots
        response = requests.get("http://localhost:8001/api/voicebots", timeout=5)
        if response.status_code == 200:
            bots = response.json().get('bots', [])
            
            # Buscar bot con GPT-OSS-20B
            gpt_bot = None
            for bot in bots:
                if bot.get('model_name') == 'openai/gpt-oss-20b':
                    gpt_bot = bot
                    break
            
            if gpt_bot:
                print(f"  ✅ Bot encontrado: {gpt_bot['name']}")
                print(f"  📊 ID: {gpt_bot['id']}")
                print(f"  📊 Modelo: {gpt_bot['model_name']}")
                print(f"  📊 Estado: {gpt_bot['status']}")
                return True
            else:
                print("  ❌ Bot GPT-OSS-20B no encontrado")
                return False
        else:
            print("  ❌ Error obteniendo bots")
            return False
    except Exception as e:
        print(f"  ❌ {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA SISTEMA VEUPLUS")
    print("🎯 Sin MongoDB - Solo SQLite + Transformers")
    print("=" * 60)
    
    results = []
    
    # Test 1: Backend
    backend_ok = test_backend_endpoints()
    results.append(("Backend (SQLite)", backend_ok))
    
    # Test 2: Transformers  
    transformers_ok = test_transformers_service()
    results.append(("Transformers", transformers_ok))
    
    # Test 3: Frontend
    frontend_ok = test_frontend_connection()
    results.append(("Frontend", frontend_ok))
    
    # Test 4: GPT-OSS Bot
    bot_ok = test_gpt_oss_bot()
    results.append(("Bot GPT-OSS-20B", bot_ok))
    
    # Resumen final
    print(f"\n{'RESUMEN FINAL'.center(60, '=')}")
    
    all_good = True
    for service, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
        if not status:
            all_good = False
    
    if all_good:
        print(f"\n🎉 ¡SISTEMA 100% FUNCIONAL!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:8001")
        print("🤖 Transformers: http://localhost:8000")
        print("📊 Base de datos: SQLite (No MongoDB)")
        print("🎯 Bot GPT-OSS-20B: Disponible")
        sys.exit(0)
    else:
        print(f"\n❌ HAY PROBLEMAS")
        print("🔧 Asegúrate de que todos los servicios estén ejecutándose")
        sys.exit(1)


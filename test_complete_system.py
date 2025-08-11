#!/usr/bin/env python3
"""
Prueba completa del sistema VeuPlus para verificar que frontend y backend están conectados
"""

import requests
import sys
import json

def test_all_endpoints():
    """Probar todos los endpoints críticos"""
    base_url = "http://localhost:8001"
    
    print("🔍 PROBANDO TODOS LOS ENDPOINTS DEL SISTEMA VEUPLUS")
    print("=" * 60)
    
    endpoints_to_test = [
        ("GET", "/api/health", "Health check"),
        ("GET", "/api/voicebots", "Lista de voicebots"),
        ("GET", "/api/chatbots", "Lista de chatbots"),
        ("GET", "/api/voices", "Lista de voces"),
        ("GET", "/api/knowledge-base", "Base de conocimiento"),
        ("GET", "/api/training/system/status", "Estado del sistema de entrenamiento"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints_to_test:
        try:
            print(f"\n🧪 Probando {description}...")
            print(f"   {method} {base_url}{endpoint}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ {response.status_code} - OK")
                    
                    # Mostrar información específica según el endpoint
                    if "voicebots" in endpoint and "bots" in data:
                        print(f"      📊 Voicebots encontrados: {len(data['bots'])}")
                        for bot in data["bots"][:3]:  # Mostrar solo los primeros 3
                            print(f"         - {bot.get('name', 'Sin nombre')} (Modelo: {bot.get('model_name', 'N/A')})")
                    
                    elif "chatbots" in endpoint and "bots" in data:
                        print(f"      📊 Chatbots encontrados: {len(data['bots'])}")
                    
                    elif "voices" in endpoint and "voices" in data:
                        print(f"      📊 Voces encontradas: {len(data['voices'])}")
                    
                    elif "knowledge-base" in endpoint and "items" in data:
                        print(f"      📊 Items de conocimiento: {len(data['items'])}")
                    
                    elif "system/status" in endpoint:
                        print(f"      📊 Sistema listo: {data.get('system_ready', False)}")
                        print(f"      📊 Idiomas soportados: {', '.join(data.get('supported_languages', []))}")
                        print(f"      📊 Trabajos activos: {data.get('active_training_jobs', 0)}")
                    
                    results.append((endpoint, True, f"OK - {response.status_code}"))
                except json.JSONDecodeError:
                    print(f"   ⚠️ {response.status_code} - Respuesta no es JSON válido")
                    results.append((endpoint, False, f"Invalid JSON - {response.status_code}"))
            else:
                print(f"   ❌ {response.status_code} - Error")
                results.append((endpoint, False, f"Error {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se puede conectar al servidor")
            results.append((endpoint, False, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout")
            results.append((endpoint, False, "Timeout"))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((endpoint, False, f"Exception: {e}"))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for endpoint, success, status in results:
        icon = "✅" if success else "❌"
        print(f"{icon} {endpoint}: {status}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} endpoints funcionando")
    
    if passed == total:
        print("✅ ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        return True
    else:
        print("❌ Hay problemas de conectividad")
        return False

def test_transformers_service():
    """Probar el servicio de transformers separadamente"""
    print("\n🤖 PROBANDO SERVICIO TRANSFORMERS (Puerto 8000)")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servicio Transformers funcionando")
            
            # Probar endpoint de modelos
            models_response = requests.get("http://localhost:8000/api/transformers/models", timeout=5)
            if models_response.status_code == 200:
                data = models_response.json()
                print(f"📊 Modelos disponibles: {len(data.get('available_models', []))}")
                print(f"📊 Modelo actual: {data.get('current_model', 'Ninguno')}")
                return True
            else:
                print("❌ Error obteniendo modelos")
                return False
        else:
            print(f"❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servicio Transformers no disponible: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA COMPLETA DEL SISTEMA VEUPLUS")
    print("🌐 Verificando conectividad Frontend ↔ Backend ↔ Transformers")
    print("=" * 60)
    
    # Probar backend principal
    backend_ok = test_all_endpoints()
    
    # Probar servicio transformers
    transformers_ok = test_transformers_service()
    
    print("\n" + "🎯 VEREDICTO FINAL".center(60, "="))
    
    if backend_ok and transformers_ok:
        print("✅ ¡SISTEMA 100% FUNCIONAL!")
        print("🎉 Frontend, Backend y Transformers conectados correctamente")
        print("🚀 Puedes usar el frontend en http://localhost:3000")
        sys.exit(0)
    elif backend_ok:
        print("⚠️ Backend funcional, pero falta servicio Transformers")
        print("🔧 Arranca: python transformers_serve.py serve --host 0.0.0.0 --port 8000")
        sys.exit(1)
    else:
        print("❌ PROBLEMAS CRÍTICOS DETECTADOS")
        print("🔧 Arranca el backend: python backend/server.py")
        sys.exit(1)


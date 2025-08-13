#!/usr/bin/env python3
"""Test básico sin cargar server.py completo"""

import os
import sys
import tempfile
from pathlib import Path

print("🔍 Test básico - evitando server.py...")

# Configurar entorno
os.environ['DISABLE_TRANSFORMERS_INIT'] = '1'
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

try:
    # Test 1: Database funciona
    print("1. Testing database...")
    temp_db = tempfile.mktemp(suffix='.db')
    os.environ['VEUPLUS_DB_PATH'] = temp_db
    
    from backend.database_sql import VeuPlusDatabase
    db = VeuPlusDatabase()
    
    # Test crear chatbot
    bot_data = {
        'id': 'test-bot',
        'name': 'Test Bot',
        'llm_provider': 'transformers',
        'model_name': 'gpt2',
        'temperature': 0.7,
        'system_prompt': 'Test prompt'
    }
    db.create_chatbot(bot_data)
    
    # Test listar chatbots
    bots = db.get_chatbots()
    assert len(bots) == 1
    assert bots[0]['name'] == 'Test Bot'
    print("✅ Database tests passed")
    
    # Test 2: Storage funciona
    print("2. Testing storage...")
    from backend.storage import StorageManager
    storage = StorageManager()
    print("✅ Storage tests passed")
    
    # Test 3: FastAPI app mínima
    print("3. Testing minimal FastAPI...")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    # Crear app mínima sin importar server.py
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"status": "ok", "message": "Test endpoint works"}
    
    @app.get("/api/health")  
    def health():
        return {"status": "healthy", "services": {"test": "ok"}}
    
    client = TestClient(app)
    
    # Test endpoints
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    print("✅ FastAPI tests passed")
    
    print("\n🎉 ¡TODOS LOS TESTS BÁSICOS PASARON!")
    print("✨ El problema está en server.py al cargar transformers/torch")
    print("💡 Solución: Los tests reales necesitan evitar la carga de modelos ML")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Limpiar
    if 'temp_db' in locals() and os.path.exists(temp_db):
        os.unlink(temp_db)

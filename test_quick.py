#!/usr/bin/env python3
"""Test rápido para verificar que el backend funciona sin cargar modelos pesados"""

import os
import sys
import tempfile
from pathlib import Path

# Configurar entorno para evitar cargas pesadas
os.environ['DISABLE_TRANSFORMERS_INIT'] = '1'
os.environ['TRANSFORMERS_PROVIDER'] = 'local'
os.environ['TRANSFORMERS_MODEL'] = 'gpt2'

# DB temporal
temp_db = tempfile.mktemp(suffix='.db')
os.environ['VEUPLUS_DB_PATH'] = temp_db

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

try:
    from fastapi.testclient import TestClient
    from backend.server import app
    
    client = TestClient(app)
    
    # Test health endpoint
    print("🔍 Testing /api/health...")
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    print("✅ Health check passed")
    
    # Test chatbots list (should be empty initially)
    print("🔍 Testing /api/chatbots...")
    response = client.get('/api/chatbots')
    assert response.status_code == 200
    data = response.json()
    assert 'bots' in data
    # Permitir que existan bots iniciales (p. ej., creados por pruebas previas o seed)
    assert isinstance(data['bots'], list)
    print("✅ Chatbots list passed (" + str(len(data['bots'])) + " bots)")
    
    # Test voices list
    print("🔍 Testing /api/voices...")
    response = client.get('/api/voices')
    assert response.status_code == 200
    data = response.json()
    assert 'voices' in data
    print("✅ Voices list passed")
    
    print("\n🎉 ¡Todos los tests básicos PASARON!")
    print("✨ El backend funciona correctamente sin modelos pesados")
    
except Exception as e:
    print(f"❌ Error en tests: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Limpiar DB temporal
    if os.path.exists(temp_db):
        os.unlink(temp_db)

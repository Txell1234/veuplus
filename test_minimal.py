#!/usr/bin/env python3
"""Test ultra-mínimo para diagnosticar el problema"""

print("🔍 Iniciando test mínimo...")

try:
    print("1. Importando os...")
    import os
    print("✅ os importado")
    
    print("2. Configurando variables de entorno...")
    os.environ['DISABLE_TRANSFORMERS_INIT'] = '1'
    os.environ['TRANSFORMERS_PROVIDER'] = 'local' 
    os.environ['TRANSFORMERS_MODEL'] = 'gpt2'
    print("✅ Variables configuradas")
    
    print("3. Importando sys...")
    import sys
    print("✅ sys importado")
    
    print("4. Añadiendo backend al path...")
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    print("✅ Path configurado")
    
    print("5. Importando FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI importado")
    
    print("6. Importando TestClient...")
    from fastapi.testclient import TestClient
    print("✅ TestClient importado")
    
    print("7. Intentando importar database_sql...")
    from backend.database_sql import VeuPlusDatabase
    print("✅ database_sql importado")
    
    print("8. Creando DB temporal...")
    import tempfile
    temp_db = tempfile.mktemp(suffix='.db')
    os.environ['VEUPLUS_DB_PATH'] = temp_db
    db = VeuPlusDatabase()
    print("✅ DB temporal creada")
    
    print("9. Importando server (ESTO PUEDE COLGAR)...")
    # Aquí es donde probablemente se cuelga
    import backend.server as server_module
    print("✅ server importado")
    
    print("10. Creando TestClient...")
    client = TestClient(server_module.app)
    print("✅ TestClient creado")
    
    print("11. Test health endpoint...")
    response = client.get('/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n🎉 ¡TEST MÍNIMO COMPLETADO!")
    
except Exception as e:
    print(f"❌ Error en paso: {e}")
    import traceback
    traceback.print_exc()

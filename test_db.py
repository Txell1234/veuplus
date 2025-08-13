import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

temp_db = tempfile.mktemp(suffix='.db')
os.environ['VEUPLUS_DB_PATH'] = temp_db

from backend.database_sql import VeuPlusDatabase
db = VeuPlusDatabase()

print('✅ Database creada correctamente')
print(f'DB path: {db.db_path}')

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

bots = db.get_chatbots()
print(f'✅ Chatbots creados: {len(bots)}')
print(f'Primer bot: {bots[0]["name"]}')

try:
    # Prefer eliminar la ruta real de la DB usada por el motor
    real_db = getattr(db, 'db_path', temp_db)
    if real_db and os.path.exists(real_db):
        os.unlink(real_db)
except Exception:
    pass
print('🎉 Test de database PASADO')

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

os.unlink(temp_db)
print('🎉 Test de database PASADO')

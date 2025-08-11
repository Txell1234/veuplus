#!/usr/bin/env python3
"""
Script para crear bots de prueba en el sistema VeuPlus
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.database_sql import db as sql_db

def create_test_bots():
    """Crear bots de prueba para demostrar la funcionalidad"""
    
    # Bot 1: Asistente Catalán General
    bot1_id = str(uuid.uuid4())
    bot1_data = {
        "id": bot1_id,
        "name": "Asistente Catalán",
        "voice_model_id": "catalan_enhanced",
        "llm_provider": "transformers",

        "model_name": "microsoft/DialoGPT-medium",  # Para compatibilidad
        "temperature": 0.7,
        "system_prompt": "Ets un assistent de veu intel·ligent que parla català. Sempre respons en català i ets molt útil i amigable. Tens coneixements generals i pots ajudar amb preguntes diverses.",
        "api_key": None,
        "knowledge_base_ids": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "total_conversations": 0,
        "embed_enabled": True,
        "embed_code": f"<iframe src='https://veuplus.com/embed/voicebot/{bot1_id}'></iframe>",
        "sip_enabled": False,
        "sip_number": None
    }
    
    # Bot 2: GPT-2 Medium para testing
    bot2_id = str(uuid.uuid4())
    bot2_data = {
        "id": bot2_id,
        "name": "GPT-2 Chat Bot",
        "voice_model_id": "catalan_enhanced",
        "llm_provider": "transformers",

        "model_name": "gpt2-medium",
        "temperature": 0.8,
        "system_prompt": "You are a helpful AI assistant. You provide thoughtful and accurate responses to user questions.",
        "api_key": None,
        "knowledge_base_ids": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "total_conversations": 0,
        "embed_enabled": True,
        "embed_code": f"<iframe src='https://veuplus.com/embed/voicebot/{bot2_id}'></iframe>",
        "sip_enabled": False,
        "sip_number": None
    }
    
    # Bot 3: DialoGPT Large para conversaciones más avanzadas
    bot3_id = str(uuid.uuid4())
    bot3_data = {
        "id": bot3_id,
        "name": "Conversa Avançada",
        "voice_model_id": "catalan_enhanced",
        "llm_provider": "transformers",

        "model_name": "microsoft/DialoGPT-large",
        "temperature": 0.6,
        "system_prompt": "Sóc un assistent especialitzat en converses fluides i naturals. Puc parlar de molts temes diferents i m'adapto al to de la conversa.",
        "api_key": None,
        "knowledge_base_ids": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "total_conversations": 0,
        "embed_enabled": True,
        "embed_code": f"<iframe src='https://veuplus.com/embed/voicebot/{bot3_id}'></iframe>",
        "sip_enabled": True,
        "sip_number": "+34600123456"
    }
    
    # Insertar bots en la base de datos
    bots = [bot1_data, bot2_data, bot3_data]
    
    for bot in bots:
        try:
            # Verificar si el bot ya existe
            existing = sql_db.execute_query("SELECT id FROM voicebots WHERE id = ?", (bot["id"],))
            if existing:
                print(f"⚠️ Bot '{bot['name']}' ya existe, actualizando...")
                # Actualizar bot existente
                sql_db.execute_query("""
                    UPDATE voicebots SET 
                        name = ?, model_name = ?, temperature = ?, system_prompt = ?, updated_at = ?
                    WHERE id = ?
                """, (bot["name"], bot["model_name"], bot["temperature"], bot["system_prompt"], 
                     datetime.now().isoformat(), bot["id"]))
            else:
                # Crear nuevo bot
                sql_db.execute_query("""
                    INSERT INTO voicebots (
                        id, name, voice_model_id, llm_provider, model_name,
                        temperature, system_prompt, api_key, knowledge_base_ids,
                        created_at, updated_at, status, total_conversations,
                        embed_enabled, embed_code, sip_enabled, sip_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bot["id"], bot["name"], bot["voice_model_id"], bot["llm_provider"],
                    bot["model_name"], bot["temperature"], 
                    bot["system_prompt"], bot["api_key"], bot["knowledge_base_ids"],
                    bot["created_at"], bot["updated_at"], bot["status"], 
                    bot["total_conversations"], bot["embed_enabled"], bot["embed_code"],
                    bot["sip_enabled"], bot["sip_number"]
                ))
                print(f"✅ Bot '{bot['name']}' creado con ID: {bot['id']}")
                
        except Exception as e:
            print(f"❌ Error creando bot '{bot['name']}': {e}")
    
    # Mostrar bots creados
    print("\n🤖 BOTS DISPONIBLES:")
    bots_list = sql_db.execute_query("SELECT id, name, model_name, status FROM voicebots")
    for bot in bots_list:
        print(f"  - {bot['name']} (ID: {bot['id'][:8]}...) - Modelo: {bot['model_name']} - Estado: {bot['status']}")
    
    return True

if __name__ == "__main__":
    print("🚀 Creando bots de prueba para VeuPlus...")
    try:
        success = create_test_bots()
        if success:
            print("\n✅ ¡Bots de prueba creados exitosamente!")
            print("Ahora puedes probar los bots desde el frontend en http://localhost:3000")
        else:
            print("\n❌ Error creando los bots de prueba")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

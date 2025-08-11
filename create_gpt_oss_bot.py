#!/usr/bin/env python3
"""
Script para crear un bot con el modelo openai/gpt-oss-20b
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.database_sql import db as sql_db

def create_gpt_oss_bot():
    """Crear un bot con el modelo openai/gpt-oss-20b"""
    
    # Bot con GPT-OSS-20B
    bot_id = str(uuid.uuid4())
    bot_data = {
        "id": bot_id,
        "name": "GPT-OSS-20B PowerBot",
        "voice_model_id": "catalan_enhanced",
        "llm_provider": "transformers",
        "model_name": "openai/gpt-oss-20b",
        "temperature": 0.7,
        "system_prompt": "You are a powerful AI assistant powered by the OpenAI GPT-OSS-20B model. You provide intelligent, thoughtful, and comprehensive responses to user questions. You can handle complex topics and maintain engaging conversations.",
        "api_key": None,
        "knowledge_base_ids": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "total_conversations": 0,
        "embed_enabled": True,
        "embed_code": f"<iframe src='https://veuplus.com/embed/voicebot/{bot_id}'></iframe>",
        "sip_enabled": True,
        "sip_number": "+34600789012"
    }
    
    try:
        # Verificar si ya existe un bot con este modelo
        existing = sql_db.execute_query("SELECT id FROM voicebots WHERE model_name = ?", ("openai/gpt-oss-20b",))
        if existing:
            print(f"⚠️ Ya existe un bot con modelo GPT-OSS-20B, actualizando...")
            # Actualizar bot existente
            sql_db.execute_query("""
                UPDATE voicebots SET 
                    name = ?, temperature = ?, system_prompt = ?, updated_at = ?
                WHERE model_name = ?
            """, (bot_data["name"], bot_data["temperature"], bot_data["system_prompt"], 
                 datetime.now().isoformat(), "openai/gpt-oss-20b"))
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
                bot_data["id"], bot_data["name"], bot_data["voice_model_id"], bot_data["llm_provider"],
                bot_data["model_name"], bot_data["temperature"], 
                bot_data["system_prompt"], bot_data["api_key"], bot_data["knowledge_base_ids"],
                bot_data["created_at"], bot_data["updated_at"], bot_data["status"], 
                bot_data["total_conversations"], bot_data["embed_enabled"], bot_data["embed_code"],
                bot_data["sip_enabled"], bot_data["sip_number"]
            ))
            print(f"✅ Bot '{bot_data['name']}' creado con ID: {bot_data['id']}")
            
    except Exception as e:
        print(f"❌ Error creando bot GPT-OSS-20B: {e}")
        return False
    
    # Mostrar bots con GPT-OSS-20B
    print(f"\n🤖 BOTS CON GPT-OSS-20B:")
    bots_list = sql_db.execute_query("SELECT id, name, model_name, status FROM voicebots WHERE model_name = ?", ("openai/gpt-oss-20b",))
    for bot in bots_list:
        print(f"  - {bot['name']} (ID: {bot['id'][:8]}...) - Modelo: {bot['model_name']} - Estado: {bot['status']}")
    
    return True

if __name__ == "__main__":
    print("🚀 Creando bot con GPT-OSS-20B...")
    try:
        success = create_gpt_oss_bot()
        if success:
            print("\n✅ ¡Bot GPT-OSS-20B creado exitosamente!")
            print("Ahora puedes usar el modelo más potente desde el frontend")
        else:
            print("\n❌ Error creando el bot GPT-OSS-20B")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


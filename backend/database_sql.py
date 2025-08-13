# SQL Database Integration for VeuPlus
import sqlite3
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

# Setup logging
logger = logging.getLogger(__name__)

# Database path strategy (server-only; no frontend access)
# Priority:
# 1) VEUPLUS_DB_PATH env var
# 2) /data/veuplus.db (Docker volume)
# 3) /backend/veuplus.db or /app/backend/veuplus.db (container)
# 4) Local file next to this module
import os

env_db_path = os.environ.get("VEUPLUS_DB_PATH")
if env_db_path:
    DB_PATH = Path(env_db_path)
elif Path("/data").exists():
    DB_PATH = Path("/data/veuplus.db")
elif Path("/backend").exists():
    DB_PATH = Path("/backend/veuplus.db")
elif Path("/app/backend").exists():
    DB_PATH = Path("/app/backend/veuplus.db")
else:
    DB_PATH = Path(__file__).parent / "veuplus.db"

class VeuPlusDatabase:
    """SQL Database manager for VeuPlus platform"""
    
    def __init__(self):
        self.db_path = DB_PATH
        # Ensure the directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Voice Models Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    dialect TEXT,
                    status TEXT DEFAULT 'ready',
                    progress INTEGER DEFAULT 100,
                    quality TEXT DEFAULT 'enhanced',
                    real_model BOOLEAN DEFAULT TRUE,
                    model_path TEXT,
                    sample_audio TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    config TEXT,
                    training_duration TEXT,
                    description TEXT
                )
            """)
            
            # Chatbots Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chatbots (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    llm_provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    temperature REAL DEFAULT 0.7,
                    system_prompt TEXT,
                    api_key TEXT,
                    knowledge_base_ids TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    status TEXT DEFAULT 'active',
                    total_conversations INTEGER DEFAULT 0,
                    embed_enabled BOOLEAN DEFAULT TRUE,
                    embed_code TEXT,
                    sip_enabled BOOLEAN DEFAULT FALSE,
                    sip_number TEXT
                )
            """)

            # Lightweight migrations for existing databases
            # Ensure "assistant_id" column exists in chatbots table to satisfy tests and server logic
            try:
                cursor.execute("PRAGMA table_info(chatbots)")
                cols = {row[1] for row in cursor.fetchall()}  # set of column names
                if "assistant_id" not in cols:
                    cursor.execute("ALTER TABLE chatbots ADD COLUMN assistant_id TEXT")
            except Exception as _e:
                logger.warning(f"Could not ensure assistant_id column on chatbots: {_e}")
            
            # Voicebots Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voicebots (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    voice_model_id TEXT NOT NULL,
                    llm_provider TEXT NOT NULL DEFAULT 'transformers',
                    llm_model TEXT NOT NULL DEFAULT 'microsoft/DialoGPT-medium',
                    model_name TEXT NOT NULL,
                    temperature REAL DEFAULT 0.7,
                    system_prompt TEXT,
                    api_key TEXT,
                    knowledge_base_ids TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    status TEXT DEFAULT 'active',
                    total_conversations INTEGER DEFAULT 0,
                    embed_enabled BOOLEAN DEFAULT TRUE,
                    embed_code TEXT,
                    sip_enabled BOOLEAN DEFAULT FALSE,
                    sip_number TEXT,
                    FOREIGN KEY (voice_model_id) REFERENCES voice_models (id)
                )
            """)
            
            # Knowledge Base Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_url TEXT,
                    file_path TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    file_size INTEGER,
                    content_hash TEXT
                )
            """)
            
            # Training Jobs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_jobs (
                    job_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    dialect TEXT,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    epoch INTEGER DEFAULT 0,
                    loss REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    model_path TEXT,
                    error_message TEXT,
                    gpu_utilization REAL DEFAULT 0.0,
                    use_catalan_dataset BOOLEAN DEFAULT TRUE,
                    custom_audio_files TEXT,
                    training_config TEXT
                )
            """)
            
            # API Keys Table (for developer dashboard)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    permissions TEXT,
                    created_at TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    rate_limit INTEGER DEFAULT 1000,
                    monthly_quota INTEGER DEFAULT 100000
                )
            """)
            
            # API Usage Table (for analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT,
                    endpoint TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data_size_mb REAL DEFAULT 0,
                    success BOOLEAN DEFAULT TRUE,
                    response_time_ms INTEGER,
                    user_agent TEXT,
                    ip_address TEXT
                )
            """)
            
            # Bot Embeddings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_embeddings (
                    id TEXT PRIMARY KEY,
                    bot_id TEXT NOT NULL,
                    bot_type TEXT NOT NULL,
                    embed_type TEXT NOT NULL,
                    theme TEXT DEFAULT 'veuplus',
                    size TEXT DEFAULT 'medium',
                    position TEXT DEFAULT 'bottom-right',
                    custom_css TEXT,
                    domain_whitelist TEXT,
                    created_at TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT
                )
            """)
            
            # SIP Integration Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sip_integrations (
                    id TEXT PRIMARY KEY,
                    bot_id TEXT NOT NULL,
                    bot_type TEXT NOT NULL,
                    sip_provider TEXT NOT NULL,
                    sip_number TEXT NOT NULL,
                    sip_config TEXT,
                    webhook_url TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    total_calls INTEGER DEFAULT 0,
                    total_minutes REAL DEFAULT 0.0
                )
            """)
            
            conn.commit()
            logger.info("Database initialized with all tables")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_insert(self, table: str, data: Dict[str, Any]) -> str:
        """Execute INSERT query"""
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return data.get('id', cursor.lastrowid)
    
    def execute_update(self, table: str, data: Dict[str, Any], where_clause: str, where_params: tuple = ()) -> int:
        """Execute UPDATE query"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + list(where_params)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount
    
    def execute_delete(self, table: str, where_clause: str, where_params: tuple = ()) -> int:
        """Execute DELETE query"""
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, where_params)
            conn.commit()
            return cursor.rowcount
    
    # Voice Models Methods
    def create_voice_model(self, voice_data: Dict[str, Any]) -> str:
        """Create new voice model"""
        voice_data['created_at'] = datetime.now().isoformat()
        if 'config' in voice_data and isinstance(voice_data['config'], dict):
            voice_data['config'] = json.dumps(voice_data['config'])
        return self.execute_insert('voice_models', voice_data)
    
    def get_voice_models(self) -> List[Dict[str, Any]]:
        """Get all voice models"""
        models = self.execute_query("SELECT * FROM voice_models ORDER BY created_at DESC")
        for model in models:
            if model.get('config'):
                try:
                    model['config'] = json.loads(model['config'])
                except:
                    model['config'] = {}
        return models
    
    def get_voice_model(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Get voice model by ID"""
        models = self.execute_query("SELECT * FROM voice_models WHERE id = ?", (voice_id,))
        if models:
            model = models[0]
            if model.get('config'):
                try:
                    model['config'] = json.loads(model['config'])
                except:
                    model['config'] = {}
            return model
        return None
    
    def update_voice_model(self, voice_id: str, updates: Dict[str, Any]) -> bool:
        """Update voice model"""
        updates['updated_at'] = datetime.now().isoformat()
        if 'config' in updates and isinstance(updates['config'], dict):
            updates['config'] = json.dumps(updates['config'])
        return self.execute_update('voice_models', updates, 'id = ?', (voice_id,)) > 0
    
    def delete_voice_model(self, voice_id: str) -> bool:
        """Delete voice model"""
        return self.execute_delete('voice_models', 'id = ?', (voice_id,)) > 0
    
    # Chatbots Methods
    def create_chatbot(self, bot_data: Dict[str, Any]) -> str:
        """Create new chatbot"""
        bot_data['created_at'] = datetime.now().isoformat()
        if 'knowledge_base_ids' in bot_data and isinstance(bot_data['knowledge_base_ids'], list):
            bot_data['knowledge_base_ids'] = json.dumps(bot_data['knowledge_base_ids'])
        
        # Generate embed code
        bot_id = bot_data.get('id', str(uuid.uuid4()))
        bot_data['id'] = bot_id
        bot_data['embed_code'] = self.generate_embed_code(bot_id, 'chatbot')
        
        return self.execute_insert('chatbots', bot_data)
    
    def get_chatbots(self) -> List[Dict[str, Any]]:
        """Get all chatbots"""
        bots = self.execute_query("SELECT * FROM chatbots ORDER BY created_at DESC")
        for bot in bots:
            if bot.get('knowledge_base_ids'):
                try:
                    bot['knowledge_base_ids'] = json.loads(bot['knowledge_base_ids'])
                except:
                    bot['knowledge_base_ids'] = []
        return bots
    
    def get_chatbot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get chatbot by ID"""
        bots = self.execute_query("SELECT * FROM chatbots WHERE id = ?", (bot_id,))
        if bots:
            bot = bots[0]
            if bot.get('knowledge_base_ids'):
                try:
                    bot['knowledge_base_ids'] = json.loads(bot['knowledge_base_ids'])
                except:
                    bot['knowledge_base_ids'] = []
            return bot
        return None
    
    # Voicebots Methods
    def create_voicebot(self, bot_data: Dict[str, Any]) -> str:
        """Create new voicebot"""
        bot_data['created_at'] = datetime.now().isoformat()
        if 'knowledge_base_ids' in bot_data and isinstance(bot_data['knowledge_base_ids'], list):
            bot_data['knowledge_base_ids'] = json.dumps(bot_data['knowledge_base_ids'])
        
        # Generate embed code
        bot_id = bot_data.get('id', str(uuid.uuid4()))
        bot_data['id'] = bot_id
        bot_data['embed_code'] = self.generate_embed_code(bot_id, 'voicebot')
        
        return self.execute_insert('voicebots', bot_data)
    
    def get_voicebots(self) -> List[Dict[str, Any]]:
        """Get all voicebots"""
        bots = self.execute_query("SELECT * FROM voicebots ORDER BY created_at DESC")
        for bot in bots:
            if bot.get('knowledge_base_ids'):
                try:
                    bot['knowledge_base_ids'] = json.loads(bot['knowledge_base_ids'])
                except:
                    bot['knowledge_base_ids'] = []
        return bots
    
    def get_voicebot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get voicebot by ID"""
        bots = self.execute_query("SELECT * FROM voicebots WHERE id = ?", (bot_id,))
        if bots:
            bot = bots[0]
            if bot.get('knowledge_base_ids'):
                try:
                    bot['knowledge_base_ids'] = json.loads(bot['knowledge_base_ids'])
                except:
                    bot['knowledge_base_ids'] = []
            return bot
        return None
    
    # Knowledge Base Methods
    def create_knowledge_item(self, kb_data: Dict[str, Any]) -> str:
        """Create knowledge base item"""
        kb_data['created_at'] = datetime.now().isoformat()
        return self.execute_insert('knowledge_base', kb_data)
    
    def get_knowledge_base(self) -> List[Dict[str, Any]]:
        """Get all knowledge base items"""
        return self.execute_query("SELECT * FROM knowledge_base ORDER BY created_at DESC")
    
    # Embed Code Generation
    def generate_embed_code(self, bot_id: str, bot_type: str) -> str:
        """Generate embed code for bot"""
        domain = "veuplus.com"  # Replace with your actual domain
        
        embed_code = f"""
<!-- VeuPlus {bot_type.title()} Embed -->
<div id="veuplus-{bot_type}-{bot_id}"></div>
<script>
(function() {{
    var script = document.createElement('script');
    script.src = 'https://{domain}/embed/veuplus-{bot_type}.js';
    script.setAttribute('data-bot-id', '{bot_id}');
    script.setAttribute('data-bot-type', '{bot_type}');
    document.body.appendChild(script);
}})();
</script>
        """.strip()
        
        return embed_code
    
    # SIP Integration Methods
    def create_sip_integration(self, sip_data: Dict[str, Any]) -> str:
        """Create SIP integration"""
        sip_data['created_at'] = datetime.now().isoformat()
        if 'sip_config' in sip_data and isinstance(sip_data['sip_config'], dict):
            sip_data['sip_config'] = json.dumps(sip_data['sip_config'])
        return self.execute_insert('sip_integrations', sip_data)
    
    def get_sip_integrations(self, bot_id: str = None) -> List[Dict[str, Any]]:
        """Get SIP integrations"""
        if bot_id:
            integrations = self.execute_query("SELECT * FROM sip_integrations WHERE bot_id = ?", (bot_id,))
        else:
            integrations = self.execute_query("SELECT * FROM sip_integrations ORDER BY created_at DESC")
        
        for integration in integrations:
            if integration.get('sip_config'):
                try:
                    integration['sip_config'] = json.loads(integration['sip_config'])
                except:
                    integration['sip_config'] = {}
        return integrations
    
    # Analytics Methods
    def log_api_usage(self, usage_data: Dict[str, Any]) -> None:
        """Log API usage for analytics"""
        usage_data['timestamp'] = datetime.now().isoformat()
        self.execute_insert('api_usage', usage_data)
    
    def get_usage_analytics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get usage analytics"""
        where_clause = "1=1"
        params = []
        
        if start_date:
            where_clause += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND timestamp <= ?"
            params.append(end_date)
        
        # Total requests
        total_requests = self.execute_query(
            f"SELECT COUNT(*) as count FROM api_usage WHERE {where_clause}", 
            tuple(params)
        )[0]['count']
        
        # Requests by endpoint
        endpoint_stats = self.execute_query(f"""
            SELECT endpoint, COUNT(*) as count, AVG(response_time_ms) as avg_response_time
            FROM api_usage 
            WHERE {where_clause}
            GROUP BY endpoint
            ORDER BY count DESC
        """, tuple(params))
        
        return {
            'total_requests': total_requests,
            'endpoint_statistics': endpoint_stats,
            'period': f"{start_date} to {end_date}" if start_date and end_date else "all time"
        }

# Global database instance
db = VeuPlusDatabase()
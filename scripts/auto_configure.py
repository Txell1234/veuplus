#!/usr/bin/env python3
"""
Script de configuració automàtica VeuPlus
Configura agents ConvHi, widgets i SIP trunk automàticament
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

class VeuPlusConfigurator:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.api_key = None
        self.agents_created = []
        
    def check_server(self):
        """Verificar que el servidor està funcionant"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor VeuPlus funcionant")
                return True
            else:
                print(f"❌ Servidor respon amb codi {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ No es pot connectar al servidor: {e}")
            print("💡 Assegura't que el servidor està executant-se:")
            print("   cd backend && python server.py")
            return False
    
    def check_api_keys(self):
        """Verificar API keys configurades"""
        print("\n🔑 Verificant API keys...")
        
        api_keys = {
            "OpenAI": os.environ.get('OPENAI_API_KEY'),
            "Gemini": os.environ.get('GEMINI_API_KEY'),
            "Anthropic": os.environ.get('ANTHROPIC_API_KEY')
        }
        
        configured = []
        for provider, key in api_keys.items():
            if key:
                print(f"✅ {provider}: Configurat")
                configured.append(provider.lower())
            else:
                print(f"❌ {provider}: No configurat")
        
        if not configured:
            print("\n⚠️  No hi ha API keys configurades!")
            print("💡 Configura almenys una API key al fitxer .env:")
            print("   OPENAI_API_KEY=sk-tu-clau-aqui")
            return False
        
        # Seleccionar el primer proveïdor configurat
        self.api_key = api_keys[configured[0].title()]
        self.llm_provider = configured[0]
        print(f"\n🎯 Utilitzant {configured[0].title()} com a proveïdor LLM")
        return True
    
    def create_default_agents(self):
        """Crear agents ConvHi per defecte"""
        print("\n🤖 Creant agents ConvHi...")
        
        default_agents = [
            {
                "name": "Agent Assistència",
                "description": "Agent d'assistència general en català",
                "llm_provider": self.llm_provider,
                "llm_model": self.get_default_model(),
                "voice_system": "edge-tts",
                "voice_id": "ca-ES-AlbaNeural",
                "language": "ca",
                "temperature": 0.7,
                "max_tokens": 1000,
                "knowledge_base_enabled": True,
                "rag_enabled": True
            },
            {
                "name": "Agent Ventes",
                "description": "Agent especialitzat en vendes i atenció al client",
                "llm_provider": self.llm_provider,
                "llm_model": self.get_default_model(),
                "voice_system": "edge-tts",
                "voice_id": "ca-ES-JoanaNeural",
                "language": "ca",
                "temperature": 0.8,
                "max_tokens": 1000,
                "knowledge_base_enabled": True,
                "rag_enabled": True
            },
            {
                "name": "Agent Suport Tècnic",
                "description": "Agent d'assistència tècnica i resolució de problemes",
                "llm_provider": self.llm_provider,
                "llm_model": self.get_default_model(),
                "voice_system": "edge-tts",
                "voice_id": "ca-ES-AlbaNeural",
                "language": "ca",
                "temperature": 0.6,
                "max_tokens": 1500,
                "knowledge_base_enabled": True,
                "rag_enabled": True
            }
        ]
        
        for agent_data in default_agents:
            try:
                response = requests.post(
                    f"{self.base_url}/api/convhi/agents",
                    json=agent_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    agent_id = result.get('agent', {}).get('id', 'unknown')
                    self.agents_created.append(agent_id)
                    print(f"✅ Agent creat: {agent_data['name']} (ID: {agent_id})")
                else:
                    print(f"❌ Error creant agent {agent_data['name']}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de connexió creant agent {agent_data['name']}: {e}")
        
        if self.agents_created:
            print(f"\n🎉 {len(self.agents_created)} agents creats correctament")
            return True
        else:
            print("\n❌ No s'han pogut crear agents")
            return False
    
    def get_default_model(self):
        """Obtenir model per defecte segons el proveïdor"""
        models = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-1.5-flash",
            "anthropic": "claude-3-5-sonnet-20241022"
        }
        return models.get(self.llm_provider, "gpt-4o-mini")
    
    def configure_widgets(self):
        """Configurar widgets per als agents creats"""
        print("\n🌐 Configurant widgets...")
        
        for agent_id in self.agents_created:
            try:
                # Crear configuració de widget
                widget_config = {
                    "agent_id": agent_id,
                    "variant": "compact",
                    "mode": "voice_text",
                    "primary_color": "#3B82F6",
                    "secondary_color": "#1E40AF",
                    "action_text": "Necessites ajuda?",
                    "start_call_text": "Començar conversa",
                    "end_call_text": "Finalitzar trucada",
                    "feedback_enabled": True,
                    "mute_enabled": True
                }
                
                response = requests.post(
                    f"{self.base_url}/api/convhi/widgets/config",
                    json=widget_config,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Widget configurat per agent {agent_id}")
                else:
                    print(f"❌ Error configurant widget per agent {agent_id}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de connexió configurant widget: {e}")
    
    def add_sample_knowledge(self):
        """Afegir coneixement de mostra"""
        print("\n📚 Afegint coneixement de mostra...")
        
        sample_knowledge = [
            {
                "title": "Informació de l'empresa",
                "content": "Som una empresa especialitzada en solucions d'intel·ligència artificial i automatització de processos. Ofereim serveis de chatbots, agents conversacionals i sistemes de veu.",
                "content_type": "text",
                "source_type": "manual"
            },
            {
                "title": "Horaris d'atenció",
                "content": "Els nostres horaris d'atenció al client són de dilluns a divendres de 9:00 a 18:00. Els caps de setmana i festius no oferim atenció presencial.",
                "content_type": "text",
                "source_type": "manual"
            },
            {
                "title": "Contacte",
                "content": "Pots contactar amb nosaltres al telèfon +34 900 123 456 o per email a info@empresa.com. També pots utilitzar el nostre sistema de tickets online.",
                "content_type": "text",
                "source_type": "manual"
            }
        ]
        
        for agent_id in self.agents_created:
            for knowledge_item in sample_knowledge:
                try:
                    knowledge_item["agent_id"] = agent_id
                    
                    response = requests.post(
                        f"{self.base_url}/api/convhi/knowledge/items",
                        json=knowledge_item,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Coneixement afegit per agent {agent_id}: {knowledge_item['title']}")
                    else:
                        print(f"❌ Error afegint coneixement: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Error de connexió afegint coneixement: {e}")
    
    def test_functionality(self):
        """Provar funcionalitat dels agents"""
        print("\n🧪 Provant funcionalitat...")
        
        if not self.agents_created:
            print("❌ No hi ha agents per provar")
            return False
        
        agent_id = self.agents_created[0]
        
        try:
            # Provar conversa amb l'agent
            test_message = {
                "agent_id": agent_id,
                "message": "Hola, com estàs?",
                "message_type": "text"
            }
            
            response = requests.post(
                f"{self.base_url}/api/convhi/agents/{agent_id}/chat",
                json=test_message,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Agent respon correctament")
                    print(f"📝 Resposta: {result.get('response', {}).get('text', 'No text')[:100]}...")
                    return True
                else:
                    print(f"❌ Agent no respon correctament: {result}")
                    return False
            else:
                print(f"❌ Error en la conversa: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de connexió provant agent: {e}")
            return False
    
    def generate_widget_code(self):
        """Generar codi HTML per als widgets"""
        print("\n📝 Generant codi HTML per widgets...")
        
        if not self.agents_created:
            print("❌ No hi ha agents per generar widgets")
            return
        
        agent_id = self.agents_created[0]
        
        html_code = f"""
<!-- VeuPlus ConvHi Widget -->
<veuplus-convhi 
  agent-id="{agent_id}"
  variant="compact"
  mode="voice_text"
  primary-color="#3B82F6"
  secondary-color="#1E40AF"
  action-text="Necessites ajuda?"
  start-call-text="Començar conversa"
  end-call-text="Finalitzar trucada"
></veuplus-convhi>

<script src="{self.base_url}/static/convhi-widget.js" async></script>
<!-- End VeuPlus ConvHi Widget -->
"""
        
        # Guardar codi en fitxer
        widget_file = Path("widget_code.html")
        widget_file.write_text(html_code, encoding='utf-8')
        
        print(f"✅ Codi HTML generat en: {widget_file.absolute()}")
        print("\n📋 Codi HTML:")
        print(html_code)
    
    def run_full_configuration(self):
        """Executar configuració completa"""
        print("🚀 INICIANT CONFIGURACIÓ COMPLETA VEUPLUS")
        print("=" * 50)
        
        steps = [
            ("Verificar servidor", self.check_server),
            ("Verificar API keys", self.check_api_keys),
            ("Crear agents", self.create_default_agents),
            ("Configurar widgets", self.configure_widgets),
            ("Afegir coneixement", self.add_sample_knowledge),
            ("Provar funcionalitat", self.test_functionality),
            ("Generar codi widget", self.generate_widget_code)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                success = step_func()
                if not success and step_name in ["Verificar servidor", "Verificar API keys", "Crear agents"]:
                    print(f"\n❌ CONFIGURACIÓ ATURADA: {step_name} ha fallat")
                    return False
            except Exception as e:
                print(f"❌ Error en {step_name}: {e}")
                if step_name in ["Verificar servidor", "Verificar API keys", "Crear agents"]:
                    return False
        
        print("\n" + "=" * 50)
        print("🎉 CONFIGURACIÓ COMPLETA EXITOSA!")
        print("=" * 50)
        
        print(f"\n📊 RESUM:")
        print(f"   • Agents creats: {len(self.agents_created)}")
        print(f"   • Proveïdor LLM: {self.llm_provider.title()}")
        print(f"   • Widgets configurats: {len(self.agents_created)}")
        
        print(f"\n🔗 ENLLAÇOS ÚTILS:")
        print(f"   • API Health: {self.base_url}/api/health")
        print(f"   • Agents: {self.base_url}/api/convhi/agents")
        print(f"   • Widget JS: {self.base_url}/static/convhi-widget.js")
        
        print(f"\n📝 PRÒXIMS PASSOS:")
        print(f"   1. Obrir widget_code.html per provar el widget")
        print(f"   2. Configurar SIP trunk (opcional)")
        print(f"   3. Personalitzar agents segons necessitats")
        
        return True

def main():
    """Funció principal"""
    print("VeuPlus Auto-Configurator v1.0")
    print("Configuració automàtica del sistema VeuPlus")
    
    # Verificar arguments
    base_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 Servidor objectiu: {base_url}")
    
    # Executar configuració
    configurator = VeuPlusConfigurator(base_url)
    success = configurator.run_full_configuration()
    
    if success:
        print("\n✅ Configuració completada amb èxit!")
        sys.exit(0)
    else:
        print("\n❌ Configuració fallida!")
        sys.exit(1)

if __name__ == "__main__":
    main()

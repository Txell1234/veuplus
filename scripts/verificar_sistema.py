#!/usr/bin/env python3
"""
Script de verificació del sistema VeuPlus
Verifica que tot estigui configurat correctament per funcionar
"""

import os
import sys
import requests
import json
from pathlib import Path

class VeuPlusVerifier:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.issues = []
        self.warnings = []
        
    def check_env_file(self):
        """Verificar fitxer .env"""
        print("🔍 Verificant fitxer .env...")
        
        env_file = Path(".env")
        if not env_file.exists():
            self.issues.append("❌ Fitxer .env no trobat")
            print("❌ Fitxer .env no trobat")
            print("💡 Copia config.example.env com .env i configura les API keys")
            return False
        
        print("✅ Fitxer .env trobat")
        
        # Verificar API keys
        api_keys = {
            "OpenAI": os.environ.get('OPENAI_API_KEY'),
            "Gemini": os.environ.get('GEMINI_API_KEY'),
            "Anthropic": os.environ.get('ANTHROPIC_API_KEY')
        }
        
        configured_keys = [provider for provider, key in api_keys.items() if key]
        
        if not configured_keys:
            self.issues.append("❌ No hi ha API keys configurades")
            print("❌ No hi ha API keys configurades")
            return False
        
        print(f"✅ API keys configurades: {', '.join(configured_keys)}")
        return True
    
    def check_server_running(self):
        """Verificar que el servidor està funcionant"""
        print("🔍 Verificant servidor VeuPlus...")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor VeuPlus funcionant")
                return True
            else:
                self.issues.append(f"❌ Servidor respon amb codi {response.status_code}")
                print(f"❌ Servidor respon amb codi {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.issues.append("❌ Servidor VeuPlus no disponible")
            print("❌ Servidor VeuPlus no disponible")
            print("💡 Executa: cd backend && python server.py")
            return False
    
    def check_convhi_agents(self):
        """Verificar agents ConvHi"""
        print("🔍 Verificant agents ConvHi...")
        
        try:
            response = requests.get(f"{self.base_url}/api/convhi/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                
                if agents:
                    print(f"✅ {len(agents)} agents ConvHi disponibles")
                    for agent in agents:
                        print(f"   • {agent.get('name', 'Unknown')} (ID: {agent.get('id', 'Unknown')})")
                    return True
                else:
                    self.warnings.append("⚠️  No hi ha agents ConvHi creats")
                    print("⚠️  No hi ha agents ConvHi creats")
                    print("💡 Executa: python scripts/crear_agents_prova.py")
                    return False
            else:
                self.issues.append("❌ Error obtenint agents ConvHi")
                print(f"❌ Error obtenint agents ConvHi: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.issues.append("❌ Error de connexió amb API agents")
            print(f"❌ Error de connexió: {e}")
            return False
    
    def check_widget_system(self):
        """Verificar sistema de widgets"""
        print("🔍 Verificant sistema de widgets...")
        
        try:
            response = requests.get(f"{self.base_url}/static/convhi-widget.js", timeout=10)
            if response.status_code == 200:
                print("✅ Widget JavaScript disponible")
                return True
            else:
                self.issues.append("❌ Widget JavaScript no disponible")
                print(f"❌ Widget JavaScript no disponible: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.issues.append("❌ Error accedint al widget")
            print(f"❌ Error accedint al widget: {e}")
            return False
    
    def check_llm_integration(self):
        """Verificar integració LLM"""
        print("🔍 Verificant integració LLM...")
        
        try:
            response = requests.get(f"{self.base_url}/api/llm/providers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                providers = data.get('providers', {})
                
                if providers:
                    print("✅ Proveïdors LLM disponibles:")
                    for provider, config in providers.items():
                        status = "✅" if config.get('available') else "❌"
                        print(f"   {status} {provider}: {config.get('name', 'Unknown')}")
                    return True
                else:
                    self.issues.append("❌ No hi ha proveïdors LLM disponibles")
                    print("❌ No hi ha proveïdors LLM disponibles")
                    return False
            else:
                self.issues.append("❌ Error obtenint proveïdors LLM")
                print(f"❌ Error obtenint proveïdors LLM: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.issues.append("❌ Error de connexió amb API LLM")
            print(f"❌ Error de connexió: {e}")
            return False
    
    def test_agent_conversation(self):
        """Provar conversa amb agent"""
        print("🔍 Provant conversa amb agent...")
        
        try:
            # Obtenir agents
            response = requests.get(f"{self.base_url}/api/convhi/agents", timeout=10)
            if response.status_code != 200:
                self.warnings.append("⚠️  No es pot provar conversa (no hi ha agents)")
                return False
            
            agents = response.json().get('agents', [])
            if not agents:
                self.warnings.append("⚠️  No es pot provar conversa (no hi ha agents)")
                return False
            
            agent_id = agents[0]['id']
            
            # Provar conversa
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
                    resposta = result.get('response', {}).get('text', 'No text')
                    print(f"📝 Resposta: {resposta[:100]}...")
                    return True
                else:
                    self.issues.append("❌ Agent no respon correctament")
                    print("❌ Agent no respon correctament")
                    return False
            else:
                self.issues.append("❌ Error en conversa amb agent")
                print(f"❌ Error en conversa: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.issues.append("❌ Error de connexió provant agent")
            print(f"❌ Error de connexió: {e}")
            return False
    
    def check_sip_configuration(self):
        """Verificar configuració SIP"""
        print("🔍 Verificant configuració SIP...")
        
        asterisk_config = Path("asterisk_config")
        if not asterisk_config.exists():
            self.warnings.append("⚠️  Directori asterisk_config no trobat")
            print("⚠️  Directori asterisk_config no trobat")
            return False
        
        extensions_conf = asterisk_config / "extensions.conf"
        if not extensions_conf.exists():
            self.warnings.append("⚠️  Fitxer extensions.conf no trobat")
            print("⚠️  Fitxer extensions.conf no trobat")
            return False
        
        print("✅ Configuració SIP trobada")
        return True
    
    def generate_report(self):
        """Generar informe de verificació"""
        print("\n" + "=" * 50)
        print("📊 INFORME DE VERIFICACIÓ VEUPLUS")
        print("=" * 50)
        
        if not self.issues and not self.warnings:
            print("🎉 SISTEMA COMPLETAMENT FUNCIONAL!")
            print("✅ Tot està configurat correctament")
            print("\n🔗 Enllaços útils:")
            print(f"   • API Health: {self.base_url}/api/health")
            print(f"   • Agents: {self.base_url}/api/convhi/agents")
            print(f"   • Widget JS: {self.base_url}/static/convhi-widget.js")
            print(f"   • Documentació: {self.base_url}/docs")
            
        else:
            if self.issues:
                print("❌ PROBLEMES CRÍTICS:")
                for issue in self.issues:
                    print(f"   {issue}")
            
            if self.warnings:
                print("\n⚠️  ADVERTÈNCIES:")
                for warning in self.warnings:
                    print(f"   {warning}")
            
            print("\n💡 SOLUCIONS:")
            if "Fitxer .env no trobat" in self.issues:
                print("   1. Copia config.example.env com .env")
                print("   2. Configura almenys una API key")
            
            if "Servidor VeuPlus no disponible" in self.issues:
                print("   1. Executa: cd backend && python server.py")
            
            if "No hi ha agents ConvHi creats" in self.warnings:
                print("   1. Executa: python scripts/crear_agents_prova.py")
            
            if "No hi ha API keys configurades" in self.issues:
                print("   1. Configura OPENAI_API_KEY al fitxer .env")
                print("   2. Obtenir clau: https://platform.openai.com/api-keys")
    
    def run_full_verification(self):
        """Executar verificació completa"""
        print("🔍 INICIANT VERIFICACIÓ COMPLETA VEUPLUS")
        print("=" * 50)
        
        checks = [
            ("Fitxer .env", self.check_env_file),
            ("Servidor VeuPlus", self.check_server_running),
            ("Agents ConvHi", self.check_convhi_agents),
            ("Sistema Widgets", self.check_widget_system),
            ("Integració LLM", self.check_llm_integration),
            ("Conversa Agent", self.test_agent_conversation),
            ("Configuració SIP", self.check_sip_configuration)
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔄 {check_name}...")
            try:
                check_func()
            except Exception as e:
                self.issues.append(f"❌ Error en {check_name}: {e}")
                print(f"❌ Error en {check_name}: {e}")
        
        self.generate_report()
        
        return len(self.issues) == 0

def main():
    """Funció principal"""
    print("VeuPlus System Verifier v1.0")
    print("Verificació completa del sistema VeuPlus")
    
    # Verificar arguments
    base_url = "http://localhost:8080"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 Servidor objectiu: {base_url}")
    
    # Executar verificació
    verifier = VeuPlusVerifier(base_url)
    success = verifier.run_full_verification()
    
    if success:
        print("\n✅ VERIFICACIÓ EXITOSA!")
        sys.exit(0)
    else:
        print("\n❌ VERIFICACIÓ FALLIDA!")
        print("💡 Revisa els problemes identificats i torna a executar")
        sys.exit(1)

if __name__ == "__main__":
    main()

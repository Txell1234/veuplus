#!/usr/bin/env python3
"""
Script per crear agents ConvHi de prova automàticament
Ús: python crear_agents_prova.py
"""

import requests
import json
import time
import sys

def crear_agents_prova():
    """Crear agents ConvHi de prova"""
    
    base_url = "http://localhost:8080"
    
    print("🤖 CREANT AGENTS CONVHI DE PROVA")
    print("=" * 40)
    
    # Verificar que el servidor està funcionant
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor no disponible")
            return False
    except:
        print("❌ No es pot connectar al servidor")
        print("💡 Assegura't que el servidor està executant-se:")
        print("   cd backend && python server.py")
        return False
    
    print("✅ Servidor disponible")
    
    # Agents de prova
    agents_prova = [
        {
            "name": "Agent Assistència Bàsica",
            "description": "Agent d'assistència general per proves",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
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
            "description": "Agent especialitzat en vendes",
            "llm_provider": "openai", 
            "llm_model": "gpt-4o-mini",
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
            "description": "Agent d'assistència tècnica",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini", 
            "voice_system": "edge-tts",
            "voice_id": "ca-ES-AlbaNeural",
            "language": "ca",
            "temperature": 0.6,
            "max_tokens": 1500,
            "knowledge_base_enabled": True,
            "rag_enabled": True
        }
    ]
    
    agents_creats = []
    
    for agent_data in agents_prova:
        print(f"\n🔄 Creant agent: {agent_data['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/convhi/agents",
                json=agent_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                agent_id = result.get('agent', {}).get('id', 'unknown')
                agents_creats.append({
                    'id': agent_id,
                    'name': agent_data['name'],
                    'description': agent_data['description']
                })
                print(f"✅ Agent creat: {agent_id}")
            else:
                print(f"❌ Error creant agent: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de connexió: {e}")
    
    if agents_creats:
        print(f"\n🎉 {len(agents_creats)} agents creats correctament")
        
        # Mostrar resum
        print("\n📋 AGENTS DISPONIBLES:")
        for agent in agents_creats:
            print(f"   • {agent['name']} (ID: {agent['id']})")
        
        # Provar el primer agent
        if agents_creats:
            print(f"\n🧪 Provant agent: {agents_creats[0]['name']}")
            provar_agent(agents_creats[0]['id'], base_url)
        
        # Generar codi HTML per widget
        generar_codi_widget(agents_creats[0]['id'], base_url)
        
        return True
    else:
        print("\n❌ No s'han pogut crear agents")
        return False

def provar_agent(agent_id, base_url):
    """Provar conversa amb un agent"""
    
    test_messages = [
        "Hola, com estàs?",
        "Què pots fer per mi?",
        "Explica'm què és VeuPlus"
    ]
    
    for message in test_messages:
        print(f"\n💬 Prova: {message}")
        
        try:
            response = requests.post(
                f"{base_url}/api/convhi/agents/{agent_id}/chat",
                json={
                    "agent_id": agent_id,
                    "message": message,
                    "message_type": "text"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    resposta = result.get('response', {}).get('text', 'No text')
                    print(f"🤖 Resposta: {resposta[:100]}...")
                else:
                    print(f"❌ Agent no respon: {result}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de connexió: {e}")
        
        time.sleep(1)  # Pausa entre proves

def generar_codi_widget(agent_id, base_url):
    """Generar codi HTML per widget"""
    
    print(f"\n📝 Generant codi HTML per widget...")
    
    html_code = f"""<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prova Widget VeuPlus</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .code-block {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3B82F6;
            font-family: monospace;
            white-space: pre-wrap;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Widget VeuPlus ConvHi</h1>
        
        <div class="info">
            <h3>✅ Agent configurat:</h3>
            <p><strong>ID:</strong> {agent_id}</p>
            <p><strong>URL:</strong> {base_url}</p>
        </div>
        
        <h3>📋 Codi HTML per incrustar:</h3>
        <div class="code-block"><!-- VeuPlus ConvHi Widget -->
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

<script src="{base_url}/static/convhi-widget.js" async></script>
<!-- End VeuPlus ConvHi Widget --></div>
        
        <h3>🧪 Prova del widget:</h3>
        <p>El widget apareixerà a la cantonada inferior dreta d'aquesta pàgina.</p>
        
        <!-- Widget real -->
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
        
        <script src="{base_url}/static/convhi-widget.js" async></script>
        
        <div class="info">
            <h3>🔗 Enllaços útils:</h3>
            <ul>
                <li><a href="{base_url}/api/convhi/agents" target="_blank">API Agents</a></li>
                <li><a href="{base_url}/api/health" target="_blank">API Health</a></li>
                <li><a href="{base_url}/docs" target="_blank">Documentació API</a></li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    # Guardar fitxer
    with open("widget_prova.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    
    print(f"✅ Codi HTML generat en: widget_prova.html")
    print(f"🌐 Obre widget_prova.html al navegador per provar el widget")

def main():
    """Funció principal"""
    
    print("VeuPlus - Creador d'Agents de Prova")
    print("====================================")
    
    success = crear_agents_prova()
    
    if success:
        print("\n🎉 CONFIGURACIÓ COMPLETA!")
        print("=" * 30)
        print("📋 Pròxims passos:")
        print("   1. Obre widget_prova.html al navegador")
        print("   2. Prova el widget a la cantonada inferior dreta")
        print("   3. Personalitza els agents segons necessitats")
        print("   4. Configura SIP trunk si cal")
    else:
        print("\n❌ CONFIGURACIÓ FALLIDA!")
        print("=" * 25)
        print("💡 Verifica que:")
        print("   1. El servidor VeuPlus està executant-se")
        print("   2. Les API keys estan configurades")
        print("   3. No hi ha errors al servidor")

if __name__ == "__main__":
    main()

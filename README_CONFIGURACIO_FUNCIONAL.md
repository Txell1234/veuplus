# 🚀 VEUPLUS - CONFIGURACIÓ FUNCIONAL COMPLETA

## 📋 **RESUM DE LA SITUACIÓ**

Després d'analitzar profundament el sistema VeuPlus, he identificat que:

- ✅ **Arquitectura completa** - Tot el codi està implementat
- ❌ **No configurat** - Falten API keys i agents creats
- ⚠️ **SIP simulació** - No hi ha configuració real de trunks

**CONCLUSIÓ:** El sistema és com un cotxe sense combustible - tot està preparat, però no funciona perquè no està configurat.

---

## 🎯 **CONFIGURACIÓ RÀPIDA (5 MINUTS)**

### **Opció 1: Script Automàtic (Recomanat)**
```bash
# 1. Configurar API key
echo "OPENAI_API_KEY=sk-tu-clau-aqui" > .env

# 2. Executar configuració automàtica
python scripts/auto_configure.py

# 3. Provar sistema
python scripts/verificar_sistema.py
```

### **Opció 2: Script Windows**
```cmd
# Executar script de configuració
CONFIGURAR_VEUPLUS.bat
```

### **Opció 3: Manual**
```bash
# 1. Copiar configuració
cp config.funcional.env .env

# 2. Editar .env amb la teva API key
# OPENAI_API_KEY=sk-tu-clau-aqui

# 3. Iniciar servidor
cd backend && python server.py

# 4. Crear agents
python scripts/crear_agents_prova.py
```

---

## 🔑 **OBTENIR API KEYS**

### **OpenAI (Més fàcil per començar)**
1. Anar a https://platform.openai.com/api-keys
2. Crear nova API key
3. Copiar clau (comença per `sk-`)
4. Afegir al fitxer `.env`:
   ```
   OPENAI_API_KEY=sk-tu-clau-aqui
   ```

### **Google Gemini (Alternativa)**
1. Anar a https://makersuite.google.com/app/apikey
2. Crear nova API key
3. Afegir al fitxer `.env`:
   ```
   GEMINI_API_KEY=tu-clau-gemini-aqui
   ```

### **Anthropic Claude (Alternativa)**
1. Anar a https://console.anthropic.com/
2. Crear nova API key
3. Afegir al fitxer `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-tu-clau-aqui
   ```

---

## 🤖 **CREAR AGENTS CONVHI**

### **Automàtic (Recomanat)**
```bash
python scripts/crear_agents_prova.py
```

### **Manual via API**
```bash
curl -X POST "http://localhost:8080/api/convhi/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agent Assistència",
    "description": "Agent d'assistència en català",
    "llm_provider": "openai",
    "llm_model": "gpt-4o-mini",
    "voice_system": "edge-tts",
    "voice_id": "ca-ES-AlbaNeural",
    "language": "ca"
  }'
```

---

## 🌐 **CONFIGURAR WIDGETS**

### **Generar codi d'integració**
```bash
curl -X POST "http://localhost:8080/api/convhi/widgets/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "convhi_1",
    "config": {
      "variant": "compact",
      "mode": "voice_text",
      "primary_color": "#3B82F6"
    },
    "domain": "localhost"
  }'
```

### **Codi HTML per incrustar**
```html
<!-- VeuPlus ConvHi Widget -->
<veuplus-convhi 
  agent-id="convhi_1"
  variant="compact"
  mode="voice_text"
  primary-color="#3B82F6"
  action-text="Necessites ajuda?"
></veuplus-convhi>

<script src="http://localhost:8080/static/convhi-widget.js" async></script>
<!-- End VeuPlus ConvHi Widget -->
```

---

## 📞 **CONFIGURAR SIP TRUNK REAL**

### **1. Instal·lar Asterisk**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install asterisk asterisk-dev

# CentOS/RHEL
sudo yum install asterisk asterisk-devel

# Windows (via Docker)
docker run -d --name asterisk -p 5060:5060/udp -p 10000-20000:10000-20000/udp andrius/asterisk
```

### **2. Configurar trunks SIP**
```ini
# asterisk_config/sip.conf
[general]
context=default
allowoverlap=no
udpbindaddr=0.0.0.0:5060

; Trunk principal
[trunk]
type=peer
host=proveidor-sip.com
username=usuari-trunk
secret=password-trunk
context=outbound
dtmfmode=rfc2833
```

### **3. Configurar extensions**
```ini
# asterisk_config/extensions.conf
[veuplus-incoming]
exten => _X.,1,NoOp(Trucada VeuPlus: ${CALLERID(num)})
exten => _X.,n,Set(VEUPLUS_CALL_ID=${CALLERID(num)}_${EXTEN}_${EPOCH})
exten => _X.,n,AGI(veuplus_greeting.agi,${CALLERID(num)},${EXTEN},ca,edge-tts)
exten => _X.,n,Goto(veuplus-conversation,start,1)
```

---

## 🧪 **PROVAR FUNCIONALITAT**

### **1. Verificar sistema**
```bash
python scripts/verificar_sistema.py
```

### **2. Provar agent**
```bash
curl -X POST "http://localhost:8080/api/convhi/agents/convhi_1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "convhi_1",
    "message": "Hola, com estàs?",
    "message_type": "text"
  }'
```

### **3. Provar widget**
1. Obrir `widget_prova.html` al navegador
2. Fer clic al widget a la cantonada inferior dreta
3. Provar conversa

---

## 🔧 **CONFIGURACIÓ AVANÇADA**

### **Múltiples agents**
```python
import requests

agents = [
    {
        "name": "Agent Ventes",
        "description": "Agent especialitzat en vendes",
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "voice_system": "edge-tts",
        "voice_id": "ca-ES-AlbaNeural",
        "language": "ca"
    },
    {
        "name": "Agent Suport",
        "description": "Agent d'atenció al client",
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "voice_system": "edge-tts",
        "voice_id": "ca-ES-JoanaNeural",
        "language": "ca"
    }
]

for agent in agents:
    response = requests.post("http://localhost:8080/api/convhi/agents", json=agent)
    print(f"Agent creat: {response.json()}")
```

### **Knowledge base**
```bash
curl -X POST "http://localhost:8080/api/convhi/knowledge/items" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "convhi_1",
    "title": "Informació empresa",
    "content": "La nostra empresa es dedica a...",
    "content_type": "text",
    "source_type": "manual"
  }'
```

---

## 🚀 **DEPLOYMENT EN PRODUCCIÓ**

### **1. Variables d'entorn de producció**
```env
# .env.production
OPENAI_API_KEY=sk-proj-clau-produccio
VEUPLUS_API_URL=https://veuplus.com
VEUPLUS_LANGUAGE=ca
DEBUG_MODE=false
```

### **2. Configurar HTTPS**
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name veuplus.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:8080;
    }
    
    location /static/ {
        proxy_pass http://localhost:8080;
    }
}
```

---

## ✅ **CHECKLIST DE FUNCIONALITAT**

### **Configuració bàsica:**
- [ ] API key configurada (OpenAI/Gemini/Anthropic)
- [ ] Servidor VeuPlus funcionant
- [ ] Almenys 1 agent ConvHi creat
- [ ] Widget carrega i respon
- [ ] Conversa amb agent funciona

### **Configuració avançada:**
- [ ] Múltiples agents creats
- [ ] Knowledge base configurat
- [ ] SIP trunk configurat (opcional)
- [ ] HTTPS configurat (producció)
- [ ] Monitoring configurat

---

## 🔗 **ENLLAÇOS ÚTILS**

- **API Health:** http://localhost:8080/api/health
- **Agents:** http://localhost:8080/api/convhi/agents
- **Widget JS:** http://localhost:8080/static/convhi-widget.js
- **Documentació:** http://localhost:8080/docs

---

## 🆘 **SOLUCIÓ DE PROBLEMES**

### **Error: "No API keys configured"**
```bash
# Solució: Configurar API key
echo "OPENAI_API_KEY=sk-tu-clau-aqui" >> .env
```

### **Error: "Server not available"**
```bash
# Solució: Iniciar servidor
cd backend && python server.py
```

### **Error: "No agents found"**
```bash
# Solució: Crear agents
python scripts/crear_agents_prova.py
```

### **Error: "Widget not loading"**
```bash
# Solució: Verificar que hi ha agents
curl "http://localhost:8080/api/convhi/agents"
```

---

## 📊 **RESULTAT ESPERAT**

Després de la configuració:
- ✅ **Agents ConvHi funcionals** amb LLM real
- ✅ **Widgets incrustables** que responen
- ✅ **SIP trunk real** (si configurat)
- ✅ **Sistema completament operatiu**

**Temps estimat:** 5-30 minuts
**Complexitat:** Baixa (principalment configuració d'API keys)

---

## 🎯 **PRÒXIMS PASSOS**

1. **Configurar API key** (5 minuts)
2. **Executar configuració automàtica** (2 minuts)
3. **Provar widget** (1 minut)
4. **Personalitzar agents** (segons necessitats)
5. **Configurar SIP trunk** (opcional)

**El sistema estarà completament funcional!** 🚀



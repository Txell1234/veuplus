# 🚀 CONFIGURACIÓ COMPLETA VEUPLUS - GUIA FUNCIONAL

## 📋 **ESTAT ACTUAL VS CONFIGURACIÓ NECESSÀRIA**

### ❌ **PROBLEMES IDENTIFICATS:**
1. **No hi ha API keys** configurades (OpenAI, Gemini, etc.)
2. **0 agents ConvHi** creats
3. **SIP trunk** és simulació, no real
4. **Widgets** no funcionen perquè no hi ha agents

### ✅ **SOLUCIÓ: CONFIGURACIÓ PAS A PAS**

---

## 🔧 **PAS 1: CONFIGURAR API KEYS**

### **1.1 Crear fitxer .env**
```bash
# Copiar configuració d'exemple
cp config.example.env .env
```

### **1.2 Configurar API Keys (Mínim 1 necessària)**
```env
# OPCIÓ A: OpenAI (Recomanat per començar)
OPENAI_API_KEY=sk-proj-tu-clau-openai-aqui

# OPCIÓ B: Google Gemini (Alternativa)
GEMINI_API_KEY=tu-clau-gemini-aqui

# OPCIÓ C: Anthropic Claude (Alternativa)
ANTHROPIC_API_KEY=sk-ant-tu-clau-anthropic-aqui

# Configuració VeuPlus
VEUPLUS_API_URL=http://localhost:8080
VEUPLUS_LANGUAGE=ca
VEUPLUS_VOICE_SYSTEM=edge-tts
```

### **1.3 Obtenir API Keys:**

**OpenAI (Més fàcil):**
1. Anar a https://platform.openai.com/api-keys
2. Crear nova API key
3. Copiar i afegir al .env

**Google Gemini:**
1. Anar a https://makersuite.google.com/app/apikey
2. Crear nova API key
3. Copiar i afegir al .env

---

## 🤖 **PAS 2: CREAR AGENTS CONVHI FUNCIONALS**

### **2.1 Iniciar el servidor**
```bash
cd backend
python server.py
```

### **2.2 Crear agent via API**
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
    "language": "ca",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### **2.3 Verificar agent creat**
```bash
curl "http://localhost:8080/api/convhi/agents"
```

---

## 🌐 **PAS 3: CONFIGURAR WIDGETS FUNCIONALS**

### **3.1 Generar codi d'integració**
```bash
curl -X POST "http://localhost:8080/api/convhi/widgets/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "convhi_1",
    "config": {
      "variant": "compact",
      "mode": "voice_text",
      "primary_color": "#3B82F6",
      "action_text": "Necessites ajuda?"
    },
    "domain": "localhost"
  }'
```

### **3.2 Codi HTML per incrustar**
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

## 📞 **PAS 4: CONFIGURAR SIP TRUNK REAL**

### **4.1 Instal·lar Asterisk**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install asterisk asterisk-dev

# CentOS/RHEL
sudo yum install asterisk asterisk-devel

# Windows (via Docker)
docker run -d --name asterisk -p 5060:5060/udp -p 10000-20000:10000-20000/udp andrius/asterisk
```

### **4.2 Configurar trunks SIP**
```ini
# asterisk_config/sip.conf
[general]
context=default
allowoverlap=no
udpbindaddr=0.0.0.0:5060
tcpenable=no
tcpbindaddr=0.0.0.0:5060
transport=udp

; Trunk principal
[trunk]
type=peer
host=proveidor-sip.com
username=usuari-trunk
secret=password-trunk
context=outbound
dtmfmode=rfc2833
canreinvite=no
insecure=port,invite

; Configuració VeuPlus
[veuplus]
type=friend
host=localhost
port=5060
context=veuplus-incoming
```

### **4.3 Configurar extensions per VeuPlus**
```ini
# asterisk_config/extensions.conf
[veuplus-incoming]
; Trucades entrants a VeuPlus
exten => _X.,1,NoOp(Trucada VeuPlus: ${CALLERID(num)} -> ${EXTEN})
exten => _X.,n,Set(VEUPLUS_CALL_ID=${CALLERID(num)}_${EXTEN}_${EPOCH})
exten => _X.,n,AGI(veuplus_greeting.agi,${CALLERID(num)},${EXTEN},ca,edge-tts)
exten => _X.,n,Goto(veuplus-conversation,start,1)

[veuplus-conversation]
exten => start,1,NoOp(Iniciant conversa VeuPlus)
exten => start,n,Set(INPUT_FILE=/tmp/veuplus_input_${VEUPLUS_CALL_ID}.wav)
exten => start,n,Record(${INPUT_FILE}:wav,5,10)
exten => start,n,AGI(veuplus_process.agi,${VEUPLUS_CALL_ID},${INPUT_FILE},ca,edge-tts)
exten => start,n,Set(RESPONSE_FILE=/tmp/veuplus_response_${VEUPLUS_CALL_ID}.wav)
exten => start,n,Playback(${RESPONSE_FILE})
exten => start,n,Set(CONTINUE=${AGI(veuplus_continue.agi,${VEUPLUS_CALL_ID})})
exten => start,n,GotoIf($["${CONTINUE}" = "yes"]?start,1)
exten => start,n,Hangup()
```

---

## 🧪 **PAS 5: PROVAR FUNCIONALITAT**

### **5.1 Provar agent ConvHi**
```bash
curl -X POST "http://localhost:8080/api/convhi/agents/convhi_1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "convhi_1",
    "message": "Hola, com estàs?",
    "message_type": "text"
  }'
```

### **5.2 Provar widget**
1. Obrir `frontend/public/widget-test.html`
2. Verificar que el widget apareix
3. Fer clic i provar conversa

### **5.3 Provar SIP**
```bash
# Trucar al número configurat
# Verificar logs d'Asterisk
tail -f /var/log/asterisk/messages
```

---

## 🔧 **PAS 6: CONFIGURACIÓ AVANÇADA**

### **6.1 Configurar múltiples agents**
```python
# Script per crear múltiples agents
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

### **6.2 Configurar knowledge base**
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

## 🚀 **PAS 7: DEPLOYMENT EN PRODUCCIÓ**

### **7.1 Configurar variables d'entorn de producció**
```env
# .env.production
OPENAI_API_KEY=sk-proj-clau-produccio
VEUPLUS_API_URL=https://veuplus.com
VEUPLUS_LANGUAGE=ca
DEBUG_MODE=false
```

### **7.2 Configurar HTTPS per widgets**
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

## ✅ **VERIFICACIÓ FINAL**

### **Checklist de funcionalitat:**
- [ ] API keys configurades
- [ ] Almenys 1 agent ConvHi creat
- [ ] Widget carrega i respon
- [ ] SIP trunk configurat (opcional)
- [ ] Knowledge base funcionant (opcional)

### **Comandes de verificació:**
```bash
# Verificar agents
curl "http://localhost:8080/api/convhi/agents"

# Verificar health
curl "http://localhost:8080/api/convhi/health"

# Verificar widget
curl "http://localhost:8080/static/convhi-widget.js"
```

---

## 🎯 **RESULTAT ESPERAT**

Després d'aquesta configuració:
- ✅ **Agents ConvHi funcionals** amb LLM real
- ✅ **Widgets incrustables** que responen
- ✅ **SIP trunk real** (si configurat)
- ✅ **Sistema completament operatiu**

**Temps estimat de configuració:** 30-60 minuts
**Complexitat:** Mitjana (principalment configuració d'API keys)

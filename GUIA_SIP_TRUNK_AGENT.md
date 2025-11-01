# 📞 GUIA COMPLETA: SIP TRUNK + AGENT INTEL·LIGENT

## 🎯 SISTEMA COMPLET IMPLEMENTAT

**VeuPlus** ara inclou **integració SIP completa** amb **agent intel·ligent** i **base de coneixement**:

- ✅ **SIP Trunk Integration** - Trucades telefòniques
- ✅ **Agent Intel·ligent** - LLM + Base de coneixement
- ✅ **ASR + TTS** - Reconeixement i síntesi de veu
- ✅ **Asterisk/FreeSWITCH** - Configuració completa
- ✅ **Base de Coneixement** - Memòria i aprenentatge

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Backend (FastAPI):
```
backend/
├── sip_trunk_integration.py    # Integració SIP
├── knowledge_base_agent.py     # Agent intel·ligent
├── api/
│   └── sip_agent.py           # API endpoints SIP
└── knowledge_base/            # Base de coneixement
    └── knowledge.db           # SQLite database
```

### Asterisk Configuration:
```
asterisk_config/
├── extensions.conf            # Configuració extensions
├── veuplus_greeting.agi      # Script benvinguda
├── veuplus_process.agi       # Script processament
└── veuplus_continue.agi      # Script continuació
```

---

## 📞 CONFIGURACIÓ SIP TRUNK

### 1. **Instal·lació Asterisk**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install asterisk

# CentOS/RHEL
sudo yum install asterisk

# Configurar
sudo systemctl enable asterisk
sudo systemctl start asterisk
```

### 2. **Configuració Extensions**
```bash
# Copiar configuració
sudo cp asterisk_config/extensions.conf /etc/asterisk/
sudo cp asterisk_config/*.agi /var/lib/asterisk/agi-bin/

# Permisos
sudo chmod +x /var/lib/asterisk/agi-bin/veuplus_*.agi
sudo chown asterisk:asterisk /var/lib/asterisk/agi-bin/veuplus_*.agi
```

### 3. **Configuració SIP**
```ini
# /etc/asterisk/sip.conf
[general]
context=default
allowguest=no
bindport=5060
bindaddr=0.0.0.0

[trunk]
type=peer
host=your-sip-provider.com
username=your-username
secret=your-password
context=default
```

### 4. **Reiniciar Asterisk**
```bash
sudo systemctl restart asterisk
sudo asterisk -r
> sip reload
> dialplan reload
```

---

## 🤖 AGENT INTEL·LIGENT

### 1. **Base de Coneixement**
```python
# Afegir coneixement
POST /api/sip/add-knowledge
{
    "category": "serveis",
    "question": "preus",
    "answer": "Els nostres preus comencen des de 50€/mes per serveis bàsics.",
    "language": "ca",
    "confidence": 1.0
}
```

### 2. **Processament Intel·ligent**
```python
# Flux de conversa
1. Usuari parla -> ASR (Whisper/ALIA)
2. Text processat -> LLM (GPT/ALIA)
3. Resposta generada -> TTS (VeuPlus)
4. Àudio reproduït -> Usuari escolta
5. Conversa guardada -> Base de coneixement
```

### 3. **Memòria de Conversa**
```python
# Històric per trucada
GET /api/sip/conversation-history/{call_id}
{
    "success": true,
    "conversation_history": [
        {
            "user_input": "Hola, quins serveis ofereix?",
            "agent_response": "Ofereixem serveis de consultoria, desenvolupament web...",
            "timestamp": "2024-01-15T10:30:00"
        }
    ]
}
```

---

## 🔧 CONFIGURACIÓ DETALLADA

### 1. **Variables d'Entorn**
```bash
# .env
VEUPLUS_API_URL=http://localhost:8003
VEUPLUS_LANGUAGE=ca
VEUPLUS_VOICE_SYSTEM=catalan
ASTERISK_AGI_PATH=/var/lib/asterisk/agi-bin
```

### 2. **Configuració Asterisk**
```ini
# extensions.conf
[globals]
VEUPLUS_API_URL=http://localhost:8003
VEUPLUS_LANGUAGE=ca
VEUPLUS_VOICE_SYSTEM=catalan

[default]
exten => _X.,1,NoOp(Trucada entrant: ${CALLERID(num)} -> ${EXTEN})
exten => _X.,n,Goto(veuplus-greeting,start,1)
```

### 3. **Scripts AGI**
```python
# veuplus_greeting.agi
#!/usr/bin/env python3
import requests
import base64

# Cridar API VeuPlus
response = requests.post('http://localhost:8003/api/sip/handle-call', json={
    'caller_id': sys.argv[1],
    'called_number': sys.argv[2],
    'language': 'ca',
    'voice_system': 'catalan'
})

# Guardar àudio de benvinguda
audio_data = base64.b64decode(response.json()['greeting_audio_base64'])
with open('/tmp/greeting.wav', 'wb') as f:
    f.write(audio_data)
```

---

## 🎤 FLUX DE TRUCADA

### 1. **Trucada Entrant**
```
Usuari truca -> Asterisk rep trucada
                ↓
Asterisk executa veuplus_greeting.agi
                ↓
AGI crida /api/sip/handle-call
                ↓
VeuPlus genera benvinguda (TTS)
                ↓
Asterisk reprodueix benvinguda
```

### 2. **Conversa**
```
Usuari parla -> Asterisk grava àudio
                ↓
Asterisk executa veuplus_process.agi
                ↓
AGI crida /api/sip/process-voice
                ↓
VeuPlus processa (ASR + LLM + TTS)
                ↓
Asterisk reprodueix resposta
```

### 3. **Finalització**
```
Asterisk executa veuplus_continue.agi
                ↓
AGI crida /api/sip/should-continue
                ↓
Si continua -> Tornar a conversa
Si no -> Finalitzar trucada
```

---

## 🌐 ENDPOINTS API

### SIP Trunk:
- `POST /api/sip/handle-call` - Gestionar trucada entrant
- `POST /api/sip/process-voice` - Processar entrada de veu
- `POST /api/sip/should-continue` - Verificar si continuar
- `GET /api/sip/configuration` - Configuració SIP

### Base de Coneixement:
- `POST /api/sip/add-knowledge` - Afegir coneixement
- `GET /api/sip/knowledge-stats` - Estadístiques
- `GET /api/sip/conversation-history/{call_id}` - Històric

---

## 🎯 CASOS D'ÚS REALS

### 1. **Call Center Automàtic**
```python
# Configuració per call center
greeting_text = "Hola, gràcies per trucar a [Empresa]. Sóc el vostre assistent virtual. Com puc ajudar-te?"

# Afegir coneixement específic
knowledge_base_agent.add_knowledge(
    category="productes",
    question="preus",
    answer="Els nostres productes comencen des de 29€. Vols més informació?",
    language="ca"
)
```

### 2. **Suport Tècnic**
```python
# Coneixement tècnic
knowledge_base_agent.add_knowledge(
    category="suport",
    question="error",
    answer="Per resoldre errors, primer reinicia l'aplicació. Si persisteix, contacta amb suport tècnic.",
    language="ca"
)
```

### 3. **Reserves i Cites**
```python
# Sistema de reserves
knowledge_base_agent.add_knowledge(
    category="reserves",
    question="cita",
    answer="Per reservar una cita, necessito el teu nom i la data preferida. Quina data et va bé?",
    language="ca"
)
```

---

## 🔐 SEGURETAT I OPTIMITZACIÓ

### 1. **Autenticació SIP**
```ini
# sip.conf
[trunk]
type=peer
host=your-provider.com
username=your-username
secret=your-password
context=default
qualify=yes
```

### 2. **Rate Limiting**
```python
# Limitar trucades per IP
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def handle_incoming_call(request):
    # Processar trucada
```

### 3. **Cache d'Àudio**
```python
# Cache per evitar regenerar
import hashlib

def get_audio_cache_key(text, voice_id):
    content = f"{text}_{voice_id}"
    return hashlib.md5(content.encode()).hexdigest()
```

---

## 📊 MONITORITZACIÓ

### 1. **Logs Estructurats**
```python
logger.info("SIP call processed", extra={
    "call_id": call_id,
    "caller_id": caller_id,
    "duration": duration,
    "language": language,
    "turns": conversation_turns
})
```

### 2. **Mètriques**
```python
# Tracking de trucades
metrics = {
    "total_calls": 1000,
    "successful_calls": 950,
    "average_duration": 120,
    "languages": {"ca": 600, "es": 300, "en": 100},
    "knowledge_hits": 800,
    "llm_fallbacks": 150
}
```

---

## 🚀 DEPLOYMENT

### 1. **Desenvolupament**
```bash
# Iniciar VeuPlus
cd C:\Users\merit\Desktop\VeusPlus
.\INICIAR_3_SISTEMES.ps1

# Iniciar Asterisk
sudo systemctl start asterisk
```

### 2. **Producció**
```bash
# Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Asterisk en container
docker run -d --name asterisk \
  -p 5060:5060/udp \
  -v /etc/asterisk:/etc/asterisk \
  asterisk:latest
```

### 3. **Verificació**
```bash
# Test trucada
curl -X POST http://localhost:8003/api/sip/handle-call \
  -H "Content-Type: application/json" \
  -d '{
    "caller_id": "123456789",
    "called_number": "987654321",
    "language": "ca",
    "voice_system": "catalan"
  }'
```

---

## 🎊 RESULTAT FINAL

### ✅ **SISTEMA COMPLET:**

1. **SIP Trunk Integration** - Trucades telefòniques completes
2. **Agent Intel·ligent** - LLM + Base de coneixement
3. **ASR + TTS** - Reconeixement i síntesi de veu
4. **Asterisk/FreeSWITCH** - Configuració completa
5. **Base de Coneixement** - Memòria i aprenentatge
6. **API REST** - 7 endpoints específics
7. **Documentació** - Guies completes

### 🎯 **POSSIBILITATS:**

- ✅ **Call Centers** automàtics
- ✅ **Suport Tècnic** 24/7
- ✅ **Reserves i Cites** automàtiques
- ✅ **Informació d'Empresa** instantània
- ✅ **Multiidioma** (ca, es, en, fr)
- ✅ **Escalabilitat** completa

---

## 🔧 COMANDES FINALS

### Iniciar Sistema:
```bash
# VeuPlus
.\INICIAR_3_SISTEMES.ps1

# Asterisk
sudo systemctl start asterisk
```

### Test:
```bash
# Test API
curl -X POST http://localhost:8003/api/sip/handle-call \
  -d '{"caller_id":"123","called_number":"456","language":"ca"}'
```

### Monitoritzar:
```bash
# Logs Asterisk
sudo tail -f /var/log/asterisk/messages

# Logs VeuPlus
tail -f logs/veuplus.log
```

---

**EL SISTEMA SIP TRUNK + AGENT INTEL·LIGENT ESTÀ COMPLETAMENT IMPLEMENTAT! 🎉**

**Ara pots rebre trucades, processar veu, i tenir converses intel·ligents amb base de coneixement! 📞🤖**











# 🚀 GUIA DE PRODUCCIÓ COMPLETA - VEUPLUS

### Branding AT Hub

- Logo: frontend/src/assets/ambtu-logo.svg
- Colors principals: blau navy #0f1f68, blau profund #07144a i accent taronja #ff6537
- Tailwind ja defineix primary/accent/slate amb aquesta paleta
- Usa aquestes referencies per a qualsevol captura o manual

## 🎯 SISTEMA FINAL PERMANENT

**VeuPlus v2.1.0** amb **3 sistemes TTS diferenciats** + **Integració Voicebots** + **Entrenament de Veus**

---

## 📊 ARQUITECTURA FINAL

### Backend (FastAPI):
```
backend/
├── server.py                    # Servidor principal
├── api/
│   ├── edge_tts_only.py        # Sistema 1: Edge-TTS (561 veus)
│   ├── catalan_tts.py          # Sistema 2: Català+SEGRE (4 veus)
│   ├── alia.py                 # Sistema 3: ALIA Premium (4 veus)
│   └── voicebots_external.py   # Integració voicebots
├── voicebots_integration.py    # Motor voicebots
├── voice_training_advanced.py  # Entrenament de veus
└── training_data/              # Veus entrenades
```

### Frontend (React):
```
frontend/
├── src/
│   ├── pages/
│   │   ├── EdgeTTSStandard.jsx      # Sistema 1
│   │   ├── CatalanHyperrealistic.jsx # Sistema 2
│   │   ├── ALIAKitBSC.jsx          # Sistema 3
│   │   └── Documentation.jsx       # Documentació
│   └── components/
└── Dockerfile.production
```

---

## 🎤 INTEGRACIÓ VOICEBOTS

### 1. **Web Voicebots**
```javascript
// Qualsevol web
const response = await fetch('http://veuplus:8003/api/voicebots/synthesize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "Hola, com puc ajudar-te?",
    voice_id: "ca-ES-EnricNeural",
    system: "edge-tts",
    language: "ca"
  })
})

const audioUrl = `data:audio/mp3;base64,${response.audio_base64}`
const audio = new Audio(audioUrl)
audio.play()
```

### 2. **Telefònics (SIP/Asterisk)**
```python
# Asterisk AGI script
import requests
import base64

def generate_voice_response(text, voice_id="ca-ES-EnricNeural"):
    response = requests.post('http://veuplus:8003/api/voicebots/synthesize', json={
        'text': text,
        'voice_id': voice_id,
        'system': 'catalan',
        'language': 'ca'
    })
    
    if response.json()['success']:
        # Guardar àudio per Asterisk
        audio_data = base64.b64decode(response.json()['audio_base64'])
        with open('/tmp/response.wav', 'wb') as f:
            f.write(audio_data)
        return '/tmp/response.wav'
    
    return None
```

### 3. **Mòbils (React Native/Flutter)**
```javascript
// React Native
const generateVoice = async (text, voiceId) => {
  const response = await fetch('http://veuplus:8003/api/voicebots/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text,
      voice_id: voiceId,
      system: 'edge-tts'
    })
  })
  
  const data = await response.json()
  return data.audio_base64
}
```

### 4. **IoT (Raspberry Pi)**
```python
# Raspberry Pi
import requests
import pygame
import base64
import tempfile

def speak(text, voice_id="ca-ES-EnricNeural"):
    response = requests.post('http://veuplus:8003/api/voicebots/synthesize', json={
        'text': text,
        'voice_id': voice_id,
        'system': 'edge-tts'
    })
    
    if response.json()['success']:
        audio_data = base64.b64decode(response.json()['audio_base64'])
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
```

---

## 🎓 ENTRENAMENT DE NOVES VEUS

### 1. **Process d'Entrenament**
```bash
# 1. Gravar àudio de referència (5-10 minuts)
# 2. Pujar fitxers al sistema
# 3. Entrenar amb qualitat "senyor català extended"
# 4. Integrar al sistema
```

### 2. **API d'Entrenament**
```bash
curl -X POST http://veuplus:8003/api/voicebots/train \
  -F "voice_name=meva_veu_personalitzada" \
  -F "language=ca" \
  -F "quality_level=senyor_catala_extended" \
  -F "audio_files=@grabacio1.wav" \
  -F "audio_files=@grabacio2.wav"
```

### 3. **Qualitats Disponibles**
- `senyor_catala_extended` - Tono formal, pronunciació clara
- `professional` - Tono professional estàndard
- `casual` - Tono casual i natural

---

## 🌐 ENDPOINTS API COMPLETS

### Sistema 1 (Edge-TTS):
- `POST /api/edge-tts/synthesize` - Síntesi (561 veus)
- `GET /api/edge-tts/voices` - Llistar veus

### Sistema 2 (Català+SEGRE):
- `POST /api/catalan/synthesize` - Síntesi català
- `GET /api/catalan/voices` - Veus catalanes

### Sistema 3 (ALIA Premium):
- `POST /api/alia/tts/synthesize` - Síntesi premium
- `GET /api/alia/voices` - Veus premium

### Voicebots (Nou):
- `POST /api/voicebots/synthesize` - Síntesi per voicebots
- `POST /api/voicebots/webhook` - Webhook per sistemes externs
- `GET /api/voicebots/voices` - Veus per voicebots
- `POST /api/voicebots/train` - Entrenar nova veu
- `GET /api/voicebots/trained` - Veus entrenades
- `POST /api/voicebots/synthesize-trained` - Síntesi amb veu entrenada

---

## 🐳 DEPLOYMENT DOCKER

### 1. **Desenvolupament**
```bash
cd C:\Users\merit\Desktop\VeusPlus
.\INICIAR_3_SISTEMES.ps1
```

### 2. **Producció**
```bash
# Build i deploy
docker-compose -f docker-compose.production.yml up -d

# Verificar
curl http://localhost:8003/health
curl http://localhost:3000
```

### 3. **Escalabilitat**
```yaml
# docker-compose.production.yml
services:
  veuplus-backend:
    replicas: 3
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

---

## 🔧 CONFIGURACIÓ DE PRODUCCIÓ

### 1. **Variables d'Entorn**
```bash
# .env.production
PYTHONPATH=/app
EDGE_TTS_ENABLED=true
VOICEBOT_INTEGRATION=true
LOG_LEVEL=INFO
MAX_VOICE_SAMPLES=10
TRAINING_QUALITY=senyor_catala_extended
CONVHI_WIDGET_SECRET=canvia-aqui
CONVHI_WIDGET_ALLOWLIST=veuplus.local,example.com
CONVHI_WEBHOOK_SECRET=canvia-aqui
```

**Nota ConvHi:** Ajusta els valors anteriors i afegeix `CONVHI_WEBHOOK_STORE=false` si no vols persistir els events.

### 2. **Nginx (Proxy)**
```nginx
# nginx.production.conf
server {
    listen 80;
    server_name veuplus.local;
    
    location /api/ {
        proxy_pass http://veuplus-backend:8003;
    }
    
    location / {
        proxy_pass http://veuplus-frontend:3000;
    }
}
```

### 3. **SSL/HTTPS**
```bash
# Certificats SSL
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
```

---

## 📊 MÈTRIQUES I MONITORITZACIÓ

### 1. **Logs Estructurats**
```python
logger.info("Voice synthesis", extra={
    "voice_id": voice_id,
    "system": system,
    "text_length": len(text),
    "duration_ms": duration
})
```

### 2. **Mètriques d'Ús**
```python
# Tracking per sistema
metrics = {
    "sistema1_edge_tts": {"requests": 1000, "voices_used": 50},
    "sistema2_catalan": {"requests": 500, "segre_applied": 400},
    "sistema3_alia": {"requests": 300, "languages": ["ca", "es"]},
    "voicebots": {"requests": 200, "external_systems": 10}
}
```

---

## 🎯 CASOS D'ÚS REALS

### 1. **Call Center Català**
```python
# Sistema de trucades automàtiques
def handle_incoming_call(caller_id, language="ca"):
    voice_id = "ca-ES-EnricNeural" if language == "ca" else "es-ES-AlvaroNeural"
    
    response = requests.post('http://veuplus:8003/api/voicebots/synthesize', json={
        'text': f"Hola, gràcies per trucar. Com puc ajudar-te?",
        'voice_id': voice_id,
        'system': 'catalan' if language == 'ca' else 'edge-tts'
    })
    
    return response.json()['audio_base64']
```

### 2. **Assistent Virtual Web**
```javascript
// Chatbot amb veu
class VoiceChatbot {
  async respondToUser(message, language = 'ca') {
    // Processar missatge amb LLM
    const response = await this.processMessage(message)
    
    // Generar veu
    const voiceResponse = await fetch('/api/voicebots/synthesize', {
      method: 'POST',
      body: JSON.stringify({
        text: response,
        voice_id: language === 'ca' ? 'ca-ES-JoanaNeural' : 'es-ES-ElviraNeural',
        system: 'alia',
        language: language
      })
    })
    
    return voiceResponse.json()
  }
}
```

### 3. **Sistema d'Anuncis Personalitzats**
```python
# Anuncis per idioma
def generate_advertisement(product, language, voice_style="professional"):
    voices = {
        'ca': {
            'professional': 'ca-ES-EnricNeural',
            'friendly': 'ca-ES-JoanaNeural',
            'premium': 'ca-ES-AlbaNeural'
        },
        'es': {
            'professional': 'es-ES-AlvaroNeural',
            'friendly': 'es-ES-ElviraNeural'
        }
    }
    
    voice_id = voices[language][voice_style]
    
    response = requests.post('http://veuplus:8003/api/voicebots/synthesize', json={
        'text': f"Descobreix {product} amb la millor qualitat",
        'voice_id': voice_id,
        'system': 'alia',
        'language': language
    })
    
    return response.json()['audio_base64']
```

---

## 🔐 SEGURETAT I OPTIMITZACIÓ

### 1. **Rate Limiting**
```python
# Limitar requests per IP
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def synthesize_voice(request):
    # Síntesi
```

### 2. **Cache d'Àudio**
```python
# Cache per evitar regenerar el mateix àudio
import hashlib

def get_audio_cache_key(text, voice_id, settings):
    content = f"{text}_{voice_id}_{settings}"
    return hashlib.md5(content.encode()).hexdigest()
```

### 3. **Compressió d'Àudio**
```python
# Compressió per optimitzar transferència
import gzip

def compress_audio(audio_base64):
    audio_bytes = base64.b64decode(audio_base64)
    compressed = gzip.compress(audio_bytes)
    return base64.b64encode(compressed).decode()
```

---

## 📈 ESCALABILITAT

### 1. **Load Balancer**
```yaml
# docker-compose.production.yml
services:
  veuplus-backend:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 2. **Database per Mètriques**
```python
# SQLite per mètriques d'ús
import sqlite3

def log_voice_usage(voice_id, system, text_length, duration):
    conn = sqlite3.connect('voice_metrics.db')
    conn.execute('''
        INSERT INTO voice_usage (voice_id, system, text_length, duration, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (voice_id, system, text_length, duration, datetime.now()))
    conn.commit()
    conn.close()
```

---

## 🎊 RESULTAT FINAL

### ✅ **SISTEMA COMPLET PERMANENT:**

1. **3 Sistemes TTS Diferenciats** (569 veus úniques)
2. **Integració Voicebots** (web, telefònic, mòbil, IoT)
3. **Entrenament de Veus** (qualitat "senyor català extended")
4. **API REST Completa** (11 endpoints)
5. **Frontend React Modern** (4 pàgines)
6. **Docker Production Ready** (escalable)
7. **Documentació Completa** (guies, exemples)

### 🎯 **POSSIBILITATS D'ÚS:**

- ✅ **Call Centers** automàtics
- ✅ **Assistents Virtuals** web
- ✅ **Sistemes Telefònics** (SIP)
- ✅ **Apps Mòbils** (React Native/Flutter)
- ✅ **IoT** (Raspberry Pi, Arduino)
- ✅ **Anuncis Personalitzats**
- ✅ **Educació** (lliçons de llengua)
- ✅ **Accessibilitat** (text-to-speech)

---

## 🚀 COMANDES FINALS

### Desenvolupament:
```powershell
cd C:\Users\merit\Desktop\VeusPlus
.\INICIAR_3_SISTEMES.ps1
```

### Producció:
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Test:
```powershell
.\test_rapido.ps1
```

---

**EL SISTEMA ESTÀ COMPLETAMENT PERMANENT I LLEST PER PRODUCCIÓ! 🎉**













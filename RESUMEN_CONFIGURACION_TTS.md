# Resumen de Configuración TTS - VeusPlus

## 🎯 Separación de Canales TTS

### 1. **Canal Hiperrealista Catalán** 
**Ruta Frontend:** `/catalan-hyperrealistic`  
**Endpoint API:** `POST /api/catalan/synthesize`

#### Características:
- ✅ Usa grabaciones reales de voces catalanas
- ✅ Procesamiento fonético con SEGRE
- ✅ Clonación de voz basada en características extraídas
- ✅ 4 voces disponibles:
  - `senyor_catala_1` - Masculina, acento Barcelona
  - `dona_catalana` - Femenina, acento Barcelona
  - `senyor_catala_2` - Masculina expresiva, acento Barcelona
  - `senyor_catala_extended` - Masculina formal, acento Barcelona

#### Grabaciones Reales:
- Ubicación: `backend/training_data/{voice_id}/processed.wav`
- Todas las grabaciones están presentes y verificadas

#### Motor de Síntesis:
- Módulo: `backend/real_voice_cloning.py`
- Sistema: `backend/realistic_catalan_tts.py`
- Método: Clonación basada en características de grabaciones reales

---

### 2. **Canal Edge-TTS Estándar**
**Ruta Frontend:** `/edge-tts-standard`  
**Endpoint API:** `POST /api/edge/synthesize`

#### Características:
- ✅ Usa Microsoft Edge-TTS Neural
- ✅ Voces multiidioma (Español, Inglés, Francés, Italiano, Alemán)
- ✅ Calidad neural comercial de Microsoft
- ✅ Procesamiento de texto optimizado

#### Voces Disponibles:
- Español (es-ES): ElviraNeural, AlvaroNeural, LaiaNeural, ArnauNeural
- Inglés (en-US): AriaNeural, GuyNeural, JennyNeural, DavisNeural
- Francés (fr-FR): DeniseNeural, HenriNeural, EloiseNeural, RemyNeural
- Alemán (de-DE): KatjaNeural, ConradNeural, AmalaNeural, KasperNeural
- Italiano (it-IT): ElsaNeural, DiegoNeural, IsabellaNeural, BenjaminNeural

#### Motor de Síntesis:
- Módulo: `backend/edge_tts_engine.py`
- API: `backend/api/edge_tts.py`
- Motor: Microsoft Azure Edge-TTS

---

## 📁 Estructura de Archivos

### Backend:
```
backend/
├── api/
│   ├── catalan_tts.py       # API específica catalana
│   ├── edge_tts.py           # API específica Edge-TTS
│   └── tts.py                # API general (fallback)
├── realistic_catalan_tts.py  # Motor catalán hiperrealista
├── real_voice_cloning.py     # Sistema de clonación
├── edge_tts_engine.py        # Motor Edge-TTS
└── training_data/            # Grabaciones reales
    ├── senyor_catala_1/
    ├── dona_catalana/
    ├── senyor_catala_2/
    └── senyor_catala_extended/
```

### Frontend:
```
frontend/src/
├── pages/
│   ├── CatalanHyperrealistic.jsx  # Página voces catalanas
│   ├── EdgeTTSStandard.jsx        # Página voces Edge-TTS
│   └── VoiceSynthesis.jsx         # Síntesis general
├── components/
│   └── Layout.jsx                  # Navegación actualizada
└── App.jsx                         # Routing actualizado
```

---

## 🚀 Cómo Arrancar el Proyecto

### Opción 1: Desarrollo Local (Windows)
```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Frontend (nueva terminal)
cd frontend
npm install
npm run dev
```

### Opción 2: Docker
```bash
docker-compose up --build
# Acceder a http://localhost:8080
```

---

## 🔍 Verificación de Funcionamiento

### 1. Health Checks:
- **Catalán**: `GET http://localhost:8001/api/catalan/health`
- **Edge-TTS**: `GET http://localhost:8001/api/edge/health`

### 2. Listar Voces:
- **Catalán**: `GET http://localhost:8001/api/catalan/voices`
- **Edge-TTS**: `GET http://localhost:8001/api/edge/voices`

### 3. Síntesis de Prueba:
```bash
# Catalán Hiperrealista
curl -X POST http://localhost:8001/api/catalan/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Bon dia, aquesta és una prova","voice_id":"senyor_catala_1"}'

# Edge-TTS
curl -X POST http://localhost:8001/api/edge/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, this is a test","voice_id":"en-US-AriaNeural"}'
```

---

## ✅ Checklist de Verificación

- [x] Grabaciones catalanas en lugar (`backend/training_data/`)
- [x] Edge-TTS instalado (requirements.txt)
- [x] Endpoints API separados (`/api/catalan/` y `/api/edge/`)
- [x] Frontend con pestañas separadas
- [x] Routing actualizado en App.jsx
- [x] Navegación actualizada en Layout.jsx
- [x] Cada canal usa su motor específico
- [x] Separación correcta de voces por tipo

---

## 📝 Notas Importantes

1. **Voces Catalanas**: Utilizan grabaciones reales ubicadas en `backend/training_data/`. Estas NO son voces Edge-TTS.

2. **Edge-TTS**: Voces neurales de Microsoft Azure que funcionan sin API key gracias a edge-tts library.

3. **Separación**: Los dos sistemas están completamente separados:
   - Diferentes endpoints API
   - Diferentes páginas frontend
   - Diferentes motores de síntesis
   - Diferentes tipos de voces

4. **Calidad**:
   - Catalán: Hiperrealista basada en grabaciones reales
   - Edge-TTS: Neural comercial de Microsoft

---

**Fecha de Configuración:** 8 de Octubre, 2025  
**Versión:** VeusPlus 2.0 - Separación Completa de Canales TTS














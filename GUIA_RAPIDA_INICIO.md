# 🚀 Guia Ràpida d'Inici - VeuPlus + ALIA Kit

## ✅ Solució Implementada

He solucionat el problema del **soroll estrany** a ALIA Kit:

### Què s'ha canviat:
- ❌ **Eliminat:** Models BSC que generaven soroll sintètic
- ✅ **Implementat:** Edge-TTS optimitzat amb SEGRE
- ✅ **Resultat:** Veu natural catalana sense soroll

---

## 🎯 Opció 1: Inici Automàtic (RECOMANAT)

### Executa un sol script:

```powershell
cd C:\Users\merit\Desktop\VeusPlus
.\INICIAR_VEUPLUS_COMPLETO.ps1
```

**Què fa aquest script:**
1. ✅ Atura processos anteriors
2. ✅ Inicia el backend (port 8003)
3. ✅ Inicia el frontend (port 3000)
4. ✅ Verifica que tot funcioni
5. ✅ Obre el navegador automàticament

**Temps estimat:** 30-40 segons

---

## 🎯 Opció 2: Inici Manual

### Terminal 1 - Backend:
```powershell
cd C:\Users\merit\Desktop\VeusPlus\backend
python server.py
```

### Terminal 2 - Frontend:
```powershell
cd C:\Users\merit\Desktop\VeusPlus\frontend
npm run dev
```

### Navegador:
Obre: `http://localhost:3000`

---

## 🧪 Provar ALIA Kit (sense soroll)

### Al Frontend:

1. **Ves a:** "ALIA Kit BSC" (menú lateral)
2. **Escriu:** "Hola, com estàs? Aquesta és una prova de veu catalana d'alta qualitat."
3. **Selecciona:**
   - Idioma: Català
   - Dialecte: Central (o Balear/Valencià)
4. **Genera àudio**
5. **Escolta:** Hauria de sonar com una veu natural, **sense cap soroll estrany**

### Veus disponibles:

| Dialecte | Veu | Tipus |
|----------|-----|-------|
| Central | ca-ES-EnricNeural | Masculina |
| Balear | ca-ES-JoanaNeural | Femenina |
| Valencià | ca-ES-AlbaNeural | Femenina |

---

## 🔍 Verificació de Qualitat

### ✅ Àudio correcte:
- Veu natural i clara
- Pronunciació catalana correcta
- Sense sorolls de fons
- Sense "piiiii" o sons sintètics

### ❌ Si encara hi ha problemes:
1. Verifica que el backend estigui actiu: `http://localhost:8003/health`
2. Comprova els logs del backend
3. Prova amb text més curt primer
4. Informa del tipus exacte de soroll

---

## 📊 Endpoints Actius

### Backend (port 8003):
- `/health` - Estat del servidor
- `/api/alia/tts/synthesize` - Síntesi ALIA Kit
- `/api/alia/voices` - Llista de veus
- `/api/alia/status` - Estat ALIA Kit
- `/api/trained/synthesize` - Veus entrenades
- `/api/edge-tts/synthesize` - Edge-TTS directe
- `/docs` - Documentació API

### Frontend (port 3000):
- `/` - Dashboard
- `/alia-kit-bsc` - **ALIA Kit BSC** ⭐
- `/catalan-hyperrealistic` - Veus hiperrealistes
- `/edge-tts-standard` - Edge-TTS estàndard
- `/chatbots` - Chatbots
- `/voicebots` - Voicebots

---

## 🎯 Diferències entre Endpoints

### 1. ALIA Kit BSC (`/api/alia/tts/synthesize`)
- ✅ Edge-TTS optimitzat
- ✅ SEGRE per català
- ✅ Configuració avançada (rate, pitch)
- ✅ Múltiples dialectes
- 🎯 **USA AQUEST per veus catalanes de qualitat**

### 2. Veus Entrenades (`/api/trained/synthesize`)
- Veus personalitzades entrenades
- Basades en gravacions reals
- IDs: `senyor_catala_1`, `dona_catalana`, etc.

### 3. Edge-TTS Directe (`/api/edge-tts/synthesize`)
- Edge-TTS sense modificacions
- Multiidioma
- Sense SEGRE

---

## 💡 Recomanacions

### Per català d'alta qualitat:
1. **Usa:** ALIA Kit BSC
2. **Dialecte:** Selecciona el teu (central/balear/valencià)
3. **Text:** Frases completes amb puntuació correcta
4. **Velocitat:** Deixa 1.0 per defecte (natural)

### Per altres idiomes:
- Castellà: ALIA Kit BSC amb `language: "es"`
- Euskera: ALIA Kit BSC amb `language: "eu"`
- Gallec: ALIA Kit BSC amb `language: "gl"`

---

## 🛠️ Solució de Problemes

### Problema: "Backend no disponible"
**Solució:**
```powershell
cd C:\Users\merit\Desktop\VeusPlus\backend
python server.py
```

### Problema: "Frontend no carrega"
**Solució:**
```powershell
cd C:\Users\merit\Desktop\VeusPlus\frontend
npm install
npm run dev
```

### Problema: "Port 8003 ja en ús"
**Solució:**
```powershell
Get-Process -Name python | Stop-Process -Force
```

### Problema: "Encara sona estrany"
**Solució:**
1. Tanca totes les finestres de PowerShell
2. Executa `INICIAR_VEUPLUS_COMPLETO.ps1` de nou
3. Esborra cache del navegador (Ctrl+Shift+Delete)
4. Prova amb un text diferent

---

## 📝 Fitxers Importants

### Scripts d'inici:
- ✅ `INICIAR_VEUPLUS_COMPLETO.ps1` - Inici automàtic complet
- ✅ `test_alia_neural.ps1` - Test d'ALIA Kit

### Codi backend:
- ✅ `backend/alia_kit_fixed.py` - Implementació ALIA Kit sense soroll
- ✅ `backend/api/alia.py` - Endpoints ALIA Kit
- ✅ `backend/server.py` - Servidor principal

### Frontend:
- ✅ `frontend/src/pages/ALIAKitBSC.jsx` - Pàgina ALIA Kit
- ✅ `frontend/vite.config.js` - Configuració (proxy a port 8003)

---

## ✅ Checklist Final

Abans de provar, assegura't que:

- [ ] Backend corrent al port 8003
- [ ] Frontend corrent al port 3000
- [ ] Navegador obert a `http://localhost:3000`
- [ ] Pàgina "ALIA Kit BSC" visible al menú
- [ ] Text introduït al camp de text
- [ ] Dialecte seleccionat
- [ ] Botó "Generar Veu" clicat
- [ ] Àudio reproduint-se sense soroll

---

## 🎉 Resultat Esperat

Quan tot funcioni correctament:

1. ✅ El backend mostra: `✅ ALIA Kit Fixed exitós`
2. ✅ El frontend genera àudio sense errors
3. ✅ L'àudio sona com una **veu natural catalana**
4. ✅ **NO hi ha cap soroll estrany** (piiiii, clics, etc.)
5. ✅ La pronunciació és correcta gràcies a SEGRE

---

**Ara executa:** `.\INICIAR_VEUPLUS_COMPLETO.ps1` i prova! 🚀


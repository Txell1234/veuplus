# Planificació Interfície Completa - ConvHi Configuration

## 🎯 Problema Actual
- Checkboxes inútils que no permeten configuració real
- Usuari no pot veure resultats d'ASR
- Usuari no pot pujar documentació
- Usuari no pot configurar coneixement
- No hi ha feedback visual

## ✅ Solució: Interfície Completa Visual i Funcional

### 1. Pàgina de Configuració d'Agent

**Ruta**: `/convhi-agents/config/{agent_id}`

**Components**:

#### A) ASR Configuration Panel
- **Test ASR**:
  - Upload d'àudio o gravar directament
  - Mostrar transcripció en temps real
  - Selector d'idioma
  - Mètriques (confidence, latency)
- **Configuració**:
  - Enable/disable switch
  - Idioma per defecte
  - Model ASR (Whisper base/small/medium)
  - Threshold de confiança
- **Visualització**:
  - Llista de transcripcions recents
  - Player d'àudio amb transcripció sincronitzada
  - Estadístiques (num transcripcions, % exit)

#### B) Knowledge Base Manager
- **Upload Documents**:
  - Drag & drop zona
  - Fitxers suportats: PDF, DOCX, TXT, HTML, EPUB
  - Barra de progrés per upload
  - Visualització de documents pujats
- **Manual Input**:
  - Editor de text ric
  - Categories i tags
  - Mètadades (autor, data, categoria)
- **Connectors**:
  - Notion connector
  - SharePoint connector
  - Google Drive connector
  - Custom API connector
- **Visualització**:
  - Llista de coneixement amb buscador
  - Preview de documents
  - Estadístiques d'ús (quantes vegades s'ha utilitzat)
  - Resultats de cerca en temps real

#### C) LLM Configuration
- **Connection Test**:
  - Input API key
  - Botó "Test Connection"
  - Mostrar resposta i latency
  - Indicador visual (verd/vermell)
- **Provider Selection**:
  - Cards visuals per cada provider
  - OpenAI, Gemini, Claude, ALIA, etc.
  - Mostrar preu per token
  - Usage stats
- **Model Configuration**:
  - Temperature slider (0-2)
  - Max tokens slider
  - System prompt editor
  - Custom instructions

#### D) Monitoring & Analytics
- **Live Dashboard**:
  - Mètriques en temps real
  - Gràfics de converses
  - Success rate
  - Avg response time
- **Logs Viewer**:
  - Filtre per data/usuari/error
  - Search a logs
  - Export CSV/JSON
  - Real-time streaming

#### E) Turn Taking Configuration
- **Test Panel**:
  - Simulador de conversa
  - Audio input/output
  - Visualitzar timings
  - Threshold sliders
- **Configuració**:
  - Silence threshold
  - Audio level threshold
  - Response delay
  - Interruption detection

---

## 📋 Components a Crear

### Frontend Components:

1. **`ASRConfigPanel.jsx`**
   - Upload/gravar àudio
   - Visualització transcripció
   - Mètriques i stats

2. **`KnowledgeBaseManager.jsx`**
   - Upload documents
   - Editor manual
   - Connectors
   - Llista de coneixement
   - Cercador

3. **`LLMConfigPanel.jsx`**
   - Connection test
   - Provider cards
   - Model config
   - Usage dashboard

4. **`MonitoringDashboard.jsx`**
   - Live mètriques
   - Gràfics
   - Logs viewer
   - Export

5. **`TurnTakingConfig.jsx`**
   - Simulador
   - Threshold sliders
   - Test real-time

---

## 🎨 Disseny User-Friendly

### Layout Principal:
```
┌────────────────────────────────────────────┐
│ Agent Configuration Dashboard              │
├────────────────────────────────────────────┤
│                                            │
│  [Tab 1: ASR] [Tab 2: KB] [Tab 3: LLM]    │
│  [Tab 4: Monitoring] [Tab 5: Turn Taking]  │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │                                     │   │
│  │     Active Tab Content            │   │
│  │                                     │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Save Changes] [Test Agent] [Deploy]     │
└────────────────────────────────────────────┘
```

### Tabs amb icons i indicadors:
- 🔴 Disabled / 🟢 Enabled
- Num d'errors si hi ha
- Last update time

---

## ✅ Implementació Planificada

### Fase 1: ASR Configuration ✅ PRIORITARI
- Component visual
- Upload/gravar
- Mostrar transcripció
- Stats visuals

### Fase 2: Knowledge Base Manager ✅ PRIORITARI
- Drag & drop upload
- Editor manual
- Llista de coneixement
- Cercador

### Fase 3: LLM Config ✅
- Connection test visual
- Provider cards
- Usage dashboard

### Fase 4: Monitoring Dashboard ✅
- Live mètriques
- Gràfics
- Logs viewer

### Fase 5: Turn Taking Config ⚠️
- Simulador
- Threshold config

---

## 🚀 Vantatges sobre Competència

### ElevenLabs NO permet:
- ❌ Veure transcripcions ASR
- ❌ Configurar knowledge base detalladament
- ❌ Test connection LLM
- ❌ Monitoring visual en temps real
- ❌ Configuració avançada

### Plivo NO permet:
- ❌ ASR configurable
- ❌ Knowledge base
- ❌ LLM integration
- ❌ Monitoring detallat

### VeuPlus SÍ permet: ✅
- ✅ Veure i configurar ASR complet
- ✅ Upload visual de documents
- ✅ Test connection LLM
- ✅ Monitoring en temps real
- ✅ Configuració 100% visual

---

## 📝 Començem Implementació...


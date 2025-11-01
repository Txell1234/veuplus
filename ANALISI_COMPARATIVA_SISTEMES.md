# Anàlisi Comparativa: VeuPlus vs ElevenLabs

## 🎯 Imatges Analitzades

### Imatge 1: Configuració Bàsica d'Agent
- **Idioma per defecte**: Dropdown amb flags
- **Idiomes addicionals**: Múltiples idiomes
- **Missatge inicial**: Àrea de text amb opció "Disable interruptions"
- **Sistema de prompt**: Visible però buit

### Imatge 2: System Prompt Detallat
- **# Personality**: Descripció completa del persona (Alex Morales, deute collection)
- **# Environment**: Context legal, company, variables del sistema
- **Dynamic Variables**: Variables dinàmiques configurables
- **Magia Wand**: Botó per generar prompts amb AI

### Imatge 3: Configuració Avançada LLM
- **Temperature**: Slider amb presets (Deterministic, Creative, More Creative)
- **Limit Token Usage**: Control de tokens
- **Agent Knowledge Base**: Upload de documents, URLs, text
- **Tools**: Eines configurables (End call, Detect language, Skip turn)

### Imatge 4: Tools Detallats
- **Tools amb enable/disable**:
  - End call
  - Detect language
  - Skip turn
  - Transfer to agent
  - Transfer to number
  - Play keypad touch tone
  - Voicemail detection
- **Custom tools**: Add custom tools
- **Custom MCP Servers**: Model Context Protocol
- **Workspace Auth Connections**: Autenticació

---

## 📊 Comparativa: VeuPlus vs ElevenLabs

### ✅ El que VeuPlus JA TÉ:

1. **System Prompt** ✅ (backend ja accepta prompts)
2. **Knowledge Base** ✅ (ConvHiAgentConfig - tabs)
3. **ASR Configuration** ✅ (Whisper integrat)
4. **Monitoring** ✅ (Logs i analytics)
5. **SIP Configuration** ✅ (SIP trunking per agent)
6. **WebRTC Configuration** ✅ (STUN/TURN servers)
7. **LLM Provider Configuration** ✅ (OpenAI, Gemini, Claude, etc.)

### ❌ El que FALTA a VeuPlus:

#### 1. **Configuració de Missatges Inicials**
```javascript
// FALTA:
- First message configurable per agent
- Opció "Disable interruptions" durant missatge inicial
- Variants de missatges per idioma
```

#### 2. **System Prompt Estructurat**
```javascript
// FALTA:
- Secció # Personality 
- Secció # Environment
- Magia Wand per generar prompts automàticament
- Preview del prompt final
```

#### 3. **Temperature i Controls LLM**
```javascript
// FALTA:
- Slider temperature amb presets
- Limit token usage
- Max response length
- Stop sequences
```

#### 4. **Tools/Actions Detallades**
```javascript
// FALTA:
- Enable/disable tools individuals:
  • End call
  • Detect language
  • Skip turn
  • Transfer to agent
  • Transfer to human
  • Play keypad tones
  • Voicemail detection
```

#### 5. **Custom Tools**
```javascript
// FALTA:
- Interface per crear custom tools
- JSON schema validation
- Testing de tools
```

#### 6. **MCP Servers**
```javascript
// FALTA:
- Model Context Protocol servers
- Integration amb sistemes externs
```

#### 7. **Workspace Auth**
```javascript
// FALTA:
- Auth connections configurables
- API keys per tool específic
```

#### 8. **Multi-Language Support**
```javascript
// FALTA:
- Flag selector per idioma
- Múltiples idiomes per agent
- Language switching automàtic
```

---

## 🎯 Planificació: Què Fer

### Prioritat ALTA (Core Functionality):

1. **Missatges Inicials**
   - Afegir camp "first_message" a agent schema
   - Afegir checkbox "disable_interruptions"
   - Validar que aquests camps es passen al backend

2. **System Prompt Estructurat**
   - Millorar ConvHiAgentConfig per tenir seccions separades
   - Afegir Personality, Environment sections
   - Permetre preview del prompt final

3. **Temperature Controls**
   - Afegir slider temperature a config
   - Afegir limit tokens
   - Afegir max response length

### Prioritat MITJANA (Tools & Integrations):

4. **Tools Enable/Disable**
   - Backend: Afegir camp "enabled_tools" array
   - Frontend: Toggle switches per cada tool
   - Validar que tools s'utilitzen correctament durant conversa

5. **Knowledge Base Modal**
   - Ja existeix, assegurar-se que funciona correctament
   - Afegir search dins de la modal
   - Millorar preview de documents

### Prioritat BAIXA (Nice to Have):

6. **Custom Tools**
7. **MCP Servers**
8. **Workspace Auth**
9. **Magic Wand AI Prompt Generation**

---

## 📝 Canvis Necessaris

### Backend (schema update):
```python
class AgentSchema(BaseModel):
    # ... existing fields ...
    
    # NOU:
    first_message: str = None
    disable_interruptions: bool = False
    temperature: float = 0.7
    max_tokens: int = 1000
    max_response_length: int = 500
    enabled_tools: List[str] = []  # ['end_call', 'detect_language', ...]
    
    system_prompt: dict = {  # Estructurat
        'personality': str,
        'environment': str,
        'dynamic_variables': dict
    }
```

### Frontend (ConvHiAgentConfig tabs):
```jsx
// Tab 1: "General"
- Name, description
- First message (textarea)
- Disable interruptions (checkbox)
- Multi-language support (flags)

// Tab 2: "System Prompt" 
- Personality section
- Environment section
- Dynamic variables
- Preview button

// Tab 3: "LLM Settings"
- Temperature slider
- Max tokens
- Max response length
- Provider/Model (ja existeix)

// Tab 4: "Knowledge Base"
- Ja existeix

// Tab 5: "Tools & Actions"
- Toggles per cada tool
- Custom tools section
```

---

## 🚀 Implementation Plan

### Step 1: Analitzar Backend Actual
- Verificar quins camps ja existeixen
- Identificar quins faltan

### Step 2: Actualitzar Backend
- Afegir camps nous al schema
- Actualitzar endpoints CREATE/UPDATE agent

### Step 3: Millorar Frontend
- Afegir tabs nous a ConvHiAgentConfig
- Afegir controls (sliders, toggles, text areas)

### Step 4: Testing
- Test crear agent amb configuració completa
- Verificar que missatges inicials funcionen
- Verificar que tools s'activen/desactiven correctament


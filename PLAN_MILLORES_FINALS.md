# Planificació Millores VeuPlus Basades en Anàlisi

## ✅ El que VeuPlus JA TÉ (Comparat amb ElevenLabs):

1. ✅ **Temperature** (0.7 default)
2. ✅ **Max tokens** (1000 default)
3. ✅ **Knowledge base enabled**
4. ✅ **Turn taking enabled**
5. ✅ **ASR enabled**
6. ✅ **Monitoring enabled**
7. ✅ **Dynamic variables**
8. ✅ **Overrides**
9. ✅ **RAG enabled**
10. ✅ **Voice system** (edge-tts, catalan, alia)
11. ✅ **LLM provider** (openai, gemini, claude)

## ❌ El que FALTA (Comparat amb ElevenLabs):

### 1. FIRST MESSAGE (MISSATGE INICIAL)
```python
# FALTA:
first_message: Optional[str] = None
disable_interruptions: bool = False
```

**Impacte**: L'agent no pot tenir un missatge inicial configurab

### 2. SYSTEM PROMPT ESTRUCTURAT
```python
# FALTA estructura:
system_prompt_structure: dict = {
    'personality': str,  # # Personality section
    'environment': str,  # # Environment section
    'variables': dict    # Dynamic variables formatted
}
```

**Impacte**: No hi ha seccions clares per prompt, tot està en un sol camp

### 3. TOOLS ENABLE/DISABLE
```python
# FALTA:
enabled_tools: List[str] = []  # ['end_call', 'detect_language', 'transfer']
```

**Impacte**: No pots activar/desactivar funcions específiques (end call, transfer, etc.)

### 4. MULTI-LANGUAGE SUPPORT
```python
# FALTA:
additional_languages: List[str] = []
language_auto_detect: bool = False
```

**Impacte**: Només un idioma per agent

### 5. ADVANCED LLM SETTINGS
```python
# FALTA:
max_response_length: int = 500
stop_sequences: List[str] = []
top_p: float = 1.0
frequency_penalty: float = 0.0
presence_penalty: float = 0.0
```

**Impacte**: Menys control sobre generació de text

---

## 🎯 PRIORITAT D'IMPLEMENTACIÓ

### 🔴 ALTA PRIORITAT:

1. **First Message Configuration**
   - Backend: Afegir camps `first_message`, `disable_interruptions`
   - Frontend: Textarea + checkbox a ConvHiAgentConfig tab "General"

2. **System Prompt Structure**
   - Backend: Separar `system_prompt` en camps estructurats
   - Frontend: Afegir tabs "Personality", "Environment" a ConvHiAgentConfig

3. **Tools Enable/Disable**
   - Backend: Afegir `enabled_tools` array
   - Frontend: Afegir toggle switches per cada tool

### 🟡 MITJANA PRIORITAT:

4. **Multi-Language**
   - Backend: Afegir `additional_languages` array
   - Frontend: Afegir flag selector amb múltiples idiomes

5. **Advanced LLM Settings**
   - Backend: Afegir camps `max_response_length`, `top_p`, etc.
   - Frontend: Afegir sliders/inputs a tab "LLM Settings"

### 🟢 BAIXA PRIORITAT:

6. **Custom Tools Integration**
7. **MCP Servers**
8. **Magic Wand AI**

---

## 📝 CANVIS NECESSARIS

### Backend (convhi_agents.py):

```python
class ConvHiAgent(BaseModel):
    # ... existing fields ...
    
    # NOUS CAMPS:
    first_message: Optional[str] = None
    disable_interruptions: bool = False
    
    system_prompt_structure: Dict[str, Any] = {
        'personality': '',
        'environment': '',
        'variables': {}
    }
    
    enabled_tools: List[str] = []
    additional_languages: List[str] = []
    language_auto_detect: bool = False
    
    # Advanced LLM
    max_response_length: int = 500
    stop_sequences: List[str] = []
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
```

### Frontend (ConvHiAgentConfig.jsx):

**Tab 1: General**
- First message (textarea)
- Disable interruptions (checkbox)

**Tab 2: System Prompt**
- Personality (textarea)
- Environment (textarea)
- Dynamic Variables (ja existeix)

**Tab 3: LLM Settings**
- Temperature (slider) ✅ JA EXISTEIX
- Max tokens (input) ✅ JA EXISTEIX
- **NOU**: Max response length (input)
- **NOU**: Top P (slider)
- **NOU**: Frequency penalty (slider)
- **NOU**: Presence penalty (slider)

**Tab 4: Voice**
- Language selector ✅ JA EXISTEIX
- **NOU**: Additional languages (multi-select)
- **NOU**: Auto-detect checkbox

**Tab 5: Tools & Actions**
- **NOU**: Toggle switches per cada tool
- **NOU**: Enable/disable list

**Tab 6: Knowledge Base**
- ✅ JA EXISTEIX

**Tab 7: SIP/WebRTC**
- ✅ JA EXISTEIX


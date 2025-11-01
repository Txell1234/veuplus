# Problema: Opcions Extres No Funcionals

## 🔍 Anàlisi del Problema

### Opcions No Funcionals:
1. ❌ Knowledge base (RAG) - `knowledge_base_enabled`
2. ❌ Turn taking en temps real - `turn_taking_enabled`
3. ❌ Monitoring & logs - `monitoring_enabled`
4. ❌ ASR (transcripció) integrat - `asr_enabled`

## 🐛 Causes Identificades

### 1. Knowledge Base (RAG) - `knowledge_base_enabled`

**Ubicació**: `backend/api/convhi_agents.py` lína 463

**Problema**:
```python
if agent_config.get("knowledge_base_enabled", True) and agent_config.get("rag_enabled", True):
    # Cerca coneixement
```

**El problema**: 
- Sempre fa default a `True` si no està definit
- No es verifica si la configuració està realment activada
- El checkbox al frontend no afecta el comportament del backend

**Solució necessària**:
```python
# Verificar explícitament el config
kb_enabled = agent_config.get("knowledge_base_enabled", False)
rag_enabled = agent_config.get("rag_enabled", False)

if kb_enabled and rag_enabled:
    # Cerca coneixement
else:
    logger.info(f"Knowledge Base deshabilitada per l'agent {agent_id}")
    knowledge_results = []
```

### 2. ASR (Transcripció) - `asr_enabled`

**Ubicació**: `backend/api/convhi_agents.py` lína 337

**Problema**:
```python
# 1. ASR si és àudio
if message.message_type == "audio" and message.audio_data:
    audio_bytes = base64.b64decode(message.audio_data)
    transcribed_text = await asr_engine.transcribe_audio(audio_bytes, agent["language"])
    message.message = transcribed_text
```

**El problema**:
- No verifica `asr_enabled`
- Sempre intenta transcribir si hi ha àudio
- No respecta la configuració de l'usuari

**Solució necessària**:
```python
# 1. ASR si és àudio I està habilitat
if agent_config.get("asr_enabled", False) and message.message_type == "audio" and message.audio_data:
    audio_bytes = base64.b64decode(message.audio_data)
    transcribed_text = await asr_engine.transcribe_audio(audio_bytes, agent["language"])
    message.message = transcribed_text
    logger.info(f"ASR: Transcripció completada")
elif message.message_type == "audio" and not agent_config.get("asr_enabled", False):
    logger.warning(f"ASR deshabilitat però s'ha rebut àudio. Salteant transcripció.")
```

### 3. Turn Taking - `turn_taking_enabled`

**Ubicació**: `backend/api/convhi_agents.py` lína 710

**Comportament actual**:
```python
if not agent["turn_taking_enabled"]:
    return {
        "should_speak": False,
        "reason": "Turn taking deshabilitat"
    }
```

**Aquest SÍ funciona** en l'endpoint `/agents/{agent_id}/turn-taking`, però:
- No s'utilitza en el cicle principal de chat
- Només funciona quan es crida explícitament l'endpoint

**Solució necessària**:
Integrar la verificació de turn_taking en el cicle principal de conversa.

### 4. Monitoring - `monitoring_enabled`

**Ubicació**: `backend/api/convhi_agents.py` lína 531

**Problema**:
```python
await monitoring_system.log_interaction(agent_id, {
    "success": True,
    "response_time": response_time,
    ...
})
```

**El problema**:
- Sempre registra interaccions
- No verifica `monitoring_enabled`
- No respecta la privacitat/configuració

**Solució necessària**:
```python
if agent_config.get("monitoring_enabled", False):
    await monitoring_system.log_interaction(agent_id, {
        "success": True,
        "response_time": response_time,
        ...
    })
else:
    logger.info(f"Monitoring deshabilitat per l'agent {agent_id}")
```

## 🔧 Solucions a Implementar

### Solució 1: Fixar Knowledge Base
- Verificar explícitament `knowledge_base_enabled` abans de cercar
- Retornar llista buida si està deshabilitat

### Solució 2: Fixar ASR
- Verificar `asr_enabled` abans de transcribir
- Ignorar àudio si està deshabilitat

### Solució 3: Fixar Monitoring
- Verificar `monitoring_enabled` abans de registrar
- No fer log si està deshabilitat

### Solució 4: Fixar Turn Taking
- Integrar verificació en cicle principal
- Respetar configuració en tot el flux de conversa

## 📋 Plan d'Implementació

1. Crear funció helper per verificar configs
2. Aplicar verificacions a totes les seccions
3. Afegir logging per indicar quan alguna opció està deshabilitada
4. Provar que els checkboxes del frontend afecten el backend

## 🎯 Resultat Esperat

Després de les correccions:
- ✅ Knowledge Base només actiu si checkbox marcat
- ✅ ASR només transcribe si checkbox marcat
- ✅ Monitoring només registra si checkbox marcat
- ✅ Turn Taking només actiu si checkbox marcat



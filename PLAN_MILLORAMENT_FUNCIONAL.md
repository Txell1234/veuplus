# Plan de Millorament: Fer Funcional

## 🎯 Objectiu
Millorar les funcionalitats actuals per fer-les controlables per l'usuari.

---

## 🔧 Estratègia Per Funcionalitat

### 1. Knowledge Base (RAG)
**Estat actual**: In-memory, busca amb substring
**Millora**: Utilitzar APIs gratuïtes

```python
# Solució: OpenAI Embeddings API
- Convertir documents a embeddings
- Guardar embeddings a SQLite
- Cerca per cosine similarity
- Persistent storage
```

### 2. ASR (Whisper)
**Estat actual**: No instal·lat
**Millora**: API alternativa

```python
# Solució: OpenAI Whisper API (gratuïta inicialment)
- POST /v1/audio/transcriptions
- Accepta .wav, .mp3
- Fàcil d'integrar
- O: Web Speech API del navegador
```

### 3. Turn Taking
**Estat actual**: 3 regles if/else
**Millora**: Audio level detection millorat

```python
# Solució: Millora detecció de silenci
- Detectar silenci amb Web Audio API (frontend)
- Millorar thresholds dinàmics
- Anàlisi de freqüència per detectar parla
```

### 4. Monitoring
**Estat actual**: In-memory comptadors
**Millora**: Database + visualització

```python
# Solució: SQLite persistent
- Guardar cada interacció a SQLite
- Metrics agregats
- Timeline de converses
```

---

## ✅ IMPLEMENTACIÓ PRAGMÀTICA

### Opció A: APIs Externes (Ràpid)
- OpenAI Whisper API per ASR
- OpenAI Embeddings per RAG
- SQLite per storage

### Opció B: Integracions Natives (Mitjà)
- Web Speech API (frontend)
- Sentence Transformers (backend)
- ChromaDB per vector DB

### Opció C: Manual (Senzyll)
- Text input directe
- File upload sense processament
- Metrics a SQLite

---

## 🚀 RECOMANACIÓ: Opció A + C (Híbrid)

1. **ASR**: Web Speech API (frontend) + fallback manual
2. **RAG**: Sentence transformers gratuït
3. **Monitoring**: SQLite persistent
4. **Turn Taking**: Millorar detecció silenci

**Temps estimat**: 2-3 hores



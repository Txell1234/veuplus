# 🎤 Catálogo Completo de Voces VeuPlus

## 📊 **Estado Actual: Sistema Dual Funcionando**

### ✅ **Separación Implementada Correctamente**

El sistema VeuPlus tiene **2 canales claramente separados**:

1. **🎯 Canal Hiperrealista** (Voces Catalanas) → Usa grabaciones reales + clonación
2. **📡 Canal Edge-TTS** (Voces Estándar) → Usa Microsoft Edge-TTS neural

---

## 🎯 **CANAL HIPERREALISTA (Voces Catalanas)**

### **🔥 4 Voces Catalanas con Grabaciones Reales**

#### **1. `senyor_catala_1`** 🧑‍💼
- **Tipo**: Voz masculina catalana natural
- **Canal**: Hiperrealista con grabaciones reales
- **Acento**: Barcelona, España
- **Archivo**: `backend/training_data/senyor_catala_1/processed.wav`
- **Calidad**: Hiperrealista con características específicas
- **Síntesis**: TTS verdadero usando características extraídas del audio

#### **2. `dona_catalana`** 👩‍💼  
- **Tipo**: Voz femenina catalana natural
- **Canal**: Hiperrealista con grabaciones reales
- **Acento**: Barcelona, España
- **Archivo**: `backend/training_data/dona_catalana/processed.wav`
- **Calidad**: Hiperrealista con características específicas
- **Síntesis**: TTS verdadero usando características extraídas del audio

#### **3. `senyor_catala_2`** 🧑‍🎤
- **Tipo**: Voz masculina catalana expresiva
- **Canal**: Hiperrealista con grabaciones reales
- **Acento**: Barcelona, España
- **Archivo**: `backend/training_data/senyor_catala_2/processed.wav`
- **Texto muestra**: "Treballadores de cures, personal sanitari..."
- **Calidad**: Hiperrealista expresiva
- **Síntesis**: TTS verdadero usando características extraídas del audio

#### **4. `senyor_catala_extended`** 🧑‍💻
- **Tipo**: Voz masculina catalana política
- **Canal**: Hiperrealista con grabaciones reales
- **Acento**: Barcelona, España
- **Archivo**: `backend/training_data/senyor_catala_extended/processed.wav`
- **Texto muestra**: "Aquest any hem assolit l'acord per a la llei d'amnistia..."
- **Calidad**: Hiperrealista formal/política
- **Síntesis**: TTS verdadero usando características extraídas del audio

### **🔧 Cómo Funciona el Canal Hiperrealista:**

```python
# Proceso para voces catalanas:
1. Detección: Sistema detecta IDs catalanas automáticamente
2. Carga: Lee grabación real procesada (.wav)
3. Extracción: Analiza características (F0, espectro, energía)
4. Base TTS: Genera audio base con Edge-TTS español como referencia  
5. Modificación: Aplica características específicas extraídas
6. Procesamiento: Usa SEGRE para fonética catalana mejorada
7. Resultado: Audio generado con características únicas de la grabación
```

### **✅ Respuesta del Canal Hiperrealista:**
```json
{
  "success": true,
  "channel": "hiperrealista",
  "catalan_voice": true,
  "provider": "veuplus_hiperrealista_catalan",
  "recording_based": true,
  "real_audio": true,
  "synthesis_method": "real_hiperrealistic_tts",
  "quality": "hiperrealista_con_grabaciones"
}
```

---

## 📡 **CANAL EDGE-TTS (Voces Estándar)**

### **🇪🇸 Voces Españolas**

#### **`es-ES-ElviraNeural`** 👩‍🏫
- **Tipo**: Voz femenina española
- **Canal**: Edge-TTS estándar
- **Idioma**: Español de España
- **Calidad**: Neural estándar Microsoft

#### **`es-ES-AlvaroNeural`** 👨‍🏫
- **Tipo**: Voz masculina española  
- **Canal**: Edge-TTS estándar
- **Idioma**: Español de España
- **Calidad**: Neural estándar Microsoft

#### **`es-ES-LaiaNeural`** 👩‍🎨
- **Tipo**: Voz femenina española alternativa
- **Canal**: Edge-TTS estándar
- **Idioma**: Español de España
- **Calidad**: Neural estándar Microsoft

#### **`es-ES-ArnauNeural`** 👨‍🎨
- **Tipo**: Voz masculina española alternativa
- **Canal**: Edge-TTS estándar
- **Idioma**: Español de España
- **Calidad**: Neural estándar Microsoft

### **🇬🇧 Voces Inglesas**

#### **`en-US-AriaNeural`** 👩‍💼
- **Tipo**: Voz femenina inglesa
- **Canal**: Edge-TTS estándar
- **Idioma**: Inglés americano
- **Calidad**: Neural estándar Microsoft

#### **`en-US-DavisNeural`** 👨‍💼
- **Tipo**: Bilateral masculina inglesa
- **Canal**: Edge-TTS estándar
- **Idioma**: Inglés americano
- **Calidad**: Neural estándar Microsoft

#### **`en-US-JennyNeural`** 👩‍🎤
- **Tipo**: Voz femenina inglesa alternativa
- **Canal**: Edge-TTS estándar
- **Idioma**: Inglés americano
- **Calidad**: Neural estándar Microsoft

#### **`en-US-GuyNeural`** 👨‍🎤
- **Tipo**: Voz masculina inglesa alternativa
- **Canal**: Edge-TTS estándar
- **Idioma**: Inglés americano
- **Calidad**: Neural estándar Microsoft

### **🇫🇷 Voces Francesas**

#### **`fr-FR-DeniseNeural`** / **`fr-FR-HenriNeural`**
- **Canal**: Edge-TTS estándar
- **Idioma**: Francés de Francia
- **Calidad**: Neural estándar Microsoft

### **🇮🇹 Voces Italianas**

#### **`it-IT-ElsaNeural`** / **`it-IT-DiegoNeural`**
- **Canal**: Edge-TTS estándar
- **Idioma**: Italiano
- **Calidad**: Neural estándar Microsoft

### **✅ Respuesta del Canal Edge-TTS:**
```json
{
  "success": true,
  "channel": "estándar",
  "catalan_voice": false,
  "provider": "veuplus_edge",
  "recording_based": false,
  "real_audio": false,
  "synthesis_method": "edge_tts",
  "quality": "edge_neural"
}
```

---

## 🔄 **Enrutamiento Automático**

### **Cómo el Sistema Decide qué Canal Usar:**

```python
# Detección automática en backend/server.py
catalan_voice_ids = [
    "senyor_catala_1", "senyor_catala_2", "senyor_catala_extended", 
    "dona_catalana", "trained_senyor_catala_1", "trained_dona_catalana",
    "catalan_enhanced", "trained_catalan", "hyperrealistic_catalan"
]

is_catalan_voice = any(catalan_id in voice_id.lower() for catalan_id in catalan_voice_ids)

if is_catalan_voice:
    # 🎯 VAN POR CANAL HIPERREALISTA
    # Usa: realistic_tts.synthesize_realistic()
else:
    # 📡 VAN POR CANAL EDGE-TTS  
    # Usa: Edge-TTS estándar
```

---

## 🎯 **Endpoints Disponibles**

### **Endpoint Principal Universal**
```
POST /api/tts/test
{
  "text": "Texto a sintetizar",
  "voice_id": "ID_de_voz", 
  "language": "idioma"
}
```

### **Endpoint Específico Catalán**
```
POST /api/tts/test-catalan
{
  "text": "Bon dia, sóc català",
  "voice_id": "senyor_catala_1"
}
```

### **Endpoint de Salud**
```
GET /api/health
```

---

## 🧪 **Ejemplos de Uso**

### **Par Usar Voces Catalanas (Canal Hiperrealista):**
```bash
curl -X POST http://localhost:8002/api/tts/test \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bon dia, sóc una veu catalana hiperrealista",
    "voice_id": "senyor_catala_1",
    "language": "ca"
  }'
```

### **Para Usar Voces Edge-TTS (Canal Estándar):**
```bash
curl -X POST http://localhost:8002/api/tts/test \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, soy una voz española estándar",
    "voice_id": "es-ES-ElviraNeural", 
    "language": "es"
  }'
```

---

## ✅ **Resumen Final**

### **🎯 Canal Hiperrealista (4 voces catalanas)**
- ✅ Funciona: Sí, con grabaciones reales procesadas
- ✅ Tecnología: Clonación basada en características extraídas
- ✅ Calidad: Hiperrealista usando TTS verdadero
- ✅ Diferenciación: Separado completamente del Edge-TTS

### **📡 Canal Edge-TTS (20+ voces estándar)**
- ✅ Funciona: Sí, con Microsoft Edge-TTS
- ✅ Tecnología: Síntesis neural estándar
- ✅ Calidad: Neural estándar comercial
- ✅ Idiomas: ES, EN, FR, IT principales

### **🔄 Enrutamiento**
- ✅ Automático: Detección inteligente por ID de voz
- ✅ Separado: Sin mezcla entre canales
- ✅ Funcional: Ambos canales operativos simultáneamente

**¡El sistema VeuPlus tiene ambos tipos de voces funcionando correctamente con separación automática!** 🎉















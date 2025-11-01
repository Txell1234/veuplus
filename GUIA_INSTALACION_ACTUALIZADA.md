# 🚀 Guía de Instalación y Uso - VeuPlus 2.1.0

**Actualizado:** 10 de octubre de 2025

### Branding AT Hub

- Logo: frontend/src/assets/ambtu-logo.svg
- Colors principals: blau navy #0f1f68, blau profund #07144a i accent taronja #ff6537
- Tailwind ja defineix primary/accent/slate amb aquesta paleta
- Usa aquestes referencies per a qualsevol captura o manual

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Python:** 3.10 o superior (recomendado 3.11+)
- **Node.js:** 18.x o superior
- **RAM:** 8 GB mínimo (16 GB recomendado)
- **Espacio en disco:** 5 GB mínimo
- **Sistema operativo:** Windows 10/11, Linux, macOS

### Requisitos Opcionales (para mejor rendimiento)
- **GPU:** NVIDIA con CUDA 11.8+ (para TTS avanzado y LLMs locales)
- **Docker:** 24.x o superior (para deployment en contenedores)

---

## 🔧 Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/VeusPlus.git
cd VeusPlus
```

### 2. Configurar Backend (Python)

#### Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Nota:** La instalación puede tardar 10-15 minutos dependiendo de tu conexión y sistema.

### 3. Configurar Frontend (React)

```bash
cd frontend
npm install
cd ..
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de configuración de ejemplo
cp config.example.env .env
```

Edita el archivo `.env` con tus claves API (opcional, solo si usas servicios externos):

```env
# Ejemplo: Configurar OpenAI
OPENAI_API_KEY=sk-tu-clave-api-aqui

# Ejemplo: Configurar Gemini
GEMINI_API_KEY=tu-clave-gemini-aqui
```

**Nota:** VeuPlus funciona perfectamente sin configurar ninguna API externa, usando los modelos locales.

**ConvHi:** si desplegas agents conversacionals, define estas variables adicionales:

- `CONVHI_WIDGET_SECRET`: clau que signa les URLs del widget incrustable.
- `CONVHI_WIDGET_ALLOWLIST`: dominios permitidos (separados por coma) para cargar el widget.
- `CONVHI_WEBHOOK_SECRET`: secret HMAC para verificar eventos de post-call.
- `CONVHI_WEBHOOK_STORE`: opcional, fija `false` si no quieres persistir los eventos en SQLite.

---

## ▶️ Ejecución

### Opción 1: Ejecución Manual (Desarrollo)

#### Terminal 1 - Backend
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Linux/macOS

# Iniciar backend
cd backend
python server.py
```

El backend estará disponible en: `http://localhost:8001`

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

### Opción 2: Scripts de Inicio Rápido (Windows)

#### Backend
```powershell
.\start_backend.ps1
```

#### Frontend
```powershell
.\start_frontend.ps1
```

### Opción 3: Docker (Producción)

```bash
# Iniciar todos los servicios
docker compose up --build -d

# Ver logs
docker compose logs -f

# Detener servicios
docker compose down
```

Acceso:
- **Frontend + Backend:** `http://localhost:8080`
- **API Docs:** `http://localhost:8080/docs`

---

## 🎯 Verificación de Instalación

### 1. Verificar Backend

Abre tu navegador en: `http://localhost:8001/docs`

Deberías ver la documentación interactiva de la API (Swagger UI).

### 2. Probar TTS Catalán

```bash
curl -X POST "http://localhost:8001/api/tts/test-catalan" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bon dia, benvingut a VeuPlus",
    "voice_id": "senyor_catala_1"
  }'
```

### 3. Verificar Frontend

Abre tu navegador en: `http://localhost:5173` (desarrollo) o `http://localhost:8080` (Docker)

---

## 🎤 Uso Básico

### Síntesis de Voz (TTS)

#### Voces Disponibles

**Voces Catalanas Hiperrealistas:**
- `senyor_catala_1` - Voz masculina catalana 1
- `senyor_catala_2` - Voz masculina catalana 2
- `senyor_catala_extended` - Voz masculina catalana extendida
- `dona_catalana` - Voz femenina catalana

**Voces Edge-TTS (20+ idiomas):**
- `system_helena` - Español (España) - Femenina
- `system_david` - Inglés (EE.UU.) - Masculina
- `system_hazel` - Inglés (Reino Unido) - Femenina
- Y más...

#### Ejemplo con Python

```python
import requests
import base64

# Configurar petición
url = "http://localhost:8001/api/tts/test-catalan"
data = {
    "text": "Bon dia, aquesta és una prova del sistema VeuPlus",
    "voice_id": "senyor_catala_1"
}

# Realizar síntesis
response = requests.post(url, json=data)
result = response.json()

if result.get("success"):
    # Guardar audio
    audio_bytes = base64.b64decode(result["audio_base64"])
    with open("output.wav", "wb") as f:
        f.write(audio_bytes)
    print("✅ Audio generado exitosamente")
else:
    print(f"❌ Error: {result.get('error')}")
```

### Chatbots y Voicebots

#### Crear un Chatbot

```python
import requests

url = "http://localhost:8001/api/chatbots"
data = {
    "name": "Mi Asistente",
    "description": "Asistente virtual personalizado",
    "llm_provider": "local",  # o "openai", "gemini", etc.
    "llm_model": "",  # Vacío usa el modelo por defecto
    "system_prompt": "Eres un asistente útil y amigable.",
    "language": "ca"
}

response = requests.post(url, json=data)
chatbot = response.json()
print(f"Chatbot creado: {chatbot['id']}")
```

#### Conversar con el Chatbot

```python
url = "http://localhost:8001/api/chatbots/chat"
data = {
    "chatbot_id": chatbot['id'],
    "message": "Hola, com estàs?",
    "session_id": "session-123"  # Opcional, para mantener contexto
}

response = requests.post(url, json=data)
reply = response.json()
print(f"Respuesta: {reply['reply']}")
```

---

## ⚙️ Configuración Avanzada

### LLM Providers

VeuPlus soporta múltiples proveedores de LLM:

#### 1. OpenAI (GPT-4, GPT-3.5, etc.)
```env
OPENAI_API_KEY=sk-tu-clave-aqui
DEFAULT_LLM_PROVIDER=openai
```

#### 2. Google Gemini
```env
GEMINI_API_KEY=tu-clave-aqui
DEFAULT_LLM_PROVIDER=gemini
```

#### 3. Anthropic Claude
```env
ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui
DEFAULT_LLM_PROVIDER=anthropic
```

#### 4. Ollama (Local)
```bash
# Instalar Ollama: https://ollama.ai
ollama pull llama3
```

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_PROVIDER=ollama
```

#### 5. vLLM (Local, para GPT-OSS-20B)
```bash
# Iniciar vLLM
.\start_veuplus_vllm.ps1
```

### Ajustar Rendimiento

#### Aumentar Workers del Servidor
```env
SERVER_WORKERS=4  # Aumenta para más concurrencia
```

#### Ajustar Timeouts
```env
TTS_TIMEOUT_SEC=180  # Para textos muy largos
OPENAI_TIMEOUT_SEC=90  # Si tienes conexión lenta
```

#### Optimizar Cache
```env
MAX_CACHE_ITEMS=500  # Aumenta para cachear más síntesis
CACHE_TTL_SECONDS=7200  # Cache más duradero
```

---

## 🐛 Solución de Problemas

### Error: "Module not found"

**Solución:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Error: "Port already in use"

**Solución:** Cambiar puerto en `.env`:
```env
SERVER_PORT=8002
```

### Error: Edge-TTS no funciona

**Solución:**
```bash
pip install --upgrade edge-tts
```

### Audio generado está vacío o corrupto

**Verificar:**
1. Que la voz solicitada existe
2. Que el texto no está vacío
3. Revisar logs del servidor para errores

### Frontend no se conecta al Backend

**Solución:** Verificar CORS en `.env`:
```env
API_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📚 Documentación Adicional

- **README principal:** `README.md`
- **Backend README:** `BACKEND_README.md`
- **Catálogo de voces:** `CATALOGO_VOCES_VEUPLUS.md`
- **Análisis completo:** `ANALISIS_VEUPLUS_COMPLETO.md`
- **Resumen funcional:** `RESUMEN_VEUPLUS.md`

---

## 🔄 Actualización desde versión anterior

Si ya tienes VeuPlus instalado:

```bash
# 1. Hacer backup de la base de datos
cp backend/veuplus.db backend/veuplus.db.backup

# 2. Actualizar código
git pull

# 3. Actualizar dependencias Python
pip install -r requirements.txt --upgrade

# 4. Actualizar dependencias Frontend
cd frontend
npm install
cd ..

# 5. Revisar nuevas variables de entorno
# Compara tu .env con config.example.env

# 6. Reiniciar servicios
```

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs del servidor:** Los errores detallados aparecen en la consola
2. **Verifica la documentación API:** `http://localhost:8001/docs`
3. **Consulta los archivos de documentación** en el repositorio
4. **Abre un issue** en GitHub con:
   - Descripción del problema
   - Logs relevantes
   - Pasos para reproducir

---

## ✅ Checklist de Instalación Exitosa

- [ ] Python 3.10+ instalado
- [ ] Node.js 18+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias Python instaladas
- [ ] Dependencias Frontend instaladas
- [ ] Archivo .env configurado
- [ ] Backend arranca sin errores
- [ ] Frontend arranca sin errores
- [ ] Swagger UI accesible en /docs
- [ ] Test de TTS funciona correctamente

---

**¡Felicidades! VeuPlus está listo para usar.** 🎉


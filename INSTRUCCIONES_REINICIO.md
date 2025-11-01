# 🔄 Instrucciones para Reiniciar VeusPlus

## ✅ ARREGLOS APLICADOS

Se han corregido todos los problemas de importación en `backend/server.py`:
- ✅ Routers de API (catalán, edge-tts, voices, tts, asr, chat)
- ✅ Motor Realistic Catalan TTS
- ✅ Motor Edge-TTS Engine
- ✅ Sistema de clonación de voz real
- ✅ Transcriptor fonético SEGRE

---

## 📋 PASOS PARA REINICIAR (CMD/PowerShell)

### 1️⃣ Detener los servidores actuales

En AMBAS ventanas donde están corriendo (backend y frontend):
- Presiona **Ctrl+C**
- Espera a que se detengan completamente

---

### 2️⃣ Reiniciar Backend

En la ventana del **backend**, ejecuta:

```cmd
cd C:\Users\merit\Desktop\VeusPlus\backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Espera a ver:**
```
✅ Routers específicos cargados: catalán, edge-tts, voices, tts, asr, chat
✅ Realistic Catalan TTS engine available (MOTOR PRINCIPAL)
INFO:     Application startup complete.
```

---

### 3️⃣ Reiniciar Frontend

En la ventana del **frontend**, ejecuta:

```cmd
cd C:\Users\merit\Desktop\VeusPlus\frontend
npm run dev
```

**Espera a ver:**
```
➜  Local:   http://localhost:3000/
```

---

### 4️⃣ Abrir en el Navegador

Abre: **http://localhost:3000**

---

## 🎯 Qué deberías ver ahora

1. **Sin errores** de importación en el backend
2. **Dos pestañas nuevas** en el menú lateral:
   - ⚡ **Veus Hiperrealistes** (badge: Català)
   - 📡 **Veus Edge-TTS** (badge: Multiidioma)

---

## 🧪 Cómo probar que funciona

### Probar Voces Catalanas Hiperrealistes:
1. Click en "Veus Hiperrealistes"
2. Escribe: "Bon dia, aquesta és una prova"
3. Selecciona una voz (ej: Senyor Català 1)
4. Click "Generar Audio Hiperrealista"
5. Debería generar audio correctamente

### Probar Edge-TTS:
1. Click en "Veus Edge-TTS"  
2. Escribe: "Hello, this is a test"
3. Selecciona una voz (ej: Aria - English)
4. Click "Generar Audio Edge-TTS"
5. Debería generar audio correctamente

---

## ❌ Si aún ves errores

Copia el mensaje de error COMPLETO y compártelo.

Los errores más comunes ya están arreglados:
- ✅ "No module named 'backend.api'"
- ✅ "No module named 'backend.realistic_catalan_tts'"
- ✅ "No module named 'backend.edge_tts_engine'"

---

## 📞 Endpoints API disponibles

Una vez arrancado, estos endpoints deberían funcionar:

- **Catalán:** `POST http://localhost:8001/api/catalan/synthesize`
- **Edge-TTS:** `POST http://localhost:8001/api/edge/synthesize`
- **Health:** `GET http://localhost:8001/api/health`
- **Docs:** http://localhost:8001/docs

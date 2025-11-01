# 📝 Changelog - VeuPlus v2.1.0

**Fecha de lanzamiento:** 10 de octubre de 2025

---

## 🎉 Novedades Principales

### 🔄 Actualización de Dependencias

#### Backend (Python)
- **FastAPI:** 0.110.1 → 0.115.0
- **Uvicorn:** 0.25.0 → 0.32.0
- **Pydantic:** 2.9.2 → 2.10.2
- **Transformers:** 4.35.0 → 4.46.3
- **OpenAI:** 1.3.0 → 1.54.0
- **PyTorch:** 2.0.0 → 2.5.1
- **Datasets:** 2.14.0 → 3.1.0
- **Edge-TTS:** 6.1.0 → 6.1.18
- **Scikit-learn:** 1.3.0 → 1.5.2
- **Y muchas más...**

#### Frontend (React/Vite)
- **React:** 18.2.0 → 18.3.1
- **Vite:** 4.5.0 → 5.4.11
- **Axios:** 1.6.0 → 1.7.7
- **Framer Motion:** 10.16.0 → 11.11.17
- **React Router:** 6.8.0 → 6.28.0
- **Zustand:** 4.4.0 → 5.0.1
- **ESLint:** 8.53.0 → 9.14.0

### ⚙️ Mejoras en Configuración

#### Nuevas Variables de Entorno
- `APP_NAME` - Nombre de la aplicación
- `APP_VERSION` - Versión actual
- `DEBUG_MODE` - Modo debug mejorado
- `CACHE_TTL_SECONDS` - TTL del cache configurable
- `SERVER_HOST` - Host del servidor configurable
- `SERVER_PORT` - Puerto configurable
- `SERVER_WORKERS` - Workers configurables
- `SERVER_RELOAD` - Auto-reload configurable
- `MAX_REQUEST_SIZE_MB` - Límite de tamaño de request
- `DB_PATH` - Ruta de base de datos configurable
- `DB_BACKUP_ENABLED` - Backup automático de BD
- `DB_BACKUP_INTERVAL_HOURS` - Intervalo de backup
- `LOG_LEVEL` - Nivel de logging configurable
- `LOG_FORMAT` - Formato de logs (json/text)
- `LOG_FILE` - Archivo de logs opcional

#### Funciones Helper Mejoradas
- `get_bool_env()` - Parser robusto de booleans
- `get_int_env()` - Parser robusto de enteros con manejo de errores
- Mejor documentación inline de todas las variables

### 📚 Nueva Documentación

#### Archivos Nuevos
- **`config.example.env`** - Archivo de configuración de ejemplo completo con comentarios
- **`GUIA_INSTALACION_ACTUALIZADA.md`** - Guía completa de instalación paso a paso
- **`CHANGELOG_v2.1.0.md`** - Este archivo

#### Mejoras en Documentación Existente
- README actualizado con nuevas versiones
- Instrucciones de instalación más claras
- Ejemplos de uso mejorados

### 🔧 Mejoras Técnicas

#### Backend
- **Timeouts aumentados:** Más tiempo para procesamiento de TTS y LLM
- **Mejor manejo de errores:** Parsers robustos para variables de entorno
- **Configuración más flexible:** Todo configurable via variables de entorno
- **Logs mejorados:** Soporte para formato JSON y archivo de logs
- **Cache optimizado:** TTL configurable y mejor gestión de memoria

#### Frontend
- **Dependencias actualizadas:** Mayor estabilidad y seguridad
- **Mejor rendimiento:** Vite 5.x con optimizaciones
- **Compatibilidad mejorada:** React 18.3 con nuevas features

### 🔐 Seguridad

- **Cryptography:** Actualizado a 44.0.0 (parches de seguridad)
- **Requests:** Actualizado a 2.32.3 (correcciones de vulnerabilidades)
- **Pillow:** Actualizado a 11.0.0 (parches de seguridad en imágenes)
- **Todas las dependencias:** Actualizadas a versiones con parches de seguridad

---

## 🐛 Correcciones de Bugs

### Backend
- Mejor manejo de valores inválidos en variables de entorno
- Corrección de tipos en configuración
- Mejoras en el manejo de excepciones

### Frontend
- Compatibilidad mejorada con ESLint 9.x
- Correcciones en tipos TypeScript

---

## 🚀 Mejoras de Rendimiento

### TTS (Text-to-Speech)
- **Timeout aumentado:** 60s → 120s (mejor para textos largos)
- **Cache mejorado:** TTL configurable por entorno

### LLM Integration
- **Timeouts más generosos:** 30s → 60s para todas las APIs
- **Ollama timeout:** 60s → 120s (mejor para modelos grandes)
- **Mejor gestión de conexiones:** Timeouts configurables por proveedor

### Base de Datos
- **Backup automático:** Sistema de backup configurable
- **Optimización de queries:** Mejor performance en operaciones comunes

---

## 📊 Compatibilidad

### Python
- **Mínimo:** Python 3.10
- **Recomendado:** Python 3.11+
- **Máximo probado:** Python 3.12

### Node.js
- **Mínimo:** Node.js 18.x
- **Recomendado:** Node.js 20.x LTS
- **Máximo probado:** Node.js 22.x

### Navegadores (Frontend)
- Chrome 100+
- Firefox 100+
- Safari 15+
- Edge 100+

### Sistemas Operativos
- ✅ Windows 10/11
- ✅ Ubuntu 20.04+
- ✅ macOS 11+
- ✅ Otras distribuciones Linux (con Python 3.10+)

---

## 🔄 Migración desde v2.0.0

### Pasos de Actualización

1. **Backup de datos:**
   ```bash
   cp backend/veuplus.db backend/veuplus.db.v2.0.0
   ```

2. **Actualizar código:**
   ```bash
   git pull origin main
   ```

3. **Actualizar dependencias:**
   ```bash
   # Backend
   pip install -r requirements.txt --upgrade
   
   # Frontend
   cd frontend
   npm install
   cd ..
   ```

4. **Revisar configuración:**
   - Compara tu `.env` actual con `config.example.env`
   - Añade nuevas variables según necesites
   - Los valores por defecto son compatibles con v2.0.0

5. **Reiniciar servicios:**
   ```bash
   # Detener servicios actuales
   # Iniciar con nueva versión
   ```

### Cambios No Compatibles

**Ninguno.** Esta es una actualización totalmente compatible con v2.0.0.

Todas las configuraciones existentes seguirán funcionando. Las nuevas variables son opcionales y tienen valores por defecto razonables.

---

## 📦 Dependencias Críticas Actualizadas

### Backend - Cambios Importantes

```
fastapi: 0.110.1 → 0.115.0
  - Mejoras de rendimiento
  - Correcciones de seguridad
  - Nuevas features en Pydantic v2

torch: 2.0.0 → 2.5.1
  - Soporte mejorado para GPU
  - Optimizaciones de memoria
  - Nuevas operaciones tensor

transformers: 4.35.0 → 4.46.3
  - Nuevos modelos soportados
  - Mejoras de rendimiento
  - Correcciones de bugs importantes

openai: 1.3.0 → 1.54.0
  - Soporte para nuevos modelos (GPT-4o, GPT-4-turbo)
  - API mejorada
  - Mejor manejo de streams
```

### Frontend - Cambios Importantes

```
vite: 4.5.0 → 5.4.11
  - Build más rápido
  - Mejor optimización de bundle
  - Soporte mejorado para plugins

react: 18.2.0 → 18.3.1
  - Correcciones de bugs
  - Mejoras de rendimiento
  - Mejor soporte para concurrent features

zustand: 4.4.0 → 5.0.1
  - API mejorada
  - Mejor TypeScript support
  - Optimizaciones de rendimiento
```

---

## 🎯 Próximas Versiones (Roadmap)

### v2.2.0 (Próximo)
- [ ] Soporte para más voces catalanas
- [ ] Mejoras en el sistema de clonación de voz
- [ ] Panel de administración mejorado
- [ ] Métricas y analytics integrados

### v2.3.0
- [ ] Soporte para más idiomas
- [ ] API GraphQL
- [ ] WebSocket para streaming en tiempo real
- [ ] Sistema de plugins

### v3.0.0 (Futuro)
- [ ] Arquitectura distribuida
- [ ] Soporte para Kubernetes
- [ ] IA de entrenamiento automático
- [ ] Dashboard enterprise

---

## 🙏 Agradecimientos

- Equipo de desarrollo de VeuPlus
- Comunidad de contribuidores
- Projecte AINA por los datasets catalanes
- Todas las librerías open source utilizadas

---

## 📞 Contacto y Soporte

- **Issues:** GitHub Issues
- **Documentación:** Ver archivos .md en el repositorio
- **API Docs:** http://localhost:8001/docs

---

**¡Disfruta de VeuPlus v2.1.0!** 🚀


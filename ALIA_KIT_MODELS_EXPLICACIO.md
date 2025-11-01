# 🎯 ALIA Kit - Models BSC vs Edge-TTS

## ✅ Tens Raó!

ALIA Kit **NO hauria de funcionar amb Edge-TTS**. Hauria d'usar **models BSC reals** del Barcelona Supercomputing Center.

---

## 🔄 Solució Implementada

He creat un sistema amb **2 nivells**:

### 1. **ALIA Kit Real BSC** (Preferit)
- ✅ Usa models TTS oficials del BSC via Coqui TTS
- ✅ Models del Projecte AINA
- ✅ Qualitat professional BSC
- ⚠️ Requereix: `pip install TTS`

### 2. **Fallback Edge-TTS** (Si BSC no disponible)
- ⚪ Edge-TTS optimitzat amb SEGRE
- ⚪ Veus catalanes natives de Microsoft
- ⚪ Funciona sempre, però no és BSC oficial

---

## 📦 Com Funciona Ara

### Sistema de Fallback Intel·ligent:

```python
1. Intentar carregar alia_kit_real_bsc (models BSC)
   ✅ SI: Usar models BSC oficials
   ❌ NO: 
       2. Carregar alia_kit_fixed (Edge-TTS + SEGRE)
          ✅ SI: Usar Edge-TTS com a fallback
          ❌ NO: Error
```

---

## 🚀 Per Usar Models BSC Reals

### Instal·la Coqui TTS:

```bash
pip install TTS
```

### Reinicia el servidor:

```powershell
cd C:\Users\merit\Desktop\VeusPlus\backend
python server.py
```

### Verifica als logs:

```
✅ alia_kit_real_bsc loaded successfully (models BSC)
```

---

## 📊 Diferències

| Aspecte | ALIA Kit BSC Real | Edge-TTS Fallback |
|---------|-------------------|-------------------|
| **Models** | BSC/AINA oficials | Microsoft Edge |
| **Qualitat** | Professional BSC | Alta (Microsoft) |
| **SEGRE** | ✅ Sí | ✅ Sí |
| **Instal·lació** | `pip install TTS` | `pip install edge-tts` |
| **Mida** | ~500MB | ~50MB |
| **Velocitat** | Mitjana | Ràpida |
| **Offline** | ✅ Sí | ❌ No (necessita internet) |

---

## 🎯 Recomanació

### Per Producció (Qualitat BSC):
```bash
pip install TTS
```

### Per Proves Ràpides:
```bash
pip install edge-tts
```

---

## 🔍 Verificar Quin S'està Usant

### Als logs del backend:

**Models BSC:**
```
✅ alia_kit_real_bsc loaded successfully (models BSC)
🎯 ALIA Kit BSC TTS: 'Hola...' en ca
✅ ALIA Kit BSC exitós (xxxxx bytes)
```

**Edge-TTS Fallback:**
```
⚠️ alia_kit_real_bsc not available: ...
✅ alia_kit_fixed loaded as fallback (Edge-TTS)
🎯 ALIA Kit BSC TTS: 'Hola...' en ca
✅ ALIA Kit TTS exitoso: ca-ES-EnricNeural
```

---

## 📝 Fitxers

### Models BSC Real:
- `backend/alia_kit_real_bsc.py` - Implementació BSC amb Coqui TTS

### Fallback Edge-TTS:
- `backend/alia_kit_fixed.py` - Implementació Edge-TTS optimitzada

### API:
- `backend/api/alia.py` - Sistema de fallback automàtic

---

## ✅ Estat Actual

**Ara mateix:**
- ✅ Sistema de fallback implementat
- ✅ Models BSC disponibles si Coqui TTS instal·lat
- ✅ Edge-TTS com a fallback si BSC no disponible
- ✅ SEGRE aplicat en tots dos casos

**Per usar BSC real:**
```bash
pip install TTS
# Reinicia servidor
```

---

**Tens raó que ALIA Kit hauria de ser BSC, no Edge-TTS. Ara ja tens l'opció de triar! 🎉**


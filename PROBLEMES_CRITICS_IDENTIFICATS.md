# Problemes Crítics Identificats

## 🔴 Errors Detectats

### 1. Backend No Arrencant
**Error**: `No module named 'edge_tts'`
**Impacte**: Tots els endpoints retornen 500 o 404
**Causa**: Dependències no instal·lades al venv

### 2. Endpoints 404
**Errors**: 
- `/api/convhi/agents` → 404
- `/api/edge-tts/voices` → 500
- `/api/convhi/analytics/*` → 404

**Causa**: Backend no està funcionant

### 3. Interfície Amb Problemes
**Error**: "Les pestanyes no càpiguen"
**Causa**: Navegació massa llarga, necessita millorar Layout

---

## 🎯 Arquitectura Sol·licitada per Usuari

### Concepte Clau (segons imatge):
"Cada SIP trunk, cada WebRTC, cada connexió ha d'estar vinculada a un agent. Poden haver-hi molts agents diferents connectats cada un a diferents bandes."

### Model Sol·licitat:
```
Agent 1 → SIP Trunk A → Config
Agent 1 → WebRTC A → Config
Agent 2 → SIP Trunk B → Config
Agent 2 → WebRTC B → Config
...
```

**Avui**: Hem creat configuracions SEPARADES per SIP i WebRTC
**Necessari**: VINCULAR tot a agents específics

---

## ✅ Solució Necessària

### 1. Arreglar Backend IMMEDIATAMENT
```bash
cd backend
pip install edge-tts fastapi uvicorn
python server.py
```

### 2. Modificar Arquitectura
**Actual**: ConvHiSIPConfig.jsx (config global)
**Necessari**: Config SIP per agent específic

**Actual**: ConvHiWebRTCConfig.jsx (config global)
**Necessari**: Config WebRTC per agent específic

### 3. Millorar Interfície
**Problema**: Navegació massa llarga
**Solució**: 
- Reorganitzar Layout
- Agrupar per categories
- Col·lapsable

---

## 🚨 Accions Prioritàries

### IMMEDIAT (Ara):
1. ❌ Instal·lar dependències backend
2. ❌ Arrencar backend
3. ❌ Verificar endpoints funcionen

### IMPORTANT (Després):
1. ⚠️ Modificar SIP Config per agent
2. ⚠️ Modificar WebRTC Config per agent
3. ⚠️ Millorar Layout navigation

### DESITJABLE (Futur):
1. 💡 Implementar vinculació agent ↔ SIP ↔ WebRTC
2. 💡 Dashboard per veure totes les connexions
3. 💡 Monitoring per agent

---

## 📝 Referències

Imatge mostra:
- Navegació lateral amb múltiples opcions
- Dashboard amb activitat recent
- Analytics parcialment visible
- Sistema funcional que necessita millores UX




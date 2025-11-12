# Planificació: Millora Wizard d'Agents

## 🎯 Problema Actual

**Ubicació**: `frontend/src/pages/ConvHiAgentWizard.jsx` (línies 182-197)

**Checkboxes inútils**:
```jsx
<p className="font-semibold text-neutral-700">Activar opcions extres</p>
<div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
  {[
    { key: 'knowledgeBaseEnabled', label: 'Knowledge base (RAG)' },
    { key: 'turnTakingEnabled', label: 'Turn taking en temps real' },
    { key: 'monitoringEnabled', label: 'Monitoring & logs' },
    { key: 'asrEnabled', label: 'ASR (transcripció) integrat' },
  ].map((item) => (
    <label key={item.key}>
      <input type="checkbox" checked={formState[item.key]} />
      {item.label}
    </label>
  ))}
</div>
```

❌ **Problemes**:
- Només enable/disable
- No configurar
- No veure resultats
- No test connection
- No upload documents

---

## ✅ Solució: Millorar Wizard

### Opció 1: Eliminar Checkboxes, Anar Directament a Config
**Abans**: Wizard → Crear Agent → Checkboxes
**Després**: Wizard → Crear Agent → Anar a `/convhi-agents/config/:id`

**Canvi**: Després de crear l'agent, redirigir automàticament a la pàgina de configuració completa.

### Opció 2: Afegir Configuració Ràpida al Wizard
**Millora**: Afegir tabs de configuració al wizard mateix

### Opció 3: Wizard Massa Llarg → Simplificar
**Problema**: 5 steps
**Solució**: Reduir a 2 steps i configurar després

---

## 📋 Millor Opció: Opció 1 + Millores

### Millora Propuesta:

#### Step 1: Eliminar Checkboxes del Wizard
```jsx
// ELIMINAR (línies 180-197)
<div className="rounded-lg border border-neutral-200 bg-white p-3">
  <p className="font-semibold text-neutral-700">Activar opcions extres</p>
  <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
    {[...checkboxes...]}
  </div>
</div>

// REEMPLAÇAR per:
<div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
  <div className="flex items-center gap-3">
    <CheckCircle2 className="w-6 h-6 text-blue-600" />
    <div>
      <h3 className="font-semibold text-blue-900">Configuració Avançada</h3>
      <p className="text-sm text-blue-700">
        Podràs configurar totes les opcions després de crear l'agent
      </p>
    </div>
  </div>
</div>
```

#### Step 2: Després de Crear Agent → Redirect
```jsx
const handleCreateAgent = async () => {
  // ... crear agent ...
  const agentId = response.data.agent?.id
  
  toast.success('Agent creat correctament!')
  
  // 🆕 REDIRECT a configuració
  setTimeout(() => {
    window.location.href = `/convhi-agents/config/${agentId}`
  }, 1000)
}
```

---

## 🎨 Interfície Proposta

### Abans (Actual):
```
┌────────────────────────────────────┐
│ [ ] Knowledge base (RAG)           │
│ [ ] Turn taking en temps real     │
│ [ ] Monitoring & logs              │
│ [ ] ASR (transcripció) integrat   │
└────────────────────────────────────┘
```

### Després (Millorat):
```
┌────────────────────────────────────┐
│ ✓ Configuració Disponible          │
│                                    │
│ Després de crear l'agent podràs:   │
│  • Configurar Knowledge Base       │
│  • Configurar ASR                  │
│  • Configurar Monitoring           │
│  • Test totes les connexions       │
│                                    │
│    [Crear Agent] → [Config]        │
└────────────────────────────────────┘
```

---

## 📝 Passos d'Implementació

### 1. Modificar Wizard
- ✅ Eliminar checkboxes (línies 180-197)
- ✅ Afegir missatge informatiu
- ✅ Afegir redirect després de crear

### 2. Verificar Config
- ✅ Assegurar que ConvHiAgentConfig.jsx té totes les funcions
- ✅ Verificar que tabs funcionen correctament

### 3. Testing
- ✅ Crear agent
- ✅ Verificar redirect a config
- ✅ Verificar que totes les opcions són configurables

---

## 🚀 Avantatges

**Abans (Checkboxes)**:
- ❌ Només enable/disable
- ❌ No pots configurar res
- ❌ No pots veure resultats

**Després (Interfície Completa)**:
- ✅ Upload documents
- ✅ Test ASR
- ✅ Configurar monitoring
- ✅ Veure resultats en temps real
- ✅ Tot configurable visualment

---

## ✅ Planificació Final

**Canvis Necessaris**:
1. **ConvHiAgentWizard.jsx**:
   - Eliminar checkboxes (línies 180-197)
   - Afegir missatge informatiu
   - Afegir redirect a config després de crear

2. **No cal canviar res més**:
   - ConvHiAgentConfig.jsx ja té tot
   - Backend ja té tots els endpoints

**Resultat**:
- Wizard més simple
- Configuració completa després
- Tot funciona visualment




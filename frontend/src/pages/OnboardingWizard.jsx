import React, { useMemo, useState } from 'react'
import { CheckCircle2, Circle, Headphones, Mic, Rocket, Shield } from 'lucide-react'
import { Link } from 'react-router-dom'

const steps = [
  { id: 'organisation', title: "Configura l'organització" },
  { id: 'channels', title: 'Canals i serveis' },
  { id: 'agents', title: 'Agents i veus' },
  { id: 'launch', title: 'Checklist final' },
]

const defaultState = {
  organisationName: '',
  timezone: 'Europe/Madrid',
  contactEmail: '',
  selectedChannels: ['widget'],
  enableSIP: false,
  enableBatch: false,
  favouriteVoice: 'senyor_catala_1',
  primaryLLM: 'openai::gpt-4o-mini',
}

const channelOptions = [
  { id: 'widget', label: 'Web widget (ConvHi)', description: 'Integració incrustada amb àudio en temps real.' },
  { id: 'sip', label: 'SIP/Telefonia', description: 'Trucades inbound/outbound amb SIP trunks.' },
  { id: 'batch', label: 'Batch calling', description: 'Campanyes massives programables.' },
  { id: 'crm', label: 'Integracions CRM', description: 'Sincronització amb Salesforce, HubSpot, etc.' },
]

const voicePresets = [
  { id: 'senyor_catala_1', name: 'Senyor Català 1 (mock)', notes: 'Desplegament immediat amb gravacions locals.' },
  { id: 'dona_catalana', name: 'Dona Catalana (mock)', notes: 'Ideal per a CX càlid mentre no hi ha GPU.' },
  { id: 'edge', name: 'Edge multilingüe', notes: 'Veus comercials (fallback).' },
]

const OnboardingWizard = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [formState, setFormState] = useState(defaultState)

  const completion = useMemo(() => Math.round(((activeStep + 1) / steps.length) * 100), [activeStep])

  const toggleChannel = (id) => {
    setFormState((prev) => {
      const selected = new Set(prev.selectedChannels)
      if (selected.has(id)) {
        selected.delete(id)
      } else {
        selected.add(id)
      }
      return { ...prev, selectedChannels: Array.from(selected) }
    })
  }

  const nextStep = () => setActiveStep((prev) => Math.min(prev + 1, steps.length - 1))
  const previousStep = () => setActiveStep((prev) => Math.max(prev - 1, 0))

  const renderStep = () => {
    const stepId = steps[activeStep].id

    switch (stepId) {
      case 'organisation':
        return (
          <div className="space-y-6">
            <p className="text-sm text-gray-600">
              Configura les dades bàsiques. Pots editar-les més endavant a la secció de configuració.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-800">Nom de l’organització</label>
                <input
                  type="text"
                  className="input-field mt-1"
                  placeholder="AT Hub - Grup Amb Tu"
                  value={formState.organisationName}
                  onChange={(event) => setFormState((prev) => ({ ...prev, organisationName: event.target.value }))}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-800">Zona horària</label>
                <select
                  className="input-field mt-1"
                  value={formState.timezone}
                  onChange={(event) => setFormState((prev) => ({ ...prev, timezone: event.target.value }))}
                >
                  <option value="Europe/Madrid">Europe/Madrid</option>
                  <option value="Europe/Paris">Europe/Paris</option>
                  <option value="America/New_York">America/New_York</option>
                  <option value="Asia/Tokyo">Asia/Tokyo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-800">Email de contacte</label>
                <input
                  type="email"
                  className="input-field mt-1"
                  placeholder="admin@athub.cat"
                  value={formState.contactEmail}
                  onChange={(event) => setFormState((prev) => ({ ...prev, contactEmail: event.target.value }))}
                />
              </div>
              <div className="rounded-lg border border-neutral-200 bg-white p-3 text-sm text-neutral-600">
                <p className="font-semibold text-neutral-800 mb-1">Consell:</p>
                <p>
                  Utilitza un compte compartit (ex. <span className="font-mono">veuplus@athub.cat</span>) per rebre
                  alertes de sistema, webhooks i informes.
                </p>
              </div>
            </div>
          </div>
        )

      case 'channels':
        return (
          <div className="space-y-6">
            <p className="text-sm text-gray-600">
              Tria els canals i serveis que vols activar durant la fase pilot. Sempre podràs afegir-ne més.
            </p>
            <div className="space-y-3">
              {channelOptions.map((option) => {
                const active = formState.selectedChannels.includes(option.id)
                return (
                  <button
                    key={option.id}
                    onClick={() => toggleChannel(option.id)}
                    className={`w-full text-left rounded-lg border-2 p-4 transition ${
                      active ? 'border-primary-500 bg-primary-50' : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-neutral-900">{option.label}</p>
                        <p className="text-sm text-neutral-600">{option.description}</p>
                      </div>
                      {active ? (
                        <CheckCircle2 className="w-5 h-5 text-primary-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-neutral-300" />
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm text-neutral-600">
              <p className="font-semibold text-neutral-800 mb-1">Recomanació</p>
              <p>
                Comença amb el <strong>web widget ConvHi</strong> i activa SIP quan tinguis els trunks configurats. El
                batch calling acostuma a desplegar-se al segon sprint.
              </p>
            </div>
          </div>
        )

      case 'agents':
        return (
          <div className="space-y-6">
            <p className="text-sm text-gray-600">
              Defineix els recursos que utilitzaràs per al primer agent pilot. Pots clonar-lo més endavant.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
                <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
                  <Mic className="w-4 h-4 text-accent-500" />
                  Veu per defecte
                </h3>
                <select
                  className="input-field"
                  value={formState.favouriteVoice}
                  onChange={(event) => setFormState((prev) => ({ ...prev, favouriteVoice: event.target.value }))}
                >
                  {voicePresets.map((voice) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-neutral-500">
                  {voicePresets.find((voice) => voice.id === formState.favouriteVoice)?.notes}
                </p>
              </div>

              <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
                <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-accent-500" />
                  LLM principal
                </h3>
                <select
                  className="input-field"
                  value={formState.primaryLLM}
                  onChange={(event) => setFormState((prev) => ({ ...prev, primaryLLM: event.target.value }))}
                >
                  <option value="openai::gpt-4o-mini">OpenAI · gpt-4o-mini</option>
                  <option value="openai::gpt-4o">OpenAI · gpt-4o</option>
                  <option value="gemini::1.5-flash">Gemini · 1.5 Flash</option>
                  <option value="alia::salamandra-7b">ALIA Kit · Salamandra 7B</option>
                  <option value="ollama::llama3.1:8b">Ollama · Llama 3.1 8B</option>
                </select>
                <p className="text-xs text-neutral-500">
                  Gestiona les claus API a <Link to="/settings" className="underline">Configuració → Credencials</Link>.
                </p>
              </div>
            </div>
          </div>
        )

      case 'launch':
      default:
        return (
          <div className="space-y-6">
            <p className="text-sm text-gray-600">
              Repassa la checklist abans del go-live. Pots exportar aquest resum o compartir-lo amb el teu equip.
            </p>
            <ul className="space-y-3">
              <li className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-emerald-700 flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 mt-0.5" />
                Domini configurat i credencials LLM guardades.
              </li>
              <li className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-emerald-700 flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 mt-0.5" />
                Canals activats: {formState.selectedChannels.sort().join(', ')}.
              </li>
              <li className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-emerald-700 flex items-start gap-2">
                <CheckCircle2 className="w-5 h-5 mt-0.5" />
                Agent base creat amb veu <strong>{formState.favouriteVoice}</strong> i LLM{' '}
                <strong>{formState.primaryLLM}</strong>.
              </li>
            </ul>
            <div className="rounded-lg border border-neutral-200 bg-white p-4 text-sm text-neutral-600">
              <p className="font-semibold text-neutral-800 mb-1">Següents passos recomanats</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Configura les rutes de SIP o integra el widget a staging.</li>
                <li>Crea el primer agent a <Link to="/convhi-agents" className="underline">ConvHi › Agents</Link>.</li>
                <li>Revisa analítiques i ajusta la veu/LLM segons el feedback.</li>
              </ol>
            </div>
          </div>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Rocket className="w-6 h-6 text-accent-500" />
            Onboarding VeuPlus
          </h1>
          <p className="text-sm text-neutral-600">
            Completa aquests passos per deixar la plataforma llesta per a producció.
          </p>
        </div>
        <span className="text-sm text-neutral-500">Progrés: {completion}%</span>
      </div>

      <div className="relative">
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => {
            const active = index === activeStep
            const completed = index < activeStep
            return (
              <div key={step.id} className="flex items-center gap-2 text-xs font-semibold uppercase text-neutral-500">
                <div
                  className={`flex h-7 w-7 items-center justify-center rounded-full border ${
                    completed ? 'bg-primary-600 text-white border-primary-600' : active ? 'border-primary-500 text-primary-600' : 'border-neutral-300 text-neutral-400'
                  }`}
                >
                  {completed ? <CheckCircle2 className="w-4 h-4" /> : index + 1}
                </div>
                <span className={active ? 'text-primary-600' : ''}>{step.title}</span>
              </div>
            )
          })}
        </div>
        <div className="card space-y-6">{renderStep()}</div>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={previousStep}
          disabled={activeStep === 0}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Enrere
        </button>
        {activeStep === steps.length - 1 ? (
          <Link to="/convhi-agents" className="btn-primary">
            Anar a la creació d’agents
          </Link>
        ) : (
          <button onClick={nextStep} className="btn-primary">
            Continuar
          </button>
        )}
      </div>
    </div>
  )
}

export default OnboardingWizard

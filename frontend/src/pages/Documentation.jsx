import React, { useState } from 'react'
import { 
  Book, Code, Key, Webhook, Globe, Copy, Check, ChevronRight, ExternalLink,
  Terminal, Zap, Mic, Volume2, Bot, Phone, Database, Settings
} from 'lucide-react'
import toast from 'react-hot-toast'

const Documentation = () => {
  const [activeSection, setActiveSection] = useState('sistemas')
  const [copiedCode, setCopiedCode] = useState('')

  const copyToClipboard = (code, id) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    toast.success('Codi copiat!')
    setTimeout(() => setCopiedCode(''), 2000)
  }

  const CodeBlock = ({ code, language = 'javascript', id, title }) => (
    <div className="relative mb-4">
      {title && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b border-gray-200 rounded-t-lg">
          <span className="text-sm font-medium text-gray-700">{title}</span>
          <button
            onClick={() => copyToClipboard(code, id)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            {copiedCode === id ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      )}
      <div className="bg-gray-900 rounded-b-lg overflow-hidden">
        <pre className="p-4 text-sm text-green-400 overflow-x-auto">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )

  const sections = [
    { id: 'sistemas', label: '3 Sistemes TTS', icon: Zap },
    { id: 'convhi', label: 'ConvHi Agents', icon: Bot },
    { id: 'multi-voice', label: 'Multi-Veu', icon: Volume2 },
    { id: 'workflows', label: 'Workflows', icon: Settings },
    { id: 'api', label: 'Endpoints API', icon: Webhook },
    { id: 'voicebots', label: 'Voicebots & SIP', icon: Phone },
    { id: 'knowledge', label: 'Base Coneixement', icon: Database },
    { id: 'training', label: 'Entrenament Veus', icon: Mic },
    { id: 'examples', label: 'Exemples', icon: Code },
    { id: 'quickstart', label: 'Inici Ràpid', icon: Terminal },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Book className="w-8 h-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Documentació VeuPlus</h1>
          </div>
          <p className="text-gray-600">Sistema TTS multilingüe amb 3 sistemes diferenciats</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-4 sticky top-4">
              <nav className="space-y-1">
                {sections.map(section => {
                  const Icon = section.icon
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                        activeSection === section.id
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-sm font-medium">{section.label}</span>
                    </button>
                  )
                })}
              </nav>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <a
                  href="http://localhost:8003/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <span>API Swagger</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm p-8">
              
              {/* SISTEMAS */}
              {activeSection === 'sistemas' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">3 Sistemes TTS Diferenciats</h2>

                  {/* Sistema 1 */}
                  <div className="border-l-4 border-blue-500 pl-6 py-4 bg-blue-50 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      Sistema 1: Edge-TTS Standard
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p><strong>Endpoint:</strong> <code className="bg-white px-2 py-1 rounded">/api/edge-tts/*</code></p>
                      <p><strong>Frontend:</strong> <code className="bg-white px-2 py-1 rounded">/edge-tts-standard</code></p>
                      <p><strong>Veus:</strong> ~400 veus globals (tots els idiomes)</p>
                      <p><strong>SEGRE:</strong> ❌ No</p>
                      <p><strong>Ús:</strong> Multiidioma global (anglès, francès, alemany, japonès, etc.)</p>
                    </div>
                  </div>

                  {/* Sistema 2 */}
                  <div className="border-l-4 border-green-500 pl-6 py-4 bg-green-50 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      Sistema 2: Català Edge-TTS + SEGRE
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p><strong>Endpoint:</strong> <code className="bg-white px-2 py-1 rounded">/api/catalan/*</code></p>
                      <p><strong>Frontend:</strong> <code className="bg-white px-2 py-1 rounded">/catalan-hyperrealistic</code></p>
                      <p><strong>Veus:</strong> Enric, Joana (catalanes natives)</p>
                      <p><strong>SEGRE:</strong> ✅ Sí (pronunciació optimitzada)</p>
                      <p><strong>Ús:</strong> Només català amb qualitat optimitzada</p>
                    </div>
                  </div>

                  {/* Sistema 3 */}
                  <div className="border-l-4 border-purple-500 pl-6 py-4 bg-purple-50 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      Sistema 3: ALIA BSC Premium
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p><strong>Endpoint:</strong> <code className="bg-white px-2 py-1 rounded">/api/alia/*</code></p>
                      <p><strong>Frontend:</strong> <code className="bg-white px-2 py-1 rounded">/alia-kit-bsc</code></p>
                      <p><strong>Veus:</strong> Alba, Álvaro, Ainhoa, Sabela (premium)</p>
                      <p><strong>SEGRE:</strong> ✅ Sí (només català)</p>
                      <p><strong>Idiomes:</strong> ca, es, eu, gl (llengües cooficials)</p>
                      <p><strong>Configuració:</strong> Avançada (expressivitat, velocitat, to)</p>
                    </div>
                  </div>

                  {/* Comparativa */}
                  <div className="mt-8">
                    <h3 className="text-lg font-bold mb-4">Comparativa</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aspecte</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sistema 1</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sistema 2</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sistema 3</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          <tr>
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">Veus</td>
                            <td className="px-6 py-4 text-sm text-gray-500">~400</td>
                            <td className="px-6 py-4 text-sm text-gray-500">2</td>
                            <td className="px-6 py-4 text-sm text-gray-500">4</td>
                          </tr>
                          <tr>
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">SEGRE</td>
                            <td className="px-6 py-4 text-sm text-gray-500">❌</td>
                            <td className="px-6 py-4 text-sm text-gray-500">✅</td>
                            <td className="px-6 py-4 text-sm text-gray-500">✅ (només ca)</td>
                          </tr>
                          <tr>
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">Idiomes</td>
                            <td className="px-6 py-4 text-sm text-gray-500">Tots</td>
                            <td className="px-6 py-4 text-sm text-gray-500">Només ca</td>
                            <td className="px-6 py-4 text-sm text-gray-500">ca, es, eu, gl</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* CONVHI AGENTS */}
              {activeSection === 'convhi' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">ConvHi Agents - Agents Conversacionals Hiperrealistes</h2>

                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🤖 Sistema ConvHi Complet</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Característiques Principals</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>ASR (Speech-to-Text)</strong> - Transcripció automàtica amb Whisper</li>
                          <li>• <strong>LLM Integration</strong> - OpenAI, Gemini, Claude, ALIA, Ollama, vLLM, Custom</li>
                          <li>• <strong>TTS (Text-to-Speech)</strong> - Síntesi de veu amb 3 sistemes</li>
                          <li>• <strong>Turn-Taking Model</strong> - Comprensió de torns conversacionals</li>
                          <li>• <strong>Knowledge Base</strong> - Base de coneixement intel·ligent</li>
                          <li>• <strong>Monitoring</strong> - Anàlisi en temps real</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2">Workflows Avançats</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Nodes Visuals</strong> - Start, Subagent, Tool, Transfer, End</li>
                          <li>• <strong>Connexions Externes</strong> - APIs, Webhooks, Bases de dades</li>
                          <li>• <strong>Crides entre Agents</strong> - Comunicació interna</li>
                          <li>• <strong>Variables Dinàmiques</strong> - Context en temps real</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Endpoints ConvHi</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/agents</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Crear nou agent ConvHi</p>
                        <CodeBlock
                          id="convhi-create"
                          title="Request"
                          code={`{
  "name": "Agent de Suport",
  "description": "Agent especialitzat en atenció al client",
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini",
  "api_key": "sk-...",
  "voice_system": "edge-tts",
  "voice_id": "es-ES-ElviraNeural",
  "language": "es",
  "knowledge_base_enabled": true,
  "turn_taking_enabled": true,
  "asr_enabled": true,
  "monitoring_enabled": true
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/agents/{'{agent_id}'}/chat</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Xatejar amb agent ConvHi</p>
                        <CodeBlock
                          id="convhi-chat"
                          title="Request"
                          code={`{
  "agent_id": "convhi_1",
  "message": "Hola, com puc ajudar-te?",
  "message_type": "text"
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/convhi/llm-providers</code>
                        </div>
                        <p className="text-sm text-gray-600">Llistar proveïdors LLM disponibles</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/llm-providers/test</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Provar connexió amb proveïdor LLM</p>
                        <CodeBlock
                          id="llm-test"
                          title="Request"
                          code={`{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "api_key": "sk-..."
}`}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* MULTI-VEU */}
              {activeSection === 'multi-voice' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Multi-Veu Support</h2>

                  <div className="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🎤 Suport Multi-Veu i Multiidioma</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Funcionalitats</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Multi-Character Storytelling</strong> - Diferents veus per personatges</li>
                          <li>• <strong>Language Tutoring</strong> - Veus natives per idiomes</li>
                          <li>• <strong>Emotional Agents</strong> - Canvis de veu segons context emocional</li>
                          <li>• <strong>Role-playing Scenarios</strong> - Veus distintes per persones</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2">Sistemes Suportats</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Edge-TTS</strong> - ~400 veus globals</li>
                          <li>• <strong>Català Hiperrealista</strong> - Veus natives catalanes</li>
                          <li>• <strong>ALIA BSC Premium</strong> - Veus premium cooficials</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Configuració Multi-Veu</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/voice-config/agent/{'{agent_id}'}/voices</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Afegir veu a agent</p>
                        <CodeBlock
                          id="add-voice"
                          title="Request"
                          code={`{
  "label": "spanish",
  "voice_system": "edge-tts",
  "voice_id": "es-ES-ElviraNeural",
  "model_family": "multilingual",
  "language": "es",
  "description": "Per paraules o frases en espanyol",
  "enabled": true,
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 1.0
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/voice-config/switch-voices</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Canviar veus amb XML markup</p>
                        <CodeBlock
                          id="switch-voices"
                          title="Request"
                          code={`{
  "agent_id": "convhi_1",
  "text": "El professor va dir: <spanish>¡Hola estudiantes!</spanish> Després l'estudiant va respondre: <english>Hello! How are you today?</english>",
  "context": {
    "conversation_id": "conv_123"
  }
}`}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Exemples d'Ús</h3>
                    
                    <div className="space-y-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Language Tutoring</h4>
                        <CodeBlock
                          id="tutoring-example"
                          title="Exemple"
                          code={`Teacher: Let's practice greetings. In Spanish, we say <spanish>¡Hola! ¿Cómo estás?</spanish>
Student: How do I respond?
Teacher: You can say <spanish>¡Hola! Estoy bien, gracias.</spanish> which means Hello! I'm fine, thank you.`}
                        />
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Multi-Character Dialogue</h4>
                        <CodeBlock
                          id="dialogue-example"
                          title="Exemple"
                          code={`<narrator>Once upon a time, in a distant kingdom...</narrator>
<princess>I need to find the magic crystal!</princess>
<wizard>The crystal lies beyond the enchanted forest.</wizard>`}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Best Practices</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Voice Selection</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Escull veus que diferenciïn clarament</li>
                          <li>• Prova combinacions de veus</li>
                          <li>• Considera el to emocional</li>
                          <li>• Assegura que les veus coincideixin amb l'idioma</li>
                        </ul>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Label Naming</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Usa labels descriptius i intuïtius</li>
                          <li>• Mantén labels curts i memorables</li>
                          <li>• Evita caràcters especials</li>
                          <li>• Labels case-sensitive</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* WORKFLOWS */}
              {activeSection === 'workflows' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Workflows Visuals</h2>

                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🔄 Sistema de Workflows Avançat</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Tipus de Nodes</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Start</strong> - Punt d'inici del workflow</li>
                          <li>• <strong>Subagent</strong> - Configuració d'agent amb LLM</li>
                          <li>• <strong>Tool</strong> - Execució d'eines del sistema</li>
                          <li>• <strong>Transfer</strong> - Transferència a agent humà</li>
                          <li>• <strong>External API</strong> - Crides a APIs externes</li>
                          <li>• <strong>ConvHi Call</strong> - Crides entre agents ConvHi</li>
                          <li>• <strong>Webhook</strong> - Notificacions externes</li>
                          <li>• <strong>Database</strong> - Operacions de base de dades</li>
                          <li>• <strong>End</strong> - Finalització del workflow</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2">Connexions Externes</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>External API</strong> - REST, GraphQL, Custom APIs</li>
                          <li>• <strong>ConvHi Agents</strong> - Comunicació interna</li>
                          <li>• <strong>Webhooks</strong> - Notificacions en temps real</li>
                          <li>• <strong>Databases</strong> - SQLite, MySQL, PostgreSQL</li>
                          <li>• <strong>Message Queues</strong> - Redis, RabbitMQ</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Endpoints Workflows</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/workflows/</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Crear nou workflow</p>
                        <CodeBlock
                          id="create-workflow"
                          title="Request"
                          code={`{
  "id": "support_workflow",
  "name": "Workflow de Suport",
  "description": "Workflow per atenció al client",
  "agent_id": "convhi_1",
  "nodes": [
    {
      "id": "start_node",
      "type": "start",
      "name": "Inici",
      "position": {"x": 100, "y": 100}
    },
    {
      "id": "greeting_node",
      "type": "subagent",
      "name": "Salutació",
      "position": {"x": 300, "y": 100},
      "config": {
        "system_prompt": "Saluda cordialment l'usuari",
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini"
      }
    }
  ],
  "edges": [
    {
      "id": "start_to_greeting",
      "source_node_id": "start_node",
      "target_node_id": "greeting_node",
      "type": "forward",
      "transition_type": "unconditional"
    }
  ]
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/workflows/execute</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Executar workflow</p>
                        <CodeBlock
                          id="execute-workflow"
                          title="Request"
                          code={`{
  "workflow_id": "support_workflow",
  "agent_id": "convhi_1",
  "conversation_id": "conv_123",
  "user_input": "Hola, tinc un problema",
  "initial_state": {
    "user_id": "user_456",
    "urgency_level": "normal"
  }
}`}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Variables Dinàmiques</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-700 mb-2">
                        Les variables dinàmiques permeten injectar valors en temps real:
                      </p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• <code>{'{{user_id}}'}</code> - ID de l'usuari</li>
                        <li>• <code>{'{{user_problem}}'}</code> - Problema de l'usuari</li>
                        <li>• <code>{'{{urgency_level}}'}</code> - Nivell d'urgència</li>
                        <li>• <code>{'{{current_timestamp}}'}</code> - Timestamp actual</li>
                        <li>• <code>{'{{agent_response}}'}</code> - Resposta de l'agent</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* MULTIIDIOMA */}
              {activeSection === 'multi-voice' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Suport Multiidioma</h2>

                  <div className="bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🌍 Sistema Multiidioma Complet</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">31 Idiomes Suportats</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Idiomes Principals</strong> - en, es, ca, fr, de, it, pt</li>
                          <li>• <strong>Idiomes Asiàtics</strong> - ja, ko, zh-cn, zh-tw, th, vi, hi</li>
                          <li>• <strong>Idiomes Europeus</strong> - nl, pl, ru, sv, no, da, fi, el, he</li>
                          <li>• <strong>Idiomes Addicionals</strong> - ar, tr, id, ms, tl, cs, hu, ro, bg, hr, sk, sl, et, lv, lt, uk, sr</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2">Funcionalitats</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Detecció Automàtica</strong> - Detecta idioma amb LLM</li>
                          <li>• <strong>Canvi Dinàmic</strong> - Canvia veu segons idioma detectat</li>
                          <li>• <strong>Missatges Personalitzats</strong> - Salutació per idioma</li>
                          <li>• <strong>Context Cultural</strong> - Adaptació cultural per idioma</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Configuració Multiidioma</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/language/agent/{'{agent_id}'}/languages</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Afegir idioma a agent</p>
                        <CodeBlock
                          id="add-language"
                          title="Request"
                          code={`{
  "language_code": "fr",
  "language_name": "French",
  "native_name": "Français",
  "voice_system": "edge-tts",
  "voice_id": "fr-FR-DeniseNeural",
  "first_message": "Bonjour! Comment puis-je vous aider aujourd'hui?",
  "enabled": true,
  "auto_translate": true,
  "cultural_context": {
    "formality": "formal",
    "greeting_style": "polite",
    "time_format": "24h"
  }
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/convhi/language/detect</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Detectar idioma del text</p>
                        <CodeBlock
                          id="detect-language"
                          title="Request"
                          code={`{
  "text": "Bonjour, comment allez-vous?",
  "agent_id": "convhi_1",
  "context": {
    "conversation_id": "conv_123"
  }
}`}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Exemples d'Ús</h3>
                    
                    <div className="space-y-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Detecció Automàtica</h4>
                        <CodeBlock
                          id="auto-detection-example"
                          title="Exemple"
                          code={`// L'usuari escriu en francès
User: "Bonjour, comment allez-vous?"

// El sistema detecta automàticament l'idioma
System: Detected language: fr (confidence: 0.95)
System: Switching to French voice: fr-FR-DeniseNeural
System: "Bonjour! Comment puis-je vous aider aujourd'hui?"`}
                        />
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Multi-Character Multiidioma</h4>
                        <CodeBlock
                          id="multi-character-multilang"
                          title="Exemple"
                          code={`<narrator>Once upon a time, in a distant kingdom...</narrator>
<princess>Je dois trouver le cristal magique!</princess>
<wizard>El cristal está más allá del bosque encantado.</wizard>
<narrator>The princess continued her quest...</narrator>`}
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Best Practices</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Voice Selection</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Escull veus entrenades específicament</li>
                          <li>• Considera accents regionals</li>
                          <li>• Prova pronunciació de paraules clau</li>
                          <li>• Assegura qualitat natural</li>
                        </ul>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Cultural Context</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Adapta salutacions culturals</li>
                          <li>• Considera formalitat per idioma</li>
                          <li>• Respecta convencions temporals</li>
                          <li>• Personalitza per regió</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* API ENDPOINTS */}
              {activeSection === 'api' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Endpoints API</h2>

                  {/* Sistema 1 APIs */}
                  <div>
                    <h3 className="text-xl font-bold text-blue-600 mb-4">Sistema 1: Edge-TTS Standard</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/edge-tts/synthesize</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Generar àudio amb qualsevol veu Edge-TTS</p>
                        <CodeBlock
                          id="s1-synthesize"
                          title="Request"
                          code={`{
  "text": "Hello, how are you?",
  "voice_id": "en-US-AriaNeural",
  "language": "en"
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/edge-tts/voices</code>
                        </div>
                        <p className="text-sm text-gray-600">Llistar totes les ~400 veus disponibles</p>
                      </div>
                    </div>
                  </div>

                  {/* Sistema 2 APIs */}
                  <div>
                    <h3 className="text-xl font-bold text-green-600 mb-4">Sistema 2: Català Edge+SEGRE</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/catalan/synthesize</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Generar àudio català amb SEGRE</p>
                        <CodeBlock
                          id="s2-synthesize"
                          title="Request"
                          code={`{
  "text": "Hola, com estàs?",
  "voice_id": "senyor_catala_1",
  "language": "ca",
  "voice_settings": {
    "dialect": "central"
  }
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/catalan/voices</code>
                        </div>
                        <p className="text-sm text-gray-600">Llistar veus catalanes (Enric, Joana)</p>
                      </div>
                    </div>
                  </div>

                  {/* Sistema 3 APIs */}
                  <div>
                    <h3 className="text-xl font-bold text-purple-600 mb-4">Sistema 3: ALIA BSC Premium</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/alia/tts/synthesize</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Generar àudio premium amb configuració avançada</p>
                        <CodeBlock
                          id="s3-synthesize"
                          title="Request"
                          code={`{
  "text": "Hola, com estàs?",
  "language": "ca",
  "dialect": "central",
  "voice_settings": {
    "speed": 1.0,
    "pitch": 1.0,
    "expressiveness": 1.2
  }
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/alia/voices</code>
                        </div>
                        <p className="text-sm text-gray-600">Llistar veus premium (Alba, Álvaro, Ainhoa, Sabela)</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/alia/status</code>
                        </div>
                        <p className="text-sm text-gray-600">Estat del sistema ALIA BSC</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* VOICEBOTS & SIP */}
              {activeSection === 'voicebots' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Voicebots & SIP Trunk</h2>

                  <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🎤 Sistema de Voicebots Complet</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Integració SIP Trunk</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Asterisk/FreeSWITCH</strong> - Configuració completa</li>
                          <li>• <strong>Scripts AGI</strong> - Integració automàtica</li>
                          <li>• <strong>Trucades Entrants</strong> - Gestió automàtica</li>
                          <li>• <strong>ASR + LLM + TTS</strong> - Conversa intel·ligent</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-bold mb-2">Agent Intel·ligent</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Base de Coneixement</strong> - Memòria i aprenentatge</li>
                          <li>• <strong>LLM Integration</strong> - GPT, ALIA, Ollama</li>
                          <li>• <strong>Històric Converses</strong> - Per trucada</li>
                          <li>• <strong>Multiidioma</strong> - ca, es, en, fr</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Endpoints Voicebots</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/voicebots/synthesize</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Síntesi per voicebots externs</p>
                        <CodeBlock
                          id="voicebot-synthesize"
                          title="Request"
                          code={`{
  "text": "Hola, com puc ajudar-te?",
  "voice_id": "ca-ES-EnricNeural",
  "system": "catalan",
  "language": "ca"
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/voicebots/webhook</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Webhook per sistemes externs (SIP, call centers)</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/sip/handle-call</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Gestionar trucada entrant SIP</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/sip/process-voice</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Processar entrada de veu (ASR + LLM + TTS)</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Configuració Asterisk</h3>
                    <CodeBlock
                      id="asterisk-config"
                      title="extensions.conf"
                      code={`[default]
exten => _X.,1,NoOp(Trucada entrant: ${CALLERID(num)} -> ${EXTEN})
exten => _X.,n,Goto(veuplus-greeting,start,1)

[veuplus-greeting]
exten => start,1,AGI(veuplus_greeting.agi,${CALLERID(num)},${EXTEN})
exten => start,n,Playback(${GREETING_FILE})
exten => start,n,Goto(veuplus-conversation,start,1)

[veuplus-conversation]
exten => start,1,Record(${INPUT_FILE}:wav,5,10)
exten => start,n,AGI(veuplus_process.agi,${CALL_ID},${INPUT_FILE})
exten => start,n,Playback(${RESPONSE_FILE})
exten => start,n,GotoIf($["${CONTINUE}" = "yes"]?start,1)
exten => start,n,Hangup()`}
                    />
                  </div>
                </div>
              )}

              {/* BASE DE CONEIXEMENT */}
              {activeSection === 'knowledge' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Base de Coneixement</h2>

                  <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🧠 Sistema Intel·ligent</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Característiques</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>SQLite Database</strong> - Emmagatzematge local</li>
                          <li>• <strong>Busca Intel·ligent</strong> - Per paraules clau</li>
                          <li>• <strong>Fallback LLM</strong> - Si no troba en base</li>
                          <li>• <strong>Multiidioma</strong> - ca, es, en, fr</li>
                          <li>• <strong>Històric Converses</strong> - Per trucada</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Endpoints Base de Coneixement</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/sip/add-knowledge</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Afegir coneixement a la base</p>
                        <CodeBlock
                          id="add-knowledge"
                          title="Request"
                          code={`{
  "category": "serveis",
  "question": "preus",
  "answer": "Els nostres preus comencen des de 50€/mes.",
  "language": "ca",
  "confidence": 1.0
}`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/sip/knowledge-stats</code>
                        </div>
                        <p className="text-sm text-gray-600">Estadístiques de coneixement</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/sip/conversation-history/{call_id}</code>
                        </div>
                        <p className="text-sm text-gray-600">Històric de conversa per trucada</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Coneixement Inicial</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Català</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Benvinguda: "Hola! Gràcies per trucar..."</li>
                          <li>• Horaris: "De dilluns a divendres 9:00-18:00"</li>
                          <li>• Contacte: "Telèfon 93 123 45 67"</li>
                          <li>• Serveis: "Consultoria, desenvolupament web..."</li>
                        </ul>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Castellà</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Bienvenida: "¡Hola! Gracias por llamar..."</li>
                          <li>• Horarios: "Lunes a viernes 9:00-18:00"</li>
                          <li>• Contacto: "Teléfono 93 123 45 67"</li>
                          <li>• Servicios: "Consultoría, desarrollo web..."</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Test de Base de Coneixement</h3>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-blue-800 mb-2">
                        <strong>Endpoint de prova:</strong> <code>GET /api/sip/knowledge-stats</code>
                      </p>
                      <p className="text-sm text-blue-700">
                        Aquest endpoint retorna estadístiques de la base de coneixement, incloent el nombre total de coneixements, distribució per idioma i categoria.
                      </p>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Configuració SIP Trunk</h3>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-bold mb-2">Asterisk Configuration</h4>
                      <p className="text-sm text-green-800 mb-2">
                        Per configurar Asterisk amb VeuPlus:
                      </p>
                      <ol className="text-sm text-green-700 space-y-1 ml-4">
                        <li>1. Copiar <code>asterisk_config/extensions.conf</code> a <code>/etc/asterisk/</code></li>
                        <li>2. Copiar scripts AGI a <code>/var/lib/asterisk/agi-bin/</code></li>
                        <li>3. Configurar <code>sip.conf</code> amb el teu proveïdor SIP</li>
                        <li>4. Reiniciar Asterisk: <code>sudo systemctl restart asterisk</code></li>
                      </ol>
                    </div>
                  </div>
                </div>
              )}

              {/* ENTRENAMENT DE VEUS */}
              {activeSection === 'training' && (
                <div className="space-y-8">
                  <h2 className="text-2xl font-bold text-gray-900">Entrenament de Veus</h2>

                  <div className="bg-purple-50 border-l-4 border-purple-500 p-6 rounded-r-lg">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">🎓 Sistema d'Entrenament Avançat</h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-bold mb-2">Qualitat "Senyor Català Extended"</h4>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• <strong>Tono Formal</strong> - Professional i autoritari</li>
                          <li>• <strong>Pronunciació Clara</strong> - Precisa i comprensible</li>
                          <li>• <strong>Pace Moderat</strong> - Ni massa ràpid ni massa lent</li>
                          <li>• <strong>Èmfasi Natural</strong> - Paraules clau destacades</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Process d'Entrenament</h3>
                    
                    <div className="space-y-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/voicebots/train</code>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">Entrenar nova veu amb qualitat professional</p>
                        <CodeBlock
                          id="train-voice"
                          title="Request (multipart/form-data)"
                          code={`curl -X POST http://localhost:8003/api/voicebots/train \\
  -F "voice_name=meva_veu_personalitzada" \\
  -F "language=ca" \\
  -F "quality_level=senyor_catala_extended" \\
  -F "audio_files=@grabacio1.wav" \\
  -F "audio_files=@grabacio2.wav"`}
                        />
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">GET</span>
                          <code className="text-sm">/api/voicebots/trained</code>
                        </div>
                        <p className="text-sm text-gray-600">Llistar veus entrenades</p>
                      </div>

                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">POST</span>
                          <code className="text-sm">/api/voicebots/synthesize-trained</code>
                        </div>
                        <p className="text-sm text-gray-600">Sintetitzar amb veu entrenada</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Qualitats Disponibles</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Senyor Català Extended</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Tono formal i professional</li>
                          <li>• Pronunciació clara i precisa</li>
                          <li>• Pace moderat i autoritari</li>
                          <li>• Ús: Presentacions, anuncis</li>
                        </ul>
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Professional</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Tono professional estàndard</li>
                          <li>• Pronunciació clara</li>
                          <li>• Pace moderat</li>
                          <li>• Ús: General professional</li>
                        </ul>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-bold mb-2">Casual</h4>
                        <ul className="text-sm space-y-1">
                          <li>• Tono casual i natural</li>
                          <li>• Pronunciació natural</li>
                          <li>• Pace normal</li>
                          <li>• Ús: Conversa casual</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* EXAMPLES */}
              {activeSection === 'examples' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">Exemples d'Ús</h2>

                  <div>
                    <h3 className="text-lg font-bold mb-3">JavaScript / Fetch API</h3>
                    <CodeBlock
                      id="example-js"
                      title="Exemple Sistema 3 (ALIA BSC)"
                      code={`// Generar àudio amb ALIA BSC Premium
const response = await fetch('http://localhost:8003/api/alia/tts/synthesize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Hola, com estàs?',
    language: 'ca',
    dialect: 'central',
    voice_settings: {
      speed: 1.0,
      pitch: 1.0,
      expressiveness: 1.2
    }
  })
})

const data = await response.json()
if (data.success) {
  // Reproduir àudio
  const audio = new Audio(\`data:audio/mp3;base64,\${data.audio_base64}\`)
  audio.play()
}
`}
                    />
                  </div>

                  <div>
                    <h3 className="text-lg font-bold mb-3">Python</h3>
                    <CodeBlock
                      id="example-py"
                      language="python"
                      title="Exemple Sistema 2 (Català+SEGRE)"
                      code={`import requests
import base64

# Generar àudio català amb SEGRE
response = requests.post('http://localhost:8003/api/catalan/synthesize', json={
    'text': 'Hola, com estàs?',
    'voice_id': 'senyor_catala_1',
    'language': 'ca',
    'voice_settings': {
        'dialect': 'central'
    }
})

data = response.json()
if data['success']:
    # Guardar àudio
    audio_data = base64.b64decode(data['audio_base64'])
    with open('output.mp3', 'wb') as f:
        f.write(audio_data)
`}
                    />
                  </div>

                  <div>
                    <h3 className="text-lg font-bold mb-3">cURL</h3>
                    <CodeBlock
                      id="example-curl"
                      language="bash"
                      title="Exemple Sistema 1 (Edge Standard)"
                      code={`curl -X POST http://localhost:8003/api/edge-tts/synthesize \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Hello, how are you?",
    "voice_id": "en-US-AriaNeural",
    "language": "en"
  }'
`}
                    />
                  </div>
                </div>
              )}

              {/* QUICKSTART */}
              {activeSection === 'quickstart' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">Inici Ràpid</h2>

                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                    <p className="text-sm text-yellow-800">
                      <strong>Requisit:</strong> pip install edge-tts
                    </p>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold mb-3">1. Iniciar el Sistema</h3>
                    <CodeBlock
                      id="quickstart-1"
                      language="powershell"
                      code={`cd C:\\Users\\merit\\Desktop\\VeusPlus
.\\INICIAR_3_SISTEMES.ps1
`}
                    />
                  </div>

                  <div>
                    <h3 className="text-lg font-bold mb-3">2. Verificar que Funciona</h3>
                    <CodeBlock
                      id="quickstart-2"
                      language="bash"
                      code={`# Health check
curl http://localhost:8003/health

# Llistar veus ALIA BSC
curl http://localhost:8003/api/alia/voices
`}
                    />
                  </div>

                  <div>
                    <h3 className="text-lg font-bold mb-3">3. Prova Ràpida</h3>
                    <p className="text-sm text-gray-600 mb-3">Obre el navegador i prova cada sistema:</p>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <a href="http://localhost:3000/edge-tts-standard" className="text-primary-600 hover:underline">
                          Sistema 1: Edge-TTS Standard
                        </a>
                      </div>
                      <div className="flex items-center space-x-2">
                        <a href="http://localhost:3000/catalan-hyperrealistic" className="text-primary-600 hover:underline">
                          Sistema 2: Català Edge+SEGRE
                        </a>
                      </div>
                      <div className="flex items-center space-x-2">
                        <a href="http://localhost:3000/alia-kit-bsc" className="text-primary-600 hover:underline">
                          Sistema 3: ALIA BSC Premium
                        </a>
                      </div>
                    </div>
                  </div>

                  <div className="mt-8 bg-primary-50 border-l-4 border-primary-400 p-4">
                    <h4 className="font-bold text-primary-900 mb-2">📚 Documentació Completa</h4>
                    <p className="text-sm text-primary-800 mb-2">
                      Consulta la documentació completa a:
                    </p>
                    <a
                      href="http://localhost:8003/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                    >
                      <span>API Swagger (Interactive)</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Documentation


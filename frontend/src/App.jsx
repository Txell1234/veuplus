import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CatalanHyperrealistic from './pages/CatalanHyperrealistic'
import EdgeTTSStandardSimple from './pages/EdgeTTSStandardSimple'
import VoiceManagement from './pages/VoiceManagement'
import Chatbots from './pages/Chatbots'
import Voicebots from './pages/Voicebots'
import ALIAKitBSC from './pages/ALIAKitBSC'
import ConvHiAgentWizard from './pages/ConvHiAgentWizard'
import SystemsHub from './pages/SystemsHub'
import TrainingUpload from './pages/TrainingUpload'
import Documentation from './pages/Documentation'
import Settings from './pages/Settings'
import { VoiceProvider } from './contexts/VoiceContext'
import { ChatbotProvider } from './contexts/ChatbotContext'
import { VoicebotProvider } from './contexts/VoicebotContext'
import { ThemeProvider } from './contexts/ThemeContext'
import TrainingMonitor from './pages/TrainingMonitor'
import ConvHiAgents from './pages/ConvHiAgents'
import ConvHiExternalVoices from './pages/ConvHiExternalVoices'
import ConvHiAnalytics from './pages/ConvHiAnalytics'
import ConvHiWidgets from './pages/ConvHiWidgets'
import ConvHiWidgetManagement from './pages/ConvHiWidgetManagement'
import ConvHiBatchCalling from './pages/ConvHiBatchCalling'
import LiveSandbox from './pages/LiveSandbox'
import OnboardingWizard from './pages/OnboardingWizard'
import ConvHiAgentConfig from './pages/ConvHiAgentConfig'
import ConvHiSIPConfig from './pages/ConvHiSIPConfig'
import ConvHiWebRTCConfig from './pages/ConvHiWebRTCConfig'

function App() {
  return (
    <ThemeProvider>
      <VoiceProvider>
        <ChatbotProvider>
          <VoicebotProvider>
            <Router basename="/">
              <div className="min-h-screen bg-neutral-50 transition-colors">
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/onboarding" element={<OnboardingWizard />} />
                    <Route path="/systems" element={<SystemsHub />} />
                    <Route path="/catalan-hyperrealistic" element={<CatalanHyperrealistic />} />
                    <Route path="/edge-tts-standard" element={<EdgeTTSStandardSimple />} />
                    <Route path="/alia-kit-bsc" element={<ALIAKitBSC />} />
                    <Route path="/voices" element={<VoiceManagement />} />
                    <Route path="/training-upload" element={<TrainingUpload />} />
                    <Route path="/chatbots" element={<Chatbots />} />
                    <Route path="/voicebots" element={<Voicebots />} />
                    <Route path="/convhi-agents" element={<ConvHiAgentWizard />} />
                    <Route path="/convhi-agents/config/:agentId" element={<ConvHiAgentConfig />} />
                    <Route path="/convhi-sip" element={<ConvHiSIPConfig />} />
                    <Route path="/convhi-webrtc" element={<ConvHiWebRTCConfig />} />
                    <Route path="/convhi-voices" element={<ConvHiExternalVoices />} />
                    <Route path="/convhi-analytics" element={<ConvHiAnalytics />} />
                    <Route path="/convhi-widgets" element={<ConvHiWidgets />} />
                    <Route path="/convhi-widget-management" element={<ConvHiWidgetManagement />} />
                    <Route path="/convhi-batch-calling" element={<ConvHiBatchCalling />} />
                    <Route path="/sandbox" element={<LiveSandbox />} />
                    <Route path="/training-monitor" element={<TrainingMonitor />} />
                    <Route path="/convhi-agents-full" element={<ConvHiAgents />} />
                    <Route path="/docs" element={<Documentation />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </Layout>
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: '#0c153f',
                      color: '#f6f7fb',
                      borderRadius: '0.75rem',
                      border: '1px solid rgba(249, 86, 30, 0.25)',
                    },
                    success: {
                      duration: 3000,
                      iconTheme: {
                        primary: '#10b981',
                        secondary: '#f6f7fb',
                      },
                    },
                    error: {
                      duration: 5000,
                      iconTheme: {
                        primary: '#dc2626',
                        secondary: '#f6f7fb',
                      },
                    },
                  }}
                />
              </div>
            </Router>
          </VoicebotProvider>
        </ChatbotProvider>
      </VoiceProvider>
    </ThemeProvider>
  )
}

export default App

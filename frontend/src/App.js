import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Multi-language translations
const translations = {
  ca: {
    dashboard: "Tauler",
    voiceLibrary: "Biblioteca de Veus",
    speechSynthesis: "Síntesi de Veu",
    chatbots: "Chatbots",
    voicebots: "Voicebots",
    knowledgeBase: "Base de Coneixement",
    welcome: "Benvingut a VeuPlus",
    voicesTrained: "Veus Entrenades",
    readyForSynthesis: "Llestes per síntesi",
    activeBots: "Bots actius",
    voiceAssistants: "Assistents de veu",
    documentsProcessed: "Documents processats",
    quickActions: "Accions Ràpides",
    trainNewVoice: "Entrenar Nova Veu",
    createChatbot: "Crear Chatbot",
    buildVoicebot: "Construir Voicebot",
    recentActivity: "Activitat Recent",
    catalanDialects: "Dialectes Catalans",
    voiceTraining: "Entrenament de Veu",
    trainNewVoiceTitle: "Entrenar Nova Veu",
    voiceName: "Nom de la Veu",
    catalanDialect: "Dialecte Català",
    description: "Descripció",
    audioFiles: "Fitxers d'Àudio",
    uploadMultipleFiles: "Puja múltiples fitxers d'àudio (mínim 30 minuts recomanat)",
    startTraining: "Iniciar Entrenament",
    training: "Entrenant...",
    trainedVoices: "Veus Entrenades",
    textToSynthesize: "Text a Sintetitzar",
    selectVoice: "Selecciona una Veu",
    selectTrainedVoice: "Selecciona una veu entrenada...",
    generateSpeech: "Generar Veu",
    synthesizing: "Sintetitzant...",
    generatedAudio: "Àudio Generat",
    downloadAudio: "Descarregar Àudio",
    createNewChatbot: "Crear Nou Chatbot",
    chatbotName: "Nom del Chatbot",
    llmProvider: "Proveïdor LLM",
    modelName: "Nom del Model",
    temperature: "Temperatura",
    systemPrompt: "Prompt del Sistema",
    apiKey: "Clau API",
    knowledgeBaseSources: "Fonts de la Base de Coneixement",
    selectKnowledgeSources: "Selecciona fonts de coneixement...",
    createChatbotBtn: "Crear Chatbot",
    cancel: "Cancel·lar",
    yourChatbots: "Els teus Chatbots",
    testChat: "Provar Xat",
    testing: "Provant",
    typeMessage: "Escriu el teu missatge...",
    send: "Enviar",
    supportedLanguages: "Idiomes Suportats",
    defaultLanguage: "Idioma per Defecte",
    createNewVoicebot: "Crear Nou Voicebot",
    selectVoiceModel: "Selecciona Model de Veu",
    voicebotName: "Nom del Voicebot",
    createVoicebotBtn: "Crear Voicebot",
    yourVoicebots: "Els teus Voicebots",
    testVoiceChat: "Provar Xat de Veu",
    uploadDocuments: "Pujar Documents",
    uploading: "Pujant...",
    uploadedDocuments: "Documents Pujats",
    ready: "Llest",
    pending: "Pendent",
    error: "Error",
    status: "Estat",
    name: "Nom",
    type: "Tipus",
    actions: "Accions",
    edit: "Editar",
    delete: "Eliminar",
    save: "Guardar",
    close: "Tancar",
    catalan: "Català",
    spanish: "Espanyol", 
    french: "Francès",
    english: "Anglès"
  },
  es: {
    dashboard: "Panel",
    voiceLibrary: "Biblioteca de Voces",
    speechSynthesis: "Síntesis de Voz",
    chatbots: "Chatbots",
    voicebots: "Voicebots",
    knowledgeBase: "Base de Conocimiento",
    welcome: "Bienvenido a VeuPlus",
    voicesTrained: "Voces Entrenadas",
    readyForSynthesis: "Listas para síntesis",
    activeBots: "Bots activos",
    voiceAssistants: "Asistentes de voz",
    documentsProcessed: "Documentos procesados",
    quickActions: "Acciones Rápidas",
    trainNewVoice: "Entrenar Nueva Voz",
    createChatbot: "Crear Chatbot",
    buildVoicebot: "Construir Voicebot",
    recentActivity: "Actividad Reciente",
    catalanDialects: "Dialectos Catalanes",
    voiceTraining: "Entrenamiento de Voz",
    trainNewVoiceTitle: "Entrenar Nueva Voz",
    voiceName: "Nombre de la Voz",
    catalanDialect: "Dialecto Catalán",
    description: "Descripción",
    audioFiles: "Archivos de Audio",
    uploadMultipleFiles: "Sube múltiples archivos de audio (mínimo 30 minutos recomendado)",
    startTraining: "Iniciar Entrenamiento",
    training: "Entrenando...",
    trainedVoices: "Voces Entrenadas",
    textToSynthesize: "Texto a Sintetizar",
    selectVoice: "Seleccionar Voz",
    selectTrainedVoice: "Selecciona una voz entrenada...",
    generateSpeech: "Generar Voz",
    synthesizing: "Sintetizando...",
    generatedAudio: "Audio Generado",
    downloadAudio: "Descargar Audio",
    createNewChatbot: "Crear Nuevo Chatbot",
    chatbotName: "Nombre del Chatbot",
    llmProvider: "Proveedor LLM",
    modelName: "Nombre del Modelo",
    temperature: "Temperatura",
    systemPrompt: "Prompt del Sistema",
    apiKey: "Clave API",
    knowledgeBaseSources: "Fuentes de la Base de Conocimiento",
    selectKnowledgeSources: "Selecciona fuentes de conocimiento...",
    createChatbotBtn: "Crear Chatbot",
    cancel: "Cancelar",
    yourChatbots: "Tus Chatbots",
    testChat: "Probar Chat",
    testing: "Probando",
    typeMessage: "Escribe tu mensaje...",
    send: "Enviar",
    supportedLanguages: "Idiomas Soportados",
    defaultLanguage: "Idioma por Defecto",
    createNewVoicebot: "Crear Nuevo Voicebot",
    selectVoiceModel: "Seleccionar Modelo de Voz",
    voicebotName: "Nombre del Voicebot",
    createVoicebotBtn: "Crear Voicebot",
    yourVoicebots: "Tus Voicebots",
    testVoiceChat: "Probar Chat de Voz",
    uploadDocuments: "Subir Documentos",
    uploading: "Subiendo...",
    uploadedDocuments: "Documentos Subidos",
    ready: "Listo",
    pending: "Pendiente",
    error: "Error",
    status: "Estado",
    name: "Nombre",
    type: "Tipo",
    actions: "Acciones",
    edit: "Editar",
    delete: "Eliminar",
    save: "Guardar",
    close: "Cerrar",
    catalan: "Catalán",
    spanish: "Español", 
    french: "Francés",
    english: "Inglés"
  },
  fr: {
    dashboard: "Tableau de bord",
    voiceLibrary: "Bibliothèque de Voix",
    speechSynthesis: "Synthèse Vocale",
    chatbots: "Chatbots",
    voicebots: "Voicebots",
    knowledgeBase: "Base de Connaissances",
    welcome: "Bienvenue à VeuPlus",
    voicesTrained: "Voix Entraînées",
    readyForSynthesis: "Prêtes pour la synthèse",
    activeBots: "Bots actifs",
    voiceAssistants: "Assistants vocaux",
    documentsProcessed: "Documents traités",
    quickActions: "Actions Rapides",
    trainNewVoice: "Entraîner Nouvelle Voix",
    createChatbot: "Créer Chatbot",
    buildVoicebot: "Construire Voicebot",
    recentActivity: "Activité Récente",
    catalanDialects: "Dialectes Catalans",
    voiceTraining: "Entraînement de Voix",
    trainNewVoiceTitle: "Entraîner Nouvelle Voix",
    voiceName: "Nom de la Voix",
    catalanDialect: "Dialecte Catalan",
    description: "Description",
    audioFiles: "Fichiers Audio",
    uploadMultipleFiles: "Téléchargez plusieurs fichiers audio (minimum 30 minutes recommandé)",
    startTraining: "Commencer l'Entraînement",
    training: "Entraînement...",
    trainedVoices: "Voix Entraînées",
    textToSynthesize: "Texte à Synthétiser",
    selectVoice: "Sélectionner Voix",
    selectTrainedVoice: "Sélectionnez une voix entraînée...",
    generateSpeech: "Générer Voix",
    synthesizing: "Synthèse...",
    generatedAudio: "Audio Généré",
    downloadAudio: "Télécharger Audio",
    createNewChatbot: "Créer Nouveau Chatbot",
    chatbotName: "Nom du Chatbot",
    llmProvider: "Fournisseur LLM",
    modelName: "Nom du Modèle",
    temperature: "Température",
    systemPrompt: "Prompt Système",
    apiKey: "Clé API",
    knowledgeBaseSources: "Sources Base de Connaissances",
    selectKnowledgeSources: "Sélectionner sources de connaissances...",
    createChatbotBtn: "Créer Chatbot",
    cancel: "Annuler",
    yourChatbots: "Vos Chatbots",
    testChat: "Tester Chat",
    testing: "Test",
    typeMessage: "Tapez votre message...",
    send: "Envoyer",
    supportedLanguages: "Langues Supportées",
    defaultLanguage: "Langue par Défaut",
    createNewVoicebot: "Créer Nouveau Voicebot",
    selectVoiceModel: "Sélectionner Modèle de Voix",
    voicebotName: "Nom du Voicebot",
    createVoicebotBtn: "Créer Voicebot",
    yourVoicebots: "Vos Voicebots",
    testVoiceChat: "Tester Chat Vocal",
    uploadDocuments: "Télécharger Documents",
    uploading: "Téléchargement...",
    uploadedDocuments: "Documents Téléchargés",
    ready: "Prêt",
    pending: "En attente",
    error: "Erreur",
    status: "Statut",
    name: "Nom",
    type: "Type",
    actions: "Actions",
    edit: "Modifier",
    delete: "Supprimer",
    save: "Sauvegarder",
    close: "Fermer",
    catalan: "Catalan",
    spanish: "Espagnol", 
    french: "Français",
    english: "Anglais"
  },
  en: {
    dashboard: "Dashboard",
    voiceLibrary: "Voice Library",
    speechSynthesis: "Speech Synthesis",
    chatbots: "Chatbots",
    voicebots: "Voicebots",
    knowledgeBase: "Knowledge Base",
    welcome: "Welcome to VeuPlus",
    voicesTrained: "Voices Trained",
    readyForSynthesis: "Ready for synthesis",
    activeBots: "Active bots",
    voiceAssistants: "Voice assistants",
    documentsProcessed: "Documents processed",
    quickActions: "Quick Actions",
    trainNewVoice: "Train New Voice",
    createChatbot: "Create Chatbot",
    buildVoicebot: "Build Voicebot",
    recentActivity: "Recent Activity",
    catalanDialects: "Catalan Dialects",
    voiceTraining: "Voice Training",
    trainNewVoiceTitle: "Train New Voice",
    voiceName: "Voice Name",
    catalanDialect: "Catalan Dialect",
    description: "Description",
    audioFiles: "Audio Files",
    uploadMultipleFiles: "Upload multiple audio files (minimum 30 minutes recommended)",
    startTraining: "Start Training",
    training: "Training...",
    trainedVoices: "Trained Voices",
    textToSynthesize: "Text to Synthesize",
    selectVoice: "Select Voice",
    selectTrainedVoice: "Select a trained voice...",
    generateSpeech: "Generate Speech",
    synthesizing: "Synthesizing...",
    generatedAudio: "Generated Audio",
    downloadAudio: "Download Audio",
    createNewChatbot: "Create New Chatbot",
    chatbotName: "Chatbot Name",
    llmProvider: "LLM Provider",
    modelName: "Model Name",
    temperature: "Temperature",
    systemPrompt: "System Prompt",
    apiKey: "API Key",
    knowledgeBaseSources: "Knowledge Base Sources",
    selectKnowledgeSources: "Select knowledge sources...",
    createChatbotBtn: "Create Chatbot",
    cancel: "Cancel",
    yourChatbots: "Your Chatbots",
    testChat: "Test Chat",
    testing: "Testing",
    typeMessage: "Type your message...",
    send: "Send",
    supportedLanguages: "Supported Languages",
    defaultLanguage: "Default Language",
    createNewVoicebot: "Create New Voicebot",
    selectVoiceModel: "Select Voice Model",
    voicebotName: "Voicebot Name",
    createVoicebotBtn: "Create Voicebot",
    yourVoicebots: "Your Voicebots",
    testVoiceChat: "Test Voice Chat",
    uploadDocuments: "Upload Documents",
    uploading: "Uploading...",
    uploadedDocuments: "Uploaded Documents",
    ready: "Ready",
    pending: "Pending",
    error: "Error",
    status: "Status",
    name: "Name",
    type: "Type",
    actions: "Actions",
    edit: "Edit",
    delete: "Delete",
    save: "Save",
    close: "Close",
    catalan: "Catalan",
    spanish: "Spanish", 
    french: "French",
    english: "English"
  }
};

// Catalan dialects
const CATALAN_DIALECTS = [
  { id: "central", name: "Català Central", region: "Barcelona, Girona" },
  { id: "balearic", name: "Balear", region: "Illes Balears" },
  { id: "valencian", name: "Valencià", region: "País Valencià" },
  { id: "andorran", name: "Andorrà", region: "Andorra" },
  { id: "rossellones", name: "Rossellonès", region: "França del Nord" },
  { id: "alguerese", name: "Alguerès", region: "L'Alguer, Sardenya" }
];

// Language options for bots
const LANGUAGE_OPTIONS = [
  { code: 'ca', name: 'Català', flag: '🏴󠁥󠁳󠁣󠁴󠁿' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'en', name: 'English', flag: '🇬🇧' }
];

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [currentLanguage, setCurrentLanguage] = useState('ca');
  const [voices, setVoices] = useState([]);
  const [chatbots, setChatbots] = useState([]);
  const [voicebots, setVoicebots] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [loading, setLoading] = useState(false);

  // Get translation function
  const t = (key) => translations[currentLanguage][key] || key;

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [voicesRes, chatbotsRes, voicebotsRes, kbRes] = await Promise.all([
        axios.get(`${API}/voices`),
        axios.get(`${API}/chatbots`),
        axios.get(`${API}/voicebots`),
        axios.get(`${API}/knowledge-base`)
      ]);
      
      setVoices(voicesRes.data.voices || []);
      setChatbots(chatbotsRes.data.bots || []);
      setVoicebots(voicebotsRes.data.bots || []);
      setKnowledgeBase(kbRes.data.items || []);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  // Professional VeuPlus Logo Component
  const VeuPlusLogo = () => (
    <div className="flex items-center">
      <div className="relative">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 flex items-center justify-center shadow-xl transform transition-all duration-300 hover:scale-110 hover:rotate-3">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C10.34 2 9 3.37 9 5.07V11.93C9 13.63 10.34 15 12 15S15 13.63 15 11.93V5.07C15 3.37 13.66 2 12 2ZM12 4C12.55 4 13 4.45 13 5.07V11.93C13 12.48 12.55 13 12 13S11 12.48 11 11.93V5.07C11 4.45 11.45 4 12 4ZM19 10V12C19 15.87 15.87 19 12 19S5 15.87 5 12V10H7V12C7 14.76 9.24 17 12 17S17 14.76 17 12V10H19ZM11 20V22H13V20H17V22H19V20H16.93C18.76 19.96 20.3 18.44 20.3 16.61V14.61H18.3V16.61C18.3 17.33 17.72 17.91 17 17.91H7C6.28 17.91 5.7 17.33 5.7 16.61V14.61H3.7V16.61C3.7 18.44 5.24 19.96 7.07 20H5V22H7V20H11Z"/>
          </svg>
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-600 animate-pulse opacity-20"></div>
        </div>
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full flex items-center justify-center">
          <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
        </div>
      </div>
      <div className="ml-4">
        <div className="text-2xl font-bold">
          <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-indigo-600 bg-clip-text text-transparent">
            Veu
          </span>
          <span className="bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 bg-clip-text text-transparent">
            Plus
          </span>
        </div>
        <div className="text-xs text-gray-400 font-medium tracking-wider">
          CATALAN AI PLATFORM
        </div>
      </div>
    </div>
  );

  // Enhanced Language Dropdown Component
  const LanguageSelector = () => {
    const [isOpen, setIsOpen] = useState(false);
    const currentLang = LANGUAGE_OPTIONS.find(lang => lang.code === currentLanguage);

    return (
      <div className="relative mb-6">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-3 bg-gradient-to-r from-gray-800 to-gray-700 text-white px-4 py-3 rounded-2xl shadow-lg hover:from-gray-700 hover:to-gray-600 transition-all duration-300 transform hover:scale-105 min-w-[160px] justify-between"
        >
          <div className="flex items-center space-x-2">
            <span className="text-lg">{currentLang?.flag}</span>
            <span className="font-medium">{currentLang?.name}</span>
          </div>
          <svg 
            className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 mt-2 w-full bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden z-50">
            {LANGUAGE_OPTIONS.map(lang => (
              <button
                key={lang.code}
                onClick={() => {
                  setCurrentLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors duration-200 ${
                  currentLanguage === lang.code ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                }`}
              >
                <span className="text-lg">{lang.flag}</span>
                <span className="font-medium">{lang.name}</span>
                {currentLanguage === lang.code && (
                  <svg className="w-4 h-4 ml-auto text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Navigation
  const Navigation = () => (
    <div className="bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white w-80 min-h-screen shadow-2xl border-r border-gray-700">
      <div className="p-6">
        {/* Logo */}
        <div className="mb-8">
          <VeuPlusLogo />
        </div>
        
        {/* Language Selector */}
        <LanguageSelector />
        
        {/* Navigation Items */}
        <nav className="space-y-2">
          {[
            { id: 'dashboard', label: t('dashboard'), icon: '🏠', gradient: 'from-blue-500 to-blue-600' },
            { id: 'voices', label: t('voiceLibrary'), icon: '🎤', gradient: 'from-purple-500 to-purple-600' },
            { id: 'synthesis', label: t('speechSynthesis'), icon: '🗣️', gradient: 'from-green-500 to-green-600' },
            { id: 'chatbots', label: t('chatbots'), icon: '💬', gradient: 'from-orange-500 to-orange-600' },
            { id: 'voicebots', label: t('voicebots'), icon: '🤖', gradient: 'from-pink-500 to-pink-600' },
            { id: 'knowledge', label: t('knowledgeBase'), icon: '📚', gradient: 'from-indigo-500 to-indigo-600' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`w-full text-left p-4 rounded-2xl transition-all duration-300 transform hover:scale-105 ${
                currentView === item.id 
                  ? `bg-gradient-to-r ${item.gradient} text-white shadow-2xl scale-105` 
                  : 'text-gray-300 hover:bg-gradient-to-r hover:from-gray-700 hover:to-gray-600 hover:text-white'
              }`}
            >
              <div className="flex items-center">
                <span className="text-2xl mr-4">{item.icon}</span>
                <span className="font-medium text-lg">{item.label}</span>
              </div>
            </button>
          ))}
        </nav>

        {/* Status Panel */}
        <div className="mt-8 p-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded-2xl border border-gray-600">
          <div className="text-sm text-gray-300 mb-2 font-medium">Platform Status</div>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <div className="absolute inset-0 w-3 h-3 bg-green-400 rounded-full animate-ping opacity-75"></div>
            </div>
            <span className="text-green-400 font-semibold">Online & Ready</span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            All systems operational
          </div>
        </div>
      </div>
    </div>
  );

  // Enhanced Dashboard View
  const Dashboard = () => (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-800 via-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
              {t('welcome')}
            </h1>
            <p className="text-xl text-gray-600">
              Professional Catalan Voice AI Platform
            </p>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="group bg-white p-6 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-blue-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">{t('voicesTrained')}</h3>
                  <p className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-blue-600 bg-clip-text text-transparent">
                    {voices.length}
                  </p>
                  <p className="text-blue-500 text-sm font-medium">{t('readyForSynthesis')}</p>
                </div>
                <div className="text-5xl group-hover:scale-110 transition-transform duration-300">🎤</div>
              </div>
            </div>
            
            <div className="group bg-white p-6 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-green-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">{t('chatbots')}</h3>
                  <p className="text-4xl font-bold bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">
                    {chatbots.length}
                  </p>
                  <p className="text-green-500 text-sm font-medium">{t('activeBots')}</p>
                </div>
                <div className="text-5xl group-hover:scale-110 transition-transform duration-300">💬</div>
              </div>
            </div>
            
            <div className="group bg-white p-6 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-purple-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">{t('voicebots')}</h3>
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-500 to-purple-600 bg-clip-text text-transparent">
                    {voicebots.length}
                  </p>
                  <p className="text-purple-500 text-sm font-medium">{t('voiceAssistants')}</p>
                </div>
                <div className="text-5xl group-hover:scale-110 transition-transform duration-300">🤖</div>
              </div>
            </div>
            
            <div className="group bg-white p-6 rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-orange-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">{t('knowledgeBase')}</h3>
                  <p className="text-4xl font-bold bg-gradient-to-r from-orange-500 to-orange-600 bg-clip-text text-transparent">
                    {knowledgeBase.length}
                  </p>
                  <p className="text-orange-500 text-sm font-medium">{t('documentsProcessed')}</p>
                </div>
                <div className="text-5xl group-hover:scale-110 transition-transform duration-300">📚</div>
              </div>
            </div>
          </div>

          {/* Action Panels */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="mr-3 text-3xl">⚡</span>
                {t('quickActions')}
              </h3>
              <div className="space-y-4">
                <button 
                  onClick={() => setCurrentView('voices')}
                  className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-2xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center justify-center">
                    <span className="text-2xl mr-3">🎤</span>
                    <span className="font-semibold">{t('trainNewVoice')}</span>
                  </div>
                </button>
                <button 
                  onClick={() => setCurrentView('chatbots')}
                  className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-2xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center justify-center">
                    <span className="text-2xl mr-3">💬</span>
                    <span className="font-semibold">{t('createChatbot')}</span>
                  </div>
                </button>
                <button 
                  onClick={() => setCurrentView('voicebots')}
                  className="w-full bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-2xl hover:from-purple-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center justify-center">
                    <span className="text-2xl mr-3">🤖</span>
                    <span className="font-semibold">{t('buildVoicebot')}</span>
                  </div>
                </button>
              </div>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="mr-3 text-3xl">📊</span>
                {t('recentActivity')}
              </h3>
              <div className="space-y-4">
                <div className="flex items-center p-3 bg-green-50 rounded-2xl border border-green-100">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">Voice training completed</span>
                </div>
                <div className="flex items-center p-3 bg-blue-50 rounded-2xl border border-blue-100">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">New chatbot created</span>
                </div>
                <div className="flex items-center p-3 bg-orange-50 rounded-2xl border border-orange-100">
                  <div className="w-3 h-3 bg-orange-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">Documents uploaded</span>
                </div>
                <div className="flex items-center p-3 bg-purple-50 rounded-2xl border border-purple-100">
                  <div className="w-3 h-3 bg-purple-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">Voicebot deployed</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-xl border border-gray-100">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="mr-3 text-3xl">🏴󠁥󠁳󠁣󠁴󠁿</span>
                {t('catalanDialects')}
              </h3>
              <div className="space-y-3">
                {CATALAN_DIALECTS.slice(0, 4).map(dialect => (
                  <div key={dialect.id} className="p-3 bg-gray-50 rounded-2xl border border-gray-100 hover:bg-gray-100 transition-colors duration-200">
                    <div className="font-semibold text-gray-800">{dialect.name}</div>
                    <div className="text-sm text-gray-500">{dialect.region}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Placeholder for other components (VoiceTraining, SpeechSynthesis, etc.)
  const VoiceTraining = () => (
    <div className="p-8 bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 min-h-screen">
      <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-8">
        {t('voiceTraining')}
      </h2>
      <div className="bg-white p-8 rounded-3xl shadow-xl">
        <p className="text-gray-600">Voice training interface will be implemented here...</p>
      </div>
    </div>
  );

  const SpeechSynthesis = () => (
    <div className="p-8 bg-gradient-to-br from-green-50 via-blue-50 to-teal-50 min-h-screen">
      <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent mb-8">
        {t('speechSynthesis')}
      </h2>
      <div className="bg-white p-8 rounded-3xl shadow-xl">
        <p className="text-gray-600">Speech synthesis interface will be implemented here...</p>
      </div>
    </div>
  );

  const Chatbots = () => (
    <div className="p-8 bg-gradient-to-br from-orange-50 via-pink-50 to-red-50 min-h-screen">
      <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent mb-8">
        {t('chatbots')}
      </h2>
      <div className="bg-white p-8 rounded-3xl shadow-xl">
        <p className="text-gray-600">Chatbot interface will be implemented here...</p>
      </div>
    </div>
  );

  const Voicebots = () => (
    <div className="p-8 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 min-h-screen">
      <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-8">
        {t('voicebots')}
      </h2>
      <div className="bg-white p-8 rounded-3xl shadow-xl">
        <p className="text-gray-600">Voicebot interface will be implemented here...</p>
      </div>
    </div>
  );

  const KnowledgeBase = () => (
    <div className="p-8 bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 min-h-screen">
      <h2 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent mb-8">
        {t('knowledgeBase')}
      </h2>
      <div className="bg-white p-8 rounded-3xl shadow-xl">
        <p className="text-gray-600">Knowledge base interface will be implemented here...</p>
      </div>
    </div>
  );

  // Render current view
  const renderView = () => {
    switch(currentView) {
      case 'dashboard': return <Dashboard />;
      case 'voices': return <VoiceTraining />;
      case 'synthesis': return <SpeechSynthesis />;
      case 'chatbots': return <Chatbots />;
      case 'voicebots': return <Voicebots />;
      case 'knowledge': return <KnowledgeBase />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Navigation />
      <div className="flex-1">
        {renderView()}
      </div>
    </div>
  );
}

export default App;

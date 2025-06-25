import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DeveloperDashboard from './DeveloperDashboard';
import VoiceTrainingAdvanced from './VoiceTrainingAdvanced';
import VoiceSelectionModal from './VoiceSelectionModal';
import CallCenterDashboard from './CallCenterDashboard';
import CallCenterLanding from './CallCenterLanding';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Complete Multi-language translations
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
    english: "Anglès",
    playAudio: "Reproduir Àudio",
    stopAudio: "Aturar Àudio",
    voiceQuality: "Qualitat de Veu",
    hyperrealistic: "Hiperrealistic",
    enhanced: "Millorat",
    selectFromKnowledge: "Seleccionar de la Base de Coneixement",
    knowledgeSelected: "documents seleccionats",
    selectDocuments: "Seleccionar Documents",
    confirmDelete: "Confirmar Eliminació",
    deleteConfirmation: "Estàs segur que vols eliminar aquest element?",
    yes: "Sí",
    no: "No",
    creating: "Creant...",
    deleting: "Eliminant...",
    useRealCatalanVoices: "Usar Veus Catalanes Reals",
    downloadCatalanDataset: "Descarregar Dataset Català",
    xttsCatalanTraining: "Entrenament XTTS Català"
  },
  es: {
    dashboard: "Panel de Control",
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
    knowledgeBaseSources: "Fuentes de Base de Conocimiento",
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
    english: "Inglés",
    playAudio: "Reproducir Audio",
    stopAudio: "Detener Audio",
    voiceQuality: "Calidad de Voz",
    hyperrealistic: "Hiperrealista",
    enhanced: "Mejorado",
    selectFromKnowledge: "Seleccionar de la Base de Conocimiento",
    knowledgeSelected: "documentos seleccionados",
    selectDocuments: "Seleccionar Documentos",
    confirmDelete: "Confirmar Eliminación",
    deleteConfirmation: "¿Estás seguro de que quieres eliminar este elemento?",
    yes: "Sí",
    no: "No",
    creating: "Creando...",
    deleting: "Eliminando...",
    useRealCatalanVoices: "Usar Voces Catalanas Reales",
    downloadCatalanDataset: "Descargar Dataset Catalán",
    xttsCatalanTraining: "Entrenamiento XTTS Catalán"
  },
  fr: {
    dashboard: "Tableau de Bord",
    voiceLibrary: "Bibliothèque de Voix",
    speechSynthesis: "Synthèse Vocale",
    chatbots: "Chatbots",
    voicebots: "Voicebots",
    knowledgeBase: "Base de Connaissances",
    welcome: "Bienvenue sur VeuPlus",
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
    voiceTraining: "Entraînement Vocal",
    trainNewVoiceTitle: "Entraîner Nouvelle Voix",
    voiceName: "Nom de la Voix",
    catalanDialect: "Dialecte Catalan",
    description: "Description",
    audioFiles: "Fichiers Audio",
    uploadMultipleFiles: "Télécharger plusieurs fichiers audio (minimum 30 minutes recommandé)",
    startTraining: "Commencer l'Entraînement",
    training: "Entraînement...",
    trainedVoices: "Voix Entraînées",
    textToSynthesize: "Texte à Synthétiser",
    selectVoice: "Sélectionner Voix",
    selectTrainedVoice: "Sélectionner une voix entraînée...",
    generateSpeech: "Générer Voix",
    synthesizing: "Synthétisation...",
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
    testing: "Test en cours",
    typeMessage: "Tapez votre message...",
    send: "Envoyer",
    supportedLanguages: "Langues Supportées",
    defaultLanguage: "Langue par Défaut",
    createNewVoicebot: "Créer Nouveau Voicebot",
    selectVoiceModel: "Sélectionner Modèle Vocal",
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
    english: "Anglais",
    playAudio: "Lire Audio",
    stopAudio: "Arrêter Audio",
    voiceQuality: "Qualité Vocale",
    hyperrealistic: "Hyperréaliste",
    enhanced: "Amélioré",
    selectFromKnowledge: "Sélectionner de la Base de Connaissances",
    knowledgeSelected: "documents sélectionnés",
    selectDocuments: "Sélectionner Documents",
    confirmDelete: "Confirmer Suppression",
    deleteConfirmation: "Êtes-vous sûr de vouloir supprimer cet élément?",
    yes: "Oui",
    no: "Non",
    creating: "Création...",
    deleting: "Suppression...",
    useRealCatalanVoices: "Utiliser Vraies Voix Catalanes",
    downloadCatalanDataset: "Télécharger Dataset Catalan",
    xttsCatalanTraining: "Entraînement XTTS Catalan"
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
    english: "English",
    playAudio: "Play Audio",
    stopAudio: "Stop Audio",
    voiceQuality: "Voice Quality",
    hyperrealistic: "Hyperrealistic",
    enhanced: "Enhanced",
    selectFromKnowledge: "Select from Knowledge Base",
    knowledgeSelected: "documents selected",
    selectDocuments: "Select Documents",
    confirmDelete: "Confirm Delete",
    deleteConfirmation: "Are you sure you want to delete this item?",
    yes: "Yes",
    no: "No",
    creating: "Creating...",
    deleting: "Deleting...",
    useRealCatalanVoices: "Use Real Catalan Voices",
    downloadCatalanDataset: "Download Catalan Dataset",
    xttsCatalanTraining: "XTTS Catalan Training"
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

  // Modals state
  const [showVoiceTrainingModal, setShowVoiceTrainingModal] = useState(false);
  const [showChatbotModal, setShowChatbotModal] = useState(false);
  const [showVoicebotModal, setShowVoicebotModal] = useState(false);
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [showTestChatModal, setShowTestChatModal] = useState(false);
  const [showTestVoiceModal, setShowTestVoiceModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showVoiceSelectionModal, setShowVoiceSelectionModal] = useState(false);

  // Selected items for modals
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [selectedVoicebot, setSelectedVoicebot] = useState(null);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [selectedVoice, setSelectedVoice] = useState(null);
  // Call center state
  const [showCallCenterCreation, setShowCallCenterCreation] = useState(false);
  const [callCenters, setCallCenters] = useState([]);

  // Get translation function
  const t = (key) => translations[currentLanguage][key] || translations.en[key] || key;

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

  // Delete functionality
  const handleDelete = async () => {
    if (!itemToDelete) return;
    
    try {
      setLoading(true);
      const { type, id } = itemToDelete;
      
      switch(type) {
        case 'chatbot':
          await axios.delete(`${API}/chatbots/${id}`);
          break;
        case 'voicebot':
          await axios.delete(`${API}/voicebots/${id}`);
          break;
        case 'voice':
          await axios.delete(`${API}/voices/${id}`);
          break;
        case 'knowledge':
          await axios.delete(`${API}/knowledge-base/${id}`);
          break;
      }
      
      await loadData();
      setShowDeleteModal(false);
      setItemToDelete(null);
    } catch (error) {
      console.error('Error deleting item:', error);
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = (type, id, name) => {
    setItemToDelete({ type, id, name });
    setShowDeleteModal(true);
  };

  const [voiceSelectionCallback, setVoiceSelectionCallback] = useState(null);

  // Voice selection helper
  const openVoiceSelection = (callback, currentVoiceId = null) => {
    setSelectedVoice(currentVoiceId);
    setVoiceSelectionCallback(() => callback);
    setShowVoiceSelectionModal(true);
  };

  const handleVoiceSelection = (voice) => {
    setSelectedVoice(voice);
    if (voiceSelectionCallback) {
      voiceSelectionCallback(voice);
    }
    setShowVoiceSelectionModal(false);
  };

  // Download Catalan Dataset
  const downloadCatalanDataset = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/voices/download-catalan-dataset`);
      console.log('Catalan dataset download initiated:', response.data);
    } catch (error) {
      console.error('Error downloading Catalan dataset:', error);
    } finally {
      setLoading(false);
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

  // Delete Confirmation Modal
  const DeleteModal = () => {
    if (!showDeleteModal || !itemToDelete) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-3xl p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">{t('confirmDelete')}</h3>
            <p className="text-gray-600 mb-6">
              {t('deleteConfirmation')}
              <br />
              <strong>"{itemToDelete.name}"</strong>
            </p>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="flex-1 py-3 px-6 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50"
              >
                {t('no')}
              </button>
              <button
                onClick={handleDelete}
                disabled={loading}
                className="flex-1 py-3 px-6 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50"
              >
                {loading ? t('deleting') : t('yes')}
              </button>
            </div>
          </div>
        </div>
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
            { id: 'training', label: t('voiceTraining'), icon: '🎤', gradient: 'from-green-500 to-green-600' },
            { id: 'training-advanced', label: 'XTTS v2 Training', icon: '🚀', gradient: 'from-red-500 to-red-600' },
            { id: 'call-center', label: 'Call Center AI', icon: '📞', gradient: 'from-indigo-500 to-indigo-600' },
            { id: 'developer', label: 'Developer Dashboard', icon: '👨‍💻', gradient: 'from-gray-500 to-gray-600' },
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

        {/* XTTS Catalan Training Panel */}
        <div className="mt-8 p-4 bg-gradient-to-r from-purple-700 to-blue-600 rounded-2xl border border-purple-500">
          <div className="text-sm text-purple-100 mb-2 font-medium">{t('xttsCatalanTraining')}</div>
          <button
            onClick={downloadCatalanDataset}
            disabled={loading}
            className="w-full py-2 px-4 bg-white bg-opacity-20 rounded-xl text-white hover:bg-opacity-30 transition-all duration-200 text-sm font-medium disabled:opacity-50"
          >
            {loading ? '⏳ Downloading...' : t('downloadCatalanDataset')}
          </button>
          <div className="text-xs text-purple-200 mt-1">
            {t('useRealCatalanVoices')}
          </div>
        </div>

        {/* Status Panel */}
        <div className="mt-4 p-4 bg-gradient-to-r from-gray-700 to-gray-600 rounded-2xl border border-gray-600">
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
              Professional Catalan Voice AI Platform with Hyperrealistic Voices
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
                  onClick={() => setShowVoiceTrainingModal(true)}
                  className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-2xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center justify-center">
                    <span className="text-2xl mr-3">🎤</span>
                    <span className="font-semibold">{t('trainNewVoice')}</span>
                  </div>
                </button>
                <button 
                  onClick={() => setShowChatbotModal(true)}
                  className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-2xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <div className="flex items-center justify-center">
                    <span className="text-2xl mr-3">💬</span>
                    <span className="font-semibold">{t('createChatbot')}</span>
                  </div>
                </button>
                <button 
                  onClick={() => setShowVoicebotModal(true)}
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
                  <span className="text-gray-700 font-medium">Hyperrealistic voice trained</span>
                </div>
                <div className="flex items-center p-3 bg-blue-50 rounded-2xl border border-blue-100">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">Catalan dataset loaded</span>
                </div>
                <div className="flex items-center p-3 bg-orange-50 rounded-2xl border border-orange-100">
                  <div className="w-3 h-3 bg-orange-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">OpenSLR voices ready</span>
                </div>
                <div className="flex items-center p-3 bg-purple-50 rounded-2xl border border-purple-100">
                  <div className="w-3 h-3 bg-purple-500 rounded-full mr-4 animate-pulse"></div>
                  <span className="text-gray-700 font-medium">XTTS v2 model active</span>
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

  // Voice Training Modal Component
  const VoiceTrainingModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      dialect: 'central',
      description: '',
      audioFiles: [],
      use_catalan_dataset: true
    });
    const [isTraining, setIsTraining] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setIsTraining(true);
      
      try {
        const formDataToSend = new FormData();
        formDataToSend.append('name', formData.name);
        formDataToSend.append('dialect', formData.dialect);
        formDataToSend.append('description', formData.description);
        formDataToSend.append('use_catalan_dataset', formData.use_catalan_dataset);
        
        for (let file of formData.audioFiles) {
          formDataToSend.append('audio_files', file);
        }
        
        await axios.post(`${API}/voices/train`, formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        await loadData();
        setShowVoiceTrainingModal(false);
        setFormData({ name: '', dialect: 'central', description: '', audioFiles: [], use_catalan_dataset: true });
      } catch (error) {
        console.error('Error training voice:', error);
      } finally {
        setIsTraining(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-3xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              {t('trainNewVoiceTitle')}
            </h2>
            <button
              onClick={() => setShowVoiceTrainingModal(false)}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('voiceName')}
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('catalanDialect')}
              </label>
              <select
                value={formData.dialect}
                onChange={(e) => setFormData({...formData, dialect: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {CATALAN_DIALECTS.map(dialect => (
                  <option key={dialect.id} value={dialect.id}>
                    {dialect.name} - {dialect.region}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={formData.use_catalan_dataset}
                  onChange={(e) => setFormData({...formData, use_catalan_dataset: e.target.checked})}
                  className="h-5 w-5 text-purple-600 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">{t('useRealCatalanVoices')}</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">Uses projecte-aina/openslr-slr69-ca dataset for enhanced quality</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('description')}
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent h-24"
                placeholder="Descripció de la veu..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('audioFiles')} (Optional if using Catalan dataset)
              </label>
              <input
                type="file"
                multiple
                accept="audio/*"
                onChange={(e) => setFormData({...formData, audioFiles: Array.from(e.target.files)})}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-2">
                {t('uploadMultipleFiles')}
              </p>
            </div>
            
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setShowVoiceTrainingModal(false)}
                className="flex-1 py-3 px-6 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors duration-200"
              >
                {t('cancel')}
              </button>
              <button
                type="submit"
                disabled={isTraining}
                className="flex-1 py-3 px-6 bg-gradient-to-r from-purple-500 to-blue-600 text-white rounded-xl hover:from-purple-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50"
              >
                {isTraining ? t('training') : t('startTraining')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Enhanced Speech Synthesis View
  const SpeechSynthesis = () => {
    const [text, setText] = useState('Hola, sóc una veu sintètica catalana d\'alta qualitat!');
    const [selectedVoice, setSelectedVoice] = useState('');
    const [isSynthesizing, setIsSynthesizing] = useState(false);
    const [audioUrl, setAudioUrl] = useState('');
    const [audioData, setAudioData] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);

    const handleSynthesis = async () => {
      if (!text) return;
      
      setIsSynthesizing(true);
      try {
        const response = await axios.post(`${API}/synthesis`, {
          text,
          voice_model_id: selectedVoice || 'catalan_enhanced',
          language: 'ca',
          enhanced: true
        });
        
        setAudioUrl(response.data.audio_url);
        setAudioData(response.data);
      } catch (error) {
        console.error('Error synthesizing speech:', error);
      } finally {
        setIsSynthesizing(false);
      }
    };

    const playAudio = () => {
      if (audioUrl) {
        const audio = new Audio(`${BACKEND_URL}${audioUrl}`);
        setIsPlaying(true);
        audio.play();
        audio.onended = () => setIsPlaying(false);
      }
    };

    return (
      <div className="p-8 bg-gradient-to-br from-green-50 via-blue-50 to-teal-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent mb-8">
            {t('speechSynthesis')}
          </h2>
          
          <div className="bg-white rounded-3xl shadow-xl p-8">
            <div className="space-y-6">
              <div>
                <label className="block text-lg font-semibold text-gray-700 mb-3">
                  {t('textToSynthesize')}
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  className="w-full p-4 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-green-500 focus:border-transparent h-32 text-lg"
                  placeholder="Escriu el text que vols sintetitzar..."
                />
              </div>
              
              <div>
                <label className="block text-lg font-semibold text-gray-700 mb-3">
                  {t('selectVoice')}
                </label>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="w-full p-4 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-lg"
                >
                  <option value="">Enhanced Catalan (Default)</option>
                  {voices.filter(v => v.status === 'ready').map(voice => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} - {voice.dialect}
                      {voice.training_quality && (
                        <span className="text-sm"> ({voice.training_quality})</span>
                      )}
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={handleSynthesis}
                disabled={!text || isSynthesizing}
                className="w-full py-4 px-8 bg-gradient-to-r from-green-500 to-teal-600 text-white rounded-2xl hover:from-green-600 hover:to-teal-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 text-lg font-semibold"
              >
                {isSynthesizing ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    {t('synthesizing')}
                  </div>
                ) : (
                  t('generateSpeech')
                )}
              </button>
              
              {audioData && (
                <div className="mt-8 p-6 bg-gray-50 rounded-2xl">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">{t('generatedAudio')}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <p><strong>Voice:</strong> {audioData.voice_model}</p>
                      <p><strong>Dialect:</strong> {audioData.dialect || 'Central Català'}</p>
                      <p><strong>Quality:</strong> {audioData.quality || 'Enhanced'}</p>
                      <p><strong>Method:</strong> {audioData.synthesis_method || 'XTTS v2'}</p>
                      {audioData.real_audio && (
                        <p className="text-green-600 font-semibold">✅ Real Catalan Voice!</p>
                      )}
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={playAudio}
                        disabled={isPlaying}
                        className="flex-1 py-3 px-6 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors duration-200 disabled:opacity-50"
                      >
                        {isPlaying ? t('stopAudio') : t('playAudio')}
                      </button>
                      <a
                        href={`${BACKEND_URL}${audioUrl}`}
                        download
                        className="flex-1 py-3 px-6 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors duration-200 text-center"
                      >
                        {t('downloadAudio')}
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Voice Training View
  const VoiceTraining = () => (
    <div className="p-8 bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            {t('voiceTraining')}
          </h2>
          <button
            onClick={() => setShowVoiceTrainingModal(true)}
            className="py-3 px-6 bg-gradient-to-r from-purple-500 to-blue-600 text-white rounded-2xl hover:from-purple-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            {t('trainNewVoice')}
          </button>
        </div>
        
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">{t('trainedVoices')}</h3>
          
          {voices.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎤</div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No voices trained yet</h3>
              <p className="text-gray-500">Train your first hyperrealistic Catalan voice!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {voices.map(voice => (
                <div key={voice.id} className="border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-bold text-gray-800">{voice.name}</h4>
                    <div className="flex space-x-2">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        voice.status === 'ready' ? 'bg-green-100 text-green-800' :
                        voice.status === 'training' ? 'bg-yellow-100 text-yellow-800' :
                        voice.status === 'pending' ? 'bg-gray-100 text-gray-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {t(voice.status)}
                      </span>
                      <button
                        onClick={() => confirmDelete('voice', voice.id, voice.name)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title={t('delete')}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600">
                    <p><strong>Dialect:</strong> {CATALAN_DIALECTS.find(d => d.id === voice.dialect)?.name}</p>
                    {voice.description && <p><strong>Description:</strong> {voice.description}</p>}
                    {voice.training_quality && (
                      <p><strong>Quality:</strong> 
                        <span className={`ml-1 px-2 py-1 rounded text-xs ${
                          voice.training_quality.includes('hyperrealistic') ? 'bg-purple-100 text-purple-800' :
                          voice.training_quality.includes('enhanced') ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {voice.training_quality}
                        </span>
                      </p>
                    )}
                    {voice.catalan_enhanced && (
                      <p className="text-green-600 font-semibold">✅ Catalan Enhanced</p>
                    )}
                    {voice.phonetic_enhanced && (
                      <p className="text-blue-600 font-semibold">🎯 Phonetic Enhanced</p>
                    )}
                  </div>
                  
                  {voice.status === 'training' && voice.progress !== undefined && (
                    <div className="mt-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Training Progress</span>
                        <span>{voice.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${voice.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Knowledge Base Selection Modal
  const KnowledgeSelectionModal = ({ isOpen, onClose, onSelect, selectedIds = [] }) => {
    const [tempSelected, setTempSelected] = useState(selectedIds);

    const handleToggle = (id) => {
      setTempSelected(prev => 
        prev.includes(id) 
          ? prev.filter(item => item !== id)
          : [...prev, id]
      );
    };

    const handleConfirm = () => {
      onSelect(tempSelected);
      onClose();
    };

    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-3xl p-8 max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-800">{t('selectFromKnowledge')}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>
          
          <div className="space-y-3 mb-6">
            {knowledgeBase.map(item => (
              <div key={item.id} className="flex items-center p-3 border border-gray-200 rounded-xl hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={tempSelected.includes(item.id)}
                  onChange={() => handleToggle(item.id)}
                  className="mr-3 h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <div className="flex-1">
                  <h4 className="font-medium text-gray-800">{item.name}</h4>
                  <p className="text-sm text-gray-500">{item.file_type.toUpperCase()}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={onClose}
              className="flex-1 py-3 px-6 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50"
            >
              {t('cancel')}
            </button>
            <button
              onClick={handleConfirm}
              className="flex-1 py-3 px-6 bg-blue-500 text-white rounded-xl hover:bg-blue-600"
            >
              {t('selectDocuments')} ({tempSelected.length})
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Enhanced Chatbot Creation Modal with better API configuration
  const ChatbotModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      llm_provider: 'openai',
      model_name: 'gpt-3.5-turbo',
      temperature: 0.7,
      system_prompt: 'Ets un assistent d\'IA que parla català. Respon sempre en català de manera útil i amigable.',
      api_key: '',
      knowledge_base_ids: []
    });
    const [isCreating, setIsCreating] = useState(false);
    const [showKnowledgeSelection, setShowKnowledgeSelection] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setIsCreating(true);
      
      try {
        await axios.post(`${API}/chatbots`, formData);
        await loadData();
        setShowChatbotModal(false);
        setFormData({
          name: '',
          llm_provider: 'openai',
          model_name: 'gpt-3.5-turbo',
          temperature: 0.7,
          system_prompt: 'Ets un assistent d\'IA que parla català. Respon sempre en català de manera útil i amigable.',
          api_key: '',
          knowledge_base_ids: []
        });
      } catch (error) {
        console.error('Error creating chatbot:', error);
      } finally {
        setIsCreating(false);
      }
    };

    return (
      <>
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-3xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                {t('createNewChatbot')}
              </h2>
              <button
                onClick={() => setShowChatbotModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('chatbotName')}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('llmProvider')}
                  </label>
                  <select
                    value={formData.llm_provider}
                    onChange={(e) => setFormData({...formData, llm_provider: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="claude">Claude</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('modelName')}
                  </label>
                  <select
                    value={formData.model_name}
                    onChange={(e) => setFormData({...formData, model_name: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {formData.llm_provider === 'openai' && (
                      <>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                      </>
                    )}
                    {formData.llm_provider === 'claude' && (
                      <>
                        <option value="claude-3-haiku">Claude 3 Haiku</option>
                        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="claude-3-opus">Claude 3 Opus</option>
                      </>
                    )}
                    {formData.llm_provider === 'gemini' && (
                      <>
                        <option value="gemini-pro">Gemini Pro</option>
                        <option value="gemini-pro-vision">Gemini Pro Vision</option>
                      </>
                    )}
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('temperature')} ({formData.temperature})
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData({...formData, temperature: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('systemPrompt')}
                </label>
                <textarea
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({...formData, system_prompt: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent h-24"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('apiKey')} (Optional - uses global key if empty)
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({...formData, api_key: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Leave empty to use global API key"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('knowledgeBaseSources')}
                </label>
                <button
                  type="button"
                  onClick={() => setShowKnowledgeSelection(true)}
                  className="w-full p-3 border border-gray-300 rounded-xl text-left hover:bg-gray-50 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {formData.knowledge_base_ids.length > 0 
                    ? `${formData.knowledge_base_ids.length} ${t('knowledgeSelected')}`
                    : t('selectKnowledgeSources')
                  }
                </button>
              </div>
              
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setShowChatbotModal(false)}
                  className="flex-1 py-3 px-6 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors duration-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isCreating}
                  className="flex-1 py-3 px-6 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-xl hover:from-green-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50"
                >
                  {isCreating ? t('creating') : t('createChatbotBtn')}
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <KnowledgeSelectionModal
          isOpen={showKnowledgeSelection}
          onClose={() => setShowKnowledgeSelection(false)}
          onSelect={(ids) => setFormData({...formData, knowledge_base_ids: ids})}
          selectedIds={formData.knowledge_base_ids}
        />
      </>
    );
  };

  // Enhanced Chat Test Modal
  const ChatTestModal = ({ bot, onClose }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isSending, setIsSending] = useState(false);

    const sendMessage = async () => {
      if (!inputMessage.trim()) return;
      
      const userMessage = { role: 'user', content: inputMessage };
      setMessages(prev => [...prev, userMessage]);
      setIsSending(true);
      
      try {
        const response = await axios.post(`${API}/chatbots/chat`, {
          message: inputMessage,
          bot_id: bot.id,
          conversation_history: messages
        });
        
        const botMessage = { role: 'assistant', content: response.data.reply };
        setMessages(prev => [...prev, botMessage]);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage = { 
          role: 'assistant', 
          content: 'Error: Unable to get response. Please check API configuration.' 
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsSending(false);
        setInputMessage('');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-3xl p-6 max-w-2xl w-full mx-4 h-[600px] flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">Test: {bot.name}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 border border-gray-200 rounded-xl">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : msg.content.includes('Error:') 
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isSending && sendMessage()}
              className="flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={t('typeMessage')}
              disabled={isSending}
            />
            <button
              onClick={sendMessage}
              disabled={isSending || !inputMessage.trim()}
              className="py-3 px-6 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50"
            >
              {t('send')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Enhanced Chatbots View with delete functionality
  const Chatbots = () => (
    <div className="p-8 bg-gradient-to-br from-orange-50 via-pink-50 to-red-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
            {t('chatbots')}
          </h2>
          <button
            onClick={() => setShowChatbotModal(true)}
            className="py-3 px-6 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-2xl hover:from-green-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            {t('createNewChatbot')}
          </button>
        </div>
        
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">{t('yourChatbots')}</h3>
          
          {chatbots.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No chatbots created yet</h3>
              <p className="text-gray-500">Create your first AI chatbot!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {chatbots.map(bot => (
                <div key={bot.id} className="border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-bold text-gray-800">{bot.name}</h4>
                    <div className="flex space-x-2">
                      <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        {bot.llm_provider}
                      </span>
                      <button
                        onClick={() => confirmDelete('chatbot', bot.id, bot.name)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title={t('delete')}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <p><strong>Model:</strong> {bot.model_name}</p>
                    <p><strong>Temperature:</strong> {bot.temperature}</p>
                    {bot.knowledge_base_ids && bot.knowledge_base_ids.length > 0 && (
                      <p><strong>Knowledge:</strong> {bot.knowledge_base_ids.length} documents</p>
                    )}
                  </div>
                  
                  <button
                    onClick={() => {
                      setSelectedChatbot(bot);
                      setShowTestChatModal(true);
                    }}
                    className="w-full py-2 px-4 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors duration-200"
                  >
                    {t('testChat')}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Enhanced Knowledge Base View with delete functionality
  const KnowledgeBase = () => {
    const [isUploading, setIsUploading] = useState(false);

    const handleFileUpload = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      
      setIsUploading(true);
      
      try {
        const formData = new FormData();
        files.forEach(file => {
          formData.append('files', file);
        });
        formData.append('name', 'Uploaded Documents');
        
        await axios.post(`${API}/knowledge-base`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        await loadData();
      } catch (error) {
        console.error('Error uploading files:', error);
      } finally {
        setIsUploading(false);
      }
    };

    return (
      <div className="p-8 bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 min-h-screen">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent mb-8">
            {t('knowledgeBase')}
          </h2>
          
          <div className="bg-white rounded-3xl shadow-xl p-8 mb-8">
            <div className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">{t('uploadDocuments')}</h3>
              <p className="text-gray-500 mb-4">Upload PDF, TXT files or provide URLs</p>
              
              <input
                type="file"
                multiple
                accept=".pdf,.txt,.docx"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className={`inline-block py-3 px-6 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-2xl hover:from-indigo-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 cursor-pointer ${
                  isUploading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isUploading ? t('uploading') : t('uploadDocuments')}
              </label>
            </div>
          </div>
          
          <div className="bg-white rounded-3xl shadow-xl p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">{t('uploadedDocuments')}</h3>
            
            {knowledgeBase.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📚</div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">No documents uploaded</h3>
                <p className="text-gray-500">Upload your first document to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {knowledgeBase.map(item => (
                  <div key={item.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-2xl hover:bg-gray-50">
                    <div>
                      <h4 className="font-semibold text-gray-800">{item.name}</h4>
                      <p className="text-sm text-gray-500">{item.file_type.toUpperCase()}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        {t('ready')}
                      </span>
                      <button
                        onClick={() => confirmDelete('knowledge', item.id, item.name)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title={t('delete')}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Enhanced Voicebot Modal
  const VoicebotModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      voice_model_id: '',
      llm_provider: 'openai',
      model_name: 'gpt-3.5-turbo',
      temperature: 0.7,
      system_prompt: 'Ets un assistent de veu que parla català. Respon sempre en català de manera útil i amigable.',
      api_key: '',
      knowledge_base_ids: []
    });
    const [isCreating, setIsCreating] = useState(false);
    const [showKnowledgeSelection, setShowKnowledgeSelection] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      setIsCreating(true);
      
      try {
        await axios.post(`${API}/voicebots`, formData);
        await loadData();
        setShowVoicebotModal(false);
        setFormData({
          name: '',
          voice_model_id: '',
          llm_provider: 'openai',
          model_name: 'gpt-3.5-turbo',
          temperature: 0.7,
          system_prompt: 'Ets un assistent de veu que parla català. Respon sempre en català de manera útil i amigable.',
          api_key: '',
          knowledge_base_ids: []
        });
      } catch (error) {
        console.error('Error creating voicebot:', error);
      } finally {
        setIsCreating(false);
      }
    };

    return (
      <>
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-3xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                {t('createNewVoicebot')}
              </h2>
              <button
                onClick={() => setShowVoicebotModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('voicebotName')}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('selectVoiceModel')}
                </label>
                <div className="space-y-3">
                  <button
                    type="button"
                    onClick={() => openVoiceSelection((voice) => setFormData({...formData, voice_model_id: voice.id}), formData.voice_model_id)}
                    className="w-full p-4 border border-gray-300 rounded-xl hover:bg-gray-50 focus:ring-2 focus:ring-purple-500 focus:border-transparent text-left transition-colors"
                  >
                    {formData.voice_model_id ? (
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">
                            {voices.find(v => v.id === formData.voice_model_id)?.name || 'Selected Voice'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {voices.find(v => v.id === formData.voice_model_id)?.language?.toUpperCase()} - {voices.find(v => v.id === formData.voice_model_id)?.dialect}
                          </div>
                        </div>
                        <div className="text-purple-500">✓</div>
                      </div>
                    ) : (
                      <div className="text-gray-500">
                        Choose a voice model for your voicebot...
                      </div>
                    )}
                  </button>
                  
                  {voices.filter(v => v.status === 'ready').length === 0 && (
                    <div className="text-center py-4 bg-yellow-50 border border-yellow-200 rounded-xl">
                      <div className="text-yellow-600 mb-2">⚠️ No trained voices available</div>
                      <button
                        type="button"
                        onClick={() => {
                          setShowVoicebotModal(false);
                          setCurrentView('training-advanced');
                        }}
                        className="text-purple-600 hover:text-purple-700 underline text-sm"
                      >
                        Train your first voice model
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('llmProvider')}
                  </label>
                  <select
                    value={formData.llm_provider}
                    onChange={(e) => setFormData({...formData, llm_provider: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="claude">Claude</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('modelName')}
                  </label>
                  <select
                    value={formData.model_name}
                    onChange={(e) => setFormData({...formData, model_name: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {formData.llm_provider === 'openai' && (
                      <>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                      </>
                    )}
                    {formData.llm_provider === 'claude' && (
                      <>
                        <option value="claude-3-haiku">Claude 3 Haiku</option>
                        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="claude-3-opus">Claude 3 Opus</option>
                      </>
                    )}
                    {formData.llm_provider === 'gemini' && (
                      <>
                        <option value="gemini-pro">Gemini Pro</option>
                        <option value="gemini-pro-vision">Gemini Pro Vision</option>
                      </>
                    )}
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('temperature')} ({formData.temperature})
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData({...formData, temperature: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('systemPrompt')}
                </label>
                <textarea
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({...formData, system_prompt: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent h-24"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('apiKey')} (Optional - uses global key if empty)
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({...formData, api_key: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Leave empty to use global API key"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('knowledgeBaseSources')}
                </label>
                <button
                  type="button"
                  onClick={() => setShowKnowledgeSelection(true)}
                  className="w-full p-3 border border-gray-300 rounded-xl text-left hover:bg-gray-50 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {formData.knowledge_base_ids.length > 0 
                    ? `${formData.knowledge_base_ids.length} ${t('knowledgeSelected')}`
                    : t('selectKnowledgeSources')
                  }
                </button>
              </div>
              
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setShowVoicebotModal(false)}
                  className="flex-1 py-3 px-6 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors duration-200"
                >
                  {t('cancel')}
                </button>
                <button
                  type="submit"
                  disabled={isCreating}
                  className="flex-1 py-3 px-6 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50"
                >
                  {isCreating ? t('creating') : t('createVoicebotBtn')}
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <KnowledgeSelectionModal
          isOpen={showKnowledgeSelection}
          onClose={() => setShowKnowledgeSelection(false)}
          onSelect={(ids) => setFormData({...formData, knowledge_base_ids: ids})}
          selectedIds={formData.knowledge_base_ids}
        />
      </>
    );
  };

  // Voice Test Modal for Voicebots
  const VoiceTestModal = ({ bot, onClose }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [currentAudio, setCurrentAudio] = useState(null);

    const sendMessage = async () => {
      if (!inputMessage.trim()) return;
      
      const userMessage = { role: 'user', content: inputMessage };
      setMessages(prev => [...prev, userMessage]);
      setIsSending(true);
      
      try {
        const response = await axios.post(`${API}/voicebots/chat`, {
          message: inputMessage,
          bot_id: bot.id,
          conversation_history: messages
        });
        
        const botMessage = { 
          role: 'assistant', 
          content: response.data.reply,
          audio_url: response.data.audio_url,
          audio_id: response.data.audio_id
        };
        setMessages(prev => [...prev, botMessage]);
        
        // Auto-play the voice response
        if (response.data.audio_url) {
          const audio = new Audio(`${BACKEND_URL}${response.data.audio_url}`);
          setCurrentAudio(audio);
          audio.play();
        }
        
      } catch (error) {
        console.error('Error sending voice message:', error);
        const errorMessage = { 
          role: 'assistant', 
          content: 'Error: Unable to get voice response. Please check voicebot configuration.' 
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsSending(false);
        setInputMessage('');
      }
    };

    const playAudio = (audioUrl) => {
      if (currentAudio) {
        currentAudio.pause();
      }
      const audio = new Audio(`${BACKEND_URL}${audioUrl}`);
      setCurrentAudio(audio);
      audio.play();
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-3xl p-6 max-w-2xl w-full mx-4 h-[600px] flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-800">🎤 Voice Test: {bot.name}</h3>
              <p className="text-sm text-gray-500">Voice Model: {bot.voice_model_id}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 border border-gray-200 rounded-xl">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-purple-500 text-white' 
                    : msg.content.includes('Error:') 
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                }`}>
                  <div>{msg.content}</div>
                  {msg.audio_url && (
                    <button
                      onClick={() => playAudio(msg.audio_url)}
                      className="mt-2 flex items-center space-x-2 text-blue-600 hover:text-blue-800"
                    >
                      <span>🔊</span>
                      <span className="text-sm">Play Voice</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isSending && sendMessage()}
              className="flex-1 p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Escriu el teu missatge per rebre resposta de veu..."
              disabled={isSending}
            />
            <button
              onClick={sendMessage}
              disabled={isSending || !inputMessage.trim()}
              className="py-3 px-6 bg-purple-500 text-white rounded-xl hover:bg-purple-600 disabled:opacity-50"
            >
              🎤 {t('send')}
            </button>
          </div>
        </div>
      </div>
    );
  };
  const Voicebots = () => (
    <div className="p-8 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            {t('voicebots')}
          </h2>
          <button
            onClick={() => setShowVoicebotModal(true)}
            className="py-3 px-6 bg-gradient-to-r from-purple-500 to-blue-600 text-white rounded-2xl hover:from-purple-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            {t('createNewVoicebot')}
          </button>
        </div>
        
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">{t('yourVoicebots')}</h3>
          
          {voicebots.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No voicebots created yet</h3>
              <p className="text-gray-500">Create your first voice assistant!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {voicebots.map(bot => (
                <div key={bot.id} className="border border-gray-200 rounded-2xl p-6 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-bold text-gray-800">{bot.name}</h4>
                    <div className="flex space-x-2">
                      <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                        {bot.voice_model}
                      </span>
                      <button
                        onClick={() => confirmDelete('voicebot', bot.id, bot.name)}
                        className="text-red-500 hover:text-red-700 p-1"
                        title={t('delete')}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <p><strong>Voice:</strong> {bot.voice_model}</p>
                    <p><strong>LLM:</strong> {bot.llm_provider}</p>
                    {bot.knowledge_base_ids && bot.knowledge_base_ids.length > 0 && (
                      <p><strong>Knowledge:</strong> {bot.knowledge_base_ids.length} documents</p>
                    )}
                  </div>
                  
                  <button
                    onClick={() => {
                      setSelectedVoicebot(bot);
                      setShowTestVoiceModal(true);
                    }}
                    className="w-full py-2 px-4 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-colors duration-200"
                  >
                    {t('testVoiceChat')}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Render current view
  const renderView = () => {
    switch(currentView) {
      case 'dashboard': return <Dashboard />;
      case 'voices': return <VoiceTraining />;
      case 'synthesis': return <SpeechSynthesis />;
      case 'training': return <VoiceTraining />;
      case 'training-advanced': return <VoiceTrainingAdvanced />;
      case 'chatbots': return <Chatbots />;
      case 'voicebots': return <Voicebots />;
      case 'knowledge': return <KnowledgeBase />;
  const CallCenterView = () => {
    const [callCenters, setCallCenters] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      loadCallCenters();
    }, []);

    const loadCallCenters = async () => {
      try {
        const response = await axios.get(`${API}/call-center/`);
        setCallCenters(response.data.call_centers || []);
      } catch (error) {
        console.error('Error loading call centers:', error);
      } finally {
        setLoading(false);
      }
    };

    const handleCreateCenter = () => {
      setShowCallCenterCreation(true);
    };

    if (loading) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        </div>
      );
    }

    // Show landing page if no call centers exist
    if (callCenters.length === 0) {
      return <CallCenterLanding onCreateCenter={handleCreateCenter} />;
    }

    // Show dashboard if call centers exist
    return <CallCenterDashboard />;
  };
      case 'developer': return <DeveloperDashboard />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Navigation />
      <div className="flex-1">
        {renderView()}
      </div>
      
      {/* Modals */}
      {showVoiceTrainingModal && <VoiceTrainingModal />}
      {showChatbotModal && <ChatbotModal />}
      {showVoicebotModal && <VoicebotModal />}
      {showTestChatModal && selectedChatbot && (
        <ChatTestModal 
          bot={selectedChatbot} 
          onClose={() => {
            setShowTestChatModal(false);
            setSelectedChatbot(null);
          }} 
        />
      )}
      {showTestVoiceModal && selectedVoicebot && (
        <VoiceTestModal 
          bot={selectedVoicebot} 
          onClose={() => {
            setShowTestVoiceModal(false);
            setSelectedVoicebot(null);
          }} 
        />
      )}
      {showVoiceSelectionModal && (
        <VoiceSelectionModal
          isOpen={showVoiceSelectionModal}
          onClose={() => setShowVoiceSelectionModal(false)}
          onSelect={handleVoiceSelection}
          selectedVoiceId={selectedVoice?.id}
        />
      )}
      <DeleteModal />
    </div>
  );
}

export default App;
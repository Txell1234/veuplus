/**
 * VeuPlus ConvHi Widget - Widget JavaScript per integració web
 * Versió: 2.1.0
 * Compatible amb: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
 */

(function() {
  'use strict';

  // Configuració per defecte
  const DEFAULT_CONFIG = {
    variant: 'compact',
    mode: 'voice_only',
    primary_color: '#3B82F6',
    secondary_color: '#1E40AF',
    avatar_orb_color_1: '#6DB035',
    avatar_orb_color_2: '#F5CABB',
    action_text: 'Need assistance?',
    start_call_text: 'Begin conversation',
    end_call_text: 'End call',
    expand_text: 'Open chat',
    listening_text: 'Listening...',
    speaking_text: 'Assistant speaking',
    feedback_enabled: true,
    terms_enabled: false,
    mute_enabled: true,
    language: 'ca'
  };

  // Classe principal del widget
  class ConvHiWidget {
    constructor(element) {
      this.element = element;
      this.config = this.parseConfig();
      this.isOpen = false;
      this.isCalling = false;
      this.isListening = false;
      this.isSpeaking = false;
      this.audioContext = null;
      this.mediaRecorder = null;
      this.audioChunks = [];
      this.sessionId = this.generateSessionId();
      
      this.init();
    }

    parseConfig() {
      const config = { ...DEFAULT_CONFIG };
      
      // Parsejar atributs del custom element
      const attrs = this.element.attributes;
      for (let i = 0; i < attrs.length; i++) {
        const attr = attrs[i];
        const key = attr.name.replace(/-/g, '_');
        let value = attr.value;
        
        // Convertir valors booleans
        if (value === 'true') value = true;
        else if (value === 'false') value = false;
        
        // Parsejar JSON per variables dinàmiques
        if (key === 'dynamic_variables' && value) {
          try {
            value = JSON.parse(value);
          } catch (e) {
            console.warn('Error parsing dynamic_variables:', e);
            value = {};
          }
        }
        
        config[key] = value;
      }
      
      return config;
    }

    generateSessionId() {
      return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
      this.createWidget();
      this.bindEvents();
      this.loadStyles();
    }

    createWidget() {
      // Crear contenidor principal
      this.widgetContainer = document.createElement('div');
      this.widgetContainer.className = 'veuplus-convhi-widget';
      this.widgetContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
        color: #333;
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
      `;

      // Crear botó principal
      this.createMainButton();
      
      // Crear panell de conversa
      this.createChatPanel();
      
      // Afegir al DOM
      document.body.appendChild(this.widgetContainer);
    }

    createMainButton() {
      this.mainButton = document.createElement('button');
      this.mainButton.className = 'veuplus-main-button';
      this.mainButton.style.cssText = `
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(45deg, ${this.config.avatar_orb_color_1}, ${this.config.avatar_orb_color_2});
        color: white;
        position: relative;
        overflow: hidden;
      `;

      this.mainButton.innerHTML = '🤖';
      
      // Afegir text d'acció
      this.actionText = document.createElement('div');
      this.actionText.className = 'veuplus-action-text';
      this.actionText.textContent = this.config.action_text;
      this.actionText.style.cssText = `
        position: absolute;
        right: 70px;
        top: 50%;
        transform: translateY(-50%);
        background: white;
        padding: 8px 12px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        border: 1px solid #e5e7eb;
      `;

      this.mainButton.appendChild(this.actionText);
      this.widgetContainer.appendChild(this.mainButton);
    }

    createChatPanel() {
      this.chatPanel = document.createElement('div');
      this.chatPanel.className = 'veuplus-chat-panel';
      this.chatPanel.style.cssText = `
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        border: 1px solid #e5e7eb;
        display: none;
        flex-direction: column;
        overflow: hidden;
      `;

      // Header del panell
      this.createChatHeader();
      
      // Àrea de conversa
      this.createChatArea();
      
      // Controls
      this.createChatControls();
      
      this.widgetContainer.appendChild(this.chatPanel);
    }

    createChatHeader() {
      const header = document.createElement('div');
      header.style.cssText = `
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: ${this.config.primary_color};
        color: white;
      `;

      const title = document.createElement('div');
      title.textContent = 'ConvHi Assistant';
      title.style.cssText = `
        font-weight: 600;
        font-size: 16px;
      `;

      const closeBtn = document.createElement('button');
      closeBtn.innerHTML = '×';
      closeBtn.style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
      `;

      header.appendChild(title);
      header.appendChild(closeBtn);
      this.chatPanel.appendChild(header);

      // Bind close event
      closeBtn.addEventListener('click', () => this.closeChat());
    }

    createChatArea() {
      this.chatArea = document.createElement('div');
      this.chatArea.className = 'veuplus-chat-area';
      this.chatArea.style.cssText = `
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        background: #f9fafb;
      `;

      // Missatge de benvinguda
      const welcomeMsg = document.createElement('div');
      welcomeMsg.className = 'veuplus-welcome-message';
      welcomeMsg.innerHTML = `
        <div style="
          background: white;
          padding: 12px 16px;
          border-radius: 12px;
          border: 1px solid #e5e7eb;
          margin-bottom: 12px;
        ">
          <div style="font-weight: 500; margin-bottom: 4px;">👋 Hola!</div>
          <div style="font-size: 13px; color: #6b7280;">
            Sóc el teu assistent ConvHi. Com et puc ajudar avui?
          </div>
        </div>
      `;

      this.chatArea.appendChild(welcomeMsg);
      this.chatPanel.appendChild(this.chatArea);
    }

    createChatControls() {
      const controls = document.createElement('div');
      controls.style.cssText = `
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        background: white;
        display: flex;
        align-items: center;
        gap: 8px;
      `;

      // Input de text
      this.textInput = document.createElement('input');
      this.textInput.type = 'text';
      this.textInput.placeholder = 'Escriu un missatge...';
      this.textInput.style.cssText = `
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s ease;
      `;

      // Botó de micròfon
      this.micButton = document.createElement('button');
      this.micButton.innerHTML = '🎤';
      this.micButton.style.cssText = `
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: none;
        background: ${this.config.primary_color};
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        transition: all 0.2s ease;
      `;

      // Botó d'enviar
      this.sendButton = document.createElement('button');
      this.sendButton.innerHTML = '➤';
      this.sendButton.style.cssText = `
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: none;
        background: ${this.config.secondary_color};
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        transition: all 0.2s ease;
      `;

      controls.appendChild(this.textInput);
      controls.appendChild(this.micButton);
      controls.appendChild(this.sendButton);
      this.chatPanel.appendChild(controls);

      // Bind events
      this.sendButton.addEventListener('click', () => this.sendMessage());
      this.textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.sendMessage();
      });
      this.micButton.addEventListener('click', () => this.toggleRecording());
    }

    bindEvents() {
      // Hover effects
      this.mainButton.addEventListener('mouseenter', () => {
        this.actionText.style.opacity = '1';
        this.mainButton.style.transform = 'scale(1.05)';
      });

      this.mainButton.addEventListener('mouseleave', () => {
        this.actionText.style.opacity = '0';
        this.mainButton.style.transform = 'scale(1)';
      });

      // Click events
      this.mainButton.addEventListener('click', () => this.toggleChat());
    }

    toggleChat() {
      this.isOpen = !this.isOpen;
      
      if (this.isOpen) {
        this.chatPanel.style.display = 'flex';
        this.mainButton.style.transform = 'scale(0.9)';
        this.mainButton.innerHTML = '✕';
        this.textInput.focus();
      } else {
        this.chatPanel.style.display = 'none';
        this.mainButton.style.transform = 'scale(1)';
        this.mainButton.innerHTML = '🤖';
      }
    }

    closeChat() {
      this.isOpen = false;
      this.chatPanel.style.display = 'none';
      this.mainButton.style.transform = 'scale(1)';
      this.mainButton.innerHTML = '🤖';
    }

    async sendMessage() {
      const message = this.textInput.value.trim();
      if (!message) return;

      // Afegir missatge de l'usuari
      this.addMessage(message, 'user');
      this.textInput.value = '';

      // Mostrar indicador de càrrega
      this.showTypingIndicator();

      try {
        // Enviar missatge al backend
        const response = await this.callAPI('/api/convhi/agents/' + this.config.agent_id + '/chat', {
          agent_id: this.config.agent_id,
          message: message,
          message_type: 'text',
          session_id: this.sessionId,
          dynamic_variables: this.config.dynamic_variables || {},
          overrides: this.config.overrides || {}
        });

        // Ocultar indicador de càrrega
        this.hideTypingIndicator();

        // Afegir resposta de l'assistent
        const assistantMessage = response.response || response.text || 'Ho sento, no he pogut processar el teu missatge.';
        this.addMessage(assistantMessage, 'assistant');

        // Reproduir àudio si està disponible
        if (response.audio_base64) {
          this.playAudio(response.audio_base64, response.mime_type || 'audio/wav');
        }

      } catch (error) {
        console.error('Error sending message:', error);
        this.hideTypingIndicator();
        this.addMessage('Ho sento, hi ha hagut un error. Torna-ho a provar.', 'assistant');
      }
    }

    addMessage(content, sender) {
      const messageDiv = document.createElement('div');
      messageDiv.style.cssText = `
        margin-bottom: 12px;
        display: flex;
        ${sender === 'user' ? 'justify-content: flex-end;' : 'justify-content: flex-start;'}
      `;

      const messageContent = document.createElement('div');
      messageContent.style.cssText = `
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
        ${sender === 'user' 
          ? `background: ${this.config.primary_color}; color: white; border-bottom-right-radius: 4px;`
          : `background: white; color: #333; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px;`
        }
      `;

      messageContent.textContent = content;
      messageDiv.appendChild(messageContent);
      this.chatArea.appendChild(messageDiv);

      // Scroll to bottom
      this.chatArea.scrollTop = this.chatArea.scrollHeight;
    }

    showTypingIndicator() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'veuplus-typing-indicator';
      typingDiv.style.cssText = `
        margin-bottom: 12px;
        display: flex;
        justify-content: flex-start;
      `;

      const typingContent = document.createElement('div');
      typingContent.style.cssText = `
        background: white;
        border: 1px solid #e5e7eb;
        padding: 12px 16px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        font-size: 14px;
        color: #6b7280;
      `;

      typingContent.innerHTML = `
        <div style="display: flex; align-items: center; gap: 4px;">
          <span>L'assistent està escrivint</span>
          <div style="display: flex; gap: 2px;">
            <div style="width: 4px; height: 4px; background: #6b7280; border-radius: 50%; animation: typing 1.4s infinite;"></div>
            <div style="width: 4px; height: 4px; background: #6b7280; border-radius: 50%; animation: typing 1.4s infinite 0.2s;"></div>
            <div style="width: 4px; height: 4px; background: #6b7280; border-radius: 50%; animation: typing 1.4s infinite 0.4s;"></div>
          </div>
        </div>
      `;

      typingDiv.appendChild(typingContent);
      this.chatArea.appendChild(typingDiv);
      this.chatArea.scrollTop = this.chatArea.scrollHeight;
    }

    hideTypingIndicator() {
      const typingIndicator = this.chatArea.querySelector('.veuplus-typing-indicator');
      if (typingIndicator) {
        typingIndicator.remove();
      }
    }

    async toggleRecording() {
      if (this.isListening) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    }

    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          this.sendAudioMessage(audioBlob);
        };

        this.mediaRecorder.start();
        this.isListening = true;
        this.micButton.style.background = '#ef4444';
        this.micButton.innerHTML = '⏹';

      } catch (error) {
        console.error('Error starting recording:', error);
        this.addMessage('No s\'ha pogut accedir al micròfon. Verifica els permisos.', 'assistant');
      }
    }

    stopRecording() {
      if (this.mediaRecorder && this.isListening) {
        this.mediaRecorder.stop();
        this.isListening = false;
        this.micButton.style.background = this.config.primary_color;
        this.micButton.innerHTML = '🎤';
      }
    }

    async sendAudioMessage(audioBlob) {
      // Mostrar indicador de processament
      this.showTypingIndicator();

      try {
        // Convertir a base64
        const base64 = await this.blobToBase64(audioBlob);

        // Enviar al backend
        const response = await this.callAPI('/api/convhi/agents/' + this.config.agent_id + '/chat', {
          agent_id: this.config.agent_id,
          message: base64,
          message_type: 'audio',
          session_id: this.sessionId,
          dynamic_variables: this.config.dynamic_variables || {},
          overrides: this.config.overrides || {}
        });

        this.hideTypingIndicator();

        const assistantMessage = response.response || response.text || 'Ho sento, no he pogut entendre l\'àudio.';
        this.addMessage(assistantMessage, 'assistant');

        if (response.audio_base64) {
          this.playAudio(response.audio_base64, response.mime_type || 'audio/wav');
        }

      } catch (error) {
        console.error('Error sending audio:', error);
        this.hideTypingIndicator();
        this.addMessage('Ho sento, hi ha hagut un error processant l\'àudio.', 'assistant');
      }
    }

    blobToBase64(blob) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    }

    playAudio(base64, mimeType) {
      const audio = new Audio(`data:${mimeType};base64,${base64}`);
      audio.play().catch(error => {
        console.error('Error playing audio:', error);
      });
    }

    async callAPI(endpoint, data) {
      const backendUrl = this.element.dataset.backendUrl || 'http://localhost:8080';
      const url = backendUrl + endpoint;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    }

    loadStyles() {
      // Afegir estils CSS al document
      const style = document.createElement('style');
      style.textContent = `
        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-10px); }
        }

        .veuplus-convhi-widget * {
          box-sizing: border-box;
        }

        .veuplus-convhi-widget button:hover {
          opacity: 0.9;
        }

        .veuplus-convhi-widget button:active {
          transform: scale(0.95);
        }

        .veuplus-chat-area::-webkit-scrollbar {
          width: 6px;
        }

        .veuplus-chat-area::-webkit-scrollbar-track {
          background: #f1f1f1;
        }

        .veuplus-chat-area::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 3px;
        }

        .veuplus-chat-area::-webkit-scrollbar-thumb:hover {
          background: #a8a8a8;
        }

        @media (max-width: 480px) {
          .veuplus-chat-panel {
            width: calc(100vw - 40px) !important;
            right: 20px !important;
            left: 20px !important;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  // Registrar el custom element
  if (!customElements.get('veuplus-convhi')) {
    customElements.define('veuplus-convhi', class extends HTMLElement {
      connectedCallback() {
        this.widget = new ConvHiWidget(this);
      }

      disconnectedCallback() {
        if (this.widget && this.widget.widgetContainer) {
          this.widget.widgetContainer.remove();
        }
      }
    });
  }

  // Auto-inicialitzar widgets existents
  document.addEventListener('DOMContentLoaded', () => {
    const widgets = document.querySelectorAll('veuplus-convhi');
    widgets.forEach(widget => {
      if (!widget.widget) {
        widget.widget = new ConvHiWidget(widget);
      }
    });
  });

})();
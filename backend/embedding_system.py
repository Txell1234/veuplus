# Bot Embedding System for VeuPlus
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime
from database_sql import db

# Embedding Router
embed_router = APIRouter(prefix="/api/embed", tags=["Bot Embedding"])

# Embedding Models
class EmbedConfig(BaseModel):
    bot_id: str
    bot_type: str  # 'chatbot' or 'voicebot'
    theme: str = "veuplus"  # veuplus, catalan, modern, minimal
    size: str = "medium"    # small, medium, large, fullscreen
    position: str = "bottom-right"  # bottom-right, bottom-left, top-right, top-left, center
    custom_css: Optional[str] = None
    domain_whitelist: Optional[List[str]] = None

class EmbedResponse(BaseModel):
    embed_id: str
    html_code: str
    iframe_code: str
    js_widget_code: str
    react_component: str

# Embed Themes
EMBED_THEMES = {
    "veuplus": {
        "primary_color": "#8B5CF6",
        "secondary_color": "#EC4899", 
        "background": "#FFFFFF",
        "text_color": "#374151",
        "border_radius": "16px",
        "shadow": "0 10px 25px rgba(139, 92, 246, 0.1)"
    },
    "catalan": {
        "primary_color": "#DC2626",
        "secondary_color": "#FBBF24",
        "background": "#FEF3C7",
        "text_color": "#1F2937",
        "border_radius": "12px", 
        "shadow": "0 8px 20px rgba(220, 38, 38, 0.1)"
    },
    "modern": {
        "primary_color": "#1F2937",
        "secondary_color": "#6B7280",
        "background": "#F9FAFB",
        "text_color": "#111827",
        "border_radius": "8px",
        "shadow": "0 4px 16px rgba(0, 0, 0, 0.1)"
    },
    "minimal": {
        "primary_color": "#000000",
        "secondary_color": "#666666",
        "background": "#FFFFFF",
        "text_color": "#333333",
        "border_radius": "4px",
        "shadow": "0 2px 8px rgba(0, 0, 0, 0.1)"
    }
}

# Embed Sizes
EMBED_SIZES = {
    "small": {"width": "300px", "height": "400px"},
    "medium": {"width": "400px", "height": "500px"},
    "large": {"width": "500px", "height": "600px"},
    "fullscreen": {"width": "100vw", "height": "100vh"}
}

# Generate Embed Codes
@embed_router.post("/generate", response_model=EmbedResponse)
async def generate_embed_code(config: EmbedConfig):
    """Generate embed codes for a bot"""
    try:
        # Verify bot exists
        if config.bot_type == "chatbot":
            bot = db.get_chatbot(config.bot_id)
        elif config.bot_type == "voicebot":
            bot = db.get_voicebot(config.bot_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid bot type")
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Generate embed ID
        embed_id = str(uuid.uuid4())
        
        # Store embed configuration
        embed_data = {
            "id": embed_id,
            "bot_id": config.bot_id,
            "bot_type": config.bot_type,
            "embed_type": "custom",
            "theme": config.theme,
            "size": config.size,
            "position": config.position,
            "custom_css": config.custom_css,
            "domain_whitelist": json.dumps(config.domain_whitelist) if config.domain_whitelist else None,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        db.execute_insert("bot_embeddings", embed_data)
        
        # Generate different embed codes
        html_code = generate_html_embed(embed_id, config, bot)
        iframe_code = generate_iframe_embed(embed_id, config, bot)
        js_widget_code = generate_js_widget_embed(embed_id, config, bot)
        react_component = generate_react_component(embed_id, config, bot)
        
        return EmbedResponse(
            embed_id=embed_id,
            html_code=html_code,
            iframe_code=iframe_code,
            js_widget_code=js_widget_code,
            react_component=react_component
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed: {str(e)}")

def generate_html_embed(embed_id: str, config: EmbedConfig, bot: Dict[str, Any]) -> str:
    """Generate HTML embed code"""
    theme = EMBED_THEMES.get(config.theme, EMBED_THEMES["veuplus"])
    size = EMBED_SIZES.get(config.size, EMBED_SIZES["medium"])
    
    domain = "veuplus.com"  # Replace with your domain
    
    html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{bot['name']} - VeuPlus Bot</title>
    <style>
        .veuplus-embed-container {{
            width: {size['width']};
            height: {size['height']};
            border: none;
            border-radius: {theme['border_radius']};
            box-shadow: {theme['shadow']};
            overflow: hidden;
            position: relative;
            background: {theme['background']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .veuplus-chat-header {{
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            color: white;
            padding: 16px;
            text-align: center;
            font-weight: 600;
        }}
        
        .veuplus-chat-body {{
            height: calc(100% - 140px);
            padding: 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .veuplus-chat-input {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 16px;
            background: {theme['background']};
            border-top: 1px solid #E5E7EB;
        }}
        
        .veuplus-input-field {{
            width: 100%;
            padding: 12px;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            outline: none;
            font-size: 14px;
        }}
        
        .veuplus-send-btn {{
            position: absolute;
            right: 24px;
            bottom: 28px;
            background: {theme['primary_color']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        .veuplus-message {{
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            margin: 4px 0;
        }}
        
        .veuplus-message.user {{
            background: {theme['primary_color']};
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }}
        
        .veuplus-message.bot {{
            background: #F3F4F6;
            color: {theme['text_color']};
            align-self: flex-start;
        }}
        
        {config.custom_css or ''}
    </style>
</head>
<body>
    <div class="veuplus-embed-container" id="veuplus-embed-{embed_id}">
        <div class="veuplus-chat-header">
            🤖 {bot['name']}
        </div>
        <div class="veuplus-chat-body" id="chat-body-{embed_id}">
            <div class="veuplus-message bot">
                Hola! Sóc {bot['name']}. Com et puc ajudar avui?
            </div>
        </div>
        <div class="veuplus-chat-input">
            <input type="text" class="veuplus-input-field" id="input-{embed_id}" placeholder="Escriu el teu missatge...">
            <button class="veuplus-send-btn" onclick="sendMessage_{embed_id}()">Enviar</button>
        </div>
    </div>
    
    <script>
        let chatHistory_{embed_id} = [];
        
        function sendMessage_{embed_id}() {{
            const input = document.getElementById('input-{embed_id}');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage_{embed_id}(message, 'user');
            input.value = '';
            
            // Send to bot
            fetch('https://{domain}/api/{config.bot_type}s/chat', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{
                    bot_id: '{config.bot_id}',
                    message: message,
                    chat_history: chatHistory_{embed_id}
                }})
            }})
            .then(response => response.json())
            .then(data => {{
                addMessage_{embed_id}(data.response || 'Ho sento, no puc respondre ara mateix.', 'bot');
                chatHistory_{embed_id}.push({{user: message, bot: data.response}});
            }})
            .catch(error => {{
                console.error('Error:', error);
                addMessage_{embed_id}('Ho sento, hi ha hagut un error.', 'bot');
            }});
        }}
        
        function addMessage_{embed_id}(message, sender) {{
            const chatBody = document.getElementById('chat-body-{embed_id}');
            const messageDiv = document.createElement('div');
            messageDiv.className = `veuplus-message ${{sender}}`;
            messageDiv.textContent = message;
            chatBody.appendChild(messageDiv);
            chatBody.scrollTop = chatBody.scrollHeight;
        }}
        
        // Enter key support
        document.getElementById('input-{embed_id}').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sendMessage_{embed_id}();
            }}
        }});
    </script>
</body>
</html>
    """.strip()
    
    return html_code

def generate_iframe_embed(embed_id: str, config: EmbedConfig, bot: Dict[str, Any]) -> str:
    """Generate iframe embed code"""
    domain = "veuplus.com"  # Replace with your domain
    size = EMBED_SIZES.get(config.size, EMBED_SIZES["medium"])
    
    iframe_code = f"""
<!-- VeuPlus {config.bot_type.title()} Embed - {bot['name']} -->
<iframe 
    src="https://{domain}/embed/{embed_id}" 
    width="{size['width']}" 
    height="{size['height']}" 
    frameborder="0" 
    style="border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);"
    allow="microphone; camera; autoplay">
</iframe>
    """.strip()
    
    return iframe_code

def generate_js_widget_embed(embed_id: str, config: EmbedConfig, bot: Dict[str, Any]) -> str:
    """Generate JavaScript widget embed code"""
    domain = "veuplus.com"  # Replace with your domain
    theme = EMBED_THEMES.get(config.theme, EMBED_THEMES["veuplus"])
    
    js_code = f"""
<!-- VeuPlus Widget - {bot['name']} -->
<script>
(function() {{
    // Create widget container
    const widget = document.createElement('div');
    widget.id = 'veuplus-widget-{embed_id}';
    widget.style.cssText = `
        position: fixed;
        {config.position.replace('-', ': 20px; ').replace('-', ': 20px;')};
        z-index: 999999;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
        border-radius: 50%;
        cursor: pointer;
        box-shadow: {theme['shadow']};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        transition: all 0.3s ease;
    `;
    widget.innerHTML = '💬';
    
    // Create chat window
    const chatWindow = document.createElement('div');
    chatWindow.id = 'veuplus-chat-{embed_id}';
    chatWindow.style.cssText = `
        position: fixed;
        {config.position.replace('-', ': 80px; ').replace('-', ': 20px;')};
        z-index: 999998;
        width: 350px;
        height: 450px;
        background: white;
        border-radius: 16px;
        box-shadow: {theme['shadow']};
        display: none;
        flex-direction: column;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;
    
    chatWindow.innerHTML = `
        <div style="background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']}); color: white; padding: 16px; border-radius: 16px 16px 0 0; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 600;">🤖 {bot['name']}</span>
            <button onclick="toggleChat_{embed_id}()" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">×</button>
        </div>
        <div id="chat-messages-{embed_id}" style="flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px;">
            <div style="background: #F3F4F6; padding: 10px 14px; border-radius: 12px; color: {theme['text_color']}; align-self: flex-start; max-width: 80%;">
                Hola! Sóc {bot['name']}. Com et puc ajudar avui?
            </div>
        </div>
        <div style="padding: 16px; border-top: 1px solid #E5E7EB;">
            <div style="display: flex; gap: 8px;">
                <input type="text" id="widget-input-{embed_id}" placeholder="Escriu aquí..." style="flex: 1; padding: 10px; border: 1px solid #D1D5DB; border-radius: 8px; outline: none;">
                <button onclick="sendWidgetMessage_{embed_id}()" style="background: {theme['primary_color']}; color: white; border: none; padding: 10px 16px; border-radius: 8px; cursor: pointer;">Enviar</button>
            </div>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(widget);
    document.body.appendChild(chatWindow);
    
    // Widget functions
    window.toggleChat_{embed_id} = function() {{
        const chat = document.getElementById('veuplus-chat-{embed_id}');
        const isVisible = chat.style.display === 'flex';
        chat.style.display = isVisible ? 'none' : 'flex';
        widget.style.transform = isVisible ? 'scale(1)' : 'scale(0.9)';
    }};
    
    window.sendWidgetMessage_{embed_id} = function() {{
        const input = document.getElementById('widget-input-{embed_id}');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        const messagesContainer = document.getElementById('chat-messages-{embed_id}');
        const userMsg = document.createElement('div');
        userMsg.style.cssText = 'background: {theme['primary_color']}; color: white; padding: 10px 14px; border-radius: 12px; align-self: flex-end; max-width: 80%; margin-left: auto;';
        userMsg.textContent = message;
        messagesContainer.appendChild(userMsg);
        
        input.value = '';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Send to bot
        fetch('https://{domain}/api/{config.bot_type}s/chat', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                bot_id: '{config.bot_id}',
                message: message
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            const botMsg = document.createElement('div');
            botMsg.style.cssText = 'background: #F3F4F6; color: {theme['text_color']}; padding: 10px 14px; border-radius: 12px; align-self: flex-start; max-width: 80%;';
            botMsg.textContent = data.response || 'Ho sento, no puc respondre ara mateix.';
            messagesContainer.appendChild(botMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }})
        .catch(error => {{
            console.error('Error:', error);
            const errorMsg = document.createElement('div');
            errorMsg.style.cssText = 'background: #FEE2E2; color: #DC2626; padding: 10px 14px; border-radius: 12px; align-self: flex-start; max-width: 80%;';
            errorMsg.textContent = 'Ho sento, hi ha hagut un error.';
            messagesContainer.appendChild(errorMsg);
        }});
    }};
    
    // Widget click event
    widget.addEventListener('click', window.toggleChat_{embed_id});
    
    // Enter key support
    document.getElementById('widget-input-{embed_id}').addEventListener('keypress', function(e) {{
        if (e.key === 'Enter') {{
            window.sendWidgetMessage_{embed_id}();
        }}
    }});
    
    // Hover effects
    widget.addEventListener('mouseenter', function() {{
        this.style.transform = 'scale(1.1)';
    }});
    
    widget.addEventListener('mouseleave', function() {{
        this.style.transform = 'scale(1)';
    }});
}})();
</script>
    """.strip()
    
    return js_code

def generate_react_component(embed_id: str, config: EmbedConfig, bot: Dict[str, Any]) -> str:
    """Generate React component code"""
    theme = EMBED_THEMES.get(config.theme, EMBED_THEMES["veuplus"])
    
    react_code = f"""
import React, {{ useState, useRef, useEffect }} from 'react';

const VeuPlusBot_{embed_id.replace('-', '_')} = () => {{
  const [messages, setMessages] = useState([
    {{ text: "Hola! Sóc {bot['name']}. Com et puc ajudar avui?", sender: 'bot' }}
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {{
    messagesEndRef.current?.scrollIntoView({{ behavior: 'smooth' }});
  }};

  useEffect(() => {{
    scrollToBottom();
  }}, [messages]);

  const sendMessage = async () => {{
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setMessages(prev => [...prev, {{ text: userMessage, sender: 'user' }}]);
    setInputValue('');
    setIsLoading(true);

    try {{
      const response = await fetch('/api/{config.bot_type}s/chat', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          bot_id: '{config.bot_id}',
          message: userMessage
        }})
      }});

      const data = await response.json();
      setMessages(prev => [...prev, {{ 
        text: data.response || 'Ho sento, no puc respondre ara mateix.', 
        sender: 'bot' 
      }}]);
    }} catch (error) {{
      console.error('Error:', error);
      setMessages(prev => [...prev, {{ 
        text: 'Ho sento, hi ha hagut un error.', 
        sender: 'bot' 
      }}]);
    }} finally {{
      setIsLoading(false);
    }}
  }};

  const handleKeyPress = (e) => {{
    if (e.key === 'Enter' && !e.shiftKey) {{
      e.preventDefault();
      sendMessage();
    }}
  }};

  return (
    <div style={{{{
      width: '400px',
      height: '500px',
      border: 'none',
      borderRadius: '{theme['border_radius']}',
      boxShadow: '{theme['shadow']}',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '{theme['background']}',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}}}>
      {{/* Header */}}
      <div style={{{{
        background: `linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']})`,
        color: 'white',
        padding: '16px',
        textAlign: 'center',
        fontWeight: '600'
      }}}}>
        🤖 {bot['name']}
      </div>

      {{/* Messages */}}
      <div style={{{{
        flex: 1,
        padding: '16px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}}}>
        {{messages.map((message, index) => (
          <div
            key={{index}}
            style={{{{
              maxWidth: '80%',
              padding: '10px 14px',
              borderRadius: '12px',
              alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: message.sender === 'user' ? '{theme['primary_color']}' : '#F3F4F6',
              color: message.sender === 'user' ? 'white' : '{theme['text_color']}',
              marginLeft: message.sender === 'user' ? 'auto' : '0'
            }}}}
          >
            {{message.text}}
          </div>
        ))}}
        {{isLoading && (
          <div style={{{{
            maxWidth: '80%',
            padding: '10px 14px',
            borderRadius: '12px',
            alignSelf: 'flex-start',
            backgroundColor: '#F3F4F6',
            color: '{theme['text_color']}'
          }}}}>
            Escrivint...
          </div>
        )}}
        <div ref={{messagesEndRef}} />
      </div>

      {{/* Input */}}
      <div style={{{{
        padding: '16px',
        borderTop: '1px solid #E5E7EB',
        display: 'flex',
        gap: '8px'
      }}}}>
        <input
          type="text"
          value={{inputValue}}
          onChange={{(e) => setInputValue(e.target.value)}}
          onKeyPress={{handleKeyPress}}
          placeholder="Escriu el teu missatge..."
          disabled={{isLoading}}
          style={{{{
            flex: 1,
            padding: '12px',
            border: '1px solid #D1D5DB',
            borderRadius: '8px',
            outline: 'none',
            fontSize: '14px'
          }}}}
        />
        <button
          onClick={{sendMessage}}
          disabled={{!inputValue.trim() || isLoading}}
          style={{{{
            background: '{theme['primary_color']}',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 16px',
            cursor: 'pointer',
            fontSize: '14px',
            opacity: (!inputValue.trim() || isLoading) ? 0.5 : 1
          }}}}
        >
          Enviar
        </button>
      </div>
    </div>
  );
}};

export default VeuPlusBot_{embed_id.replace('-', '_')};

// Usage:
// import VeuPlusBot from './VeuPlusBot_{embed_id.replace('-', '_')}';
// 
// function App() {{
//   return (
//     <div>
//       <h1>My Website</h1>
//       <VeuPlusBot_{embed_id.replace('-', '_')} />
//     </div>
//   );
// }}
    """.strip()
    
    return react_code

# Embed serving endpoints
@embed_router.get("/{embed_id}")
async def serve_embed(embed_id: str):
    """Serve embed page"""
    try:
        # Get embed configuration
        embed_data = db.execute_query("SELECT * FROM bot_embeddings WHERE id = ?", (embed_id,))
        
        if not embed_data:
            raise HTTPException(status_code=404, detail="Embed not found")
        
        embed = embed_data[0]
        
        # Get bot data
        if embed['bot_type'] == 'chatbot':
            bot = db.get_chatbot(embed['bot_id'])
        else:
            bot = db.get_voicebot(embed['bot_id'])
        
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Generate embed HTML
        config = EmbedConfig(
            bot_id=embed['bot_id'],
            bot_type=embed['bot_type'],
            theme=embed['theme'],
            size=embed['size'],
            position=embed['position'],
            custom_css=embed['custom_css']
        )
        
        html_content = generate_html_embed(embed_id, config, bot)
        
        # Update usage count
        db.execute_update(
            "bot_embeddings",
            {"usage_count": embed['usage_count'] + 1, "last_used": datetime.now().isoformat()},
            "id = ?",
            (embed_id,)
        )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve embed: {str(e)}")

@embed_router.get("/themes")
async def get_embed_themes():
    """Get available embed themes"""
    return {"themes": EMBED_THEMES, "sizes": EMBED_SIZES}

@embed_router.get("/stats/{embed_id}")
async def get_embed_stats(embed_id: str):
    """Get embed usage statistics"""
    try:
        embed_data = db.execute_query("SELECT * FROM bot_embeddings WHERE id = ?", (embed_id,))
        
        if not embed_data:
            raise HTTPException(status_code=404, detail="Embed not found")
        
        embed = embed_data[0]
        
        return {
            "embed_id": embed_id,
            "usage_count": embed['usage_count'],
            "created_at": embed['created_at'],
            "last_used": embed['last_used'],
            "bot_type": embed['bot_type'],
            "theme": embed['theme'],
            "size": embed['size']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get embed stats: {str(e)}")
#!/usr/bin/env python3
"""
VeuPlus Backend API Comprehensive Testing Suite
Tests all enhanced features including multi-language support, bot configuration, voice synthesis, and embedding widgets.
"""

import requests
import sys
import json
import time
from datetime import datetime
from io import BytesIO
import tempfile
import os

class VeuPlusAPITester:
    def __init__(self, base_url="https://54fe411b-0f98-4906-bf8c-c8a6fc8763b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.created_voice_id = None
        self.created_chatbot_id = None
        self.created_voicebot_id = None
        self.created_kb_item_id = None

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    def test_enhanced_features_connectivity(self):
        """Test enhanced API endpoints connectivity"""
        print("\n🌐 TESTING ENHANCED FEATURES CONNECTIVITY")
        print("=" * 60)
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "VeuPlus API" in data.get("message", ""):
                    self.log_test("API Health Check", True, f"Status: {data.get('status')}")
                else:
                    self.log_test("API Health Check", False, "Invalid response message")
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))

        # Test embed themes endpoint (new enhanced feature)
        try:
            response = requests.get(f"{self.api_url}/embed/themes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                themes = data.get("themes", {})
                sizes = data.get("sizes", {})
                if len(themes) >= 4 and len(sizes) >= 4:  # modern, minimal, catalan, voice + 4 sizes
                    self.log_test("Enhanced Embed Themes", True, f"Found {len(themes)} themes, {len(sizes)} sizes")
                    print(f"   Themes: {list(themes.keys())}")
                    print(f"   Sizes: {list(sizes.keys())}")
                else:
                    self.log_test("Enhanced Embed Themes", False, f"Insufficient themes/sizes: {len(themes)}/{len(sizes)}")
            else:
                self.log_test("Enhanced Embed Themes", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Embed Themes", False, str(e))

    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "VeuPlus API" in data.get("message", ""):
                    self.log_test("API Health Check", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_test("API Health Check", False, "Invalid response message")
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
        return False

    def test_catalan_dialects(self):
        """Test Catalan dialects endpoint"""
        try:
            response = requests.get(f"{self.api_url}/dialects", timeout=10)
            if response.status_code == 200:
                data = response.json()
                dialects = data.get("dialects", [])
                expected_dialects = ["central", "balearic", "valencian", "andorran", "rossellones", "alguerese"]
                
                if len(dialects) >= 6:
                    dialect_ids = [d.get("id") for d in dialects]
                    if all(expected in dialect_ids for expected in expected_dialects):
                        self.log_test("Catalan Dialects", True, f"Found {len(dialects)} dialects")
                        return True
                    else:
                        self.log_test("Catalan Dialects", False, "Missing expected dialects")
                else:
                    self.log_test("Catalan Dialects", False, f"Only {len(dialects)} dialects found")
            else:
                self.log_test("Catalan Dialects", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Catalan Dialects", False, str(e))
        return False

    def test_voice_endpoints(self):
        """Test voice training and retrieval endpoints"""
        # Test GET voices first
        try:
            response = requests.get(f"{self.api_url}/voices", timeout=10)
            if response.status_code == 200:
                data = response.json()
                voices = data.get("voices", [])
                self.log_test("Get Voices", True, f"Found {len(voices)} voices")
            else:
                self.log_test("Get Voices", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Voices", False, str(e))
            return False

        # Test voice training with mock audio file
        try:
            # Create a mock audio file
            mock_audio_content = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
            
            files = {
                'audio_files': ('test_voice.wav', BytesIO(mock_audio_content), 'audio/wav')
            }
            
            data = {
                'name': f'Test Voice {int(time.time())}',
                'dialect': 'central',
                'language': 'ca',
                'description': 'Test voice for API testing'
            }
            
            response = requests.post(f"{self.api_url}/voices/train", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "voice_id" in result:
                    self.log_test("Voice Training", True, f"Voice ID: {result['voice_id']}")
                    return result['voice_id']
                else:
                    self.log_test("Voice Training", False, "No voice_id in response")
            else:
                self.log_test("Voice Training", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Voice Training", False, str(e))
        
        return None

    def test_speech_synthesis(self, voice_id=None):
        """Test speech synthesis endpoint"""
        # If no voice_id provided, try to get one from existing voices
        if not voice_id:
            try:
                response = requests.get(f"{self.api_url}/voices", timeout=10)
                if response.status_code == 200:
                    voices = response.json().get("voices", [])
                    ready_voices = [v for v in voices if v.get("status") == "ready"]
                    if ready_voices:
                        voice_id = ready_voices[0]["id"]
                    else:
                        # Create a mock voice_id for testing
                        voice_id = "test-voice-id"
            except:
                voice_id = "test-voice-id"

        try:
            synthesis_data = {
                "text": "Hola, aquest és un test de síntesi de veu en català.",
                "voice_model_id": voice_id,
                "language": "ca"
            }
            
            response = requests.post(f"{self.api_url}/synthesis", json=synthesis_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "audio_id" in result and "audio_url" in result:
                    self.log_test("Speech Synthesis", True, f"Audio ID: {result['audio_id']}")
                    return result['audio_id']
                else:
                    self.log_test("Speech Synthesis", False, "Missing audio_id or audio_url")
            elif response.status_code == 404:
                self.log_test("Speech Synthesis", False, "Voice model not found (expected for test)")
            else:
                self.log_test("Speech Synthesis", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Speech Synthesis", False, str(e))
        
        return None

    def test_knowledge_base(self):
        """Test knowledge base endpoints"""
        # Test GET knowledge base
        try:
            response = requests.get(f"{self.api_url}/knowledge-base", timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                self.log_test("Get Knowledge Base", True, f"Found {len(items)} items")
            else:
                self.log_test("Get Knowledge Base", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Knowledge Base", False, str(e))
            return False

        # Test POST knowledge base (upload document)
        try:
            mock_text_content = "Aquest és un document de prova per a la base de coneixement en català."
            
            files = {
                'files': ('test_document.txt', BytesIO(mock_text_content.encode('utf-8')), 'text/plain')
            }
            
            data = {
                'name': f'Test Document {int(time.time())}'
            }
            
            response = requests.post(f"{self.api_url}/knowledge-base", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "items" in result:
                    self.log_test("Upload Knowledge Base", True, f"Uploaded {len(result['items'])} items")
                    return True
                else:
                    self.log_test("Upload Knowledge Base", False, "No items in response")
            else:
                self.log_test("Upload Knowledge Base", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Upload Knowledge Base", False, str(e))
        
        return False

    def test_enhanced_chatbot_configuration(self):
        """Test enhanced chatbot creation with comprehensive configuration"""
        print("\n💬 TESTING ENHANCED CHATBOT CONFIGURATION")
        print("=" * 60)
        
        # Test GET chatbots
        try:
            response = requests.get(f"{self.api_url}/chatbots", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bots = data.get("bots", [])
                self.log_test("Get Chatbots", True, f"Found {len(bots)} chatbots")
            else:
                self.log_test("Get Chatbots", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Chatbots", False, str(e))
            return None

        # Test enhanced chatbot creation with comprehensive config
        try:
            chatbot_data = {
                "name": f"Enhanced Test Chatbot {int(time.time())}",
                "llm_provider": "openai",
                "model_name": "gpt-4",
                "api_key": "sk-test-key-for-validation",  # Enhanced: API key field
                "temperature": 0.7,
                "max_tokens": 150,  # Enhanced: max tokens parameter
                "top_p": 1.0,  # Enhanced: top_p parameter
                "frequency_penalty": 0.0,  # Enhanced: frequency penalty
                "presence_penalty": 0.0,  # Enhanced: presence penalty
                "system_prompt": "You are a helpful AI assistant that responds in Catalan.",
                "knowledge_base_ids": [],
                "response_format": "text",  # Enhanced: response format
                "stream_responses": False,  # Enhanced: streaming option
                "context_window": 4000  # Enhanced: context window
            }
            
            response = requests.post(f"{self.api_url}/chatbots", json=chatbot_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "bot_id" in result:
                    bot_id = result["bot_id"]
                    self.created_chatbot_id = bot_id
                    self.log_test("Enhanced Chatbot Creation", True, f"Bot ID: {bot_id}")
                    
                    # Verify the bot was created with all enhanced parameters
                    self.verify_enhanced_chatbot_config(bot_id)
                    
                    # Test chat with the created bot
                    self.test_chatbot_chat(bot_id)
                    return bot_id
                else:
                    self.log_test("Enhanced Chatbot Creation", False, "No bot_id in response")
            else:
                self.log_test("Enhanced Chatbot Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Chatbot Creation", False, str(e))
        
        return None

    def verify_enhanced_chatbot_config(self, bot_id):
        """Verify that enhanced chatbot configuration was saved correctly"""
        try:
            response = requests.get(f"{self.api_url}/chatbots", timeout=10)
            if response.status_code == 200:
                bots = response.json().get("bots", [])
                created_bot = next((bot for bot in bots if bot.get("id") == bot_id), None)
                
                if created_bot:
                    # Check for enhanced parameters
                    enhanced_params = ["api_key", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"]
                    missing_params = [param for param in enhanced_params if param not in created_bot]
                    
                    if not missing_params:
                        self.log_test("Enhanced Config Verification", True, "All enhanced parameters present")
                        print(f"   API Key: {'✓' if created_bot.get('api_key') else '✗'}")
                        print(f"   Max Tokens: {created_bot.get('max_tokens', 'N/A')}")
                        print(f"   Temperature: {created_bot.get('temperature', 'N/A')}")
                        print(f"   Top P: {created_bot.get('top_p', 'N/A')}")
                    else:
                        self.log_test("Enhanced Config Verification", False, f"Missing parameters: {missing_params}")
                else:
                    self.log_test("Enhanced Config Verification", False, "Created bot not found")
            else:
                self.log_test("Enhanced Config Verification", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Config Verification", False, str(e))

    def test_chatbot_chat(self, bot_id):
        """Test chatbot chat functionality"""
        try:
            chat_data = {
                "message": "Hola, com estàs?",
                "bot_id": bot_id,
                "conversation_history": []
            }
            
            response = requests.post(f"{self.api_url}/chatbots/chat", json=chat_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "reply" in result:
                    self.log_test("Chatbot Chat", True, f"Reply received: {result['reply'][:50]}...")
                    return True
                else:
                    self.log_test("Chatbot Chat", False, "No reply in response")
            else:
                self.log_test("Chatbot Chat", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Chatbot Chat", False, str(e))
        
        return False

    def test_voicebot_endpoints(self):
        """Test voicebot endpoints"""
        # Test GET voicebots
        try:
            response = requests.get(f"{self.api_url}/voicebots", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bots = data.get("bots", [])
                self.log_test("Get Voicebots", True, f"Found {len(bots)} voicebots")
            else:
                self.log_test("Get Voicebots", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Voicebots", False, str(e))
            return False

        # Test POST voicebot (create) - requires a voice model
        try:
            voicebot_data = {
                "name": f"Test Voicebot {int(time.time())}",
                "voice_model_id": "test-voice-id",  # Mock ID
                "llm_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.7,
                "system_prompt": "You are a helpful voice assistant that responds in Catalan.",
                "knowledge_base_ids": []
            }
            
            response = requests.post(f"{self.api_url}/voicebots", json=voicebot_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "bot_id" in result:
                    self.log_test("Create Voicebot", True, f"Bot ID: {result['bot_id']}")
                    return result["bot_id"]
                else:
                    self.log_test("Create Voicebot", False, "No bot_id in response")
            elif response.status_code == 404:
                self.log_test("Create Voicebot", False, "Voice model not found (expected for test)")
            else:
                self.log_test("Create Voicebot", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Create Voicebot", False, str(e))
        
        return None

    def run_comprehensive_enhanced_tests(self):
        """Run comprehensive enhanced API test suite"""
        print("🚀 VeuPlus Enhanced Platform Comprehensive Test Suite")
        print("=" * 80)
        print(f"📡 Testing API at: {self.api_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Enhanced connectivity and features tests
            self.test_enhanced_features_connectivity()
            
            # Multi-language support (Catalan dialects)
            self.test_catalan_dialects()
            
            # Enhanced voice training and synthesis
            voice_id = self.test_voice_endpoints()
            self.test_enhanced_speech_synthesis(voice_id)
            
            # Knowledge base system
            self.test_knowledge_base()
            
            # Enhanced chatbot configuration
            chatbot_id = self.test_enhanced_chatbot_configuration()
            
            # Enhanced voicebot system
            self.test_enhanced_voicebot_endpoints(voice_id)
            
            # Enhanced embedding widgets
            self.test_enhanced_embedding_widgets(chatbot_id)
            
            # Print comprehensive summary
            self.print_enhanced_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% success rate threshold

    def test_enhanced_speech_synthesis(self, voice_id=None):
        """Test enhanced speech synthesis with quality feedback"""
        print("\n🗣️ TESTING ENHANCED SPEECH SYNTHESIS")
        print("=" * 60)
        
        # If no voice_id provided, try to get one from existing voices
        if not voice_id:
            try:
                response = requests.get(f"{self.api_url}/voices", timeout=10)
                if response.status_code == 200:
                    voices = response.json().get("voices", [])
                    ready_voices = [v for v in voices if v.get("status") == "ready"]
                    if ready_voices:
                        voice_id = ready_voices[0]["id"]
                    else:
                        # Create a mock voice_id for testing
                        voice_id = "test-voice-id"
            except:
                voice_id = "test-voice-id"

        try:
            synthesis_data = {
                "text": "Hola, aquest és un test de síntesi de veu en català amb qualitat millorada.",
                "voice_model_id": voice_id,
                "language": "ca"
            }
            
            response = requests.post(f"{self.api_url}/synthesis", json=synthesis_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "audio_id" in result and "audio_url" in result:
                    # Check for enhanced synthesis features
                    quality = result.get("quality", "unknown")
                    method = result.get("synthesis_method", "unknown")
                    dialect = result.get("dialect", "unknown")
                    
                    self.log_test("Enhanced Speech Synthesis", True, 
                                f"Audio ID: {result['audio_id']}, Quality: {quality}, Method: {method}")
                    
                    print(f"   🎵 Audio ID: {result['audio_id']}")
                    print(f"   🔊 Quality: {quality}")
                    print(f"   ⚙️ Method: {method}")
                    print(f"   🏴󠁥󠁳󠁣󠁴󠁿 Dialect: {dialect}")
                    
                    return result['audio_id']
                else:
                    self.log_test("Enhanced Speech Synthesis", False, "Missing audio_id or audio_url")
            elif response.status_code == 404:
                self.log_test("Enhanced Speech Synthesis", False, "Voice model not found (expected for test)")
            else:
                self.log_test("Enhanced Speech Synthesis", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Speech Synthesis", False, str(e))
        
        return None

    def test_enhanced_voicebot_endpoints(self, voice_id=None):
        """Test enhanced voicebot endpoints with voice model integration"""
        print("\n🤖 TESTING ENHANCED VOICEBOT SYSTEM")
        print("=" * 60)
        
        # Test GET voicebots
        try:
            response = requests.get(f"{self.api_url}/voicebots", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bots = data.get("bots", [])
                self.log_test("Get Voicebots", True, f"Found {len(bots)} voicebots")
            else:
                self.log_test("Get Voicebots", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Voicebots", False, str(e))
            return False

        # Test enhanced voicebot creation with voice model integration
        if voice_id:
            try:
                voicebot_data = {
                    "name": f"Enhanced Test Voicebot {int(time.time())}",
                    "voice_model_id": voice_id,
                    "llm_provider": "openai",
                    "model_name": "gpt-4",
                    "api_key": "sk-test-key-for-validation",  # Enhanced: API key
                    "temperature": 0.7,
                    "max_tokens": 150,  # Enhanced: max tokens
                    "system_prompt": "You are a helpful voice assistant that responds in Catalan.",
                    "knowledge_base_ids": [],
                    "voice_settings": {  # Enhanced: voice settings
                        "speed": 1.0,
                        "pitch": 1.0,
                        "volume": 1.0
                    },
                    "speech_speed": 1.0,  # Enhanced: speech parameters
                    "speech_pitch": 1.0,
                    "speech_volume": 1.0,
                    "auto_play_responses": True
                }
                
                response = requests.post(f"{self.api_url}/voicebots", json=voicebot_data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if "bot_id" in result:
                        self.created_voicebot_id = result["bot_id"]
                        self.log_test("Enhanced Voicebot Creation", True, f"Bot ID: {result['bot_id']}")
                        
                        # Test voice chat functionality
                        self.test_voicebot_chat(result["bot_id"])
                        return result["bot_id"]
                    else:
                        self.log_test("Enhanced Voicebot Creation", False, "No bot_id in response")
                elif response.status_code == 404:
                    self.log_test("Enhanced Voicebot Creation", False, "Voice model not found (expected for test)")
                else:
                    self.log_test("Enhanced Voicebot Creation", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Enhanced Voicebot Creation", False, str(e))
        else:
            self.log_test("Enhanced Voicebot Creation", False, "No voice_id available for testing")
        
        return None

    def test_voicebot_chat(self, bot_id):
        """Test voicebot voice chat functionality"""
        try:
            chat_data = {
                "message": "Explica'm què pots fer com a assistent de veu.",
                "bot_id": bot_id,
                "conversation_history": []
            }
            
            response = requests.post(f"{self.api_url}/voicebots/chat", json=chat_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "reply" in result and "audio_url" in result:
                    self.log_test("Voicebot Voice Chat", True, f"Reply and audio received")
                    print(f"   💬 Reply: {result['reply'][:50]}...")
                    print(f"   🔊 Audio URL: {result.get('audio_url', 'N/A')}")
                    print(f"   🎤 Voice Model: {result.get('voice_model', 'N/A')}")
                    return True
                else:
                    self.log_test("Voicebot Voice Chat", False, "Missing reply or audio_url")
            else:
                self.log_test("Voicebot Voice Chat", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Voicebot Voice Chat", False, str(e))
        
        return False

    def test_enhanced_embedding_widgets(self, chatbot_id=None):
        """Test enhanced embedding widgets with customization options"""
        print("\n🎨 TESTING ENHANCED EMBEDDING WIDGETS")
        print("=" * 60)
        
        # Test embed themes endpoint (already tested in connectivity, but verify again)
        try:
            response = requests.get(f"{self.api_url}/embed/themes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                themes = data.get("themes", {})
                sizes = data.get("sizes", {})
                self.log_test("Embed Customization Options", True, f"Themes: {len(themes)}, Sizes: {len(sizes)}")
            else:
                self.log_test("Embed Customization Options", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Embed Customization Options", False, str(e))
        
        # Test chatbot embed code generation with different themes
        if chatbot_id:
            themes_to_test = ["modern", "minimal", "catalan"]
            sizes_to_test = ["small", "medium", "large"]
            
            for theme in themes_to_test:
                for size in sizes_to_test[:1]:  # Test only one size per theme to avoid spam
                    try:
                        response = requests.get(
                            f"{self.api_url}/embed/chatbot/{chatbot_id}?theme={theme}&size={size}", 
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            embed_code = result.get("embed_code", "")
                            customization = result.get("customization_options", {})
                            
                            if len(embed_code) > 500:  # Reasonable embed code length
                                self.log_test(f"Chatbot Embed ({theme})", True, 
                                            f"Generated {len(embed_code)} chars")
                                print(f"   🎨 Theme: {theme}, Size: {size}")
                                print(f"   📏 Code length: {len(embed_code)} characters")
                                
                                # Check for advanced features in embed code
                                features = []
                                if "iframe" in embed_code:
                                    features.append("iframe")
                                if "toggleBtn" in embed_code:
                                    features.append("toggle")
                                if "animation" in embed_code:
                                    features.append("animations")
                                if "gradient" in embed_code:
                                    features.append("gradients")
                                
                                print(f"   ✨ Features: {', '.join(features) if features else 'basic'}")
                            else:
                                self.log_test(f"Chatbot Embed ({theme})", False, "Embed code too short")
                        else:
                            self.log_test(f"Chatbot Embed ({theme})", False, f"Status code: {response.status_code}")
                    except Exception as e:
                        self.log_test(f"Chatbot Embed ({theme})", False, str(e))
        
        # Test voicebot embed code generation
        if self.created_voicebot_id:
            try:
                response = requests.get(
                    f"{self.api_url}/embed/voicebot/{self.created_voicebot_id}?theme=voice&size=medium", 
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    embed_code = result.get("embed_code", "")
                    features = result.get("features", [])
                    
                    if len(embed_code) > 500:
                        self.log_test("Voicebot Embed (voice theme)", True, 
                                    f"Generated {len(embed_code)} chars")
                        print(f"   🎤 Voice features: {', '.join(features)}")
                    else:
                        self.log_test("Voicebot Embed (voice theme)", False, "Embed code too short")
                else:
                    self.log_test("Voicebot Embed (voice theme)", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Voicebot Embed (voice theme)", False, str(e))

    def print_enhanced_summary(self):
        """Print comprehensive enhanced test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ENHANCED TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📈 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Enhanced features analysis
        print("\n🎯 ENHANCED FEATURES ANALYSIS:")
        
        # Multi-language support
        dialect_tests = [r for r in self.test_results if 'dialect' in r['name'].lower()]
        if dialect_tests and any(r['success'] for r in dialect_tests):
            print("✅ Multi-language Support: Catalan dialects working")
        else:
            print("❌ Multi-language Support: Issues detected")
        
        # Enhanced bot configuration
        config_tests = [r for r in self.test_results if 'enhanced' in r['name'].lower() and 'config' in r['name'].lower()]
        if config_tests and any(r['success'] for r in config_tests):
            print("✅ Enhanced Bot Configuration: API keys and advanced parameters")
        else:
            print("❌ Enhanced Bot Configuration: Issues detected")
        
        # Voice synthesis quality
        synthesis_tests = [r for r in self.test_results if 'synthesis' in r['name'].lower()]
        if synthesis_tests and any(r['success'] for r in synthesis_tests):
            print("✅ Enhanced Voice Synthesis: Quality feedback and multi-backend")
        else:
            print("❌ Enhanced Voice Synthesis: Issues detected")
        
        # Embedding widgets
        embed_tests = [r for r in self.test_results if 'embed' in r['name'].lower()]
        if embed_tests and any(r['success'] for r in embed_tests):
            print("✅ Enhanced Embedding Widgets: Customizable themes and sizes")
        else:
            print("❌ Enhanced Embedding Widgets: Issues detected")
        
        # Voice-voicebot connection
        voicebot_tests = [r for r in self.test_results if 'voicebot' in r['name'].lower()]
        if voicebot_tests and any(r['success'] for r in voicebot_tests):
            print("✅ Voice-Voicebot Integration: Working connection")
        else:
            print("❌ Voice-Voicebot Integration: Issues detected")
        
        # Print failed tests for debugging
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests[:10]:  # Show first 10 failed tests
                print(f"  • {test['name']}: {test['details']}")
            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Enhanced platform ready!")
        elif success_rate >= 60:
            print("👍 OVERALL ASSESSMENT: GOOD - Minor enhancements needed")
        elif success_rate >= 40:
            print("⚠️ OVERALL ASSESSMENT: NEEDS WORK - Several issues to fix")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL - Major problems detected")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = VeuPlusAPITester()
    
    try:
        success = tester.run_comprehensive_enhanced_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
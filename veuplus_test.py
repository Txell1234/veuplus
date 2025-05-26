#!/usr/bin/env python3
"""
VeuPlus Production Validation Testing
Comprehensive testing for all VeuPlus endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

class VeuPlusAPITester:
    def __init__(self, base_url: str = "https://54fe411b-0f98-4906-bf8c-c8a6fc8763b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.created_items = {
            'chatbots': [],
            'voicebots': [],
            'voices': [],
            'knowledge_base': []
        }

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        if details and success:
            print(f"   {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details,
            'response_data': response_data,
            'timestamp': datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Any = None, files: Any = None) -> tuple[bool, Any, str]:
        """Make HTTP request and handle errors"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, None, f"Unsupported method: {method}"
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            success = 200 <= response.status_code < 300
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Response: {response.text[:200]}"
            
            return success, response_data, details
            
        except requests.exceptions.Timeout:
            return False, None, "Request timeout (30s)"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error"
        except Exception as e:
            return False, None, f"Request error: {str(e)}"

    def test_health_check(self):
        """Test API health endpoint"""
        print("\n🔍 Testing Health Check...")
        success, data, details = self.make_request('GET', 'health')
        
        if success and data:
            services = data.get('services', {})
            mongodb_status = services.get('mongodb', 'unknown')
            openai_status = services.get('openai', 'unknown')
            
            details += f" | MongoDB: {mongodb_status}, OpenAI: {openai_status}"
            
            if mongodb_status == 'connected':
                details += " | ✅ Database connected"
            if openai_status == 'available':
                details += " | ✅ OpenAI available"
        
        self.log_test("Health Check", success, details, data)
        return success

    def test_voice_synthesis(self):
        """Test voice synthesis with Catalan text"""
        print("\n🎤 Testing Voice Synthesis...")
        
        test_cases = [
            {
                "text": "Hola, sóc una veu sintètica catalana d'alta qualitat!",
                "voice_model_id": "catalan_enhanced",
                "language": "ca"
            },
            {
                "text": "Aquest és un test de síntesi de veu amb dialecte balear.",
                "voice_model_id": "catalan_enhanced", 
                "language": "ca"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            success, data, details = self.make_request('POST', 'synthesis', test_case)
            
            if success and data:
                audio_id = data.get('audio_id')
                synthesis_method = data.get('synthesis_method', 'unknown')
                quality = data.get('quality', 'unknown')
                real_audio = data.get('real_audio', False)
                
                details += f" | Audio ID: {audio_id}, Method: {synthesis_method}, Quality: {quality}"
                if real_audio:
                    details += " | ✅ Real Catalan Voice!"
                
                # Test audio file access
                if audio_id:
                    audio_success, _, audio_details = self.make_request('GET', f'audio/{audio_id}')
                    if audio_success:
                        details += " | ✅ Audio file accessible"
                    else:
                        details += f" | ❌ Audio file not accessible: {audio_details}"
            
            self.log_test(f"Voice Synthesis Test {i+1}", success, details, data)

    def test_knowledge_base(self):
        """Test knowledge base operations"""
        print("\n📚 Testing Knowledge Base...")
        
        # Test getting knowledge base (should work even if empty)
        success, data, details = self.make_request('GET', 'knowledge-base')
        self.log_test("Get Knowledge Base", success, details, data)
        
        # Test uploading knowledge base (simulate file upload)
        test_content = "Aquest és un document de prova per a la base de coneixement de VeuPlus. Conté informació sobre síntesi de veu catalana."
        
        files = {
            'files': ('test_document.txt', test_content.encode('utf-8'), 'text/plain')
        }
        form_data = {
            'name': 'Test Knowledge Document'
        }
        
        success, data, details = self.make_request('POST', 'knowledge-base', form_data, files)
        
        if success and data:
            items = data.get('items', [])
            if items:
                kb_item = items[0]
                self.created_items['knowledge_base'].append(kb_item['id'])
                details += f" | Created KB item: {kb_item['id']}"
        
        self.log_test("Upload Knowledge Base", success, details, data)

    def test_chatbots(self):
        """Test chatbot creation and chat functionality"""
        print("\n💬 Testing Chatbots...")
        
        # Test getting chatbots
        success, data, details = self.make_request('GET', 'chatbots')
        self.log_test("Get Chatbots", success, details, data)
        
        # Test creating chatbot
        chatbot_data = {
            "name": "Test Catalan Chatbot",
            "llm_provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "system_prompt": "Ets un assistent d'IA que parla català. Respon sempre en català de manera útil i amigable.",
            "api_key": "",  # Use global key
            "knowledge_base_ids": self.created_items['knowledge_base']
        }
        
        success, data, details = self.make_request('POST', 'chatbots', chatbot_data)
        
        chatbot_id = None
        if success and data:
            chatbot = data.get('chatbot', {})
            chatbot_id = chatbot.get('id')
            if chatbot_id:
                self.created_items['chatbots'].append(chatbot_id)
                details += f" | Created chatbot: {chatbot_id}"
                
                # Check if OpenAI Assistant ID is set
                assistant_id = chatbot.get('assistant_id')
                if assistant_id:
                    details += f" | Assistant ID: {assistant_id}"
        
        self.log_test("Create Chatbot", success, details, data)
        
        # Test chatbot conversation
        if chatbot_id:
            chat_data = {
                "message": "Hola! Com estàs? Pots parlar-me en català?",
                "bot_id": chatbot_id,
                "conversation_history": []
            }
            
            success, data, details = self.make_request('POST', 'chatbots/chat', chat_data)
            
            if success and data:
                reply = data.get('reply', '')
                assistant_used = data.get('assistant_used', '')
                model = data.get('model', '')
                
                details += f" | Reply length: {len(reply)} chars"
                if assistant_used:
                    details += f" | Assistant: {assistant_used}"
                if model:
                    details += f" | Model: {model}"
                
                # Check if reply is in Catalan (basic check)
                catalan_indicators = ['català', 'sóc', 'estic', 'com', 'hola', 'bé']
                if any(word in reply.lower() for word in catalan_indicators):
                    details += " | ✅ Response appears to be in Catalan"
            
            self.log_test("Chatbot Conversation", success, details, data)

    def test_voicebots(self):
        """Test voicebot creation and voice chat functionality - CRITICAL TEST"""
        print("\n🤖 Testing Voicebots (CRITICAL - was 404)...")
        
        # Test getting voicebots
        success, data, details = self.make_request('GET', 'voicebots')
        self.log_test("Get Voicebots", success, details, data)
        
        # Test creating voicebot
        voicebot_data = {
            "name": "Test Catalan Voicebot",
            "voice_model_id": "catalan_enhanced",
            "llm_provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "system_prompt": "Ets un assistent de veu intel·ligent que parla català. Respon de manera natural i amigable.",
            "api_key": "",  # Use global key
            "knowledge_base_ids": self.created_items['knowledge_base']
        }
        
        success, data, details = self.make_request('POST', 'voicebots', voicebot_data)
        
        voicebot_id = None
        if success and data:
            voicebot = data.get('voicebot', {})
            voicebot_id = voicebot.get('id')
            if voicebot_id:
                self.created_items['voicebots'].append(voicebot_id)
                details += f" | Created voicebot: {voicebot_id}"
                
                # Check voice model and assistant ID
                voice_model = voicebot.get('voice_model_id')
                assistant_id = voicebot.get('assistant_id')
                if voice_model:
                    details += f" | Voice: {voice_model}"
                if assistant_id:
                    details += f" | Assistant: {assistant_id}"
        
        self.log_test("Create Voicebot", success, details, data)
        
        # Test voicebot conversation (CRITICAL - was 404 before)
        if voicebot_id:
            print("🎯 Testing CRITICAL voicebot chat endpoint (was 404)...")
            
            voice_chat_data = {
                "message": "Hola! Pots respondre'm amb veu catalana?",
                "bot_id": voicebot_id,
                "conversation_history": []
            }
            
            success, data, details = self.make_request('POST', 'voicebots/chat', voice_chat_data)
            
            if success and data:
                reply = data.get('reply', '')
                audio_id = data.get('audio_id')
                audio_url = data.get('audio_url')
                synthesis_method = data.get('synthesis_method', '')
                quality = data.get('quality', '')
                real_audio = data.get('real_audio', False)
                assistant_used = data.get('assistant_used', '')
                
                details += f" | Reply: {len(reply)} chars"
                if audio_id:
                    details += f" | Audio ID: {audio_id}"
                if audio_url:
                    details += f" | Audio URL: {audio_url}"
                if synthesis_method:
                    details += f" | Method: {synthesis_method}"
                if quality:
                    details += f" | Quality: {quality}"
                if real_audio:
                    details += " | ✅ Real audio!"
                if assistant_used:
                    details += f" | Assistant: {assistant_used}"
                
                # Test audio file if available
                if audio_id:
                    audio_success, _, audio_details = self.make_request('GET', f'audio/{audio_id}')
                    if audio_success:
                        details += " | ✅ Voice audio accessible"
                    else:
                        details += f" | ❌ Voice audio not accessible: {audio_details}"
            
            self.log_test("CRITICAL: Voicebot Voice Chat", success, details, data)

    def test_voice_training(self):
        """Test voice training functionality"""
        print("\n🎤 Testing Voice Training...")
        
        # Test getting voices
        success, data, details = self.make_request('GET', 'voices')
        self.log_test("Get Voices", success, details, data)
        
        # Test voice training (simulate form data)
        form_data = {
            'name': 'Test Catalan Voice',
            'dialect': 'central',
            'description': 'Test voice for VeuPlus validation',
            'use_catalan_dataset': 'true'
        }
        
        # Simulate audio file upload (empty for now since we're using Catalan dataset)
        files = {}
        
        success, data, details = self.make_request('POST', 'voices/train', form_data, files)
        
        if success and data:
            voice = data.get('voice', {})
            voice_id = voice.get('id')
            if voice_id:
                self.created_items['voices'].append(voice_id)
                details += f" | Created voice: {voice_id}"
                
                # Check training details
                status = voice.get('status', '')
                progress = voice.get('progress', 0)
                training_quality = voice.get('training_quality', '')
                catalan_enhanced = voice.get('catalan_enhanced', False)
                
                details += f" | Status: {status}, Progress: {progress}%"
                if training_quality:
                    details += f" | Quality: {training_quality}"
                if catalan_enhanced:
                    details += " | ✅ Catalan Enhanced"
        
        self.log_test("Voice Training", success, details, data)

    def test_catalan_dataset_download(self):
        """Test Catalan dataset download functionality"""
        print("\n🏴󠁥󠁳󠁣󠁴󠁿 Testing Catalan Dataset Download...")
        
        success, data, details = self.make_request('POST', 'voices/download-catalan-dataset')
        
        if success and data:
            status = data.get('status', '')
            message = data.get('message', '')
            samples_downloaded = data.get('samples_downloaded', 0)
            datasets = data.get('datasets', [])
            
            details += f" | Status: {status}"
            if message:
                details += f" | Message: {message[:100]}"
            if samples_downloaded:
                details += f" | Samples: {samples_downloaded}"
            if datasets:
                details += f" | Datasets: {len(datasets)}"
        
        self.log_test("Catalan Dataset Download", success, details, data)

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        cleanup_count = 0
        
        # Delete created chatbots
        for chatbot_id in self.created_items['chatbots']:
            success, _, details = self.make_request('DELETE', f'chatbots/{chatbot_id}')
            if success:
                cleanup_count += 1
                print(f"   ✅ Deleted chatbot: {chatbot_id}")
            else:
                print(f"   ❌ Failed to delete chatbot {chatbot_id}: {details}")
        
        # Delete created voicebots
        for voicebot_id in self.created_items['voicebots']:
            success, _, details = self.make_request('DELETE', f'voicebots/{voicebot_id}')
            if success:
                cleanup_count += 1
                print(f"   ✅ Deleted voicebot: {voicebot_id}")
            else:
                print(f"   ❌ Failed to delete voicebot {voicebot_id}: {details}")
        
        # Delete created voices
        for voice_id in self.created_items['voices']:
            success, _, details = self.make_request('DELETE', f'voices/{voice_id}')
            if success:
                cleanup_count += 1
                print(f"   ✅ Deleted voice: {voice_id}")
            else:
                print(f"   ❌ Failed to delete voice {voice_id}: {details}")
        
        # Delete created knowledge base items
        for kb_id in self.created_items['knowledge_base']:
            success, _, details = self.make_request('DELETE', f'knowledge-base/{kb_id}')
            if success:
                cleanup_count += 1
                print(f"   ✅ Deleted knowledge base item: {kb_id}")
            else:
                print(f"   ❌ Failed to delete knowledge base item {kb_id}: {details}")
        
        print(f"   Cleaned up {cleanup_count} items")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting VeuPlus Production Validation Testing")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Core functionality tests
        if not self.test_health_check():
            print("❌ API not responding - stopping tests")
            return False
            
        self.test_voice_synthesis()
        self.test_knowledge_base()
        self.test_chatbots()
        self.test_voicebots()  # CRITICAL - was 404
        self.test_voice_training()
        self.test_catalan_dataset_download()
        
        # Cleanup
        self.cleanup_test_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"🕒 Total time: {duration:.2f} seconds")
        print(f"📈 Tests run: {self.tests_run}")
        print(f"✅ Tests passed: {self.tests_passed}")
        print(f"❌ Tests failed: {self.tests_run - self.tests_passed}")
        print(f"📊 Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Critical issues
        critical_issues = []
        for result in self.test_results:
            if not result['success']:
                if 'voicebot' in result['name'].lower() and 'chat' in result['name'].lower():
                    critical_issues.append(f"🚨 CRITICAL: {result['name']} - {result['details']}")
                elif 'synthesis' in result['name'].lower():
                    critical_issues.append(f"⚠️ HIGH: {result['name']} - {result['details']}")
                else:
                    critical_issues.append(f"❌ {result['name']} - {result['details']}")
        
        if critical_issues:
            print("\n🚨 ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   {issue}")
        else:
            print("\n🎉 ALL TESTS PASSED! VeuPlus is ready for production!")
        
        # Return success status
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = VeuPlusAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
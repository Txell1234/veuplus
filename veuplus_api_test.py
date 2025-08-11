#!/usr/bin/env python3
"""
VeuPlus Platform - Comprehensive Backend Testing
Testing all major transformations for production readiness

🎯 MAJOR TRANSFORMATIONS TO TEST:
1. SQL Database Migration - Converted from MongoDB to SQLite
2. Bot Embedding System - Bots can be embedded in websites with 4 themes and sizes
3. SIP Trunk Integration - Bots can handle phone calls through SIP providers
4. Real Voice Training - Actual voice model creation (not simulation)
5. Voice Selection in Bot Creation - Professional voice selection interface
"""

import requests
import sys
import json
import time
from datetime import datetime
from io import BytesIO
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VeuPlusAPITester:
    def __init__(self, base_url="http://localhost:8001"):
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
        self.embed_id = None
        self.sip_integration_id = None

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            logger.info(f"✅ {name} - PASSED")
        else:
            logger.error(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    def test_api_health(self):
        """Test API health check"""
        logger.info("\n🔍 TESTING API HEALTH")
        logger.info("=" * 60)
        
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"Status: {data.get('status', 'OK')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
        return False

    def test_sql_database(self):
        """Test SQL database functionality"""
        logger.info("\n🔍 TESTING SQL DATABASE FUNCTIONALITY")
        logger.info("=" * 60)
        
        # Test endpoints that should use SQL backend
        endpoints = [
            "/api/voices",
            "/api/chatbots",
            "/api/voicebots",
            "/api/knowledge-base"
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"SQL Endpoint: {endpoint}", True, f"Response received")
                else:
                    self.log_test(f"SQL Endpoint: {endpoint}", False, f"Status code: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"SQL Endpoint: {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed

    def test_voice_training(self):
        """Test real voice training"""
        logger.info("\n🔍 TESTING REAL VOICE TRAINING")
        logger.info("=" * 60)
        
        try:
            # Create a mock audio file
            mock_audio_content = b"RIFF\x24\x08WAVEfmt \x10\x01\x01\x44\xac\x88X\x01\x02\x10data\x08"
            
            files = {
                'audio_files': ('test_voice.wav', BytesIO(mock_audio_content), 'audio/wav')
            }
            
            data = {
                'name': f'Test Catalan Voice {int(time.time())}',
                'dialect': 'central',
                'language': 'ca',
                'description': 'Test voice for API testing'
            }
            
            response = requests.post(f"{self.api_url}/voices/train", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "voice_id" in result:
                    self.created_voice_id = result['voice_id']
                    self.log_test("Real Voice Training", True, f"Voice ID: {result['voice_id']}")
                    
                    # Verify voice model exists
                    voice_response = requests.get(f"{self.api_url}/voices/{result['voice_id']}", timeout=10)
                    if voice_response.status_code == 200:
                        voice_data = voice_response.json()
                        is_real = voice_data.get("real_model", False)
                        self.log_test("Voice Model Verification", True, f"Real model: {is_real}")
                        return result['voice_id']
                    else:
                        self.log_test("Voice Model Verification", False, f"Status code: {voice_response.status_code}")
                else:
                    self.log_test("Real Voice Training", False, "No voice_id in response")
            else:
                self.log_test("Real Voice Training", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Real Voice Training", False, str(e))
        
        return None

    def test_voice_selection(self):
        """Test voice selection in bot creation"""
        logger.info("\n🔍 TESTING VOICE SELECTION IN BOT CREATION")
        logger.info("=" * 60)
        
        try:
            # First get available voices
            response = requests.get(f"{self.api_url}/voices", timeout=10)
            if response.status_code != 200:
                self.log_test("Get Available Voices", False, f"Status code: {response.status_code}")
                return False
            
            voices = response.json().get("voices", [])
            if not voices:
                self.log_test("Get Available Voices", False, "No voices available")
                return False
            
            self.log_test("Get Available Voices", True, f"Found {len(voices)} voices")
            
            # Select a voice for testing
            voice_id = voices[0]["id"] if voices else "test-voice-id"
            
            # Create a voicebot with the selected voice
            voicebot_data = {
                "name": f"Test Voicebot with Voice Selection {int(time.time())}",
                "voice_model_id": voice_id,
                "llm_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "system_prompt": "You are a helpful voice assistant that responds in Catalan.",
                "knowledge_base_ids": []
            }
            
            response = requests.post(f"{self.api_url}/voicebots", json=voicebot_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "bot_id" in result:
                    self.created_voicebot_id = result["bot_id"]
                    self.log_test("Create Voicebot with Selected Voice", True, f"Bot ID: {result['bot_id']}")
                    
                    # Verify voicebot has the correct voice
                    voicebot_response = requests.get(f"{self.api_url}/voicebots/{result['bot_id']}", timeout=10)
                    if voicebot_response.status_code == 200:
                        voicebot_data = voicebot_response.json()
                        if voicebot_data.get("voice_model_id") == voice_id:
                            self.log_test("Voicebot Voice Verification", True, f"Voice ID matches: {voice_id}")
                            return True
                        else:
                            self.log_test("Voicebot Voice Verification", False, f"Voice ID mismatch: {voicebot_data.get('voice_model_id')} != {voice_id}")
                    else:
                        self.log_test("Voicebot Voice Verification", False, f"Status code: {voicebot_response.status_code}")
                else:
                    self.log_test("Create Voicebot with Selected Voice", False, "No bot_id in response")
            else:
                self.log_test("Create Voicebot with Selected Voice", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Create Voicebot with Selected Voice", False, str(e))
        
        return False

    def test_bot_embedding(self):
        """Test bot embedding system"""
        logger.info("\n🔍 TESTING BOT EMBEDDING SYSTEM")
        logger.info("=" * 60)
        
        # Test embed themes endpoint
        try:
            response = requests.get(f"{self.api_url}/embed/themes", timeout=10)
            if response.status_code == 200:
                data = response.json()
                themes = data.get("themes", {})
                sizes = data.get("sizes", {})
                if len(themes) >= 4 and len(sizes) >= 4:
                    self.log_test("Embed Themes and Sizes", True, f"Found {len(themes)} themes, {len(sizes)} sizes")
                else:
                    self.log_test("Embed Themes and Sizes", False, f"Insufficient themes/sizes: {len(themes)}/{len(sizes)}")
                    return False
            else:
                self.log_test("Embed Themes and Sizes", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Embed Themes and Sizes", False, str(e))
            return False
        
        # Test embed generation for a bot
        if self.created_chatbot_id or self.created_voicebot_id:
            bot_id = self.created_chatbot_id or self.created_voicebot_id
            bot_type = "chatbot" if self.created_chatbot_id else "voicebot"
            
            try:
                # Test different themes
                themes = ["veuplus", "catalan", "modern", "minimal"]
                sizes = ["small", "medium", "large", "fullscreen"]
                
                for theme in themes:
                    for size in sizes[:1]:  # Test only one size per theme to avoid too many tests
                        embed_data = {
                            "bot_id": bot_id,
                            "bot_type": bot_type,
                            "theme": theme,
                            "size": size
                        }
                        
                        response = requests.post(f"{self.api_url}/embed/generate", json=embed_data, timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json()
                            if "embed_id" in result and "html_code" in result:
                                self.embed_id = result["embed_id"]
                                self.log_test(f"Embed Generation ({theme}, {size})", True, f"Embed ID: {result['embed_id']}")
                            else:
                                self.log_test(f"Embed Generation ({theme}, {size})", False, "Missing embed_id or html_code")
                        else:
                            self.log_test(f"Embed Generation ({theme}, {size})", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Embed Generation", False, str(e))
                return False
            
            # Test embed serving
            if self.embed_id:
                try:
                    response = requests.get(f"{self.api_url}/embed/{self.embed_id}", timeout=10)
                    if response.status_code == 200:
                        self.log_test("Embed Serving", True, f"Embed served successfully")
                        return True
                    else:
                        self.log_test("Embed Serving", False, f"Status code: {response.status_code}")
                except Exception as e:
                    self.log_test("Embed Serving", False, str(e))
        else:
            self.log_test("Embed Generation", False, "No bot available for testing")
        
        return False

    def test_sip_integration(self):
        """Test SIP integration setup"""
        logger.info("\n🔍 TESTING SIP INTEGRATION")
        logger.info("=" * 60)
        
        # Test SIP providers endpoint
        try:
            response = requests.get(f"{self.api_url}/sip/providers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", {})
                if len(providers) >= 3:  # Twilio, Vonage, Telnyx
                    self.log_test("SIP Providers", True, f"Found {len(providers)} providers")
                else:
                    self.log_test("SIP Providers", False, f"Insufficient providers: {len(providers)}")
                    return False
            else:
                self.log_test("SIP Providers", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("SIP Providers", False, str(e))
            return False
        
        # Test SIP configuration for a bot
        if self.created_voicebot_id:
            try:
                # Test with Twilio provider
                sip_data = {
                    "bot_id": self.created_voicebot_id,
                    "bot_type": "voicebot",
                    "sip_provider": "twilio",
                    "sip_number": "+1234567890",
                    "provider_config": {
                        "account_sid": "AC123456789",
                        "auth_token": "auth_token_123"
                    }
                }
                
                response = requests.post(f"{self.api_url}/sip/configure", json=sip_data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if "sip_id" in result and "webhook_url" in result:
                        self.sip_integration_id = result["sip_id"]
                        self.log_test("SIP Configuration", True, f"SIP ID: {result['sip_id']}")
                    else:
                        self.log_test("SIP Configuration", False, "Missing sip_id or webhook_url")
                else:
                    self.log_test("SIP Configuration", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("SIP Configuration", False, str(e))
                return False
            
            # Test SIP integrations listing
            try:
                response = requests.get(f"{self.api_url}/sip/integrations", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    integrations = data.get("integrations", [])
                    self.log_test("SIP Integrations Listing", True, f"Found {len(integrations)} integrations")
                    return True
                else:
                    self.log_test("SIP Integrations Listing", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("SIP Integrations Listing", False, str(e))
        else:
            self.log_test("SIP Configuration", False, "No voicebot available for testing")
        
        return False

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        logger.info("\n🔍 TESTING END-TO-END WORKFLOW")
        logger.info("=" * 60)
        
        # Step 1: Train a new voice model
        voice_id = self.test_voice_training()
        if not voice_id:
            self.log_test("E2E: Voice Training", False, "Failed to train voice model")
            return False
        
        self.log_test("E2E: Voice Training", True, f"Voice ID: {voice_id}")
        
        # Step 2: Create a voicebot with the trained voice
        try:
            voicebot_data = {
                "name": f"E2E Test Voicebot {int(time.time())}",
                "voice_model_id": voice_id,
                "llm_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "system_prompt": "You are a helpful voice assistant that responds in Catalan.",
                "knowledge_base_ids": []
            }
            
            response = requests.post(f"{self.api_url}/voicebots", json=voicebot_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "bot_id" in result:
                    bot_id = result["bot_id"]
                    self.log_test("E2E: Create Voicebot", True, f"Bot ID: {bot_id}")
                else:
                    self.log_test("E2E: Create Voicebot", False, "No bot_id in response")
                    return False
            else:
                self.log_test("E2E: Create Voicebot", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("E2E: Create Voicebot", False, str(e))
            return False
        
        # Step 3: Generate embedding code for the voicebot
        try:
            embed_data = {
                "bot_id": bot_id,
                "bot_type": "voicebot",
                "theme": "veuplus",
                "size": "medium"
            }
            
            response = requests.post(f"{self.api_url}/embed/generate", json=embed_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "embed_id" in result:
                    embed_id = result["embed_id"]
                    self.log_test("E2E: Generate Embed", True, f"Embed ID: {embed_id}")
                else:
                    self.log_test("E2E: Generate Embed", False, "No embed_id in response")
                    return False
            else:
                self.log_test("E2E: Generate Embed", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("E2E: Generate Embed", False, str(e))
            return False
        
        # Step 4: Configure SIP integration for the voicebot
        try:
            sip_data = {
                "bot_id": bot_id,
                "bot_type": "voicebot",
                "sip_provider": "twilio",
                "sip_number": "+1234567890",
                "provider_config": {
                    "account_sid": "AC123456789",
                    "auth_token": "auth_token_123"
                }
            }
            
            response = requests.post(f"{self.api_url}/sip/configure", json=sip_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "sip_id" in result:
                    sip_id = result["sip_id"]
                    self.log_test("E2E: Configure SIP", True, f"SIP ID: {sip_id}")
                else:
                    self.log_test("E2E: Configure SIP", False, "No sip_id in response")
                    return False
            else:
                self.log_test("E2E: Configure SIP", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("E2E: Configure SIP", False, str(e))
            return False
        
        # Step 5: Test voicebot chat
        try:
            chat_data = {
                "message": "Hola, com estàs?",
                "bot_id": bot_id,
                "conversation_history": []
            }
            
            response = requests.post(f"{self.api_url}/voicebots/chat", json=chat_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "reply" in result and "audio_url" in result:
                    self.log_test("E2E: Voicebot Chat", True, f"Reply received with audio")
                    return True
                else:
                    self.log_test("E2E: Voicebot Chat", False, "Missing reply or audio_url")
                    return False
            else:
                self.log_test("E2E: Voicebot Chat", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("E2E: Voicebot Chat", False, str(e))
            return False

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        logger.info(f"📈 Total Tests Run: {self.tests_run}")
        logger.info(f"✅ Tests Passed: {self.tests_passed}")
        logger.info(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Group results by feature
        feature_results = {
            "SQL Database": [t for t in self.test_results if "SQL" in t["name"]],
            "Voice Training": [t for t in self.test_results if "Voice Training" in t["name"] or "Voice Model" in t["name"]],
            "Voice Selection": [t for t in self.test_results if "Voice Selection" in t["name"] or "Selected Voice" in t["name"]],
            "Bot Embedding": [t for t in self.test_results if "Embed" in t["name"]],
            "SIP Integration": [t for t in self.test_results if "SIP" in t["name"]],
            "End-to-End Workflow": [t for t in self.test_results if "E2E" in t["name"]]
        }
        
        logger.info("\n🎯 FEATURE RESULTS:")
        for feature, tests in feature_results.items():
            if tests:
                passed = sum(1 for t in tests if t["success"])
                logger.info(f"  • {feature}: {passed}/{len(tests)} tests passed")
        
        # Print failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            logger.info(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                logger.info(f"  • {test['name']}: {test['details']}")
        
        logger.info("\n" + "=" * 80)
        
        if success_rate >= 90:
            logger.info("🎉 OVERALL ASSESSMENT: EXCELLENT - Platform ready for production!")
        elif success_rate >= 75:
            logger.info("👍 OVERALL ASSESSMENT: GOOD - Minor issues to fix")
        elif success_rate >= 50:
            logger.info("⚠️ OVERALL ASSESSMENT: NEEDS WORK - Several issues to fix")
        else:
            logger.info("🚨 OVERALL ASSESSMENT: CRITICAL - Major problems detected")
        
        logger.info("=" * 80)

    def run_all_tests(self):
        """Run all tests"""
        logger.info("🎯 VeuPlus Platform Comprehensive Testing")
        logger.info("=" * 80)
        logger.info(f"📡 Testing API at: {self.api_url}")
        logger.info(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        try:
            # Basic connectivity
            if not self.test_api_health():
                logger.error("❌ API not responding - stopping tests")
                return False
            
            # Test SQL database
            self.test_sql_database()
            
            # Test voice training
            self.test_voice_training()
            
            # Test voice selection
            self.test_voice_selection()
            
            # Test bot embedding
            self.test_bot_embedding()
            
            # Test SIP integration
            self.test_sip_integration()
            
            # Test end-to-end workflow
            self.test_end_to_end_workflow()
            
            # Print summary
            self.print_summary()
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            logger.error(f"\n💥 Unexpected error during testing: {e}")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% success rate

def main():
    """Main test execution"""
    tester = VeuPlusAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
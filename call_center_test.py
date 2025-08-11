#!/usr/bin/env python3
"""
VeuPlus Call Center System - Comprehensive Testing
Testing all Call Center functionality for production readiness

🎯 CALL CENTER TESTING FOCUS:
1. Call Center Creation - Test creating new call centers
2. Call Center Dashboard - Verify dashboard data retrieval
3. AI Agents - Test default agent creation and management
4. Analytics - Verify analytics data retrieval
5. SIP Integration - Test SIP configuration and webhook URLs
"""

import requests
import sys
import json
import time
from datetime import datetime

class CallCenterAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.created_call_center_id = None
        self.created_agent_id = None

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

    def test_health_check(self):
        """Test basic API health check"""
        try:
            # Use call-center endpoint instead of root endpoint
            response = requests.get(f"{self.api_url}/call-center/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "call_centers" in data:
                    self.log_test("API Health Check", True, "Call Center API is responding")
                    return True
                else:
                    self.log_test("API Health Check", False, "Invalid response format")
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
        return False

    def test_list_call_centers(self):
        """Test listing all call centers"""
        try:
            response = requests.get(f"{self.api_url}/call-center/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                centers = data.get("call_centers", [])
                self.log_test("List Call Centers", True, f"Found {len(centers)} call centers")
                print(f"   📊 Call Centers: {len(centers)}")
                return centers
            else:
                self.log_test("List Call Centers", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("List Call Centers", False, str(e))
        return []

    def test_create_call_center(self):
        """Test creating a new call center"""
        try:
            call_center_data = {
                "name": f"Test Call Center {int(time.time())}",
                "description": "Testing VeuPlus call center capabilities",
                "languages": ["ca", "es", "en"]
            }
            
            response = requests.post(f"{self.api_url}/call-center/create", json=call_center_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "call_center_id" in result:
                    self.created_call_center_id = result["call_center_id"]
                    self.log_test("Create Call Center", True, f"Call Center ID: {result['call_center_id']}")
                    
                    # Print important details
                    print(f"   🏢 Call Center ID: {result['call_center_id']}")
                    print(f"   📞 SIP Number: {result.get('sip_number', 'N/A')}")
                    print(f"   🔗 Webhook URL: {result.get('webhook_url', 'N/A')}")
                    
                    # Check default agents
                    default_agents = result.get("default_agents", [])
                    if default_agents:
                        print(f"   🤖 Default Agents: {len(default_agents)}")
                        for agent in default_agents:
                            print(f"      - {agent.get('name', 'Unknown')} ({agent.get('language', 'Unknown')})")
                    
                    return result["call_center_id"]
                else:
                    self.log_test("Create Call Center", False, "No call_center_id in response")
            else:
                self.log_test("Create Call Center", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create Call Center", False, str(e))
        
        return None

    def test_get_dashboard(self, call_center_id=None):
        """Test getting call center dashboard data"""
        if not call_center_id and self.created_call_center_id:
            call_center_id = self.created_call_center_id
        
        if not call_center_id:
            self.log_test("Get Dashboard", False, "No call center ID available")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/call-center/dashboard/{call_center_id}", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for expected dashboard components
                call_center = result.get("call_center", {})
                agents = result.get("agents", [])
                recent_calls = result.get("recent_calls", [])
                
                self.log_test("Get Dashboard", True, f"Dashboard data retrieved successfully")
                print(f"   🏢 Call Center: {call_center.get('name', 'Unknown')}")
                print(f"   🤖 Agents: {len(agents)}")
                print(f"   📞 Recent Calls: {len(recent_calls)}")
                
                return True
            else:
                self.log_test("Get Dashboard", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Get Dashboard", False, str(e))
        
        return False

    def test_get_analytics(self, call_center_id=None):
        """Test getting call center analytics"""
        if not call_center_id and self.created_call_center_id:
            call_center_id = self.created_call_center_id
        
        if not call_center_id:
            self.log_test("Get Analytics", False, "No call center ID available")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/call-center/analytics/{call_center_id}?period=7d", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                analytics = result.get("analytics", {})
                
                self.log_test("Get Analytics", True, f"Analytics data retrieved successfully")
                print(f"   📊 Total Calls: {analytics.get('total_calls', 0)}")
                print(f"   ⏱️ Avg Call Duration: {analytics.get('avg_call_duration', 0)} minutes")
                print(f"   ✅ Resolution Rate: {analytics.get('resolution_rate', 0) * 100:.1f}%")
                print(f"   💰 Cost Savings: €{analytics.get('cost_savings', 0)}")
                
                # Check language distribution
                lang_dist = analytics.get("language_distribution", {})
                if lang_dist:
                    print(f"   🌐 Language Distribution:")
                    for lang, count in lang_dist.items():
                        print(f"      - {lang}: {count} calls")
                
                return True
            else:
                self.log_test("Get Analytics", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Get Analytics", False, str(e))
        
        return False

    def test_create_agent(self, call_center_id=None):
        """Test creating a new call center agent"""
        if not call_center_id and self.created_call_center_id:
            call_center_id = self.created_call_center_id
        
        if not call_center_id:
            self.log_test("Create Agent", False, "No call center ID available")
            return False
        
        try:
            agent_data = {
                "name": f"Test Agent {int(time.time())}",
                "voice_model_id": "test_voice_model",
                "specialization": "technical",
                "languages": ["ca", "es"],
                "knowledge_base_ids": [],
                "escalation_threshold": 0.6,
                "personality_prompt": "You are a technical support agent who is very knowledgeable about IT issues."
            }
            
            response = requests.post(f"{self.api_url}/call-center/agents?call_center_id={call_center_id}", 
                                   json=agent_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "agent_id" in result:
                    self.created_agent_id = result["agent_id"]
                    self.log_test("Create Agent", True, f"Agent ID: {result['agent_id']}")
                    print(f"   🤖 Agent ID: {result['agent_id']}")
                    print(f"   👤 Name: {result.get('name', 'Unknown')}")
                    print(f"   🔧 Specialization: {result.get('specialization', 'Unknown')}")
                    return True
                else:
                    self.log_test("Create Agent", False, "No agent_id in response")
            else:
                self.log_test("Create Agent", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create Agent", False, str(e))
        
        return False

    def test_sip_providers(self):
        """Test getting SIP providers"""
        try:
            response = requests.get(f"{self.api_url}/sip/providers", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                providers = result.get("providers", {})
                
                self.log_test("SIP Providers", True, f"Found {len(providers)} SIP providers")
                print(f"   📞 SIP Providers: {len(providers)}")
                for provider, details in providers.items():
                    print(f"      - {provider}: {details.get('name', 'Unknown')}")
                
                return True
            else:
                self.log_test("SIP Providers", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("SIP Providers", False, str(e))
        
        return False

    def test_webhook_simulation(self, call_center_id=None):
        """Test call center webhook simulation"""
        if not call_center_id and self.created_call_center_id:
            call_center_id = self.created_call_center_id
        
        if not call_center_id:
            self.log_test("Webhook Simulation", False, "No call center ID available")
            return False
        
        try:
            # Simulate an incoming call
            webhook_data = {
                "From": "+34612345678",
                "To": "+34-12345678",
                "CallSid": f"test-call-{int(time.time())}",
                "SpeechResult": "Hola, necesito ayuda con mi cuenta."
            }
            
            response = requests.post(f"{self.api_url}/call-center/webhook/{call_center_id}", 
                                   json=webhook_data, timeout=30)
            
            if response.status_code == 200:
                # Check if we got a valid response (could be TwiML or JSON)
                content_type = response.headers.get('content-type', '')
                
                if 'application/xml' in content_type:
                    # TwiML response
                    if '<Response>' in response.text and '<Say>' in response.text:
                        self.log_test("Webhook Simulation", True, "Valid TwiML response received")
                        return True
                elif 'application/json' in content_type:
                    # JSON response
                    result = response.json()
                    if 'response' in result or 'ncco' in result:
                        self.log_test("Webhook Simulation", True, "Valid JSON response received")
                        return True
                
                self.log_test("Webhook Simulation", False, "Invalid response format")
            else:
                self.log_test("Webhook Simulation", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Webhook Simulation", False, str(e))
        
        return False

    def run_all_tests(self):
        """Run all call center tests"""
        print("🎯 VeuPlus Call Center System Testing")
        print("=" * 80)
        print(f"📡 Testing API at: {self.api_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Basic connectivity
            if not self.test_health_check():
                print("❌ API not responding - stopping tests")
                return False
            
            # List existing call centers
            centers = self.test_list_call_centers()
            
            # Create a new call center
            self.created_call_center_id = self.test_create_call_center()
            
            if self.created_call_center_id:
                # Test dashboard
                self.test_get_dashboard(self.created_call_center_id)
                
                # Test analytics
                self.test_get_analytics(self.created_call_center_id)
                
                # Test creating a custom agent
                self.test_create_agent(self.created_call_center_id)
                
                # Test webhook simulation
                self.test_webhook_simulation(self.created_call_center_id)
            
            # Test SIP providers
            self.test_sip_providers()
            
            # Print summary
            self.print_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        
        return self.tests_passed >= (self.tests_run * 0.8)  # 80% success rate

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 CALL CENTER TESTING RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📈 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n🎯 CALL CENTER FEATURES STATUS:")
        
        # Check each feature
        feature_checks = [
            ("Call Center Creation", "create call center"),
            ("Dashboard", "dashboard"),
            ("Analytics", "analytics"),
            ("Agent Management", "agent"),
            ("SIP Integration", "sip"),
            ("Webhook Handling", "webhook")
        ]
        
        for feature_name, test_keyword in feature_checks:
            related_tests = [t for t in self.test_results if test_keyword.lower() in t['name'].lower()]
            if related_tests:
                passed_tests = [t for t in related_tests if t['success']]
                if len(passed_tests) == len(related_tests):
                    print(f"✅ {feature_name}: WORKING")
                elif len(passed_tests) > 0:
                    print(f"⚠️ {feature_name}: PARTIALLY WORKING ({len(passed_tests)}/{len(related_tests)})")
                else:
                    print(f"❌ {feature_name}: NOT WORKING")
            else:
                print(f"❓ {feature_name}: NOT TESTED")
        
        # Print failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n🚨 FAILURES ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Call Center system ready for production!")
        elif success_rate >= 75:
            print("👍 OVERALL ASSESSMENT: GOOD - Minor issues to fix")
        elif success_rate >= 50:
            print("⚠️ OVERALL ASSESSMENT: NEEDS WORK - Several issues to address")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL - Major problems detected")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = CallCenterAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
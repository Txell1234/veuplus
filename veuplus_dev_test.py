#!/usr/bin/env python3
"""
VeuPlus Developer Platform - Comprehensive Testing
Testing the new developer dashboard and API management features
"""

import requests
import sys
import json
import time
from datetime import datetime

class VeuPlusDeveloperPlatformTester:
    def __init__(self, base_url="https://54fe411b-0f98-4906-bf8c-c8a6fc8763b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.dev_api_url = f"{self.api_url}/dev"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.api_key = None
        self.project_id = None

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
        """Test API health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
        return False

    def test_api_key_creation(self):
        """Test API key creation endpoint"""
        try:
            api_key_data = {
                "name": f"Test Key {int(time.time())}",
                "description": "Created during automated testing",
                "permissions": ["tts", "stt", "chat"]
            }
            
            response = requests.post(f"{self.dev_api_url}/api-keys", json=api_key_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "api_key" in data:
                    self.api_key = data["api_key"]
                    self.log_test("API Key Creation", True, f"API Key: {self.api_key[:10]}...")
                    return self.api_key
                else:
                    self.log_test("API Key Creation", False, "No API key in response")
            else:
                self.log_test("API Key Creation", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("API Key Creation", False, str(e))
        
        return None

    def test_list_api_keys(self):
        """Test listing API keys endpoint"""
        try:
            response = requests.get(f"{self.dev_api_url}/api-keys", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "api_keys" in data:
                    keys = data["api_keys"]
                    self.log_test("List API Keys", True, f"Found {len(keys)} API keys")
                    return keys
                else:
                    self.log_test("List API Keys", False, "No api_keys in response")
            else:
                self.log_test("List API Keys", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("List API Keys", False, str(e))
        
        return []

    def test_usage_analytics(self):
        """Test usage analytics endpoint"""
        try:
            response = requests.get(f"{self.dev_api_url}/analytics/usage?period=7d", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "total_requests" in data:
                    self.log_test("Usage Analytics", True, f"Total requests: {data['total_requests']}")
                    return data
                else:
                    self.log_test("Usage Analytics", False, "No total_requests in response")
            else:
                self.log_test("Usage Analytics", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Usage Analytics", False, str(e))
        
        return {}

    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        try:
            response = requests.get(f"{self.dev_api_url}/analytics/performance", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "performance_metrics" in data:
                    metrics = data["performance_metrics"]
                    self.log_test("Performance Metrics", True, f"Found {len(metrics)} metrics")
                    return metrics
                else:
                    self.log_test("Performance Metrics", False, "No performance_metrics in response")
            else:
                self.log_test("Performance Metrics", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Performance Metrics", False, str(e))
        
        return []

    def test_create_project(self):
        """Test project creation endpoint"""
        if not self.api_key:
            self.log_test("Create Project", False, "No API key available")
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            project_data = {
                "name": f"Test Project {int(time.time())}",
                "description": "Created during automated testing"
            }
            
            response = requests.post(f"{self.dev_api_url}/projects", json=project_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "project" in data and "id" in data["project"]:
                    self.project_id = data["project"]["id"]
                    self.log_test("Create Project", True, f"Project ID: {self.project_id}")
                    return self.project_id
                else:
                    self.log_test("Create Project", False, "No project ID in response")
            else:
                self.log_test("Create Project", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create Project", False, str(e))
        
        return None

    def test_list_projects(self):
        """Test listing projects endpoint"""
        if not self.api_key:
            self.log_test("List Projects", False, "No API key available")
            return []
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.dev_api_url}/projects", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "projects" in data:
                    projects = data["projects"]
                    self.log_test("List Projects", True, f"Found {len(projects)} projects")
                    return projects
                else:
                    self.log_test("List Projects", False, "No projects in response")
            else:
                self.log_test("List Projects", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("List Projects", False, str(e))
        
        return []

    def test_api_endpoints_discovery(self):
        """Test API endpoints discovery"""
        try:
            response = requests.get(f"{self.dev_api_url}/endpoints", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "available_endpoints" in data:
                    endpoints = data["available_endpoints"]
                    self.log_test("API Endpoints Discovery", True, f"Found {len(endpoints)} endpoints")
                    return endpoints
                else:
                    self.log_test("API Endpoints Discovery", False, "No available_endpoints in response")
            else:
                self.log_test("API Endpoints Discovery", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("API Endpoints Discovery", False, str(e))
        
        return {}

    def test_billing_usage(self):
        """Test billing usage endpoint"""
        if not self.api_key:
            self.log_test("Billing Usage", False, "No API key available")
            return {}
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.dev_api_url}/billing/usage", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "billing_usage" in data:
                    usage = data["billing_usage"]
                    self.log_test("Billing Usage", True, f"Billing period: {usage.get('billing_period', 'N/A')}")
                    return usage
                else:
                    self.log_test("Billing Usage", False, "No billing_usage in response")
            else:
                self.log_test("Billing Usage", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Billing Usage", False, str(e))
        
        return {}

    def test_platform_status(self):
        """Test platform status endpoint"""
        try:
            response = requests.get(f"{self.dev_api_url}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "platform_status" in data:
                    status = data["platform_status"]
                    components = data.get("components", {})
                    self.log_test("Platform Status", True, f"Status: {status}, Components: {len(components)}")
                    return data
                else:
                    self.log_test("Platform Status", False, "No platform_status in response")
            else:
                self.log_test("Platform Status", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Platform Status", False, str(e))
        
        return {}

    def test_revoke_api_key(self):
        """Test revoking API key endpoint"""
        if not self.api_key:
            self.log_test("Revoke API Key", False, "No API key available")
            return False
        
        try:
            response = requests.delete(f"{self.dev_api_url}/api-keys/{self.api_key}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "revoked" in data["message"].lower():
                    self.log_test("Revoke API Key", True, f"Message: {data['message']}")
                    return True
                else:
                    self.log_test("Revoke API Key", False, f"Unexpected message: {data.get('message', 'N/A')}")
            else:
                self.log_test("Revoke API Key", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Revoke API Key", False, str(e))
        
        return False

    def test_original_features_still_working(self):
        """Test that original voice and bot features still work"""
        print("\n🔄 TESTING ORIGINAL FEATURES COMPATIBILITY")
        print("=" * 60)
        
        # Test voice synthesis
        try:
            synthesis_data = {
                "text": "Hola, bon dia! Com estàs avui?",
                "voice_model_id": "catalan_enhanced",
                "language": "ca"
            }
            
            response = requests.post(f"{self.api_url}/synthesis", json=synthesis_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "audio_url" in data:
                    self.log_test("Original Voice Synthesis", True, f"Audio URL: {data['audio_url']}")
                else:
                    self.log_test("Original Voice Synthesis", False, "No audio_url in response")
            else:
                self.log_test("Original Voice Synthesis", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Original Voice Synthesis", False, str(e))
        
        # Test chatbots listing
        try:
            response = requests.get(f"{self.api_url}/chatbots", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "bots" in data:
                    self.log_test("Original Chatbots Listing", True, f"Found {len(data['bots'])} chatbots")
                else:
                    self.log_test("Original Chatbots Listing", False, "No bots in response")
            else:
                self.log_test("Original Chatbots Listing", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Original Chatbots Listing", False, str(e))
        
        # Test voicebots listing
        try:
            response = requests.get(f"{self.api_url}/voicebots", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "bots" in data:
                    self.log_test("Original Voicebots Listing", True, f"Found {len(data['bots'])} voicebots")
                else:
                    self.log_test("Original Voicebots Listing", False, "No bots in response")
            else:
                self.log_test("Original Voicebots Listing", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Original Voicebots Listing", False, str(e))

    def run_all_tests(self):
        """Run all developer platform tests"""
        print("🚀 VeuPlus Developer Platform Testing")
        print("=" * 80)
        print(f"📡 Testing API at: {self.api_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Basic connectivity
            if not self.test_health_check():
                print("❌ API not responding - stopping tests")
                return False
            
            # Test API key management
            self.test_api_key_creation()
            self.test_list_api_keys()
            
            # Test analytics
            self.test_usage_analytics()
            self.test_performance_metrics()
            
            # Test project management
            self.test_create_project()
            self.test_list_projects()
            
            # Test API documentation
            self.test_api_endpoints_discovery()
            
            # Test billing
            self.test_billing_usage()
            
            # Test platform status
            self.test_platform_status()
            
            # Test original features still work
            self.test_original_features_still_working()
            
            # Test revoking API key (do this last)
            self.test_revoke_api_key()
            
            # Print summary
            self.print_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% success rate

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 DEVELOPER PLATFORM TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📈 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Group tests by category
        categories = {
            "API Key Management": ["API Key Creation", "List API Keys", "Revoke API Key"],
            "Analytics": ["Usage Analytics", "Performance Metrics"],
            "Project Management": ["Create Project", "List Projects"],
            "Documentation": ["API Endpoints Discovery"],
            "Billing": ["Billing Usage"],
            "Platform Status": ["Platform Status"],
            "Original Features": ["Original Voice Synthesis", "Original Chatbots Listing", "Original Voicebots Listing"]
        }
        
        print("\n🔍 RESULTS BY CATEGORY:")
        
        for category, test_names in categories.items():
            category_tests = [t for t in self.test_results if any(name in t["name"] for name in test_names)]
            if category_tests:
                passed = sum(1 for t in category_tests if t["success"])
                total = len(category_tests)
                if passed == total:
                    print(f"✅ {category}: All tests passed ({passed}/{total})")
                elif passed > 0:
                    print(f"⚠️ {category}: Some tests passed ({passed}/{total})")
                else:
                    print(f"❌ {category}: All tests failed (0/{total})")
        
        # Print failed tests
        failed_tests = [t for t in self.test_results if not t["success"]]
        if failed_tests:
            print(f"\n🚨 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Developer Platform ready for production!")
        elif success_rate >= 70:
            print("👍 OVERALL ASSESSMENT: GOOD - Minor issues to fix")
        elif success_rate >= 50:
            print("⚠️ OVERALL ASSESSMENT: NEEDS WORK - Several issues to fix")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL - Major problems detected")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = VeuPlusDeveloperPlatformTester()
    
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
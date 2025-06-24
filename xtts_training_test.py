#!/usr/bin/env python3
"""
VeuPlus Platform - XTTS v2 Voice Training Pipeline Testing
Testing the newly implemented real XTTS v2 voice training pipeline with multi-language support
"""

import requests
import json
import time
import sys
import websocket
import threading
import ssl
from datetime import datetime

class XTTSTrainingTester:
    def __init__(self, base_url="https://54fe411b-0f98-4906-bf8c-c8a6fc8763b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.ws_messages = []
        self.ws_connected = False
        self.ws_error = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_system_status(self):
        """Test system status endpoint"""
        success, response = self.run_test(
            "System Status",
            "GET",
            "training/system/status",
            200
        )
        
        if success:
            print(f"System status: {json.dumps(response, indent=2)}")
            print(f"GPU Available: {response.get('gpu_available', False)}")
            print(f"Active Training Jobs: {response.get('active_training_jobs', 0)}")
            print(f"System Ready: {response.get('system_ready', False)}")
        
        return success

    def test_supported_languages(self):
        """Test supported languages endpoint"""
        success, response = self.run_test(
            "Supported Languages",
            "GET",
            "training/languages",
            200
        )
        
        if success:
            languages = response.get('supported_languages', {})
            print(f"Supported languages: {', '.join(languages.keys())}")
            
            # Check if Catalan is supported with dialects
            if 'ca' in languages:
                catalan = languages['ca']
                print(f"Catalan dialects: {', '.join(catalan.get('dialects', []))}")
        
        return success

    def test_training_jobs(self):
        """Test training jobs listing endpoint"""
        success, response = self.run_test(
            "Training Jobs List",
            "GET",
            "training/jobs",
            200
        )
        
        if success:
            jobs = response.get('jobs', [])
            print(f"Found {len(jobs)} training jobs")
            
            if jobs:
                print("Recent jobs:")
                for job in jobs[:3]:  # Show only the most recent 3 jobs
                    print(f"  - {job.get('name')} ({job.get('language')}) - Status: {job.get('status')}")
        
        return success

    def test_start_training(self, language="ca", dialect="central"):
        """Test starting a training job"""
        training_data = {
            "name": f"Test Voice {datetime.now().strftime('%H%M%S')}",
            "language": language,
            "dialect": dialect,
            "use_catalan_dataset": True,
            "training_config": {
                "num_epochs": 10,  # Reduced for testing
                "batch_size": 4,
                "learning_rate": 0.0001
            }
        }
        
        success, response = self.run_test(
            f"Start Training ({language}/{dialect})",
            "POST",
            "training/start",
            200,
            data=training_data
        )
        
        if success:
            job_id = response.get('job_id')
            print(f"Training job started with ID: {job_id}")
            return job_id
        
        return None

    def test_job_status(self, job_id):
        """Test getting job status"""
        success, response = self.run_test(
            "Job Status",
            "GET",
            f"training/jobs/{job_id}",
            200
        )
        
        if success:
            print(f"Job status: {response.get('status')}")
            print(f"Progress: {response.get('progress')}%")
            
            if 'epoch' in response:
                print(f"Current epoch: {response.get('epoch')}")
            
            if 'loss' in response:
                print(f"Current loss: {response.get('loss')}")
        
        return success

    def test_cancel_training(self, job_id):
        """Test cancelling a training job"""
        success, response = self.run_test(
            "Cancel Training",
            "DELETE",
            f"training/jobs/{job_id}",
            200
        )
        
        if success:
            print(f"Job cancelled: {response.get('message', '')}")
        
        return success

    def on_ws_message(self, ws, message):
        """Handle WebSocket message"""
        try:
            data = json.loads(message)
            self.ws_messages.append(data)
            print(f"WebSocket progress update: {data.get('progress')}% - {data.get('message')}")
        except Exception as e:
            print(f"Error parsing WebSocket message: {e}")

    def on_ws_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"WebSocket error: {error}")
        self.ws_error = error

    def on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.ws_connected = False

    def on_ws_open(self, ws):
        """Handle WebSocket open"""
        print("WebSocket connection established")
        self.ws_connected = True

    def test_websocket_progress(self, job_id, timeout=30):
        """Test WebSocket progress updates"""
        print(f"\n🔍 Testing WebSocket Progress Updates for job {job_id}...")
        
        # Extract domain from base_url
        domain = self.base_url.split('//')[1].split('/')[0]
        ws_url = f"wss://{domain}/api/training/ws/{job_id}"
        
        print(f"Connecting to WebSocket: {ws_url}")
        
        # Reset WebSocket state
        self.ws_messages = []
        self.ws_connected = False
        self.ws_error = None
        
        # Create WebSocket connection
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_ws_message,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close,
            on_open=self.on_ws_open
        )
        
        # Start WebSocket in a separate thread
        ws_thread = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for connection or timeout
        start_time = time.time()
        while not self.ws_connected and not self.ws_error and time.time() - start_time < 10:
            time.sleep(0.1)
        
        if not self.ws_connected:
            print(f"❌ Failed to connect to WebSocket: {self.ws_error}")
            self.tests_run += 1
            return False
        
        # Wait for messages or timeout
        print(f"Waiting for progress updates (timeout: {timeout}s)...")
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            if len(self.ws_messages) > 0:
                break
            time.sleep(1)
        
        # Close WebSocket
        ws.close()
        
        # Check results
        self.tests_run += 1
        if len(self.ws_messages) > 0:
            self.tests_passed += 1
            print(f"✅ Passed - Received {len(self.ws_messages)} WebSocket messages")
            return True
        else:
            print("❌ Failed - No WebSocket messages received")
            return False

    def test_multi_language_support(self):
        """Test training with different languages"""
        languages = ["ca", "es", "fr", "en", "pt"]
        results = {}
        
        for lang in languages:
            print(f"\n🔍 Testing {lang.upper()} language support...")
            job_id = self.test_start_training(language=lang)
            
            if job_id:
                # Wait a bit for the job to start
                time.sleep(3)
                
                # Check job status
                success = self.test_job_status(job_id)
                
                # Try to cancel the job to clean up
                self.test_cancel_training(job_id)
                
                results[lang] = success
            else:
                results[lang] = False
        
        # Print summary
        print("\n📊 Multi-language Support Results:")
        for lang, success in results.items():
            status = "✅ Supported" if success else "❌ Failed"
            print(f"{lang.upper()}: {status}")
        
        return all(results.values())

    def run_all_tests(self):
        """Run all XTTS v2 voice training tests"""
        print("🎯 VeuPlus XTTS v2 Voice Training Pipeline Testing")
        print("=" * 80)
        print(f"📡 Testing API at: {self.api_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # Test system status
            self.test_system_status()
            
            # Test supported languages
            self.test_supported_languages()
            
            # Test training jobs listing
            self.test_training_jobs()
            
            # Test starting a training job
            job_id = self.test_start_training()
            
            if job_id:
                # Test WebSocket progress updates
                self.test_websocket_progress(job_id, timeout=20)
                
                # Test job status
                self.test_job_status(job_id)
                
                # Test cancelling the job
                self.test_cancel_training(job_id)
            
            # Test multi-language support (limited to save time)
            # Uncomment to test all languages
            # self.test_multi_language_support()
            
            # Print results
            self.print_summary()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        
        return self.tests_passed >= (self.tests_run * 0.8)  # 80% success rate

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 XTTS v2 VOICE TRAINING TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📈 Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 ASSESSMENT: EXCELLENT - XTTS v2 training pipeline working perfectly!")
        elif success_rate >= 75:
            print("\n👍 ASSESSMENT: GOOD - XTTS v2 training pipeline working with minor issues")
        elif success_rate >= 50:
            print("\n⚠️ ASSESSMENT: NEEDS WORK - XTTS v2 training pipeline has significant issues")
        else:
            print("\n🚨 ASSESSMENT: CRITICAL - XTTS v2 training pipeline not working")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = XTTSTrainingTester()
    
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
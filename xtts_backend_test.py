import requests
import json
import time
import sys
import websocket
import threading
import ssl
from datetime import datetime

class XTTSTrainingTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.ws_messages = []
        self.ws_connected = False
        self.ws_error = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/training/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
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
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_system_status(self):
        """Test system status endpoint"""
        success, response = self.run_test(
            "System Status",
            "GET",
            "system/status",
            200
        )
        
        if success:
            print(f"GPU Available: {response.get('gpu_available', False)}")
            print(f"Active Training Jobs: {response.get('active_training_jobs', 0)}")
            print(f"Supported Languages: {response.get('supported_languages', [])}")
        
        return success

    def test_supported_languages(self):
        """Test supported languages endpoint"""
        success, response = self.run_test(
            "Supported Languages",
            "GET",
            "languages",
            200
        )
        
        if success:
            languages = response.get('supported_languages', {})
            print(f"Supported Languages: {list(languages.keys())}")
            
            # Check if all 5 required languages are supported
            required_languages = ['ca', 'es', 'fr', 'en', 'pt']
            all_languages_supported = all(lang in languages for lang in required_languages)
            
            if all_languages_supported:
                print("✅ All required languages are supported")
                
                # Check Catalan dialects
                if 'ca' in languages and 'dialects' in languages['ca']:
                    catalan_dialects = languages['ca']['dialects']
                    required_dialects = ['central', 'balearic', 'valencian', 'andorran', 'rossellones', 'alguerese']
                    all_dialects_supported = all(dialect in catalan_dialects for dialect in required_dialects)
                    
                    if all_dialects_supported:
                        print(f"✅ All required Catalan dialects are supported: {catalan_dialects}")
                    else:
                        print(f"❌ Not all required Catalan dialects are supported. Found: {catalan_dialects}")
                        success = False
                else:
                    print("❌ Catalan language or dialects information missing")
                    success = False
            else:
                print(f"❌ Not all required languages are supported. Found: {list(languages.keys())}")
                success = False
        
        return success

    def test_start_training(self, language="ca", dialect="central"):
        """Test starting a training job"""
        training_data = {
            "name": f"Test Voice {datetime.now().strftime('%H%M%S')}",
            "language": language,
            "dialect": dialect,
            "use_catalan_dataset": True,
            "custom_audio_files": [],
            "training_config": {
                "num_epochs": 25,  # Reduced for testing
                "batch_size": 4,
                "learning_rate": 0.0001
            }
        }
        
        success, response = self.run_test(
            f"Start Training ({language}-{dialect})",
            "POST",
            "start",
            200,
            data=training_data
        )
        
        if success and 'job_id' in response:
            job_id = response['job_id']
            print(f"Training job started with ID: {job_id}")
            return success, job_id
        
        return False, None

    def test_get_jobs(self):
        """Test getting training jobs"""
        success, response = self.run_test(
            "Get Training Jobs",
            "GET",
            "jobs",
            200
        )
        
        if success and 'jobs' in response:
            jobs = response['jobs']
            print(f"Found {len(jobs)} training jobs")
            
            if len(jobs) > 0:
                print(f"Latest job: {jobs[0]['name']} - Status: {jobs[0]['status']}")
            
            return success, jobs
        
        return False, []

    def test_get_job_status(self, job_id):
        """Test getting a specific job status"""
        success, response = self.run_test(
            f"Get Job Status ({job_id})",
            "GET",
            f"jobs/{job_id}",
            200
        )
        
        if success:
            print(f"Job Status: {response.get('status', 'unknown')}")
            print(f"Progress: {response.get('progress', 0)}%")
            
            return success, response
        
        return False, {}

    def test_cancel_job(self, job_id):
        """Test cancelling a job"""
        success, response = self.run_test(
            f"Cancel Job ({job_id})",
            "DELETE",
            f"jobs/{job_id}",
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
            print(f"WebSocket Progress: {data.get('progress', 0)}% - {data.get('message', '')}")
        except Exception as e:
            print(f"Error parsing WebSocket message: {e}")

    def on_ws_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"WebSocket Error: {error}")
        self.ws_error = error

    def on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"WebSocket Closed: {close_status_code} - {close_msg}")
        self.ws_connected = False

    def on_ws_open(self, ws):
        """Handle WebSocket open"""
        print("WebSocket Connected")
        self.ws_connected = True

    def test_websocket_progress(self, job_id, timeout=30):
        """Test WebSocket progress updates"""
        print(f"\n🔍 Testing WebSocket Progress Updates for job {job_id}...")
        
        # Convert HTTP to WebSocket protocol
        domain = self.base_url.split('://')[-1]
        ws_url = f"wss://{domain}/api/training/ws/{job_id}"
        
        print(f"Connecting to WebSocket: {ws_url}")
        
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
        
        # Wait for connection
        start_time = time.time()
        while not self.ws_connected and not self.ws_error and time.time() - start_time < 10:
            time.sleep(0.1)
        
        if not self.ws_connected:
            print(f"❌ Failed to connect to WebSocket: {self.ws_error}")
            self.tests_run += 1
            return False
        
        # Wait for messages
        print(f"Waiting for progress updates (max {timeout} seconds)...")
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
            print(f"✅ Received {len(self.ws_messages)} WebSocket progress updates")
            return True
        else:
            print("❌ No WebSocket progress updates received")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting XTTS v2 Training API Tests 🧪")
        
        # Test system status
        system_status_ok = self.test_system_status()
        
        # Test supported languages
        languages_ok = self.test_supported_languages()
        
        # Test training jobs list
        jobs_ok, jobs = self.test_get_jobs()
        
        # Start a new training job
        training_ok, job_id = self.test_start_training()
        
        if training_ok and job_id:
            # Test job status
            self.test_get_job_status(job_id)
            
            # Test WebSocket progress
            self.test_websocket_progress(job_id, timeout=20)
            
            # Test cancelling the job
            self.test_cancel_job(job_id)
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    # Get base URL from command line if provided
    base_url = "http://localhost:8001"
    
    # Run tests
    tester = XTTSTrainingTester(base_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
import requests
import json
import time
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenAIConfigTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_api_key = "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"

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        elif self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

        self.tests_run += 1
        logging.info(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                logging.info(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                logging.error(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            logging.error(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test basic API connectivity"""
        return self.run_test("API Root", "GET", "api", 200)

    def test_init_admin(self):
        """Test admin initialization"""
        return self.run_test("Initialize Admin", "POST", "api/init-admin", 200)

    def test_admin_login(self, email="admin@ketto.org", password="admin123"):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            logging.info(f"Admin login successful, token obtained")
            return True
        return False

    def test_get_initial_config(self):
        """Test getting the initial OpenAI configuration"""
        if not self.admin_token:
            logging.error("❌ Cannot test GPT config: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Get Initial GPT Config",
            "GET",
            "api/admin/gpt-config",
            200,
            token=self.admin_token
        )
        
        if success:
            logging.info(f"Initial GPT config status: {response.get('status', 'unknown')}")
            if 'api_key' in response:
                logging.info(f"API key preview: {response['api_key']}")
            return True, response
        return False, None

    def test_save_new_config(self):
        """Test saving a new OpenAI API key"""
        if not self.admin_token:
            logging.error("❌ Cannot test saving GPT config: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Save New GPT Config",
            "POST",
            "api/admin/gpt-config",
            200,
            data={"api_key": self.test_api_key},
            token=self.admin_token
        )
        
        if success:
            logging.info(f"GPT config saved: {response.get('message', 'unknown')}")
            if 'api_key_preview' in response:
                logging.info(f"API key preview: {response['api_key_preview']}")
            return True, response
        return False, None

    def test_verify_saved_config(self):
        """Test verifying the saved OpenAI API key"""
        if not self.admin_token:
            logging.error("❌ Cannot test verifying GPT config: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Verify Saved GPT Config",
            "GET",
            "api/admin/gpt-config",
            200,
            token=self.admin_token
        )
        
        if success:
            logging.info(f"GPT config status: {response.get('status', 'unknown')}")
            if 'api_key' in response:
                logging.info(f"API key preview: {response['api_key']}")
            
            # Verify the status is "configured"
            if response.get('status') == 'configured':
                logging.info("✅ API key is properly configured in database")
                return True, response
            else:
                logging.error(f"❌ API key not properly configured, status: {response.get('status')}")
                return False, response
        return False, None

    def test_chat_functionality(self):
        """Test chat functionality with the configured API key"""
        # First register a test user
        timestamp = datetime.now().strftime("%H%M%S")
        employee_data = {
            "name": f"Test Employee {timestamp}",
            "email": f"employee{timestamp}@test.com",
            "password": "test123",
            "role": "employee"
        }
        
        success, response = self.run_test(
            "Employee Registration",
            "POST",
            "api/auth/register",
            200,
            data=employee_data
        )
        
        if not success or 'access_token' not in response:
            logging.error("❌ Failed to register test employee")
            return False, None
        
        employee_token = response['access_token']
        employee_id = response['user']['id']
        
        # Test chat with AI
        success, response = self.run_test(
            "Chat with CareAI",
            "POST",
            "api/chat",
            200,
            data={"message": "I'm feeling stressed at work", "user_id": employee_id},
            token=employee_token
        )
        
        if success:
            ai_response = response.get('response', '')
            logging.info(f"AI Response: {ai_response[:100]}...")
            
            # Check if we got a meaningful response
            if len(ai_response) > 20:
                logging.info("✅ Received meaningful AI response")
                return True, response
            else:
                logging.error("❌ AI response too short or empty")
                return False, response
        return False, None

    def test_config_endpoint(self):
        """Test the new test-gpt-config endpoint"""
        if not self.admin_token:
            logging.error("❌ Cannot test GPT config endpoint: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Test GPT Config Endpoint",
            "POST",
            "api/admin/test-gpt-config",
            200,
            token=self.admin_token
        )
        
        if success:
            logging.info(f"Test result: {response.get('message', 'unknown')}")
            logging.info(f"Status: {response.get('status', 'unknown')}")
            if 'test_response' in response:
                logging.info(f"Test response: {response['test_response']}")
            
            # Verify the status is "working"
            if response.get('status') == 'working' and response.get('success') == True:
                logging.info("✅ API key is working correctly")
                return True, response
            else:
                logging.error(f"❌ API key test failed, status: {response.get('status')}")
                return False, response
        return False, None

    def simulate_server_restart(self):
        """Simulate server restart by restarting the backend service"""
        logging.info("Simulating server restart...")
        try:
            os.system("sudo supervisorctl restart backend")
            logging.info("Backend service restarted")
            # Wait for server to come back up
            time.sleep(5)
            return True
        except Exception as e:
            logging.error(f"Failed to restart backend: {str(e)}")
            return False

    def test_persistence_after_restart(self):
        """Test if the API key persists after server restart"""
        if not self.admin_token:
            logging.error("❌ Cannot test persistence: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Verify Config After Restart",
            "GET",
            "api/admin/gpt-config",
            200,
            token=self.admin_token
        )
        
        if success:
            logging.info(f"GPT config status after restart: {response.get('status', 'unknown')}")
            if 'api_key' in response:
                logging.info(f"API key preview after restart: {response['api_key']}")
            
            # Verify the status is still "configured"
            if response.get('status') == 'configured':
                logging.info("✅ API key persisted after server restart")
                return True, response
            else:
                logging.error(f"❌ API key not persisted, status: {response.get('status')}")
                return False, response
        return False, None

    def test_chat_after_restart(self):
        """Test chat functionality after server restart"""
        # Register a new test user
        timestamp = datetime.now().strftime("%H%M%S")
        employee_data = {
            "name": f"Test Employee After Restart {timestamp}",
            "email": f"employee_restart{timestamp}@test.com",
            "password": "test123",
            "role": "employee"
        }
        
        success, response = self.run_test(
            "Employee Registration After Restart",
            "POST",
            "api/auth/register",
            200,
            data=employee_data
        )
        
        if not success or 'access_token' not in response:
            logging.error("❌ Failed to register test employee after restart")
            return False, None
        
        employee_token = response['access_token']
        employee_id = response['user']['id']
        
        # Test chat with AI after restart
        success, response = self.run_test(
            "Chat with CareAI After Restart",
            "POST",
            "api/chat",
            200,
            data={"message": "I need help with my work-life balance", "user_id": employee_id},
            token=employee_token
        )
        
        if success:
            ai_response = response.get('response', '')
            logging.info(f"AI Response After Restart: {ai_response[:100]}...")
            
            # Check if we got a meaningful response
            if len(ai_response) > 20:
                logging.info("✅ Received meaningful AI response after restart")
                return True, response
            else:
                logging.error("❌ AI response after restart too short or empty")
                return False, response
        return False, None

def test_openai_api_key_persistence():
    """Test the OpenAI API key persistence workflow"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    logging.info(f"Testing OpenAI API key persistence at: {backend_url}")
    tester = OpenAIConfigTester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test admin initialization and login
    tester.test_init_admin()
    admin_login_success = tester.test_admin_login()
    if not admin_login_success:
        logging.error("❌ Admin login failed, stopping tests")
        return 1
    
    # Step 1: Check initial OpenAI configuration status
    logging.info("\n===== STEP 1: Check Initial OpenAI Configuration Status =====")
    initial_config_success, initial_config = tester.test_get_initial_config()
    if not initial_config_success:
        logging.error("❌ Failed to get initial configuration")
    
    # Step 2: Save a new API key through admin dashboard
    logging.info("\n===== STEP 2: Save New API Key =====")
    save_config_success, save_config = tester.test_save_new_config()
    if not save_config_success:
        logging.error("❌ Failed to save new API key")
        return 1
    
    # Step 3: Verify the API key was saved correctly
    logging.info("\n===== STEP 3: Verify API Key Was Saved Correctly =====")
    verify_config_success, verify_config = tester.test_verify_saved_config()
    if not verify_config_success:
        logging.error("❌ Failed to verify saved API key")
        return 1
    
    # Step 4: Test the chat functionality with the new key
    logging.info("\n===== STEP 4: Test Chat Functionality With New Key =====")
    chat_success, chat_response = tester.test_chat_functionality()
    if not chat_success:
        logging.error("❌ Failed to test chat functionality")
        return 1
    
    # Step 5: Use the new test endpoint to verify configuration
    logging.info("\n===== STEP 5: Test New Configuration Endpoint =====")
    test_endpoint_success, test_endpoint = tester.test_config_endpoint()
    if not test_endpoint_success:
        logging.error("❌ Failed to test configuration endpoint")
        return 1
    
    # Step 6: Simulate server restart scenario
    logging.info("\n===== STEP 6: Simulate Server Restart =====")
    restart_success = tester.simulate_server_restart()
    if not restart_success:
        logging.error("❌ Failed to simulate server restart")
        return 1
    
    # Step 7: Verify the API key persistence after restart
    logging.info("\n===== STEP 7: Verify API Key Persistence After Restart =====")
    persistence_success, persistence = tester.test_persistence_after_restart()
    if not persistence_success:
        logging.error("❌ Failed to verify API key persistence after restart")
        return 1
    
    # Step 8: Test chat functionality after restart
    logging.info("\n===== STEP 8: Test Chat Functionality After Restart =====")
    chat_after_restart_success, chat_after_restart = tester.test_chat_after_restart()
    if not chat_after_restart_success:
        logging.error("❌ Failed to test chat functionality after restart")
        return 1
    
    # Print test results
    logging.info("\n" + "="*50)
    logging.info(f"Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    logging.info("="*50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(test_openai_api_key_persistence())
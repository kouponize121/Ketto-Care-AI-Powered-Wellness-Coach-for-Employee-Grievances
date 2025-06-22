import requests
import json
import time
import os
import sys
from datetime import datetime

def test_openai_api_key_persistence():
    """Test the OpenAI API key persistence workflow"""
    backend_url = "https://f260db41-e692-4f6c-aedc-6884036a152a.preview.emergentagent.com"
    print(f"Testing OpenAI API key persistence at: {backend_url}")
    
    # Admin token from previous registration
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiODlkYmNjNzEtZTIyMi00YTllLWI4ZWYtZjZjNjUyYmNlN2I4IiwiZW1haWwiOiJ0ZXN0YWRtaW5AZXhhbXBsZS5jb20iLCJleHAiOjE3NTExOTAwODZ9.RDCyCOxffuVAqDW0ODc6QHvj_43CCKE62r4VfxVwba0"
    
    # Step 1: Check initial OpenAI configuration status
    print("\n===== STEP 1: Check Initial OpenAI Configuration Status =====")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }
    
    response = requests.get(f"{backend_url}/api/admin/gpt-config", headers=headers)
    if response.status_code == 200:
        config = response.json()
        print(f"Initial GPT config status: {config.get('status', 'unknown')}")
        if 'api_key' in config:
            print(f"API key preview: {config['api_key']}")
        print("✅ Successfully retrieved initial configuration")
    else:
        print(f"❌ Failed to get initial configuration: {response.status_code}")
        print(response.text)
        return 1
    
    # Step 2: Test the chat functionality with the existing key
    print("\n===== STEP 2: Test Chat Functionality With Existing Key =====")
    
    # Register a test user
    timestamp = datetime.now().strftime("%H%M%S")
    employee_data = {
        "name": f"Test Employee {timestamp}",
        "email": f"employee{timestamp}@test.com",
        "password": "test123",
        "role": "employee"
    }
    
    response = requests.post(f"{backend_url}/api/auth/register", json=employee_data, headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        print(f"❌ Failed to register test employee: {response.status_code}")
        print(response.text)
        return 1
    
    employee_token = response.json()['access_token']
    employee_id = response.json()['user']['id']
    print(f"✅ Successfully registered test employee: {employee_data['email']}")
    
    # Test chat with AI
    chat_data = {
        "message": "I'm feeling stressed at work",
        "user_id": employee_id
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {employee_token}'
    }
    
    response = requests.post(f"{backend_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to test chat functionality: {response.status_code}")
        print(response.text)
        return 1
    
    ai_response = response.json().get('response', '')
    print(f"AI Response: {ai_response[:100]}...")
    
    # Check if we got a meaningful response
    if len(ai_response) > 20:
        print("✅ Received meaningful AI response")
    else:
        print("❌ AI response too short or empty")
        return 1
    
    # Step 3: Use the test endpoint to verify configuration
    print("\n===== STEP 3: Test Configuration Endpoint =====")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }
    
    response = requests.post(f"{backend_url}/api/admin/test-gpt-config", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to test configuration endpoint: {response.status_code}")
        print(response.text)
        return 1
    
    test_result = response.json()
    print(f"Test result: {test_result.get('message', 'unknown')}")
    print(f"Status: {test_result.get('status', 'unknown')}")
    if 'test_response' in test_result:
        print(f"Test response: {test_result['test_response']}")
    
    # Verify the status is "working"
    if test_result.get('status') == 'working' and test_result.get('success') == True:
        print("✅ API key is working correctly")
    else:
        print(f"❌ API key test failed, status: {test_result.get('status')}")
        return 1
    
    # Step 4: Simulate server restart scenario
    print("\n===== STEP 4: Simulate Server Restart =====")
    try:
        print("Simulating server restart...")
        os.system("sudo supervisorctl restart backend")
        print("Backend service restarted")
        # Wait for server to come back up
        time.sleep(5)
    except Exception as e:
        print(f"Failed to restart backend: {str(e)}")
        return 1
    
    # Step 5: Verify the API key persistence after restart
    print("\n===== STEP 5: Verify API Key Persistence After Restart =====")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }
    
    response = requests.get(f"{backend_url}/api/admin/gpt-config", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to verify API key persistence after restart: {response.status_code}")
        print(response.text)
        return 1
    
    config = response.json()
    print(f"GPT config status after restart: {config.get('status', 'unknown')}")
    if 'api_key' in config:
        print(f"API key preview after restart: {config['api_key']}")
    
    # Verify the status is still "configured"
    if config.get('status') == 'configured':
        print("✅ API key persisted after server restart")
    else:
        print(f"❌ API key not persisted, status: {config.get('status')}")
        return 1
    
    # Step 6: Test chat functionality after restart
    print("\n===== STEP 6: Test Chat Functionality After Restart =====")
    
    # Register a new test user
    timestamp = datetime.now().strftime("%H%M%S")
    employee_data = {
        "name": f"Test Employee After Restart {timestamp}",
        "email": f"employee_restart{timestamp}@test.com",
        "password": "test123",
        "role": "employee"
    }
    
    response = requests.post(f"{backend_url}/api/auth/register", json=employee_data, headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        print(f"❌ Failed to register test employee after restart: {response.status_code}")
        print(response.text)
        return 1
    
    employee_token = response.json()['access_token']
    employee_id = response.json()['user']['id']
    print(f"✅ Successfully registered test employee after restart: {employee_data['email']}")
    
    # Test chat with AI after restart
    chat_data = {
        "message": "I need help with my work-life balance",
        "user_id": employee_id
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {employee_token}'
    }
    
    response = requests.post(f"{backend_url}/api/chat", json=chat_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to test chat functionality after restart: {response.status_code}")
        print(response.text)
        return 1
    
    ai_response = response.json().get('response', '')
    print(f"AI Response After Restart: {ai_response[:100]}...")
    
    # Check if we got a meaningful response
    if len(ai_response) > 20:
        print("✅ Received meaningful AI response after restart")
    else:
        print("❌ AI response after restart too short or empty")
        return 1
    
    # Print test results
    print("\n" + "="*50)
    print("Test Results: All tests passed!")
    print("="*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(test_openai_api_key_persistence())
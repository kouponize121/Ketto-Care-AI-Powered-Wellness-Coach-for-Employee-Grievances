import requests
import json
import base64

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🔍 TESTING USER MANAGEMENT ISSUES")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
if response.status_code == 200:
    admin_data = response.json()
    token = admin_data["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Admin login successful")
    
    # Issue 1: Test CSV upload with simple user
    print("\n📝 ISSUE 1: Testing CSV upload and login...")
    
    csv_content = """name,email,password,role
Test User CSV,csvtest@example.com,testpass123,employee"""
    
    csv_data = {
        "file_content": base64.b64encode(csv_content.encode()).decode()
    }
    
    response = requests.post(f"{base_url}/api/admin/upload-users", json=csv_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ CSV upload successful: {result.get('message', '')}")
        
        # Try to login with the uploaded user
        print("🔐 Testing login with CSV uploaded user...")
        test_login = {"email": "csvtest@example.com", "password": "testpass123"}
        response = requests.post(f"{base_url}/api/auth/login", json=test_login)
        
        if response.status_code == 200:
            print("✅ CSV uploaded user can login successfully!")
        else:
            print(f"❌ CSV uploaded user cannot login: {response.status_code}")
            print(f"Response: {response.text}")
            
    else:
        print(f"❌ CSV upload failed: {response.status_code}")
        print(f"Error: {response.text}")
    
    # Issue 2: Test user update
    print(f"\n👤 ISSUE 2: Testing user update...")
    
    # Get list of users first
    response = requests.get(f"{base_url}/api/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        if users:
            # Find a non-admin user to update
            test_user = None
            for user in users:
                if user['role'] == 'employee':
                    test_user = user
                    break
            
            if test_user:
                print(f"📝 Testing update for user: {test_user['name']} ({test_user['email']})")
                
                # Try to update the user
                update_data = {
                    "name": test_user['name'] + " Updated",
                    "designation": "Updated Designation",
                    "password": "newpassword123"
                }
                
                response = requests.put(f"{base_url}/api/admin/users/{test_user['id']}", json=update_data, headers=headers)
                
                if response.status_code == 200:
                    print("✅ User update successful!")
                    
                    # Test login with new password
                    print("🔐 Testing login with updated password...")
                    updated_login = {"email": test_user['email'], "password": "newpassword123"}
                    response = requests.post(f"{base_url}/api/auth/login", json=updated_login)
                    
                    if response.status_code == 200:
                        print("✅ Updated user can login with new password!")
                    else:
                        print(f"❌ Updated user cannot login: {response.status_code}")
                        print(f"Response: {response.text}")
                        
                else:
                    print(f"❌ User update failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("❌ No employee users found to test update")
        else:
            print("❌ No users found")
    else:
        print(f"❌ Failed to get users: {response.status_code}")
        
else:
    print(f"❌ Admin login failed: {response.text}")

print("\n" + "="*60)
print("ISSUE DIAGNOSIS COMPLETE")
print("="*60)
print("Issues to check:")
print("1. CSV uploaded users login issues")
print("2. User update 'ticket not found' error")
print("3. Password reset functionality")

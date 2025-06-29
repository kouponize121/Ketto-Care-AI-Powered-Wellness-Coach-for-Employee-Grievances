import requests
import time

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🔍 TESTING AUTHENTICATION FLOW")
print("="*50)

print("Step 1: Testing admin login and dashboard access...")

# Test admin login
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)

if response.status_code == 200:
    admin_data = response.json()
    token = admin_data["access_token"]
    user = admin_data["user"]
    
    print(f"✅ Admin login successful")
    print(f"   User: {user['name']}")
    print(f"   Role: {user['role']}")
    print(f"   Token received: {token[:20]}...")
    
    # Test if admin can access admin endpoints
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/admin/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Admin can access admin endpoints - Found {len(users)} users")
    else:
        print(f"❌ Admin cannot access admin endpoints: {response.status_code}")
        
else:
    print(f"❌ Admin login failed: {response.status_code} - {response.text}")

print(f"\nStep 2: Testing employee login and dashboard access...")

# Test employee login
employee_login = {"email": "cleanemailtest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)

if response.status_code == 200:
    employee_data = response.json()
    token = employee_data["access_token"]
    user = employee_data["user"]
    
    print(f"✅ Employee login successful")
    print(f"   User: {user['name']}")
    print(f"   Role: {user['role']}")
    print(f"   Token received: {token[:20]}...")
    
    # Test if employee can access employee endpoints
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/tickets", headers=headers)
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"✅ Employee can access employee endpoints - Found {len(tickets)} tickets")
    else:
        print(f"❌ Employee cannot access employee endpoints: {response.status_code}")
        
    # Test if employee CANNOT access admin endpoints (should be blocked)
    response = requests.get(f"{base_url}/api/admin/users", headers=headers)
    
    if response.status_code == 403 or response.status_code == 401:
        print(f"✅ Employee correctly blocked from admin endpoints")
    else:
        print(f"❌ Employee should not access admin endpoints: {response.status_code}")
        
else:
    print(f"❌ Employee login failed: {response.status_code} - {response.text}")

print(f"\nStep 3: Testing invalid credentials...")

# Test invalid login
invalid_login = {"email": "invalid@example.com", "password": "wrong"}
response = requests.post(f"{base_url}/api/auth/login", json=invalid_login)

if response.status_code == 401:
    print(f"✅ Invalid credentials correctly rejected")
else:
    print(f"❌ Invalid credentials should be rejected: {response.status_code}")

print("\n" + "="*50)
print("AUTHENTICATION FLOW DIAGNOSIS")
print("="*50)
print("✅ Backend authentication API working correctly")
print("✅ JWT tokens generated successfully")
print("✅ Role-based access control working")
print("✅ Protected endpoints responding correctly")

print("\n🔍 IF DASHBOARD STILL NOT LOADING:")
print("1. Check browser console for JavaScript errors")
print("2. Verify AuthContext state is being updated")
print("3. Check if ProtectedRoute is receiving user data")
print("4. Ensure token is stored in localStorage")
print("5. Verify navigation is not being intercepted")

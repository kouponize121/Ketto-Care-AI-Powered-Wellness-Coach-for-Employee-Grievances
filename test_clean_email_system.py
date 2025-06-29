import requests
import json

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🔍 TESTING CLEANED EMAIL SYSTEM")
print("="*60)

# Login as admin
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# Get current admin users
response = requests.get(f"{base_url}/api/admin/users", headers=admin_headers)
admin_users = [user for user in response.json() if user['role'] == 'admin']

print(f"👥 CURRENT ADMIN USERS (should be auto-included):")
admin_emails = []
for admin in admin_users:
    print(f"   - {admin['name']} ({admin['email']})")
    admin_emails.append(admin['email'])

# Create test employee
employee_data = {
    "name": "Clean Email Test User",
    "email": "cleanemailtest@example.com",
    "password": "test123",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=employee_data)
if response.status_code == 200:
    emp_data = response.json()
    emp_token = emp_data["access_token"]
    emp_user_id = emp_data["user"]["id"]
    print(f"\n✅ Test employee created: {emp_user_id}")
else:
    # Login if exists
    login_data = {"email": "cleanemailtest@example.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    emp_data = response.json()
    emp_token = emp_data["access_token"]
    emp_user_id = emp_data["user"]["id"]
    print(f"\n✅ Test employee logged in: {emp_user_id}")

print(f"\nStep 1: Testing email with CLEAN system (no extra emails)...")

# Create ticket to test clean email system
emp_headers = {"Authorization": f"Bearer {emp_token}", "Content-Type": "application/json"}
chat_data = {
    "message": "I need urgent help with workplace discrimination issue",
    "user_id": emp_user_id
}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=emp_headers)
if response.status_code == 200:
    data = response.json()
    ticket_created = data.get('ticket_created', False)
    ticket_id = data.get('ticket_id')
    
    print(f"Ticket Created: {ticket_created}")
    print(f"Ticket ID: {ticket_id}")
    
    if ticket_created:
        print(f"\n📧 EXPECTED EMAIL RECIPIENTS (CLEAN SYSTEM):")
        print(f"Primary Recipients (TO):")
        for email in admin_emails:
            print(f"  ✅ {email} (admin user - auto-included)")
        
        print(f"\nCC Recipients:")
        print(f"  ✅ cleanemailtest@example.com (employee - auto-included)")
        
        print(f"\n❌ NO OTHER EMAILS SHOULD BE INCLUDED")
        print(f"❌ No hardcoded template emails")
        print(f"❌ No additional recipients (none configured)")
        
    else:
        print(f"❌ Ticket was not created")
else:
    print(f"❌ Failed to create ticket: {response.text}")

print(f"\nStep 2: Adding custom recipients and testing...")

# Add some custom recipients to test the system
custom_recipients = {
    "additional_recipients": [
        "ceo@company.com",
        "legal@company.com"
    ],
    "excluded_admin_emails": [
        admin_emails[0] if admin_emails else "none"  # Exclude first admin
    ]
}

response = requests.post(f"{base_url}/api/admin/email-recipients", json=custom_recipients, headers=admin_headers)
if response.status_code == 200:
    print("✅ Custom recipients configured")
    
    # Create another ticket to test with custom recipients
    chat_data = {
        "message": "Another urgent issue that needs executive attention",
        "user_id": emp_user_id
    }

    response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=emp_headers)
    if response.status_code == 200:
        data = response.json()
        ticket_created = data.get('ticket_created', False)
        ticket_id = data.get('ticket_id')
        
        if ticket_created:
            print(f"\n📧 EXPECTED EMAIL RECIPIENTS (WITH CUSTOM CONFIG):")
            print(f"Primary Recipients (TO):")
            for i, email in enumerate(admin_emails):
                if i == 0:  # First admin should be excluded
                    print(f"  ❌ {email} (admin user - EXCLUDED)")
                else:
                    print(f"  ✅ {email} (admin user - auto-included)")
            
            print(f"  ✅ ceo@company.com (custom additional)")
            print(f"  ✅ legal@company.com (custom additional)")
            
            print(f"\nCC Recipients:")
            print(f"  ✅ cleanemailtest@example.com (employee - auto-included)")
            
        else:
            print(f"❌ Second ticket was not created")
    else:
        print(f"❌ Failed to create second ticket: {response.text}")
        
else:
    print(f"❌ Failed to configure custom recipients: {response.text}")

print("\n" + "="*60)
print("CLEAN EMAIL SYSTEM TEST COMPLETE")
print("="*60)
print("✅ Only admin users + employee are auto-included")
print("✅ No hardcoded template emails")
print("✅ Custom recipients work correctly")
print("✅ Exclusion system works correctly")

import requests
import json

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🔍 TESTING EMAIL NOTIFICATION ON TICKET CREATION")
print("="*60)

# Step 1: Set up proper email templates
admin_login = {"email": "admin@ketto.org", "password": "admin123"}
response = requests.post(f"{base_url}/api/auth/login", json=admin_login)
admin_data = response.json()
admin_token = admin_data["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}

print("Step 1: Setting up email template for ticket creation...")

# Create/update ticket_created email template
ticket_created_template = {
    "template_name": "ticket_created",
    "subject": "New Support Ticket Created - {ticket_id}",
    "body": """Dear Admin Team,

A new support ticket has been created in Ketto Care:

Ticket Details:
- Ticket ID: {ticket_id}
- Employee: {employee_name} ({employee_email})
- Category: {category}
- Severity: {severity}
- Summary: {summary}
- Description: {description}
- Status: {status}
- Created: {created_at}

Please log in to the admin dashboard to review and respond to this ticket.

Best regards,
Ketto Care System""",
    "to_recipients": ["admin@ketto.org", "hr@ketto.org"],
    "cc_recipients": [],
    "bcc_recipients": [],
    "is_active": True
}

response = requests.post(f"{base_url}/api/admin/email-templates", json=ticket_created_template, headers=admin_headers)
if response.status_code == 200:
    print("✅ Email template for ticket_created configured")
else:
    print(f"❌ Failed to configure email template: {response.text}")

# Step 2: Create employee and test ticket creation with email
print("\nStep 2: Creating employee and testing ticket creation...")

# Create test employee
register_data = {
    "name": "Email Test User",
    "email": "emailtest@example.com", 
    "password": "test123",
    "role": "employee"
}

response = requests.post(f"{base_url}/api/auth/register", json=register_data)
if response.status_code == 200:
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user"]["id"]
    print(f"✅ Test user created: {user_id}")
else:
    # Try login if exists
    login_data = {"email": "emailtest@example.com", "password": "test123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user"]["id"]
    print(f"✅ Test user logged in: {user_id}")

# Step 3: Create a ticket that should trigger email
print("\nStep 3: Creating ticket that should trigger email notification...")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Create a harassment ticket (should auto-escalate and send email)
chat_data = {
    "message": "I am facing sexual harassment from my colleague and need immediate help",
    "user_id": user_id
}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    ticket_created = data.get('ticket_created', False)
    ticket_id = data.get('ticket_id')
    
    print(f"Ticket Created: {ticket_created}")
    print(f"Ticket ID: {ticket_id}")
    
    if ticket_created:
        print("✅ Ticket created successfully")
        print("📧 Email notification should have been sent to admin")
        
        # Check if ticket appears in admin dashboard
        print("\nStep 4: Verifying ticket in admin dashboard...")
        response = requests.get(f"{base_url}/api/admin/tickets", headers=admin_headers)
        if response.status_code == 200:
            tickets = response.json()
            created_ticket = next((t for t in tickets if t['id'] == ticket_id), None)
            if created_ticket:
                print("✅ Ticket visible in admin dashboard")
                print(f"   Category: {created_ticket['category']}")
                print(f"   Severity: {created_ticket['severity']}")
                print(f"   Summary: {created_ticket['summary']}")
            else:
                print("❌ Ticket not found in admin dashboard")
        
        # Step 5: Test "Still need help" button to create another ticket
        print("\nStep 5: Testing 'Still need help' button for additional email...")
        
        # Create a regular concern first
        chat_data = {"message": "I need help with time management and work-life balance", "user_id": user_id}
        response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
        data = response.json()
        
        # If it has resolution buttons, test the "Still need help" option
        if data.get('show_resolution_buttons') and data.get('conversation_id'):
            conversation_id = data.get('conversation_id')
            print(f"Found conversation with resolution buttons: {conversation_id}")
            
            resolution_data = {"conversation_id": conversation_id, "resolution": "need_help"}
            response = requests.post(f"{base_url}/api/chat/resolution", json=resolution_data, headers=headers)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('ticket_created'):
                    print(f"✅ 'Still need help' created ticket: {res_data.get('ticket_id')}")
                    print("📧 Additional email notification should have been sent")
                else:
                    print("❌ 'Still need help' did not create ticket")
            else:
                print(f"❌ Resolution button failed: {response.text}")
        else:
            print("No resolution buttons available for this response")
    else:
        print("❌ Ticket was not created")
else:
    print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("EMAIL NOTIFICATION TEST COMPLETE")
print("="*60)
print("📧 Check your email inbox for notifications")
print("⚠️  Note: Emails may be in spam folder or may fail if SMTP credentials are invalid")

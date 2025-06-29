import requests
import json

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🔍 TESTING INVESTIGATIVE CAREAI (Fixed)")
print("="*60)

# Login as employee
employee_login = {"email": "cleanemailtest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)
if response.status_code == 200:
    employee_data = response.json()
    token = employee_data["access_token"]
    user_id = employee_data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Employee login successful")
    
    # Test vague scenarios that require investigation
    test_scenarios = [
        {
            "name": "Vague Health Issue",
            "message": "I'm not feeling good"
        },
        {
            "name": "General Stress",
            "message": "I'm feeling stressed"
        },
        {
            "name": "Workplace Issue",
            "message": "I'm having problems at work"
        },
        {
            "name": "Manager Mention",
            "message": "My manager is difficult"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
        print(f"Employee: {scenario['message']}")
        
        chat_data = {
            "message": scenario['message'],
            "user_id": user_id
        }
        
        response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            show_buttons = data.get('show_resolution_buttons', False)
            ticket_created = data.get('ticket_created', False)
            
            print(f"CareAI: {ai_response}")
            
            # Check for investigation qualities
            has_empathy = any(phrase in ai_response.lower() for phrase in ['sorry', 'understand', 'tough', 'difficult'])
            asks_questions = '?' in ai_response
            investigates = any(phrase in ai_response.lower() for phrase in ['can you share', 'what', 'how', 'tell me more', 'what\'s'])
            shows_markers = any(marker in ai_response for marker in ['EMPATHETIC', 'CONFIDENT', 'EMPOWERING'])
            suggests_external = any(phrase in ai_response.lower() for phrase in ['healthcare provider', 'contact hr', 'reach out to'])
            
            print(f"\n🔍 Investigation Analysis:")
            print(f"  - Shows empathy: {'✅' if has_empathy else '❌'}")
            print(f"  - Asks clarifying questions: {'✅' if asks_questions else '❌'}")
            print(f"  - Investigates situation: {'✅' if investigates else '❌'}")
            print(f"  - No internal markers: {'✅' if not shows_markers else '❌ SHOWS MARKERS!'}")
            print(f"  - Doesn't suggest external help: {'✅' if not suggests_external else '❌ SUGGESTS EXTERNAL'}")
            print(f"  - Resolution buttons: {show_buttons}")
            print(f"  - Ticket created: {ticket_created}")
            
            # Overall assessment
            investigation_score = sum([has_empathy, asks_questions, investigates, not shows_markers, not suggests_external])
            if investigation_score >= 4:
                print(f"  🌟 EXCELLENT: Proper investigative mental wellness support!")
            elif investigation_score >= 3:
                print(f"  ✅ GOOD: Generally supportive but needs improvement")
            else:
                print(f"  ❌ POOR: Still not investigative enough")
                
        else:
            print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("🎯 INVESTIGATIVE CAREAI REQUIREMENTS")
print("="*60)
print("✅ Must ask questions to understand the situation")
print("✅ Must be empathetic and validating")
print("✅ Must NOT show internal formatting markers")
print("✅ Must NOT immediately suggest external help")
print("✅ Must be curious and caring")
print("✅ Must investigate before providing solutions")

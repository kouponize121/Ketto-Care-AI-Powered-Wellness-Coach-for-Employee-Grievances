import requests
import json

base_url = "https://cfe17b23-6636-463b-a02a-fcb4a5219b29.preview.emergentagent.com"

print("🎯 TESTING QUICK SOLUTION-FOCUSED CAREAI")
print("="*60)

# Login as employee
employee_login = {"email": "cleanemailtest@example.com", "password": "test123"}
response = requests.post(f"{base_url}/api/auth/login", json=employee_login)
employee_data = response.json()
token = employee_data["access_token"]
user_id = employee_data["user"]["id"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("✅ Employee login successful")

# Test the problematic scenario from user's example
print("\n🔄 Testing the exact scenario that was problematic...")

# Message that should get solutions, not more questions
message = "he is not providing guidance on solving my performance issue I tried talking to him but he never provide solution"

print(f"Employee: {message}")

chat_data = {
    "message": message,
    "user_id": user_id
}

response = requests.post(f"{base_url}/api/chat", json=chat_data, headers=headers)
if response.status_code == 200:
    data = response.json()
    ai_response = data.get('response', '')
    show_buttons = data.get('show_resolution_buttons', False)
    
    print(f"CareAI: {ai_response}")
    
    # Analyze if it provides solutions
    has_numbered_solutions = any(num in ai_response for num in ['1.', '2.', '3.', '4.'])
    has_solution_words = any(word in ai_response.lower() for word in ['here are', 'here\'s what', 'you can', 'steps'])
    asks_more_questions = any(phrase in ai_response.lower() for phrase in ['can you share', 'tell me more', 'what specifically'])
    question_count = ai_response.count('?')
    
    print(f"\n📊 Analysis:")
    print(f"  - Provides numbered solutions: {'✅' if has_numbered_solutions else '❌'}")
    print(f"  - Uses solution language: {'✅' if has_solution_words else '❌'}")
    print(f"  - Asks for more details: {'❌' if not asks_more_questions else '✅ (BAD)'}")
    print(f"  - Number of questions: {question_count} {'✅' if question_count <= 1 else '❌ (TOO MANY)'}")
    print(f"  - Resolution buttons shown: {'✅' if show_buttons else '❌'}")
    
    # Overall assessment
    if has_numbered_solutions and not asks_more_questions:
        print(f"  🌟 EXCELLENT: Provides solutions without asking more questions!")
    elif has_solution_words and question_count <= 1:
        print(f"  ✅ GOOD: Provides some guidance")
    else:
        print(f"  ❌ STILL PROBLEMATIC: Asking questions instead of providing solutions")
        
else:
    print(f"❌ Chat failed: {response.text}")

print("\n" + "="*60)
print("🎯 EXPECTED BEHAVIOR")
print("="*60)
print("When user says:")
print("'he is not providing guidance on solving my performance issue I tried talking to him but he never provide solution'")
print()
print("CareAI should respond with:")
print("✅ Empathy: 'That's frustrating when you need guidance...'")
print("✅ Solutions: '1. Send email requesting specific feedback'")
print("✅ Solutions: '2. Ask for written development plan'") 
print("✅ Solutions: '3. Request regular check-ins'")
print("✅ Solutions: '4. Escalate to HR if unresponsive'")
print("✅ Max 1 follow-up question (optional)")
print()
print("❌ Should NOT ask for more details about what already explained")

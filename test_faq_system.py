import requests
import json
import time
import base64
import csv
import io
import os
from datetime import datetime

class KettoCareAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.employee_token = None
        self.employee_id = None
        self.test_ticket_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, admin=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        elif admin and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
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
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test basic API connectivity"""
        return self.run_test("API Root", "GET", "api", 200)

    def test_employee_registration(self):
        """Test employee registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        employee_data = {
            "name": f"Test Employee {timestamp}",
            "email": f"employee{timestamp}@test.com",
            "password": "test123",
            "role": "employee",
            "designation": "Software Engineer",
            "business_unit": "Engineering",
            "reporting_manager": "John Doe"
        }
        
        success, response = self.run_test(
            "Employee Registration",
            "POST",
            "api/auth/register",
            200,
            data=employee_data
        )
        
        if success and 'access_token' in response:
            self.employee_token = response['access_token']
            self.employee_id = response['user']['id']
            print(f"Employee registration successful, token obtained")
            return True, employee_data
        return False, None

    def test_employee_login(self, email, password="test123"):
        """Test employee login"""
        success, response = self.run_test(
            "Employee Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"Employee login successful, token obtained")
            return True
        return False

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
            print(f"Admin login successful, token obtained")
            return True
        return False

    def test_admin_get_tickets(self):
        """Test admin getting all tickets"""
        if not self.admin_token:
            print("❌ Cannot test admin tickets: No admin token")
            return False, None
            
        success, response = self.run_test(
            "Admin Get All Tickets",
            "GET",
            "api/admin/tickets",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"Admin retrieved {len(response)} tickets")
            return True, response
        return False, None

def test_faq_system():
    """Test the FAQ system backend functionality"""
    backend_url = "http://localhost:8001"
    print(f"Testing FAQ system at: {backend_url}")
    tester = KettoCareAPITester(backend_url)
    
    # Test basic connectivity
    tester.test_api_root()
    
    # Test employee registration and login
    reg_success, employee_data = tester.test_employee_registration()
    if not reg_success:
        print("❌ Employee registration failed, trying to login with existing employee")
        login_success = tester.test_employee_login("employee@example.com", "password123")
        if not login_success:
            print("❌ Could not login with existing employee, creating a new one")
            reg_success, employee_data = tester.test_employee_registration()
            if not reg_success:
                print("❌ Failed to create employee account, stopping tests")
                return False
            login_success = tester.test_employee_login(employee_data["email"])
            if not login_success:
                print("❌ Failed to login with new employee account, stopping tests")
                return False
    else:
        login_success = tester.test_employee_login(employee_data["email"])
        if not login_success:
            print("❌ Failed to login with new employee account, stopping tests")
            return False
    
    # Test admin login for checking tickets later
    admin_login_success = tester.test_admin_login()
    
    # Test 1: Get FAQ Questions
    print("\n🔍 Testing GET /api/faq/questions endpoint")
    success, questions_response = tester.run_test(
        "Get FAQ Questions",
        "GET",
        "api/faq/questions",
        200,
        token=tester.token
    )
    
    if success and 'questions' in questions_response:
        questions = questions_response['questions']
        print(f"✅ Retrieved {len(questions)} FAQ questions")
        
        # Verify we have all 8 predefined questions
        expected_question_ids = [
            "payslip_request", "incentive_pending", "shift_extension", 
            "admin_issue", "attendance_query", "no_break", 
            "parking_issue", "misbehaviour"
        ]
        
        found_ids = [q['id'] for q in questions]
        missing_ids = [qid for qid in expected_question_ids if qid not in found_ids]
        
        if not missing_ids and len(questions) == 8:
            print("✅ All 8 predefined questions found")
        else:
            print(f"❌ Missing questions: {missing_ids}")
            return False
        
        # Verify question structure
        for question in questions:
            if not all(key in question for key in ['id', 'title', 'description']):
                print(f"❌ Question missing required fields: {question}")
                return False
        
        print("✅ All questions have proper structure (id, title, description)")
    else:
        print("❌ Failed to retrieve FAQ questions")
        return False
    
    # Test 2: FAQ Processing - Payslip Request without additional_info
    print("\n🔍 Testing payslip_request without additional_info")
    success, response = tester.run_test(
        "Payslip Request without additional_info",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "payslip_request",
            "user_id": tester.employee_id,
            "additional_info": None
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if requires_followup and not ticket_created:
            print("✅ Payslip request without additional_info correctly requires followup")
        else:
            print("❌ Payslip request without additional_info should require followup and not create ticket")
            return False
    else:
        print("❌ Failed to test payslip_request without additional_info")
        return False
    
    # Test 3: FAQ Processing - Payslip Request with additional_info
    print("\n🔍 Testing payslip_request with additional_info")
    success, response = tester.run_test(
        "Payslip Request with additional_info",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "payslip_request",
            "user_id": tester.employee_id,
            "additional_info": "April 2023"
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if not requires_followup and ticket_created and ticket_id:
            print("✅ Payslip request with additional_info correctly creates ticket")
            
            # Save ticket ID for admin verification
            payslip_ticket_id = ticket_id
        else:
            print("❌ Payslip request with additional_info should create ticket and not require followup")
            return False
    else:
        print("❌ Failed to test payslip_request with additional_info")
        return False
    
    # Test 4: FAQ Processing - Incentive Pending without additional_info
    print("\n🔍 Testing incentive_pending without additional_info")
    success, response = tester.run_test(
        "Incentive Pending without additional_info",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "incentive_pending",
            "user_id": tester.employee_id,
            "additional_info": None
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if requires_followup and not ticket_created:
            print("✅ Incentive pending without additional_info correctly requires followup")
        else:
            print("❌ Incentive pending without additional_info should require followup and not create ticket")
            return False
    else:
        print("❌ Failed to test incentive_pending without additional_info")
        return False
    
    # Test 5: FAQ Processing - Misbehaviour (should create ticket immediately)
    print("\n🔍 Testing misbehaviour (should create critical ticket immediately)")
    success, response = tester.run_test(
        "Misbehaviour",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "misbehaviour",
            "user_id": tester.employee_id,
            "additional_info": "My colleague is being rude to me"
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if not requires_followup and ticket_created and ticket_id:
            print("✅ Misbehaviour correctly creates ticket immediately")
            
            # Save ticket ID for admin verification
            misbehaviour_ticket_id = ticket_id
        else:
            print("❌ Misbehaviour should create ticket immediately and not require followup")
            return False
    else:
        print("❌ Failed to test misbehaviour")
        return False
    
    # Test 6: FAQ Processing - No Break with "today" in additional_info
    print("\n🔍 Testing no_break with 'today' in additional_info")
    success, response = tester.run_test(
        "No Break with today",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "no_break",
            "user_id": tester.employee_id,
            "additional_info": "I didn't get a break today"
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if not requires_followup and ticket_created and ticket_id:
            print("✅ No break with 'today' correctly creates high priority ticket")
            
            # Save ticket ID for admin verification
            no_break_ticket_id = ticket_id
        else:
            print("❌ No break with 'today' should create ticket and not require followup")
            return False
    else:
        print("❌ Failed to test no_break with 'today'")
        return False
    
    # Test 7: FAQ Processing - Shift Extension with productive hours
    print("\n🔍 Testing shift_extension with productive hours")
    success, response = tester.run_test(
        "Shift Extension with hours",
        "POST",
        "api/faq",
        200,
        data={
            "question_type": "shift_extension",
            "user_id": tester.employee_id,
            "additional_info": "9.5 hours"
        },
        token=tester.token
    )
    
    if success:
        requires_followup = response.get('requires_followup', False)
        ticket_created = response.get('ticket_created', False)
        ticket_id = response.get('ticket_id')
        
        print(f"Response: {response.get('response', '')[:100]}...")
        print(f"Requires followup: {requires_followup}")
        print(f"Ticket created: {ticket_created}")
        
        if not requires_followup and ticket_created and ticket_id:
            print("✅ Shift extension with hours > 8 correctly creates ticket")
            
            # Save ticket ID for admin verification
            shift_extension_ticket_id = ticket_id
        else:
            print("❌ Shift extension with hours > 8 should create ticket and not require followup")
            return False
    else:
        print("❌ Failed to test shift_extension with hours")
        return False
    
    # Verify tickets as admin
    if admin_login_success:
        print("\n🔍 Verifying created tickets as admin")
        success, admin_tickets = tester.test_admin_get_tickets()
        
        if success:
            # Check payslip ticket
            payslip_ticket = next((t for t in admin_tickets if t['id'] == payslip_ticket_id), None)
            if payslip_ticket:
                print(f"✅ Found payslip ticket: {payslip_ticket['id']}")
                if payslip_ticket['category'] == 'request' and payslip_ticket['severity'] == 'low':
                    print("✅ Payslip ticket has correct category (request) and severity (low)")
                else:
                    print(f"❌ Payslip ticket has incorrect category or severity: {payslip_ticket['category']}, {payslip_ticket['severity']}")
            else:
                print("❌ Could not find payslip ticket")
            
            # Check misbehaviour ticket
            misbehaviour_ticket = next((t for t in admin_tickets if t['id'] == misbehaviour_ticket_id), None)
            if misbehaviour_ticket:
                print(f"✅ Found misbehaviour ticket: {misbehaviour_ticket['id']}")
                if misbehaviour_ticket['category'] == 'grievance' and misbehaviour_ticket['severity'] == 'critical':
                    print("✅ Misbehaviour ticket has correct category (grievance) and severity (critical)")
                else:
                    print(f"❌ Misbehaviour ticket has incorrect category or severity: {misbehaviour_ticket['category']}, {misbehaviour_ticket['severity']}")
            else:
                print("❌ Could not find misbehaviour ticket")
            
            # Check no break ticket
            no_break_ticket = next((t for t in admin_tickets if t['id'] == no_break_ticket_id), None)
            if no_break_ticket:
                print(f"✅ Found no break ticket: {no_break_ticket['id']}")
                if no_break_ticket['category'] == 'grievance' and no_break_ticket['severity'] == 'high':
                    print("✅ No break ticket has correct category (grievance) and severity (high)")
                else:
                    print(f"❌ No break ticket has incorrect category or severity: {no_break_ticket['category']}, {no_break_ticket['severity']}")
            else:
                print("❌ Could not find no break ticket")
        else:
            print("❌ Failed to get admin tickets for verification")
    
    print("\n✅ All FAQ system tests completed successfully")
    return True

if __name__ == "__main__":
    print("\n===== TESTING FAQ SYSTEM =====\n")
    result = test_faq_system()
    print("\nTest Result: " + ("✅ PASSED" if result else "❌ FAILED"))
#!/usr/bin/env python3
"""
Login System Test for Diogenes Travel Panel
Tests the POST /api/login endpoint with various scenarios
"""

import requests
import json
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://travel-booking-hub-8.preview.emergentagent.com/api"

class LoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")

    def test_initialize_users(self):
        """Test POST /api/users/init to ensure default users exist"""
        try:
            response = self.session.post(f"{BACKEND_URL}/users/init", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_test("Initialize Users", True, f"Users initialization: {data['message']}", data)
                else:
                    self.log_test("Initialize Users", False, f"Invalid response format: {data}", data)
            else:
                self.log_test("Initialize Users", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Initialize Users", False, f"Error: {str(e)}")

    def test_login_success_admin(self):
        """Test POST /api/login with correct admin credentials"""
        try:
            login_data = {
                "email": "admin@diogenes.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['id', 'name', 'email', 'role', 'status', 'created_at']
                if all(field in data for field in expected_fields):
                    if data['email'] == 'admin@diogenes.com' and data['role'] == 'admin' and data['status'] == 'active':
                        self.log_test("Login Success - Admin", True, f"Admin login successful: {data['name']} ({data['role']})", data)
                        return data  # Return user data for further tests
                    else:
                        self.log_test("Login Success - Admin", False, f"Incorrect user data returned: {data}", data)
                else:
                    self.log_test("Login Success - Admin", False, f"Missing required fields in response: {data}", data)
            else:
                self.log_test("Login Success - Admin", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login Success - Admin", False, f"Error: {str(e)}")
        return None

    def test_login_wrong_password(self):
        """Test POST /api/login with wrong password"""
        try:
            login_data = {
                "email": "admin@diogenes.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
            if response.status_code == 401:
                data = response.json()
                if 'detail' in data and 'Email veya şifre hatalı' in data['detail']:
                    self.log_test("Login Wrong Password", True, "Correctly rejected wrong password with 401", data)
                else:
                    self.log_test("Login Wrong Password", False, f"Wrong error message: {data}", data)
            else:
                self.log_test("Login Wrong Password", False, f"Expected 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login Wrong Password", False, f"Error: {str(e)}")

    def test_login_nonexistent_email(self):
        """Test POST /api/login with non-existent email"""
        try:
            login_data = {
                "email": "nonexistent@diogenes.com",
                "password": "anypassword"
            }
            
            response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
            if response.status_code == 401:
                data = response.json()
                if 'detail' in data and 'Email veya şifre hatalı' in data['detail']:
                    self.log_test("Login Nonexistent Email", True, "Correctly rejected non-existent email with 401", data)
                else:
                    self.log_test("Login Nonexistent Email", False, f"Wrong error message: {data}", data)
            else:
                self.log_test("Login Nonexistent Email", False, f"Expected 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login Nonexistent Email", False, f"Error: {str(e)}")

    def test_login_empty_credentials(self):
        """Test POST /api/login with empty email and password"""
        try:
            login_data = {
                "email": "",
                "password": ""
            }
            
            response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
            if response.status_code == 401:
                data = response.json()
                if 'detail' in data and 'Email veya şifre hatalı' in data['detail']:
                    self.log_test("Login Empty Credentials", True, "Correctly rejected empty credentials with 401", data)
                else:
                    self.log_test("Login Empty Credentials", False, f"Wrong error message: {data}", data)
            else:
                self.log_test("Login Empty Credentials", False, f"Expected 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login Empty Credentials", False, f"Error: {str(e)}")

    def test_login_all_users(self):
        """Test login for all default users"""
        test_users = [
            {"email": "reservation@diogenes.com", "password": "reservation123", "role": "reservation", "name": "Rezervasyon Manager"},
            {"email": "operation@diogenes.com", "password": "operation123", "role": "operation", "name": "Operasyon Manager"},
            {"email": "flight@diogenes.com", "password": "flight123", "role": "flight", "name": "Uçak Manager"},
            {"email": "management@diogenes.com", "password": "management123", "role": "management", "name": "Yönetim Manager"}
        ]
        
        for user in test_users:
            try:
                login_data = {
                    "email": user["email"],
                    "password": user["password"]
                }
                
                response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ['id', 'name', 'email', 'role', 'status', 'created_at']
                    if all(field in data for field in expected_fields):
                        if (data['email'] == user["email"] and 
                            data['role'] == user["role"] and 
                            data['status'] == 'active'):
                            self.log_test(f"Login Success - {user['role'].title()}", True, 
                                        f"{user['role'].title()} login successful: {data['name']} ({data['role']})", data)
                        else:
                            self.log_test(f"Login Success - {user['role'].title()}", False, 
                                        f"Incorrect user data for {user['email']}: {data}", data)
                    else:
                        self.log_test(f"Login Success - {user['role'].title()}", False, 
                                    f"Missing required fields for {user['email']}: {data}", data)
                else:
                    self.log_test(f"Login Success - {user['role'].title()}", False, 
                                f"Login failed for {user['email']}: HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Login Success - {user['role'].title()}", False, 
                            f"Error testing {user['email']}: {str(e)}")

    def run_login_tests(self):
        """Run all login tests"""
        print("=" * 60)
        print("DIOGENES TRAVEL PANEL - LOGIN SYSTEM TESTS")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print()
        
        # Initialize users first
        self.test_initialize_users()
        
        print("\n" + "-" * 40)
        print("LOGIN FUNCTIONALITY TESTS")
        print("-" * 40)
        
        # Test login scenarios
        admin_user = self.test_login_success_admin()
        self.test_login_wrong_password()
        self.test_login_nonexistent_email()
        self.test_login_empty_credentials()
        
        print("\n" + "-" * 40)
        print("ALL USERS LOGIN TESTS")
        print("-" * 40)
        
        self.test_login_all_users()
        
        # Summary
        print("\n" + "=" * 60)
        print("LOGIN TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL LOGIN TESTS PASSED!")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = LoginTester()
    passed, failed, results = tester.run_login_tests()
    
    # Save results to file
    with open('/app/login_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/login_test_results.json")
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
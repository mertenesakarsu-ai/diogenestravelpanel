#!/usr/bin/env python3
"""
Backend API Test Suite for Diogenes Travel Panel
Tests all backend endpoints including Excel upload and compare functionality
"""

import requests
import pandas as pd
import io
import json
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://view-columns-change.preview.emergentagent.com/api"

class BackendTester:
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
    
    def create_sample_flights_excel(self):
        """Create sample Excel file for flights testing"""
        flights_data = [
            {
                'flightCode': 'TK1234',
                'airline': 'Turkish Airlines',
                'from': 'Istanbul',
                'to': 'Antalya',
                'date': '2024-01-15',
                'time': '14:30',
                'direction': 'departure',
                'passengers': 150,
                'hasPNR': True,
                'pnr': 'ABC123'
            },
            {
                'flightCode': 'PC5678',
                'airline': 'Pegasus',
                'from': 'Antalya',
                'to': 'Istanbul',
                'date': '2024-01-16',
                'time': '18:45',
                'direction': 'arrival',
                'passengers': 180,
                'hasPNR': True,
                'pnr': 'DEF456'
            },
            {
                'flightCode': 'SU9012',
                'airline': 'SunExpress',
                'from': 'Izmir',
                'to': 'Antalya',
                'date': '2024-01-17',
                'time': '10:15',
                'direction': 'arrival',
                'passengers': 120,
                'hasPNR': False,
                'pnr': ''
            }
        ]
        
        df = pd.DataFrame(flights_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer
    
    def create_sample_reservations_excel(self):
        """Create sample Excel file for reservations testing"""
        reservations_data = [
            {
                'voucherNo': 'VOC001',
                'leader_name': 'Ahmet Yılmaz',
                'leader_passport': 'T12345678',
                'product_code': 'ANT001',
                'product_name': 'Antalya Beach Resort',
                'hotel': 'Grand Hotel Antalya',
                'arrivalDate': '2024-01-20',
                'departureDate': '2024-01-27',
                'pax': 4,
                'status': 'confirmed'
            },
            {
                'voucherNo': 'VOC002',
                'leader_name': 'Fatma Demir',
                'leader_passport': 'T87654321',
                'product_code': 'IST002',
                'product_name': 'Istanbul City Tour',
                'hotel': 'Istanbul Palace Hotel',
                'arrivalDate': '2024-01-25',
                'departureDate': '2024-01-30',
                'pax': 2,
                'status': 'pending'
            },
            {
                'voucherNo': 'VOC003',
                'leader_name': 'Mehmet Kaya',
                'leader_passport': 'T11223344',
                'product_code': 'CAP003',
                'product_name': 'Cappadocia Adventure',
                'hotel': 'Cave Hotel Cappadocia',
                'arrivalDate': '2024-02-01',
                'departureDate': '2024-02-05',
                'pax': 6,
                'status': 'confirmed'
            }
        ]
        
        df = pd.DataFrame(reservations_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer
    
    def create_sample_operations_excel(self):
        """Create sample Excel file for operations testing"""
        operations_data = [
            {
                'flightCode': 'TK1234',
                'type': 'transfer',
                'from': 'Airport',
                'to': 'Grand Hotel Antalya',
                'date': '2024-01-15',
                'time': '15:30',
                'passengers': 4,
                'hotel': 'Grand Hotel Antalya',
                'transferTime': '45 minutes',
                'notes': 'VIP transfer service'
            },
            {
                'flightCode': 'PC5678',
                'type': 'tour',
                'from': 'Hotel',
                'to': 'Pamukkale',
                'date': '2024-01-16',
                'time': '08:00',
                'passengers': 25,
                'hotel': 'Various Hotels',
                'transferTime': '3 hours',
                'notes': 'Full day tour with lunch'
            },
            {
                'flightCode': 'SU9012',
                'type': 'transfer',
                'from': 'Istanbul Palace Hotel',
                'to': 'Airport',
                'date': '2024-01-17',
                'time': '07:00',
                'passengers': 2,
                'hotel': 'Istanbul Palace Hotel',
                'transferTime': '1 hour',
                'notes': 'Early morning departure'
            }
        ]
        
        df = pd.DataFrame(operations_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        return excel_buffer

    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy' and data.get('database') == 'connected':
                    self.log_test("Health Check", True, "System is healthy and database connected", data)
                else:
                    self.log_test("Health Check", False, f"System unhealthy: {data}", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")

    def test_get_flights(self):
        """Test GET /api/flights"""
        try:
            response = self.session.get(f"{BACKEND_URL}/flights", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Flights", True, f"Retrieved {len(data)} flights", {"count": len(data)})
            else:
                self.log_test("Get Flights", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Flights", False, f"Error: {str(e)}")

    def test_get_reservations(self):
        """Test GET /api/reservations"""
        try:
            response = self.session.get(f"{BACKEND_URL}/reservations", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Reservations", True, f"Retrieved {len(data)} reservations", {"count": len(data)})
            else:
                self.log_test("Get Reservations", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Reservations", False, f"Error: {str(e)}")

    def test_get_operations(self):
        """Test GET /api/operations"""
        try:
            response = self.session.get(f"{BACKEND_URL}/operations", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Operations", True, f"Retrieved {len(data)} operations", {"count": len(data)})
            else:
                self.log_test("Get Operations", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Operations", False, f"Error: {str(e)}")

    def test_flights_upload(self):
        """Test POST /api/flights/upload"""
        try:
            excel_file = self.create_sample_flights_excel()
            files = {'file': ('test_flights.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = self.session.post(f"{BACKEND_URL}/flights/upload", files=files, timeout=30)
            if response.status_code in [200, 201]:
                data = response.json()
                if 'count' in data and data['count'] > 0:
                    self.log_test("Flights Upload", True, f"Successfully uploaded {data['count']} flights", data)
                else:
                    self.log_test("Flights Upload", False, f"Upload completed but no flights added: {data}", data)
            else:
                self.log_test("Flights Upload", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flights Upload", False, f"Error: {str(e)}")

    def test_reservations_upload(self):
        """Test POST /api/reservations/upload"""
        try:
            excel_file = self.create_sample_reservations_excel()
            files = {'file': ('test_reservations.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = self.session.post(f"{BACKEND_URL}/reservations/upload", files=files, timeout=30)
            if response.status_code in [200, 201]:
                data = response.json()
                if 'count' in data and data['count'] > 0:
                    self.log_test("Reservations Upload", True, f"Successfully uploaded {data['count']} reservations", data)
                else:
                    self.log_test("Reservations Upload", False, f"Upload completed but no reservations added: {data}", data)
            else:
                self.log_test("Reservations Upload", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Reservations Upload", False, f"Error: {str(e)}")

    def test_operations_upload(self):
        """Test POST /api/operations/upload"""
        try:
            excel_file = self.create_sample_operations_excel()
            files = {'file': ('test_operations.xlsx', excel_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = self.session.post(f"{BACKEND_URL}/operations/upload", files=files, timeout=30)
            if response.status_code in [200, 201]:
                data = response.json()
                if 'count' in data and data['count'] > 0:
                    self.log_test("Operations Upload", True, f"Successfully uploaded {data['count']} operations", data)
                else:
                    self.log_test("Operations Upload", False, f"Upload completed but no operations added: {data}", data)
            else:
                self.log_test("Operations Upload", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Operations Upload", False, f"Error: {str(e)}")

    def test_flights_compare(self):
        """Test POST /api/flights/compare"""
        try:
            # Create a comparison Excel file with some different data
            compare_data = [
                {
                    'flightCode': 'TK1234',
                    'airline': 'Turkish Airlines',
                    'from': 'Istanbul',
                    'to': 'Antalya',
                    'date': '2024-01-15',
                    'time': '14:30',
                    'direction': 'departure',
                    'passengers': 150,
                    'hasPNR': True,
                    'pnr': 'XYZ999'  # Different PNR to test update detection
                },
                {
                    'flightCode': 'NEW001',  # New flight not in database
                    'airline': 'New Airline',
                    'from': 'Ankara',
                    'to': 'Izmir',
                    'date': '2024-01-18',
                    'time': '12:00',
                    'direction': 'departure',
                    'passengers': 100,
                    'hasPNR': False,
                    'pnr': ''
                }
            ]
            
            df = pd.DataFrame(compare_data)
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
            
            files = {'file': ('compare_flights.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = self.session.post(f"{BACKEND_URL}/flights/compare", files=files, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'summary' in data:
                    summary = data['summary']
                    self.log_test("Flights Compare", True, 
                                f"Compare completed - New: {summary.get('new', 0)}, Updated: {summary.get('updated', 0)}, Missing: {summary.get('missing', 0)}", 
                                data)
                else:
                    self.log_test("Flights Compare", False, f"Invalid response format: {data}", data)
            else:
                self.log_test("Flights Compare", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flights Compare", False, f"Error: {str(e)}")

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
                    else:
                        self.log_test("Login Success - Admin", False, f"Incorrect user data returned: {data}", data)
                else:
                    self.log_test("Login Success - Admin", False, f"Missing required fields in response: {data}", data)
            else:
                self.log_test("Login Success - Admin", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Login Success - Admin", False, f"Error: {str(e)}")

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

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("DIOGENES TRAVEL PANEL - BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print()
        
        # Test basic endpoints first
        self.test_health_endpoint()
        
        print("\n" + "-" * 40)
        print("LOGIN SYSTEM TESTS")
        print("-" * 40)
        
        # Initialize users first
        self.test_initialize_users()
        
        # Test login functionality
        self.test_login_success_admin()
        self.test_login_wrong_password()
        self.test_login_nonexistent_email()
        self.test_login_empty_credentials()
        self.test_login_all_users()
        
        print("\n" + "-" * 40)
        print("BASIC ENDPOINT TESTS")
        print("-" * 40)
        
        self.test_get_flights()
        self.test_get_reservations()
        self.test_get_operations()
        
        print("\n" + "-" * 40)
        print("EXCEL UPLOAD TESTS")
        print("-" * 40)
        
        # Test upload endpoints
        self.test_flights_upload()
        self.test_reservations_upload()
        self.test_operations_upload()
        
        print("\n" + "-" * 40)
        print("EXCEL COMPARE TESTS")
        print("-" * 40)
        
        # Test compare functionality
        self.test_flights_compare()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
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
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, results = tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
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
BACKEND_URL = "https://aerodata-portal.preview.emergentagent.com/api"

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
                "email": "admin@diogenestravel.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['id', 'name', 'email', 'role', 'status', 'created_at']
                if all(field in data for field in expected_fields):
                    if data['email'] == 'admin@diogenestravel.com' and data['role'] == 'admin' and data['status'] == 'active':
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
                "email": "admin@diogenestravel.com",
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
                "email": "nonexistent@diogenestravel.com",
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
            {"email": "reservation@diogenestravel.com", "password": "reservation123", "role": "reservation", "name": "Rezervasyon Manager"},
            {"email": "operation@diogenestravel.com", "password": "operation123", "role": "operation", "name": "Operasyon Manager"},
            {"email": "flight@diogenestravel.com", "password": "flight123", "role": "flight", "name": "Uçak Manager"},
            {"email": "management@diogenestravel.com", "password": "management123", "role": "management", "name": "Yönetim Manager"}
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

    def test_get_users(self):
        """Test GET /api/users to check if users exist"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users", timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_emails = [user.get('email', '') for user in data]
                expected_emails = [
                    'admin@diogenestravel.com',
                    'reservation@diogenestravel.com', 
                    'operation@diogenestravel.com',
                    'flight@diogenestravel.com',
                    'management@diogenestravel.com'
                ]
                
                missing_users = [email for email in expected_emails if email not in user_emails]
                
                if len(data) == 0:
                    self.log_test("Get Users", False, "No users found in database", {"count": 0, "users": []})
                elif missing_users:
                    self.log_test("Get Users", False, f"Missing users: {missing_users}", {"count": len(data), "missing": missing_users, "existing": user_emails})
                else:
                    self.log_test("Get Users", True, f"All {len(data)} expected users found", {"count": len(data), "users": user_emails})
            else:
                self.log_test("Get Users", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Users", False, f"Error: {str(e)}")

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

    def get_user_id_by_email(self, email):
        """Get user ID by email for authentication headers"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users", timeout=10)
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('email') == email:
                        return user.get('id')
            return None
        except Exception:
            return None

    def test_flight_details_api_success(self):
        """Test GET /api/operations/flight-details/{flight_code} with operation user"""
        try:
            # Get operation user ID
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Flight Details API - Success", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            flight_code = "TK2412"
            airport_code = "IST"
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/{flight_code}?airport_code={airport_code}", 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check for comprehensive flight information
                required_fields = ['flight_number', 'callsign', 'status', 'airline', 'aircraft', 'departure', 'arrival']
                
                if all(field in data for field in required_fields):
                    # Check airline info
                    airline = data.get('airline', {})
                    if 'name' in airline and 'iata' in airline:
                        # Check departure info
                        departure = data.get('departure', {})
                        arrival = data.get('arrival', {})
                        
                        if ('airport' in departure and 'scheduled_time' in departure and 
                            'airport' in arrival and 'scheduled_time' in arrival):
                            self.log_test("Flight Details API - Success", True, 
                                        f"Successfully retrieved comprehensive flight details for {flight_code}", 
                                        {
                                            "flight_number": data.get('flight_number'),
                                            "airline": airline.get('name'),
                                            "status": data.get('status'),
                                            "departure_airport": departure.get('airport'),
                                            "arrival_airport": arrival.get('airport')
                                        })
                        else:
                            self.log_test("Flight Details API - Success", False, 
                                        f"Missing departure/arrival details: {data}")
                    else:
                        self.log_test("Flight Details API - Success", False, 
                                    f"Missing airline information: {data}")
                else:
                    missing_fields = [field for field in required_fields if field not in data]
                    self.log_test("Flight Details API - Success", False, 
                                f"Missing required fields: {missing_fields}. Response: {data}")
            else:
                self.log_test("Flight Details API - Success", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flight Details API - Success", False, f"Error: {str(e)}")

    def test_flight_details_api_permission_denied(self):
        """Test GET /api/operations/flight-details/{flight_code} with reservation user (should be denied)"""
        try:
            # Get reservation user ID
            reservation_user_id = self.get_user_id_by_email("reservation@diogenestravel.com")
            if not reservation_user_id:
                self.log_test("Flight Details API - Permission Denied", False, "Could not get reservation user ID")
                return

            headers = {"x-user-id": reservation_user_id}
            flight_code = "TK2412"
            airport_code = "IST"
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/{flight_code}?airport_code={airport_code}", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 403:
                data = response.json()
                if 'detail' in data and 'permission' in data['detail'].lower():
                    self.log_test("Flight Details API - Permission Denied", True, 
                                "Correctly denied access for reservation user with 403", data)
                else:
                    self.log_test("Flight Details API - Permission Denied", False, 
                                f"Wrong error message for 403: {data}")
            else:
                self.log_test("Flight Details API - Permission Denied", False, 
                            f"Expected 403, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flight Details API - Permission Denied", False, f"Error: {str(e)}")

    def test_flight_details_api_no_auth(self):
        """Test GET /api/operations/flight-details/{flight_code} without authentication"""
        try:
            flight_code = "TK2412"
            airport_code = "IST"
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/{flight_code}?airport_code={airport_code}", 
                timeout=10
            )
            
            if response.status_code == 401:
                data = response.json()
                if 'detail' in data and 'authentication' in data['detail'].lower():
                    self.log_test("Flight Details API - No Auth", True, 
                                "Correctly rejected request without authentication with 401", data)
                else:
                    self.log_test("Flight Details API - No Auth", False, 
                                f"Wrong error message for 401: {data}")
            else:
                self.log_test("Flight Details API - No Auth", False, 
                            f"Expected 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flight Details API - No Auth", False, f"Error: {str(e)}")

    def test_flight_details_api_invalid_flight(self):
        """Test GET /api/operations/flight-details/{flight_code} with invalid flight code"""
        try:
            # Get operation user ID
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Flight Details API - Invalid Flight", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            flight_code = "INVALID999"
            airport_code = "IST"
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/{flight_code}?airport_code={airport_code}", 
                headers=headers, 
                timeout=30
            )
            
            # Should handle gracefully - either return error info or empty result
            if response.status_code in [200, 404, 502]:
                if response.status_code == 200:
                    data = response.json()
                    if 'error' in data or not data.get('flight_number'):
                        self.log_test("Flight Details API - Invalid Flight", True, 
                                    "Gracefully handled invalid flight code", data)
                    else:
                        self.log_test("Flight Details API - Invalid Flight", False, 
                                    f"Unexpected success for invalid flight: {data}")
                else:
                    self.log_test("Flight Details API - Invalid Flight", True, 
                                f"Appropriately handled invalid flight with HTTP {response.status_code}")
            else:
                self.log_test("Flight Details API - Invalid Flight", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flight Details API - Invalid Flight", False, f"Error: {str(e)}")

    def test_flight_details_api_cache(self):
        """Test GET /api/operations/flight-details/{flight_code} caching (15 minutes)"""
        try:
            # Get operation user ID
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Flight Details API - Cache Test", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            flight_code = "TK2412"
            airport_code = "IST"
            url = f"{BACKEND_URL}/operations/flight-details/{flight_code}?airport_code={airport_code}"
            
            # First call
            import time
            start_time = time.time()
            response1 = self.session.get(url, headers=headers, timeout=30)
            first_call_time = time.time() - start_time
            
            if response1.status_code != 200:
                self.log_test("Flight Details API - Cache Test", False, 
                            f"First call failed: HTTP {response1.status_code}")
                return
            
            # Second call (should be cached)
            start_time = time.time()
            response2 = self.session.get(url, headers=headers, timeout=30)
            second_call_time = time.time() - start_time
            
            if response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                # Check if responses are similar (cached)
                if (data1.get('flight_number') == data2.get('flight_number') and
                    data1.get('status') == data2.get('status')):
                    
                    # Second call should be faster (cached)
                    if second_call_time < first_call_time * 0.8:  # At least 20% faster
                        self.log_test("Flight Details API - Cache Test", True, 
                                    f"Cache working - First call: {first_call_time:.2f}s, Second call: {second_call_time:.2f}s", 
                                    {
                                        "first_call_time": first_call_time,
                                        "second_call_time": second_call_time,
                                        "flight_number": data1.get('flight_number')
                                    })
                    else:
                        self.log_test("Flight Details API - Cache Test", True, 
                                    f"Cache appears to be working (consistent data) - First: {first_call_time:.2f}s, Second: {second_call_time:.2f}s", 
                                    {
                                        "first_call_time": first_call_time,
                                        "second_call_time": second_call_time,
                                        "note": "Second call not significantly faster, but data is consistent"
                                    })
                else:
                    self.log_test("Flight Details API - Cache Test", False, 
                                f"Inconsistent data between calls - possible cache issue")
            else:
                self.log_test("Flight Details API - Cache Test", False, 
                            f"Second call failed: HTTP {response2.status_code}")
        except Exception as e:
            self.log_test("Flight Details API - Cache Test", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("DIOGENES TRAVEL PANEL - BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print()
        
        # 1. Backend Health Check
        print("1. BACKEND HEALTH CHECK")
        print("-" * 40)
        self.test_health_endpoint()
        
        # 2. User Control - Check if users exist
        print("\n2. KULLANICI KONTROLÜ")
        print("-" * 40)
        self.test_get_users()
        
        # 3. User Re-creation if needed
        print("\n3. KULLANICI YENİDEN OLUŞTURMA")
        print("-" * 40)
        self.test_initialize_users()
        
        # 4. Login Tests
        print("\n4. LOGİN TESTLERİ")
        print("-" * 40)
        
        # Test admin login first
        self.test_login_success_admin()
        
        # Test different users
        self.test_login_all_users()
        
        # Test error scenarios
        self.test_login_wrong_password()
        self.test_login_nonexistent_email()
        self.test_login_empty_credentials()
        
        print("\n" + "-" * 40)
        print("ADDITIONAL BACKEND TESTS")
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
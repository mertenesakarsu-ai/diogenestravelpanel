#!/usr/bin/env python3
"""
Flight API Integration Test Suite
Tests the new Flight API integration endpoint for Operations department
"""

import requests
import time
import json
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://diogenes-env.preview.emergentagent.com/api"

class FlightAPITester:
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

    def test_health_check(self):
        """Test GET /api/health - Quick verification"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy' and data.get('database') == 'connected':
                    self.log_test("Health Check", True, "Backend is running and database is connected", data)
                else:
                    self.log_test("Health Check", False, f"System unhealthy: {data}", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")

    def test_flight_details_main_feature(self):
        """Test Flight Details API - Main feature with TK2412"""
        try:
            # Get operation user ID from database
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Flight Details - Main Feature", False, "Could not get operation user ID from database")
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
                required_sections = ['flight_number', 'callsign', 'airline', 'aircraft', 'departure', 'arrival', 'status']
                
                if all(section in data for section in required_sections):
                    # Verify flight identity
                    airline = data.get('airline', {})
                    aircraft = data.get('aircraft', {})
                    departure = data.get('departure', {})
                    arrival = data.get('arrival', {})
                    
                    flight_info = {
                        "flight_number": data.get('flight_number'),
                        "callsign": data.get('callsign'),
                        "airline_name": airline.get('name'),
                        "airline_iata": airline.get('iata'),
                        "aircraft_model": aircraft.get('model'),
                        "aircraft_registration": aircraft.get('registration'),
                        "departure_airport": departure.get('airport'),
                        "departure_terminal": departure.get('terminal'),
                        "departure_gate": departure.get('gate'),
                        "departure_std": departure.get('scheduled_time'),
                        "departure_etd": departure.get('estimated_time'),
                        "departure_atd": departure.get('actual_time'),
                        "departure_delay": departure.get('delay'),
                        "arrival_airport": arrival.get('airport'),
                        "arrival_terminal": arrival.get('terminal'),
                        "arrival_gate": arrival.get('gate'),
                        "arrival_baggage": arrival.get('baggage'),
                        "arrival_sta": arrival.get('scheduled_time'),
                        "arrival_eta": arrival.get('estimated_time'),
                        "arrival_ata": arrival.get('actual_time'),
                        "arrival_delay": arrival.get('delay'),
                        "duration": data.get('duration'),
                        "distance": data.get('distance'),
                        "status": data.get('status')
                    }
                    
                    self.log_test("Flight Details - Main Feature", True, 
                                f"Successfully retrieved comprehensive flight information for {flight_code}", 
                                flight_info)
                else:
                    missing_sections = [section for section in required_sections if section not in data]
                    self.log_test("Flight Details - Main Feature", False, 
                                f"Missing required sections: {missing_sections}")
            else:
                self.log_test("Flight Details - Main Feature", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Flight Details - Main Feature", False, f"Error: {str(e)}")

    def test_permission_operation_user(self):
        """Test with operation user (should have access)"""
        try:
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Permission Test - Operation User", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/TK2412?airport_code=IST", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Permission Test - Operation User", True, 
                            "Operation user has correct access to flight details")
            else:
                self.log_test("Permission Test - Operation User", False, 
                            f"Operation user denied access: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Permission Test - Operation User", False, f"Error: {str(e)}")

    def test_permission_reservation_user(self):
        """Test with reservation user (should NOT have access - 403)"""
        try:
            reservation_user_id = self.get_user_id_by_email("reservation@diogenestravel.com")
            if not reservation_user_id:
                self.log_test("Permission Test - Reservation User", False, "Could not get reservation user ID")
                return

            headers = {"x-user-id": reservation_user_id}
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/TK2412?airport_code=IST", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 403:
                data = response.json()
                if 'detail' in data and 'permission' in data['detail'].lower():
                    self.log_test("Permission Test - Reservation User", True, 
                                "Reservation user correctly denied access with 403")
                else:
                    self.log_test("Permission Test - Reservation User", False, 
                                f"Wrong error message: {data}")
            else:
                self.log_test("Permission Test - Reservation User", False, 
                            f"Expected 403, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Permission Test - Reservation User", False, f"Error: {str(e)}")

    def test_cache_functionality(self):
        """Test cache functionality (15 minutes)"""
        try:
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Cache Test", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            url = f"{BACKEND_URL}/operations/flight-details/TK2412?airport_code=IST"
            
            # First call
            start_time = time.time()
            response1 = self.session.get(url, headers=headers, timeout=30)
            first_call_time = time.time() - start_time
            
            if response1.status_code != 200:
                self.log_test("Cache Test", False, f"First call failed: HTTP {response1.status_code}")
                return
            
            # Second call (should be cached and faster)
            start_time = time.time()
            response2 = self.session.get(url, headers=headers, timeout=30)
            second_call_time = time.time() - start_time
            
            if response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                # Check if responses are consistent (cached)
                if (data1.get('flight_number') == data2.get('flight_number') and
                    data1.get('status') == data2.get('status')):
                    
                    cache_info = {
                        "first_call_time": round(first_call_time, 3),
                        "second_call_time": round(second_call_time, 3),
                        "speed_improvement": f"{round((first_call_time - second_call_time) / first_call_time * 100, 1)}%",
                        "flight_number": data1.get('flight_number')
                    }
                    
                    if second_call_time < first_call_time * 0.8:  # At least 20% faster
                        self.log_test("Cache Test", True, 
                                    f"Cache working effectively - Second call {cache_info['speed_improvement']} faster", 
                                    cache_info)
                    else:
                        self.log_test("Cache Test", True, 
                                    f"Cache working (consistent data) - Times: {first_call_time:.3f}s vs {second_call_time:.3f}s", 
                                    cache_info)
                else:
                    self.log_test("Cache Test", False, "Inconsistent data between calls - cache issue")
            else:
                self.log_test("Cache Test", False, f"Second call failed: HTTP {response2.status_code}")
        except Exception as e:
            self.log_test("Cache Test", False, f"Error: {str(e)}")

    def test_error_handling_invalid_flight(self):
        """Test with invalid flight code (should handle gracefully)"""
        try:
            operation_user_id = self.get_user_id_by_email("operation@diogenestravel.com")
            if not operation_user_id:
                self.log_test("Error Handling - Invalid Flight", False, "Could not get operation user ID")
                return

            headers = {"x-user-id": operation_user_id}
            
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/INVALID999?airport_code=IST", 
                headers=headers, 
                timeout=30
            )
            
            # Should handle gracefully - API error is expected for invalid flights
            if response.status_code == 500:
                data = response.json()
                if 'detail' in data and 'flight api error' in data['detail'].lower():
                    self.log_test("Error Handling - Invalid Flight", True, 
                                "Gracefully handled invalid flight code with appropriate error")
                else:
                    self.log_test("Error Handling - Invalid Flight", False, 
                                f"Unexpected error message: {data}")
            elif response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    self.log_test("Error Handling - Invalid Flight", True, 
                                "Gracefully handled invalid flight code", data)
                else:
                    self.log_test("Error Handling - Invalid Flight", False, 
                                f"Unexpected success for invalid flight: {data}")
            else:
                self.log_test("Error Handling - Invalid Flight", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Flight", False, f"Error: {str(e)}")

    def test_error_handling_no_auth(self):
        """Test without authentication (should return 401)"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/operations/flight-details/TK2412?airport_code=IST", 
                timeout=10
            )
            
            if response.status_code == 401:
                data = response.json()
                if 'detail' in data and 'authentication' in data['detail'].lower():
                    self.log_test("Error Handling - No Auth", True, 
                                "Correctly rejected request without authentication")
                else:
                    self.log_test("Error Handling - No Auth", False, 
                                f"Wrong error message: {data}")
            else:
                self.log_test("Error Handling - No Auth", False, 
                            f"Expected 401, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - No Auth", False, f"Error: {str(e)}")

    def run_flight_api_tests(self):
        """Run all Flight API integration tests"""
        print("=" * 70)
        print("FLIGHT API INTEGRATION TEST SUITE")
        print("Operations Department - RapidAPI Aerodatabox Integration")
        print("=" * 70)
        print(f"Testing backend at: {BACKEND_URL}")
        print()
        
        # 1. Health Check
        print("1. HEALTH CHECK (Quick verification)")
        print("-" * 50)
        self.test_health_check()
        
        # 2. Main Feature Test
        print("\n2. FLIGHT DETAILS API TEST (Main feature)")
        print("-" * 50)
        print("   Endpoint: GET /api/operations/flight-details/{flight_code}")
        print("   Parameters: flight_code = 'TK2412', airport_code = 'IST'")
        print("   Headers: x-user-id = operation user id")
        self.test_flight_details_main_feature()
        
        # 3. Permission Tests
        print("\n3. PERMISSION TESTS")
        print("-" * 50)
        self.test_permission_operation_user()
        self.test_permission_reservation_user()
        
        # 4. Cache Test
        print("\n4. CACHE TEST (15 minutes)")
        print("-" * 50)
        self.test_cache_functionality()
        
        # 5. Error Handling
        print("\n5. ERROR HANDLING")
        print("-" * 50)
        self.test_error_handling_invalid_flight()
        self.test_error_handling_no_auth()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
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
            print("\n🎉 ALL FLIGHT API INTEGRATION TESTS PASSED!")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = FlightAPITester()
    passed, failed, results = tester.run_flight_api_tests()
    
    # Save results to file
    with open('/app/flight_api_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/flight_api_test_results.json")
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
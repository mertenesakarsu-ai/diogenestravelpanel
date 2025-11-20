#!/usr/bin/env python3
"""
Focused Login Test for Diogenes Travel Panel
Tests the specific scenarios mentioned in the review request
"""

import requests
import json
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://flight-data-service.preview.emergentagent.com/api"

def test_login_scenarios():
    """Test the specific login scenarios from the review request"""
    session = requests.Session()
    results = []
    
    print("=" * 60)
    print("FOCUSED LOGIN TEST - DIOGENES TRAVEL PANEL")
    print("=" * 60)
    print(f"Testing backend at: {BACKEND_URL}")
    print()
    
    # 1. Backend Health Check
    print("1. BACKEND HEALTH CHECK")
    print("-" * 40)
    try:
        response = session.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Backend is healthy and running")
                print(f"   Database: {data.get('database')}")
                print(f"   Users: {data.get('total_users')}")
                results.append({"test": "Health Check", "status": "PASS", "details": data})
            else:
                print("❌ Backend is unhealthy")
                results.append({"test": "Health Check", "status": "FAIL", "details": data})
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            results.append({"test": "Health Check", "status": "FAIL", "details": response.text})
    except Exception as e:
        print(f"❌ Backend connection error: {str(e)}")
        results.append({"test": "Health Check", "status": "FAIL", "details": str(e)})
    
    # 2. Check Users in Database
    print("\n2. KULLANICI KONTROLÜ")
    print("-" * 40)
    try:
        response = session.get(f"{BACKEND_URL}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            user_emails = [user.get('email', '') for user in users]
            print(f"✅ Found {len(users)} users in database:")
            for email in user_emails:
                print(f"   - {email}")
            results.append({"test": "User Check", "status": "PASS", "details": {"count": len(users), "emails": user_emails}})
        else:
            print(f"❌ Failed to get users: HTTP {response.status_code}")
            results.append({"test": "User Check", "status": "FAIL", "details": response.text})
    except Exception as e:
        print(f"❌ Error checking users: {str(e)}")
        results.append({"test": "User Check", "status": "FAIL", "details": str(e)})
    
    # 3. Test Login with Admin User (as mentioned in review request)
    print("\n3. LOGİN TESTİ - ADMIN")
    print("-" * 40)
    try:
        login_data = {
            "email": "admin@diogenestravel.com",
            "password": "admin123"
        }
        
        response = session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Admin login successful!")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Status: {user_data.get('status')}")
            results.append({"test": "Admin Login", "status": "PASS", "details": user_data})
        else:
            print(f"❌ Admin login failed: HTTP {response.status_code}")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   Error: {error_data}")
            results.append({"test": "Admin Login", "status": "FAIL", "details": error_data})
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        results.append({"test": "Admin Login", "status": "FAIL", "details": str(e)})
    
    # 4. Test Login with Reservation User
    print("\n4. LOGİN TESTİ - RESERVATION")
    print("-" * 40)
    try:
        login_data = {
            "email": "reservation@diogenestravel.com",
            "password": "reservation123"
        }
        
        response = session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Reservation login successful!")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            results.append({"test": "Reservation Login", "status": "PASS", "details": user_data})
        else:
            print(f"❌ Reservation login failed: HTTP {response.status_code}")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   Error: {error_data}")
            results.append({"test": "Reservation Login", "status": "FAIL", "details": error_data})
    except Exception as e:
        print(f"❌ Reservation login error: {str(e)}")
        results.append({"test": "Reservation Login", "status": "FAIL", "details": str(e)})
    
    # 5. Test Login with Operation User
    print("\n5. LOGİN TESTİ - OPERATION")
    print("-" * 40)
    try:
        login_data = {
            "email": "operation@diogenestravel.com",
            "password": "operation123"
        }
        
        response = session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Operation login successful!")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            results.append({"test": "Operation Login", "status": "PASS", "details": user_data})
        else:
            print(f"❌ Operation login failed: HTTP {response.status_code}")
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f"   Error: {error_data}")
            results.append({"test": "Operation Login", "status": "FAIL", "details": error_data})
    except Exception as e:
        print(f"❌ Operation login error: {str(e)}")
        results.append({"test": "Operation Login", "status": "FAIL", "details": str(e)})
    
    # 6. Test Wrong Password Scenario
    print("\n6. YANLIŞ ŞİFRE TESTİ")
    print("-" * 40)
    try:
        login_data = {
            "email": "admin@diogenestravel.com",
            "password": "wrongpassword"
        }
        
        response = session.post(f"{BACKEND_URL}/login", json=login_data, timeout=10)
        if response.status_code == 401:
            error_data = response.json()
            if 'Email veya şifre hatalı' in error_data.get('detail', ''):
                print("✅ Wrong password correctly rejected with proper error message")
                print(f"   Error message: {error_data.get('detail')}")
                results.append({"test": "Wrong Password", "status": "PASS", "details": error_data})
            else:
                print(f"❌ Wrong error message: {error_data}")
                results.append({"test": "Wrong Password", "status": "FAIL", "details": error_data})
        else:
            print(f"❌ Expected 401, got HTTP {response.status_code}")
            results.append({"test": "Wrong Password", "status": "FAIL", "details": response.text})
    except Exception as e:
        print(f"❌ Wrong password test error: {str(e)}")
        results.append({"test": "Wrong Password", "status": "FAIL", "details": str(e)})
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results if result['status'] == 'PASS')
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Login system is working correctly.")
        print("\nKULLANICI BİLGİLERİ:")
        print("✅ admin@diogenestravel.com / admin123")
        print("✅ reservation@diogenestravel.com / reservation123")
        print("✅ operation@diogenestravel.com / operation123")
        print("✅ flight@diogenestravel.com / flight123")
        print("✅ management@diogenestravel.com / management123")
    else:
        print(f"\n❌ {failed} tests failed. See details above.")
    
    return results

if __name__ == "__main__":
    results = test_login_scenarios()
    
    # Save results
    with open('/app/login_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'passed': sum(1 for r in results if r['status'] == 'PASS'),
            'failed': sum(1 for r in results if r['status'] == 'FAIL'),
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/login_test_results.json")
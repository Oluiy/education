"""
EduNerve Authentication Service - Test Script
Quick test script to verify the authentication system
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1/auth"

def test_api():
    """
    Test the authentication API endpoints
    """
    print("🧪 Testing EduNerve Authentication Service")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check failed: {e}")
        return
    
    # Test school creation
    print("\n2. Creating Test School...")
    school_data = {
        "name": "Test Secondary School",
        "code": "TEST001",
        "address": "Test Address, Lagos, Nigeria",
        "phone": "+2348123456789",
        "email": "test@school.edu.ng",
        "principal_name": "Mr. Test Principal"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/schools", json=school_data)
        print(f"✅ School Creation: {response.status_code}")
        school_response = response.json()
        school_id = school_response.get("id")
        print(f"   School ID: {school_id}")
    except Exception as e:
        print(f"❌ School Creation failed: {e}")
        # Try to get existing school
        try:
            response = requests.get(f"{BASE_URL}/schools")
            schools = response.json()
            if schools:
                school_id = schools[0]["id"]
                print(f"   Using existing school ID: {school_id}")
            else:
                print("   No schools found")
                return
        except:
            print("   Cannot proceed without school")
            return
    
    # Test user registration
    print("\n3. Testing User Registration...")
    
    # Register admin
    admin_data = {
        "email": "admin@test.com",
        "password": "AdminPass123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "school_id": school_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=admin_data)
        print(f"✅ Admin Registration: {response.status_code}")
        if response.status_code == 201:
            print("   Admin created successfully")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Admin Registration failed: {e}")
    
    # Register teacher
    teacher_data = {
        "email": "teacher@test.com",
        "password": "TeacherPass123",
        "first_name": "Teacher",
        "last_name": "User",
        "role": "teacher",
        "school_id": school_id,
        "employee_id": "EMP001",
        "subjects": "Mathematics, Physics"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=teacher_data)
        print(f"✅ Teacher Registration: {response.status_code}")
        if response.status_code == 201:
            print("   Teacher created successfully")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Teacher Registration failed: {e}")
    
    # Register student
    student_data = {
        "email": "student@test.com",
        "password": "StudentPass123",
        "first_name": "Student",
        "last_name": "User",
        "role": "student",
        "school_id": school_id,
        "class_level": "SS2",
        "student_id": "STU001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=student_data)
        print(f"✅ Student Registration: {response.status_code}")
        if response.status_code == 201:
            print("   Student created successfully")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Student Registration failed: {e}")
    
    # Test login
    print("\n4. Testing Login...")
    
    # Login as admin
    login_data = {
        "email": "admin@test.com",
        "password": "AdminPass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"✅ Admin Login: {response.status_code}")
        if response.status_code == 200:
            login_response = response.json()
            admin_token = login_response.get("access_token")
            print(f"   Token received: {admin_token[:50]}...")
        else:
            print(f"   Response: {response.json()}")
            admin_token = None
    except Exception as e:
        print(f"❌ Admin Login failed: {e}")
        admin_token = None
    
    # Test authenticated requests
    if admin_token:
        print("\n5. Testing Authenticated Requests...")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get current user
        try:
            response = requests.get(f"{BASE_URL}/me", headers=headers)
            print(f"✅ Get Current User: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   User: {user_data['first_name']} {user_data['last_name']} ({user_data['role']})")
        except Exception as e:
            print(f"❌ Get Current User failed: {e}")
        
        # Get users list
        try:
            response = requests.get(f"{BASE_URL}/users", headers=headers)
            print(f"✅ Get Users List: {response.status_code}")
            if response.status_code == 200:
                users = response.json()
                print(f"   Found {len(users)} users")
        except Exception as e:
            print(f"❌ Get Users List failed: {e}")
        
        # Get students
        try:
            response = requests.get(f"{BASE_URL}/students", headers=headers)
            print(f"✅ Get Students: {response.status_code}")
            if response.status_code == 200:
                students = response.json()
                print(f"   Found {len(students)} students")
        except Exception as e:
            print(f"❌ Get Students failed: {e}")
        
        # Get stats
        try:
            response = requests.get(f"{BASE_URL}/stats", headers=headers)
            print(f"✅ Get Stats: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Stats: {stats}")
        except Exception as e:
            print(f"❌ Get Stats failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\n📋 Next Steps:")
    print("1. Check the API documentation at: http://localhost:8000/docs")
    print("2. Test with your frontend application")
    print("3. Set up production database (PostgreSQL)")
    print("4. Configure proper environment variables")
    print("5. Add email/SMS verification")


if __name__ == "__main__":
    test_api()

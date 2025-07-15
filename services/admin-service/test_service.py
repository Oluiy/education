"""
Test script for EduNerve Admin Service
Tests all endpoints and functionality
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8004"
API_BASE = f"{BASE_URL}/api/v1/admin"

# Test data
TEST_USER = {
    "email": "admin@test.com",
    "password": "testpassword123"
}

TEST_SCHOOL_DATA = {
    "school_id": 1,
    "name": "Test High School",
    "code": "THS001",
    "address": "123 Test Street, Test City",
    "phone": "555-0123",
    "email": "admin@testhighschool.edu",
    "website": "https://testhighschool.edu",
    "principal_name": "John Doe",
    "principal_email": "principal@testhighschool.edu",
    "school_type": "public",
    "subscription_tier": "premium"
}

TEST_DEPARTMENT_DATA = {
    "school_id": 1,
    "name": "Mathematics",
    "code": "MATH",
    "description": "Mathematics Department",
    "head_name": "Dr. Jane Smith",
    "head_email": "jane.smith@testhighschool.edu",
    "budget": 50000.0
}

TEST_ALERT_DATA = {
    "school_id": 1,
    "title": "System Maintenance",
    "message": "System maintenance scheduled for tonight from 10 PM to 2 AM",
    "alert_type": "warning",
    "severity": "medium",
    "is_dismissible": True,
    "auto_dismiss_after": 60
}

TEST_ANALYTICS_REQUEST = {
    "school_id": 1,
    "metric_type": "user_activity",
    "date_range_start": "2024-01-01T00:00:00Z",
    "date_range_end": "2024-12-31T23:59:59Z"
}

class AdminServiceTester:
    """Test class for Admin Service"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.headers = {}
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 Setting up Admin Service tests...")
        
        # Check if service is running
        if not await self.check_service_health():
            print("❌ Admin Service is not running!")
            return False
        
        # Try to get auth token (assuming auth service is running)
        if not await self.get_auth_token():
            print("⚠️ Running tests without authentication (some may fail)")
        
        return True
    
    async def teardown(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("✅ Test session cleaned up")
    
    async def check_service_health(self) -> bool:
        """Check if the service is healthy"""
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Service health check passed: {data}")
                    return True
                else:
                    print(f"❌ Service health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Service health check error: {str(e)}")
            return False
    
    async def get_auth_token(self) -> bool:
        """Get authentication token from auth service"""
        try:
            # Try to login to auth service
            auth_url = "http://localhost:8001/api/v1/auth/login"
            login_data = {
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(auth_url, json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    self.headers = {"Authorization": f"Bearer {self.auth_token}"}
                    print("✅ Authentication successful")
                    return True
                else:
                    print(f"⚠️ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️ Authentication error: {str(e)}")
            return False
    
    async def test_dashboard(self) -> bool:
        """Test dashboard endpoint"""
        try:
            print("\\n🧪 Testing dashboard...")
            
            async with self.session.get(
                f"{API_BASE}/dashboard",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Dashboard loaded: {data.get('school_id')} - {data.get('total_users')} users")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Dashboard failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Dashboard error: {str(e)}")
            return False
    
    async def test_school_management(self) -> bool:
        """Test school management endpoints"""
        try:
            print("\\n🧪 Testing school management...")
            
            # Get schools
            async with self.session.get(
                f"{API_BASE}/schools",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    schools = await response.json()
                    print(f"✅ Retrieved {len(schools)} schools")
                    
                    # If no schools, try to create one (might fail if not super admin)
                    if len(schools) == 0:
                        async with self.session.post(
                            f"{API_BASE}/schools",
                            json=TEST_SCHOOL_DATA,
                            headers=self.headers
                        ) as create_response:
                            if create_response.status == 200:
                                school_data = await create_response.json()
                                print(f"✅ Created school: {school_data.get('name')}")
                            else:
                                print("⚠️ Could not create school (may require super admin)")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ School management failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ School management error: {str(e)}")
            return False
    
    async def test_department_management(self) -> bool:
        """Test department management endpoints"""
        try:
            print("\\n🧪 Testing department management...")
            
            # Get departments
            async with self.session.get(
                f"{API_BASE}/departments",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    departments = await response.json()
                    print(f"✅ Retrieved {len(departments)} departments")
                    
                    # Try to create a department
                    async with self.session.post(
                        f"{API_BASE}/departments",
                        json=TEST_DEPARTMENT_DATA,
                        headers=self.headers
                    ) as create_response:
                        if create_response.status == 200:
                            dept_data = await create_response.json()
                            print(f"✅ Created department: {dept_data.get('name')}")
                        else:
                            print("⚠️ Could not create department (may already exist)")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Department management failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Department management error: {str(e)}")
            return False
    
    async def test_admin_users(self) -> bool:
        """Test admin user management"""
        try:
            print("\\n🧪 Testing admin user management...")
            
            async with self.session.get(
                f"{API_BASE}/users",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    users = await response.json()
                    print(f"✅ Retrieved {len(users)} admin users")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Admin user management failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Admin user management error: {str(e)}")
            return False
    
    async def test_audit_logs(self) -> bool:
        """Test audit logs"""
        try:
            print("\\n🧪 Testing audit logs...")
            
            async with self.session.get(
                f"{API_BASE}/audit-logs",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    logs = await response.json()
                    print(f"✅ Retrieved {logs.get('total', 0)} audit logs")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Audit logs failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Audit logs error: {str(e)}")
            return False
    
    async def test_system_alerts(self) -> bool:
        """Test system alerts"""
        try:
            print("\\n🧪 Testing system alerts...")
            
            # Get alerts
            async with self.session.get(
                f"{API_BASE}/alerts",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    alerts = await response.json()
                    print(f"✅ Retrieved {len(alerts)} system alerts")
                    
                    # Try to create an alert
                    async with self.session.post(
                        f"{API_BASE}/alerts",
                        json=TEST_ALERT_DATA,
                        headers=self.headers
                    ) as create_response:
                        if create_response.status == 200:
                            alert_data = await create_response.json()
                            print(f"✅ Created alert: {alert_data.get('title')}")
                        else:
                            print("⚠️ Could not create alert")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ System alerts failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ System alerts error: {str(e)}")
            return False
    
    async def test_analytics(self) -> bool:
        """Test analytics"""
        try:
            print("\\n🧪 Testing analytics...")
            
            async with self.session.post(
                f"{API_BASE}/analytics",
                json=TEST_ANALYTICS_REQUEST,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    analytics = await response.json()
                    print(f"✅ Retrieved analytics: {analytics.get('metric_type')} - {len(analytics.get('data', []))} data points")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Analytics failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Analytics error: {str(e)}")
            return False
    
    async def test_data_exports(self) -> bool:
        """Test data exports"""
        try:
            print("\\n🧪 Testing data exports...")
            
            # Get existing exports
            async with self.session.get(
                f"{API_BASE}/exports",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    exports = await response.json()
                    print(f"✅ Retrieved {len(exports)} data exports")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Data exports failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Data exports error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Admin Service Tests\\n")
        
        if not await self.setup():
            print("❌ Failed to setup tests")
            return
        
        # Test results
        results = {}
        
        # Run tests
        results["dashboard"] = await self.test_dashboard()
        results["school_management"] = await self.test_school_management()
        results["department_management"] = await self.test_department_management()
        results["admin_users"] = await self.test_admin_users()
        results["audit_logs"] = await self.test_audit_logs()
        results["system_alerts"] = await self.test_system_alerts()
        results["analytics"] = await self.test_analytics()
        results["data_exports"] = await self.test_data_exports()
        
        # Print summary
        print("\\n" + "="*50)
        print("📊 TEST RESULTS SUMMARY")
        print("="*50)
        
        passed = 0
        total = 0
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
            total += 1
        
        print(f"\\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Admin Service is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the service configuration and dependencies.")
        
        await self.teardown()

async def main():
    """Main test function"""
    tester = AdminServiceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

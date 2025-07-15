"""
Test script for EduNerve Assistant Service
Tests all endpoints and functionality
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8003"
API_BASE = f"{BASE_URL}/api/v1/assistant"

# Test data
TEST_USER = {
    "email": "student@test.com",
    "password": "testpassword123"
}

TEST_STUDY_PLAN = {
    "subject": "Mathematics",
    "grade_level": "Grade 10",
    "learning_objectives": [
        "Understand quadratic equations",
        "Solve linear systems",
        "Master function concepts"
    ],
    "duration_weeks": 4
}

TEST_RESOURCE_REQUEST = {
    "topic": "Quadratic Equations",
    "subject": "Mathematics",
    "grade_level": "Grade 10",
    "difficulty_level": "medium"
}

TEST_ACTIVITY = {
    "activity_type": "study_session",
    "activity_data": {
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "duration": 30,
        "completed": True
    }
}

class AssistantServiceTester:
    """Test class for Assistant Service"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.headers = {}
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 Setting up Assistant Service tests...")
        
        # Check if service is running
        if not await self.check_service_health():
            print("❌ Assistant Service is not running!")
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
    
    async def test_study_plan_creation(self) -> bool:
        """Test study plan creation"""
        try:
            print("\\n🧪 Testing study plan creation...")
            
            async with self.session.post(
                f"{API_BASE}/study-plan",
                json=TEST_STUDY_PLAN,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Study plan created successfully: {data.get('title')}")
                    return True, data.get('id')
                else:
                    error_data = await response.json()
                    print(f"❌ Study plan creation failed: {response.status} - {error_data}")
                    return False, None
        except Exception as e:
            print(f"❌ Study plan creation error: {str(e)}")
            return False, None
    
    async def test_study_plans_retrieval(self) -> bool:
        """Test study plans retrieval"""
        try:
            print("\\n🧪 Testing study plans retrieval...")
            
            async with self.session.get(
                f"{API_BASE}/study-plans",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved {len(data)} study plans")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Study plans retrieval failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Study plans retrieval error: {str(e)}")
            return False
    
    async def test_resource_generation(self) -> bool:
        """Test study resource generation"""
        try:
            print("\\n🧪 Testing study resource generation...")
            
            async with self.session.post(
                f"{API_BASE}/resources",
                json=TEST_RESOURCE_REQUEST,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Generated {len(data)} study resources")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Resource generation failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Resource generation error: {str(e)}")
            return False
    
    async def test_resources_retrieval(self) -> bool:
        """Test study resources retrieval"""
        try:
            print("\\n🧪 Testing study resources retrieval...")
            
            async with self.session.get(
                f"{API_BASE}/resources",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved {len(data)} study resources")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Resources retrieval failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Resources retrieval error: {str(e)}")
            return False
    
    async def test_activity_tracking(self) -> bool:
        """Test activity tracking"""
        try:
            print("\\n🧪 Testing activity tracking...")
            
            async with self.session.post(
                f"{API_BASE}/activity",
                json=TEST_ACTIVITY,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Activity tracked successfully: {data.get('message')}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Activity tracking failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Activity tracking error: {str(e)}")
            return False
    
    async def test_activities_retrieval(self) -> bool:
        """Test activities retrieval"""
        try:
            print("\\n🧪 Testing activities retrieval...")
            
            async with self.session.get(
                f"{API_BASE}/activities",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved {len(data)} activities")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Activities retrieval failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Activities retrieval error: {str(e)}")
            return False
    
    async def test_analytics_retrieval(self) -> bool:
        """Test learning analytics retrieval"""
        try:
            print("\\n🧪 Testing learning analytics retrieval...")
            
            async with self.session.get(
                f"{API_BASE}/analytics",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved learning analytics: {data.get('analytics_data', {}).keys()}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Analytics retrieval failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Analytics retrieval error: {str(e)}")
            return False
    
    async def test_video_search(self) -> bool:
        """Test video search"""
        try:
            print("\\n🧪 Testing video search...")
            
            async with self.session.get(
                f"{API_BASE}/videos/search",
                params={"query": "quadratic equations tutorial", "max_results": 5},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get('videos', [])
                    print(f"✅ Found {len(videos)} educational videos")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Video search failed: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Video search error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Assistant Service Tests\\n")
        
        if not await self.setup():
            print("❌ Failed to setup tests")
            return
        
        # Test results
        results = {}
        
        # Run tests
        results["study_plan_creation"] = await self.test_study_plan_creation()
        results["study_plans_retrieval"] = await self.test_study_plans_retrieval()
        results["resource_generation"] = await self.test_resource_generation()
        results["resources_retrieval"] = await self.test_resources_retrieval()
        results["activity_tracking"] = await self.test_activity_tracking()
        results["activities_retrieval"] = await self.test_activities_retrieval()
        results["analytics_retrieval"] = await self.test_analytics_retrieval()
        results["video_search"] = await self.test_video_search()
        
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
            print("🎉 All tests passed! Assistant Service is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the service configuration and dependencies.")
        
        await self.teardown()

async def main():
    """Main test function"""
    tester = AssistantServiceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

"""
EduNerve Notification Service - Test Script
Comprehensive testing for notification service endpoints
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
import pytest
from typing import Dict, Any, List

# Test configuration
BASE_URL = "http://localhost:8006"
TEST_TOKEN = "test_token_123"  # Replace with actual token
TEST_SCHOOL_ID = 1

class NotificationServiceTester:
    """Test suite for notification service"""
    
    def __init__(self, base_url: str = BASE_URL, token: str = TEST_TOKEN):
        self.base_url = base_url
        self.token = token
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else await response.text()
                    }
        except Exception as e:
            return {
                "status": 500,
                "error": str(e)
            }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        
        response = await self.make_request("GET", "/health")
        success = response["status"] == 200
        
        self.log_test(
            "Health Check",
            success,
            f"Status: {response['status']}, Data: {response.get('data', 'N/A')}"
        )
        
        return success
    
    async def test_create_notification(self) -> str:
        """Test creating a notification"""
        print("\n=== Testing Create Notification ===")
        
        notification_data = {
            "notification_type": "email",
            "subject": "Test Notification",
            "message": "This is a test notification from the API test suite.",
            "priority": "normal",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "recipient_type": "student"
                }
            ]
        }
        
        response = await self.make_request("POST", "/notifications", notification_data)
        success = response["status"] == 200
        
        notification_id = None
        if success and "data" in response:
            notification_id = response["data"].get("notification_id")
        
        self.log_test(
            "Create Notification",
            success,
            f"Status: {response['status']}, ID: {notification_id}"
        )
        
        return notification_id
    
    async def test_quick_notification(self):
        """Test quick notification endpoint"""
        print("\n=== Testing Quick Notification ===")
        
        quick_data = {
            "type": "sms",
            "recipients": ["+1234567890"],
            "message": "Quick test message",
            "priority": "high"
        }
        
        response = await self.make_request("POST", "/notifications/quick", quick_data)
        success = response["status"] == 200
        
        self.log_test(
            "Quick Notification",
            success,
            f"Status: {response['status']}, Data: {response.get('data', 'N/A')}"
        )
        
        return success
    
    async def test_bulk_notification(self):
        """Test bulk notification endpoint"""
        print("\n=== Testing Bulk Notification ===")
        
        bulk_data = {
            "type": "push",
            "subject": "Bulk Test",
            "message": "Bulk notification test message",
            "target_audience": {
                "all_students": True,
                "grade_levels": ["10", "11", "12"]
            },
            "priority": "normal"
        }
        
        response = await self.make_request("POST", "/notifications/bulk", bulk_data)
        success = response["status"] == 200
        
        self.log_test(
            "Bulk Notification",
            success,
            f"Status: {response['status']}, Data: {response.get('data', 'N/A')}"
        )
        
        return success
    
    async def test_get_notification(self, notification_id: str):
        """Test getting notification details"""
        print("\n=== Testing Get Notification ===")
        
        if not notification_id:
            self.log_test("Get Notification", False, "No notification ID provided")
            return False
        
        response = await self.make_request("GET", f"/notifications/{notification_id}")
        success = response["status"] == 200
        
        self.log_test(
            "Get Notification",
            success,
            f"Status: {response['status']}, ID: {notification_id}"
        )
        
        return success
    
    async def test_list_notifications(self):
        """Test listing notifications"""
        print("\n=== Testing List Notifications ===")
        
        response = await self.make_request("GET", "/notifications?limit=10")
        success = response["status"] == 200
        
        count = 0
        if success and "data" in response:
            count = len(response["data"]) if isinstance(response["data"], list) else 0
        
        self.log_test(
            "List Notifications",
            success,
            f"Status: {response['status']}, Count: {count}"
        )
        
        return success
    
    async def test_update_notification(self, notification_id: str):
        """Test updating a notification"""
        print("\n=== Testing Update Notification ===")
        
        if not notification_id:
            self.log_test("Update Notification", False, "No notification ID provided")
            return False
        
        update_data = {
            "subject": "Updated Test Notification",
            "priority": "high"
        }
        
        response = await self.make_request("PUT", f"/notifications/{notification_id}", update_data)
        success = response["status"] == 200
        
        self.log_test(
            "Update Notification",
            success,
            f"Status: {response['status']}, ID: {notification_id}"
        )
        
        return success
    
    async def test_create_template(self) -> str:
        """Test creating a notification template"""
        print("\n=== Testing Create Template ===")
        
        template_data = {
            "name": "Test Template",
            "description": "Template for testing purposes",
            "template_type": "email",
            "subject_template": "Hello {{name}}",
            "message_template": "This is a test message for {{name}} in {{school}}.",
            "variables": ["name", "school"],
            "category": "test"
        }
        
        response = await self.make_request("POST", "/templates", template_data)
        success = response["status"] == 200
        
        template_id = None
        if success and "data" in response:
            template_id = response["data"].get("template_id")
        
        self.log_test(
            "Create Template",
            success,
            f"Status: {response['status']}, ID: {template_id}"
        )
        
        return template_id
    
    async def test_list_templates(self):
        """Test listing templates"""
        print("\n=== Testing List Templates ===")
        
        response = await self.make_request("GET", "/templates")
        success = response["status"] == 200
        
        count = 0
        if success and "data" in response:
            count = len(response["data"]) if isinstance(response["data"], list) else 0
        
        self.log_test(
            "List Templates",
            success,
            f"Status: {response['status']}, Count: {count}"
        )
        
        return success
    
    async def test_get_template(self, template_id: str):
        """Test getting a template"""
        print("\n=== Testing Get Template ===")
        
        if not template_id:
            self.log_test("Get Template", False, "No template ID provided")
            return False
        
        response = await self.make_request("GET", f"/templates/{template_id}")
        success = response["status"] == 200
        
        self.log_test(
            "Get Template",
            success,
            f"Status: {response['status']}, ID: {template_id}"
        )
        
        return success
    
    async def test_update_template(self, template_id: str):
        """Test updating a template"""
        print("\n=== Testing Update Template ===")
        
        if not template_id:
            self.log_test("Update Template", False, "No template ID provided")
            return False
        
        update_data = {
            "name": "Updated Test Template",
            "description": "Updated template description"
        }
        
        response = await self.make_request("PUT", f"/templates/{template_id}", update_data)
        success = response["status"] == 200
        
        self.log_test(
            "Update Template",
            success,
            f"Status: {response['status']}, ID: {template_id}"
        )
        
        return success
    
    async def test_analytics(self):
        """Test analytics endpoint"""
        print("\n=== Testing Analytics ===")
        
        response = await self.make_request("GET", "/analytics/summary?days=7")
        success = response["status"] == 200
        
        self.log_test(
            "Analytics Summary",
            success,
            f"Status: {response['status']}, Data: {response.get('data', 'N/A')}"
        )
        
        return success
    
    async def test_notification_settings(self):
        """Test notification settings"""
        print("\n=== Testing Notification Settings ===")
        
        # Get settings
        response = await self.make_request("GET", "/settings")
        success = response["status"] == 200
        
        self.log_test(
            "Get Settings",
            success,
            f"Status: {response['status']}"
        )
        
        if success:
            # Update settings
            update_data = {
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True
            }
            
            response = await self.make_request("PUT", "/settings", update_data)
            success = response["status"] == 200
            
            self.log_test(
                "Update Settings",
                success,
                f"Status: {response['status']}"
            )
        
        return success
    
    async def test_admin_endpoints(self):
        """Test admin endpoints"""
        print("\n=== Testing Admin Endpoints ===")
        
        # Test queue status
        response = await self.make_request("GET", "/admin/queue-status")
        success = response["status"] in [200, 403]  # 403 if not admin
        
        self.log_test(
            "Queue Status",
            success,
            f"Status: {response['status']}"
        )
        
        # Test manual queue processing
        response = await self.make_request("POST", "/admin/process-queue")
        success = response["status"] in [200, 403]  # 403 if not admin
        
        self.log_test(
            "Manual Queue Process",
            success,
            f"Status: {response['status']}"
        )
        
        return success
    
    async def test_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid notification
        invalid_data = {
            "notification_type": "invalid",
            "recipients": []
        }
        
        response = await self.make_request("POST", "/notifications", invalid_data)
        success = response["status"] >= 400
        
        self.log_test(
            "Invalid Notification",
            success,
            f"Status: {response['status']} (Expected 4xx)"
        )
        
        # Test non-existent notification
        response = await self.make_request("GET", "/notifications/nonexistent")
        success = response["status"] == 404
        
        self.log_test(
            "Non-existent Notification",
            success,
            f"Status: {response['status']} (Expected 404)"
        )
        
        return success
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting EduNerve Notification Service Test Suite")
        print("=" * 60)
        
        # Basic tests
        await self.test_health_check()
        
        # Core functionality tests
        notification_id = await self.test_create_notification()
        await self.test_quick_notification()
        await self.test_bulk_notification()
        await self.test_get_notification(notification_id)
        await self.test_list_notifications()
        await self.test_update_notification(notification_id)
        
        # Template tests
        template_id = await self.test_create_template()
        await self.test_list_templates()
        await self.test_get_template(template_id)
        await self.test_update_template(template_id)
        
        # Analytics and settings
        await self.test_analytics()
        await self.test_notification_settings()
        
        # Admin tests
        await self.test_admin_endpoints()
        
        # Error handling
        await self.test_error_handling()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        # Save results to file
        self.save_test_results()
    
    def save_test_results(self):
        """Save test results to file"""
        try:
            results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(self.test_results),
                    "passed": sum(1 for r in self.test_results if r["success"]),
                    "failed": sum(1 for r in self.test_results if not r["success"]),
                    "results": self.test_results
                }, f, indent=2)
            
            print(f"Test results saved to: {results_file}")
        except Exception as e:
            print(f"Failed to save test results: {e}")

async def main():
    """Main test function"""
    # Check if service is running
    print("🔍 Checking if notification service is running...")
    
    async with NotificationServiceTester() as tester:
        try:
            health_response = await tester.make_request("GET", "/health")
            if health_response["status"] != 200:
                print(f"❌ Service not responding. Status: {health_response['status']}")
                print("Please make sure the notification service is running on http://localhost:8006")
                return
            
            print("✅ Service is running!")
            
            # Run all tests
            await tester.run_all_tests()
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            print("Please check your service configuration and try again.")

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())

"""
EduNerve API Gateway - Test Script
Test script to verify the API Gateway functionality
"""

import requests
import json
import time
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any

# Base URL for the API Gateway
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"

class APIGatewayTester:
    def __init__(self):
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_school_id = None
        self.test_results = {}
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, success: bool, message: str = ""):
        """Print test result"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        self.test_results[test_name] = success
    
    def test_health_check(self):
        """Test the health check endpoint"""
        self.print_header("Testing Health Check")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_test("Health Check", True, f"Status: {data.get('status', 'unknown')}")
                print(f"   Services: {data.get('services', [])}")
                print(f"   Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.print_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Health Check", False, f"Error: {e}")
            return False
    
    def test_service_status(self):
        """Test service status endpoint"""
        self.print_header("Testing Service Status")
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/services", timeout=10)
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', [])
                self.print_test("Service Status", True, f"Found {len(services)} services")
                
                for service in services:
                    status_icon = "✅" if service['status'] == 'healthy' else "❌"
                    print(f"   {status_icon} {service['name']}: {service['status']}")
                
                return True
            else:
                self.print_test("Service Status", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Service Status", False, f"Error: {e}")
            return False
    
    def test_authentication_flow(self):
        """Test authentication through gateway"""
        self.print_header("Testing Authentication Flow")
        
        # Step 1: Create a test school
        school_data = {
            "name": "Gateway Test School",
            "code": "GTS001",
            "address": "Test Address, Lagos, Nigeria",
            "phone": "+2348123456789",
            "email": "gateway@test.edu.ng",
            "principal_name": "Mr. Gateway Test"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/schools", json=school_data, timeout=10)
            if response.status_code == 201:
                school_response = response.json()
                self.test_school_id = school_response.get("id")
                self.print_test("School Creation", True, f"School ID: {self.test_school_id}")
            else:
                # Try to get existing school
                response = requests.get(f"{BASE_URL}/api/v1/auth/schools", timeout=10)
                if response.status_code == 200:
                    schools = response.json()
                    if schools:
                        self.test_school_id = schools[0]["id"]
                        self.print_test("School Creation", True, f"Using existing school ID: {self.test_school_id}")
                    else:
                        self.print_test("School Creation", False, "No schools found")
                        return False
        except Exception as e:
            self.print_test("School Creation", False, f"Error: {e}")
            return False
        
        # Step 2: Test user registration
        admin_data = {
            "email": "gateway_admin@test.com",
            "password": "AdminPass123",
            "first_name": "Gateway",
            "last_name": "Admin",
            "role": "admin",
            "school_id": self.test_school_id
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=admin_data, timeout=10)
            if response.status_code in [200, 201]:
                self.print_test("Admin Registration", True, "Admin user created")
            else:
                self.print_test("Admin Registration", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Admin Registration", False, f"Error: {e}")
        
        # Step 3: Test login
        login_data = {
            "email": "gateway_admin@test.com",
            "password": "AdminPass123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                login_response = response.json()
                self.admin_token = login_response.get("access_token")
                self.print_test("Admin Login", True, f"Token received: {self.admin_token[:20]}...")
                return True
            else:
                self.print_test("Admin Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Admin Login", False, f"Error: {e}")
            return False
    
    def test_authenticated_requests(self):
        """Test authenticated requests through gateway"""
        if not self.admin_token:
            self.print_test("Authenticated Requests", False, "No admin token available")
            return False
        
        self.print_header("Testing Authenticated Requests")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test getting current user
        try:
            response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                self.print_test("Get Current User", True, f"User: {user_data.get('first_name', 'Unknown')}")
            else:
                self.print_test("Get Current User", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Current User", False, f"Error: {e}")
        
        # Test getting users list
        try:
            response = requests.get(f"{BASE_URL}/api/v1/auth/users", headers=headers, timeout=10)
            if response.status_code == 200:
                users = response.json()
                self.print_test("Get Users List", True, f"Found {len(users)} users")
            else:
                self.print_test("Get Users List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Users List", False, f"Error: {e}")
        
        # Test getting stats
        try:
            response = requests.get(f"{BASE_URL}/api/v1/auth/stats", headers=headers, timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.print_test("Get Stats", True, f"Stats retrieved: {stats}")
            else:
                self.print_test("Get Stats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Get Stats", False, f"Error: {e}")
        
        return True
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        self.print_header("Testing Rate Limiting")
        
        # Test login rate limiting (5 per minute)
        login_data = {
            "email": "test@invalid.com",
            "password": "invalid"
        }
        
        success_count = 0
        rate_limited = False
        
        for i in range(7):  # Try 7 requests (should be rate limited after 5)
            try:
                response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=5)
                if response.status_code == 429:  # Rate limited
                    rate_limited = True
                    break
                success_count += 1
            except Exception as e:
                break
            
            time.sleep(0.1)  # Small delay between requests
        
        if rate_limited:
            self.print_test("Rate Limiting", True, f"Rate limited after {success_count} requests")
        else:
            self.print_test("Rate Limiting", False, "Rate limiting not working")
        
        return rate_limited
    
    def test_error_handling(self):
        """Test error handling"""
        self.print_header("Testing Error Handling")
        
        # Test 404 error
        try:
            response = requests.get(f"{BASE_URL}/api/v1/nonexistent/endpoint", timeout=10)
            if response.status_code == 404:
                self.print_test("404 Error Handling", True, "404 error properly handled")
            else:
                self.print_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.print_test("404 Error Handling", False, f"Error: {e}")
        
        # Test invalid service
        try:
            response = requests.get(f"{BASE_URL}/api/v1/invalid_service/test", timeout=10)
            if response.status_code in [404, 503]:
                self.print_test("Invalid Service", True, "Invalid service properly handled")
            else:
                self.print_test("Invalid Service", False, f"Expected 404/503, got {response.status_code}")
        except Exception as e:
            self.print_test("Invalid Service", False, f"Error: {e}")
        
        return True
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        self.print_header("Testing WebSocket Connection")
        
        try:
            # Test WebSocket connection
            uri = f"{WS_BASE_URL}/ws/test_user_123"
            async with websockets.connect(uri) as websocket:
                # Send a test message
                test_message = {
                    "type": "test",
                    "message": "Hello from test client",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    self.print_test("WebSocket Connection", True, "WebSocket connection successful")
                    print(f"   Received: {response}")
                except asyncio.TimeoutError:
                    self.print_test("WebSocket Connection", True, "WebSocket connected (no response expected)")
                
                return True
        except Exception as e:
            self.print_test("WebSocket Connection", False, f"Error: {e}")
            return False
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        self.print_header("Testing Metrics Endpoint")
        
        try:
            response = requests.get(f"{BASE_URL}/metrics", timeout=10)
            if response.status_code == 200:
                metrics_data = response.text
                if "gateway_requests_total" in metrics_data:
                    self.print_test("Metrics Endpoint", True, "Metrics available")
                    print(f"   Metrics length: {len(metrics_data)} characters")
                else:
                    self.print_test("Metrics Endpoint", False, "Expected metrics not found")
            else:
                self.print_test("Metrics Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Metrics Endpoint", False, f"Error: {e}")
        
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting EduNerve API Gateway Tests")
        print(f"Target: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run synchronous tests
        self.test_health_check()
        self.test_service_status()
        self.test_authentication_flow()
        self.test_authenticated_requests()
        self.test_rate_limiting()
        self.test_error_handling()
        self.test_metrics_endpoint()
        
        # Run WebSocket test
        try:
            asyncio.run(self.test_websocket_connection())
        except Exception as e:
            self.print_test("WebSocket Test", False, f"Error: {e}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"   - {test_name}")
        
        print("\n🎯 Next Steps:")
        print("1. Check that all microservices are running")
        print("2. Verify database connections")
        print("3. Test with frontend application")
        print("4. Monitor logs for any errors")
        print("5. Check API documentation at: http://localhost:8000/docs")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Gateway is ready for production.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please review and fix issues.")


def main():
    """Main function to run tests"""
    tester = APIGatewayTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
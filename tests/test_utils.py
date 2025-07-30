"""
Test utilities and helper functions for the comprehensive test suite.
"""

import asyncio
import httpx
import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class ServiceHealthChecker:
    """Utility to check if services are running and healthy."""
    
    def __init__(self, service_urls: Dict[str, str]):
        self.service_urls = service_urls
        self.timeout = 5.0
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check if a specific service is healthy."""
        url = self.service_urls.get(service_name)
        if not url:
            return {"status": "unknown", "error": "URL not configured"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try health endpoint first
                health_endpoints = ["/health", "/healthz", "/status", "/"]
                
                for endpoint in health_endpoints:
                    try:
                        response = await client.get(f"{url}{endpoint}")
                        if response.status_code == 200:
                            return {
                                "status": "healthy",
                                "url": url,
                                "endpoint": endpoint,
                                "response_time": response.elapsed.total_seconds()
                            }
                    except Exception:
                        continue
                
                # If no health endpoint worked, try a basic connection
                try:
                    response = await client.get(url)
                    return {
                        "status": "running",
                        "url": url,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                except Exception as e:
                    return {
                        "status": "unreachable", 
                        "url": url,
                        "error": str(e)
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }
    
    async def check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all configured services."""
        tasks = []
        for service_name in self.service_urls.keys():
            task = self.check_service_health(service_name)
            tasks.append((service_name, task))
        
        results = {}
        for service_name, task in tasks:
            results[service_name] = await task
            
        return results
    
    def print_health_report(self, results: Dict[str, Dict[str, Any]]):
        """Print a formatted health report."""
        print("\n" + "="*60)
        print("SERVICE HEALTH REPORT")
        print("="*60)
        
        healthy_count = 0
        total_count = len(results)
        
        for service_name, result in results.items():
            status = result.get("status", "unknown")
            url = result.get("url", "N/A")
            
            status_symbol = {
                "healthy": "✅",
                "running": "🟡", 
                "unreachable": "❌",
                "error": "💥",
                "unknown": "❓"
            }.get(status, "❓")
            
            print(f"{status_symbol} {service_name:<20} | {status:<12} | {url}")
            
            if status in ["healthy", "running"]:
                healthy_count += 1
                if "response_time" in result:
                    print(f"   └── Response time: {result['response_time']:.3f}s")
            else:
                error = result.get("error", "No additional info")
                print(f"   └── Error: {error}")
        
        print("-"*60)
        print(f"Summary: {healthy_count}/{total_count} services accessible")
        print("="*60)


class TestDataManager:
    """Manage test data creation and cleanup."""
    
    def __init__(self):
        self.created_users = []
        self.created_resources = []
    
    def generate_unique_user(self, base_data: Dict[str, str]) -> Dict[str, str]:
        """Generate a unique user for testing."""
        timestamp = str(int(time.time() * 1000))
        unique_data = base_data.copy()
        unique_data["email"] = f"test_{timestamp}@example.com"
        unique_data["full_name"] = f"Test User {timestamp}"
        
        self.created_users.append(unique_data)
        return unique_data
    
    async def cleanup_test_data(self, service_urls: Dict[str, str]):
        """Clean up test data after tests complete."""
        # This would implement cleanup logic for each service
        # For now, just log what would be cleaned up
        print(f"\nCleaning up {len(self.created_users)} test users...")
        print(f"Cleaning up {len(self.created_resources)} test resources...")


class APITestHelper:
    """Helper functions for API testing."""
    
    @staticmethod
    async def test_endpoint_exists(url: str, method: str = "GET", 
                                 data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test if an endpoint exists and returns appropriate response."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data or {})
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data or {})
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    return {"exists": False, "error": f"Unsupported method: {method}"}
                
                return {
                    "exists": response.status_code != 404,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "content_type": response.headers.get("content-type", ""),
                    "has_json": response.headers.get("content-type", "").startswith("application/json")
                }
                
        except httpx.ConnectError:
            return {"exists": False, "error": "Connection failed"}
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    @staticmethod
    async def test_authentication_required(url: str, method: str = "GET") -> bool:
        """Test if an endpoint requires authentication."""
        result = await APITestHelper.test_endpoint_exists(url, method)
        return result.get("status_code") == 401
    
    @staticmethod
    def validate_json_response(response_data: Any, expected_fields: List[str]) -> Dict[str, Any]:
        """Validate that a JSON response has expected fields."""
        if not isinstance(response_data, dict):
            return {"valid": False, "error": "Response is not a JSON object"}
        
        missing_fields = []
        present_fields = []
        
        for field in expected_fields:
            if field in response_data:
                present_fields.append(field)
            else:
                missing_fields.append(field)
        
        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "present_fields": present_fields,
            "total_fields": len(response_data),
            "response_keys": list(response_data.keys())
        }


class PerformanceTestHelper:
    """Helper for basic performance testing."""
    
    @staticmethod
    async def measure_response_time(url: str, iterations: int = 5) -> Dict[str, float]:
        """Measure average response time for an endpoint."""
        times = []
        
        async with httpx.AsyncClient() as client:
            for _ in range(iterations):
                start_time = time.time()
                try:
                    response = await client.get(url)
                    end_time = time.time()
                    times.append(end_time - start_time)
                except Exception:
                    continue
        
        if not times:
            return {"error": "No successful requests"}
        
        return {
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "iterations": len(times)
        }
    
    @staticmethod
    async def test_concurrent_requests(url: str, concurrent_users: int = 10) -> Dict[str, Any]:
        """Test concurrent request handling."""
        async def make_request():
            try:
                async with httpx.AsyncClient() as client:
                    start_time = time.time()
                    response = await client.get(url)
                    end_time = time.time()
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Create concurrent requests
        tasks = [make_request() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        response_times = [r["response_time"] for r in successful]
        
        return {
            "total_requests": concurrent_users,
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / concurrent_users * 100,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }


class TestReportGenerator:
    """Generate comprehensive test reports."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_service_health_report(self, health_results: Dict[str, Dict[str, Any]]):
        """Generate service health report."""
        report_file = self.output_dir / "service_health_report.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "results": health_results,
                "summary": {
                    "total_services": len(health_results),
                    "healthy_services": len([r for r in health_results.values() 
                                           if r.get("status") in ["healthy", "running"]]),
                    "unhealthy_services": len([r for r in health_results.values() 
                                             if r.get("status") not in ["healthy", "running"]])
                }
            }, f, indent=2)
        
        print(f"Service health report saved to: {report_file}")
    
    def generate_api_coverage_report(self, api_test_results: Dict[str, Any]):
        """Generate API endpoint coverage report."""
        report_file = self.output_dir / "api_coverage_report.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "api_coverage": api_test_results
            }, f, indent=2)
        
        print(f"API coverage report saved to: {report_file}")


# Global test utilities instance
test_data_manager = TestDataManager()


def pytest_configure(config):
    """Configure pytest with custom markers and setup."""
    config.addinivalue_line(
        "markers", "smoke: Quick smoke tests for basic functionality"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )


async def run_pre_test_health_check(service_urls: Dict[str, str]) -> bool:
    """Run health check before starting tests."""
    print("Running pre-test health check...")
    
    health_checker = ServiceHealthChecker(service_urls)
    results = await health_checker.check_all_services()
    health_checker.print_health_report(results)
    
    # Check if at least auth service and gateway are running
    critical_services = ["auth", "gateway"]
    critical_healthy = all(
        results.get(svc, {}).get("status") in ["healthy", "running"] 
        for svc in critical_services
    )
    
    if not critical_healthy:
        print("\n⚠️  WARNING: Critical services (auth, gateway) are not running!")
        print("Some tests will be skipped.")
        return False
    
    return True

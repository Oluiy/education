#!/usr/bin/env python3
"""
Comprehensive Test Runner for EduNerve Monorepo
Runs all tests for backend microservices and API gateway.
"""

import sys
import subprocess
import asyncio
import argparse
from pathlib import Path

# Add tests directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from test_utils import (
    ServiceHealthChecker, 
    TestDataManager, 
    TestReportGenerator,
    run_pre_test_health_check
)


class TestRunner:
    """Main test runner for the entire test suite."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = Path(__file__).parent
        self.reports_dir = self.tests_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Service URLs for testing
        self.service_urls = {
            "auth": "http://localhost:8001",
            "admin": "http://localhost:8002", 
            "assistant": "http://localhost:8003",
            "content-quiz": "http://localhost:8004",
            "file-storage": "http://localhost:8005",
            "notification": "http://localhost:8006",
            "progress": "http://localhost:8007",
            "sync-messaging": "http://localhost:8008",
            "gateway": "http://localhost:8000"
        }
    
    def install_test_dependencies(self):
        """Install test dependencies."""
        print("Installing test dependencies...")
        requirements_file = self.tests_dir / "requirements.txt"
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True, text=True)
            print("✅ Test dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    async def run_health_check(self):
        """Run comprehensive health check."""
        print("\n" + "="*60)
        print("RUNNING PRE-TEST HEALTH CHECK")
        print("="*60)
        
        health_checker = ServiceHealthChecker(self.service_urls)
        results = await health_checker.check_all_services()
        health_checker.print_health_report(results)
        
        # Generate health report
        report_generator = TestReportGenerator(self.reports_dir)
        report_generator.generate_service_health_report(results)
        
        return results
    
    def run_structure_tests(self):
        """Run structure and existence tests."""
        print("\n" + "="*60)
        print("RUNNING STRUCTURE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest", 
            str(self.tests_dir / "test_structure.py"),
            "-v", "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Structure tests failed: {e}")
            return False
    
    def run_api_tests(self):
        """Run API endpoint tests.""" 
        print("\n" + "="*60)
        print("RUNNING API ENDPOINT TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir / "test_api_endpoints.py"), 
            "-v", "--tb=short", "-x"  # Stop on first failure
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ API tests failed: {e}")
            return False
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir / "test_integration.py"),
            "-v", "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Integration tests failed: {e}")
            return False
    
    def run_all_tests_with_coverage(self):
        """Run all tests with coverage report."""
        print("\n" + "="*60)
        print("RUNNING FULL TEST SUITE WITH COVERAGE")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-v", 
            "--cov=services",
            "--cov=api-gateway", 
            "--cov-report=html:" + str(self.reports_dir / "coverage"),
            "--cov-report=term-missing",
            "--html=" + str(self.reports_dir / "test_report.html"),
            "--self-contained-html"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            print(f"\n📊 Test reports generated in: {self.reports_dir}")
            print(f"   - HTML Report: {self.reports_dir / 'test_report.html'}")
            print(f"   - Coverage Report: {self.reports_dir / 'coverage' / 'index.html'}")
            
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Full test suite failed: {e}")
            return False
    
    def run_quick_smoke_tests(self):
        """Run quick smoke tests only."""
        print("\n" + "="*60)
        print("RUNNING QUICK SMOKE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.tests_dir),
            "-v", "-m", "smoke or not slow",
            "--tb=short", "--maxfail=5"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Smoke tests failed: {e}")
            return False
    
    def generate_final_report(self, test_results):
        """Generate final comprehensive report."""
        print("\n" + "="*60)
        print("FINAL TEST REPORT")
        print("="*60)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Test Summary:")
        print(f"   Total Test Suites: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📁 Reports Location: {self.reports_dir}")
        
        if failed_tests > 0:
            print(f"\n⚠️  Failed Test Suites:")
            for test_name, result in test_results.items():
                if not result:
                    print(f"   - {test_name}")
        
        return failed_tests == 0


async def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="EduNerve Comprehensive Test Runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick smoke tests only")
    parser.add_argument("--structure-only", action="store_true",
                       help="Run structure tests only")
    parser.add_argument("--api-only", action="store_true", 
                       help="Run API tests only")
    parser.add_argument("--integration-only", action="store_true",
                       help="Run integration tests only")
    parser.add_argument("--no-deps", action="store_true",
                       help="Skip dependency installation")
    parser.add_argument("--no-health", action="store_true",
                       help="Skip health check")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    test_results = {}
    
    print("🚀 EduNerve Comprehensive Test Suite")
    print("="*60)
    
    # Install dependencies
    if not args.no_deps:
        if not runner.install_test_dependencies():
            print("❌ Failed to install dependencies. Exiting.")
            return False
    
    # Run health check
    if not args.no_health:
        await runner.run_health_check()
    
    # Run tests based on arguments
    if args.quick:
        test_results["smoke_tests"] = runner.run_quick_smoke_tests()
    elif args.structure_only:
        test_results["structure_tests"] = runner.run_structure_tests()
    elif args.api_only:
        test_results["api_tests"] = runner.run_api_tests()
    elif args.integration_only:
        test_results["integration_tests"] = runner.run_integration_tests()
    else:
        # Run full comprehensive test suite
        test_results["structure_tests"] = runner.run_structure_tests()
        test_results["api_tests"] = runner.run_api_tests()
        test_results["integration_tests"] = runner.run_integration_tests()
        test_results["full_coverage"] = runner.run_all_tests_with_coverage()
    
    # Generate final report
    success = runner.generate_final_report(test_results)
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return True
    else:
        print("\n💥 Some tests failed. Check the reports for details.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⛔ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)

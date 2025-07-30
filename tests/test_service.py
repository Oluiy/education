#!/usr/bin/env python3
"""
Individual Service Test Runner
Run tests for specific services or components.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_service_tests(service_name, test_type="all"):
    """Run tests for a specific service."""
    project_root = Path(__file__).parent.parent
    tests_dir = Path(__file__).parent
    
    print(f"🧪 Running {test_type} tests for {service_name}")
    print("="*50)
    
    if test_type == "structure":
        # Run structure tests for specific service
        cmd = [
            sys.executable, "-m", "pytest",
            str(tests_dir / "test_structure.py"),
            "-v", "-k", service_name
        ]
    elif test_type == "api":
        # Run API tests for specific service  
        cmd = [
            sys.executable, "-m", "pytest",
            str(tests_dir / "test_api_endpoints.py"),
            "-v", "-k", service_name
        ]
    elif test_type == "integration":
        # Run integration tests involving the service
        cmd = [
            sys.executable, "-m", "pytest", 
            str(tests_dir / "test_integration.py"),
            "-v", "-k", service_name
        ]
    else:
        # Run all tests for the service
        cmd = [
            sys.executable, "-m", "pytest",
            str(tests_dir),
            "-v", "-k", service_name
        ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run {service_name} tests: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for specific services")
    parser.add_argument("service", help="Service name (auth, admin, gateway, etc.)")
    parser.add_argument("--type", choices=["structure", "api", "integration", "all"],
                       default="all", help="Type of tests to run")
    
    args = parser.parse_args()
    
    success = run_service_tests(args.service, args.type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

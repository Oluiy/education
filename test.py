#!/usr/bin/env python3
"""
Root-level test runner for EduNerve project.
This script provides easy access to the comprehensive test suite.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run the comprehensive test suite."""
    project_root = Path(__file__).parent
    test_runner = project_root / "tests" / "run_tests.py"
    
    if not test_runner.exists():
        print("❌ Test runner not found. Please ensure tests/run_tests.py exists.")
        return False
    
    # Pass all arguments to the test runner
    cmd = [sys.executable, str(test_runner)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Test runner script for the planning scraper package.

This script runs the test suite and provides a summary of results.
"""

import sys
import subprocess
from pathlib import Path


def run_pytest():
    """Run tests using pytest."""
    print("\n" + "="*70)
    print("RUNNING TESTS WITH PYTEST")
    print("="*70 + "\n")
    
    cmd = [
        "pytest",
        "tests/",
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--cov=pipeline",  # Coverage for pipeline package
        "--cov-report=term-missing",  # Show missing lines
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def run_unittest():
    """Run tests using unittest (fallback if pytest not available)."""
    print("\n" + "="*70)
    print("RUNNING TESTS WITH UNITTEST")
    print("="*70 + "\n")
    
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "tests/",
        "-v",
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


def check_pytest_available():
    """Check if pytest is installed."""
    try:
        subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Run the appropriate test suite."""
    # Check if we're in the right directory
    if not Path("tests").exists():
        print("Error: tests/ directory not found")
        print("Please run this script from the project root directory")
        return 1
    
    if not Path("pipeline").exists():
        print("Error: pipeline/ directory not found")
        print("Please run this script from the project root directory")
        return 1
    
    # Run tests with pytest if available, otherwise use unittest
    if check_pytest_available():
        returncode = run_pytest()
    else:
        print("pytest not found, falling back to unittest")
        print("Install pytest for better test output: pip install pytest pytest-cov")
        returncode = run_unittest()
    
    # Print summary
    print("\n" + "="*70)
    if returncode == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("="*70 + "\n")
    
    return returncode


if __name__ == "__main__":
    sys.exit(main())

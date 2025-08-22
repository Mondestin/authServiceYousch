#!/usr/bin/env python3
"""
Comprehensive test runner for AuthService
Runs all tests with various configurations and generates reports
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command, description, capture_output=False):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"📝 Command: {command}")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            if capture_output and result.stderr:
                print(f"Error output: {result.stderr}")
            return result
    
    except Exception as e:
        print(f"💥 Error running {description}: {e}")
        return None


def install_test_dependencies():
    """Install test dependencies"""
    print("\n📦 Installing test dependencies...")
    
    # Check if requirements-test.txt exists
    test_requirements = project_root / "requirements-test.txt"
    if not test_requirements.exists():
        print("❌ requirements-test.txt not found")
        return False
    
    # Install test dependencies
    command = f"pip install -r {test_requirements}"
    result = run_command(command, "Installing test dependencies")
    
    return result.returncode == 0 if result else False


def run_unit_tests(verbose=False, coverage=False, parallel=False):
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/test_models.py tests/test_schemas.py tests/test_core.py")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    if coverage:
        command_parts.append("--cov=app --cov-report=html --cov-report=term-missing")
    
    if parallel:
        command_parts.append("-n auto")
    
    # Add other useful options
    command_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "Unit tests")
    
    return result.returncode == 0 if result else False


def run_api_tests(verbose=False, coverage=False):
    """Run API tests"""
    print("\n🌐 Running API tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/test_api.py")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    if coverage:
        command_parts.append("--cov=app.api --cov-report=html --cov-report=term-missing")
    
    # Add other useful options
    command_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "API tests")
    
    return result.returncode == 0 if result else False


def run_integration_tests(verbose=False, coverage=False):
    """Run integration tests"""
    print("\n🔗 Running integration tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    if coverage:
        command_parts.append("--cov=app --cov-report=html --cov-report=term-missing")
    
    # Add markers for integration tests
    command_parts.extend([
        "-m integration",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "Integration tests")
    
    return result.returncode == 0 if result else False


def run_security_tests(verbose=False):
    """Run security tests"""
    print("\n🔒 Running security tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    # Add markers for security tests
    command_parts.extend([
        "-m security",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "Security tests")
    
    return result.returncode == 0 if result else False


def run_performance_tests(verbose=False):
    """Run performance tests"""
    print("\n⚡ Running performance tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    # Add markers for performance tests
    command_parts.extend([
        "-m slow",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "Performance tests")
    
    return result.returncode == 0 if result else False


def run_all_tests(verbose=False, coverage=False, parallel=False):
    """Run all tests"""
    print("\n🎯 Running all tests...")
    
    # Build pytest command
    command_parts = ["python -m pytest"]
    
    # Add test paths
    command_parts.append("tests/")
    
    # Add options
    if verbose:
        command_parts.append("-v")
    
    if coverage:
        command_parts.append("--cov=app --cov-report=html --cov-report=term-missing")
    
    if parallel:
        command_parts.append("-n auto")
    
    # Add other useful options
    command_parts.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    command = " ".join(command_parts)
    result = run_command(command, "All tests")
    
    return result.returncode == 0 if result else False


def generate_coverage_report():
    """Generate coverage report"""
    print("\n📊 Generating coverage report...")
    
    command = "coverage html --directory=htmlcov"
    result = run_command(command, "Coverage report generation")
    
    if result and result.returncode == 0:
        print("📁 Coverage report generated in htmlcov/ directory")
        print("🌐 Open htmlcov/index.html in your browser to view the report")
    
    return result.returncode == 0 if result else False


def run_code_quality_checks():
    """Run code quality checks"""
    print("\n🔍 Running code quality checks...")
    
    checks = [
        ("black --check app/", "Code formatting check (Black)"),
        ("flake8 app/", "Linting check (Flake8)"),
        ("isort --check-only app/", "Import sorting check (isort)"),
        ("mypy app/", "Type checking (MyPy)")
    ]
    
    all_passed = True
    
    for command, description in checks:
        result = run_command(command, description, capture_output=True)
        if not result or result.returncode != 0:
            all_passed = False
    
    return all_passed


def run_security_checks():
    """Run security checks"""
    print("\n🛡️ Running security checks...")
    
    checks = [
        ("bandit -r app/", "Security linting (Bandit)"),
        ("safety check", "Dependency security check (Safety)")
    ]
    
    all_passed = True
    
    for command, description in checks:
        result = run_command(command, description, capture_output=True)
        if not result or result.returncode != 0:
            all_passed = False
    
    return all_passed


def create_test_summary(results):
    """Create test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for test_name, result in results.items():
            if not result:
                print(f"   {test_name}")
    
    print("\n" + "="*60)
    
    return passed_tests == total_tests


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run AuthService tests")
    parser.add_argument("--test-type", choices=["unit", "api", "integration", "security", "performance", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--quality", "-q", action="store_true", help="Run code quality checks")
    parser.add_argument("--security-check", "-s", action="store_true", help="Run security checks")
    parser.add_argument("--install-deps", "-i", action="store_true", help="Install test dependencies")
    
    args = parser.parse_args()
    
    print("🚀 AuthService Test Runner")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project root: {project_root}")
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("❌ Failed to install test dependencies")
            sys.exit(1)
    
    # Run tests based on type
    results = {}
    
    if args.test_type == "unit" or args.test_type == "all":
        results["Unit Tests"] = run_unit_tests(args.verbose, args.coverage, args.parallel)
    
    if args.test_type == "api" or args.test_type == "all":
        results["API Tests"] = run_api_tests(args.verbose, args.coverage)
    
    if args.test_type == "integration" or args.test_type == "all":
        results["Integration Tests"] = run_integration_tests(args.verbose, args.coverage)
    
    if args.test_type == "security" or args.test_type == "all":
        results["Security Tests"] = run_security_tests(args.verbose)
    
    if args.test_type == "performance" or args.test_type == "all":
        results["Performance Tests"] = run_performance_tests(args.verbose)
    
    # Run additional checks if requested
    if args.quality:
        results["Code Quality"] = run_code_quality_checks()
    
    if args.security_check:
        results["Security Checks"] = run_security_checks()
    
    # Generate coverage report if requested
    if args.coverage:
        generate_coverage_report()
    
    # Create summary
    all_passed = create_test_summary(results)
    
    # Exit with appropriate code
    if all_passed:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
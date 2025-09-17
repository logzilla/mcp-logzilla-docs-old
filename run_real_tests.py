#!/usr/bin/env python3
"""
Test runner for real implementation tests.
Provides convenient commands for running different test categories.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run real implementation tests")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", 
                       help="Model name to use for testing")
    parser.add_argument("--device", default="cpu", help="Device to use (cpu/cuda)")
    parser.add_argument("--keep-data", action="store_true", help="Keep test data after completion")
    parser.add_argument("--category", choices=["unit", "integration", "all"], default="all",
                       help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set environment variables
    env = os.environ.copy()
    env["TEST_MODEL_NAME"] = args.model
    env["TEST_DEVICE"] = args.device
    env["SKIP_SLOW_TESTS"] = "true" if args.fast else "false"
    if args.keep_data:
        env["KEEP_TEST_DATA"] = "true"
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    # Add test files
    test_files = [
        "tests/test_models.py",
        "tests/test_index_builder_real.py", 
        "tests/test_search_engine_real.py",
        "tests/test_server_real.py",
        "tests/test_server_app_factory_real.py",
        "tests/test_integration_real.py"
    ]
    
    cmd.extend(test_files)
    
    # Add markers
    markers = []
    if args.fast:
        markers.append("not slow")
    if args.category != "all":
        markers.append(args.category)
    
    if markers:
        cmd.extend(["-m", " and ".join(markers)])
    
    # Run tests
    print("Real Implementation Test Runner")
    print(f"Model: {args.model}")
    print(f"Device: {args.device}")
    print(f"Category: {args.category}")
    print(f"Skip slow tests: {args.fast}")
    
    success = run_command(cmd, "Real implementation tests")
    
    if success:
        print(f"\n🎉 All tests passed!")
        print("\nTo run specific test categories:")
        print("  python run_real_tests.py --fast          # Skip slow tests")
        print("  python run_real_tests.py --category unit # Unit tests only")
        print("  python run_real_tests.py --verbose       # Detailed output")
    else:
        print(f"\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

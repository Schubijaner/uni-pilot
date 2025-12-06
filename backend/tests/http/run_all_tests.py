#!/usr/bin/env python3
"""
Run all HTTP test scripts in sequence.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import test functions
from tests.http.test_01_auth import test_01_auth
from tests.http.test_02_onboarding import test_02_onboarding
from tests.http.test_03_user_profile import test_03_user_profile
from tests.http.test_04_modules import test_04_modules
from tests.http.test_05_roadmaps import test_05_roadmaps
from tests.http.test_06_chat import test_06_chat


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_colored(message: str, color: str = Colors.NC):
    print(f"{color}{message}{Colors.NC}")


def main():
    """Run all test suites."""
    print_colored("=" * 70, Colors.BLUE)
    print_colored("Uni Pilot API - Complete Test Suite", Colors.BLUE)
    print_colored("=" * 70, Colors.BLUE)
    print()
    
    results = []
    
    # Test Suite 1: Authentication
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_01_auth()
    results.append(("01 - Authentication", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Test Suite 2: Onboarding
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_02_onboarding()
    results.append(("02 - Onboarding", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Test Suite 3: User Profile
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_03_user_profile()
    results.append(("03 - User Profile", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Test Suite 4: Modules
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_04_modules()
    results.append(("04 - Modules", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Test Suite 5: Roadmaps
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_05_roadmaps()
    results.append(("05 - Roadmaps", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Test Suite 6: Chat
    print_colored("\n" + "=" * 70, Colors.BLUE)
    success = test_06_chat()
    results.append(("06 - Chat", success))
    print_colored("=" * 70 + "\n", Colors.BLUE)
    
    # Final Summary
    print_colored("=" * 70, Colors.BLUE)
    print_colored("Final Test Summary", Colors.BLUE)
    print_colored("=" * 70, Colors.BLUE)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_suite, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_suite}")
    
    print()
    print_colored(f"Total: {passed}/{total} test suites passed", 
                  Colors.GREEN if passed == total else Colors.YELLOW)
    print_colored("=" * 70, Colors.BLUE)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


#!/usr/bin/env python3
"""
Test script for 03-user-profile.http
Tests all user profile and module progress endpoints sequentially.
"""

import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
TOKEN_FILE = Path("/tmp/uni_pilot_token.txt")


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_colored(message: str, color: str = Colors.NC):
    print(f"{color}{message}{Colors.NC}")


def print_test_header(test_name: str, test_num: str):
    print()
    print_colored(f"=== Test {test_num}: {test_name} ===", Colors.YELLOW)
    print()


def make_request(client: httpx.Client, method: str, endpoint: str, 
                 data: Optional[Dict] = None, token: Optional[str] = None,
                 params: Optional[Dict] = None) -> tuple:
    """Make HTTP request and return (body, status_code)."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Accept": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if data:
        headers["Content-Type"] = "application/json"
        response = client.request(method, url, json=data, headers=headers, params=params)
    else:
        response = client.request(method, url, headers=headers, params=params)
    
    try:
        body = response.json()
    except:
        body = {"raw": response.text}
    
    return body, response.status_code


def load_token() -> Optional[str]:
    """Load token from file."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def test_03_user_profile():
    """Run all user profile tests from 03-user-profile.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("User Profile Tests (03-user-profile.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return False
    
    results = []
    module_id = None
    
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Test 1: Get User Profile (may exist if topic field was selected in onboarding)
        print_test_header("Get User Profile", "03-01")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/profile", token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        # Profile might already exist if topic field was selected in onboarding
        success = status in [200, 404]
        results.append(("Get Profile", success, status))
        if status == 200:
            print_colored("✅ PASS - Profile already exists (from topic field selection)\n", Colors.GREEN)
        elif status == 404:
            print_colored("✅ PASS - Profile doesn't exist yet\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 2: Create User Profile
        print_test_header("Create User Profile", "03-02")
        profile_data = {
            "university_id": 1,
            "study_program_id": 1,
            "current_semester": 3,
            "skills": "Python, JavaScript, SQL"
        }
        body, status = make_request(client, "PUT", f"api/{API_VERSION}/users/me/profile",
                                   data=profile_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Create Profile", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 3: Update User Profile
        print_test_header("Update User Profile", "03-03")
        updated_profile = {
            "university_id": 1,
            "study_program_id": 1,
            "current_semester": 4,
            "skills": "Python, JavaScript, SQL, React, FastAPI"
        }
        body, status = make_request(client, "PUT", f"api/{API_VERSION}/users/me/profile",
                                   data=updated_profile, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Update Profile", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 4: Get User Profile (should now return profile)
        print_test_header("Get User Profile (should exist)", "03-04")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/profile", token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Profile", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 5: Get User Modules (empty initially)
        print_test_header("Get User Modules (empty)", "03-05")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/modules", token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Modules (empty)", success, status))
        if success and isinstance(body, list) and len(body) > 0:
            module_id = body[0].get("module", {}).get("id")
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 6: Update Module Progress
        module_id_to_test = module_id or 1  # Use found module or default to 1
        print_test_header("Update Module Progress", "03-06")
        progress_data = {
            "completed": True,
            "grade": "1.3",
            "completed_at": "2024-01-15T10:00:00Z"
        }
        body, status = make_request(client, "PUT",
                                   f"api/{API_VERSION}/users/me/modules/{module_id_to_test}/progress",
                                   data=progress_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Update Module Progress", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 7: Update Module Progress - Incomplete
        print_test_header("Update Module Progress (incomplete)", "03-07")
        incomplete_data = {
            "completed": False,
            "grade": None,
            "completed_at": None
        }
        module_id_2 = (module_id_to_test + 1) if module_id_to_test else 2
        body, status = make_request(client, "PUT",
                                   f"api/{API_VERSION}/users/me/modules/{module_id_2}/progress",
                                   data=incomplete_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Update Module (incomplete)", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 8: Get User Modules (should now show progress)
        print_test_header("Get User Modules (with progress)", "03-08")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/modules", token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Modules (with progress)", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
    
    # Summary
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Test Summary", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, status in results:
        status_icon = "✅" if success else "❌"
        status_text = f"PASS ({status})" if success else f"FAIL ({status})" if status else "SKIPPED"
        print(f"{status_icon} {test_name}: {status_text}")
    
    print()
    print_colored(f"Total: {passed}/{total} tests passed", Colors.GREEN if passed == total else Colors.YELLOW)
    print_colored("=" * 60, Colors.BLUE)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = test_03_user_profile()
    sys.exit(0 if success else 1)


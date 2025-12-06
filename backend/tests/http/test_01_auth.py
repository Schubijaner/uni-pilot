#!/usr/bin/env python3
"""
Test script for 01-auth.http
Tests all authentication endpoints sequentially.
"""

import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"
API_VERSION = "v1"
TOKEN_FILE = Path("/tmp/uni_pilot_token.txt")
USER_DATA_FILE = Path("/tmp/uni_pilot_user_data.txt")


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
                 data: Optional[Dict] = None, token: Optional[str] = None) -> tuple:
    """Make HTTP request and return (body, status_code)."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Accept": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if data:
        headers["Content-Type"] = "application/json"
        response = client.request(method, url, json=data, headers=headers)
    else:
        response = client.request(method, url, headers=headers)
    
    try:
        body = response.json()
    except:
        body = {"raw": response.text}
    
    return body, response.status_code


def test_01_auth():
    """Run all authentication tests from 01-auth.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Authentication Tests (01-auth.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    results = []
    token = None
    
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Test 1: Health Check
        print_test_header("Health Check", "01-01")
        body, status = make_request(client, "GET", "health")
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Health Check", success, status))
        if success:
            print_colored("✅ PASS\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 2: API Info
        print_test_header("API Info", "01-02")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/")
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("API Info", success, status))
        if success:
            print_colored("✅ PASS\n", Colors.GREEN)
        else:
            print_colored("⚠️  Non-200 status\n", Colors.YELLOW)
        
        # Test 3: User Registration
        print_test_header("User Registration", "01-03")
        register_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/register", register_data)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 201
        results.append(("User Registration", success, status))
        if success:
            print_colored("✅ PASS\n", Colors.GREEN)
            USER_DATA_FILE.write_text(json.dumps({
                "id": body.get("id"),
                "email": body.get("email"),
                **register_data
            }))
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 4: Duplicate Registration (should fail)
        print_test_header("Duplicate Registration (should fail)", "01-04")
        duplicate_data = {
            "email": "testuser@example.com",
            "password": "AnotherPassword123!",
            "first_name": "Duplicate",
            "last_name": "User"
        }
        body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/register", duplicate_data)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status} (expected 400)", Colors.BLUE)
        success = status == 400
        results.append(("Duplicate Registration", success, status))
        if success:
            print_colored("✅ PASS\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 5: User Login
        print_test_header("User Login", "01-05")
        login_data = {
            "email": "testuser@example.com",
            "password": "TestPassword123!"
        }
        body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/login", login_data)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("User Login", success, status))
        if success:
            token = body.get("access_token")
            if token:
                TOKEN_FILE.write_text(token)
                print_colored(f"✅ PASS - Token saved\n", Colors.GREEN)
                print_colored(f"Token: {token[:50]}...\n", Colors.GREEN)
            else:
                print_colored("⚠️  No token in response\n", Colors.YELLOW)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 6: Wrong Password (should fail)
        print_test_header("Wrong Password Login (should fail)", "01-06")
        wrong_login = {
            "email": "testuser@example.com",
            "password": "WrongPassword123!"
        }
        body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/login", wrong_login)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status} (expected 401)", Colors.BLUE)
        success = status == 401
        results.append(("Wrong Password", success, status))
        if success:
            print_colored("✅ PASS\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 7: Get Current User
        print_test_header("Get Current User", "01-07")
        if token:
            body, status = make_request(client, "GET", f"api/{API_VERSION}/auth/me", token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get Current User", success, status))
            if success:
                print_colored("✅ PASS\n", Colors.GREEN)
            else:
                print_colored("❌ FAIL\n", Colors.RED)
        else:
            print_colored("⚠️  SKIPPED - No token available\n", Colors.YELLOW)
            results.append(("Get Current User", False, None))
    
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
    success = test_01_auth()
    sys.exit(0 if success else 1)


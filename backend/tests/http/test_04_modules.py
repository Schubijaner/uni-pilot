#!/usr/bin/env python3
"""
Test script for 04-modules.http
Tests module-related endpoints.
"""

import httpx
import json
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"
API_VERSION = "v1"


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


def test_04_modules():
    """Run all module tests from 04-modules.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Modules Tests (04-modules.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    results = []
    study_program_id = 1  # Default, should be replaced with actual ID
    
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Test 1: Get Modules by Study Program ID
        print_test_header("Get Modules by Study Program", "04-01")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/study-programs/{study_program_id}/modules")
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Modules by Study Program", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 2: Get All Modules (might not exist)
        print_test_header("Get All Modules (might not exist)", "04-02")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/modules")
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        # This endpoint might not exist, so 404 is acceptable
        success = status in [200, 404]
        results.append(("Get All Modules", success, status))
        if status == 404:
            print_colored("⚠️  Endpoint not found (404) - This is expected\n", Colors.YELLOW)
        else:
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
    success = test_04_modules()
    sys.exit(0 if success else 1)


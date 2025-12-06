#!/usr/bin/env python3
"""
Test script for 02-onboarding.http
Tests all onboarding endpoints sequentially.
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


def test_02_onboarding():
    """Run all onboarding tests from 02-onboarding.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Onboarding Tests (02-onboarding.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        print()
    
    results = []
    university_id = None
    study_program_id = None
    topic_field_id = None
    
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Test 1: Get All Universities
        print_test_header("Get All Universities", "02-01")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/universities", token=token)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get All Universities", success, status))
        if success and isinstance(body, dict) and body.get("items"):
            university_id = body["items"][0]["id"] if body["items"] else None
            print_colored(f"✅ PASS - Found {len(body.get('items', []))} universities\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 2: Get Universities with Search
        print_test_header("Get Universities with Search", "02-02")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/universities", 
                                   token=token, params={"search": "Berlin"})
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Search Universities", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 3: Get Universities with Pagination
        print_test_header("Get Universities with Pagination", "02-03")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/universities",
                                   token=token, params={"limit": 10, "offset": 0})
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Pagination Universities", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 4: Get Study Programs by University
        if university_id:
            print_test_header("Get Study Programs by University", "02-04")
            body, status = make_request(client, "GET", 
                                       f"api/{API_VERSION}/universities/{university_id}/study-programs",
                                       token=token)
            print(json.dumps(body, indent=2))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get Study Programs", success, status))
            if success and isinstance(body, dict) and body.get("items"):
                study_program_id = body["items"][0]["id"] if body["items"] else None
                print_colored(f"✅ PASS - Found {len(body.get('items', []))} programs\n", Colors.GREEN)
            else:
                print_colored("❌ FAIL\n", Colors.RED)
        else:
            print_colored("⚠️  SKIPPED - No university ID available\n", Colors.YELLOW)
            results.append(("Get Study Programs", False, None))
        
        # Test 5: Get Study Programs - Filter by Degree Type
        if university_id:
            print_test_header("Get Study Programs - Filter by Degree Type", "02-05")
            body, status = make_request(client, "GET",
                                       f"api/{API_VERSION}/universities/{university_id}/study-programs",
                                       token=token, params={"degree_type": "Bachelor"})
            print(json.dumps(body, indent=2))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Filter Study Programs", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 6: Get Career Tree
        if study_program_id:
            print_test_header("Get Career Tree", "02-06")
            body, status = make_request(client, "GET",
                                       f"api/{API_VERSION}/study-programs/{study_program_id}/career-tree",
                                       token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get Career Tree", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 7: Get All Topic Fields
        print_test_header("Get All Topic Fields", "02-07")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/topic-fields", token=token)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Topic Fields", success, status))
        if success and isinstance(body, list) and len(body) > 0:
            topic_field_id = body[0]["id"]
            print_colored(f"✅ PASS - Found {len(body)} topic fields\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 8: Get Topic Fields with Search
        print_test_header("Get Topic Fields with Search", "02-08")
        body, status = make_request(client, "GET", f"api/{API_VERSION}/topic-fields",
                                   token=token, params={"search": "Full Stack"})
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Search Topic Fields", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 9: Get Topic Field by ID
        if topic_field_id:
            print_test_header("Get Topic Field by ID", "02-09")
            body, status = make_request(client, "GET", f"api/{API_VERSION}/topic-fields/{topic_field_id}", token=token)
            print(json.dumps(body, indent=2))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get Topic Field by ID", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 10: Select Topic Field (requires auth)
        if topic_field_id and token:
            print_test_header("Select Topic Field", "02-10")
            data = {"topic_field_id": topic_field_id}
            body, status = make_request(client, "PUT",
                                       f"api/{API_VERSION}/users/me/profile/topic-field",
                                       data=data, token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Select Topic Field", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 11: Create User Question (requires auth)
        if token:
            print_test_header("Create User Question", "02-11")
            data = {
                "question_text": "Are you interested in frontend development?",
                "answer": True,
                "career_tree_node_id": 1
            }
            body, status = make_request(client, "POST", f"api/{API_VERSION}/users/me/questions",
                                       data=data, token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 201
            results.append(("Create User Question", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 12: Create User Question - Without Career Tree Node
        if token:
            print_test_header("Create User Question (without node)", "02-12")
            data = {
                "question_text": "Do you prefer working in teams?",
                "answer": True
            }
            body, status = make_request(client, "POST", f"api/{API_VERSION}/users/me/questions",
                                       data=data, token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 201
            results.append(("Create Question (no node)", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 13: Get User Questions
        if token:
            print_test_header("Get User Questions", "02-13")
            body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/questions", token=token)
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get User Questions", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 14: Get User Questions - Filtered
        if token:
            print_test_header("Get User Questions (filtered)", "02-14")
            body, status = make_request(client, "GET", f"api/{API_VERSION}/users/me/questions",
                                       token=token, params={"career_tree_node_id": 1})
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.BLUE)
            success = status == 200
            results.append(("Get Questions (filtered)", success, status))
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
    success = test_02_onboarding()
    sys.exit(0 if success else 1)


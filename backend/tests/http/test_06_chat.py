#!/usr/bin/env python3
"""
Test script for 06-chat.http
Tests chat session and message endpoints sequentially.
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


def test_06_chat():
    """Run all chat tests from 06-chat.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Chat Tests (06-chat.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return False
    
    results = []
    topic_field_id = 1  # Default, should be replaced with actual ID
    session_id = None
    
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:  # Longer timeout for LLM responses
        # Test 1: Create or Get Chat Session
        print_test_header("Create or Get Chat Session", "06-01")
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/chat/sessions",
                                   data={}, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 201
        results.append(("Create Chat Session", success, status))
        if success and isinstance(body, dict):
            session_id = body.get("id")
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 2: Create Chat Session - Invalid Topic Field (should fail)
        print_test_header("Create Chat Session (invalid topic field)", "06-02")
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/topic-fields/9999/chat/sessions",
                                   data={}, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status} (expected 404)", Colors.BLUE)
        success = status == 404
        results.append(("Invalid Topic Field", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 3: Get Chat Messages for Session
        session_id_to_test = session_id or 1  # Use found ID or default
        print_test_header("Get Chat Messages", "06-03")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/chat/sessions/{session_id_to_test}/messages",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Chat Messages", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 4: Get Chat Messages with Pagination
        print_test_header("Get Chat Messages (pagination)", "06-04")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/chat/sessions/{session_id_to_test}/messages",
                                   token=token, params={"limit": 10, "offset": 0})
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Messages (pagination)", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 5: Send Chat Message
        print_test_header("Send Chat Message", "06-05")
        print_colored("⏳ This may take a while (LLM response)...\n", Colors.YELLOW)
        message_data = {
            "content": "Welche Skills brauche ich für Full Stack Development?"
        }
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/{session_id_to_test}/messages",
                                   data=message_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Send Chat Message", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 6: Send Another Chat Message
        print_test_header("Send Another Chat Message", "06-06")
        print_colored("⏳ This may take a while (LLM response)...\n", Colors.YELLOW)
        message_data_2 = {
            "content": "Welche Tools empfehlst du für Backend-Entwicklung?"
        }
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/{session_id_to_test}/messages",
                                   data=message_data_2, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Send Another Message", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 7: Get Chat Messages (should now show conversation)
        print_test_header("Get Chat Messages (conversation)", "06-07")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/chat/sessions/{session_id_to_test}/messages",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Messages (conversation)", success, status))
        if success and isinstance(body, list):
            print_colored(f"✅ PASS - Found {len(body)} messages\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 8: Send Message - Invalid Session (should fail)
        print_test_header("Send Message (invalid session)", "06-08")
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/9999/messages",
                                   data={"content": "This should fail"}, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status} (expected 404)", Colors.BLUE)
        success = status == 404
        results.append(("Invalid Session", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 9: Get All User Chat Sessions
        print_test_header("Get All User Chat Sessions", "06-09")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/users/me/chat/sessions",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get User Sessions", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 10: Get User Chat Sessions - Filtered by Topic Field
        print_test_header("Get User Chat Sessions (filtered)", "06-10")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/users/me/chat/sessions",
                                   token=token, params={"topic_field_id": topic_field_id})
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Sessions (filtered)", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 11: Get User Chat Sessions with Pagination
        print_test_header("Get User Chat Sessions (pagination)", "06-11")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/users/me/chat/sessions",
                                   token=token, params={"limit": 10, "offset": 0})
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Sessions (pagination)", success, status))
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
    success = test_06_chat()
    sys.exit(0 if success else 1)


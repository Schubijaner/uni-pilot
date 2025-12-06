#!/usr/bin/env python3
"""
Test script for 05-roadmaps.http
Tests roadmap generation and progress endpoints sequentially.
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


def test_05_roadmaps():
    """Run all roadmap tests from 05-roadmaps.http"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Roadmaps Tests (05-roadmaps.http)", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return False
    
    results = []
    topic_field_id = 1  # Default, should be replaced with actual ID from onboarding
    roadmap_item_id = None
    
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:  # Longer timeout for roadmap generation
        # Test 1: Get Roadmap (may exist from seed data or previous tests)
        print_test_header("Get Roadmap", "05-01")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/roadmap",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        if status == 500:
            print_colored(f"⚠️  Server Error: {body.get('detail', 'Unknown error')}\n", Colors.RED)
        # Accept both 200 (exists) and 404 (doesn't exist) as valid
        success = status in [200, 404]
        results.append(("Get Roadmap", success, status))
        if status == 200:
            print_colored("✅ PASS - Roadmap exists\n", Colors.GREEN)
        elif status == 404:
            print_colored("✅ PASS - Roadmap doesn't exist yet (will be generated)\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 2: Generate Roadmap
        print_test_header("Generate Roadmap", "05-02")
        print_colored("⏳ This may take a while (LLM generation)...\n", Colors.YELLOW)
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/roadmap/generate",
                                   data={}, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status in [200, 201]  # Accept both success codes
        results.append(("Generate Roadmap", success, status))
        if success and isinstance(body, dict) and body.get("items"):
            # Try to get first roadmap item ID
            items = body.get("items", [])
            if items:
                roadmap_item_id = items[0].get("id")
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 3: Get Roadmap (should now return the generated roadmap)
        print_test_header("Get Roadmap (should exist)", "05-03")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/roadmap",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Roadmap", success, status))
        if success and isinstance(body, dict) and body.get("items") and not roadmap_item_id:
            items = body.get("items", [])
            if items:
                roadmap_item_id = items[0].get("id")
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 4: Get Roadmap Progress
        print_test_header("Get Roadmap Progress", "05-04")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/users/me/roadmap/progress",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Roadmap Progress", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 5: Update Roadmap Item Progress
        roadmap_item_id_to_test = roadmap_item_id or 1  # Use found ID or default
        print_test_header("Update Roadmap Item Progress", "05-05")
        progress_data = {
            "completed": True,
            "completed_at": "2024-01-20T12:00:00Z",
            "notes": "Completed the first milestone!"
        }
        body, status = make_request(client, "PUT",
                                   f"api/{API_VERSION}/users/me/roadmap/items/{roadmap_item_id_to_test}/progress",
                                   data=progress_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Update Roadmap Item Progress", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 6: Update Roadmap Item Progress - Incomplete
        print_test_header("Update Roadmap Item Progress (incomplete)", "05-06")
        incomplete_data = {
            "completed": False,
            "completed_at": None,
            "notes": "Still working on this"
        }
        roadmap_item_id_2 = (roadmap_item_id_to_test + 1) if roadmap_item_id_to_test else 2
        body, status = make_request(client, "PUT",
                                   f"api/{API_VERSION}/users/me/roadmap/items/{roadmap_item_id_2}/progress",
                                   data=incomplete_data, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Update Roadmap Item (incomplete)", success, status))
        print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        
        # Test 7: Get Roadmap Progress (should show updated progress)
        print_test_header("Get Roadmap Progress (updated)", "05-07")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/users/me/roadmap/progress",
                                   token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 200
        results.append(("Get Roadmap Progress (updated)", success, status))
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
    success = test_05_roadmaps()
    sys.exit(0 if success else 1)


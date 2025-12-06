#!/usr/bin/env python3
"""
Comprehensive test script for LLM features (Chat and Roadmap generation).
Tests AWS Bedrock integration through the API endpoints.

Prerequisites:
1. AWS credentials configured via 'aws configure' or environment variables
2. Bedrock model access enabled in AWS Console
3. Server running on localhost:8000
4. User authenticated (run test_01_auth.py first)
5. User onboarded (run test_02_onboarding.py first)
"""

import httpx
import json
import time
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
    CYAN = '\033[0;36m'
    NC = '\033[0m'


def print_colored(message: str, color: str = Colors.NC):
    print(f"{color}{message}{Colors.NC}")


def print_test_header(test_name: str, test_num: str):
    print()
    print_colored(f"=== Test {test_num}: {test_name} ===", Colors.YELLOW)
    print()


def make_request(client: httpx.Client, method: str, endpoint: str, 
                 data: Optional[Dict] = None, token: Optional[str] = None,
                 params: Optional[Dict] = None, timeout: float = 60.0) -> tuple:
    """Make HTTP request and return (body, status_code)."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Accept": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if data:
        headers["Content-Type"] = "application/json"
        response = client.request(method, url, json=data, headers=headers, params=params, timeout=timeout)
    else:
        response = client.request(method, url, headers=headers, params=params, timeout=timeout)
    
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


def test_llm_chat_features():
    """Test LLM-powered chat features."""
    print_colored("=" * 70, Colors.CYAN)
    print_colored("LLM Chat Features Test", Colors.CYAN)
    print_colored("=" * 70, Colors.CYAN)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return False
    
    results = []
    topic_field_id = 1  # Should match topic field from onboarding
    session_id = None
    
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:  # Extended timeout for LLM
        # Test 1: Create Chat Session
        print_test_header("Create Chat Session", "LLM-01")
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/chat/sessions",
                                   data={}, token=token)
        print(json.dumps(body, indent=2, default=str))
        print_colored(f"Status: {status}", Colors.BLUE)
        success = status == 201
        results.append(("Create Chat Session", success, status))
        if success and isinstance(body, dict):
            session_id = body.get("id")
            print_colored(f"✅ Session ID: {session_id}\n", Colors.GREEN)
        else:
            print_colored("❌ FAIL\n", Colors.RED)
            return False
        
        # Test 2: Send First Chat Message (LLM Response)
        print_test_header("Send Chat Message - LLM Response Test", "LLM-02")
        print_colored("⏳ Waiting for LLM response (this may take 10-30 seconds)...\n", Colors.YELLOW)
        start_time = time.time()
        
        message_data = {
            "content": "Hallo! Kannst du mir erklären, welche Grundlagen ich für Machine Learning brauche?"
        }
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/{session_id}/messages",
                                   data=message_data, token=token, timeout=120.0)
        
        elapsed_time = time.time() - start_time
        print_colored(f"⏱️  Response time: {elapsed_time:.2f} seconds\n", Colors.BLUE)
        
        if status == 200 and isinstance(body, dict):
            user_msg = body.get("user_message", {})
            assistant_msg = body.get("assistant_message", {})
            
            print_colored("User Message:", Colors.CYAN)
            print(f"  {user_msg.get('content', 'N/A')}\n")
            
            print_colored("Assistant Message (LLM Response):", Colors.CYAN)
            assistant_content = assistant_msg.get('content', 'N/A')
            print(f"  {assistant_content[:500]}{'...' if len(assistant_content) > 500 else ''}\n")
            
            # Validate LLM response quality
            has_content = len(assistant_content) > 50
            has_relevant_keywords = any(keyword in assistant_content.lower() 
                                       for keyword in ['machine learning', 'ml', 'daten', 'algorithmus', 'modell'])
            
            success = status == 200 and has_content
            results.append(("Send Chat Message (LLM)", success, status))
            
            if has_relevant_keywords:
                print_colored("✅ LLM response appears relevant\n", Colors.GREEN)
            else:
                print_colored("⚠️  LLM response may not be relevant\n", Colors.YELLOW)
        else:
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.RED)
            success = False
            results.append(("Send Chat Message (LLM)", success, status))
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 3: Send Follow-up Message (Context Test)
        print_test_header("Send Follow-up Message - Context Test", "LLM-03")
        print_colored("⏳ Waiting for LLM response with context...\n", Colors.YELLOW)
        
        followup_data = {
            "content": "Welche Programmiersprachen sind dafür am wichtigsten?"
        }
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/{session_id}/messages",
                                   data=followup_data, token=token, timeout=120.0)
        
        if status == 200 and isinstance(body, dict):
            assistant_msg = body.get("assistant_message", {})
            assistant_content = assistant_msg.get('content', 'N/A')
            
            print_colored("Assistant Response (with context):", Colors.CYAN)
            print(f"  {assistant_content[:500]}{'...' if len(assistant_content) > 500 else ''}\n")
            
            success = status == 200 and len(assistant_content) > 50
            results.append(("Follow-up Message (Context)", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        else:
            print(json.dumps(body, indent=2, default=str))
            success = False
            results.append(("Follow-up Message (Context)", success, status))
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 4: Get Chat History (Verify Context Preservation)
        print_test_header("Get Chat History - Context Verification", "LLM-04")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/chat/sessions/{session_id}/messages",
                                   token=token)
        
        if status == 200 and isinstance(body, list):
            print_colored(f"✅ Found {len(body)} messages in conversation\n", Colors.GREEN)
            print_colored("Message History:", Colors.CYAN)
            for i, msg in enumerate(body[-3:], 1):  # Show last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]
                print(f"  {i}. [{role.upper()}]: {content}...")
            print()
            
            success = len(body) >= 4  # At least 2 user + 2 assistant messages
            results.append(("Get Chat History", success, status))
        else:
            print(json.dumps(body, indent=2, default=str))
            success = False
            results.append(("Get Chat History", success, status))
            print_colored("❌ FAIL\n", Colors.RED)
    
    return results


def test_llm_roadmap_generation():
    """Test LLM-powered roadmap generation."""
    print_colored("=" * 70, Colors.CYAN)
    print_colored("LLM Roadmap Generation Test", Colors.CYAN)
    print_colored("=" * 70, Colors.CYAN)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return []
    
    results = []
    topic_field_id = 1  # Should match topic field from onboarding
    
    with httpx.Client(timeout=180.0, follow_redirects=True) as client:  # Extended timeout for roadmap generation
        # Test 1: Generate Roadmap (LLM Generation)
        print_test_header("Generate Roadmap - LLM Generation", "LLM-05")
        print_colored("⏳ Generating roadmap with LLM (this may take 30-60 seconds)...\n", Colors.YELLOW)
        print_colored("⚠️  This will call AWS Bedrock Claude 3 Sonnet model\n", Colors.YELLOW)
        
        start_time = time.time()
        
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/roadmap/generate",
                                   data={}, token=token, timeout=180.0)
        
        elapsed_time = time.time() - start_time
        print_colored(f"⏱️  Generation time: {elapsed_time:.2f} seconds\n", Colors.BLUE)
        
        if status == 201 and isinstance(body, dict):
            roadmap_id = body.get("id")
            roadmap_name = body.get("name", "N/A")
            items = body.get("items", [])
            
            print_colored("✅ Roadmap Generated Successfully!", Colors.GREEN)
            print_colored(f"   Roadmap ID: {roadmap_id}", Colors.CYAN)
            print_colored(f"   Roadmap Name: {roadmap_name}", Colors.CYAN)
            print_colored(f"   Number of Items: {len(items)}\n", Colors.CYAN)
            
            # Validate roadmap structure
            has_items = len(items) > 0
            has_structure = any(item.get("level") is not None for item in items[:5])
            
            if has_items:
                print_colored("Sample Roadmap Items:", Colors.CYAN)
                for item in items[:5]:
                    title = item.get("title", "N/A")
                    level = item.get("level", "N/A")
                    item_type = item.get("item_type", "N/A")
                    print(f"  - [{level}] {item_type}: {title}")
                print()
            
            success = status == 201 and has_items and has_structure
            results.append(("Generate Roadmap (LLM)", success, status))
            print_colored("✅ PASS\n" if success else "❌ FAIL\n", Colors.GREEN if success else Colors.RED)
        elif status == 200:
            print_colored("ℹ️  Roadmap already exists (returning existing)\n", Colors.BLUE)
            results.append(("Generate Roadmap (LLM)", True, status))
        else:
            print(json.dumps(body, indent=2, default=str))
            print_colored(f"Status: {status}", Colors.RED)
            success = False
            results.append(("Generate Roadmap (LLM)", success, status))
            print_colored("❌ FAIL\n", Colors.RED)
        
        # Test 2: Get Generated Roadmap with Tree Structure
        print_test_header("Get Roadmap with Tree Structure", "LLM-06")
        body, status = make_request(client, "GET",
                                   f"api/{API_VERSION}/topic-fields/{topic_field_id}/roadmap",
                                   token=token)
        
        if status == 200 and isinstance(body, dict):
            tree = body.get("tree")
            items = body.get("items", [])
            
            print_colored(f"✅ Roadmap retrieved with {len(items)} items\n", Colors.GREEN)
            
            if tree:
                print_colored("Roadmap Tree Structure (first 3 levels):", Colors.CYAN)
                def print_tree(node, level=0, max_level=3):
                    if level > max_level:
                        return
                    indent = "  " * level
                    title = node.get("title", "N/A")
                    item_type = node.get("item_type", "N/A")
                    print(f"{indent}- [{item_type}] {title}")
                    children = node.get("children", [])
                    for child in children[:3]:  # Limit children shown
                        print_tree(child, level + 1, max_level)
                
                print_tree(tree)
                print()
            
            success = status == 200 and len(items) > 0
            results.append(("Get Roadmap Tree", success, status))
        else:
            print(json.dumps(body, indent=2, default=str))
            success = False
            results.append(("Get Roadmap Tree", success, status))
            print_colored("❌ FAIL\n", Colors.RED)
    
    return results


def test_llm_error_handling():
    """Test LLM error handling (e.g., invalid credentials, model errors)."""
    print_colored("=" * 70, Colors.CYAN)
    print_colored("LLM Error Handling Test", Colors.CYAN)
    print_colored("=" * 70, Colors.CYAN)
    
    token = load_token()
    if not token:
        print_colored("⚠️  No token found. Please run test_01_auth.py first!", Colors.YELLOW)
        return []
    
    results = []
    
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        # Test: Invalid Session ID (should handle gracefully)
        print_test_header("Error Handling - Invalid Session", "LLM-07")
        body, status = make_request(client, "POST",
                                   f"api/{API_VERSION}/chat/sessions/99999/messages",
                                   data={"content": "Test"}, token=token)
        
        success = status == 404  # Should return 404, not 500
        results.append(("Error Handling (Invalid Session)", success, status))
        
        if success:
            print_colored("✅ Error handled correctly (404)\n", Colors.GREEN)
        else:
            print_colored(f"⚠️  Unexpected status: {status}\n", Colors.YELLOW)
            print(json.dumps(body, indent=2, default=str))
    
    return results


def main():
    """Run all LLM feature tests."""
    print_colored("\n" + "=" * 70, Colors.BLUE)
    print_colored("AWS Bedrock LLM Features - Comprehensive Test Suite", Colors.BLUE)
    print_colored("=" * 70, Colors.BLUE)
    print()
    print_colored("Prerequisites:", Colors.YELLOW)
    print("  1. AWS credentials configured (aws configure)")
    print("  2. Bedrock model access enabled in AWS Console")
    print("  3. Server running on localhost:8000")
    print("  4. User authenticated and onboarded")
    print()
    
    all_results = []
    
    # Test Chat Features
    chat_results = test_llm_chat_features()
    all_results.extend(chat_results)
    
    # Test Roadmap Generation
    roadmap_results = test_llm_roadmap_generation()
    all_results.extend(roadmap_results)
    
    # Test Error Handling
    error_results = test_llm_error_handling()
    all_results.extend(error_results)
    
    # Summary
    print_colored("=" * 70, Colors.BLUE)
    print_colored("Test Summary", Colors.BLUE)
    print_colored("=" * 70, Colors.BLUE)
    
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)
    
    for test_name, success, status in all_results:
        status_icon = "✅" if success else "❌"
        status_text = f"PASS ({status})" if success else f"FAIL ({status})"
        print(f"{status_icon} {test_name}: {status_text}")
    
    print()
    if passed == total:
        print_colored(f"🎉 All tests passed! ({passed}/{total})", Colors.GREEN)
    else:
        print_colored(f"⚠️  Some tests failed: {passed}/{total} passed", Colors.YELLOW)
    print_colored("=" * 70, Colors.BLUE)
    
    return passed == total


if __name__ == "__main__":
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Tests interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n\n❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)


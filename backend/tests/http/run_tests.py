#!/usr/bin/env python3
"""
CLI script to run HTTP tests using httpx (already in requirements.txt).
Usage: python tests/http/run_tests.py [test_file_number]
Example: python tests/http/run_tests.py 01
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install it with: pip install httpx")
    sys.exit(1)

BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

# Colors for terminal
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_colored(message: str, color: str = Colors.NC):
    """Print colored message."""
    print(f"{color}{message}{Colors.NC}")


def make_request(
    client: httpx.Client,
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
) -> tuple[Dict[str, Any], int]:
    """Make HTTP request and return response body and status code."""
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


def test_01_auth(client: httpx.Client, token_file: Path):
    """Run authentication tests."""
    print_colored("=== Running Authentication Tests ===", Colors.YELLOW)
    print()
    
    token = None
    
    # 1. Health Check
    print_colored("1. Health Check", Colors.GREEN)
    body, status = make_request(client, "GET", "health")
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status}\n", Colors.BLUE)
    
    # 2. API Info (using example router endpoint)
    print_colored("2. API Info", Colors.GREEN)
    body, status = make_request(client, "GET", f"api/{API_VERSION}/")
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status}\n", Colors.BLUE)
    
    # 3. User Registration
    print_colored("3. User Registration", Colors.GREEN)
    register_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/register", register_data)
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status}\n", Colors.BLUE)
    
    user_id = body.get("id") if status == 201 else None
    if user_id:
        print_colored(f"User ID: {user_id}\n", Colors.GREEN)
    
    # 4. Duplicate Registration (should fail)
    print_colored("4. Duplicate Registration (should fail)", Colors.GREEN)
    body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/register", register_data)
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status} (expected 400)\n", Colors.BLUE)
    
    # 5. User Login
    print_colored("5. User Login", Colors.GREEN)
    login_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }
    body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/login", login_data)
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status}\n", Colors.BLUE)
    
    # Extract and save token
    if status == 200:
        token = body.get("access_token")
        if token:
            token_file.write_text(token)
            print_colored(f"Token saved to {token_file}\n", Colors.YELLOW)
            print_colored(f"Token: {token[:50]}...\n", Colors.GREEN)
    
    # 6. Wrong Password (should fail)
    print_colored("6. Wrong Password (should fail)", Colors.GREEN)
    wrong_login = {
        "email": "testuser@example.com",
        "password": "WrongPassword123!"
    }
    body, status = make_request(client, "POST", f"api/{API_VERSION}/auth/login", wrong_login)
    print(json.dumps(body, indent=2))
    print_colored(f"Status: {status} (expected 401)\n", Colors.BLUE)
    
    # 7. Get Current User
    if token:
        print_colored("7. Get Current User", Colors.GREEN)
        body, status = make_request(client, "GET", f"api/{API_VERSION}/auth/me", token=token)
        print(json.dumps(body, indent=2))
        print_colored(f"Status: {status}\n", Colors.BLUE)
    else:
        print_colored("7. Get Current User - SKIPPED (no token)", Colors.RED)
        print()
    
    print_colored("=== Authentication Tests Complete ===\n", Colors.GREEN)
    return token


def main():
    """Main function."""
    test_file = sys.argv[1] if len(sys.argv) > 1 else "01"
    token_file = Path("/tmp/uni_pilot_token.txt")
    
    with httpx.Client(timeout=30.0) as client:
        if test_file in ["01", "auth"]:
            test_01_auth(client, token_file)
        else:
            print_colored(f"Unknown test: {test_file}", Colors.RED)
            print("Available tests: 01 (auth)")
            sys.exit(1)


if __name__ == "__main__":
    main()


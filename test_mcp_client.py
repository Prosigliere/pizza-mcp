#!/usr/bin/env python3
"""
Simple test client for the Pizza MCP Server
Tests the deployed MCP server endpoints
"""
import requests
import json
from typing import Dict, Any

# Configuration
SERVER_URL = "https://pizza-mcp-47901888500.us-central1.run.app"
SECRET_KEY = "you-cant-spell-awesome-without-wes"

def test_endpoint(name: str, endpoint: str, data: Dict[str, Any] = None) -> None:
    """Test a single MCP endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SECRET_KEY}"
    }
    
    try:
        if data is not None:
            response = requests.post(f"{SERVER_URL}{endpoint}", json=data, headers=headers, timeout=10)
        else:
            response = requests.get(f"{SERVER_URL}{endpoint}", headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"Response Body:\n{json.dumps(result, indent=2)}")
        except:
            print(f"Response Body (text):\n{response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def main():
    print("🍕 Pizza MCP Server Test Client")
    print(f"Server: {SERVER_URL}")
    
    # Test 1: Root endpoint (might not exist)
    test_endpoint("Root Endpoint", "/")
    
    # Test 2: SSE endpoint (FastMCP uses this)
    test_endpoint("SSE Endpoint", "/sse")
    
    # Test 3: List tools (if FastMCP exposes this)
    test_endpoint("List Tools", "/mcp/v1/tools/list", data={})
    
    # Test 4: Call a simple tool
    test_endpoint(
        "Call 'add' Tool",
        "/mcp/v1/tools/call",
        data={
            "name": "add",
            "arguments": {"a": 5, "b": 7}
        }
    )
    
    # Test 5: Call find_all_people
    test_endpoint(
        "Call 'find_all_people' Tool",
        "/mcp/v1/tools/call",
        data={
            "name": "find_all_people",
            "arguments": {}
        }
    )
    
    print(f"\n{'='*60}")
    print("✅ Testing complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

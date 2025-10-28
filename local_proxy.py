#!/usr/bin/env python3
"""
Local MCP proxy that connects Windsurf (stdio) to the remote HTTP MCP server.
This allows Windsurf to use your Cloud Run deployed MCP server.
"""
import asyncio
import json
import sys
import os
import aiohttp
from typing import Any, Dict, Optional

# Configuration
REMOTE_MCP_URL = os.getenv("REMOTE_MCP_URL", "my-api-url-ending-in-/mcp")

# Session management
session_id: Optional[str] = None

async def forward_request(session: aiohttp.ClientSession, method: str, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
    """Forward a JSON-RPC request to the remote MCP server using streamable-http transport."""
    global session_id
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # Add session ID if we have one (except for initialize)
    if session_id and method != "initialize":
        headers["mcp-session-id"] = session_id
    
    # Build JSON-RPC request
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    
    try:
        async with session.post(REMOTE_MCP_URL, json=jsonrpc_request, headers=headers) as response:
            if response.status == 200:
                # Handle SSE response
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/event-stream' in content_type:
                    # Parse SSE format
                    text = await response.text()
                    # Extract data from SSE format (lines starting with "data: ")
                    for line in text.split('\n'):
                        if line.startswith('data: '):
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            
                            # Store session ID from initialize response
                            if method == "initialize" and 'mcp-session-id' in response.headers:
                                session_id = response.headers['mcp-session-id']
                            
                            return data
                    
                    return {"error": {"code": -32603, "message": "No data in SSE response"}}
                else:
                    # Regular JSON response
                    return await response.json()
            else:
                error_text = await response.text()
                return {
                    "error": {
                        "code": response.status,
                        "message": f"Remote server error: {error_text}"
                    }
                }
    except Exception as e:
        return {
            "error": {
                "code": -32603,
                "message": f"Connection error: {str(e)}"
            }
        }

async def main():
    """Main stdio loop for MCP communication."""
    async with aiohttp.ClientSession() as session:
        # Read JSON-RPC messages from stdin
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")
                
                # Forward to remote server
                result = await forward_request(session, method, params, request_id)
                
                # Send response back via stdout
                # The result from forward_request is already a complete JSON-RPC response
                if "jsonrpc" in result:
                    # Already formatted as JSON-RPC response
                    print(json.dumps(result), flush=True)
                else:
                    # Wrap in JSON-RPC response format
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                    }
                    
                    if "error" in result:
                        response["error"] = result["error"]
                    else:
                        response["result"] = result
                    
                    print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())

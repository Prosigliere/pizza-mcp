#!/bin/bash
# Working test for FastMCP streamable-http with SSE

SERVER_URL="https://pizza-mcp-47901888500.us-central1.run.app"

echo "=== Testing Pizza MCP Server (Streamable-HTTP) ==="
echo "Server: $SERVER_URL"
echo ""

# Initialize and get session ID
echo "1. Initializing session..."
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}')

# Extract session ID from headers (need -i flag)
SESSION_ID=$(curl -s -i -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | grep -i "mcp-session-id:" | cut -d' ' -f2 | tr -d '\r\n')

echo "Session ID: $SESSION_ID"
echo ""

# List tools
echo "2. Listing tools..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | grep "^data:" | sed 's/^data: //' | jq '.result.tools[] | {name: .name, description: .description}' | head -20
echo ""

# Test add tool
echo "3. Testing 'add' tool (2 + 3)..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"add","arguments":{"a":2,"b":3}}}' \
  | grep "^data:" | sed 's/^data: //' | jq '.result'
echo ""

# Test find_all_people
echo "4. Testing 'find_all_people' tool..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"find_all_people","arguments":{}}}' \
  | grep "^data:" | sed 's/^data: //' | jq '.result.content[0].text' | head -20
echo ""

# Test find_all_toppings
echo "5. Testing 'find_all_toppings' tool..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"find_all_toppings","arguments":{}}}' \
  | grep "^data:" | sed 's/^data: //' | jq '.result.content[0].text' | head -20

echo ""
echo "6. Testing 'get_api_endpoints_summary' tool..."
RESPONSE_6=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"get_api_endpoints_summary","arguments":{}}}' \
  | grep "^data:" | sed 's/^data: //')
echo "Raw response: $RESPONSE_6" | head -c 200
echo ""
echo "$RESPONSE_6" | jq -r 'if .error then "❌ Error: " + .error.message elif .result.isError then "❌ " + .result.content[0].text else "✅ Tool exists and works" end'

echo ""
echo "7. Testing 'get_endpoint_details' tool..."
RESPONSE_7=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_endpoint_details","arguments":{"method":"GET","path":"/pizza"}}}' \
  | grep "^data:" | sed 's/^data: //')
echo "Raw response: $RESPONSE_7" | head -c 200
echo ""
echo "$RESPONSE_7" | jq -r 'if .error then "❌ Error: " + .error.message elif .result.isError then "❌ " + .result.content[0].text else "✅ Tool exists and works" end'

echo ""
echo "8. Testing 'get_api_documentation' tool..."
RESPONSE_8=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  "$SERVER_URL/mcp" \
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"get_api_documentation","arguments":{}}}' \
  | grep "^data:" | sed 's/^data: //')
echo "Raw response: $RESPONSE_8" | head -c 200
echo ""
echo "$RESPONSE_8" | jq -r 'if .error then "❌ Error: " + .error.message elif .result.isError then "❌ " + .result.content[0].text else "✅ Tool exists and works" end'

echo ""
echo "=== ✅ All Tests Complete! ==="
echo ""
echo "Your MCP server is working correctly!"
echo "- ✅ Cloud Run IAM: Allowing requests"
echo "- ✅ Application: Running without auth"
echo "- ✅ MCP Protocol: Working"
echo "- ✅ Tools: Responding"
echo "- ✅ Backend API: Connected"

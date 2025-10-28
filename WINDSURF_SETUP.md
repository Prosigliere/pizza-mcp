# Windsurf Setup Guide

## Overview

To use the pizza MCP server with Windsurf, you need the local proxy because:

- **Windsurf expects**: stdio transport (stdin/stdout)
- **Your server provides**: HTTP/SSE transport (streamable-http)
- **Solution**: `local_proxy.py` bridges the two

## Setup Steps

### 1. Install Dependencies

```bash
pip install aiohttp
```

### 2. Configure Windsurf

Edit your Windsurf MCP settings file:

**Location**: `~/.codeium/windsurf/mcp_settings.json`

**Add this configuration**:

```json
{
  "mcpServers": {
    "pizza-mcp": {
      "command": "python3",
      "args": [
        "path to file"
      ],
      "env": {
        "REMOTE_MCP_URL": "path to deployed mcp server"
      }
    }
  }
}
```

**Important**: 
- The `REMOTE_MCP_URL` should end with `/mcp` (not just the base URL)

### 3. Restart Windsurf

Close and reopen Windsurf completely for the changes to take effect.

### 4. Verify It's Working

In Windsurf, try asking:
- "List all the pizza toppings"
- "Create a person named Alice with email alice@example.com and phone 555-1234"
- "What pizzas are available?"

## What Changed


## Troubleshooting

### "Command not found" or "Permission denied"

Make sure the proxy is executable:
```bash
chmod +x /Users/wesgoldwater/coding/pizza-mcp/local_proxy.py
```

### "Connection refused" or "Cannot connect"

1. Test the server directly:
   ```bash
   ./test_working.sh
   ```
2. Verify the URL in your config matches the deployment
3. Check that Cloud Run service is running

### "No tools available" in Windsurf

1. Check Windsurf logs (usually in the IDE's developer console)
2. Test the proxy manually:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | python3 local_proxy.py
   ```
3. Make sure you restarted Windsurf after changing the config

### Proxy returns errors

Check that:
- The `REMOTE_MCP_URL` ends with `/mcp`
- The Cloud Run service is accessible (run `./test_simple.sh`)
- You have `aiohttp` installed (`pip list | grep aiohttp`)

## How It Works

```
┌──────────────┐
│   Windsurf   │
│     IDE      │
└──────┬───────┘
       │ stdio (JSON-RPC over stdin/stdout)
       ▼
┌──────────────┐
│ local_proxy  │
│    .py       │
└──────┬───────┘
       │ HTTP/SSE (streamable-http)
       ▼
┌──────────────────────┐
│   Cloud Run          │
│   pizza-mcp server   │
└──────┬───────────────┘
       │ HTTP with x-api-key
       ▼
┌──────────────────────┐
│   Backend Pizza API  │
│   (prosigliere)      │
└──────────────────────┘
```

## Available Tools in Windsurf

Once configured, you'll have access to all tools:

## Alternative: Run Locally

If you prefer to run the server locally instead of using the Cloud Run deployment:

1. Start the local server:
   ```bash
   python server_no_auth.py
   ```

2. Update Windsurf config to use local URL:
   ```json
   "env": {
     "REMOTE_MCP_URL": "http://localhost:8080/mcp"
   }
   ```

3. Restart Windsurf

This is useful for development and testing without hitting the Cloud Run deployment.

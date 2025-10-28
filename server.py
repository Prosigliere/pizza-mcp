# server.py
import asyncio
import logging
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv # Import dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import AuthProvider, AccessToken
from starlette.requests import Request

# Load environment variables from .env file
# Make sure you have a .env file or set these in your Cloud Run environment
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Load configuration from environment variables
BASE_URL = os.getenv("PIZZA_API_BASE_URL", "https://fake-example-pizza-api.com")
API_KEY = os.getenv("PIZZA_API_KEY", "my_api_key")
PORT = int(os.getenv("PORT", 8080))
BRIDGE_SECRET_KEY = os.getenv("BRIDGE_SECRET_KEY", "bridge-secret-key") # Secret key for Windsurf to authenticate to this bridge


if not API_KEY:
    logger.error("PIZZA_API_KEY environment variable is not set.")
    exit(1)
if not BRIDGE_SECRET_KEY:
    logger.error("BRIDGE_SECRET_KEY environment variable is not set. Windsurf will not be able to authenticate.")
    # You might want to exit(1) here in production if auth is required

HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

# --- Authentication Provider for the MCP Bridge ---
class BridgeAuthProvider(AuthProvider):
    """Simple token-based authentication for the MCP bridge."""
    
    def __init__(self, secret_key: str):
        super().__init__()
        self.secret_key = secret_key
    
    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify the bearer token matches our secret key."""
        if token == self.secret_key:
            logger.debug("MCP Bridge authentication successful.")
            return AccessToken(
                access_token=token,
                token_type="bearer",
                claims={"authenticated": True}
            )
        else:
            logger.warning("MCP Bridge authentication failed. Invalid token.")
            return None

# Initialize FastMCP with the authentication provider
mcp = FastMCP(
    name="Pizza MCP Server on Cloud Run",
    auth=BridgeAuthProvider(BRIDGE_SECRET_KEY) if BRIDGE_SECRET_KEY else None
)

# --- Tool Helper ---
def call_pizza_api(method: str, path: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
    """Helper function to call the backend pizza API."""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(method, url, json=json_data, headers=HEADERS)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        # Check if response is empty or has no content type before trying .json()
        if response.status_code == 204 or not response.content:
            return {"status": "success", "message": "Operation successful, no content returned."}
        # Check content type before parsing JSON
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
        else:
            # Handle non-JSON responses if necessary, or return text
            logger.warning(f"Received non-JSON response from {url}: {response.text}")
            return {"status": "success", "message": "Operation successful", "raw_response": response.text}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Pizza API ({method.upper()} {url}): {e}")
        # Try to get more details from the response if available
        error_details = {"error": str(e)}
        if e.response is not None:
            try:
                 error_details["status_code"] = e.response.status_code
                 error_details["response_body"] = e.response.json() # Try to parse error body as JSON
            except ValueError: # If error response isn't JSON
                 error_details["response_body"] = e.response.text
            except Exception: # Fallback for any other parsing issue
                error_details["response_body"] = "Could not parse error response body."

        # Re-raise or return a structured error for MCP. Here, we'll raise.
        # MCP tools should ideally return data, raising exceptions might cause issues
        # depending on the client. Consider returning an error dict instead.
        # For simplicity now, we re-raise.
        raise Exception(f"Pizza API request failed: {error_details}")


# --- Tool Definitions (Keep these as they are) ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """Use this to add two numbers together. Args: a (int): The first number. b (int): The second number. Returns: int: The sum."""
    logger.info(f">>> Tool: 'add' called with numbers '{a}' and '{b}'")
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Use this to subtract two numbers. Args: a (int): The first number. b (int): The second number. Returns: int: The difference."""
    logger.info(f">>> Tool: 'subtract' called with numbers '{a}' and '{b}'")
    return a - b

# --- Person Tools ---
@mcp.tool()
def create_person(name: str, email: str, phone: str) -> Dict[str, Any]:
    """Creates a new person. Args: name (str): The name. email (str): The email. phone (str): The phone number. Returns: Dict: The created person."""
    logger.info(f">>> Tool: 'create_person' called with name='{name}', email='{email}', phone='{phone}'")
    return call_pizza_api("post", "/person", json_data={"name": name, "email": email, "phone": phone})

@mcp.tool()
def find_all_people() -> List[Dict[str, Any]]:
    """Retrieves all people. Returns: List[Dict]: A list of all people."""
    logger.info(">>> Tool: 'find_all_people' called")
    return call_pizza_api("get", "/person")

@mcp.tool()
def find_one_person(person_id: int) -> Dict[str, Any]:
    """Retrieves a single person by ID. Args: person_id (int): The ID. Returns: Dict: The person data."""
    logger.info(f">>> Tool: 'find_one_person' called with person_id={person_id}")
    return call_pizza_api("get", f"/person/{person_id}")

@mcp.tool()
def update_person(person_id: int, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
    """Updates a person. Args: person_id (int): The ID. name (Optional[str]): New name. email (Optional[str]): New email. phone (Optional[str]): New phone. Returns: Dict: Updated person data."""
    logger.info(f">>> Tool: 'update_person' called with person_id={person_id}")
    data = {k: v for k, v in {"name": name, "email": email, "phone": phone}.items() if v is not None}
    return call_pizza_api("patch", f"/person/{person_id}", json_data=data)

@mcp.tool()
def remove_person(person_id: int) -> Dict[str, str]:
    """Deletes a person. Args: person_id (int): The ID. Returns: Dict: Confirmation message."""
    logger.info(f">>> Tool: 'remove_person' called with person_id={person_id}")
    return call_pizza_api("delete", f"/person/{person_id}")


# --- Topping Tools ---
@mcp.tool()
def create_topping(name: str, description: str, kosher: Optional[bool] = False, spicy: Optional[bool] = False, gluten_free: Optional[bool] = False) -> Dict[str, Any]:
    """Creates a topping. Args: name (str): Name. description (str): Description. kosher (Optional[bool]): Is it kosher?. spicy (Optional[bool]): Is it spicy?. gluten_free (Optional[bool]): Is it gluten-free?. Returns: Dict: Created topping."""
    logger.info(f">>> Tool: 'create_topping' called with name='{name}'")
    data = {"name": name, "description": description, "kosher": kosher, "spicy": spicy, "gluten_free": gluten_free}
    return call_pizza_api("post", "/topping", json_data=data)

@mcp.tool()
def find_all_toppings() -> List[Dict[str, Any]]:
    """Retrieves all toppings. Returns: List[Dict]: List of toppings."""
    logger.info(">>> Tool: 'find_all_toppings' called")
    return call_pizza_api("get", "/topping")

@mcp.tool()
def find_one_topping(topping_id: int) -> Dict[str, Any]:
    """Retrieves a single topping by ID. Args: topping_id (int): The ID. Returns: Dict: Topping data."""
    logger.info(f">>> Tool: 'find_one_topping' called with topping_id={topping_id}")
    return call_pizza_api("get", f"/topping/{topping_id}")

@mcp.tool()
def update_topping(topping_id: int, name: Optional[str] = None, description: Optional[str] = None, kosher: Optional[bool] = None, spicy: Optional[bool] = None, gluten_free: Optional[bool] = None) -> Dict[str, Any]:
    """Updates a topping. Args: topping_id (int): The ID. name (Optional[str])... Returns: Dict: Updated topping."""
    logger.info(f">>> Tool: 'update_topping' called with topping_id={topping_id}")
    data = {k: v for k, v in {"name": name, "description": description, "kosher": kosher, "spicy": spicy, "gluten_free": gluten_free}.items() if v is not None}
    return call_pizza_api("patch", f"/topping/{topping_id}", json_data=data)

@mcp.tool()
def remove_topping(topping_id: int) -> Dict[str, str]:
    """Deletes a topping. Args: topping_id (int): The ID. Returns: Dict: Confirmation message."""
    logger.info(f">>> Tool: 'remove_topping' called with topping_id={topping_id}")
    return call_pizza_api("delete", f"/topping/{topping_id}")


# --- API Documentation Tools ---
@mcp.tool()
def get_api_documentation() -> Dict[str, Any]:
    """Retrieves the complete OpenAPI/Swagger documentation for the Pizza API. 
    This includes all available endpoints, request/response schemas, and API details.
    Use this to understand what HTTP endpoints are available and how to call them.
    Returns: Dict: The complete OpenAPI specification."""
    logger.info(">>> Tool: 'get_api_documentation' called")
    return call_pizza_api("get", "/api")

@mcp.tool()
def get_api_endpoints_summary() -> Dict[str, Any]:
    """Retrieves a summary of all available API endpoints with their methods and paths.
    This is useful for quickly seeing what endpoints exist without the full schema details.
    Returns: Dict: Summary of endpoints grouped by resource type."""
    logger.info(">>> Tool: 'get_api_endpoints_summary' called")
    try:
        spec = call_pizza_api("get", "/api")
        
        # Parse the OpenAPI spec to extract endpoint summaries
        endpoints = {}
        if "paths" in spec:
            for path, methods in spec["paths"].items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                        endpoint_key = f"{method.upper()} {path}"
                        endpoints[endpoint_key] = {
                            "method": method.upper(),
                            "path": path,
                            "summary": details.get("summary", ""),
                            "description": details.get("description", ""),
                            "operationId": details.get("operationId", "")
                        }
        
        return {
            "base_url": BASE_URL,
            "api_key_required": True,
            "api_key_header": "x-api-key",
            "endpoints": endpoints
        }
    except Exception as e:
        logger.error(f"Error parsing API documentation: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_endpoint_details(method: str, path: str) -> Dict[str, Any]:
    """Retrieves detailed information about a specific API endpoint including request/response schemas.
    Args: 
        method (str): HTTP method (GET, POST, PUT, PATCH, DELETE)
        path (str): API path (e.g., '/pizza', '/person/{id}')
    Returns: Dict: Detailed endpoint information including parameters and schemas."""
    logger.info(f">>> Tool: 'get_endpoint_details' called with method='{method}', path='{path}'")
    try:
        spec = call_pizza_api("get", "/api")
        
        method_lower = method.lower()
        if "paths" in spec and path in spec["paths"] and method_lower in spec["paths"][path]:
            endpoint_spec = spec["paths"][path][method_lower]
            
            # Extract relevant details
            details = {
                "method": method.upper(),
                "path": path,
                "base_url": BASE_URL,
                "summary": endpoint_spec.get("summary", ""),
                "description": endpoint_spec.get("description", ""),
                "operationId": endpoint_spec.get("operationId", ""),
                "parameters": endpoint_spec.get("parameters", []),
                "requestBody": endpoint_spec.get("requestBody", {}),
                "responses": endpoint_spec.get("responses", {}),
                "authentication": {
                    "required": True,
                    "header": "x-api-key",
                    "note": "Include API key in x-api-key header"
                }
            }
            
            return details
        else:
            return {"error": f"Endpoint {method.upper()} {path} not found in API specification"}
    except Exception as e:
        logger.error(f"Error getting endpoint details: {e}")
        return {"error": str(e)}


# --- Pizza Tools ---
@mcp.tool()
def create_pizza(name: str, person_id: int, topping_ids: List[int]) -> Dict[str, Any]:
    """Creates a new pizza. Args: name (str): Pizza name. person_id (int): Owner ID. topping_ids (List[int]): List of topping IDs. Returns: Dict: Created pizza."""
    logger.info(f">>> Tool: 'create_pizza' called with name='{name}'")
    data = {"name": name, "personId": person_id, "toppingIds": topping_ids}
    return call_pizza_api("post", "/pizza", json_data=data)

@mcp.tool()
def find_all_pizzas() -> List[Dict[str, Any]]:
    """Retrieves all pizzas. Returns: List[Dict]: List of pizzas."""
    logger.info(">>> Tool: 'find_all_pizzas' called")
    return call_pizza_api("get", "/pizza")

@mcp.tool()
def find_one_pizza(pizza_id: int) -> Dict[str, Any]:
    """Retrieves a single pizza by ID. Args: pizza_id (int): The ID. Returns: Dict: Pizza data."""
    logger.info(f">>> Tool: 'find_one_pizza' called with pizza_id={pizza_id}")
    return call_pizza_api("get", f"/pizza/{pizza_id}")

@mcp.tool()
def update_pizza(pizza_id: int, name: Optional[str] = None, person_id: Optional[int] = None, topping_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    """Updates a pizza. Args: pizza_id (int): The ID. name (Optional[str])... Returns: Dict: Updated pizza."""
    logger.info(f">>> Tool: 'update_pizza' called with pizza_id={pizza_id}")
    data = {k: v for k, v in {"name": name, "personId": person_id, "toppingIds": topping_ids}.items() if v is not None}
    return call_pizza_api("patch", f"/pizza/{pizza_id}", json_data=data)

@mcp.tool()
def remove_pizza(pizza_id: int) -> Dict[str, str]:
    """Deletes a pizza. Args: pizza_id (int): The ID. Returns: Dict: Confirmation message."""
    logger.info(f">>> Tool: 'remove_pizza' called with pizza_id={pizza_id}")
    return call_pizza_api("delete", f"/pizza/{pizza_id}")

# --- Main execution ---
if __name__ == "__main__":
    logger.info(f"MCP server starting on port {PORT}")
    # Use the synchronous run() method which handles asyncio internally
    mcp.run(
        transport="streamable-http",  # Correct transport for Cloud Run/most web deployments
        host="0.0.0.0",               # Listen on all interfaces (required for containers)
        port=PORT,
    )
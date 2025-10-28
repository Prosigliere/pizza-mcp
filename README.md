# Pizza MCP Server

A Model Context Protocol (MCP) server for managing pizzas, toppings, and people.

## Fixed Issues

✅ **Line 5 Error Fixed**: The `requests` module import error has been resolved by:
1. Adding proper `[project]` configuration to `pyproject.toml`
2. Installing all required dependencies using `uv sync`
3. Upgrading `fastmcp` from 2.6.1 to 2.13.0.1 to fix compatibility issues
4. Updating FastMCP initialization API calls (`title` → `name`, `auth_handler` → `auth`)

## Setup

### Prerequisites
- Python 3.10 or higher
- `uv` package manager

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file (optional, see `.env.example`):
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration:
   - `PIZZA_API_BASE_URL`: Backend API URL
   - `PIZZA_API_KEY`: API authentication key
   - `BRIDGE_SECRET_KEY`: MCP server authentication key
   - `PORT`: Server port (default: 8080)

## Running the Server

```bash
uv run python server.py
```

The server will start on `http://0.0.0.0:8080` by default.

## Available Tools

### Math Tools
- `add(a, b)` - Add two numbers
- `subtract(a, b)` - Subtract two numbers

### Person Management
- `create_person(name, email, phone)` - Create a new person
- `find_all_people()` - Get all people
- `find_one_person(person_id)` - Get a specific person
- `update_person(person_id, ...)` - Update person details
- `remove_person(person_id)` - Delete a person

### Topping Management
- `create_topping(name, description, ...)` - Create a new topping
- `find_all_toppings()` - Get all toppings
- `find_one_topping(topping_id)` - Get a specific topping
- `update_topping(topping_id, ...)` - Update topping details
- `remove_topping(topping_id)` - Delete a topping

### Pizza Management
- `create_pizza(name, person_id, topping_ids)` - Create a new pizza
- `find_all_pizzas()` - Get all pizzas
- `find_one_pizza(pizza_id)` - Get a specific pizza
- `update_pizza(pizza_id, ...)` - Update pizza details
- `remove_pizza(pizza_id)` - Delete a pizza

## Dependencies

- `fastmcp` - MCP server framework
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `starlette` - Web framework components

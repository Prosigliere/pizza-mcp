import asyncio
import logging
import os
import requests
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("MCP Server on Cloud Run")

BASE_URL = "https://prosigliere-pizza-47901888500.us-central1.run.app"
API_KEY = "a9bn9VFnQ7kuI8cHiyEFZG9XC9aQo8WP"
HEADERS = {"x-api-key": API_KEY}


@mcp.tool()
def add(a: int, b: int) -> int:
    """Use this to add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    logger.info(f">>> Tool: 'add' called with numbers '{a}' and '{b}'")
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Use this to subtract two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference of the two numbers.
    """
    logger.info(f">>> Tool: 'subtract' called with numbers '{a}' and '{b}'")
    return a - b


# --- Person Tools ---
@mcp.tool()
def create_person(name: str, email: str, phone: str) -> Dict[str, Any]:
    """Creates a new person.

    Args:
        name: The name of the person.
        email: The email of the person.
        phone: The phone number of the person.

    Returns:
        The created person's data.
    """
    logger.info(f">>> Tool: 'create_person' called with name='{name}', email='{email}', phone='{phone}'")
    response = requests.post(f"{BASE_URL}/person", json={"name": name, "email": email, "phone": phone}, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_all_people() -> List[Dict[str, Any]]:
    """Retrieves all people.

    Returns:
        A list of all people.
    """
    logger.info(">>> Tool: 'find_all_people' called")
    response = requests.get(f"{BASE_URL}/person", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_one_person(person_id: int) -> Dict[str, Any]:
    """Retrieves a single person by their ID.

    Args:
        person_id: The ID of the person to retrieve.

    Returns:
        The person's data.
    """
    logger.info(f">>> Tool: 'find_one_person' called with person_id={person_id}")
    response = requests.get(f"{BASE_URL}/person/{person_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def update_person(person_id: int, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
    """Updates a person's details.

    Args:
        person_id: The ID of the person to update.
        name: The new name of the person.
        email: The new email of the person.
        phone: The new phone number of the person.

    Returns:
        The updated person's data.
    """
    logger.info(f">>> Tool: 'update_person' called with person_id={person_id}")
    data = {}
    if name:
        data["name"] = name
    if email:
        data["email"] = email
    if phone:
        data["phone"] = phone
    response = requests.patch(f"{BASE_URL}/person/{person_id}", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def remove_person(person_id: int) -> Dict[str, str]:
    """Deletes a person.

    Args:
        person_id: The ID of the person to delete.

    Returns:
        A confirmation message.
    """
    logger.info(f">>> Tool: 'remove_person' called with person_id={person_id}")
    response = requests.delete(f"{BASE_URL}/person/{person_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


# --- Topping Tools ---
@mcp.tool()
def create_topping(
    name: str,
    description: str,
    kosher: Optional[bool] = False,
    spicy: Optional[bool] = False,
    gluten_free: Optional[bool] = False,
) -> Dict[str, Any]:
    """Creates a new topping.

    Args:
        name: The name of the topping.
        description: A description of the topping.
        kosher: Whether the topping is kosher.
        spicy: Whether the topping is spicy.
        gluten_free: Whether the topping is gluten-free.

    Returns:
        The created topping's data.
    """
    logger.info(f">>> Tool: 'create_topping' called with name='{name}'")
    data = {
        "name": name,
        "description": description,
        "kosher": kosher,
        "spicy": spicy,
        "gluten_free": gluten_free,
    }
    response = requests.post(f"{BASE_URL}/topping", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_all_toppings() -> List[Dict[str, Any]]:
    """Retrieves all toppings.

    Returns:
        A list of all toppings.
    """
    logger.info(">>> Tool: 'find_all_toppings' called")
    response = requests.get(f"{BASE_URL}/topping", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_one_topping(topping_id: int) -> Dict[str, Any]:
    """Retrieves a single topping by its ID.

    Args:
        topping_id: The ID of the topping to retrieve.

    Returns:
        The topping's data.
    """
    logger.info(f">>> Tool: 'find_one_topping' called with topping_id={topping_id}")
    response = requests.get(f"{BASE_URL}/topping/{topping_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def update_topping(
    topping_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    kosher: Optional[bool] = None,
    spicy: Optional[bool] = None,
    gluten_free: Optional[bool] = None,
) -> Dict[str, Any]:
    """Updates a topping's details.

    Args:
        topping_id: The ID of the topping to update.
        name: The new name of the topping.
        description: The new description of the topping.
        kosher: The new kosher status.
        spicy: The new spicy status.
        gluten_free: The new gluten-free status.

    Returns:
        The updated topping's data.
    """
    logger.info(f">>> Tool: 'update_topping' called with topping_id={topping_id}")
    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    if kosher is not None:
        data["kosher"] = kosher
    if spicy is not None:
        data["spicy"] = spicy
    if gluten_free is not None:
        data["gluten_free"] = gluten_free
    response = requests.patch(f"{BASE_URL}/topping/{topping_id}", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def remove_topping(topping_id: int) -> Dict[str, str]:
    """Deletes a topping.

    Args:
        topping_id: The ID of the topping to delete.

    Returns:
        A confirmation message.
    """
    logger.info(f">>> Tool: 'remove_topping' called with topping_id={topping_id}")
    response = requests.delete(f"{BASE_URL}/topping/{topping_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


# --- Pizza Tools ---
@mcp.tool()
def create_pizza(name: str, person_id: int, topping_ids: List[int]) -> Dict[str, Any]:
    """Creates a new pizza.

    Args:
        name: The name of the pizza.
        person_id: The ID of the person who owns the pizza.
        topping_ids: A list of topping IDs to add to the pizza.

    Returns:
        The created pizza's data.
    """
    logger.info(f">>> Tool: 'create_pizza' called with name='{name}'")
    data = {"name": name, "personId": person_id, "toppingIds": topping_ids}
    response = requests.post(f"{BASE_URL}/pizza", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_all_pizzas() -> List[Dict[str, Any]]:
    """Retrieves all pizzas.

    Returns:
        A list of all pizzas.
    """
    logger.info(">>> Tool: 'find_all_pizzas' called")
    response = requests.get(f"{BASE_URL}/pizza", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def find_one_pizza(pizza_id: int) -> Dict[str, Any]:
    """Retrieves a single pizza by its ID.

    Args:
        pizza_id: The ID of the pizza to retrieve.

    Returns:
        The pizza's data.
    """
    logger.info(f">>> Tool: 'find_one_pizza' called with pizza_id={pizza_id}")
    response = requests.get(f"{BASE_URL}/pizza/{pizza_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def update_pizza(
    pizza_id: int,
    name: Optional[str] = None,
    person_id: Optional[int] = None,
    topping_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Updates a pizza's details.

    Args:
        pizza_id: The ID of the pizza to update.
        name: The new name of the pizza.
        person_id: The new owner of the pizza.
        topping_ids: The new list of topping IDs.

    Returns:
        The updated pizza's data.
    """
    logger.info(f">>> Tool: 'update_pizza' called with pizza_id={pizza_id}")
    data = {}
    if name:
        data["name"] = name
    if person_id:
        data["personId"] = person_id
    if topping_ids:
        data["toppingIds"] = topping_ids
    response = requests.patch(f"{BASE_URL}/pizza/{pizza_id}", json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def remove_pizza(pizza_id: int) -> Dict[str, str]:
    """Deletes a pizza.

    Args:
        pizza_id: The ID of the pizza to delete.

    Returns:
        A confirmation message.
    """
    logger.info(f">>> Tool: 'remove_pizza' called with pizza_id={pizza_id}")
    response = requests.delete(f"{BASE_URL}/pizza/{pizza_id}", headers=HEADERS)
    response.raise_for_status()
    return response.json()



if __name__ == "__main__":
    logger.info(f" MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="sse",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )

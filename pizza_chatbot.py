"""
This script demonstrates how to create a simple chatbot using Vertex AI's
Generative Models. The chatbot acts as a client to a remote MCP (Model
Controller Platform) server, retrieving tool definitions and executing them
over the network.

Prerequisites:
- Google Cloud SDK is initialized and authenticated.
  (e.g., `gcloud auth application-default login`)
- A Google Cloud project with the Vertex AI API enabled.
- The `google-cloud-aiplatform` and `fastmcp` libraries are installed.
- An MCP server (like the one in `server.py`) must be running and accessible.

Usage:
- Set the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` environment variables.
- Set the `MCP_SERVER_URL` environment variable to the URL of your deployed MCP server.
  (e.g., `export MCP_SERVER_URL="http://localhost:8080/mcp"`)
- Run the script: `python pizza_chatbot.py`
"""

import os
import asyncio
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    Tool,
)
from fastmcp import Client

# Your Google Cloud project ID and location
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# URL of the deployed MCP server
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8080/mcp")


async def main():
    """
    Initializes the Vertex AI SDK, connects to the MCP server, loads the
    Gemini model, and starts a chat session with the pizza bot.
    """
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # System prompt to define the chatbot's persona
    system_prompt = """
    You are a helpful pizza bot. Your goal is to assist users with creating
    and managing people, toppings, and pizzas using the available tools.
    You have full knowledge of all the tools and their functions.
    Be friendly, and guide the user through the process if they are unsure.
    """

    # Load the Gemini 1.0 Pro model with the system prompt
    model = GenerativeModel("gemini-1.0-pro", system_instruction=system_prompt)

    # Connect to the remote MCP server to get the tools
    print(f"Connecting to MCP server at {MCP_SERVER_URL} to get tools...")
    async with Client(MCP_SERVER_URL) as client:
        # Retrieve the tool definitions from the server
        # The client returns a list of FunctionDeclaration-like objects.
        function_declarations = await client.list_tools()
        tool_names = [decl.name for decl in function_declarations]
        print(f"Successfully retrieved tools: {', '.join(tool_names)}")

        # We need to wrap the declarations in a single Tool object for the Vertex AI SDK.
        pizza_tools = [Tool(function_declarations=function_declarations)] if function_declarations else []


        # Start a chat session with the model
        chat = model.start_chat()

        print("\nPizza Bot: Hello! How can I help you with your pizza order today?")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Pizza Bot: Goodbye!")
                break

            # Send the user's message to the model
            response = chat.send_message(user_input, tools=pizza_tools)

            # Handle tool calls from the model
            try:
                while response.candidates[0].content.parts[0].function_call.name:
                    function_call = response.candidates[0].content.parts[0].function_call
                    tool_name = function_call.name
                    tool_args = {key: value for key, value in function_call.args.items()}

                    print(f"Pizza Bot: Calling tool '{tool_name}' on remote server with args {tool_args}...")

                    # Call the tool on the remote server
                    tool_response_parts = await client.call_tool(tool_name, tool_args)

                    # The client returns a list of Part objects. We need to create a single
                    # function response part to send back to the model.
                    # We will aggregate the text content from the response parts.
                    response_content = " ".join(part.text for part in tool_response_parts if part.text)

                    # Send the tool's response back to the model
                    response = chat.send_message(
                        Part.from_function_response(
                            name=tool_name,
                            response={
                                "content": response_content,
                            }
                        ),
                        tools=pizza_tools
                    )

            except (AttributeError, IndexError):
                # This occurs when the response does not contain a function call.
                pass

            # Print the model's final text response.
            print(f"Pizza Bot: {response.text}")


if __name__ == "__main__":
    # The main function is async, so we run it with asyncio.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chatbot.")

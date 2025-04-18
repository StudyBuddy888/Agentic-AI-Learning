
#Using Function Calling Capabilities with LLMs

import json
import os
from typing import List

from litellm import completion

def list_files() -> List[str]:
    """List files in the current directory."""
    return os.listdir(".")

def read_file(file_name: str) -> str:
    """Read a file's contents."""
    try:
        with open(file_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except Exception as e:
        return f"Error: {str(e)}"
"""First, we define the actual Python functions that will be executed. 
    These contain the business logic for each tool and handle the actual 
        operations the AI agent can perform."""
tool_functions = {
    "list_files": list_files,
    "read_file": read_file
}


"""We maintain a dictionary that maps function names to their corresponding 
Python implementations. This registry allows us to easily look up and execute 
the appropriate function when the model calls it."""

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Returns a list of files in the directory.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {"file_name": {"type": "string"}},
                "required": ["file_name"]
            }
        }
    }
]

"""This is where we describe our tools to the model. Each tool specification includes:

A name that matches a key in our tool_functions dictionary
A description that helps the model understand when to use this tool
Parameters defined using JSON Schema, specifying the expected input format"""


# Our rules are simplified since we don't have to worry about getting a specific output format
agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools. 

If a user asks about files, documents, or content, first list the files before reading them.
"""
}]

"""The system message provides guidance on how the agent should behave. With function calling, 
we don’t need to instruct the model on how to format its outputs - 
we only need to focus on the decision-making logic"""

user_task = input("What would you like me to do? ")

memory = [{"role": "user", "content": user_task}]

messages = agent_rules + memory
"""We combine the system instructions with the user’s input to create the conversation context."""
response = completion(
    model="openai/gpt-4o",
    messages=messages,
    tools=tools,
    max_tokens=1024
)

"""The critical difference here is the inclusion of the tools parameter, 
which tells the model what functions it can call. 
This is what activates the function calling mechanism."""

# Extract the tool call from the response, note we don't have to parse now!
tool = response.choices[0].message.tool_calls[0]
tool_name = tool.function.name
tool_args = json.loads(tool.function.arguments)
result = tool_functions[tool_name](**tool_args)

"""When using function calling, 
the response comes back with a dedicated tool_calls array rather than free-text output. 
This ensures that:

The function name is properly identified
The arguments are correctly formatted as valid JSON
We don’t need to parse or extract from unstructured text"""

print(f"Tool Name: {tool_name}")
print(f"Tool Arguments: {tool_args}")
print(f"Result: {result}")
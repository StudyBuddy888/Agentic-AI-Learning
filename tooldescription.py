#The Power of Decorators
@register_tool(tags=["file_operations"])
def read_file(file_path: str) -> str:
    """Reads and returns the content of a file from the specified path.
    
    The function opens the file in read mode and returns its entire contents
    as a string. If the file doesn't exist or can't be read, it raises an
    appropriate exception.
    
    Args:
        file_path: The path to the file to read
        
    Returns:
        The contents of the file as a string
    """
    with open(file_path, 'r') as f:
        return f.read()
    

"""Our decorator examines the function and automatically:

Uses the function name as the tool name
Extracts the docstring for the description
Analyzes type hints and parameters to build the schema
Registers the tool in a central registry"""

#Implementing the Decorator
def register_tool(tool_name=None, description=None, 
                 parameters_override=None, terminal=False, tags=None):
    """Registers a function as an agent tool."""
    def decorator(func):
        # Extract all metadata from the function
        metadata = get_tool_metadata(
            func=func,
            tool_name=tool_name,
            description=description,
            parameters_override=parameters_override,
            terminal=terminal,
            tags=tags
        )
        
        # Register in our global tools dictionary
        tools[metadata["tool_name"]] = {
            "description": metadata["description"],
            "parameters": metadata["parameters"],
            "function": metadata["function"],
            "terminal": metadata["terminal"],
            "tags": metadata["tags"]
        }
        
        # Also maintain a tag-based index
        for tag in metadata["tags"]:
            if tag not in tools_by_tag:
                tools_by_tag[tag] = []
            tools_by_tag[tag].append(metadata["tool_name"])
        
        return func
    return decorator

def get_tool_metadata(func, tool_name=None, description=None, 
                     parameters_override=None, terminal=False, tags=None):
    """Extracts metadata for a function to use in tool registration."""
    
    # Use function name if no tool_name provided
    tool_name = tool_name or func.__name__
    
    # Use docstring if no description provided
    description = description or (func.__doc__.strip() 
                                if func.__doc__ else "No description provided.")
    
    # If no parameter override, analyze the function
    if parameters_override is None:
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Build JSON schema for arguments
        args_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Examine each parameter
        for param_name, param in signature.parameters.items():
            # Skip special parameters
            if param_name in ["action_context", "action_agent"]:
                continue

            # Convert Python types to JSON schema types
            param_type = type_hints.get(param_name, str)
            param_schema = {
                "type": get_json_type(param_type)
            }
            
            args_schema["properties"][param_name] = param_schema
            
            # If parameter has no default, it's required
            if param.default == inspect.Parameter.empty:
                args_schema["required"].append(param_name)
    else:
        args_schema = parameters_override
    
    return {
        "tool_name": tool_name,
        "description": description,
        "parameters": args_schema,
        "function": func,
        "terminal": terminal,
        "tags": tags or []
    }

#Consider how this simplifies adding a new parameter:
@register_tool(tags=["file_operations"])
def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    """Reads and returns the content of a file.
    
    Args:
        file_path: The path to the file to read
        encoding: The character encoding to use (default: utf-8)
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()
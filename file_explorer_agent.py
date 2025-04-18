#Complete Implementation
#Here’s the full implementation using the GAME framework:

def main():
    # Define the agent's goals
    goals = [
        Goal(
            priority=1, 
            name="Explore Files", 
            description="Explore files in the current directory by listing and reading them"
        ),
        Goal(
            priority=2, 
            name="Terminate", 
            description="Terminate the session when tasks are complete with a helpful summary"
        )
    ]
    
    # Define tool functions
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

    def terminate(message: str) -> str:
        """Terminate the agent loop and provide a summary message."""
        return message
    
    # Create action registry and register actions
    action_registry = ActionRegistry()
    
    action_registry.register(Action(
        name="list_files",
        function=list_files,
        description="Returns a list of files in the directory.",
        parameters={},
        terminal=False
    ))
    
    action_registry.register(Action(
        name="read_file",
        function=read_file,
        description="Reads the content of a specified file in the directory.",
        parameters={
            "type": "object",
            "properties": {
                "file_name": {"type": "string"}
            },
            "required": ["file_name"]
        },
        terminal=False
    ))
    
    action_registry.register(Action(
        name="terminate",
        function=terminate,
        description="Terminates the conversation. Prints the provided message for the user.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
            "required": ["message"]
        },
        terminal=True
    ))
    
    # Define the agent language and environment
    agent_language = AgentFunctionCallingActionLanguage()
    environment = Environment()
    
    # Create the agent
    file_explorer_agent = Agent(
        goals=goals,
        agent_language=agent_language,
        action_registry=action_registry,
        generate_response=generate_response,
        environment=environment
    )
    
    # Run the agent
    user_input = input("What would you like me to do? ")
    final_memory = file_explorer_agent.run(user_input, max_iterations=10)
    
    # Print the termination message (if any)
    for item in final_memory.get_memories():
        print(f"\nMemory: {item['content']}")

if __name__ == "__main__":
    main()

class Agent:
    def __init__(self,
                 goals: List[Goal],
                 agent_language: AgentLanguage,
                 action_registry: ActionRegistry,
                 generate_response: Callable[[Prompt], str],
                 environment: Environment):
        """
        Initialize an agent with its core GAME components
        """
        self.goals = goals
        self.generate_response = generate_response
        self.agent_language = agent_language
        self.actions = action_registry
        self.environment = environment

    def construct_prompt(self, goals: List[Goal], memory: Memory, actions: ActionRegistry) -> Prompt:
        """Build prompt with memory context"""
        return self.agent_language.construct_prompt(
            actions=actions.get_actions(),
            environment=self.environment,
            goals=goals,
            memory=memory
        )

    def get_action(self, response):
        invocation = self.agent_language.parse_response(response)
        action = self.actions.get_action(invocation["tool"])
        return action, invocation

    def should_terminate(self, response: str) -> bool:
        action_def, _ = self.get_action(response)
        return action_def.terminal

    def set_current_task(self, memory: Memory, task: str):
        memory.add_memory({"type": "user", "content": task})

    def update_memory(self, memory: Memory, response: str, result: dict):
        """
        Update memory with the agent's decision and the environment's response.
        """
        new_memories = [
            {"type": "assistant", "content": response},
            {"type": "user", "content": json.dumps(result)}
        ]
        for m in new_memories:
            memory.add_memory(m)

    def prompt_llm_for_action(self, full_prompt: Prompt) -> str:
        response = self.generate_response(full_prompt)
        return response

    def run(self, user_input: str, memory=None, max_iterations: int = 50) -> Memory:
        """
        Execute the GAME loop for this agent with a maximum iteration limit.
        """
        memory = memory or Memory()
        self.set_current_task(memory, user_input)

        for _ in range(max_iterations):
            # Construct a prompt that includes the Goals, Actions, and the current Memory
            prompt = self.construct_prompt(self.goals, memory, self.actions)

            print("Agent thinking...")
            # Generate a response from the agent
            response = self.prompt_llm_for_action(prompt)
            print(f"Agent Decision: {response}")

            # Determine which action the agent wants to execute
            action, invocation = self.get_action(response)

            # Execute the action in the environment
            result = self.environment.execute_action(action, invocation["args"])
            print(f"Action Result: {result}")

            # Update the agent's memory with information about what happened
            self.update_memory(memory, response, result)

            # Check if the agent has decided to terminate
            if self.should_terminate(response):
                break

        return memory


#let’s walk through how the GAME components work together in this agent architecture, explaining each part of agent loop.
#Step 1: Constructing the Prompt

def construct_prompt(self, goals: List[Goal], memory: Memory, actions: ActionRegistry) -> Prompt:
    """Build prompt with memory context"""
    return self.agent_language.construct_prompt(
        actions=actions.get_actions(),
        environment=self.environment,
        goals=goals,
        memory=memory
    )
#Step 2: Generating a Response
def prompt_llm_for_action(self, full_prompt: Prompt) -> str:
    response = self.generate_response(full_prompt)
    return response
#Step 3: Parsing the Response
def get_action(self, response):
    invocation = self.agent_language.parse_response(response)
    action = self.actions.get_action(invocation["tool"])
    return action, invocation
#The action is the interface definition of what the agent “can” do. The invocation

#Step 4: Executing the Action
# Execute the action in the environment
result = self.environment.execute_action(action, invocation["args"])

"""The Environment handles the actual execution of the action, which might involve:

Making API calls
Reading/writing files
Querying databases
Processing data"""
#Step 5: Updating Memory
def update_memory(self, memory: Memory, response: str, result: dict):
    """
    Update memory with the agent's decision and the environment's response.
    """
    new_memories = [
        {"type": "assistant", "content": response},
        {"type": "user", "content": json.dumps(result)}
    ]
    for m in new_memories:
        memory.add_memory(m)

#Step 6: Termination Check
def should_terminate(self, response: str) -> bool:
    action_def, _ = self.get_action(response)
    return action_def.terminal
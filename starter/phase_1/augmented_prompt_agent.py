from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

augmentedPromptAgent = AugmentedPromptAgent(openai_api_key, persona)

augmented_agent_response=augmentedPromptAgent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

print("The Augmented Prompt Agent uses - additionally to the knowledge contained in the LLM itself - additional knowledge which can be given to him via a system prompt." \
" If in the system prompt a persona is defined, the agent will formulate his answer from the perspective of the persona - and based on the persona's knowledge.")

# Test script for DirectPromptAgent class

from workflow_agents.base_agents import DirectPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

direct_agent_response = DirectPromptAgent(openai_api_key).respond(prompt)

# Print the response from the agent
print(direct_agent_response)

print("The Direct Prompt Agent uses general knowledge from the selected LLM and does not enrich it with additional knowledge from other sources.")

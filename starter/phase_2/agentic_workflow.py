# agentic_workflow.py

from workflow_agents.base_agents import ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

# load the product spec

with open("./starter/phase_2/Product-Spec-Email-Router.txt", "r", encoding="utf-8") as f:
    product_spec = f.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "For generating a development plan for a product, the following 3 steps need to be executed:\n"
    "1) User stories need to be generated based on a product specification. Stories should contain a persona, an action and a desired outcome. Each story represents a specific functionality of the product."
    "2) The generated user stories need to be grouped into features."
    "3) Concrete engineering tasks need to be derived from the user stories/features. They represent the engineering work required to develop the product."
    "Assure that for the generation of a product development plan, exactly these 3 steps are executed in sequence."
    # "Stories are defined from a product spec by identifying a "
    # "persona, an action, and a desired outcome for each story. "
    # "Each story represents a specific functionality of the product "
    # "described in the specification. \n"
    # "Features are defined by grouping related user stories. \n"
    # "Tasks are defined for each story and represent the engineering "
    # "work required to develop the product. \n"
    # "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    f"{product_spec}"
)
product_manager_knowledge_agent=KnowledgeAugmentedPromptAgent(openai_api_key, persona_product_manager, knowledge_product_manager)

# Product Manager - Evaluation Agent
persona_pm_eval_agent="You are a meticulous evaluation agent. You evaluate and verify the answers of other agents."
product_manager_eval_crit=(
    "The answers of the agents should be user stories. The description of the stories should have the following structure:"
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
    "The description always start with 'As a ' and contains the following information: Requesting persona, requested action and desired outcome."
)
product_manager_evaluation_agent = EvaluationAgent(openai_api_key, persona_pm_eval_agent, product_manager_eval_crit, product_manager_knowledge_agent, 3)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_program_manager, knowledge_program_manager)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
program_manager_eval_crit=(
    "The answer should be product features that follow the following structure: " \
    "Feature Name: A clear, concise title that identifies the capability\n" \
    "Description: A brief explanation of what the feature does and its purpose\n" \
    "Key Functionality: The specific capabilities or actions the feature provides\n" \
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(openai_api_key, persona_program_manager_eval, program_manager_eval_crit, program_manager_knowledge_agent, 3)


# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_dev_engineer, knowledge_dev_engineer)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
dev_engineer_eval_crit=(
    "The answer should be tasks following this exact structure: " \
    "Task ID: A unique identifier for tracking purposes\n" \
    "Task Title: Brief description of the specific development work\n" \
    "Related User Story: Reference to the parent user story\n" \
    "Description: Detailed explanation of the technical work required\n" \
    "Acceptance Criteria: Specific requirements that must be met for completion\n" \
    "Estimated Effort: Time or complexity estimation\n" \
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(openai_api_key, persona_dev_engineer_eval, dev_engineer_eval_crit, development_engineer_knowledge_agent, 3)

# Routing Agent
agents = [
    {
        "name": "product manager agent",
        "description": "Defines user stories for the functionalities which a product should have.",
        "func": lambda x: product_manager_support_function(x)
    },
    {
        "name": "program manager agent",
        "description": "Defines features of a product by organizing user stories into cohesive groups.",
        "func": lambda x: program_manager_support_function(x)
    },
    {
        "name": "development engineer",
        "description": "Derives concrete engineering tasks tasks for implementing user stories of a product.",
        "func": lambda x: development_engineer_support_function(x)
    }
]
routing_agent=RoutingAgent(openai_api_key, agents)

# Job function persona support functions

def product_manager_support_function(prompt):
    response = product_manager_knowledge_agent.respond(prompt)
    eval_result = product_manager_evaluation_agent.evaluate(response)
    return eval_result['final_response']

def program_manager_support_function(prompt):
    response = program_manager_knowledge_agent.respond(prompt)
    eval_result = program_manager_evaluation_agent.evaluate(response)
    return eval_result['final_response']

def development_engineer_support_function(prompt):
    response = development_engineer_knowledge_agent.respond(prompt)
    eval_result = development_engineer_evaluation_agent.evaluate(response)
    return eval_result['final_response']

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")

steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
completed_steps=[]
for i, step in enumerate(steps):
    curr_prompt = f"Task: {step}" 
    if(completed_steps):
        curr_prompt=curr_prompt+f". Data: {completed_steps}"
    result=routing_agent.route_prompt(curr_prompt)
    completed_steps.append(result)
    print(f"Workflow step {i+1}: {step}")
    print(f"Result: {result}")
if(completed_steps):
    print(f"Final output of workflow: {completed_steps[-1]}")
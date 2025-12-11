"""
"""

from google.adk.agents import SequentialAgent

from .util import load_instruction_from_file
from google.adk.tools import google_search
from google.adk.agents import LlmAgent
# from google.adk.models import Gemini

model="gemini-2.0-flash"

# --- Sub Agent 1: IngredientsGenerator ---
ingredients_generator_agent = LlmAgent(
    name="IngredientsGenerator",
    model=model,
    instruction=load_instruction_from_file("ingredients_generator_instructions.txt"),
    tools=[google_search],
    output_key="generated_ingredients",  # Save result to state
)

# --- Sub Agent 2: DiseaseIdentifier ---
disease_identifier_agent = LlmAgent(
    name="DiseaseIdentifier",
    model=model,
    instruction=load_instruction_from_file("disease_identifier_instructions.txt"),
    tools=[google_search],
)


# --- 3. Create the SequentialAgent ---
# This agent orchestrates the pipeline by running the sub-agents in order.
ingredients_x_disease_agent = SequentialAgent(
    name="IngredientsDiseasePipelineAgent",
    sub_agents=[
        ingredients_generator_agent,
        disease_identifier_agent,
    ],
    description="Executes a sequence of ingredient search followed by diesease identification stemming from those ingredients.",
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = ingredients_x_disease_agent

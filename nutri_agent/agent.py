"""
https://medium.com/@dharamai2024/structured-outputs-in-google-adk-part-3-of-the-series-80c683dc2d83
"""

from google.adk.agents import SequentialAgent

from .util import load_instruction_from_file
from google.adk.tools import google_search
from google.adk.agents import LlmAgent
import google.adk
from pydantic import BaseModel, Field

print(f'adk version: {google.adk.__version__}')
model="gemini-2.0-flash"

class IngredientList(BaseModel):
    ingredients: list[str] = Field(description="A list of ingredients")

# --- Sub Agent 1: IngredientsGenerator ---
ingredients_generator_agent = LlmAgent(
    name="IngredientsGenerator",
    model=model,
    instruction=load_instruction_from_file("ingredients_generator_instructions.txt"),
    tools=[google_search],
    output_schema=IngredientList,
    output_key="ingredients_list",  # Save result to state
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

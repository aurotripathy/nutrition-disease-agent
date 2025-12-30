"""
https://medium.com/@dharamai2024/structured-outputs-in-google-adk-part-3-of-the-series-80c683dc2d83
"""

from google.adk.agents import SequentialAgent

from .util import load_instruction_from_file
from google.adk.tools import google_search
from google.adk.agents import LlmAgent
import google.adk
from pydantic import BaseModel, Field
from typing import Dict
from .tools.get_nutriments_from_open_food_facts import get_grouped_nutriments_from_open_food_facts
import logging

from google.adk.tools.google_search_tool import GoogleSearchTool

logging.basicConfig(level=logging.DEBUG)

# Initialize the tool with the bypass parameter set to True
google_search_wrapper = GoogleSearchTool(bypass_multi_tools_limit=True)

logging.debug(f'adk version: {google.adk.__version__}')

model="gemini-2.5-pro"  # was flash
# model="gemini-2.5-flash"  # was flash

class IngredientsListAndAilment(BaseModel):
    food_item: str = Field(description="The food item name")
    ingredients: Dict[str, str]  = Field(description="A dictionary of ingredients and their quantities")
    ailment: str = Field(description="Optionally, a disease or ailment that the users is interested in associating with the ingredients")

# --- Sub Agent 1: IngredientsGenerator ---
ingredients_generator_agent = LlmAgent(
    name="IngredientsGenerator",
    model=model,
    instruction=load_instruction_from_file("ingredients_generator_instructions.txt"),
    # tools=[get_nutriments_from_off, google_search],
    tools=[get_grouped_nutriments_from_open_food_facts],
    output_schema=IngredientsListAndAilment,
    output_key="ingredients_list_and_ailment",  # Save result to state
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

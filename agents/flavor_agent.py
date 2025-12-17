"""
Flavor Profile Agent - Handles taste matching and allergy safety.
"""
import os
import sys
from strands import Agent
from strands.models import BedrockModel
from agents.tools.taste_tools import generate_taste_vector_tool
from agents.tools.allergy_tools import filter_dishes_by_allergy_hybrid
from agents.utils.guardrail import get_guardrail_id

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    guardrail_id=get_guardrail_id()
)

FLAVOR_AGENT_PROMPT = """You are a flavor profile agent specializing in taste matching and allergy safety.
Your role is to:
1. Generate taste vectors for dishes (6D: sweet, salty, sour, bitter, umami, spicy)
2. Filter dishes by allergies using hybrid approach (keyword + AI intersection) - SAFETY FIRST
3. Match user preferences to dish taste profiles (only for safe dishes)
4. Calculate similarity scores for safe dishes only

Always prioritize safety - filter allergies BEFORE taste matching.
Always provide accurate taste analysis."""

flavor_profile_agent = Agent(
    model=bedrock_model,
    system_prompt=FLAVOR_AGENT_PROMPT,
    tools=[generate_taste_vector_tool, filter_dishes_by_allergy_hybrid]
)

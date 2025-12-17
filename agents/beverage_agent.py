"""
Beverage Agent - Handles beer pairing recommendations.
"""
import os
import sys
from strands import Agent
from strands.models import BedrockModel
from agents.tools.beer_tools import check_menu_for_beer_tool, recommend_beer_pairing_tool
from agents.utils.guardrail import get_guardrail_id

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    guardrail_id=get_guardrail_id()
)

BEVERAGE_AGENT_PROMPT = """You are a beverage pairing agent specializing in beer recommendations.
Your role is to:
1. Check if restaurant serves beer (via menu URL)
2. Recommend beer pairings using ML model
3. Provide pairing explanations

Only recommend beer if the restaurant actually serves it."""

beverage_agent = Agent(
    model=bedrock_model,
    system_prompt=BEVERAGE_AGENT_PROMPT,
    tools=[check_menu_for_beer_tool, recommend_beer_pairing_tool]
)

"""
Yelp Discovery Agent - Searches for restaurants using Yelp AI API.
"""
import os
import sys
from strands import Agent
from strands.models import BedrockModel
from agents.tools.yelp_tools import yelp_search_tool
from agents.utils.guardrail import get_guardrail_id

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    guardrail_id=get_guardrail_id()
)

YELP_AGENT_PROMPT = """You are a restaurant discovery agent using Yelp AI API.
Your role is to:
1. Search for restaurants based on user preferences
2. Extract restaurant data from Yelp AI responses
3. Format results clearly

Always use the yelp_search_tool to find restaurants."""

yelp_discovery_agent = Agent(
    model=bedrock_model,
    system_prompt=YELP_AGENT_PROMPT,
    tools=[yelp_search_tool]
)

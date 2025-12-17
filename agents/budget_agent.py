"""
Budget Agent - Handles price filtering and budget analysis.
"""
import os
import sys
from strands import Agent
from strands.models import BedrockModel
from agents.tools.budget_tools import calculate_price_filter
from agents.utils.guardrail import get_guardrail_id

# Add backend to path for config
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
from config import GROQ_API_KEY

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    guardrail_id=get_guardrail_id()
)

BUDGET_AGENT_PROMPT = """You are a budget analysis agent for restaurant recommendations.
Your role is to:
1. Extract price/budget constraints from user queries
2. Calculate appropriate price filters for Yelp search
3. Provide budget-friendly recommendations

Always be helpful and provide clear budget guidance."""

budget_agent = Agent(
    model=bedrock_model,
    system_prompt=BUDGET_AGENT_PROMPT,
    tools=[calculate_price_filter]
)

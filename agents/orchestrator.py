"""
Orchestrator Agent - Coordinates multiple specialized agents.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
_agents_dir = Path(__file__).parent
_project_root = _agents_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Try to import strands - if not available, orchestrator will be disabled
try:
    from strands import Agent, tool
    from strands.models import BedrockModel
    from strands.agent.conversation_manager import SummarizingConversationManager
    STRANDS_AVAILABLE = True
except ImportError as e:
    STRANDS_AVAILABLE = False
    print(f"⚠️ Strands framework not available: {e}")
    print("⚠️ Agent system will use fallback mode. To enable full agent system:")
    print("   pip install strands-agents")
    print("   Note: Strands requires C++ compilation and may fail on some systems")

if not STRANDS_AVAILABLE:
    # Fallback function when strands is not available
    def process_query(query: str) -> str:
        """
        Fallback process_query when strands is not available.
        Returns error message indicating strands needs to be installed.
        """
        return "Agent system requires strands framework. Please install with: pip install strands-agents"

else:
    # Import agent modules only if strands is available
    from agents.budget_agent import budget_agent
    from agents.yelp_agent import yelp_discovery_agent
    from agents.flavor_agent import flavor_profile_agent
    from agents.beverage_agent import beverage_agent
    from agents.utils.guardrail import get_guardrail_id

    # Initialize Bedrock model only if strands is available
    bedrock_model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        guardrail_id=get_guardrail_id()
    )

    ORCHESTRATOR_PROMPT = """You are a restaurant recommendation orchestrator coordinating multiple specialized agents.

Your specialized agents are:
1. **budget_agent_tool**: Handles price filtering and budget analysis
2. **yelp_discovery_agent_tool**: Searches for restaurants using Yelp AI API
3. **flavor_profile_agent_tool**: Generates taste vectors, calculates flavor matching, and filters allergies
4. **beverage_agent_tool**: Recommends beer pairings (menu-aware)

Guidelines:
- Use **budget_agent_tool** for price/budget questions
- Use **yelp_discovery_agent_tool** for restaurant search
- Use **flavor_profile_agent_tool** for taste matching AND allergy filtering
- Use **beverage_agent_tool** for drink pairing recommendations
- You can use multiple agents together for complex queries
- Always synthesize responses into a coherent recommendation
- **CRITICAL**: If user mentions allergies, extract them and ensure flavor_profile_agent filters dishes
- Safety first: Never recommend dishes with allergens

When a user asks a question:
1. Extract any allergies mentioned (e.g., "peanut allergy", "lactose intolerant", "shellfish allergy")
2. Determine which agent(s) are needed
3. Call the relevant agent(s) with focused queries (include allergies if mentioned)
4. Synthesize responses into a comprehensive answer
5. Provide actionable recommendations with allergy safety noted"""


    @tool
    def budget_agent_tool(query: str) -> str:
        """Handle budget and price-related queries."""
        try:
            response = budget_agent(query)
            return str(response)
        except Exception as e:
            return f"Budget agent error: {str(e)}"


    @tool
    def yelp_discovery_agent_tool(query: str) -> str:
        """Handle restaurant discovery queries."""
        try:
            response = yelp_discovery_agent(query)
            return str(response)
        except Exception as e:
            return f"Yelp agent error: {str(e)}"


    @tool
    def flavor_profile_agent_tool(query: str) -> str:
        """Handle taste and flavor matching queries."""
        try:
            response = flavor_profile_agent(query)
            return str(response)
        except Exception as e:
            return f"Flavor agent error: {str(e)}"


    @tool
    def beverage_agent_tool(query: str) -> str:
        """Handle beverage pairing queries."""
        try:
            response = beverage_agent(query)
            return str(response)
        except Exception as e:
            return f"Beverage agent error: {str(e)}"


    # Conversation manager
    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.3,
        preserve_recent_messages=5
    )

    # Create orchestrator
    orchestrator_agent = Agent(
        model=bedrock_model,
        system_prompt=ORCHESTRATOR_PROMPT,
        tools=[
            budget_agent_tool,
            yelp_discovery_agent_tool,
            flavor_profile_agent_tool,
            beverage_agent_tool
        ],
        conversation_manager=conversation_manager
    )


    def process_query(query: str) -> str:
        """
        Process a user query through the orchestrator.
        
        Args:
            query: User's restaurant recommendation query
            
        Returns:
            Agent response string
        """
        try:
            response = orchestrator_agent(query)
            return str(response)
        except Exception as e:
            return f"Orchestrator error: {str(e)}"

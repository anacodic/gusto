"""
Yelp API tools for agent system.
"""
import json
import sys
import os
from typing import Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
from integrations.yelp_client import YelpAPIClient
from strands import tool

# Global Yelp client
_yelp_client = None


def get_yelp_client() -> Optional[YelpAPIClient]:
    """Get or initialize Yelp client."""
    global _yelp_client
    if _yelp_client is None:
        try:
            _yelp_client = YelpAPIClient()
        except Exception as e:
            print(f"❌ [Yelp Client] Failed to initialize: {e}")
    return _yelp_client


@tool
def yelp_search_tool(query: str, location: str = None, chat_id: str = None) -> str:
    """Search for restaurants using Yelp AI Chat API.
    
    Args:
        query: Search query (e.g., "spicy Thai restaurants")
        location: Location string (e.g., "Boston, MA") - will be added to query
        chat_id: Chat ID for multi-turn conversations (optional)
    
    Returns:
        JSON string with restaurant data from Yelp AI Chat API
    """
    print(f"🔍 [Yelp Tool] Searching: '{query}'" + (f" in {location}" if location else ""))
    try:
        yelp_client = get_yelp_client()
        if yelp_client is None:
            print("❌ [Yelp Tool] Yelp client not available")
            return json.dumps({"error": "Yelp API client not initialized"})
        
        # If location provided, add it to query
        if location:
            if location.lower() not in query.lower():
                query = f"{query} in {location}"
                print(f"📍 [Yelp Tool] Added location to query: '{query}'")
        
        print(f"📡 [Yelp Tool] Calling Yelp AI Chat API...")
        result = yelp_client.ai_chat_search(query=query, chat_id=chat_id)
        print(f"✅ [Yelp Tool] Received response from Yelp API")
        return json.dumps(result, indent=2)
    except Exception as e:
        print(f"❌ [Yelp Tool] Error: {str(e)}")
        return json.dumps({"error": str(e)})

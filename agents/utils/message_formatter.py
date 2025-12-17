"""
Message formatting utilities for agent responses.
"""
from typing import Dict, Any, List


def format_agent_response(response: Any) -> str:
    """
    Format agent response for display.
    
    Args:
        response: Agent response (can be string, dict, or other)
        
    Returns:
        Formatted string
    """
    if isinstance(response, str):
        return response
    elif isinstance(response, dict):
        # Extract text if available
        if "text" in response:
            return response["text"]
        elif "response" in response:
            return format_agent_response(response["response"])
        else:
            return str(response)
    else:
        return str(response)


def format_restaurant_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """
    Format restaurant recommendations for display.
    
    Args:
        recommendations: List of restaurant recommendation dicts
        
    Returns:
        Formatted string
    """
    if not recommendations:
        return "No recommendations found."
    
    lines = []
    for i, rec in enumerate(recommendations, 1):
        name = rec.get("name", "Unknown")
        rating = rec.get("rating", "N/A")
        price = rec.get("price_range", "N/A")
        lines.append(f"{i}. {name} (Rating: {rating}, Price: {price})")
    
    return "\n".join(lines)

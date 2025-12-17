"""
Guardrail utilities for Bedrock agents.
"""
import os
import boto3
from typing import Optional, Tuple

# Configure AWS clients
bedrock_client = boto3.client("bedrock", region_name=os.getenv("AWS_REGION", "us-east-1"))
bedrock_runtime = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))


def get_guardrail_id(guardrail_name: str = "guardrail-restaurant-safety") -> Optional[str]:
    """
    Get the guardrail ID for restaurant recommendations.
    
    Args:
        guardrail_name: Name of the guardrail to find
        
    Returns:
        str or None: The guardrail ID if found, None otherwise
    """
    try:
        existing_guardrails = bedrock_client.list_guardrails()
        for guardrail in existing_guardrails.get("guardrails", []):
            if guardrail.get("name") == guardrail_name:
                guardrail_id = guardrail.get("id")
                print(f"Found guardrail '{guardrail_name}' with ID: {guardrail_id}")
                return guardrail_id
        
        print(f"Guardrail '{guardrail_name}' not found")
        return None
        
    except Exception as e:
        print(f"Error finding guardrail: {e}")
        return None


def create_guardrail(guardrail_name: str = "guardrail-restaurant-safety") -> Optional[Tuple[str, str]]:
    """
    Create a Bedrock guardrail for restaurant recommendations.
    
    Returns:
        Tuple of (guardrail_id, guardrail_arn) if successful, None otherwise
    """
    try:
        # Check if guardrail already exists
        existing_guardrails = bedrock_client.list_guardrails()
        for guardrail in existing_guardrails.get("guardrails", []):
            if guardrail.get("name") == guardrail_name:
                print(f"Guardrail '{guardrail_name}' already exists")
                return (guardrail.get("id"), guardrail.get("arn"))
        
        # Create new guardrail
        print(f"Creating guardrail '{guardrail_name}'...")
        response = bedrock_client.create_guardrail(
            name=guardrail_name,
            description="Ensures restaurant recommendations are safe and appropriate",
            contentPolicyConfig={
                "filtersConfig": [
                    {
                        "type": "HATE",
                        "inputStrength": "NONE",
                        "outputStrength": "NONE"
                    },
                    {
                        "type": "MISCONDUCT",
                        "inputStrength": "NONE",
                        "outputStrength": "NONE"
                    },
                    {
                        "type": "PROMPT_ATTACK",
                        "inputStrength": "NONE",
                        "outputStrength": "NONE"
                    }
                ]
            }
        )
        
        guardrail_id = response.get("guardrailId")
        guardrail_arn = response.get("guardrailArn")
        print(f"Created guardrail '{guardrail_name}' with ID: {guardrail_id}")
        return (guardrail_id, guardrail_arn)
        
    except Exception as e:
        print(f"Error creating guardrail: {e}")
        return None

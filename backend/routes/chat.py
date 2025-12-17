"""
Chat endpoint for restaurant recommendations.
"""
from fastapi import HTTPException
from typing import Dict, Any, Optional, Tuple
import json
import re
import csv
import os

from models import ChatRequest
from database import get_dummy_user, sync_dummy_user_from_request, dummy_user_to_user_profile
from db import get_db, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from middleware.auth import get_current_user_id
from typing import Optional
from integrations.embeddings import embed_text, combine_vectors
from services.taste_service import user_profile_to_taste_vector, infer_taste_from_text_hybrid, taste_similarity
from integrations.pinecone_client import get_pinecone_index, maybe_upsert_ingredients_to_pinecone
from services.recommendation_service import filter_and_rank_recommendations
from services.restaurant_service import get_groq_client, classify_dish_diet_with_groq
from config import GROQ_API_KEY, USE_SEMANTIC_INGREDIENT_TASTE, USE_SEMANTIC_DISH_TASTE
from recipe_database import (
    load_recipes_database,
    search_recipe_by_name,
    get_taste_vector_from_recipe,
    has_valid_taste_profile
)

# Agent system integration
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from agents.orchestrator import process_query as orchestrator_process
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    print("⚠️ Agent system not available - using direct service calls")


# Load all ingredients from CSV at startup (cached globally)
_INGREDIENT_LIST = None

def load_ingredients_from_csv() -> list[str]:
    """Load all ingredient names from ingredient-flavor.csv"""
    global _INGREDIENT_LIST
    
    if _INGREDIENT_LIST is not None:
        return _INGREDIENT_LIST
    
    ingredients = []
    csv_path = os.path.join(os.path.dirname(__file__), "..", "ingredient-flavor.csv")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ingredient = row.get('ingredient', '').strip().lower()
                if ingredient:
                    ingredients.append(ingredient)
        
        _INGREDIENT_LIST = ingredients
        print(f"[INFO] Loaded {len(ingredients)} ingredients from CSV")
        return ingredients
    except Exception as e:
        print(f"[ERROR] Failed to load ingredients from CSV: {e}")
        # Fallback to basic list
        _INGREDIENT_LIST = ['chicken', 'paneer', 'ginger', 'garlic', 'tomato', 'onion']
        return _INGREDIENT_LIST


def extract_location_from_query(query: str) -> Optional[str]:
    """
    Extract location from the query text.

    Returns:
        Location string if found, None otherwise
    """
    query_lower = query.lower()

    # Location patterns
    patterns = [
        r'\bnear\s+(.+?)(?:\s*,|\s+also|\s+and|\s*$)',
        r'\bin\s+(.+?)(?:\s*,|\s+also|\s+and|\s*$)',
        r'\bat\s+(.+?)(?:\s*,|\s+also|\s+and|\s*$)',
        r'\baround\s+(.+?)(?:\s*,|\s+also|\s+and|\s*$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            location = match.group(1).strip()
            # Filter out common non-location words
            non_locations = ["me", "here", "there", "my place", "home"]
            if location not in non_locations and len(location) > 2:
                return location

    return None


def extract_cuisine_from_query(query: str) -> Optional[str]:
    """
    Extract cuisine type from the query text.

    Returns:
        Cuisine string if found (e.g., 'Thai', 'Italian', 'Chinese'), None otherwise
    """
    query_lower = query.lower()

    # Common cuisine types with their variations
    cuisines = {
        'thai': ['thai'],
        'italian': ['italian', 'pizza', 'pasta'],
        'chinese': ['chinese'],
        'japanese': ['japanese', 'sushi', 'ramen'],
        'indian': ['indian', 'curry'],
        'mexican': ['mexican', 'taco', 'burrito'],
        'korean': ['korean', 'kimchi', 'bibimbap'],
        'vietnamese': ['vietnamese', 'pho'],
        'american': ['american', 'burger'],
        'french': ['french'],
        'greek': ['greek'],
        'mediterranean': ['mediterranean'],
        'middle eastern': ['middle eastern', 'falafel', 'shawarma'],
        'spanish': ['spanish', 'tapas', 'paella'],
    }

    # Pattern: look for cuisine keywords in query
    # Examples: "Thai food", "Italian restaurant", "I want Chinese"
    for cuisine_name, keywords in cuisines.items():
        for keyword in keywords:
            # Check if keyword appears as a whole word
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower):
                print(f"[DEBUG] Cuisine type detected in query: {cuisine_name}")
                return cuisine_name

    return None


def extract_diet_from_query(query: str) -> Optional[str]:
    """
    Extract diet preference from the query text.

    This function checks:
    1. Explicit diet mentions (e.g., "I want veg food")
    2. Dish-based diet detection (e.g., "I want chicken curry" -> non-veg)

    Returns:
        'veg', 'vegetarian', 'non-veg', or None if not specified
    """
    query_lower = query.lower()

    # STEP 1: Check for explicit diet preference
    # Vegetarian indicators
    veg_patterns = [
        r'\b(?:i am|i\'m|looking for|want|need|prefer)\s+(?:a\s+)?veg(?:etarian)?\s+(?:food|dish|meal|option)',
        r'\bveg(?:etarian)?\s+(?:\w+\s+)?(?:food|dish|meal|option|restaurant|cuisine)',  # Allows "vegetarian Thai food"
        r'\bonly\s+veg(?:etarian)?',
        r'\bpure\s+veg(?:etarian)?',
        r'\bvegetarian\s+only',
        r'\bno\s+(?:meat|non-veg|nonveg)',
        r'\bplant[-\s]?based',
    ]

    # Non-vegetarian indicators
    nonveg_patterns = [
        r'\b(?:i am|i\'m|looking for|want|need|prefer)\s+(?:a\s+)?non[-\s]?veg(?:etarian)?\s+(?:food|dish|meal|option)',
        r'\bnon[-\s]?veg(?:etarian)?\s+(?:\w+\s+)?(?:food|dish|meal|option|restaurant|cuisine)',  # Allows "non-veg Thai food"
        r'\b(?:meat|chicken|fish|seafood)\s+(?:lover|eater)',
        r'\bonly\s+non[-\s]?veg',
    ]

    # Check for explicit vegetarian
    for pattern in veg_patterns:
        if re.search(pattern, query_lower):
            print(f"[DEBUG] Explicit veg preference detected in query")
            return "veg"

    # Check for explicit non-vegetarian
    for pattern in nonveg_patterns:
        if re.search(pattern, query_lower):
            print(f"[DEBUG] Explicit non-veg preference detected in query")
            return "non-veg"

    # STEP 2: Check for dish-based diet detection
    # Extract potential dish names from query
    dish_patterns = [
        # Specific pattern for "to eat/have/try X" - must come first
        r'(?:i want|i need)\s+to\s+(?:eat|have|try)\s+(?:some\s+)?(.+?)(?:\s+(?:near|in|at|and)|$)',
        # "I want to X" (where X is dish, not "to eat") - captures the dish after "to"
        r'(?:i want|i need)\s+to\s+(?!(?:eat|have|try)\s)(?:some\s+)?(.+?)(?:\s+(?:near|in|at|and)|$)',
        # General patterns (exclude "to" prefix)
        r'(?:i want|i need|looking for|get me|find|show me|give me)\s+(?!to\s)(?:some\s+)?(.+?)(?:\s+(?:near|in|at|and)|$)',
        r'(?:where.*get|where.*find)\s+(.+?)(?:\s+(?:near|in|at|and)|$)',
        r'(?:is there|do you have|any)\s+(.+?)(?:\s+(?:available|near|in|at)|$)',
    ]

    detected_dishes = []
    for pattern in dish_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            # Clean up the match
            dish = match.strip()
            # Remove common words
            dish = re.sub(r'\b(a|an|the|some|any|place|restaurant|where|that|has)\b', '', dish).strip()
            
            # Filter out generic/preference-only terms (same as is_dish_query)
            if dish and len(dish) > 2:
                # Check if it's just preferences/generic terms
                generic_terms = ["food", "something", "anything", "restaurant", "place", "restaurants", "places"]
                preference_words = ["spicy", "savory", "sweet", "sour", "salty", "bitter", "hot", "mild", 
                                   "delicious", "tasty", "good", "fresh", "healthy", "light", "heavy"]
                
                words = dish.split()
                meaningful_words = [w for w in words if w not in (generic_terms + preference_words + ["and", "or"])]
                
                # Only add if there are meaningful dish words
                if len(meaningful_words) > 0 and dish not in generic_terms:
                    detected_dishes.append(dish)

    # Classify detected dishes
    if detected_dishes:
        print(f"[DEBUG] Detected potential dishes in query: {detected_dishes}")

        veg_count = 0
        nonveg_count = 0

        for dish in detected_dishes:
            classification = classify_dish_diet_with_groq(dish)
            if classification == "veg":
                veg_count += 1
            else:
                nonveg_count += 1

        # If all dishes are veg, return veg
        if veg_count > 0 and nonveg_count == 0:
            print(f"[DEBUG] All detected dishes are vegetarian -> diet: veg")
            return "veg"

        # If all dishes are non-veg, return non-veg
        if nonveg_count > 0 and veg_count == 0:
            print(f"[DEBUG] All detected dishes are non-vegetarian -> diet: non-veg")
            return "non-veg"

        # If mixed, return None (use user profile default)
        if veg_count > 0 and nonveg_count > 0:
            print(f"[DEBUG] Mixed veg/non-veg dishes detected -> using user profile default")
            return None

    return None


def search_dish_in_db(dish_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for a dish using hybrid approach:
    1. Search Pinecone ingredients namespace
    2. Search recipe CSV database (231K recipes)
    3. Return None if not found

    Returns:
        Dict with dish info if found, None otherwise
    """
    # STEP 1: Search in Pinecone ingredients namespace
    try:
        pc_index = get_pinecone_index()

        # Create embedding for dish name using OpenAI API
        dish_embedding = embed_text(dish_name)

        # Search in ingredients namespace first
        result = pc_index.query(
            vector=dish_embedding,
            top_k=5,
            include_metadata=True,
            namespace="ingredients"
        )

        matches = result.get("matches", []) if isinstance(result, dict) else getattr(result, "matches", [])

        # Check if we have a good match (score > 0.8)
        if matches and len(matches) > 0:
            best_match = matches[0]
            score = best_match.get("score", 0) if isinstance(best_match, dict) else getattr(best_match, "score", 0)

            if score > 0.8:
                metadata = best_match.get("metadata") if isinstance(best_match, dict) else getattr(best_match, "metadata", {})
                print(f"[DEBUG] Found dish '{dish_name}' in Pinecone with score {score}")
                return {
                    "found": True,
                    "source": "pinecone",
                    "dish_name": metadata.get("name", dish_name),
                    "taste_vector": [
                        metadata.get("sweet", 0),
                        metadata.get("salty", 0),
                        metadata.get("sour", 0),
                        metadata.get("bitter", 0),
                        metadata.get("umami", 0),
                        metadata.get("spicy", 0)
                    ],
                    "ingredients": metadata.get("ingredients", []),
                    "metadata": metadata
                }

    except Exception as e:
        print(f"[ERROR] Failed to search dish in Pinecone: {e}")

    # STEP 2: Search in recipe CSV database (231K recipes)
    try:
        recipe = search_recipe_by_name(dish_name, threshold=0.6)

        if recipe and has_valid_taste_profile(recipe):
            taste_vector = get_taste_vector_from_recipe(recipe)
            print(f"[DEBUG] Found dish '{dish_name}' in recipe database: '{recipe['original_name']}'")
            return {
                "found": True,
                "source": "csv",
                "dish_name": recipe["original_name"],
                "taste_vector": taste_vector,
                "ingredients": recipe.get("ingredients", []),
                "metadata": {
                    "name": recipe["original_name"],
                    "ingredients": recipe.get("ingredients", []),
                    "recipe_id": recipe.get("id", "")
                }
            }
        elif recipe and not has_valid_taste_profile(recipe):
            print(f"[DEBUG] Found dish '{dish_name}' in CSV but has zero taste vector, will use Groq")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to search dish in recipe database: {e}")

    print(f"[DEBUG] Dish '{dish_name}' not found in any database")
    return None


def get_ingredients_from_groq(dish_name: str) -> Optional[Dict[str, Any]]:
    """
    Get ingredients and taste profile for a dish using Groq API.

    Returns:
        Dict with ingredients and taste vector, or None if failed
    """
    try:
        groq_client = get_groq_client()

        prompt = f"""Analyze the dish "{dish_name}" and provide:
1. Main ingredients (comma-separated list)
2. Taste profile on a scale of 0-1 for each: sweet, salty, sour, bitter, umami, spicy

Respond in this exact JSON format:
{{
    "dish_name": "{dish_name}",
    "ingredients": ["ingredient1", "ingredient2", ...],
    "taste_profile": {{
        "sweet": 0.0-1.0,
        "salty": 0.0-1.0,
        "sour": 0.0-1.0,
        "bitter": 0.0-1.0,
        "umami": 0.0-1.0,
        "spicy": 0.0-1.0
    }}
}}

Only respond with valid JSON, nothing else."""

        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500
        )

        response_text = completion.choices[0].message.content.strip()

        # Try to parse JSON
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        dish_info = json.loads(response_text)

        print(f"[DEBUG] Got ingredients from Groq for '{dish_name}': {dish_info.get('ingredients', [])}")

        return dish_info

    except Exception as e:
        print(f"[ERROR] Failed to get ingredients from Groq: {e}")
        return None


def save_dish_to_db(dish_name: str, dish_info: Dict[str, Any]) -> bool:
    """
    Save dish and its ingredients to Pinecone database.

    Args:
        dish_name: Name of the dish
        dish_info: Dict containing ingredients and taste_profile from Groq

    Returns:
        True if successful, False otherwise
    """
    try:
        pc_index = get_pinecone_index()

        taste_profile = dish_info.get("taste_profile", {})
        ingredients = dish_info.get("ingredients", [])

        # Create embedding for dish using OpenAI API
        dish_embedding = embed_text(dish_name)

        # Create taste vector
        taste_vector = [
            float(taste_profile.get("sweet", 0)),
            float(taste_profile.get("salty", 0)),
            float(taste_profile.get("sour", 0)),
            float(taste_profile.get("bitter", 0)),
            float(taste_profile.get("umami", 0)),
            float(taste_profile.get("spicy", 0))
        ]

        # Prepare vectors to upsert
        vectors = []

        # Add dish vector
        dish_vector = {
            "id": f"ingredient:{dish_name.lower().replace(' ', '_')}",
            "values": dish_embedding,
            "metadata": {
                "type": "ingredient",
                "name": dish_name,
                "sweet": taste_vector[0],
                "salty": taste_vector[1],
                "sour": taste_vector[2],
                "bitter": taste_vector[3],
                "umami": taste_vector[4],
                "spicy": taste_vector[5],
                "ingredients": ingredients[:10]  # Limit to 10 ingredients
            }
        }
        vectors.append(dish_vector)

        # Add ingredient vectors (if not already in DB)
        for ingredient in ingredients[:10]:  # Limit to 10 ingredients
            ingredient_embedding = embed_text(ingredient)

            # Use average taste profile for individual ingredients
            # (In a real system, you'd want to get specific taste profiles for each ingredient)
            ingredient_vector = {
                "id": f"ingredient:{ingredient.lower().replace(' ', '_')}",
                "values": ingredient_embedding,
                "metadata": {
                    "type": "ingredient",
                    "name": ingredient,
                    "sweet": taste_vector[0] * 0.5,  # Reduced weight for individual ingredients
                    "salty": taste_vector[1] * 0.5,
                    "sour": taste_vector[2] * 0.5,
                    "bitter": taste_vector[3] * 0.5,
                    "umami": taste_vector[4] * 0.5,
                    "spicy": taste_vector[5] * 0.5,
                }
            }
            vectors.append(ingredient_vector)

        # Upsert to Pinecone
        pc_index.upsert(vectors=vectors, namespace="ingredients")

        print(f"[DEBUG] Saved dish '{dish_name}' and {len(ingredients)} ingredients to DB")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save dish to DB: {e}")
        return False


def is_greeting(query: str) -> bool:
    """
    Check if the query is a greeting.

    Returns:
        True if query is a greeting, False otherwise
    """
    query_lower = query.lower().strip()
    greetings = [
        "hi", "hello", "hey", "hola", "greetings", "good morning",
        "good afternoon", "good evening", "howdy", "what's up",
        "whats up", "sup", "yo", "hiya", "heya"
    ]

    # Check if query is exactly a greeting or starts with greeting
    for greeting in greetings:
        if query_lower == greeting or query_lower.startswith(greeting + " "):
            return True

    return False


def normalize_dish_name_with_groq(dish_name: str) -> str:
    """
    Use Groq to normalize/correct misspelled or partial dish names.
    
    Args:
        dish_name: Raw dish name extracted from query (may be misspelled)
        
    Returns:
        Normalized dish name or original if Groq fails
    """
    try:
        groq_client = get_groq_client()
        
        prompt = f"""You are a food name correction assistant. Given a potentially misspelled or partial dish name, return the correct, most likely full dish name.

Examples:
- "pizz" -> "pizza"
- "burgr" -> "burger"  
- "pasta alfrd" -> "pasta alfredo"
- "panr tikka" -> "paneer tikka"
- "biryani" -> "biryani" (already correct)

Dish name: "{dish_name}"

Respond with ONLY the corrected dish name, nothing else. If the name seems correct, return it as is."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=50
        )
        
        corrected_name = response.choices[0].message.content.strip().lower()
        
        # Clean up the response (remove quotes, extra spaces)
        corrected_name = corrected_name.strip('"\'').strip()
        
        if corrected_name and corrected_name != dish_name.lower():
            print(f"[DEBUG] Groq corrected '{dish_name}' -> '{corrected_name}'")
            return corrected_name
        
        return dish_name
        
    except Exception as e:
        print(f"[ERROR] Groq normalization failed: {e}")
        return dish_name


def is_dish_query(query: str) -> Optional[str]:
    """
    Check if the query is asking for a specific dish (not at a specific restaurant).

    Handles both single and multiple dishes (e.g., "paratha and paneer curry").

    Returns:
        Dish name(s) if detected (comma-separated if multiple), None otherwise
    """
    query_lower = query.lower().strip()

    # Patterns for dish queries - more specific patterns
    patterns = [
        # "is there a place where X is available"
        r"is\s+there\s+(?:a\s+)?(?:place|restaurant)\s+(?:where|that\s+has)\s+(.+?)\s+(?:is\s+)?available",
        # "where can I find X" or "where can I get X" or "where i can get X"
        r"where\s+(?:can\s+)?i\s+(?:can\s+)?(?:find|get)\s+(.+?)(?:\s+near|\s+in|\s+at|\s*$)",
        # "do you have X" or "is there X"
        r"^(?:do\s+you\s+have|is\s+there)\s+(?:any\s+)?(.+?)(?:\s+available|\s+near|\s+in|\s+at|\s*$)",
        # "I want to eat/have/try X" - specific pattern to skip "to eat/have/try"
        r"^(?:i\s+want|i'd\s+like|i\s+need)\s+to\s+(?:eat|have|try)\s+(?:some\s+)?(.+?)(?:\s+near|\s+in|\s+at|\s*$)",
        # "I want to X" (where X is dish, not "to eat") - captures the dish after "to"
        r"^(?:i\s+want|i'd\s+like|i\s+need)\s+to\s+(?!(?:eat|have|try)\s)(?:some\s+)?(.+?)(?:\s+near|\s+in|\s+at|\s*$)",
        # "I want X" or "show me X" (no "to" involved)
        r"^(?:i\s+want|i'd\s+like|i\s+need|give\s+me|show\s+me|find|get\s+me|looking\s+for)\s+(?!to\s)(?:some\s+)?(.+?)(?:\s+near|\s+in|\s+at|\s*$)",
        # "can I get X"
        r"^can\s+i\s+get\s+(.+?)(?:\s+near|\s+in|\s+at|\s*$)",
    ]

    # Don't treat greetings or very short queries as dish queries
    if len(query_lower.split()) <= 1:
        return None

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            dish_name = match.group(1).strip()
            # Clean up the dish name
            dish_name = re.sub(r'\s+(?:near|in|at|from)\s+.*$', '', dish_name).strip()
            # Remove articles and common words
            dish_name = re.sub(r'^(?:a|an|the|some)\s+', '', dish_name).strip()
            
            # Filter out generic/vague terms that aren't dish names
            generic_terms = ["food", "something", "anything", "restaurant", "place", "restaurants", "places"]
            
            # Filter out preference descriptors (not actual dish names)
            preference_words = ["spicy", "savory", "sweet", "sour", "salty", "bitter", "hot", "mild", 
                               "delicious", "tasty", "good", "fresh", "healthy", "light", "heavy"]
            
            # Check if dish_name contains only generic terms and preferences
            words = dish_name.split()
            meaningful_words = [w for w in words if w not in (generic_terms + preference_words + ["and", "or"])]
            
            # If no meaningful dish name words remain, it's not a dish query
            if len(meaningful_words) == 0:
                return None  # It's just preferences/generic terms, not a dish name
            
            # Also reject if the whole phrase is a generic term
            if dish_name in generic_terms:
                return None
            
            if len(dish_name) > 2:
                return dish_name

    return None


def extract_ingredients_from_query(query: str) -> list[str]:
    """
    Extract ingredient names mentioned in the query.
    Uses the comprehensive ingredient list from ingredient-flavor.csv (622 ingredients).
    
    Returns:
        List of ingredient names found in query
    """
    query_lower = query.lower()
    
    # Load all ingredients from CSV (cached after first call)
    all_ingredients = load_ingredients_from_csv()
    
    found_ingredients = []
    
    # Check for each ingredient in the query
    # Sort by length (descending) to match longer phrases first
    # e.g., "soy sauce" before "soy"
    sorted_ingredients = sorted(all_ingredients, key=len, reverse=True)
    
    for ingredient in sorted_ingredients:
        # Use word boundaries to avoid partial matches
        # e.g., "ham" shouldn't match "graham"
        pattern = r'\b' + re.escape(ingredient) + r'\b'
        if re.search(pattern, query_lower):
            found_ingredients.append(ingredient)
    
    return found_ingredients


def is_restaurant_menu_query(query: str) -> Optional[str]:
    """
    Check if the query is asking for a specific restaurant's menu.

    Returns:
        Restaurant name if detected, None otherwise
    """
    query_lower = query.lower().strip()

    # Patterns for restaurant menu queries
    patterns = [
        r"(?:what'?s|show|tell me|get)\s+(?:the\s+)?menu\s+(?:for|of|at)\s+(.+?)(?:\s+restaurant)?$",
        r"menu\s+(?:for|of|at)\s+(.+?)(?:\s+restaurant)?$",
        r"(?:show|tell)\s+me\s+(.+?)(?:'s|\s+)menu",
        r"what\s+does\s+(.+?)\s+(?:have|serve|offer)",
        r"what\s+can\s+i\s+(?:get|order)\s+(?:at|from)\s+(.+?)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            restaurant_name = match.group(1).strip()
            # Clean up common words
            restaurant_name = re.sub(r'\s+restaurant$', '', restaurant_name).strip()
            if len(restaurant_name) > 2:
                return restaurant_name

    return None


def parse_specific_query(query: str) -> Optional[Tuple[str, str]]:
    """
    Parse query to detect if user is asking about a specific dish at a specific restaurant.

    Returns:
        Tuple of (dish_name, restaurant_name) if specific query detected, None otherwise
    """
    query_lower = query.lower()

    # Pattern: "dish ... where restaurant is X" or "dish ... at/from X"
    pattern1 = r"(.+?)\s+where\s+restaurant\s+is\s+(.+?)$"
    match = re.search(pattern1, query_lower)
    if match:
        dish = match.group(1).strip()
        restaurant = match.group(2).strip()
        # Clean up common prefixes
        dish = re.sub(r"^(?:i want|i'd like|give me|show me|find)\s+", "", dish).strip()
        dish = re.sub(r"\s+like\s+", " ", dish).strip()  # Remove "like"
        return (dish, restaurant)

    return None


async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint for restaurant recommendations.
    
    Flow:
    1. Use orchestrator agent system which routes to specialized agents
    2. yelp_discovery_agent uses Yelp AI Chat API via yelp_search_tool
    3. parse_yelp_response_tool maps Yelp response to frontend format
    4. Return formatted recommendations
    
    The orchestrator coordinates multiple agents:
    - yelp_discovery_agent: Searches restaurants using Yelp AI Chat API
    - flavor_profile_agent: Handles taste matching and allergy filtering
    - budget_agent: Handles price/budget queries
    - beverage_agent: Recommends beer pairings
    """
    # Setup: Direct service calls
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY")

    groq_client = get_groq_client()
    
    # Ensure ingredients are loaded into Pinecone (for dish/ingredient search only)
    maybe_upsert_ingredients_to_pinecone()

    # Sync user metadata from request
    sync_dummy_user_from_request(request)
    user_key = (request.user_key or "default").strip() or "default"
    dummy_user = get_dummy_user(user_key)
    dummy_profile = dummy_user_to_user_profile(dummy_user)

    # Extract user preferences
    allergies = (dummy_user.get("allergies") or []) if isinstance(dummy_user, dict) else []
    favorite_dishes = (dummy_user.get("favorite_dishes") or []) if isinstance(dummy_user, dict) else []
    diet_type = (dummy_user.get("diet_type") if isinstance(dummy_user, dict) else None) or "mix"

    print(f"[DEBUG] Using dummy user: {user_key}")
    print(f"[DEBUG] Allergies: {allergies}")
    print(f"[DEBUG] Favorite dishes: {favorite_dishes}")
    print(f"[DEBUG] Diet type: {diet_type}")

    if dummy_profile:
        allergies = dummy_profile.allergies or allergies
        favorite_dishes = [d.model_dump() for d in (dummy_profile.favorite_dishes or [])] or favorite_dishes
        diet_type = dummy_profile.diet_type or diet_type

    # Extract diet preference from query (overrides user profile)
    query_diet = extract_diet_from_query(request.query)
    if query_diet:
        diet_type = query_diet
        print(f"[DEBUG] Diet type overridden from query: {diet_type}")

    # Extract cuisine type from query
    query_cuisine = extract_cuisine_from_query(request.query)

    # Extract location from query (PRIORITY: query location overrides everything)
    query_location = extract_location_from_query(request.query)
    if query_location:
        # Query location takes highest priority
        request.location = query_location
        print(f"[DEBUG] Location extracted from query (PRIORITY): {query_location}")
        
        # If location is generic (downtown, nearby, etc.) and user has home city, contextualize it
        generic_locations = ["downtown", "nearby", "near me", "around here", "local", "in the area"]
        if any(generic in query_location.lower() for generic in generic_locations):
            user_db_location = (dummy_user.get("location") if isinstance(dummy_user, dict) else None) or ""
            if user_db_location:
                # Append user's city to make it specific
                request.location = f"{query_location}, {user_db_location}"
                print(f"[DEBUG] Contextualized generic location '{query_location}' with user city: {request.location}")
    elif not query_location and not request.location:
        # No location in query or request, will use fallback later
        print(f"[DEBUG] No location in query, will use fallback location")

    # Calculate user taste vector
    user_taste_vec = user_profile_to_taste_vector(dummy_profile) if dummy_profile else [0.0] * 6
    print(f"[DEBUG] Initial user_taste_vec from profile: {[round(x, 2) for x in user_taste_vec]}")
    
    fav_text = ""
    if favorite_dishes:
        try:
            fav_text = " ".join([
                (d.name if hasattr(d, "name") else (d.get("name") if isinstance(d, dict) else str(d)))
                for d in favorite_dishes
            ])
        except Exception:
            fav_text = ""
    
    print(f"[DEBUG] Favorite dishes text for taste inference: '{fav_text}'")
    inferred_user = infer_taste_from_text_hybrid(fav_text, semantic=USE_SEMANTIC_INGREDIENT_TASTE)
    print(f"[DEBUG] Inferred taste vector: {[round(x, 2) for x in inferred_user]}")
    user_taste_vec = combine_vectors(user_taste_vec, inferred_user, secondary_weight=0.35)
    print(f"[DEBUG] Final combined user_taste_vec: {[round(x, 2) for x in user_taste_vec]}")

    # Handle location and pending queries
    is_first_turn = not request.chat_id
    pending_query = dummy_user.get("pending_query") if isinstance(dummy_user, dict) else None
    if is_first_turn and pending_query and request.query and not request.location:
        request.location = request.query
        request.query = pending_query
        dummy_user["location"] = request.location
        dummy_user["pending_query"] = None
    
    user_db_location = (dummy_user.get("location") if isinstance(dummy_user, dict) else None) or ""
    fallback_location = request.location
    if not fallback_location and user_db_location:
        fallback_location = user_db_location
    
    print(f"[DEBUG] user_key: {user_key}")
    print(f"[DEBUG] user_db_location: {user_db_location}")
    print(f"[DEBUG] request.location: {request.location}")
    print(f"[DEBUG] fallback_location: {fallback_location}")

    # Set max results
    final_max_results = request.max_results or 10
    print(f"[DEBUG] max_results set to: {final_max_results}")

    # Initialize flags
    dish_not_found = False
    dish_not_found_name = None

    # Check if this is a greeting
    if is_greeting(request.query):
        print(f"[DEBUG] Greeting detected")
        greeting_responses = [
            "Hello! 👋 I'm Swaad, your AI food companion. I can help you discover amazing restaurants and dishes based on your taste preferences. What are you craving today?",
            "Hey there! 🍽️ Welcome to Swaad! Tell me what kind of food you're in the mood for, and I'll find the perfect restaurants for you.",
            "Hi! 😊 I'm here to help you find delicious food. Whether you're craving something spicy, sweet, or savory, just let me know and I'll recommend the best spots!",
        ]
        import random
        return {
            "response": {
                "text": random.choice(greeting_responses)
            },
            "chat_id": request.chat_id,
            "menu_buddy": {"recommendations": []}
        }

    # Check if query is relevant to food/restaurants
    from services.restaurant_service import is_relevant_query
    if not is_relevant_query(request.query):
        print(f"[DEBUG] Non-food query detected: '{request.query}'")
        out_of_scope_responses = [
            "I'm Swaad, your food and restaurant recommendation assistant! 🍽️ I specialize in helping you discover amazing dishes and restaurants. For questions about tourist attractions, hotels, or other travel info, you might want to check a travel guide. But if you're hungry and looking for great food recommendations, I'm here to help! What are you craving?",
            "I focus on food and restaurant recommendations! 😊 While I can't help with general travel or tourist spots, I'm excellent at finding delicious restaurants and dishes that match your taste. Want to explore some amazing food options instead?",
            "That's outside my expertise! I'm your AI food companion, specialized in restaurant and dish recommendations. 🍴 If you're looking for places to eat or specific dishes to try, I'm your go-to assistant! What kind of food are you in the mood for?"
        ]
        import random
        return {
            "response": {
                "text": random.choice(out_of_scope_responses)
            },
            "chat_id": request.chat_id,
            "menu_buddy": {"recommendations": []}
        }

    # Check if this is a restaurant menu query
    restaurant_name_query = is_restaurant_menu_query(request.query)
    if restaurant_name_query:
        print(f"[DEBUG] Restaurant menu query detected: '{restaurant_name_query}'")
        
        # Use orchestrator to search for restaurant via Yelp AI Chat API
        if AGENTS_AVAILABLE:
            try:
                agent_response = orchestrator_process(request.query)
                return {
                    "response": {
                        "text": agent_response
                    },
                    "chat_id": request.chat_id,
                    "menu_buddy": {
                        "recommendations": []
                    }
                }
            except Exception as e:
                print(f"⚠️ Agent system error: {e}")
        
        # If agents unavailable or failed
        return {
            "response": {
                "text": f"Sorry, I couldn't find a restaurant named '{restaurant_name_query}'. Could you try a different name or ask for dish recommendations instead?"
            },
            "chat_id": request.chat_id,
            "menu_buddy": {"recommendations": []}
        }

    # Check if this is a dish-specific query (not at a specific restaurant)
    dish_query = is_dish_query(request.query)
    if dish_query and "where restaurant is" not in request.query.lower():
        # Normalize dish name with Groq (correct typos, partial names)
        normalized_dish = normalize_dish_name_with_groq(dish_query)
        print(f"[DEBUG] Dish-specific query detected: '{dish_query}'" + 
              (f" -> normalized to '{normalized_dish}'" if normalized_dish != dish_query else ""))
        
        # Use normalized name for search
        dish_query = normalized_dish

        # STEP 1: Search for dish in our database
        dish_in_db = search_dish_in_db(dish_query)

        # STEP 2: If not found, get ingredients from Groq and save to DB
        if not dish_in_db:
            print(f"[DEBUG] Dish '{dish_query}' not in DB, calling Groq API...")
            dish_info_from_groq = get_ingredients_from_groq(dish_query)

            if dish_info_from_groq:
                # Save to database
                save_dish_to_db(dish_query, dish_info_from_groq)

                # Create dish_in_db structure from Groq response
                taste_profile = dish_info_from_groq.get("taste_profile", {})
                dish_in_db = {
                    "found": True,
                    "dish_name": dish_query,
                    "taste_vector": [
                        float(taste_profile.get("sweet", 0)),
                        float(taste_profile.get("salty", 0)),
                        float(taste_profile.get("sour", 0)),
                        float(taste_profile.get("bitter", 0)),
                        float(taste_profile.get("umami", 0)),
                        float(taste_profile.get("spicy", 0))
                    ],
                    "ingredients": dish_info_from_groq.get("ingredients", []),
                    "metadata": {
                        "name": dish_query,
                        "ingredients": dish_info_from_groq.get("ingredients", [])
                    }
                }

        # STEP 3: Search for restaurants that have this dish using orchestrator
        try:
            # Build query for orchestrator
            dish_search_query = f"restaurants with {dish_query}"
            if fallback_location:
                dish_search_query += f" in {fallback_location}"
            
            print(f"[DEBUG] Using orchestrator to search for restaurants with dish '{dish_query}'")
            
            if dish_in_db:
                # We have dish info, use it for taste-based recommendations
                print(f"[DEBUG] Using dish taste profile for recommendations")
                dish_taste_vec = dish_in_db.get("taste_vector", [0.0] * 6)
                # Combine user taste with dish taste
                user_taste_vec = combine_vectors(user_taste_vec, dish_taste_vec, secondary_weight=0.6)
            
            # Use orchestrator to find restaurants via Yelp AI Chat API
            if AGENTS_AVAILABLE:
                try:
                    agent_response = orchestrator_process(dish_search_query)
                    # Try to extract structured data from response
                    try:
                        import re
                        json_match = re.search(r'\{.*"restaurants".*\}', agent_response, re.DOTALL)
                        if json_match:
                            parsed_data = json.loads(json_match.group())
                            restaurants = parsed_data.get("restaurants", [])
                            if restaurants:
                                # Format for frontend
                                ranked_restaurants = []
                                for rest in restaurants[:final_max_results]:
                                    # Ensure the searched dish is in recommended_dishes
                                    recommended_dishes = rest.get("recommended_dishes", [])
                                    dish_found = False
                                    for dish in recommended_dishes:
                                        dish_name = dish.get("name", "").lower()
                                        if dish_query.lower() in dish_name or dish_name in dish_query.lower():
                                            dish_found = True
                                            recommended_dishes.remove(dish)
                                            recommended_dishes.insert(0, dish)
                                            break
                                    if not dish_found:
                                        dish_taste_vec = infer_taste_from_text_hybrid(dish_query, semantic=USE_SEMANTIC_DISH_TASTE)
                                        similarity = taste_similarity(user_taste_vec, dish_taste_vec)
                                        recommended_dishes.insert(0, {
                                            "name": dish_query,
                                            "similarity": round(similarity * 100, 1)
                                        })
                                    
                                    ranked_restaurants.append({
                                        "name": rest.get("name"),
                                        "rating": rest.get("avg_rating"),
                                        "price_range": rest.get("price_range"),
                                        "cuisine_types": rest.get("cuisine_types", []),
                                        "recommended_dishes": recommended_dishes[:5]
                                    })
                                
                                ranked_restaurants.sort(key=lambda x: x.get("rating", 0) or 0, reverse=True)
                                
                                return {
                                    "response": {
                                        "text": f"Great choice! I found restaurants that serve '{dish_query}'. Here are the top-rated ones:"
                                    },
                                    "chat_id": parsed_data.get("chat_id") or request.chat_id,
                                    "menu_buddy": {"recommendations": ranked_restaurants}
                                }
                    except Exception as e:
                        print(f"[DEBUG] Could not parse structured data: {e}")
                    
                    # Return text response if structured data not available
                    return {
                        "response": {
                            "text": agent_response
                        },
                        "chat_id": request.chat_id,
                        "menu_buddy": {"recommendations": []}
                    }
                except Exception as e:
                    print(f"⚠️ Orchestrator error: {e}")
            
            # If orchestrator unavailable or dish not found, set flag
            dish_not_found = True
            dish_not_found_name = dish_query

        except Exception as e:
            print(f"[DEBUG] Error in dish query: {e}")
            import traceback
            traceback.print_exc()
            dish_not_found = True
            dish_not_found_name = dish_query

    # Check if this is a specific query (dish at specific restaurant)
    specific_query = parse_specific_query(request.query)
    if specific_query:
        dish_name, restaurant_name = specific_query
        print(f"[DEBUG] Specific query detected: dish='{dish_name}', restaurant='{restaurant_name}'")

        # Use orchestrator to search for specific dish at restaurant via Yelp AI Chat API
        if AGENTS_AVAILABLE:
            try:
                agent_response = orchestrator_process(request.query)
                # Try to extract structured data
                try:
                    import re
                    json_match = re.search(r'\{.*"restaurants".*\}', agent_response, re.DOTALL)
                    if json_match:
                        parsed_data = json.loads(json_match.group())
                        restaurants = parsed_data.get("restaurants", [])
                        if restaurants:
                            # Find matching restaurant
                            target_restaurant = None
                            for rest in restaurants:
                                rest_name = rest.get("name", "").lower()
                                if restaurant_name.lower() in rest_name or rest_name in restaurant_name.lower():
                                    target_restaurant = rest
                                    break
                            
                            if target_restaurant:
                                # Check if dish is in recommended_dishes
                                matching_dish = None
                                recommended_dishes = target_restaurant.get("recommended_dishes", [])
                                for dish in recommended_dishes:
                                    dish_obj_name = dish.get("name", "").lower()
                                    if dish_name.lower() in dish_obj_name or dish_obj_name in dish_name.lower():
                                        matching_dish = dish.get("name")
                                        break
                                
                                if not matching_dish:
                                    matching_dish = dish_name
                                
                                return {
                                    "response": {
                                        "text": f"{matching_dish} is available at {target_restaurant.get('name')} (Rating: {target_restaurant.get('avg_rating', 'N/A')}/5)"
                                    },
                                    "chat_id": parsed_data.get("chat_id") or request.chat_id,
                                    "menu_buddy": {
                                        "recommendations": [{
                                            "name": target_restaurant.get("name"),
                                            "rating": target_restaurant.get("avg_rating"),
                                            "price_range": target_restaurant.get("price_range"),
                                            "cuisine_types": target_restaurant.get("cuisine_types", []),
                                            "recommended_dishes": [{"name": matching_dish, "similarity": 80.0}]
                                        }]
                                    }
                                }
                except Exception as e:
                    print(f"[DEBUG] Could not parse structured data: {e}")
                
                # Return text response
                return {
                    "response": {
                        "text": agent_response
                    },
                    "chat_id": request.chat_id,
                    "menu_buddy": {"recommendations": []}
                }
            except Exception as e:
                print(f"⚠️ Orchestrator error: {e}")
        
        # If orchestrator unavailable
        return {
            "response": {
                "text": f"Sorry, I couldn't find '{dish_name}' at '{restaurant_name}'. Please try again."
            },
            "chat_id": request.chat_id,
            "menu_buddy": {"recommendations": []}
        }

    # Check if location is provided (for general queries)
    if is_first_turn and not fallback_location:
        if isinstance(dummy_user, dict):
            dummy_user["pending_query"] = request.query
        return {
            "response": {
                "text": "Please share your location (city or ZIP/postal code) so I can find restaurants near you."
            },
            "chat_id": request.chat_id
        }

    # Use orchestrator with Yelp AI Chat API for restaurant recommendations
    print(f"[DEBUG] Using orchestrator with Yelp AI Chat API for restaurant recommendations")
    
    # Build query for orchestrator (include location if available)
    location_to_filter = query_location if query_location else fallback_location
    orchestrator_query = request.query
    if location_to_filter and location_to_filter.lower() not in orchestrator_query.lower():
        orchestrator_query = f"{request.query} in {location_to_filter}"
    
    # Initialize response structure
    if dish_not_found:
        if " and " in dish_not_found_name or "," in dish_not_found_name:
            initial_text = f"Sorry, I couldn't find '{dish_not_found_name}' at our partner restaurants. However, based on your preferences and the taste profile of these dishes, here are some recommendations you might enjoy:"
        else:
            initial_text = f"Sorry, I couldn't find '{dish_not_found_name}' at our partner restaurants. However, based on your preferences and the taste profile of this dish, here are some recommendations you might enjoy:"
    else:
        initial_text = f"Here are some great restaurant recommendations for you in {location_to_filter or 'your area'}!"

    ai_json = {
        "response": {
            "text": initial_text
        },
        "chat_id": request.chat_id
    }

    ranked = []
    
    # Use orchestrator to get restaurant recommendations via Yelp AI Chat API
    if AGENTS_AVAILABLE:
        try:
            print(f"[DEBUG] Calling orchestrator with query: '{orchestrator_query}'")
            print(f"[DEBUG] User preferences - Allergies: {allergies}, Diet: {diet_type}, Location: {location_to_filter}")
            
            # Build comprehensive query for orchestrator with all user preferences
            enhanced_query = orchestrator_query
            if allergies:
                enhanced_query += f" (allergies: {', '.join(allergies)})"
            if diet_type and diet_type != "mix":
                enhanced_query += f" ({diet_type} diet)"
            
            agent_response = orchestrator_process(enhanced_query)
            print(f"[DEBUG] Orchestrator returned response (length: {len(agent_response)} chars)")
            
            # Try to extract structured data from orchestrator response
            # The yelp_discovery_agent uses parse_yelp_response_tool which returns JSON
            # This JSON might be embedded in the agent's text response
            try:
                # Look for JSON blocks in the response (parse_yelp_response_tool returns JSON)
                import re
                # Try multiple extraction strategies
                parsed_data = None
                
                # Strategy 1: Look for JSON in markdown code blocks
                json_block_pattern = r'```(?:json)?\s*(\{.*?"restaurants".*?\})\s*```'
                json_block_match = re.search(json_block_pattern, agent_response, re.DOTALL)
                if json_block_match:
                    try:
                        parsed_data = json.loads(json_block_match.group(1))
                        if "restaurants" in parsed_data:
                            print(f"[DEBUG] Found structured data in code block with {len(parsed_data.get('restaurants', []))} restaurants")
                    except json.JSONDecodeError:
                        pass
                
                # Strategy 2: Find JSON object by matching braces (handles nested structures)
                if not parsed_data:
                    start_idx = agent_response.find('{"restaurants"')
                    if start_idx == -1:
                        start_idx = agent_response.find('{\n  "restaurants"')
                    if start_idx != -1:
                        # Find the matching closing brace by counting
                        brace_count = 0
                        end_idx = start_idx
                        for i in range(start_idx, len(agent_response)):
                            if agent_response[i] == '{':
                                brace_count += 1
                            elif agent_response[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        
                        if end_idx > start_idx:
                            json_str = agent_response[start_idx:end_idx]
                            try:
                                parsed_data = json.loads(json_str)
                                if "restaurants" in parsed_data:
                                    print(f"[DEBUG] Found structured data via brace matching with {len(parsed_data.get('restaurants', []))} restaurants")
                            except json.JSONDecodeError as e:
                                print(f"[DEBUG] JSON parse error: {e}")
                                pass
                
                if parsed_data and "restaurants" in parsed_data:
                    restaurants = parsed_data.get("restaurants", [])
                    if restaurants:
                        ranked = restaurants[:final_max_results]
                        response_text = parsed_data.get("response_text", agent_response)
                        chat_id = parsed_data.get("chat_id") or request.chat_id
                        ai_json["response"]["text"] = response_text
                        ai_json["chat_id"] = chat_id
                        print(f"[DEBUG] Extracted {len(ranked)} restaurants from orchestrator response")
            except Exception as e:
                print(f"[DEBUG] Could not parse structured data from orchestrator response: {e}")
                import traceback
                traceback.print_exc()
                # Use text response as-is
                ai_json["response"]["text"] = agent_response
            
            # If no structured data found, return text response
            if not ranked:
                return {
                    "response": {
                        "text": agent_response
                    },
                    "chat_id": request.chat_id,
                    "menu_buddy": {
                        "recommendations": []
                    }
                }
        except Exception as e:
            print(f"⚠️ Orchestrator error: {e}")
            import traceback
            traceback.print_exc()
            ranked = []
    else:
        print(f"⚠️ Agent system not available")
        ranked = []

    # If no results from orchestrator
    if len(ranked) == 0:
        if dish_not_found:
            no_results_msg = f"Sorry, I couldn't find '{dish_not_found_name}' or any similar dishes"
            if location_to_filter:
                no_results_msg += f" in {location_to_filter}"
            if allergies:
                no_results_msg += f" that are safe for your allergies ({', '.join(allergies)})"
            no_results_msg += ". Try a different location or dish!"
            ai_json["response"]["text"] = no_results_msg
        else:
            no_results_msg = "Sorry, I couldn't find any restaurants matching your preferences"
            if location_to_filter:
                no_results_msg += f" in {location_to_filter}"
            if diet_type and diet_type != "mix":
                no_results_msg += f" with {diet_type} options"
            if allergies:
                no_results_msg += f" that are safe for your allergies"
            no_results_msg += ". Try broadening your search or changing your location!"
            ai_json["response"]["text"] = no_results_msg
    
    # Filter response to only include essential fields
    filtered_recommendations = []
    for restaurant in ranked:
        filtered_restaurant = {
            "name": restaurant.get("name"),
            "rating": restaurant.get("avg_rating"),
            "price_range": restaurant.get("price_range"),
            "cuisine_types": restaurant.get("cuisine_types", []),
            "recommended_dishes": [
                {
                    "name": dish.get("name"),
                    "similarity": dish.get("similarity")
                }
                for dish in restaurant.get("recommended_dishes", [])[:5]  # Limit to top 5 dishes
            ]
        }
        filtered_recommendations.append(filtered_restaurant)

    ai_json["menu_buddy"] = {
        "recommendations": filtered_recommendations
    }
    
    # Rewrite response text to match filtered results
    try:
        original_text = ai_json.get("response", {}).get("text", "")
        if original_text and ranked:
            restaurant_names = [r.get("name") for r in ranked if r.get("name")]
            diet_label = "vegetarian" if diet_type in {"veg", "vegetarian"} else diet_type or "any diet"

            if dish_not_found:
                rewrite_prompt = f"""The user asked for '{dish_not_found_name}' but we don't have it at our partner restaurants.
Rewrite this text to:
1. Apologize that '{dish_not_found_name}' is not available at our partner restaurants
2. Mention these {len(ranked)} alternative restaurants: {', '.join(restaurant_names[:5])}
3. Say these are similar recommendations based on their taste preferences
4. Only mention dishes suitable for {diet_label} diet
5. Keep the tone friendly and helpful
6. Be concise (2-3 sentences max)

Original text: {original_text}

Rewritten text:"""
            else:
                rewrite_prompt = f"""Rewrite this restaurant recommendation text to:
1. Match the actual {len(ranked)} restaurants shown: {', '.join(restaurant_names[:5])}
2. Only mention dishes suitable for {diet_label} diet (NO meat, fish, eggs, or animal products if vegetarian)
3. Keep the tone friendly and helpful
4. Be concise (2-3 sentences max)

Original text: {original_text}

Rewritten text:"""

            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": rewrite_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=200
            )

            rewritten_text = completion.choices[0].message.content.strip()
            ai_json["response"]["text"] = rewritten_text
            print(f"[DEBUG] Rewrote response text for {diet_label} diet")
    except Exception as e:
        print(f"[DEBUG] Failed to rewrite response text: {e}")

    return ai_json


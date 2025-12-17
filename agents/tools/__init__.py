"""Agent tools for the multi-agent system.
All tools use the exact same functions from swaad/backend.
"""
# Taste analysis tools
from .taste_tools import (
    generate_taste_vector_tool,
    generate_taste_vector_groq_tool,
    generate_taste_vector_semantic_tool,
    calculate_taste_similarity_tool,
    calculate_favorites_boost_tool
)

# Recommendation tools
from .recommendation_tools import (
    get_dish_recommendations_tool,
    rank_restaurants_tool,
    calculate_restaurant_taste_vector_tool,
    filter_and_rank_recommendations_tool
)

# Dish processing tools
from .dish_processing_tools import (
    filter_dishes_by_diet_tool,
    detect_diet_from_query_tool,
    classify_dish_diet_tool,
    classify_dish_category_tool,
    normalize_dish_name_tool,
    extract_dish_from_query_tool,
    extract_location_from_query_tool,
    classify_intent_tool,
    is_relevant_query_tool,
    check_location_match_tool,
    validate_dishes_tool,
    extract_dish_and_restaurant_tool,
    is_nonveg_text_tool
)

# Allergy tools
from .allergy_tools import (
    filter_dishes_by_allergy_hybrid
)

# Menu scraping tools
from .menu_tools import (
    scrape_menu_url_tool
)

# Yelp tools (if exists)
try:
    from .yelp_tools import *
except ImportError:
    pass

# Budget tools (if exists)
try:
    from .budget_tools import *
except ImportError:
    pass

# Beer tools (if exists)
try:
    from .beer_tools import *
except ImportError:
    pass

__all__ = [
    # Taste tools
    "generate_taste_vector_tool",
    "generate_taste_vector_groq_tool",
    "generate_taste_vector_semantic_tool",
    "calculate_taste_similarity_tool",
    "calculate_favorites_boost_tool",
    # Recommendation tools
    "get_dish_recommendations_tool",
    "rank_restaurants_tool",
    "calculate_restaurant_taste_vector_tool",
    "filter_and_rank_recommendations_tool",
    # Dish processing tools
    "filter_dishes_by_diet_tool",
    "detect_diet_from_query_tool",
    "classify_dish_diet_tool",
    "classify_dish_category_tool",
    "normalize_dish_name_tool",
    "extract_dish_from_query_tool",
    "extract_location_from_query_tool",
    "classify_intent_tool",
    "is_relevant_query_tool",
    "check_location_match_tool",
    "validate_dishes_tool",
    "extract_dish_and_restaurant_tool",
    "is_nonveg_text_tool",
    # Allergy tools
    "filter_dishes_by_allergy_hybrid",
    # Menu scraping tools
    "scrape_menu_url_tool",
]

# Agent Tools - Using Swaad Functions

This directory contains agent tools that expose the exact same functions from `swaad/backend` as tools for the agent system.

## Architecture

All tools import functions from `gusto/backend/services/` which are exact copies of the functions from `swaad/backend/`:

- `services/taste_service.py` = `swaad/backend/taste_analysis.py`
- `services/recommendation_service.py` = `swaad/backend/recommendations.py`
- `services/restaurant_service.py` = `swaad/backend/dish_processing.py`

## Tool Files

### 1. `taste_tools.py`
Exposes taste analysis functions from `swaad/backend/taste_analysis.py`:

- `generate_taste_vector_tool` - Generate 6D taste vector using keyword matching (falls back to Groq)
- `generate_taste_vector_groq_tool` - Generate taste vector using Groq AI
- `generate_taste_vector_semantic_tool` - Generate taste vector using semantic search in Pinecone
- `calculate_taste_similarity_tool` - Calculate similarity between user and dish taste vectors
- `calculate_favorites_boost_tool` - Calculate boost score based on favorite dishes

**Functions used from swaad:**
- `infer_taste_from_text()`
- `infer_taste_from_groq()`
- `infer_taste_from_text_semantic()`
- `infer_taste_from_text_hybrid()`
- `taste_similarity()`
- `favorites_boost()`

### 2. `recommendation_tools.py`
Exposes recommendation functions from `swaad/backend/recommendations.py`:

- `get_dish_recommendations_tool` - Get recommended dishes from a restaurant's menu
- `rank_restaurants_tool` - Rank restaurants by taste similarity and favorites
- `calculate_restaurant_taste_vector_tool` - Calculate aggregate taste vector for a restaurant
- `filter_and_rank_recommendations_tool` - Complete filtering and ranking pipeline

**Functions used from swaad:**
- `dish_recommendations_for_restaurant()`
- `rank_restaurants()`
- `calculate_restaurant_taste_vector()`
- `filter_and_rank_recommendations()`

### 3. `dish_processing_tools.py`
Exposes dish processing functions from `swaad/backend/dish_processing.py`:

- `filter_dishes_by_diet_tool` - Filter dishes by dietary preferences (veg/non-veg)
- `detect_diet_from_query_tool` - Detect diet preference from query string
- `classify_dish_diet_tool` - Classify dish as veg/non-veg using Groq
- `classify_dish_category_tool` - Classify dish category (appetizer/mains/desserts)
- `normalize_dish_name_tool` - Normalize dish name for comparison
- `extract_dish_from_query_tool` - Extract dish name from user query
- `extract_location_from_query_tool` - Extract location from user query
- `classify_intent_tool` - Classify user intent (dish_search/restaurant_search/greeting)
- `is_relevant_query_tool` - Check if query is relevant to food/restaurants
- `check_location_match_tool` - Check if user location matches restaurant location
- `validate_dishes_tool` - Filter out non-dish items from menu text
- `extract_dish_and_restaurant_tool` - Extract both dish and restaurant from query
- `is_nonveg_text_tool` - Check if text contains non-vegetarian keywords

**Functions used from swaad:**
- `filter_dishes_by_diet()`
- `detect_diet_from_query()`
- `classify_dish_diet_with_groq()`
- `classify_dish_with_groq()`
- `normalize_dish_name()`
- `extract_dish_from_query()`
- `extract_location_from_query()`
- `classify_intent()`
- `is_relevant_query()`
- `check_location_match()`
- `validate_dishes_with_groq()`
- `extract_dish_and_restaurant()`
- `is_nonveg_text()`

### 4. `allergy_tools.py`
Exposes allergy filtering functions from `swaad/backend/dish_processing.py`:

- `filter_dishes_by_allergy_hybrid` - Hybrid allergy filtering (keyword + AI intersection)

**Functions used from swaad:**
- `allergy_filter()` - Keyword-based filtering
- `filter_dishes_by_allergy()` - AI-based filtering using Groq

## Usage Example

```python
from agents.tools.taste_tools import generate_taste_vector_tool
from agents.tools.recommendation_tools import get_dish_recommendations_tool
from agents.tools.dish_processing_tools import filter_dishes_by_diet_tool

# Use in agent
agent = Agent(
    tools=[
        generate_taste_vector_tool,
        get_dish_recommendations_tool,
        filter_dishes_by_diet_tool
    ]
)
```

## Import Path

All tools add the backend directory to the Python path and import from `services/`:

```python
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
from services.taste_service import ...
```

This ensures tools use the exact same functions as the original `swaad` product.

## Tool Return Format

All tools return JSON strings for easy parsing by agents:

```json
{
  "sweet": 0.5,
  "salty": 0.3,
  "sour": 0.1,
  "bitter": 0.0,
  "umami": 0.7,
  "spicy": 0.2
}
```

Error handling is included in all tools, returning error information in the JSON response if something goes wrong.

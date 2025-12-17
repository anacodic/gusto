"""
Beer pairing service - integrates beer recommender ML model.
"""
import os
import sys
from typing import Dict, List, Optional

# Add agents/tools to path to import beer_recommender
agents_path = os.path.join(os.path.dirname(__file__), "..", "..", "agents", "tools")
if agents_path not in sys.path:
    sys.path.insert(0, agents_path)

try:
    from beer_recommender import BeerRecommender
except ImportError:
    BeerRecommender = None

# Global beer recommender instance
_beer_recommender = None


def get_beer_recommender() -> Optional[BeerRecommender]:
    """Get or initialize beer recommender."""
    global _beer_recommender
    
    if _beer_recommender is None and BeerRecommender is not None:
        try:
            _beer_recommender = BeerRecommender()
            # Data path is now in data/ directory
            data_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..", "data", "beer_profile_and_ratings.csv"
            )
            if os.path.exists(data_path):
                _beer_recommender.load_and_preprocess_data()
                _beer_recommender.train_regression_model()
                print("✅ Beer recommender initialized")
            else:
                print(f"⚠️ Beer data file not found at {data_path}")
        except Exception as e:
            print(f"❌ Error initializing beer recommender: {e}")
    
    return _beer_recommender


def get_beer_recommendations(
    restaurant_taste_vector: List[float],
    restaurant_cuisine: str,
    menu_items: List[str],
    dish_name: Optional[str] = None
) -> Dict:
    """
    Get beer pairing recommendations for a restaurant.
    
    Args:
        restaurant_taste_vector: 6D taste vector [sweet, salty, sour, bitter, umami, spicy]
        restaurant_cuisine: Cuisine type (e.g., "Thai", "Italian")
        menu_items: List of menu item names
        dish_name: Optional specific dish name
        
    Returns:
        Dict with beer recommendations and match scores
    """
    recommender = get_beer_recommender()
    
    if recommender is None:
        return {
            "error": "Beer recommender not available",
            "recommendations": []
        }
    
    try:
        # Create user input from taste vector and cuisine
        taste_desc = f"cuisine: {restaurant_cuisine}, taste: sweet={restaurant_taste_vector[0]:.2f}, "
        taste_desc += f"spicy={restaurant_taste_vector[5]:.2f}, umami={restaurant_taste_vector[4]:.2f}"
        
        if dish_name:
            taste_desc = f"{dish_name} with {taste_desc}"
        
        result = recommender.get_recommendations(taste_desc)
        
        return {
            "recommendations": result.get("recommendations", []),
            "predicted_rating": result.get("predicted_rating", 0),
            "user_features": result.get("user_features", {})
        }
    except Exception as e:
        print(f"❌ Error getting beer recommendations: {e}")
        return {
            "error": str(e),
            "recommendations": []
        }

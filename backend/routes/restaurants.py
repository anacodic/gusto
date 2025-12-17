"""
Restaurant routes for discover feed and restaurant details
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from db import get_db, User
from middleware.auth import get_current_user_id
from integrations.embeddings import embed_text, combine_vectors
from integrations.pinecone_client import get_pinecone_index, query_pinecone
from services.taste_service import user_profile_to_taste_vector, infer_taste_from_text_hybrid, taste_similarity
from services.recommendation_service import filter_and_rank_recommendations
from config import USE_SEMANTIC_INGREDIENT_TASTE

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])


@router.get("/discover")
async def discover_restaurants(
    location: Optional[str] = Query(None, description="Location filter (e.g., 'Boston, MA')"),
    cuisine: Optional[str] = Query(None, description="Cuisine type filter"),
    max_results: int = Query(20, ge=1, le=50, description="Maximum number of results"),
    cognito_user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get discover feed of restaurants.
    Returns popular restaurants based on user preferences or general recommendations.
    """
    try:
        # Get user profile if authenticated
        user_taste_vec = [0.0] * 6
        allergies = []
        diet_type = "mix"
        favorite_dishes = []
        
        if cognito_user_id:
            result = await db.execute(
                select(User).where(User.cognito_user_id == cognito_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user_taste_vec = user.taste_vector or [0.0] * 6
                allergies = user.allergies or []
                diet_type = user.diet_type or "mix"
                favorite_dishes = user.favorite_dishes or []
        
        # Build query text for semantic search
        query_parts = ["popular restaurants", "best restaurants"]
        if cuisine:
            query_parts.append(cuisine)
        if location:
            query_parts.append(f"in {location}")
        
        query_text = " ".join(query_parts)
        
        # Get embedding for query
        query_embedding = embed_text(query_text)
        
        # Query Pinecone
        index = get_pinecone_index()
        matches = query_pinecone(
            query_vector=query_embedding,
            top_k=max_results * 2,  # Get more to filter
            include_metadata=True
        )
        
        if not matches:
            return {
                "restaurants": [],
                "message": "No restaurants found. Try adjusting your filters."
            }
        
        # Filter and rank recommendations
        ranked = filter_and_rank_recommendations(
            matches=matches,
            user_taste_vec=user_taste_vec,
            favorite_dishes=favorite_dishes,
            diet_type=diet_type,
            allergies=allergies,
            max_results=max_results,
            query_text=query_text,
            location_filter=location,
            cuisine_filter=cuisine
        )
        
        # Format response
        restaurants = []
        for r in ranked:
            restaurants.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "rating": r.get("avg_rating"),
                "price_range": r.get("price_range"),
                "cuisine_types": r.get("cuisine_types", []),
                "location": r.get("location", {}),
                "coordinates": r.get("coordinates"),
                "taste_vector": r.get("taste_vector", [0.0] * 6),
                "recommended_dishes": [
                    {
                        "name": d.get("name"),
                        "similarity": d.get("similarity", 0.0)
                    }
                    for d in r.get("recommended_dishes", [])[:3]
                ],
                "photos": r.get("photos", []),
                "menu_url": r.get("menu_url"),
                "score": r.get("score", 0.0)
            })
        
        return {
            "restaurants": restaurants,
            "count": len(restaurants)
        }
        
    except Exception as e:
        print(f"[ERROR] Discover endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")


@router.get("/{restaurant_id}")
async def get_restaurant(
    restaurant_id: str,
    cognito_user_id: Optional[str] = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific restaurant.
    """
    try:
        # Get user profile if authenticated
        user_taste_vec = [0.0] * 6
        allergies = []
        diet_type = "mix"
        favorite_dishes = []
        
        if cognito_user_id:
            result = await db.execute(
                select(User).where(User.cognito_user_id == cognito_user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user_taste_vec = user.taste_vector or [0.0] * 6
                allergies = user.allergies or []
                diet_type = user.diet_type or "mix"
                favorite_dishes = user.favorite_dishes or []
        
        # Query Pinecone for this specific restaurant
        index = get_pinecone_index()
        
        # Try to find restaurant by ID
        # First, try direct query with restaurant name/ID
        query_embedding = embed_text(restaurant_id)
        matches = query_pinecone(
            query_vector=query_embedding,
            top_k=10,
            include_metadata=True
        )
        
        # Find exact match by ID
        restaurant = None
        for match in matches:
            meta = match.get("metadata", {})
            match_id = match.get("id") or meta.get("id") or meta.get("restaurant_id")
            if match_id == restaurant_id or meta.get("name", "").lower() == restaurant_id.lower():
                restaurant = match
                break
        
        # If no exact match, use first result
        if not restaurant and matches:
            restaurant = matches[0]
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Extract restaurant data
        meta = restaurant.get("metadata", {})
        
        # Get recommended dishes
        menu_items = meta.get("menu_items", [])
        taste_vec = meta.get("taste_vector", [0.0] * 6)
        
        # Calculate taste match
        taste_match = taste_similarity(user_taste_vec, taste_vec) if user_taste_vec else 0.0
        
        # Get recommended dishes
        from services.recommendation_service import dish_recommendations_for_restaurant
        
        # Check if metadata has pre-calculated dish taste vectors
        dishes_with_taste = None
        dishes_json = meta.get("dishes_json")
        if dishes_json:
            try:
                import json
                dishes_with_taste = json.loads(dishes_json)
            except Exception:
                dishes_with_taste = None
        
        if dishes_with_taste:
            recommended_dishes = dish_recommendations_for_restaurant(
                dishes_with_taste, user_taste_vec, diet_type, allergies, top_n=10
            )
        else:
            recommended_dishes = dish_recommendations_for_restaurant(
                menu_items, user_taste_vec, diet_type, allergies, top_n=10
            )
        
        # Build response
        response = {
            "id": restaurant.get("id") or meta.get("id") or restaurant_id,
            "name": meta.get("name", "Unknown Restaurant"),
            "url": meta.get("url"),
            "avg_rating": meta.get("avg_rating"),
            "review_count": meta.get("review_count", 0),
            "price_range": meta.get("price_range"),
            "cuisine_types": meta.get("cuisine_types", []),
            "location": meta.get("location", {}),
            "coordinates": meta.get("coordinates"),
            "menu_items": menu_items,
            "popular_dishes": meta.get("popular_dishes", []),
            "taste_vector": taste_vec,
            "taste_match": round(taste_match * 100, 1),  # Percentage
            "recommended_dishes": [
                {
                    "name": d.get("name"),
                    "similarity": d.get("similarity", 0.0),
                    "taste": d.get("taste")
                }
                for d in recommended_dishes
            ],
            "photos": meta.get("photos", []),
            "menu_url": meta.get("menu_url"),
            "hours": meta.get("hours"),
            "phone": meta.get("phone"),
            "website": meta.get("website")
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Restaurant details endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching restaurant details: {str(e)}")

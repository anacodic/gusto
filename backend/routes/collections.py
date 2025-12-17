"""
Collections routes (Pinterest-style saving)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional
from db import get_db, User, Collection, CollectionRestaurant
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/api/collections", tags=["collections"])


class CreateCollectionRequest(BaseModel):
    name: str
    emoji: Optional[str] = "📌"


class AddRestaurantRequest(BaseModel):
    restaurant_id: str
    restaurant_name: str
    restaurant_data: dict


@router.post("")
async def create_collection(
    request: CreateCollectionRequest,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new collection"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    collection = Collection(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=request.name,
        emoji=request.emoji or "📌"
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    
    return {
        "id": collection.id,
        "name": collection.name,
        "emoji": collection.emoji,
        "user_id": collection.user_id,
        "created_at": collection.created_at.isoformat()
    }


@router.get("")
async def get_collections(
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all collections for current user"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    result = await db.execute(
        select(Collection).where(Collection.user_id == current_user.id)
    )
    collections = result.scalars().all()
    
    collections_list = []
    for collection in collections:
        # Get restaurant count
        count_result = await db.execute(
            select(func.count(CollectionRestaurant.id)).where(
                CollectionRestaurant.collection_id == collection.id
            )
        )
        restaurant_count = count_result.scalar() or 0
        
        collections_list.append({
            "id": collection.id,
            "name": collection.name,
            "emoji": collection.emoji,
            "restaurant_count": restaurant_count,
            "created_at": collection.created_at.isoformat()
        })
    
    return {"collections": collections_list}


@router.get("/{collection_id}")
async def get_collection(
    collection_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get collection with restaurants"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get collection
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(404, "Collection not found")
    
    if collection.user_id != current_user.id:
        raise HTTPException(403, "Not your collection")
    
    # Get restaurants
    result = await db.execute(
        select(CollectionRestaurant).where(
            CollectionRestaurant.collection_id == collection_id
        )
    )
    restaurants = result.scalars().all()
    
    return {
        "id": collection.id,
        "name": collection.name,
        "emoji": collection.emoji,
        "restaurants": [
            {
                "id": r.id,
                "restaurant_id": r.restaurant_id,
                "restaurant_name": r.restaurant_name,
                "restaurant_data": r.restaurant_data,
                "added_at": r.added_at.isoformat()
            }
            for r in restaurants
        ],
        "created_at": collection.created_at.isoformat()
    }


@router.post("/{collection_id}/restaurants")
async def add_restaurant(
    collection_id: str,
    request: AddRestaurantRequest,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add restaurant to collection"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get collection
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(404, "Collection not found")
    
    if collection.user_id != current_user.id:
        raise HTTPException(403, "Not your collection")
    
    # Check if already in collection
    result = await db.execute(
        select(CollectionRestaurant).where(
            and_(
                CollectionRestaurant.collection_id == collection_id,
                CollectionRestaurant.restaurant_id == request.restaurant_id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Restaurant already in collection")
    
    # Add restaurant
    collection_restaurant = CollectionRestaurant(
        id=str(uuid.uuid4()),
        collection_id=collection_id,
        restaurant_id=request.restaurant_id,
        restaurant_name=request.restaurant_name,
        restaurant_data=request.restaurant_data
    )
    db.add(collection_restaurant)
    await db.commit()
    
    return {"message": "Restaurant added to collection"}


@router.delete("/{collection_id}/restaurants/{restaurant_id}")
async def remove_restaurant(
    collection_id: str,
    restaurant_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Remove restaurant from collection"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get collection
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(404, "Collection not found")
    
    if collection.user_id != current_user.id:
        raise HTTPException(403, "Not your collection")
    
    # Get restaurant
    result = await db.execute(
        select(CollectionRestaurant).where(
            and_(
                CollectionRestaurant.collection_id == collection_id,
                CollectionRestaurant.restaurant_id == restaurant_id
            )
        )
    )
    collection_restaurant = result.scalar_one_or_none()
    if not collection_restaurant:
        raise HTTPException(404, "Restaurant not in collection")
    
    await db.delete(collection_restaurant)
    await db.commit()
    
    return {"message": "Restaurant removed from collection"}

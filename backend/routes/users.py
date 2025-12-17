"""
User profile routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from db import get_db, User
from middleware.auth import get_current_user_id, get_current_user_token
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    allergies: Optional[List[str]] = None
    diet_type: Optional[str] = None
    taste_vector: Optional[List[float]] = None
    favorite_dishes: Optional[List[dict]] = None


@router.post("/sync")
async def sync_user(
    cognito_user_id: str = Depends(get_current_user_id),
    claims: dict = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    """Create/update user from Cognito token - called after login"""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    user = result.scalar_one_or_none()
    
    email = claims.get("email", "")
    name = claims.get("name") or claims.get("cognito:username") or email.split("@")[0]
    
    if not user:
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            cognito_user_id=cognito_user_id,
            email=email,
            name=name,
            taste_vector=[0.0] * 6,
            allergies=[],
            favorite_dishes=[]
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update email/name if changed
        if email and user.email != email:
            user.email = email
        if name and user.name != name:
            user.name = name
        await db.commit()
        await db.refresh(user)
    
    return {
        "id": user.id,
        "cognito_user_id": user.cognito_user_id,
        "email": user.email,
        "name": user.name,
        "location": user.location,
        "allergies": user.allergies,
        "diet_type": user.diet_type,
        "taste_vector": user.taste_vector,
        "favorite_dishes": user.favorite_dishes
    }


@router.get("/profile")
async def get_profile(
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "location": user.location,
        "allergies": user.allergies,
        "diet_type": user.diet_type,
        "taste_vector": user.taste_vector,
        "favorite_dishes": user.favorite_dishes
    }


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    if request.name is not None:
        user.name = request.name
    if request.location is not None:
        user.location = request.location
    if request.allergies is not None:
        user.allergies = request.allergies
    if request.diet_type is not None:
        user.diet_type = request.diet_type
    if request.taste_vector is not None:
        user.taste_vector = request.taste_vector
    if request.favorite_dishes is not None:
        user.favorite_dishes = request.favorite_dishes
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "location": user.location,
        "allergies": user.allergies,
        "diet_type": user.diet_type,
        "taste_vector": user.taste_vector,
        "favorite_dishes": user.favorite_dishes
    }


@router.get("/search")
async def search_users(
    q: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Search users by name or email"""
    result = await db.execute(
        select(User).where(
            (User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))
        ).limit(20)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "location": user.location,
            "taste_vector": user.taste_vector,
            "allergies": user.allergies
        }
        for user in users if user.cognito_user_id != cognito_user_id
    ]

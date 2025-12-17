"""
Groups and group recommendations routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional
from db import get_db, User, Group, GroupMember
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/api/groups", tags=["groups"])


class CreateGroupRequest(BaseModel):
    name: str
    budget: Optional[float] = None
    location: Optional[str] = None
    member_ids: Optional[List[str]] = None


class AddMemberRequest(BaseModel):
    user_id: str


@router.post("")
async def create_group(
    request: CreateGroupRequest,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new group"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Create group
    group = Group(
        id=str(uuid.uuid4()),
        name=request.name,
        created_by=current_user.id,
        budget=request.budget,
        location=request.location
    )
    db.add(group)
    await db.flush()
    
    # Add creator as member
    creator_member = GroupMember(
        id=str(uuid.uuid4()),
        group_id=group.id,
        user_id=current_user.id
    )
    db.add(creator_member)
    
    # Add other members if provided
    if request.member_ids:
        for member_id in request.member_ids:
            if member_id != current_user.id:
                member = GroupMember(
                    id=str(uuid.uuid4()),
                    group_id=group.id,
                    user_id=member_id
                )
                db.add(member)
    
    await db.commit()
    await db.refresh(group)
    
    return {
        "id": group.id,
        "name": group.name,
        "created_by": group.created_by,
        "budget": group.budget,
        "location": group.location,
        "created_at": group.created_at.isoformat()
    }


@router.get("")
async def get_groups(
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all groups for current user"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get groups where user is a member
    result = await db.execute(
        select(Group, GroupMember).join(
            GroupMember, Group.id == GroupMember.group_id
        ).where(GroupMember.user_id == current_user.id)
    )
    groups_data = result.all()
    
    groups = []
    for group, member in groups_data:
        # Get member count
        member_count_result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group.id)
        )
        member_count = len(member_count_result.scalars().all())
        
        groups.append({
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by,
            "budget": group.budget,
            "location": group.location,
            "member_count": member_count,
            "created_at": group.created_at.isoformat()
        })
    
    return {"groups": groups}


@router.get("/{group_id}")
async def get_group(
    group_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get group details with members"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get group
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(404, "Group not found")
    
    # Check if user is member
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, "Not a member of this group")
    
    # Get all members
    result = await db.execute(
        select(GroupMember, User).join(
            User, GroupMember.user_id == User.id
        ).where(GroupMember.group_id == group_id)
    )
    members_data = result.all()
    
    members = []
    for member, user in members_data:
        members.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "taste_vector": user.taste_vector,
            "allergies": user.allergies,
            "diet_type": user.diet_type
        })
    
    return {
        "id": group.id,
        "name": group.name,
        "created_by": group.created_by,
        "budget": group.budget,
        "location": group.location,
        "members": members,
        "created_at": group.created_at.isoformat()
    }


@router.post("/{group_id}/members")
async def add_member(
    group_id: str,
    request: AddMemberRequest,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add member to group"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get group
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(404, "Group not found")
    
    # Check if current user is member
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, "Not a member of this group")
    
    # Check if target user exists
    result = await db.execute(
        select(User).where(User.id == request.user_id)
    )
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(404, "Target user not found")
    
    # Check if already a member
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == request.user_id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "User already in group")
    
    # Add member
    member = GroupMember(
        id=str(uuid.uuid4()),
        group_id=group_id,
        user_id=request.user_id
    )
    db.add(member)
    await db.commit()
    
    return {"message": "Member added"}


@router.get("/{group_id}/recommendations")
async def get_group_recommendations(
    group_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get group recommendations with combined taste vectors and allergies.
    
    Returns group metadata including combined taste vector, allergies, and members.
    Use the /api/chat endpoint with group context for actual restaurant recommendations.
    """
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get group and members
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(404, "Group not found")
    
    # Get all members
    result = await db.execute(
        select(GroupMember, User).join(
            User, GroupMember.user_id == User.id
        ).where(GroupMember.group_id == group_id)
    )
    members_data = result.all()
    
    members = []
    combined_allergies = set()
    taste_vectors = []
    
    for member, user in members_data:
        members.append({
            "id": user.id,
            "name": user.name,
            "taste_vector": user.taste_vector,
            "allergies": user.allergies
        })
        if user.allergies:
            combined_allergies.update(user.allergies)
        if user.taste_vector:
            taste_vectors.append(user.taste_vector)
    
    # Calculate combined taste vector (average)
    combined_taste = [0.0] * 6
    if taste_vectors:
        for i in range(6):
            combined_taste[i] = sum(vec[i] if i < len(vec) else 0.0 for vec in taste_vectors) / len(taste_vectors)
    
    return {
        "group_id": group_id,
        "group_name": group.name,
        "combined_taste": combined_taste,
        "combined_allergies": list(combined_allergies),
        "budget": group.budget,
        "location": group.location,
        "members": members,
        "message": "Use /api/chat endpoint with group context for recommendations"
    }

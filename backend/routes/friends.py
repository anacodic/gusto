"""
Friends and friend requests routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from pydantic import BaseModel
from db import get_db, User, FriendRequest, Friendship
from middleware.auth import get_current_user_id
import uuid

router = APIRouter(prefix="/api/friends", tags=["friends"])


class FriendRequestCreate(BaseModel):
    to_user_id: str


@router.post("/request")
async def send_friend_request(
    request: FriendRequestCreate,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Send friend request"""
    # Get current user
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get target user
    result = await db.execute(
        select(User).where(User.id == request.to_user_id)
    )
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(404, "Target user not found")
    
    if current_user.id == target_user.id:
        raise HTTPException(400, "Cannot send friend request to yourself")
    
    # Check if already friends
    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.user1_id == current_user.id, Friendship.user2_id == target_user.id),
                and_(Friendship.user1_id == target_user.id, Friendship.user2_id == current_user.id)
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Already friends")
    
    # Check if request already exists
    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.from_user_id == current_user.id,
                FriendRequest.to_user_id == target_user.id,
                FriendRequest.status == "pending"
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Friend request already sent")
    
    # Create request
    friend_request = FriendRequest(
        id=str(uuid.uuid4()),
        from_user_id=current_user.id,
        to_user_id=target_user.id,
        status="pending"
    )
    db.add(friend_request)
    await db.commit()
    
    return {"message": "Friend request sent", "request_id": friend_request.id}


@router.get("/requests")
async def get_friend_requests(
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get pending friend requests (sent and received)"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get received requests
    result = await db.execute(
        select(FriendRequest, User).join(
            User, FriendRequest.from_user_id == User.id
        ).where(
            and_(
                FriendRequest.to_user_id == current_user.id,
                FriendRequest.status == "pending"
            )
        )
    )
    received = result.all()
    
    # Get sent requests
    result = await db.execute(
        select(FriendRequest, User).join(
            User, FriendRequest.to_user_id == User.id
        ).where(
            and_(
                FriendRequest.from_user_id == current_user.id,
                FriendRequest.status == "pending"
            )
        )
    )
    sent = result.all()
    
    return {
        "received": [
            {
                "id": req.id,
                "from_user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "taste_vector": user.taste_vector,
                    "allergies": user.allergies
                },
                "created_at": req.created_at.isoformat()
            }
            for req, user in received
        ],
        "sent": [
            {
                "id": req.id,
                "to_user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                },
                "created_at": req.created_at.isoformat()
            }
            for req, user in sent
        ]
    }


@router.post("/accept/{request_id}")
async def accept_friend_request(
    request_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Accept friend request"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.id == request_id,
                FriendRequest.to_user_id == current_user.id,
                FriendRequest.status == "pending"
            )
        )
    )
    friend_request = result.scalar_one_or_none()
    
    if not friend_request:
        raise HTTPException(404, "Friend request not found")
    
    # Create friendship
    friendship = Friendship(
        id=str(uuid.uuid4()),
        user1_id=friend_request.from_user_id,
        user2_id=friend_request.to_user_id
    )
    db.add(friendship)
    
    # Update request status
    friend_request.status = "accepted"
    await db.commit()
    
    return {"message": "Friend request accepted"}


@router.post("/decline/{request_id}")
async def decline_friend_request(
    request_id: str,
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Decline friend request"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.id == request_id,
                FriendRequest.to_user_id == current_user.id,
                FriendRequest.status == "pending"
            )
        )
    )
    friend_request = result.scalar_one_or_none()
    
    if not friend_request:
        raise HTTPException(404, "Friend request not found")
    
    friend_request.status = "declined"
    await db.commit()
    
    return {"message": "Friend request declined"}


@router.get("")
async def get_friends(
    cognito_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all friends"""
    result = await db.execute(
        select(User).where(User.cognito_user_id == cognito_user_id)
    )
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(404, "User not found")
    
    # Get all friendships
    result = await db.execute(
        select(Friendship, User).join(
            User,
            or_(
                and_(Friendship.user1_id == current_user.id, Friendship.user2_id == User.id),
                and_(Friendship.user2_id == current_user.id, Friendship.user1_id == User.id)
            )
        ).where(
            or_(
                Friendship.user1_id == current_user.id,
                Friendship.user2_id == current_user.id
            )
        )
    )
    friendships = result.all()
    
    friends = []
    for friendship, user in friendships:
        if user.id != current_user.id:
            friends.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "location": user.location,
                "taste_vector": user.taste_vector,
                "allergies": user.allergies,
                "diet_type": user.diet_type
            })
    
    return {"friends": friends}

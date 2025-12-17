"""
Database setup with async SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from datetime import datetime
from typing import List
import os

# Database URL - SQLite for development, can switch to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./swaad.db")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    cognito_user_id = Column(String, unique=True, index=True)  # Links to Cognito
    email = Column(String, index=True)
    name = Column(String)
    location = Column(String, default="")
    allergies = Column(JSON, default=list)  # List of strings
    diet_type = Column(String, default="mix")
    taste_vector = Column(JSON, default=list)  # [sweet, salty, sour, bitter, umami, spicy]
    favorite_dishes = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FriendRequest(Base):
    __tablename__ = "friend_requests"
    
    id = Column(String, primary_key=True)
    from_user_id = Column(String, ForeignKey("users.id"))
    to_user_id = Column(String, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending, accepted, declined
    created_at = Column(DateTime, default=datetime.utcnow)


class Friendship(Base):
    __tablename__ = "friendships"
    
    id = Column(String, primary_key=True)
    user1_id = Column(String, ForeignKey("users.id"))
    user2_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    budget = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(String, primary_key=True)
    group_id = Column(String, ForeignKey("groups.id"))
    user_id = Column(String, ForeignKey("users.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)


class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    emoji = Column(String, default="📌")
    created_at = Column(DateTime, default=datetime.utcnow)


class CollectionRestaurant(Base):
    __tablename__ = "collection_restaurants"
    
    id = Column(String, primary_key=True)
    collection_id = Column(String, ForeignKey("collections.id"))
    restaurant_id = Column(String)  # Yelp restaurant ID
    restaurant_name = Column(String)
    restaurant_data = Column(JSON)  # Full restaurant data
    added_at = Column(DateTime, default=datetime.utcnow)


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

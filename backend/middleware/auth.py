"""
FastAPI authentication middleware for Cognito JWT tokens
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from cognito_auth import verify_cognito_token, get_cognito_user_id


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    FastAPI dependency to extract and verify Cognito user ID from JWT token.
    
    Usage:
        @router.get("/api/endpoint")
        async def my_endpoint(user_id: str = Depends(get_current_user_id)):
            # user_id is the cognito_user_id from the token
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = get_cognito_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_user_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency to get full token claims.
    
    Usage:
        @router.get("/api/endpoint")
        async def my_endpoint(claims: dict = Depends(get_current_user_token)):
            email = claims.get("email")
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    claims = verify_cognito_token(authorization)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return claims

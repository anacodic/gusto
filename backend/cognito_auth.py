"""
AWS Cognito JWT Token Verification
"""
import os
import requests
from typing import Optional, Dict
from jose import jwt, JWTError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import base64
from datetime import datetime, timedelta

COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "us-east-1_jUJj5G3YE")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Extract region from pool ID if needed
if "_" in COGNITO_USER_POOL_ID:
    AWS_REGION = COGNITO_USER_POOL_ID.split("_")[0]

COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

# Cache for JWKS
_jwks_cache = None
_jwks_cache_time = None
JWKS_CACHE_TTL = timedelta(hours=1)


def get_jwks() -> Dict:
    """Get Cognito public keys (JWKS) with caching"""
    global _jwks_cache, _jwks_cache_time
    
    now = datetime.utcnow()
    if _jwks_cache is None or _jwks_cache_time is None or (now - _jwks_cache_time) > JWKS_CACHE_TTL:
        try:
            response = requests.get(JWKS_URL, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = now
        except Exception as e:
            print(f"Error fetching JWKS: {e}")
            if _jwks_cache is None:
                raise
    return _jwks_cache


def jwks_to_rsa_public_key(jwk: Dict) -> bytes:
    """Convert JWK to RSA public key"""
    n = base64.urlsafe_b64decode(jwk['n'] + '==')
    e = base64.urlsafe_b64decode(jwk['e'] + '==')
    
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    public_numbers = rsa.RSAPublicNumbers(
        int.from_bytes(e, 'big'),
        int.from_bytes(n, 'big')
    )
    public_key = public_numbers.public_key(default_backend())
    
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def verify_cognito_token(token: str) -> Optional[Dict]:
    """Verify Cognito JWT and return claims"""
    try:
        # Remove Bearer prefix
        token = token.replace("Bearer ", "").strip()
        
        # Get unverified header to find key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            return None
        
        # Get JWKS and find the key
        jwks = get_jwks()
        key_data = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                key_data = key
                break
        
        if not key_data:
            return None
        
        # Convert JWK to PEM format
        public_key_pem = jwks_to_rsa_public_key(key_data)
        
        # Verify and decode token
        claims = jwt.decode(
            token,
            public_key_pem,
            algorithms=["RS256"],
            audience=None,  # Cognito doesn't always set audience
            issuer=COGNITO_ISSUER,
            options={"verify_aud": False}  # Skip audience verification
        )
        
        return claims
    except JWTError as e:
        print(f"JWT verification error: {e}")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None


def get_cognito_user_id(token: str) -> Optional[str]:
    """Extract cognito_user_id (sub) from token"""
    claims = verify_cognito_token(token)
    return claims.get("sub") if claims else None


def get_cognito_email(token: str) -> Optional[str]:
    """Extract email from token"""
    claims = verify_cognito_token(token)
    return claims.get("email") if claims else None

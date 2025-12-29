from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jose import jwt, JWTError
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def validate_jwt_token(token: str) -> dict:
    """
    Validate JWT token and extract claims.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token claims
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Determine algorithm and key based on configuration
        if settings.algorithm.startswith("RS"):
            # RSA signature - use public key
            if not settings.jwt_public_key:
                logger.error("JWT_PUBLIC_KEY not configured for RS256 algorithm")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWT validation not properly configured",
                )
            key = settings.jwt_public_key
        else:
            # HMAC signature - use secret key
            key = settings.secret_key
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.algorithm],
            issuer=settings.jwt_issuer if settings.jwt_issuer else None,
            audience=settings.jwt_audience if settings.jwt_audience else None,
        )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    Extract and validate user from JWT token.
    
    In development mode (enable_auth_bypass=True), allows unauthenticated requests.
    In production, validates JWT tokens against the BiteSoft provider portal.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        str: User ID extracted from token
        
    Raises:
        HTTPException: If authentication fails in production mode
    """
    # Development mode bypass
    if settings.enable_auth_bypass and credentials is None:
        logger.debug("Auth bypass enabled - allowing unauthenticated request")
        return "dev_user_001"
    
    # Production mode - require authentication
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate JWT and extract user_id
    payload = validate_jwt_token(token)
    
    # Extract user_id from token claims
    # Common claim names: sub, user_id, uid, userId
    user_id = (
        payload.get("sub") or 
        payload.get("user_id") or 
        payload.get("uid") or 
        payload.get("userId")
    )
    
    if not user_id:
        logger.error(f"No user_id found in JWT claims: {payload.keys()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return str(user_id)

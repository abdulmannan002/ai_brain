"""
Security and authentication utilities
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

from .config import settings

# Security scheme
security = HTTPBearer()


class AuthManager:
    """Authentication manager"""
    
    def __init__(self):
        self.secret_key = "your-secret-key"  # In production, use secure secret
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current authenticated user"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        token = credentials.credentials
        
        # For development, use simple token validation
        # In production, validate with Auth0
        if settings.auth0.domain:
            return await self._validate_auth0_token(token)
        else:
            return self._validate_simple_token(token)
    
    async def _validate_auth0_token(self, token: str) -> Dict[str, Any]:
        """Validate Auth0 JWT token"""
        # In production, implement proper Auth0 validation
        # This is a placeholder implementation
        try:
            # Verify token with Auth0
            # payload = jwt.decode(token, auth0_public_key, algorithms=["RS256"])
            # return {"user_id": payload["sub"], "email": payload.get("email")}
            return {"user_id": "auth0_user_123", "email": "user@example.com"}
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Auth0 token"
            )
    
    def _validate_simple_token(self, token: str) -> Dict[str, Any]:
        """Validate simple token for development"""
        if token == "invalid" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # For development, return mock user
        return {"user_id": "dev_user_123", "email": "dev@example.com"}


# Global auth manager instance
auth_manager = AuthManager()


# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    return await auth_manager.get_current_user(credentials) 
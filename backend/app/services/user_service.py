"""
User service - Business logic for user management
"""
from typing import Optional, Dict, Any
from datetime import datetime
import asyncpg

from ..models.user import UserCreate, UserUpdate, UserResponse
from ..core.database import get_db_connection


class UserService:
    """Service for user management operations"""
    
    def __init__(self):
        pass
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        async with get_db_connection() as conn:
            user_id = await conn.fetchval(
                """
                INSERT INTO users (auth0_id, email, subscription, created_at) 
                VALUES ($1, $2, $3, $4) 
                RETURNING id
                """,
                user_data.auth0_id,
                user_data.email,
                user_data.subscription,
                datetime.utcnow()
            )
            
            return UserResponse(
                id=user_id,
                email=user_data.email,
                subscription=user_data.subscription
            )
    
    async def get_user_by_auth0_id(self, auth0_id: str) -> Optional[UserResponse]:
        """Get user by Auth0 ID"""
        async with get_db_connection() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE auth0_id = $1",
                auth0_id
            )
            
            if not user:
                return None
            
            return UserResponse(
                id=user["id"],
                email=user["email"],
                subscription=user["subscription"]
            )
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        async with get_db_connection() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            
            if not user:
                return None
            
            return UserResponse(
                id=user["id"],
                email=user["email"],
                subscription=user["subscription"]
            )
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user"""
        async with get_db_connection() as conn:
            # Check if user exists
            existing_user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            
            if not existing_user:
                return None
            
            # Build update query
            update_fields = []
            query_params = []
            param_count = 0
            
            if user_data.email is not None:
                param_count += 1
                update_fields.append(f"email = ${param_count}")
                query_params.append(user_data.email)
            
            if user_data.subscription is not None:
                param_count += 1
                update_fields.append(f"subscription = ${param_count}")
                query_params.append(user_data.subscription)
            
            if not update_fields:
                return await self.get_user_by_id(user_id)
            
            query_params.append(user_id)
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count + 1}
            """
            
            await conn.execute(query, *query_params)
            
            return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        async with get_db_connection() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1",
                user_id
            )
            
            return result == "DELETE 1"
    
    async def get_or_create_user(self, auth0_id: str, email: str) -> UserResponse:
        """Get existing user or create new one"""
        user = await self.get_user_by_auth0_id(auth0_id)
        
        if user:
            return user
        
        # Create new user
        user_data = UserCreate(
            auth0_id=auth0_id,
            email=email,
            subscription="free"
        )
        
        return await self.create_user(user_data)


# Global user service instance
user_service = UserService() 
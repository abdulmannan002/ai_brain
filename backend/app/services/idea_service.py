"""
Idea service - Business logic for idea management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
from fastapi import HTTPException, status

from ..models.idea import IdeaCreate, IdeaUpdate, IdeaResponse, IdeaSearchParams
from ..core.database import db_manager


class IdeaService:
    """Service for idea management operations"""
    
    def __init__(self):
        pass
    
    async def create_idea(self, idea_data: IdeaCreate, user_id: str) -> IdeaResponse:
        """Create a new idea"""
        conn = await db_manager.get_connection()
        try:
            idea_id = await conn.fetchval(
                """
                INSERT INTO ideas (content, source, timestamp, user_id) 
                VALUES ($1, $2, $3, $4) 
                RETURNING id
                """,
                idea_data.content,
                idea_data.source,
                datetime.utcnow(),
                user_id
            )
            
            return IdeaResponse(
                id=idea_id,
                content=idea_data.content,
                source=idea_data.source,
                timestamp=datetime.utcnow(),
                project=None,
                theme=None,
                emotion=None,
                transformed_output=None
            )
        finally:
            await db_manager.pool.release(conn)
    
    async def get_user_ideas(
        self, 
        user_id: str, 
        params: IdeaSearchParams
    ) -> List[IdeaResponse]:
        """Get user's ideas with filtering and pagination"""
        conn = await db_manager.get_connection()
        try:
            # Build query with filters
            query = "SELECT * FROM ideas WHERE user_id = $1"
            query_params = [user_id]
            param_count = 1
            
            if params.project:
                param_count += 1
                query += f" AND project = ${param_count}"
                query_params.append(params.project)
            
            if params.theme:
                param_count += 1
                query += f" AND theme = ${param_count}"
                query_params.append(params.theme)
            
            if params.emotion:
                param_count += 1
                query += f" AND emotion = ${param_count}"
                query_params.append(params.emotion)
            
            query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            query_params.extend([params.limit, params.skip])
            
            ideas = await conn.fetch(query, *query_params)
            
            return [
                IdeaResponse(
                    id=idea["id"],
                    content=idea["content"],
                    source=idea["source"],
                    timestamp=idea["timestamp"],
                    project=idea["project"],
                    theme=idea["theme"],
                    emotion=idea["emotion"],
                    transformed_output=idea["transformed_output"]
                )
                for idea in ideas
            ]
        finally:
            await db_manager.pool.release(conn)
    
    async def search_ideas(self, user_id: str, query: str) -> List[IdeaResponse]:
        """Search ideas using full-text search"""
        conn = await db_manager.get_connection()
        try:
            ideas = await conn.fetch(
                """
                SELECT * FROM ideas 
                WHERE user_id = $1 
                AND to_tsvector('english', content) @@ plainto_tsquery('english', $2) 
                ORDER BY timestamp DESC
                """,
                user_id, query
            )
            
            return [
                IdeaResponse(
                    id=idea["id"],
                    content=idea["content"],
                    source=idea["source"],
                    timestamp=idea["timestamp"],
                    project=idea["project"],
                    theme=idea["theme"],
                    emotion=idea["emotion"],
                    transformed_output=idea["transformed_output"]
                )
                for idea in ideas
            ]
        finally:
            await db_manager.pool.release(conn)
    
    async def get_idea_by_id(self, idea_id: int, user_id: str) -> Optional[IdeaResponse]:
        """Get idea by ID for specific user"""
        conn = await db_manager.get_connection()
        try:
            idea = await conn.fetchrow(
                "SELECT * FROM ideas WHERE id = $1 AND user_id = $2",
                idea_id, user_id
            )
            
            if not idea:
                return None
            
            return IdeaResponse(
                id=idea["id"],
                content=idea["content"],
                source=idea["source"],
                timestamp=idea["timestamp"],
                project=idea["project"],
                theme=idea["theme"],
                emotion=idea["emotion"],
                transformed_output=idea["transformed_output"]
            )
        finally:
            await db_manager.pool.release(conn)
    
    async def update_idea(
        self, 
        idea_id: int, 
        user_id: str, 
        idea_data: IdeaUpdate
    ) -> Optional[IdeaResponse]:
        """Update an idea"""
        conn = await db_manager.get_connection()
        try:
            # Check if idea exists and belongs to user
            existing_idea = await conn.fetchrow(
                "SELECT * FROM ideas WHERE id = $1 AND user_id = $2",
                idea_id, user_id
            )
            
            if not existing_idea:
                return None
            
            # Build update query
            update_fields = []
            query_params = []
            param_count = 0
            
            if idea_data.content is not None:
                param_count += 1
                update_fields.append(f"content = ${param_count}")
                query_params.append(idea_data.content)
            
            if idea_data.project is not None:
                param_count += 1
                update_fields.append(f"project = ${param_count}")
                query_params.append(idea_data.project)
            
            if idea_data.theme is not None:
                param_count += 1
                update_fields.append(f"theme = ${param_count}")
                query_params.append(idea_data.theme)
            
            if idea_data.emotion is not None:
                param_count += 1
                update_fields.append(f"emotion = ${param_count}")
                query_params.append(idea_data.emotion)
            
            if idea_data.transformed_output is not None:
                param_count += 1
                update_fields.append(f"transformed_output = ${param_count}")
                query_params.append(idea_data.transformed_output)
            
            if not update_fields:
                return await self.get_idea_by_id(idea_id, user_id)
            
            query_params.extend([idea_id, user_id])
            query = f"""
                UPDATE ideas 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count + 1} AND user_id = ${param_count + 2}
            """
            
            await conn.execute(query, *query_params)
            
            return await self.get_idea_by_id(idea_id, user_id)
        finally:
            await db_manager.pool.release(conn)
    
    async def delete_idea(self, idea_id: int, user_id: str) -> bool:
        """Delete an idea"""
        conn = await db_manager.get_connection()
        try:
            result = await conn.execute(
                "DELETE FROM ideas WHERE id = $1 AND user_id = $2",
                idea_id, user_id
            )
            
            return result == "DELETE 1"
        finally:
            await db_manager.pool.release(conn)
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's idea statistics"""
        conn = await db_manager.get_connection()
        try:
            # Total ideas
            total_ideas = await conn.fetchval(
                "SELECT COUNT(*) FROM ideas WHERE user_id = $1",
                user_id
            )
            
            # Ideas this month
            from datetime import datetime, timedelta
            first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            ideas_this_month = await conn.fetchval(
                "SELECT COUNT(*) FROM ideas WHERE user_id = $1 AND timestamp >= $2",
                user_id, first_day_of_month
            )
            
            # Unique projects
            projects_count = await conn.fetchval(
                "SELECT COUNT(DISTINCT project) FROM ideas WHERE user_id = $1 AND project IS NOT NULL",
                user_id
            )
            
            # Unique themes
            themes_count = await conn.fetchval(
                "SELECT COUNT(DISTINCT theme) FROM ideas WHERE user_id = $1 AND theme IS NOT NULL",
                user_id
            )
            
            # Unique emotions
            emotions_count = await conn.fetchval(
                "SELECT COUNT(DISTINCT emotion) FROM ideas WHERE user_id = $1 AND emotion IS NOT NULL",
                user_id
            )
            
            return {
                "total_ideas": total_ideas or 0,
                "ideas_this_month": ideas_this_month or 0,
                "projects_count": projects_count or 0,
                "themes_count": themes_count or 0,
                "emotions_count": emotions_count or 0
            }
        finally:
            await db_manager.pool.release(conn)


# Global idea service instance
idea_service = IdeaService() 
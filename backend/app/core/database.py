"""
Database connection and session management
"""
import asyncpg
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from .config import settings


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self._pool: asyncpg.Pool | None = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        if not self._pool:
            self._pool = await asyncpg.create_pool(
                settings.database.dsn,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'ai_brain_vault'
                }
            )
    
    async def close(self):
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @property
    def pool(self) -> asyncpg.Pool:
        """Get database connection pool"""
        if not self._pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._pool
    
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return await self._pool.acquire()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency to get database connection"""
    conn = await db_manager.get_connection()
    try:
        yield conn
    finally:
        await db_manager.pool.release(conn) 
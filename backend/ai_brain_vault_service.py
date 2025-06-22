from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
from datetime import datetime
import aiohttp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ai_brain_vault")

DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class IdeaInput(BaseModel):
    content: str
    source: str = "manual"

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DB_DSN)

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.post("/ideas/")
async def capture_idea(idea: IdeaInput):
    async with app.state.pool.acquire() as conn:
        idea_id = await conn.fetchval(
            "INSERT INTO ideas (content, source, timestamp) VALUES ($1, $2, $3) RETURNING id",
            idea.content,
            idea.source,
            datetime.utcnow()
        )
        return {"id": idea_id, "content": idea.content} 
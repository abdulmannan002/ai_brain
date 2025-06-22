from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncpg
import os
from datetime import datetime
import aiohttp
import json
import boto3
import whisper
import spacy
from kafka import KafkaProducer, KafkaConsumer
import threading
import time
from typing import Optional, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import httpx
import uuid

app = FastAPI(title="AI Brain Vault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "ai_brain_vault")

# AWS Configuration
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "ai-brain-vault-audio")

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# xAI API Configuration
XAI_API_KEY = os.environ.get("XAI_API_KEY")
XAI_API_URL = "https://api.x.ai/v1/llama3"

# Auth0 Configuration
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")

DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize services
security = HTTPBearer()
nlp = spacy.load("en_core_web_sm")
whisper_model = whisper.load_model("base")
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
kafka_producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Pydantic Models
class IdeaInput(BaseModel):
    content: str
    source: str = "manual"
    user_id: Optional[str] = None

class IdeaResponse(BaseModel):
    id: int
    content: str
    source: str
    timestamp: datetime
    project: Optional[str] = None
    theme: Optional[str] = None
    emotion: Optional[str] = None
    transformed_output: Optional[str] = None

class TransformRequest(BaseModel):
    idea_id: int
    output_type: str  # "content", "ip", "tasks"
    user_id: str

class UserCreate(BaseModel):
    auth0_id: str
    email: str
    subscription: str = "free"

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    token = credentials.credentials
    # In production, validate JWT token with Auth0
    # For now, we'll use a simple token validation
    if not token or token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": "user_123", "email": "user@example.com"}  # Placeholder

@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(DB_DSN)
    # Start Kafka consumer for NLP processing
    start_kafka_consumer()

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()
    kafka_producer.close()

# Kafka Consumer for NLP Processing
def start_kafka_consumer():
    def consume_messages():
        consumer = KafkaConsumer(
            'idea-sorting',
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        for message in consumer:
            process_idea_with_nlp(message.value)
    
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()

async def process_idea_with_nlp(idea_data):
    """Process idea with NLP for sorting and categorization"""
    try:
        content = idea_data['content']
        
        # Theme extraction using spaCy
        doc = nlp(content)
        themes = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON']]
        theme = themes[0] if themes else "general"
        
        # Emotion classification using xAI API
        emotion = await classify_emotion(content)
        
        # Project clustering (simplified)
        project = await cluster_project(content)
        
        # Update database
        async with app.state.pool.acquire() as conn:
            await conn.execute(
                "UPDATE ideas SET project = $1, theme = $2, emotion = $3 WHERE id = $4",
                project, theme, emotion, idea_data['id']
            )
            
    except Exception as e:
        print(f"Error processing idea with NLP: {e}")

async def classify_emotion(text: str) -> str:
    """Classify emotion using xAI API"""
    if not XAI_API_KEY:
        return "neutral"  # Fallback
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                XAI_API_URL,
                headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                json={
                    "task": "emotion_classification",
                    "text": text,
                    "max_tokens": 10
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('emotion', 'neutral')
            else:
                return "neutral"
    except Exception as e:
        print(f"Error classifying emotion: {e}")
        return "neutral"

async def cluster_project(text: str) -> str:
    """Simple project clustering"""
    # In a real implementation, this would use more sophisticated clustering
    projects = ["Startup Ideas", "Blog Content", "Product Features", "Research Notes"]
    # Simple keyword-based clustering
    if any(word in text.lower() for word in ['startup', 'business', 'company']):
        return "Startup Ideas"
    elif any(word in text.lower() for word in ['blog', 'article', 'write']):
        return "Blog Content"
    elif any(word in text.lower() for word in ['feature', 'product', 'app']):
        return "Product Features"
    else:
        return "Research Notes"

# Capture Service Endpoints
@app.post("/ideas/", response_model=IdeaResponse)
async def capture_idea(idea: IdeaInput, current_user: dict = Depends(get_current_user)):
    """Capture a new idea"""
    async with app.state.pool.acquire() as conn:
        idea_id = await conn.fetchval(
            "INSERT INTO ideas (content, source, timestamp, user_id) VALUES ($1, $2, $3, $4) RETURNING id",
            idea.content,
            idea.source,
            datetime.utcnow(),
            current_user["user_id"]
        )
        
        # Send to Kafka for NLP processing
        kafka_producer.send('idea-sorting', {
            'id': idea_id,
            'content': idea.content,
            'user_id': current_user["user_id"]
        })
        
        return {
            "id": idea_id,
            "content": idea.content,
            "source": idea.source,
            "timestamp": datetime.utcnow(),
            "project": None,
            "theme": None,
            "emotion": None,
            "transformed_output": None
        }

@app.post("/ideas/voice/")
async def capture_voice_idea(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Capture idea from voice input"""
    if not file.filename.endswith(('.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # Save audio file temporarily
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Transcribe using Whisper
        result = whisper_model.transcribe(temp_path)
        transcribed_text = result["text"]
        
        # Save to S3
        s3_key = f"audio/{current_user['user_id']}/{uuid.uuid4()}_{file.filename}"
        s3_client.upload_file(temp_path, S3_BUCKET, s3_key)
        
        # Create idea with transcribed text
        idea = IdeaInput(content=transcribed_text, source="voice")
        return await capture_idea(idea, current_user)
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# NLP Service Endpoints
@app.get("/ideas/{idea_id}/analysis")
async def get_idea_analysis(idea_id: int, current_user: dict = Depends(get_current_user)):
    """Get NLP analysis for an idea"""
    async with app.state.pool.acquire() as conn:
        idea = await conn.fetchrow(
            "SELECT * FROM ideas WHERE id = $1 AND user_id = $2",
            idea_id, current_user["user_id"]
        )
        
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        return {
            "id": idea["id"],
            "content": idea["content"],
            "project": idea["project"],
            "theme": idea["theme"],
            "emotion": idea["emotion"]
        }

# Transform Service Endpoints
@app.post("/transform/")
async def transform_idea(request: TransformRequest, current_user: dict = Depends(get_current_user)):
    """Transform idea into content, IP, or tasks"""
    # Verify idea ownership
    async with app.state.pool.acquire() as conn:
        idea = await conn.fetchrow(
            "SELECT * FROM ideas WHERE id = $1 AND user_id = $2",
            request.idea_id, current_user["user_id"]
        )
        
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
    
    # Generate transformation using xAI API
    transformed_content = await generate_transformation(idea["content"], request.output_type)
    
    # Save transformation
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "UPDATE ideas SET transformed_output = $1 WHERE id = $2",
            transformed_content, request.idea_id
        )
    
    return {"transformed_content": transformed_content}

async def generate_transformation(content: str, output_type: str) -> str:
    """Generate transformation using xAI API"""
    if not XAI_API_KEY:
        return f"Generated {output_type} for: {content}"  # Fallback
    
    prompts = {
        "content": f"Generate a blog post based on this idea: {content}",
        "ip": f"Create a patent-like summary for this concept: {content}",
        "tasks": f"Convert this idea into actionable tasks: {content}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                XAI_API_URL,
                headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                json={
                    "task": "text_generation",
                    "prompt": prompts.get(output_type, prompts["content"]),
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', f"Generated {output_type} for: {content}")
            else:
                return f"Generated {output_type} for: {content}"
    except Exception as e:
        print(f"Error generating transformation: {e}")
        return f"Generated {output_type} for: {content}"

# User Management Service Endpoints
@app.post("/users/")
async def create_user(user: UserCreate):
    """Create a new user"""
    async with app.state.pool.acquire() as conn:
        user_id = await conn.fetchval(
            "INSERT INTO users (auth0_id, email, subscription) VALUES ($1, $2, $3) RETURNING id",
            user.auth0_id, user.email, user.subscription
        )
        return {"id": user_id, "email": user.email, "subscription": user.subscription}

@app.get("/users/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    async with app.state.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE auth0_id = $1",
            current_user["user_id"]
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "subscription": user["subscription"]
        }

# Dashboard Endpoints
@app.get("/ideas/", response_model=List[IdeaResponse])
async def get_user_ideas(
    skip: int = 0,
    limit: int = 10,
    project: Optional[str] = None,
    theme: Optional[str] = None,
    emotion: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's ideas with filtering"""
    query = "SELECT * FROM ideas WHERE user_id = $1"
    params = [current_user["user_id"]]
    param_count = 1
    
    if project:
        param_count += 1
        query += f" AND project = ${param_count}"
        params.append(project)
    
    if theme:
        param_count += 1
        query += f" AND theme = ${param_count}"
        params.append(theme)
    
    if emotion:
        param_count += 1
        query += f" AND emotion = ${param_count}"
        params.append(emotion)
    
    query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
    params.extend([limit, skip])
    
    async with app.state.pool.acquire() as conn:
        ideas = await conn.fetch(query, *params)
        
        return [
            {
                "id": idea["id"],
                "content": idea["content"],
                "source": idea["source"],
                "timestamp": idea["timestamp"],
                "project": idea["project"],
                "theme": idea["theme"],
                "emotion": idea["emotion"],
                "transformed_output": idea["transformed_output"]
            }
            for idea in ideas
        ]

@app.get("/ideas/search/")
async def search_ideas(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    """Search ideas using full-text search"""
    async with app.state.pool.acquire() as conn:
        ideas = await conn.fetch(
            "SELECT * FROM ideas WHERE user_id = $1 AND to_tsvector('english', content) @@ plainto_tsquery('english', $2) ORDER BY timestamp DESC",
            current_user["user_id"], q
        )
        
        return [
            {
                "id": idea["id"],
                "content": idea["content"],
                "source": idea["source"],
                "timestamp": idea["timestamp"],
                "project": idea["project"],
                "theme": idea["theme"],
                "emotion": idea["emotion"]
            }
            for idea in ideas
        ]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()} 
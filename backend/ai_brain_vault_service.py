"""
AI Brain Vault Service - Main entry point
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "ai_brain_vault_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
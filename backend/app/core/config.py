"""
Configuration management for AI Brain Vault
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="ai_brain_vault", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    
    @property
    def dsn(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class AWSSettings(BaseSettings):
    """AWS configuration settings"""
    access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_bucket: str = Field(default="ai-brain-vault-audio", env="S3_BUCKET")


class KafkaSettings(BaseSettings):
    """Kafka configuration settings"""
    bootstrap_servers: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    topic_idea_sorting: str = Field(default="idea-sorting", env="KAFKA_TOPIC_IDEA_SORTING")
    topic_idea_transformation: str = Field(default="idea-transformation", env="KAFKA_TOPIC_IDEA_TRANSFORMATION")


class AIAPISettings(BaseSettings):
    """AI API configuration settings"""
    xai_api_key: Optional[str] = Field(default=None, env="XAI_API_KEY")
    xai_api_url: str = Field(default="https://api.x.ai/v1/llama3", env="XAI_API_URL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")


class Auth0Settings(BaseSettings):
    """Auth0 configuration settings"""
    domain: Optional[str] = Field(default=None, env="AUTH0_DOMAIN")
    audience: Optional[str] = Field(default=None, env="AUTH0_AUDIENCE")
    issuer: Optional[str] = Field(default=None, env="AUTH0_ISSUER")


class Settings(BaseSettings):
    """Main application settings"""
    # Application
    app_name: str = Field(default="AI Brain Vault API", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Database
    database: DatabaseSettings = DatabaseSettings()
    
    # AWS
    aws: AWSSettings = AWSSettings()
    
    # Kafka
    kafka: KafkaSettings = KafkaSettings()
    
    # AI APIs
    ai_api: AIAPISettings = AIAPISettings()
    
    # Auth0
    auth0: Auth0Settings = Auth0Settings()
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 
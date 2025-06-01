from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/influenceflow"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "influenceflow-creators"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "influenceflow-contracts"
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # WhatsApp (Mock for demo)
    WHATSAPP_API_URL: str = "https://api.whatsapp.com/send"
    WHATSAPP_TOKEN: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    EMAIL_QUEUE_NAME: str = None
    RABBITMQ_HOST: str = None
    RABBITMQ_PORT: int = None
    RABBITMQ_USER: str = None
    RABBITMQ_PASSWORD: str = None
    RABBITMQ_VHOST: str = None
    WHATSAPP_QUEUE_NAME: str = None

    OPENAI_API_KEY: str

    CHAT_DATABASE_URL: str

    STRIPE_SECRET_KEY: Optional[str] = None

    WHATSAPP_AGENT_API_URL: str 

    WHATSAPP_AGENT_API_TOKEN: str
    
    class Config:
        env_file = ".env"

settings = Settings()
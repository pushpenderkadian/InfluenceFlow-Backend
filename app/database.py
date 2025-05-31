from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DBAPIError, DisconnectionError
from sqlalchemy import text
from fastapi import HTTPException
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "server_settings": {
            "jit": "off"
        }
    }
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    session = None
    try:
        session = AsyncSessionLocal()
        # Test the connection
        await session.execute(text("SELECT 1"))
        yield session
    except (DBAPIError, DisconnectionError) as e:
        logger.error(f"Database connection error: {str(e)}")
        if session:
            try:
                await session.rollback()
            except:
                pass
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        if session:
            try:
                await session.rollback()
            except:
                pass
        raise e
    finally:
        if session:
            try:
                await session.close()
            except Exception as e:
                logger.error(f"Error closing database session: {str(e)}")
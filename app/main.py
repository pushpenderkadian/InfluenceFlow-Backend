from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
import logging
import asyncio

from .config import settings
from .middlewares.rate_limiter import limiter, rate_limit_handler
from .routers import auth, campaigns, creators
from .database import engine, Base
# Import all models to ensure they are registered with SQLAlchemy
from .models import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="InfluenceFlow API",
    description="End-to-End Influencer Marketing Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(campaigns.router)
app.include_router(creators.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    logger.info("Starting InfluenceFlow API...")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Create database tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database tables created successfully")
            break
            
        except Exception as e:
            logger.error(f"Database initialization failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.critical("Failed to initialize database after all retries")
                # Don't raise here to allow the app to start, but log the issue
                # The health check endpoint will show the database status

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down InfluenceFlow API...")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to InfluenceFlow API",
        "version": "1.0.0",
        "description": "End-to-End Influencer Marketing Automation Platform",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity"""
    health_status = {
        "status": "healthy",
        "service": "InfluenceFlow API",
        "database": "unknown"
    }
    
    try:
        # Test database connectivity
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"disconnected: {str(e)}"
        
    return health_status

@app.get("/demo-run")
async def demo_lifecycle():
    """Demo endpoint to simulate full campaign lifecycle"""
    return {
        "message": "Demo lifecycle simulation",
        "steps": [
            "1. Search creators using /creators/search",
            "2. Create campaign using /campaigns/",
            "3. Invite creators using /campaigns/{id}/invite",
            "4. Creators accept/decline invitations",
            "5. Generate contracts and send for signing",
            "6. Process payments",
            "7. Track performance metrics"
        ],
        "note": "Use the individual endpoints to test the complete workflow"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
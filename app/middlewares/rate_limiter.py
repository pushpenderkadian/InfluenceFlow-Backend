from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import redis.asyncio as redis
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection for rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL)
except Exception as e:
    logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
    redis_client = None

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL if redis_client else "memory://",
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)

# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = {
        "error": "Rate limit exceeded",
        "detail": f"Too many requests. Limit: {exc.detail}",
        "retry_after": exc.retry_after
    }
    raise HTTPException(status_code=429, detail=response)
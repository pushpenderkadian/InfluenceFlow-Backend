import asyncio
import logging
from functools import wraps
from sqlalchemy.exc import DBAPIError, DisconnectionError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry_db_operation(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry database operations that fail due to connection issues.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (DBAPIError, DisconnectionError, ConnectionError) as e:
                    last_exception = e
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    
                    if attempt < max_retries - 1:
                        # Wait before retrying, with exponential backoff
                        wait_time = delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # Last attempt failed, re-raise the exception
                        logger.error(f"Database operation failed after {max_retries} attempts: {str(e)}")
                        raise last_exception
                except Exception as e:
                    # For non-connection related errors, don't retry
                    logger.error(f"Non-retryable database error: {str(e)}")
                    raise e
            
            return None
        return wrapper
    return decorator

async def ensure_db_connection(db: AsyncSession) -> bool:
    """
    Check if database connection is alive and reconnect if necessary.
    """
    try:
        # Simple query to test connection
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database connection test failed: {str(e)}")
        try:
            # Try to rollback and close
            await db.rollback()
            await db.close()
        except:
            pass
        return False

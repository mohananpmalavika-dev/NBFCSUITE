"""
Logging Middleware
Logs all API requests and responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"→ {method} {path} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)
            
            # Log response
            status_code = response.status_code
            log_level = logging.INFO if status_code < 400 else logging.WARNING
            
            logger.log(
                log_level,
                f"← {method} {path} - {status_code} - {duration_ms}ms"
            )
            
            # Add custom headers
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            duration_ms = round(duration * 1000, 2)
            
            logger.error(
                f"✗ {method} {path} - ERROR - {duration_ms}ms - {str(e)}",
                exc_info=True
            )
            raise

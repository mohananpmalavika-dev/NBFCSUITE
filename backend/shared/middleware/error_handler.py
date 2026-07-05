"""
Error Handler Middleware
Standardizes error responses across the application
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback

from backend.shared.config import settings

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API exception"""
    
    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(APIError):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class UnauthorizedError(APIError):
    """Unauthorized access"""
    
    def __init__(self, message: str = "Unauthorized", details: dict = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class ForbiddenError(APIError):
    """Forbidden access"""
    
    def __init__(self, message: str = "Forbidden", details: dict = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationError(APIError):
    """Validation error"""
    
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ConflictError(APIError):
    """Resource conflict"""
    
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and standardize all errors
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except APIError as e:
            # Handle custom API errors
            logger.warning(f"API Error: {e.code} - {e.message}")
            
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "details": e.details
                    }
                }
            )
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            error_details = None
            if settings.APP_DEBUG:
                error_details = {
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "details": error_details
                    }
                }
            )

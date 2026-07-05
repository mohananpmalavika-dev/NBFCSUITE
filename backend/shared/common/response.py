"""
Standard API Response Format
Ensures consistent response structure across all endpoints
"""

from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi import status


class CustomException(Exception):
    """Custom API exception for application errors"""
    
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



def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict] = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Standard success response
    
    Args:
        data: Response data
        message: Success message
        meta: Optional metadata (pagination, etc.)
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized format
        
    Example:
        ```python
        @app.get("/users")
        async def get_users():
            users = await get_users_from_db()
            return success_response(
                data=users,
                message="Users retrieved successfully",
                meta={"total": len(users)}
            )
        ```
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if meta:
        response["meta"] = meta
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def error_response(
    message: str,
    code: str = "ERROR",
    details: Optional[Dict] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Standard error response
    
    Args:
        message: Error message
        code: Error code
        details: Optional error details
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized error format
        
    Example:
        ```python
        @app.get("/users/{user_id}")
        async def get_user(user_id: str):
            user = await get_user_from_db(user_id)
            if not user:
                return error_response(
                    message="User not found",
                    code="USER_NOT_FOUND",
                    status_code=404
                )
            return success_response(data=user)
        ```
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )


def paginated_response(
    data: list,
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "Success"
) -> JSONResponse:
    """
    Paginated response
    
    Args:
        data: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Items per page
        message: Success message
        
    Returns:
        JSONResponse with pagination metadata
        
    Example:
        ```python
        @app.get("/users")
        async def get_users(page: int = 1, page_size: int = 10):
            users, total = await get_paginated_users(page, page_size)
            return paginated_response(
                data=users,
                total=total,
                page=page,
                page_size=page_size
            )
        ```
    """
    total_pages = (total + page_size - 1) // page_size
    
    return success_response(
        data=data,
        message=message,
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    )

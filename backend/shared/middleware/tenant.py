"""
Multi-Tenant Middleware
Extracts tenant context from request and validates access
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional
import logging

from backend.shared.config import settings

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle multi-tenant context
    
    Tenant can be identified by:
    1. X-Tenant-ID header
    2. Subdomain (e.g., acme.nbfcsuite.com)
    3. Custom domain mapping
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip tenant check for health endpoints
        if request.url.path in ["/", "/health", "/health/ready", "/health/live", "/docs", "/redoc", "/openapi.json"]:
            request.state.tenant_id = settings.DEFAULT_TENANT_ID
            return await call_next(request)
        
        # Extract tenant ID
        tenant_id = self._extract_tenant_id(request)
        
        if not tenant_id:
            logger.warning(f"No tenant ID found for request: {request.url.path}")
            return Response(
                content='{"success": false, "error": {"code": "TENANT_REQUIRED", "message": "Tenant identification required"}}',
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="application/json"
            )
        
        # TODO: Validate tenant exists and is active
        # For now, accept any tenant ID
        
        # Store tenant ID in request state
        request.state.tenant_id = tenant_id
        logger.debug(f"Request tenant: {tenant_id}")
        
        # Process request
        response = await call_next(request)
        
        # Add tenant ID to response headers
        response.headers["X-Tenant-ID"] = tenant_id
        
        return response
    
    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extract tenant ID from request"""
        
        # 1. Check X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id
        
        # 2. Check subdomain
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            # Skip common subdomains
            if subdomain not in ["www", "api", "admin", "localhost"]:
                return subdomain
        
        # 3. Check query parameter (for testing)
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            return tenant_id
        
        # 4. Use default tenant
        return settings.DEFAULT_TENANT_ID


def get_tenant_id(request: Request) -> str:
    """
    Helper function to get tenant ID from request
    
    Usage:
        @app.get("/customers")
        async def get_customers(request: Request):
            tenant_id = get_tenant_id(request)
            ...
    """
    return getattr(request.state, "tenant_id", settings.DEFAULT_TENANT_ID)

"""
Deposit Operating System - Main Application
Enterprise Deposit Management Microservice
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from .routes import (
    products_router,
    accounts_router,
    rd_router,
    interest_router,
    maturity_router,
    premature_closure_router,
    ai_router,
    dashboard_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deposit Operating System",
    description="Enterprise-grade Deposit Management with AI Intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "deposit-os",
        "version": "1.0.0"
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Deposit Operating System",
        "version": "1.0.0",
        "description": "Enterprise Deposit Management with AI",
        "features": [
            "Fixed Deposit Management",
            "Recurring Deposit Management",
            "Interest Engine",
            "Maturity Management",
            "Premature Closure",
            "AI Intelligence",
            "Treasury Analytics"
        ],
        "docs": "/api/docs"
    }


# Include routers
app.include_router(products_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(rd_router, prefix="/api/v1")
app.include_router(interest_router, prefix="/api/v1")
app.include_router(maturity_router, prefix="/api/v1")
app.include_router(premature_closure_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("🚀 Deposit Operating System starting...")
    logger.info("📊 Initializing deposit engines...")
    logger.info("🤖 Loading AI models...")
    logger.info("✅ Deposit OS ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("👋 Deposit Operating System shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )

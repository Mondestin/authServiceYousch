"""
Main FastAPI application for the AuthService
Includes comprehensive middleware, error handling, and startup/shutdown events
"""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import init_database, close_database_connection, engine
from app.core.logging import setup_logging, get_logger

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger = get_logger(__name__)
    logger.info("Starting authGhost API", version="1.0.0")
    
    try:
        # Setup logging
        setup_logging()
        logger.info("Logging configured successfully")
        
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Test database connection
        from app.core.database import test_database_connection
        if test_database_connection(engine):
            logger.info("Database connection test successful")
        else:
            logger.error("Database connection test failed")
        
        logger.info("authGhost API started successfully")
        
    except Exception as e:
        logger.error("Failed to start authGhost API", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down authGhost API")
    try:
        # Close database connections
        close_database_connection(engine)
        logger.info("Database connections closed")
        
        logger.info("authGhost API shutdown completed")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="authGhost API",
    description="""
    authGhost is Phoenone's centralized authentication and access management API, designed for developers
    building multi-service applications. It provides a secure and consistent way to handle:

    - User authentication and service-specific JWT token issuance.
    - Role-based access control (RBAC) across multiple services.
    - Organization-level subscription management and feature access.
    - Multi-tenant support for SaaS platforms.
    - Token refresh and optional revocation for secure session management.

    Developers can integrate authGhost with Laravel, Symfony, SpringBoot, ExpressJS, or any other 
    microservices, ensuring that authentication, authorization, and subscription checks are consistent 
    across all products. It is optimized for stateless JWT validation but also supports token introspection 
    for revocable access.
    """,
    version="1.0.0",
    docs_url="/docs",  # Always show Swagger docs
    redoc_url="/redoc",  # Always show ReDoc docs
    openapi_url="/openapi.json",  # Always show OpenAPI schema
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers"""
    start_time = time.time()
    
    # Get request ID from headers or generate new one
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add timing headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger = get_logger(__name__)
    
    # Log the error
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger = get_logger(__name__)
    
    # Log the validation error
    logger.warning(
        "Request validation failed",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger = get_logger(__name__)
    
    # Log the error
    logger.error(
        "Unhandled exception occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "docs": "/docs",  # Always show docs link
        "health": "/api/v1/health/health"
    }


# Health check at root level for load balancers
@app.get("/health")
async def root_health_check() -> dict:
    """Simple health check for load balancers"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower()
    ) 
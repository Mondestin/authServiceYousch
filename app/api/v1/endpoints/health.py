"""
Health check endpoints for the AuthService
Includes service status, database connectivity, and system information
"""

import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.database import test_database_connection, get_database_info, engine
from app.core.logging import get_logger
from app.schemas.auth import HealthCheck

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Service start time for uptime calculation
START_TIME = time.time()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)) -> Any:
    """
    Comprehensive health check endpoint
    
    Args:
        db: Database session
        
    Returns:
        HealthCheck: Service health status and information
    """
    try:
        # Calculate uptime
        uptime = time.time() - START_TIME
        
        # Test database connection
        db_status = "healthy" if test_database_connection(engine) else "unhealthy"
        
        # Get database pool information
        db_info = get_database_info(engine)
        
        # Create health check response
        health_data = HealthCheck(
            status="healthy" if db_status == "healthy" else "degraded",
            timestamp=datetime.now().isoformat(),
            version=settings.app_version,
            environment=settings.environment,
            database={
                "status": db_status,
                "pool_size": db_info.get("pool_size", 0),
                "checked_out": db_info.get("checked_out", 0),
                "overflow": db_info.get("overflow", 0)
            },
            uptime=uptime
        )
        
        # Log health check
        logger.info("Health check performed", 
                   status=health_data.status,
                   database_status=db_status,
                   uptime=uptime)
        
        return health_data
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        
        # Return degraded status on error
        return HealthCheck(
            status="degraded",
            timestamp=datetime.now().isoformat(),
            version=settings.app_version,
            environment=settings.environment,
            database={
                "status": "unknown",
                "pool_size": 0,
                "checked_out": 0,
                "overflow": 0
            },
            uptime=time.time() - START_TIME
        )


@router.get("/health/readiness")
async def readiness_check() -> dict:
    """
    Readiness check for Kubernetes/container orchestration
    
    Returns:
        dict: Readiness status
    """
    try:
        # Check if service is ready to receive traffic
        # This could include database connectivity, external service checks, etc.
        
        # Test database connection
        db_ready = test_database_connection(engine)
        
        if db_ready:
            logger.info("Readiness check passed")
            return {"status": "ready"}
        else:
            logger.warning("Readiness check failed - database not accessible")
            return {"status": "not_ready", "reason": "database_unavailable"}
            
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {"status": "not_ready", "reason": "service_error"}


@router.get("/health/liveness")
async def liveness_check() -> dict:
    """
    Liveness check for Kubernetes/container orchestration
    
    Returns:
        dict: Liveness status
    """
    try:
        # Simple check to see if the service is alive
        # This should be lightweight and not check external dependencies
        
        uptime = time.time() - START_TIME
        
        # Consider service dead if it's been running for more than 24 hours without restart
        # This is a simple example - in production you might want more sophisticated logic
        if uptime > 86400:  # 24 hours
            logger.warning("Service has been running for more than 24 hours")
            return {"status": "alive", "uptime": uptime, "warning": "long_uptime"}
        
        logger.info("Liveness check passed", uptime=uptime)
        return {"status": "alive", "uptime": uptime}
        
    except Exception as e:
        logger.error("Liveness check failed", error=str(e))
        return {"status": "dead", "reason": "service_error"}


@router.get("/health/detailed")
async def detailed_health_check() -> dict:
    """
    Detailed health check with comprehensive system information
    
    Returns:
        dict: Detailed health information
    """
    try:
        # Test database connection
        db_healthy = test_database_connection(engine)
        db_info = get_database_info(engine) if db_healthy else {}
        
        # Calculate uptime
        uptime = time.time() - START_TIME
        
        # Get memory usage (basic)
        memory_info = {}
        cpu_percent = 0
        disk_info = {}
        
        try:
            import psutil
            memory_info = {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            }
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Check disk usage
            try:
                disk_usage = psutil.disk_usage('/')
                disk_info = {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": disk_usage.percent
                }
            except Exception:
                disk_info = {"error": "Unable to get disk information"}
        except ImportError:
            memory_info = {"error": "psutil not available"}
            cpu_percent = 0
            disk_info = {"error": "psutil not available"}
        
        # Overall health status
        overall_status = "healthy"
        issues = []
        
        if not db_healthy:
            overall_status = "degraded"
            issues.append("database_unavailable")
        
        if memory_info["percent"] > 90:
            overall_status = "degraded"
            issues.append("high_memory_usage")
        
        if cpu_percent > 90:
            overall_status = "degraded"
            issues.append("high_cpu_usage")
        
        if disk_info.get("percent", 0) > 90:
            overall_status = "degraded"
            issues.append("high_disk_usage")
        
        detailed_health = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "service": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "uptime": uptime
            },
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "pool_info": db_info
            },
            "system": {
                "memory": memory_info,
                "cpu_percent": cpu_percent,
                "disk": disk_info
            },
            "issues": issues
        }
        
        logger.info("Detailed health check completed", 
                   status=overall_status,
                   issues_count=len(issues))
        
        return detailed_health
        
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/health/metrics")
async def metrics() -> dict:
    """
    Basic metrics endpoint for monitoring
    
    Returns:
        dict: Service metrics
    """
    try:
        uptime = time.time() - START_TIME
        
        # Get database pool information
        db_info = get_database_info(engine)
        
        # Basic metrics
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "database": {
                "pool_size": db_info.get("pool_size", 0),
                "checked_in": db_info.get("checked_in", 0),
                "checked_out": db_info.get("checked_out", 0),
                "overflow": db_info.get("overflow", 0)
            },
            "service": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment
            }
        }
        
        logger.debug("Metrics collected", metrics_count=len(metrics_data))
        return metrics_data
        
    except Exception as e:
        logger.error("Metrics collection failed", error=str(e))
        return {
            "error": "Failed to collect metrics",
            "timestamp": datetime.now().isoformat()
        } 
"""
Comprehensive logging configuration for the AuthService
Includes structured logging, file rotation, and JSON formatting for production
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import get_settings

# Get settings
settings = get_settings()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp if not present
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.now().isoformat()
        
        # Ensure level is properly set
        if not log_record.get('level'):
            log_record['level'] = record.levelname
        
        # Add service information
        log_record['service'] = settings.app_name
        log_record['version'] = settings.app_version
        log_record['environment'] = record.environment if hasattr(record, 'environment') else settings.environment
        
        # Add process and thread information
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Add function and line information
        if record.funcName:
            log_record['function'] = record.funcName
        if record.lineno:
            log_record['line_number'] = record.lineno
        
        # Add module information
        if record.module:
            log_record['module'] = record.module
        
        # Add task name if available (for async operations)
        if hasattr(record, 'taskName'):
            log_record['taskName'] = record.taskName


def setup_logging() -> None:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    if settings.log_file_path:
        log_dir = Path(settings.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    if settings.log_format.lower() == "json":
        console_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(level)s - %(message)s'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation if log file path is specified
    if settings.log_file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file_path,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, settings.log_level))
        
        # Always use JSON format for file logging
        file_formatter = CustomJsonFormatter(
            '%(timestamp)s %(levelname)s %(name)s %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)
    
    # Configure structlog for structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def log_request_info(request_id: str, method: str, url: str, client_ip: str, user_agent: str) -> None:
    """Log request information for monitoring"""
    logger = get_logger("request")
    logger.info(
        "Incoming request",
        request_id=request_id,
        method=method,
        url=url,
        client_ip=client_ip,
        user_agent=user_agent
    )


def log_response_info(request_id: str, status_code: int, response_time: float) -> None:
    """Log response information for monitoring"""
    logger = get_logger("response")
    logger.info(
        "Response sent",
        request_id=request_id,
        status_code=status_code,
        response_time_ms=round(response_time * 1000, 2)
    )


def log_auth_event(event_type: str, user_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
    """Log authentication events for security monitoring"""
    logger = get_logger("auth")
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if details:
        log_data.update(details)
    
    logger.info("Authentication event", **log_data)


def log_security_event(event_type: str, severity: str, details: Dict[str, Any]) -> None:
    """Log security events for threat detection"""
    logger = get_logger("security")
    log_data = {
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        **details
    }
    
    logger.warning("Security event detected", **log_data)


def log_database_operation(operation: str, table: str, duration: float, success: bool) -> None:
    """Log database operations for performance monitoring"""
    logger = get_logger("database")
    logger.info(
        "Database operation",
        operation=operation,
        table=table,
        duration_ms=round(duration * 1000, 2),
        success=success
    )


def log_external_service_call(service: str, endpoint: str, duration: float, status_code: int, success: bool) -> None:
    """Log external service calls for monitoring"""
    logger = get_logger("external_service")
    logger.info(
        "External service call",
        service=service,
        endpoint=endpoint,
        duration_ms=round(duration * 1000, 2),
        status_code=status_code,
        success=success
    ) 
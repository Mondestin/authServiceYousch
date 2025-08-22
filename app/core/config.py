"""
Configuration management for the AuthService
Uses Pydantic settings for type-safe environment variable handling
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = Field(default="Yousch", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="dev", env="ENVIRONMENT")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Security Settings
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database Settings
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file_path: Optional[str] = Field(default="logs/auth_service.log", env="LOG_FILE_PATH")
    
    # Redis Settings
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # External Services
    user_service_url: Optional[str] = Field(default=None, env="USER_SERVICE_URL")
    notification_service_url: Optional[str] = Field(default=None, env="NOTIFICATION_SERVICE_URL")
    
    # Email Settings - Support both naming conventions
    mail_driver: str = Field(default="smtp", env="MAIL_DRIVER")
    mail_host: str = Field(default="fleetpay.phoenone.com", env="MAIL_HOST")
    mail_port: int = Field(default=465, env="MAIL_PORT")
    mail_username: str = Field(default="noreply@fleetpay.phoenone.com", env="MAIL_USERNAME")
    mail_password: str = Field(default="", env="MAIL_PASSWORD")
    mail_encryption: str = Field(default="ssl", env="MAIL_ENCRYPTION")
    mail_use_tls: bool = Field(default=False, env="MAIL_USE_TLS")
    mail_use_ssl: bool = Field(default=True, env="MAIL_USE_SSL")
    mail_from_name: str = Field(default="Yousch", env="MAIL_FROM_NAME")
    mail_from_address: str = Field(default="noreply@fleetpay.phoenone.com", env="MAIL_FROM_ADDRESS")
    mail_verification_url: str = Field(default="http://localhost:3000/verify-email", env="MAIL_VERIFICATION_URL")
    mail_password_reset_url: str = Field(default="http://localhost:3000/reset-password", env="MAIL_PASSWORD_RESET_URL")
    mail_login_url: str = Field(default="http://localhost:3000/login", env="MAIL_LOGIN_URL")
    mail_to_admin: Optional[str] = Field(default="sydneymondestin@gmail.com", env="MAIL_TO_ADMIN")
    

    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is at least 32 characters long"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the allowed values"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    @field_validator("mail_use_tls")
    @classmethod
    def validate_mail_use_tls(cls, v, info):
        """Set mail_use_tls based on encryption type"""
        if hasattr(info, 'data') and info.data:
            encryption = info.data.get("mail_encryption", "ssl")
            return encryption in ["tls", "ssl"]
        return v
    
    @field_validator("mail_use_ssl")
    @classmethod
    def validate_mail_use_ssl(cls, v, info):
        """Set mail_use_ssl based on encryption type"""
        if hasattr(info, 'data') and info.data:
            encryption = info.data.get("mail_encryption", "ssl")
            return encryption in ["tls", "ssl"]
        return v
    

    

    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings 
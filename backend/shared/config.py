"""
Shared Configuration Module
Loads configuration from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "NBFC Financial Suite"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_URL: str = "postgresql://nbfc_admin:nbfc_secure_2026@localhost:5432/nbfc_suite"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://:nbfc_redis_2026@localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "nbfc_redis_2026"
    REDIS_DB: int = 0
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://nbfc_admin:nbfc_rabbit_2026@localhost:5672/"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "nbfc_admin"
    MINIO_SECRET_KEY: str = "nbfc_minio_2026"
    MINIO_BUCKET: str = "nbfc-documents"
    MINIO_SECURE: bool = False
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "nbfc"
    
    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "change-this-32-byte-encryption-key"
    
    # Multi-tenant
    DEFAULT_TENANT_ID: str = "default"
    TENANT_ISOLATION_ENABLED: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Feature Flags
    FEATURE_WORKFLOW_ENGINE: bool = True
    FEATURE_RULES_ENGINE: bool = True
    FEATURE_DECISION_ENGINE: bool = True
    FEATURE_FRAUD_DETECTION: bool = True
    FEATURE_AI_ASSISTANT: bool = False
    FEATURE_MULTI_TENANT: bool = True
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    
    # API Documentation
    ENABLE_SWAGGER: bool = True
    ENABLE_REDOC: bool = True
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@nbfcsuite.com"
    SMTP_FROM_NAME: str = "NBFC Suite"
    
    # SMS
    SMS_PROVIDER: str = "twilio"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Aadhaar eKYC
    AADHAAR_API_URL: str = ""
    AADHAAR_CLIENT_ID: str = ""
    AADHAAR_CLIENT_SECRET: str = ""
    
    # Credit Bureaus
    CIBIL_API_URL: str = ""
    CIBIL_USER_ID: str = ""
    CIBIL_PASSWORD: str = ""
    
    # Payment Gateway
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    
    # AWS
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    
    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    PROMETHEUS_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

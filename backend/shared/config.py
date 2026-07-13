"""
Configuration Settings with Feature Flags for Memory Optimization
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = ConfigDict(
        extra='ignore',  # Ignore extra fields from .env file
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    
    # Application
    APP_NAME: str = "NBFC Financial Suite"
    APP_ENV: str = Field(default="production", env="APP_ENV")
    APP_DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")  # SQLAlchemy echo queries
    DB_POOL_SIZE: int = Field(default=2, env="DB_POOL_SIZE")  # Reduced from 5 for memory
    DB_MAX_OVERFLOW: int = Field(default=3, env="DB_MAX_OVERFLOW")  # Reduced from 10
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=False, env="CORS_ALLOW_CREDENTIALS")
    
    # Multi-tenancy
    TENANT_ISOLATION_ENABLED: bool = Field(default=True, env="TENANT_ISOLATION_ENABLED")
    DEFAULT_TENANT_ID: str = Field(default="default", env="DEFAULT_TENANT_ID")
    
    # Redis (optional)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # RabbitMQ (optional)
    RABBITMQ_URL: Optional[str] = Field(default=None, env="RABBITMQ_URL")
    
    # AWS (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="ap-south-1", env="AWS_REGION")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(default=10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field(default="pdf,jpg,jpeg,png,doc,docx", env="ALLOWED_EXTENSIONS")
    
    # API Documentation
    ENABLE_SWAGGER: bool = Field(default=True, env="ENABLE_SWAGGER")
    ENABLE_REDOC: bool = Field(default=True, env="ENABLE_REDOC")
    
    # ==================================================================
    # FEATURE FLAGS FOR MEMORY OPTIMIZATION (FREE TIER)
    # Enable only the modules you need to reduce memory usage
    # ==================================================================
    
    # Core modules (always enabled)
    ENABLE_AUTH: bool = Field(default=True, env="ENABLE_AUTH")
    ENABLE_DASHBOARD: bool = Field(default=True, env="ENABLE_DASHBOARD")
    
    # Essential business modules
    ENABLE_CUSTOMERS: bool = Field(default=True, env="ENABLE_CUSTOMERS")
    ENABLE_LOANS: bool = Field(default=True, env="ENABLE_LOANS")
    ENABLE_ACCOUNTING: bool = Field(default=False, env="ENABLE_ACCOUNTING")  # Disabled by default
    ENABLE_MASTERDATA: bool = Field(default=True, env="ENABLE_MASTERDATA")
    
    # Optional modules (disable to save memory)
    ENABLE_DEPOSITS: bool = Field(default=False, env="ENABLE_DEPOSITS")
    ENABLE_GOLD_LOANS: bool = Field(default=False, env="ENABLE_GOLD_LOANS")
    ENABLE_VEHICLE_LOANS: bool = Field(default=False, env="ENABLE_VEHICLE_LOANS")
    ENABLE_PROPERTY_LOANS: bool = Field(default=False, env="ENABLE_PROPERTY_LOANS")
    
    # Advanced modules (disable to save memory)
    ENABLE_WORKFLOW: bool = Field(default=False, env="ENABLE_WORKFLOW")
    ENABLE_RULES_ENGINE: bool = Field(default=False, env="ENABLE_RULES_ENGINE")
    ENABLE_DECISION_ENGINE: bool = Field(default=False, env="ENABLE_DECISION_ENGINE")
    ENABLE_NOTIFICATIONS: bool = Field(default=False, env="ENABLE_NOTIFICATIONS")
    
    # Integration modules (disable to save memory)
    ENABLE_BUREAU_INTEGRATION: bool = Field(default=False, env="ENABLE_BUREAU_INTEGRATION")
    ENABLE_BANK_STATEMENT: bool = Field(default=False, env="ENABLE_BANK_STATEMENT")
    ENABLE_OCR: bool = Field(default=False, env="ENABLE_OCR")
    ENABLE_EKYC: bool = Field(default=False, env="ENABLE_EKYC")
    ENABLE_DIGILOCKER: bool = Field(default=False, env="ENABLE_DIGILOCKER")
    
    # Compliance & Regulatory (disable to save memory)
    ENABLE_COMPLIANCE: bool = Field(default=False, env="ENABLE_COMPLIANCE")
    ENABLE_RISK_MANAGEMENT: bool = Field(default=False, env="ENABLE_RISK_MANAGEMENT")
    
    # Treasury & Cash (disable to save memory)
    ENABLE_TREASURY: bool = Field(default=False, env="ENABLE_TREASURY")
    ENABLE_ALM: bool = Field(default=False, env="ENABLE_ALM")
    
    # Branch Operations (disable to save memory)
    ENABLE_BRANCH: bool = Field(default=False, env="ENABLE_BRANCH")
    
    # HRMS modules (disable to save memory)
    ENABLE_HRMS: bool = Field(default=False, env="ENABLE_HRMS")
    ENABLE_RECRUITMENT: bool = Field(default=False, env="ENABLE_RECRUITMENT")
    ENABLE_ATTENDANCE: bool = Field(default=False, env="ENABLE_ATTENDANCE")
    ENABLE_PAYROLL: bool = Field(default=False, env="ENABLE_PAYROLL")
    ENABLE_TRAINING: bool = Field(default=False, env="ENABLE_TRAINING")
    
    # Asset Management (disable to save memory)
    ENABLE_FIXED_ASSETS: bool = Field(default=False, env="ENABLE_FIXED_ASSETS")
    ENABLE_INVENTORY: bool = Field(default=False, env="ENABLE_INVENTORY")
    
    # CRM modules (disable to save memory)
    ENABLE_CRM: bool = Field(default=False, env="ENABLE_CRM")
    ENABLE_CRM_OPPORTUNITIES: bool = Field(default=False, env="ENABLE_CRM_OPPORTUNITIES")
    ENABLE_CRM_SALES: bool = Field(default=False, env="ENABLE_CRM_SALES")
    ENABLE_CRM_SERVICE: bool = Field(default=False, env="ENABLE_CRM_SERVICE")
    
    # Legal & Compliance (disable to save memory)
    ENABLE_LEGAL: bool = Field(default=False, env="ENABLE_LEGAL")
    ENABLE_LITIGATION: bool = Field(default=False, env="ENABLE_LITIGATION")
    ENABLE_LICENSE: bool = Field(default=False, env="ENABLE_LICENSE")
    
    # Document Management (disable to save memory)
    ENABLE_DMS: bool = Field(default=False, env="ENABLE_DMS")
    
    # Facility Management (disable to save memory)
    ENABLE_FACILITY: bool = Field(default=False, env="ENABLE_FACILITY")
    
    # Reporting & Analytics (disable to save memory)
    ENABLE_REPORTING: bool = Field(default=False, env="ENABLE_REPORTING")
    
    # Insurance (disable to save memory)
    ENABLE_INSURANCE: bool = Field(default=False, env="ENABLE_INSURANCE")
    
    # LMS Extensions (disable to save memory)
    ENABLE_NACH: bool = Field(default=False, env="ENABLE_NACH")
    ENABLE_RESTRUCTURING: bool = Field(default=False, env="ENABLE_RESTRUCTURING")
    ENABLE_LOAN_INSURANCE: bool = Field(default=False, env="ENABLE_LOAN_INSURANCE")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convert ALLOWED_EXTENSIONS string to list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
        return self.ALLOWED_EXTENSIONS


# Create settings instance
settings = Settings()

"""
Integration Hub Models
Phase 13: Integration Hub
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, TIMESTAMP, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class IntegrationProvider(Base):
    """External system/service providers"""
    __tablename__ = "integration_providers"

    provider_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Provider Details
    provider_code = Column(String(50), nullable=False, unique=True, index=True)
    provider_name = Column(String(200), nullable=False)
    provider_type = Column(String(50), nullable=False, index=True)
    provider_category = Column(String(50), nullable=False, index=True)
    
    # Provider Information
    description = Column(Text)
    website_url = Column(String(500))
    support_email = Column(String(200))
    support_phone = Column(String(50))
    documentation_url = Column(String(500))
    
    # Connection Details
    base_url = Column(String(500))
    auth_type = Column(String(50))
    connection_timeout = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    retry_delay = Column(Integer, default=5)
    
    # Configuration
    config_schema = Column(JSONB)
    default_config = Column(JSONB)
    supported_operations = Column(JSONB)
    
    # Status & Compliance
    provider_status = Column(String(50), default='active', index=True)
    certification_required = Column(Boolean, default=False)
    compliance_requirements = Column(JSONB)
    
    # Versioning
    api_version = Column(String(50))
    sdk_version = Column(String(50))
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    configurations = relationship("IntegrationConfiguration", back_populates="provider", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="provider")


class IntegrationConfiguration(Base):
    """Configuration instances for providers"""
    __tablename__ = "integration_configurations"

    config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Provider Reference
    provider_id = Column(UUID(as_uuid=True), ForeignKey('integration_providers.provider_id'), nullable=False, index=True)
    
    # Configuration Details
    config_name = Column(String(200), nullable=False)
    config_code = Column(String(50), nullable=False, unique=True, index=True)
    environment = Column(String(50), nullable=False, index=True)
    
    # Connection Configuration
    endpoint_url = Column(String(500))
    auth_config = Column(JSONB)
    headers = Column(JSONB)
    query_params = Column(JSONB)
    
    # Provider-Specific Settings
    provider_config = Column(JSONB)
    feature_flags = Column(JSONB)
    limits_config = Column(JSONB)
    
    # Routing & Load Balancing
    priority = Column(Integer, default=1)
    weight = Column(Integer, default=100)
    is_primary = Column(Boolean, default=False)
    failover_config_id = Column(UUID(as_uuid=True), ForeignKey('integration_configurations.config_id'))
    
    # Security
    ip_whitelist = Column(JSONB)
    encryption_enabled = Column(Boolean, default=True)
    certificate_path = Column(String(500))
    
    # Monitoring
    health_check_url = Column(String(500))
    health_check_interval = Column(Integer, default=60)
    last_health_check = Column(TIMESTAMP)
    health_status = Column(String(50), index=True)
    
    # Status
    config_status = Column(String(50), default='active', index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(TIMESTAMP)
    
    # Relationships
    provider = relationship("IntegrationProvider", back_populates="configurations")
    endpoints = relationship("IntegrationEndpoint", back_populates="configuration", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="configuration")
    failover_config = relationship("IntegrationConfiguration", remote_side=[config_id])


class IntegrationEndpoint(Base):
    """Specific API endpoints for integrations"""
    __tablename__ = "integration_endpoints"

    endpoint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration Reference
    config_id = Column(UUID(as_uuid=True), ForeignKey('integration_configurations.config_id'), nullable=False, index=True)
    
    # Endpoint Details
    endpoint_name = Column(String(200), nullable=False)
    endpoint_code = Column(String(50), nullable=False, index=True)
    endpoint_path = Column(String(500), nullable=False)
    http_method = Column(String(10), nullable=False, index=True)
    
    # Operation Details
    operation_type = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Request Configuration
    request_format = Column(String(50))
    request_schema = Column(JSONB)
    request_template = Column(JSONB)
    headers = Column(JSONB)
    
    # Response Configuration
    response_format = Column(String(50))
    response_schema = Column(JSONB)
    success_codes = Column(JSONB)
    error_mapping = Column(JSONB)
    
    # Retry & Timeout
    timeout_seconds = Column(Integer, default=30)
    retry_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_strategy = Column(String(50))
    
    # Rate Limiting
    rate_limit_per_minute = Column(Integer)
    rate_limit_per_hour = Column(Integer)
    rate_limit_per_day = Column(Integer)
    
    # Transformation
    request_transformer = Column(String(100))
    response_transformer = Column(String(100))
    
    # Monitoring
    log_request = Column(Boolean, default=True)
    log_response = Column(Boolean, default=True)
    mask_sensitive_data = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    configuration = relationship("IntegrationConfiguration", back_populates="endpoints")
    logs = relationship("IntegrationLog", back_populates="endpoint")


class IntegrationLog(Base):
    """Detailed logging of integration calls"""
    __tablename__ = "integration_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reference
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey('integration_endpoints.endpoint_id'), index=True)
    config_id = Column(UUID(as_uuid=True), ForeignKey('integration_configurations.config_id'), index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('integration_providers.provider_id'), index=True)
    
    # Request Details
    correlation_id = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True)
    request_timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    request_method = Column(String(10))
    request_url = Column(Text)
    request_headers = Column(JSONB)
    request_body = Column(JSONB)
    
    # Response Details
    response_timestamp = Column(TIMESTAMP)
    response_duration = Column(Integer)
    response_status = Column(Integer)
    response_headers = Column(JSONB)
    response_body = Column(JSONB)
    
    # Transaction Context
    transaction_id = Column(UUID(as_uuid=True), index=True)
    entity_type = Column(String(100), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), index=True)
    
    # Status & Error
    call_status = Column(String(50), index=True)
    error_code = Column(String(100))
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Retry Information
    retry_attempt = Column(Integer, default=0)
    is_retry = Column(Boolean, default=False, index=True)
    parent_log_id = Column(UUID(as_uuid=True), ForeignKey('integration_logs.log_id'))
    
    # Performance
    response_size = Column(Integer)
    network_time = Column(Integer)
    processing_time = Column(Integer)
    
    # IP & Location
    client_ip = Column(String(50))
    server_ip = Column(String(50))
    
    # Metadata
    additional_metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    endpoint = relationship("IntegrationEndpoint", back_populates="logs")
    parent_log = relationship("IntegrationLog", remote_side=[log_id])


class APIKey(Base):
    """API key management for external systems"""
    __tablename__ = "api_keys"

    key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Key Details
    key_name = Column(String(200), nullable=False)
    key_code = Column(String(50), nullable=False, unique=True, index=True)
    api_key = Column(String(500), nullable=False, unique=True)
    key_secret = Column(String(500))
    
    # Association
    config_id = Column(UUID(as_uuid=True), ForeignKey('integration_configurations.config_id'), index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('integration_providers.provider_id'), index=True)
    
    # Scope & Permissions
    key_type = Column(String(50), nullable=False, index=True)
    allowed_operations = Column(JSONB)
    ip_whitelist = Column(JSONB)
    rate_limits = Column(JSONB)
    
    # Validity
    valid_from = Column(TIMESTAMP, default=datetime.utcnow)
    valid_until = Column(TIMESTAMP, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Usage Stats
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    failed_calls = Column(Integer, default=0)
    last_used_at = Column(TIMESTAMP, index=True)
    last_used_ip = Column(String(50))
    
    # Security
    encryption_algorithm = Column(String(50))
    rotation_required = Column(Boolean, default=False, index=True)
    rotation_due_date = Column(Date, index=True)
    previous_key_id = Column(UUID(as_uuid=True), ForeignKey('api_keys.key_id'))
    
    # Metadata
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    revoked_at = Column(TIMESTAMP)
    revoked_by = Column(UUID(as_uuid=True))
    revocation_reason = Column(Text)
    
    # Relationships
    configuration = relationship("IntegrationConfiguration", back_populates="api_keys")
    provider = relationship("IntegrationProvider", back_populates="api_keys")
    previous_key = relationship("APIKey", remote_side=[key_id])


class Webhook(Base):
    """Webhook configurations for event notifications"""
    __tablename__ = "webhooks"

    webhook_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Webhook Details
    webhook_name = Column(String(200), nullable=False)
    webhook_code = Column(String(50), nullable=False, unique=True, index=True)
    
    # Target Configuration
    target_url = Column(String(500), nullable=False)
    http_method = Column(String(10), default='POST')
    
    # Authentication
    auth_type = Column(String(50))
    auth_config = Column(JSONB)
    
    # Headers & Payload
    custom_headers = Column(JSONB)
    payload_template = Column(JSONB)
    content_type = Column(String(100), default='application/json')
    
    # Event Configuration
    event_types = Column(JSONB, nullable=False)
    event_filters = Column(JSONB)
    
    # Delivery Settings
    delivery_timeout = Column(Integer, default=30)
    retry_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)
    
    # Security
    signature_enabled = Column(Boolean, default=True)
    signature_algorithm = Column(String(50), default='sha256')
    signature_header = Column(String(100), default='X-Webhook-Signature')
    secret_key = Column(String(500))
    
    # Status & Monitoring
    webhook_status = Column(String(50), default='active', index=True)
    last_triggered_at = Column(TIMESTAMP, index=True)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")


class WebhookDelivery(Base):
    """Webhook delivery attempts and logs"""
    __tablename__ = "webhook_deliveries"

    delivery_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Webhook Reference
    webhook_id = Column(UUID(as_uuid=True), ForeignKey('webhooks.webhook_id'), nullable=False, index=True)
    
    # Event Details
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    event_timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    event_payload = Column(JSONB, nullable=False)
    
    # Delivery Attempt
    attempt_number = Column(Integer, default=1, index=True)
    attempted_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Request Details
    request_url = Column(String(500))
    request_method = Column(String(10))
    request_headers = Column(JSONB)
    request_body = Column(JSONB)
    signature = Column(String(500))
    
    # Response Details
    response_status = Column(Integer)
    response_headers = Column(JSONB)
    response_body = Column(JSONB)
    response_time = Column(Integer)
    
    # Status
    delivery_status = Column(String(50), index=True)
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Retry Information
    next_retry_at = Column(TIMESTAMP, index=True)
    max_retries_reached = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")


class MessageQueue(Base):
    """Async message queue for integrations"""
    __tablename__ = "message_queue"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Message Details
    message_type = Column(String(100), nullable=False, index=True)
    priority = Column(Integer, default=5, index=True)
    
    # Target
    target_config_id = Column(UUID(as_uuid=True), ForeignKey('integration_configurations.config_id'), index=True)
    target_endpoint_id = Column(UUID(as_uuid=True), ForeignKey('integration_endpoints.endpoint_id'), index=True)
    
    # Payload
    message_payload = Column(JSONB, nullable=False)
    message_headers = Column(JSONB)
    
    # Context
    correlation_id = Column(UUID(as_uuid=True), index=True)
    entity_type = Column(String(100), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True))
    
    # Scheduling
    scheduled_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    expires_at = Column(TIMESTAMP, index=True)
    
    # Processing
    status = Column(String(50), default='pending', index=True)
    picked_at = Column(TIMESTAMP)
    processed_at = Column(TIMESTAMP)
    worker_id = Column(String(100))
    
    # Retry Logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(TIMESTAMP, index=True)
    
    # Result
    result = Column(JSONB)
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

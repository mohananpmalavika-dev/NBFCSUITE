"""
Integration Hub Schemas
Phase 13: Integration Hub
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


# =====================================================
# Integration Provider Schemas
# =====================================================

class IntegrationProviderCreate(BaseModel):
    provider_code: str = Field(..., max_length=50)
    provider_name: str = Field(..., max_length=200)
    provider_type: str
    provider_category: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    documentation_url: Optional[str] = None
    base_url: Optional[str] = None
    auth_type: Optional[str] = None
    connection_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    supported_operations: Optional[List[str]] = None
    certification_required: bool = False
    compliance_requirements: Optional[Dict[str, Any]] = None
    api_version: Optional[str] = None
    sdk_version: Optional[str] = None
    created_by: Optional[UUID] = None


class IntegrationProviderUpdate(BaseModel):
    provider_name: Optional[str] = None
    provider_type: Optional[str] = None
    provider_category: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    documentation_url: Optional[str] = None
    base_url: Optional[str] = None
    auth_type: Optional[str] = None
    connection_timeout: Optional[int] = None
    retry_attempts: Optional[int] = None
    retry_delay: Optional[int] = None
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    supported_operations: Optional[List[str]] = None
    provider_status: Optional[str] = None
    certification_required: Optional[bool] = None
    compliance_requirements: Optional[Dict[str, Any]] = None
    api_version: Optional[str] = None
    sdk_version: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[UUID] = None


class IntegrationProviderResponse(BaseModel):
    provider_id: UUID
    provider_code: str
    provider_name: str
    provider_type: str
    provider_category: str
    description: Optional[str]
    website_url: Optional[str]
    support_email: Optional[str]
    support_phone: Optional[str]
    documentation_url: Optional[str]
    base_url: Optional[str]
    auth_type: Optional[str]
    connection_timeout: int
    retry_attempts: int
    retry_delay: int
    config_schema: Optional[Dict[str, Any]]
    default_config: Optional[Dict[str, Any]]
    supported_operations: Optional[List[str]]
    provider_status: str
    certification_required: bool
    compliance_requirements: Optional[Dict[str, Any]]
    api_version: Optional[str]
    sdk_version: Optional[str]
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_by: Optional[UUID]
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Integration Configuration Schemas
# =====================================================

class IntegrationConfigurationCreate(BaseModel):
    provider_id: UUID
    config_name: str = Field(..., max_length=200)
    config_code: str = Field(..., max_length=50)
    environment: str
    endpoint_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, str]] = None
    provider_config: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, bool]] = None
    limits_config: Optional[Dict[str, Any]] = None
    priority: int = 1
    weight: int = 100
    is_primary: bool = False
    failover_config_id: Optional[UUID] = None
    ip_whitelist: Optional[List[str]] = None
    encryption_enabled: bool = True
    certificate_path: Optional[str] = None
    health_check_url: Optional[str] = None
    health_check_interval: int = 60
    created_by: Optional[UUID] = None


class IntegrationConfigurationUpdate(BaseModel):
    config_name: Optional[str] = None
    environment: Optional[str] = None
    endpoint_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, str]] = None
    provider_config: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, bool]] = None
    limits_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    weight: Optional[int] = None
    is_primary: Optional[bool] = None
    failover_config_id: Optional[UUID] = None
    ip_whitelist: Optional[List[str]] = None
    encryption_enabled: Optional[bool] = None
    certificate_path: Optional[str] = None
    health_check_url: Optional[str] = None
    health_check_interval: Optional[int] = None
    config_status: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[UUID] = None


class IntegrationConfigurationResponse(BaseModel):
    config_id: UUID
    provider_id: UUID
    config_name: str
    config_code: str
    environment: str
    endpoint_url: Optional[str]
    headers: Optional[Dict[str, str]]
    query_params: Optional[Dict[str, str]]
    provider_config: Optional[Dict[str, Any]]
    feature_flags: Optional[Dict[str, bool]]
    limits_config: Optional[Dict[str, Any]]
    priority: int
    weight: int
    is_primary: bool
    failover_config_id: Optional[UUID]
    ip_whitelist: Optional[List[str]]
    encryption_enabled: bool
    certificate_path: Optional[str]
    health_check_url: Optional[str]
    health_check_interval: int
    last_health_check: Optional[datetime]
    health_status: Optional[str]
    config_status: str
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_by: Optional[UUID]
    updated_at: datetime
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConfigurationApprove(BaseModel):
    approved_by: UUID


class ConfigurationHealthCheck(BaseModel):
    health_status: str
    last_health_check: datetime
    health_details: Optional[Dict[str, Any]] = None


# =====================================================
# Integration Endpoint Schemas
# =====================================================

class IntegrationEndpointCreate(BaseModel):
    config_id: UUID
    endpoint_name: str = Field(..., max_length=200)
    endpoint_code: str = Field(..., max_length=50)
    endpoint_path: str
    http_method: str
    operation_type: str
    description: Optional[str] = None
    request_format: Optional[str] = 'json'
    request_schema: Optional[Dict[str, Any]] = None
    request_template: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    response_format: Optional[str] = 'json'
    response_schema: Optional[Dict[str, Any]] = None
    success_codes: Optional[List[int]] = [200, 201, 202]
    error_mapping: Optional[Dict[str, str]] = None
    timeout_seconds: int = 30
    retry_enabled: bool = True
    max_retries: int = 3
    retry_strategy: Optional[str] = 'exponential'
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    request_transformer: Optional[str] = None
    response_transformer: Optional[str] = None
    log_request: bool = True
    log_response: bool = True
    mask_sensitive_data: bool = True


class IntegrationEndpointUpdate(BaseModel):
    endpoint_name: Optional[str] = None
    endpoint_path: Optional[str] = None
    http_method: Optional[str] = None
    operation_type: Optional[str] = None
    description: Optional[str] = None
    request_format: Optional[str] = None
    request_schema: Optional[Dict[str, Any]] = None
    request_template: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    response_format: Optional[str] = None
    response_schema: Optional[Dict[str, Any]] = None
    success_codes: Optional[List[int]] = None
    error_mapping: Optional[Dict[str, str]] = None
    timeout_seconds: Optional[int] = None
    retry_enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    retry_strategy: Optional[str] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    request_transformer: Optional[str] = None
    response_transformer: Optional[str] = None
    log_request: Optional[bool] = None
    log_response: Optional[bool] = None
    mask_sensitive_data: Optional[bool] = None
    is_active: Optional[bool] = None


class IntegrationEndpointResponse(BaseModel):
    endpoint_id: UUID
    config_id: UUID
    endpoint_name: str
    endpoint_code: str
    endpoint_path: str
    http_method: str
    operation_type: str
    description: Optional[str]
    request_format: Optional[str]
    request_schema: Optional[Dict[str, Any]]
    request_template: Optional[Dict[str, Any]]
    headers: Optional[Dict[str, str]]
    response_format: Optional[str]
    response_schema: Optional[Dict[str, Any]]
    success_codes: Optional[List[int]]
    error_mapping: Optional[Dict[str, str]]
    timeout_seconds: int
    retry_enabled: bool
    max_retries: int
    retry_strategy: Optional[str]
    rate_limit_per_minute: Optional[int]
    rate_limit_per_hour: Optional[int]
    rate_limit_per_day: Optional[int]
    request_transformer: Optional[str]
    response_transformer: Optional[str]
    log_request: bool
    log_response: bool
    mask_sensitive_data: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Integration Log Schemas
# =====================================================

class IntegrationLogCreate(BaseModel):
    endpoint_id: Optional[UUID] = None
    config_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None
    request_method: str
    request_url: str
    request_headers: Optional[Dict[str, str]] = None
    request_body: Optional[Dict[str, Any]] = None
    transaction_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    client_ip: Optional[str] = None
    server_ip: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None


class IntegrationLogResponse(BaseModel):
    log_id: UUID
    endpoint_id: Optional[UUID]
    config_id: Optional[UUID]
    provider_id: Optional[UUID]
    correlation_id: UUID
    request_timestamp: datetime
    request_method: str
    request_url: str
    request_headers: Optional[Dict[str, str]]
    request_body: Optional[Dict[str, Any]]
    response_timestamp: Optional[datetime]
    response_duration: Optional[int]
    response_status: Optional[int]
    response_headers: Optional[Dict[str, str]]
    response_body: Optional[Dict[str, Any]]
    transaction_id: Optional[UUID]
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    user_id: Optional[UUID]
    call_status: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    retry_attempt: int
    is_retry: bool
    parent_log_id: Optional[UUID]
    response_size: Optional[int]
    network_time: Optional[int]
    processing_time: Optional[int]
    client_ip: Optional[str]
    server_ip: Optional[str]
    additional_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# API Key Schemas
# =====================================================

class APIKeyCreate(BaseModel):
    key_name: str = Field(..., max_length=200)
    key_code: str = Field(..., max_length=50)
    config_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    key_type: str
    allowed_operations: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    rate_limits: Optional[Dict[str, int]] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    encryption_algorithm: Optional[str] = 'sha256'
    created_by: Optional[UUID] = None


class APIKeyUpdate(BaseModel):
    key_name: Optional[str] = None
    allowed_operations: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    rate_limits: Optional[Dict[str, int]] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    rotation_required: Optional[bool] = None
    rotation_due_date: Optional[date] = None
    updated_by: Optional[UUID] = None


class APIKeyResponse(BaseModel):
    key_id: UUID
    key_name: str
    key_code: str
    api_key: str  # This should be masked in actual responses
    config_id: Optional[UUID]
    provider_id: Optional[UUID]
    key_type: str
    allowed_operations: Optional[List[str]]
    ip_whitelist: Optional[List[str]]
    rate_limits: Optional[Dict[str, int]]
    valid_from: datetime
    valid_until: Optional[datetime]
    is_active: bool
    total_calls: int
    successful_calls: int
    failed_calls: int
    last_used_at: Optional[datetime]
    last_used_ip: Optional[str]
    encryption_algorithm: Optional[str]
    rotation_required: bool
    rotation_due_date: Optional[date]
    created_by: Optional[UUID]
    created_at: datetime
    updated_by: Optional[UUID]
    updated_at: datetime
    revoked_at: Optional[datetime]
    revoked_by: Optional[UUID]
    revocation_reason: Optional[str]

    class Config:
        from_attributes = True


class APIKeyRevoke(BaseModel):
    revoked_by: UUID
    revocation_reason: str


class APIKeyRotate(BaseModel):
    rotated_by: UUID


# =====================================================
# Webhook Schemas
# =====================================================

class WebhookCreate(BaseModel):
    webhook_name: str = Field(..., max_length=200)
    webhook_code: str = Field(..., max_length=50)
    target_url: str
    http_method: str = 'POST'
    auth_type: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    custom_headers: Optional[Dict[str, str]] = None
    payload_template: Optional[Dict[str, Any]] = None
    content_type: str = 'application/json'
    event_types: List[str]
    event_filters: Optional[Dict[str, Any]] = None
    delivery_timeout: int = 30
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 60
    signature_enabled: bool = True
    signature_algorithm: str = 'sha256'
    signature_header: str = 'X-Webhook-Signature'
    secret_key: Optional[str] = None
    created_by: Optional[UUID] = None


class WebhookUpdate(BaseModel):
    webhook_name: Optional[str] = None
    target_url: Optional[str] = None
    http_method: Optional[str] = None
    auth_type: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    custom_headers: Optional[Dict[str, str]] = None
    payload_template: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    event_types: Optional[List[str]] = None
    event_filters: Optional[Dict[str, Any]] = None
    delivery_timeout: Optional[int] = None
    retry_enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[int] = None
    signature_enabled: Optional[bool] = None
    signature_algorithm: Optional[str] = None
    signature_header: Optional[str] = None
    secret_key: Optional[str] = None
    webhook_status: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[UUID] = None


class WebhookResponse(BaseModel):
    webhook_id: UUID
    webhook_name: str
    webhook_code: str
    target_url: str
    http_method: str
    auth_type: Optional[str]
    custom_headers: Optional[Dict[str, str]]
    payload_template: Optional[Dict[str, Any]]
    content_type: str
    event_types: List[str]
    event_filters: Optional[Dict[str, Any]]
    delivery_timeout: int
    retry_enabled: bool
    max_retries: int
    retry_delay: int
    signature_enabled: bool
    signature_algorithm: str
    signature_header: str
    webhook_status: str
    last_triggered_at: Optional[datetime]
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    is_active: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_by: Optional[UUID]
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Webhook Delivery Schemas
# =====================================================

class WebhookDeliveryCreate(BaseModel):
    webhook_id: UUID
    event_type: str
    event_payload: Dict[str, Any]


class WebhookDeliveryResponse(BaseModel):
    delivery_id: UUID
    webhook_id: UUID
    event_id: UUID
    event_type: str
    event_timestamp: datetime
    event_payload: Dict[str, Any]
    attempt_number: int
    attempted_at: datetime
    request_url: Optional[str]
    request_method: Optional[str]
    request_headers: Optional[Dict[str, str]]
    request_body: Optional[Dict[str, Any]]
    signature: Optional[str]
    response_status: Optional[int]
    response_headers: Optional[Dict[str, str]]
    response_body: Optional[Dict[str, Any]]
    response_time: Optional[int]
    delivery_status: str
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    next_retry_at: Optional[datetime]
    max_retries_reached: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Message Queue Schemas
# =====================================================

class MessageQueueCreate(BaseModel):
    message_type: str
    priority: int = 5
    target_config_id: Optional[UUID] = None
    target_endpoint_id: Optional[UUID] = None
    message_payload: Dict[str, Any]
    message_headers: Optional[Dict[str, str]] = None
    correlation_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    max_retries: int = 3


class MessageQueueUpdate(BaseModel):
    status: Optional[str] = None
    picked_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    retry_count: Optional[int] = None
    next_retry_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class MessageQueueResponse(BaseModel):
    message_id: UUID
    message_type: str
    priority: int
    target_config_id: Optional[UUID]
    target_endpoint_id: Optional[UUID]
    message_payload: Dict[str, Any]
    message_headers: Optional[Dict[str, str]]
    correlation_id: Optional[UUID]
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    user_id: Optional[UUID]
    scheduled_at: datetime
    expires_at: Optional[datetime]
    status: str
    picked_at: Optional[datetime]
    processed_at: Optional[datetime]
    worker_id: Optional[str]
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Statistics Schemas
# =====================================================

class IntegrationStatistics(BaseModel):
    total_providers: int
    active_providers: int
    total_configurations: int
    active_configurations: int
    total_endpoints: int
    total_calls_today: int
    successful_calls_today: int
    failed_calls_today: int
    avg_response_time: float
    total_webhooks: int
    active_webhooks: int
    pending_messages: int


class ProviderPerformance(BaseModel):
    provider_id: UUID
    provider_code: str
    provider_name: str
    provider_type: str
    config_count: int
    endpoint_count: int
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_response_time: float
    last_call_at: Optional[datetime]


class WebhookHealth(BaseModel):
    webhook_id: UUID
    webhook_code: str
    webhook_name: str
    webhook_status: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    last_triggered_at: Optional[datetime]
    pending_deliveries: int
    retrying_deliveries: int

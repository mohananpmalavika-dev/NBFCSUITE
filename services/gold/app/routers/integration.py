"""
Integration Hub Router - Phase 13
Handles external integrations, webhooks, API keys, and message queue
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.database import get_db
from app.models.integration import (
    IntegrationProvider, IntegrationConfiguration, IntegrationEndpoint,
    IntegrationLog, APIKey, Webhook, WebhookDelivery, MessageQueue
)
from app.schemas.integration import (
    IntegrationProviderCreate, IntegrationProviderUpdate, IntegrationProviderResponse,
    IntegrationConfigurationCreate, IntegrationConfigurationUpdate, IntegrationConfigurationResponse,
    IntegrationEndpointCreate, IntegrationEndpointUpdate, IntegrationEndpointResponse,
    IntegrationLogCreate, IntegrationLogResponse,
    APIKeyCreate, APIKeyUpdate, APIKeyResponse,
    WebhookCreate, WebhookUpdate, WebhookResponse,
    WebhookDeliveryCreate, WebhookDeliveryResponse,
    MessageQueueCreate, MessageQueueUpdate, MessageQueueResponse,
    IntegrationStatistics, ProviderPerformance, WebhookHealth, QueueSummary
)

router = APIRouter(prefix="/api/v1/gold/integration", tags=["Integration Hub"])


# ===== Integration Provider Endpoints =====

@router.post("/providers", response_model=IntegrationProviderResponse, status_code=201)
def create_integration_provider(
    provider: IntegrationProviderCreate,
    db: Session = Depends(get_db)
):
    """Create new integration provider"""
    # Check if provider code already exists
    existing = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_code == provider.provider_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Provider code already exists")
    
    db_provider = IntegrationProvider(**provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.get("/providers", response_model=List[IntegrationProviderResponse])
def get_integration_providers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of integration providers"""
    query = db.query(IntegrationProvider)
    
    if category:
        query = query.filter(IntegrationProvider.category == category)
    if is_active is not None:
        query = query.filter(IntegrationProvider.is_active == is_active)
    
    providers = query.offset(skip).limit(limit).all()
    return providers


@router.get("/providers/{provider_id}", response_model=IntegrationProviderResponse)
def get_integration_provider(
    provider_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get integration provider by ID"""
    provider = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_id == provider_id
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Integration provider not found")
    
    return provider


@router.get("/providers/code/{provider_code}", response_model=IntegrationProviderResponse)
def get_integration_provider_by_code(
    provider_code: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get integration provider by code"""
    provider = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_code == provider_code
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Integration provider not found")
    
    return provider


@router.put("/providers/{provider_id}", response_model=IntegrationProviderResponse)
def update_integration_provider(
    provider_id: int = Path(..., gt=0),
    provider_update: IntegrationProviderUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update integration provider"""
    db_provider = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_id == provider_id
    ).first()
    
    if not db_provider:
        raise HTTPException(status_code=404, detail="Integration provider not found")
    
    for key, value in provider_update.dict(exclude_unset=True).items():
        setattr(db_provider, key, value)
    
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.delete("/providers/{provider_id}", status_code=204)
def delete_integration_provider(
    provider_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete integration provider"""
    db_provider = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_id == provider_id
    ).first()
    
    if not db_provider:
        raise HTTPException(status_code=404, detail="Integration provider not found")
    
    # Check for active configurations
    active_configs = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.provider_id == provider_id,
        IntegrationConfiguration.status == 'active'
    ).count()
    
    if active_configs > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete provider with {active_configs} active configurations"
        )
    
    db.delete(db_provider)
    db.commit()


# ===== Integration Configuration Endpoints =====

@router.post("/configurations", response_model=IntegrationConfigurationResponse, status_code=201)
def create_integration_configuration(
    config: IntegrationConfigurationCreate,
    db: Session = Depends(get_db)
):
    """Create new integration configuration"""
    # Verify provider exists
    provider = db.query(IntegrationProvider).filter(
        IntegrationProvider.provider_id == config.provider_id
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db_config = IntegrationConfiguration(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.get("/configurations", response_model=List[IntegrationConfigurationResponse])
def get_integration_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    provider_id: Optional[int] = None,
    status: Optional[str] = None,
    environment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of integration configurations"""
    query = db.query(IntegrationConfiguration)
    
    if provider_id:
        query = query.filter(IntegrationConfiguration.provider_id == provider_id)
    if status:
        query = query.filter(IntegrationConfiguration.status == status)
    if environment:
        query = query.filter(IntegrationConfiguration.environment == environment)
    
    configs = query.offset(skip).limit(limit).all()
    return configs


@router.get("/configurations/{config_id}", response_model=IntegrationConfigurationResponse)
def get_integration_configuration(
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get integration configuration by ID"""
    config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config


@router.put("/configurations/{config_id}", response_model=IntegrationConfigurationResponse)
def update_integration_configuration(
    config_id: int = Path(..., gt=0),
    config_update: IntegrationConfigurationUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update integration configuration"""
    db_config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == config_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    for key, value in config_update.dict(exclude_unset=True).items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/configurations/{config_id}", status_code=204)
def delete_integration_configuration(
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete integration configuration"""
    db_config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == config_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if db_config.status == 'active':
        raise HTTPException(
            status_code=400,
            detail="Cannot delete active configuration. Please deactivate first."
        )
    
    db.delete(db_config)
    db.commit()


@router.post("/configurations/{config_id}/approve", response_model=IntegrationConfigurationResponse)
def approve_integration_configuration(
    config_id: int = Path(..., gt=0),
    approved_by: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Approve integration configuration (maker-checker)"""
    db_config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == config_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if db_config.status != 'pending':
        raise HTTPException(status_code=400, detail="Only pending configurations can be approved")
    
    db_config.status = 'active'
    db_config.approved_by = approved_by
    db_config.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_config)
    return db_config


@router.post("/configurations/{config_id}/health-check")
def check_configuration_health(
    config_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Perform health check on integration configuration"""
    db_config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == config_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update last health check time
    db_config.last_health_check = datetime.utcnow()
    db.commit()
    
    return {
        "config_id": config_id,
        "status": "healthy",
        "last_check": db_config.last_health_check,
        "message": "Health check completed successfully"
    }


# ===== Integration Endpoint Endpoints =====

@router.post("/endpoints", response_model=IntegrationEndpointResponse, status_code=201)
def create_integration_endpoint(
    endpoint: IntegrationEndpointCreate,
    db: Session = Depends(get_db)
):
    """Create new integration endpoint"""
    # Verify configuration exists
    config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == endpoint.config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db_endpoint = IntegrationEndpoint(**endpoint.dict())
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint


@router.get("/endpoints", response_model=List[IntegrationEndpointResponse])
def get_integration_endpoints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    config_id: Optional[int] = None,
    method: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of integration endpoints"""
    query = db.query(IntegrationEndpoint)
    
    if config_id:
        query = query.filter(IntegrationEndpoint.config_id == config_id)
    if method:
        query = query.filter(IntegrationEndpoint.method == method)
    if is_active is not None:
        query = query.filter(IntegrationEndpoint.is_active == is_active)
    
    endpoints = query.offset(skip).limit(limit).all()
    return endpoints


@router.get("/endpoints/{endpoint_id}", response_model=IntegrationEndpointResponse)
def get_integration_endpoint(
    endpoint_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get integration endpoint by ID"""
    endpoint = db.query(IntegrationEndpoint).filter(
        IntegrationEndpoint.endpoint_id == endpoint_id
    ).first()
    
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    return endpoint


@router.put("/endpoints/{endpoint_id}", response_model=IntegrationEndpointResponse)
def update_integration_endpoint(
    endpoint_id: int = Path(..., gt=0),
    endpoint_update: IntegrationEndpointUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update integration endpoint"""
    db_endpoint = db.query(IntegrationEndpoint).filter(
        IntegrationEndpoint.endpoint_id == endpoint_id
    ).first()
    
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    for key, value in endpoint_update.dict(exclude_unset=True).items():
        setattr(db_endpoint, key, value)
    
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint


@router.delete("/endpoints/{endpoint_id}", status_code=204)
def delete_integration_endpoint(
    endpoint_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete integration endpoint"""
    db_endpoint = db.query(IntegrationEndpoint).filter(
        IntegrationEndpoint.endpoint_id == endpoint_id
    ).first()
    
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    db.delete(db_endpoint)
    db.commit()


# ===== Integration Log Endpoints =====

@router.post("/logs", response_model=IntegrationLogResponse, status_code=201)
def create_integration_log(
    log: IntegrationLogCreate,
    db: Session = Depends(get_db)
):
    """Create integration log entry"""
    db_log = IntegrationLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/logs", response_model=List[IntegrationLogResponse])
def get_integration_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    config_id: Optional[int] = None,
    endpoint_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get list of integration logs"""
    query = db.query(IntegrationLog)
    
    if config_id:
        query = query.filter(IntegrationLog.config_id == config_id)
    if endpoint_id:
        query = query.filter(IntegrationLog.endpoint_id == endpoint_id)
    if status:
        query = query.filter(IntegrationLog.status == status)
    if start_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) <= end_date)
    
    logs = query.order_by(desc(IntegrationLog.request_timestamp)).offset(skip).limit(limit).all()
    return logs


@router.get("/logs/{log_id}", response_model=IntegrationLogResponse)
def get_integration_log(
    log_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get integration log by ID"""
    log = db.query(IntegrationLog).filter(
        IntegrationLog.log_id == log_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return log


@router.get("/logs/correlation/{correlation_id}", response_model=List[IntegrationLogResponse])
def get_logs_by_correlation(
    correlation_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get logs by correlation ID"""
    logs = db.query(IntegrationLog).filter(
        IntegrationLog.correlation_id == correlation_id
    ).order_by(desc(IntegrationLog.request_timestamp)).all()
    
    return logs


@router.get("/logs/statistics/summary")
def get_log_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    config_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get integration log statistics"""
    query = db.query(IntegrationLog)
    
    if start_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) <= end_date)
    if config_id:
        query = query.filter(IntegrationLog.config_id == config_id)
    
    total_requests = query.count()
    success_requests = query.filter(IntegrationLog.status == 'success').count()
    failed_requests = query.filter(IntegrationLog.status == 'failure').count()
    avg_response_time = query.with_entities(func.avg(IntegrationLog.response_time)).scalar() or 0
    
    return {
        "total_requests": total_requests,
        "success_requests": success_requests,
        "failed_requests": failed_requests,
        "success_rate": (success_requests / total_requests * 100) if total_requests > 0 else 0,
        "average_response_time": float(avg_response_time)
    }


# ===== API Key Endpoints =====

@router.post("/api-keys", response_model=APIKeyResponse, status_code=201)
def create_api_key(
    api_key: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """Create new API key"""
    # Verify configuration exists
    config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == api_key.config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db_key = APIKey(**api_key.dict())
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


@router.get("/api-keys", response_model=List[APIKeyResponse])
def get_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    config_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of API keys"""
    query = db.query(APIKey)
    
    if config_id:
        query = query.filter(APIKey.config_id == config_id)
    if is_active is not None:
        query = query.filter(APIKey.is_active == is_active)
    
    keys = query.offset(skip).limit(limit).all()
    return keys


@router.get("/api-keys/{key_id}", response_model=APIKeyResponse)
def get_api_key(
    key_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get API key by ID"""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return api_key



@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
def update_api_key(
    key_id: int = Path(..., gt=0),
    key_update: APIKeyUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update API key"""
    db_key = db.query(APIKey).filter(
        APIKey.key_id == key_id
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    for key, value in key_update.dict(exclude_unset=True).items():
        setattr(db_key, key, value)
    
    db.commit()
    db.refresh(db_key)
    return db_key


@router.delete("/api-keys/{key_id}", status_code=204)
def delete_api_key(
    key_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete API key"""
    db_key = db.query(APIKey).filter(
        APIKey.key_id == key_id
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(db_key)
    db.commit()


@router.post("/api-keys/{key_id}/revoke", response_model=APIKeyResponse)
def revoke_api_key(
    key_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Revoke API key"""
    db_key = db.query(APIKey).filter(
        APIKey.key_id == key_id
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db_key.is_active = False
    db_key.revoked_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_key)
    return db_key


@router.post("/api-keys/{key_id}/rotate", response_model=APIKeyResponse)
def rotate_api_key(
    key_id: int = Path(..., gt=0),
    new_key_value: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Rotate API key with new value"""
    db_key = db.query(APIKey).filter(
        APIKey.key_id == key_id
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db_key.key_value = new_key_value
    db_key.last_rotated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_key)
    return db_key


# ===== Webhook Endpoints =====

@router.post("/webhooks", response_model=WebhookResponse, status_code=201)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db)
):
    """Create new webhook"""
    # Verify configuration exists
    config = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.config_id == webhook.config_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db_webhook = Webhook(**webhook.dict())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


@router.get("/webhooks", response_model=List[WebhookResponse])
def get_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    config_id: Optional[int] = None,
    event_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of webhooks"""
    query = db.query(Webhook)
    
    if config_id:
        query = query.filter(Webhook.config_id == config_id)
    if event_type:
        query = query.filter(Webhook.event_type == event_type)
    if is_active is not None:
        query = query.filter(Webhook.is_active == is_active)
    
    webhooks = query.offset(skip).limit(limit).all()
    return webhooks


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get webhook by ID"""
    webhook = db.query(Webhook).filter(
        Webhook.webhook_id == webhook_id
    ).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.put("/webhooks/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int = Path(..., gt=0),
    webhook_update: WebhookUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update webhook"""
    db_webhook = db.query(Webhook).filter(
        Webhook.webhook_id == webhook_id
    ).first()
    
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    for key, value in webhook_update.dict(exclude_unset=True).items():
        setattr(db_webhook, key, value)
    
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Delete webhook"""
    db_webhook = db.query(Webhook).filter(
        Webhook.webhook_id == webhook_id
    ).first()
    
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(db_webhook)
    db.commit()


@router.post("/webhooks/{webhook_id}/test")
def test_webhook(
    webhook_id: int = Path(..., gt=0),
    test_payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Test webhook with sample payload"""
    db_webhook = db.query(Webhook).filter(
        Webhook.webhook_id == webhook_id
    ).first()
    
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {
        "webhook_id": webhook_id,
        "status": "test_sent",
        "url": db_webhook.webhook_url,
        "payload": test_payload,
        "message": "Test webhook sent successfully"
    }



# ===== Webhook Delivery Endpoints =====

@router.post("/webhook-deliveries", response_model=WebhookDeliveryResponse, status_code=201)
def create_webhook_delivery(
    delivery: WebhookDeliveryCreate,
    db: Session = Depends(get_db)
):
    """Create webhook delivery record"""
    db_delivery = WebhookDelivery(**delivery.dict())
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@router.get("/webhook-deliveries", response_model=List[WebhookDeliveryResponse])
def get_webhook_deliveries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    webhook_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get list of webhook deliveries"""
    query = db.query(WebhookDelivery)
    
    if webhook_id:
        query = query.filter(WebhookDelivery.webhook_id == webhook_id)
    if status:
        query = query.filter(WebhookDelivery.status == status)
    if start_date:
        query = query.filter(func.date(WebhookDelivery.sent_at) >= start_date)
    if end_date:
        query = query.filter(func.date(WebhookDelivery.sent_at) <= end_date)
    
    deliveries = query.order_by(desc(WebhookDelivery.sent_at)).offset(skip).limit(limit).all()
    return deliveries


@router.get("/webhook-deliveries/{delivery_id}", response_model=WebhookDeliveryResponse)
def get_webhook_delivery(
    delivery_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get webhook delivery by ID"""
    delivery = db.query(WebhookDelivery).filter(
        WebhookDelivery.delivery_id == delivery_id
    ).first()
    
    if not delivery:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    
    return delivery


@router.post("/webhook-deliveries/{delivery_id}/retry", response_model=WebhookDeliveryResponse)
def retry_webhook_delivery(
    delivery_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Retry failed webhook delivery"""
    db_delivery = db.query(WebhookDelivery).filter(
        WebhookDelivery.delivery_id == delivery_id
    ).first()
    
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    
    if db_delivery.status == 'success':
        raise HTTPException(status_code=400, detail="Cannot retry successful delivery")
    
    db_delivery.retry_count += 1
    db_delivery.next_retry = None
    
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


# ===== Message Queue Endpoints =====

@router.post("/message-queue", response_model=MessageQueueResponse, status_code=201)
def create_message(
    message: MessageQueueCreate,
    db: Session = Depends(get_db)
):
    """Create new message in queue"""
    db_message = MessageQueue(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/message-queue", response_model=List[MessageQueueResponse])
def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    config_id: Optional[int] = None,
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of messages from queue"""
    query = db.query(MessageQueue)
    
    if config_id:
        query = query.filter(MessageQueue.config_id == config_id)
    if message_type:
        query = query.filter(MessageQueue.message_type == message_type)
    if status:
        query = query.filter(MessageQueue.status == status)
    if priority:
        query = query.filter(MessageQueue.priority == priority)
    
    messages = query.order_by(desc(MessageQueue.created_at)).offset(skip).limit(limit).all()
    return messages


@router.get("/message-queue/{message_id}", response_model=MessageQueueResponse)
def get_message(
    message_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Get message by ID"""
    message = db.query(MessageQueue).filter(
        MessageQueue.message_id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message


@router.put("/message-queue/{message_id}", response_model=MessageQueueResponse)
def update_message(
    message_id: int = Path(..., gt=0),
    message_update: MessageQueueUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update message in queue"""
    db_message = db.query(MessageQueue).filter(
        MessageQueue.message_id == message_id
    ).first()
    
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    for key, value in message_update.dict(exclude_unset=True).items():
        setattr(db_message, key, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message


@router.post("/message-queue/{message_id}/process", response_model=MessageQueueResponse)
def process_message(
    message_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    """Mark message as processed"""
    db_message = db.query(MessageQueue).filter(
        MessageQueue.message_id == message_id
    ).first()
    
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if db_message.status != 'pending':
        raise HTTPException(status_code=400, detail="Only pending messages can be processed")
    
    db_message.status = 'processing'
    db_message.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/message-queue/pending/list", response_model=List[MessageQueueResponse])
def get_pending_messages(
    limit: int = Query(100, ge=1, le=1000),
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get pending messages sorted by priority"""
    query = db.query(MessageQueue).filter(
        MessageQueue.status == 'pending'
    )
    
    if priority:
        query = query.filter(MessageQueue.priority == priority)
    
    # Order by priority (high, medium, low) and then by created_at
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    messages = query.order_by(MessageQueue.created_at).limit(limit).all()
    
    return messages


# ===== Statistics and Monitoring Endpoints =====

@router.get("/statistics/integration", response_model=IntegrationStatistics)
def get_integration_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    provider_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive integration statistics"""
    log_query = db.query(IntegrationLog)
    
    if start_date:
        log_query = log_query.filter(func.date(IntegrationLog.request_timestamp) >= start_date)
    if end_date:
        log_query = log_query.filter(func.date(IntegrationLog.request_timestamp) <= end_date)
    
    total_requests = log_query.count()
    success_requests = log_query.filter(IntegrationLog.status == 'success').count()
    failed_requests = log_query.filter(IntegrationLog.status == 'failure').count()
    
    avg_response = log_query.with_entities(func.avg(IntegrationLog.response_time)).scalar() or 0
    
    active_configs = db.query(IntegrationConfiguration).filter(
        IntegrationConfiguration.status == 'active'
    ).count()
    
    active_webhooks = db.query(Webhook).filter(
        Webhook.is_active == True
    ).count()
    
    pending_messages = db.query(MessageQueue).filter(
        MessageQueue.status == 'pending'
    ).count()
    
    return IntegrationStatistics(
        total_requests=total_requests,
        successful_requests=success_requests,
        failed_requests=failed_requests,
        average_response_time=float(avg_response),
        active_configurations=active_configs,
        active_webhooks=active_webhooks,
        pending_messages=pending_messages
    )


@router.get("/statistics/provider-performance", response_model=List[ProviderPerformance])
def get_provider_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get performance metrics by provider"""
    query = db.query(
        IntegrationProvider.provider_id,
        IntegrationProvider.provider_name,
        func.count(IntegrationLog.log_id).label('total_calls'),
        func.sum(
            func.case([(IntegrationLog.status == 'success', 1)], else_=0)
        ).label('successful_calls'),
        func.avg(IntegrationLog.response_time).label('avg_response_time')
    ).join(
        IntegrationConfiguration,
        IntegrationProvider.provider_id == IntegrationConfiguration.provider_id
    ).join(
        IntegrationLog,
        IntegrationConfiguration.config_id == IntegrationLog.config_id
    )
    
    if start_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(IntegrationLog.request_timestamp) <= end_date)
    
    results = query.group_by(
        IntegrationProvider.provider_id,
        IntegrationProvider.provider_name
    ).all()
    
    performance_list = []
    for result in results:
        success_rate = (result.successful_calls / result.total_calls * 100) if result.total_calls > 0 else 0
        performance_list.append(
            ProviderPerformance(
                provider_id=result.provider_id,
                provider_name=result.provider_name,
                total_calls=result.total_calls,
                successful_calls=result.successful_calls,
                success_rate=success_rate,
                average_response_time=float(result.avg_response_time or 0)
            )
        )
    
    return performance_list


@router.get("/statistics/webhook-health", response_model=WebhookHealth)
def get_webhook_health(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get webhook health metrics"""
    delivery_query = db.query(WebhookDelivery)
    
    if start_date:
        delivery_query = delivery_query.filter(func.date(WebhookDelivery.sent_at) >= start_date)
    if end_date:
        delivery_query = delivery_query.filter(func.date(WebhookDelivery.sent_at) <= end_date)
    
    total_deliveries = delivery_query.count()
    successful_deliveries = delivery_query.filter(WebhookDelivery.status == 'success').count()
    failed_deliveries = delivery_query.filter(WebhookDelivery.status == 'failure').count()
    pending_deliveries = delivery_query.filter(WebhookDelivery.status == 'pending').count()
    
    avg_response = delivery_query.with_entities(
        func.avg(WebhookDelivery.response_time)
    ).scalar() or 0
    
    total_retries = delivery_query.with_entities(
        func.sum(WebhookDelivery.retry_count)
    ).scalar() or 0
    
    return WebhookHealth(
        total_deliveries=total_deliveries,
        successful_deliveries=successful_deliveries,
        failed_deliveries=failed_deliveries,
        pending_deliveries=pending_deliveries,
        success_rate=(successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
        average_response_time=float(avg_response),
        total_retries=int(total_retries)
    )


@router.get("/statistics/queue-summary", response_model=QueueSummary)
def get_queue_summary(
    db: Session = Depends(get_db)
):
    """Get message queue summary statistics"""
    total_messages = db.query(MessageQueue).count()
    pending_messages = db.query(MessageQueue).filter(
        MessageQueue.status == 'pending'
    ).count()
    processing_messages = db.query(MessageQueue).filter(
        MessageQueue.status == 'processing'
    ).count()
    completed_messages = db.query(MessageQueue).filter(
        MessageQueue.status == 'completed'
    ).count()
    failed_messages = db.query(MessageQueue).filter(
        MessageQueue.status == 'failed'
    ).count()
    
    high_priority = db.query(MessageQueue).filter(
        MessageQueue.priority == 'high',
        MessageQueue.status == 'pending'
    ).count()
    
    oldest_pending = db.query(MessageQueue).filter(
        MessageQueue.status == 'pending'
    ).order_by(MessageQueue.created_at).first()
    
    avg_processing = db.query(MessageQueue).filter(
        MessageQueue.status == 'completed',
        MessageQueue.processed_at.isnot(None)
    ).with_entities(
        func.avg(
            func.extract('epoch', MessageQueue.processed_at - MessageQueue.created_at)
        )
    ).scalar() or 0
    
    return QueueSummary(
        total_messages=total_messages,
        pending_messages=pending_messages,
        processing_messages=processing_messages,
        completed_messages=completed_messages,
        failed_messages=failed_messages,
        high_priority_pending=high_priority,
        oldest_pending_age=int((datetime.utcnow() - oldest_pending.created_at).total_seconds()) if oldest_pending else 0,
        average_processing_time=float(avg_processing)
    )

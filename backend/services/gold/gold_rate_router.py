"""
Gold Rate Router
API endpoints for gold rate management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.gold.gold_rate_service import GoldRateService
from backend.services.gold.schemas import (
    GoldRateCreateRequest,
    GoldRateUpdateRequest,
    GoldRateHistoryResponse,
    CurrentGoldRatesResponse
)

router = APIRouter(prefix="/gold-rates", tags=["Gold Rates"])


@router.get("/current", response_model=CurrentGoldRatesResponse)
async def get_current_gold_rates(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get currently active gold rates"""
    service = GoldRateService(db, tenant_id)
    rates = service.get_current_rates()
    
    if not rates:
        raise HTTPException(status_code=404, detail="No current gold rates found")
    
    return CurrentGoldRatesResponse(
        gold_rate_24k=rates.gold_rate_24k,
        gold_rate_22k=rates.gold_rate_22k,
        gold_rate_18k=rates.gold_rate_18k,
        silver_rate=rates.silver_rate,
        rate_date=rates.rate_date,
        source=rates.source,
        market_name=rates.market_name,
        last_updated=rates.fetched_at or rates.created_at
    )


@router.post("/update-live")
async def update_live_gold_rates(
    source: str = Query(default="IBJA", description="Rate source: IBJA, MCX, MetalAPI"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Fetch and update live gold rates from external API"""
    service = GoldRateService(db, tenant_id)
    rate = await service.update_live_rates(source)
    return {"message": "Gold rates updated successfully", "rate": GoldRateHistoryResponse.from_orm(rate)}


@router.post("/", response_model=GoldRateHistoryResponse)
async def create_manual_gold_rates(
    rate_data: GoldRateCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create manual gold rate entry"""
    service = GoldRateService(db, tenant_id)
    rate = service.create_manual_rates(rate_data)
    return GoldRateHistoryResponse.from_orm(rate)


@router.put("/{rate_id}", response_model=GoldRateHistoryResponse)
async def update_gold_rates(
    rate_id: str,
    rate_data: GoldRateUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update existing gold rates"""
    service = GoldRateService(db, tenant_id)
    rate = service.update_rates(rate_id, rate_data)
    return GoldRateHistoryResponse.from_orm(rate)


@router.get("/{rate_id}", response_model=GoldRateHistoryResponse)
async def get_gold_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get gold rate by ID"""
    service = GoldRateService(db, tenant_id)
    rate = service.get_rate_by_id(rate_id)
    
    if not rate:
        raise HTTPException(status_code=404, detail="Gold rate not found")
    
    return GoldRateHistoryResponse.from_orm(rate)


@router.get("/", response_model=List[GoldRateHistoryResponse])
async def list_gold_rates_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get historical gold rates"""
    service = GoldRateService(db, tenant_id)
    rates = service.get_rates_history(start_date, end_date, source, limit)
    return [GoldRateHistoryResponse.from_orm(rate) for rate in rates]


@router.get("/statistics/summary")
async def get_gold_rate_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get gold rate statistics for a period"""
    service = GoldRateService(db, tenant_id)
    stats = service.get_rate_statistics(start_date, end_date)
    return stats


@router.get("/calculate/value")
async def calculate_gold_value(
    weight_grams: float = Query(..., gt=0, description="Gold weight in grams"),
    karat: int = Query(..., ge=1, le=24, description="Gold purity in karats"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate gold value based on weight and purity"""
    from decimal import Decimal
    service = GoldRateService(db, tenant_id)
    value = service.calculate_gold_value(Decimal(str(weight_grams)), karat)
    
    current_rates = service.get_current_rates()
    rate = service.get_rate_by_karat(karat)
    
    return {
        "weight_grams": weight_grams,
        "karat": karat,
        "rate_per_gram": float(rate),
        "total_value": float(value),
        "rate_source": current_rates.source if current_rates else None,
        "rate_date": current_rates.rate_date if current_rates else None
    }


@router.delete("/{rate_id}")
async def delete_gold_rate(
    rate_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Delete/deactivate gold rate"""
    service = GoldRateService(db, tenant_id)
    service.delete_rate(rate_id)
    return {"message": "Gold rate deactivated successfully"}

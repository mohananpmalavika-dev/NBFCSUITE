"""
Gold Rate Service
Manages live gold rates with API integration and caching
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import httpx
import json
from fastapi import HTTPException

from backend.shared.database.gold_loan_models import GoldRateHistory
from backend.services.gold.schemas import (
    GoldRateHistoryResponse,
    GoldRateCreateRequest,
    GoldRateUpdateRequest,
    CurrentGoldRatesResponse
)


class GoldRateService:
    """Service for managing gold rates"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.cache_duration_minutes = 30  # Cache rates for 30 minutes
    
    async def fetch_live_gold_rates(self, source: str = "IBJA") -> Dict[str, Decimal]:
        """
        Fetch live gold rates from external API
        Supports multiple sources: IBJA, MCX, MetalAPI
        """
        try:
            if source == "IBJA":
                return await self._fetch_ibja_rates()
            elif source == "MCX":
                return await self._fetch_mcx_rates()
            elif source == "MetalAPI":
                return await self._fetch_metal_api_rates()
            else:
                raise ValueError(f"Unsupported gold rate source: {source}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch live gold rates: {str(e)}"
            )
    
    async def _fetch_ibja_rates(self) -> Dict[str, Decimal]:
        """
        Fetch rates from India Bullion & Jewellers Association
        Note: This is a placeholder - actual API integration requires API key
        """
        # Placeholder implementation - replace with actual API
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Example API endpoint (replace with actual IBJA API)
                # response = await client.get(
                #     "https://api.ibja.co/gold-rates",
                #     headers={"Authorization": f"Bearer {API_KEY}"}
                # )
                # data = response.json()
                
                # For now, return mock data
                # In production, parse actual API response
                return {
                    "gold_rate_24k": Decimal("6500.00"),
                    "gold_rate_22k": Decimal("5958.33"),
                    "gold_rate_18k": Decimal("4875.00"),
                    "silver_rate": Decimal("75.00"),
                    "source": "IBJA",
                    "market_name": "Mumbai"
                }
            except httpx.HTTPError as e:
                raise Exception(f"IBJA API error: {str(e)}")
    
    async def _fetch_mcx_rates(self) -> Dict[str, Decimal]:
        """
        Fetch rates from Multi Commodity Exchange
        """
        # Placeholder implementation
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Example implementation
                return {
                    "gold_rate_24k": Decimal("6480.00"),
                    "gold_rate_22k": Decimal("5940.00"),
                    "gold_rate_18k": Decimal("4860.00"),
                    "silver_rate": Decimal("74.50"),
                    "source": "MCX",
                    "market_name": "India"
                }
            except httpx.HTTPError as e:
                raise Exception(f"MCX API error: {str(e)}")
    
    async def _fetch_metal_api_rates(self) -> Dict[str, Decimal]:
        """
        Fetch rates from MetalsAPI or similar service
        """
        # Placeholder implementation
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Example implementation
                # response = await client.get(
                #     "https://metals-api.com/api/latest",
                #     params={"access_key": API_KEY, "base": "INR", "symbols": "XAU"}
                # )
                
                return {
                    "gold_rate_24k": Decimal("6520.00"),
                    "gold_rate_22k": Decimal("5976.67"),
                    "gold_rate_18k": Decimal("4890.00"),
                    "silver_rate": Decimal("75.50"),
                    "source": "MetalAPI",
                    "market_name": "International"
                }
            except httpx.HTTPError as e:
                raise Exception(f"MetalAPI error: {str(e)}")
    
    def get_current_rates(self) -> Optional[GoldRateHistory]:
        """Get currently active gold rates"""
        return self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.tenant_id == self.tenant_id,
                GoldRateHistory.is_current == True,
                GoldRateHistory.is_active == True
            )
        ).first()
    
    def get_current_rates_with_cache(self) -> Optional[GoldRateHistory]:
        """
        Get current rates with cache validation
        Fetches new rates if cache is expired
        """
        current_rates = self.get_current_rates()
        
        if current_rates:
            # Check if cache is still valid
            cache_expiry = current_rates.fetched_at + timedelta(minutes=self.cache_duration_minutes)
            if datetime.utcnow() < cache_expiry:
                return current_rates
        
        return None
    
    async def update_live_rates(self, source: str = "IBJA") -> GoldRateHistory:
        """
        Fetch and update live gold rates
        """
        # Fetch live rates
        rate_data = await self.fetch_live_gold_rates(source)
        
        # Deactivate current rates
        current_rates = self.get_current_rates()
        if current_rates:
            current_rates.is_current = False
            self.db.add(current_rates)
        
        # Create new rate record
        new_rate = GoldRateHistory(
            tenant_id=self.tenant_id,
            rate_date=datetime.utcnow(),
            gold_rate_24k=rate_data["gold_rate_24k"],
            gold_rate_22k=rate_data["gold_rate_22k"],
            gold_rate_18k=rate_data["gold_rate_18k"],
            silver_rate=rate_data.get("silver_rate"),
            source=rate_data.get("source", source),
            market_name=rate_data.get("market_name"),
            currency="INR",
            is_active=True,
            is_current=True,
            fetched_at=datetime.utcnow(),
            applied_from=datetime.utcnow()
        )
        
        self.db.add(new_rate)
        self.db.commit()
        self.db.refresh(new_rate)
        
        return new_rate
    
    def create_manual_rates(self, rate_data: GoldRateCreateRequest) -> GoldRateHistory:
        """
        Create manual gold rates entry
        """
        # Deactivate current rates if setting as current
        if rate_data.is_current:
            current_rates = self.get_current_rates()
            if current_rates:
                current_rates.is_current = False
                self.db.add(current_rates)
        
        new_rate = GoldRateHistory(
            tenant_id=self.tenant_id,
            rate_date=rate_data.rate_date or datetime.utcnow(),
            gold_rate_24k=rate_data.gold_rate_24k,
            gold_rate_22k=rate_data.gold_rate_22k,
            gold_rate_18k=rate_data.gold_rate_18k,
            silver_rate=rate_data.silver_rate,
            source=rate_data.source or "Manual",
            source_reference=rate_data.source_reference,
            market_name=rate_data.market_name,
            currency=rate_data.currency or "INR",
            is_active=rate_data.is_active,
            is_current=rate_data.is_current,
            fetched_at=datetime.utcnow(),
            applied_from=rate_data.applied_from,
            applied_to=rate_data.applied_to,
            remarks=rate_data.remarks
        )
        
        self.db.add(new_rate)
        self.db.commit()
        self.db.refresh(new_rate)
        
        return new_rate
    
    def update_rates(self, rate_id: str, rate_data: GoldRateUpdateRequest) -> GoldRateHistory:
        """
        Update existing gold rates
        """
        rate = self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.id == rate_id,
                GoldRateHistory.tenant_id == self.tenant_id
            )
        ).first()
        
        if not rate:
            raise HTTPException(status_code=404, detail="Gold rate not found")
        
        # Update fields
        if rate_data.gold_rate_24k is not None:
            rate.gold_rate_24k = rate_data.gold_rate_24k
        if rate_data.gold_rate_22k is not None:
            rate.gold_rate_22k = rate_data.gold_rate_22k
        if rate_data.gold_rate_18k is not None:
            rate.gold_rate_18k = rate_data.gold_rate_18k
        if rate_data.silver_rate is not None:
            rate.silver_rate = rate_data.silver_rate
        if rate_data.is_active is not None:
            rate.is_active = rate_data.is_active
        if rate_data.is_current is not None:
            if rate_data.is_current:
                # Deactivate other current rates
                current = self.get_current_rates()
                if current and current.id != rate_id:
                    current.is_current = False
                    self.db.add(current)
            rate.is_current = rate_data.is_current
        if rate_data.remarks is not None:
            rate.remarks = rate_data.remarks
        
        self.db.add(rate)
        self.db.commit()
        self.db.refresh(rate)
        
        return rate
    
    def get_rate_by_id(self, rate_id: str) -> Optional[GoldRateHistory]:
        """Get gold rate by ID"""
        return self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.id == rate_id,
                GoldRateHistory.tenant_id == self.tenant_id
            )
        ).first()
    
    def get_rates_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[GoldRateHistory]:
        """
        Get historical gold rates
        """
        query = self.db.query(GoldRateHistory).filter(
            GoldRateHistory.tenant_id == self.tenant_id
        )
        
        if start_date:
            query = query.filter(GoldRateHistory.rate_date >= start_date)
        if end_date:
            query = query.filter(GoldRateHistory.rate_date <= end_date)
        if source:
            query = query.filter(GoldRateHistory.source == source)
        
        return query.order_by(desc(GoldRateHistory.rate_date)).limit(limit).all()
    
    def get_rate_for_date(self, target_date: datetime) -> Optional[GoldRateHistory]:
        """
        Get applicable gold rate for a specific date
        """
        return self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.tenant_id == self.tenant_id,
                GoldRateHistory.rate_date <= target_date,
                GoldRateHistory.is_active == True
            )
        ).order_by(desc(GoldRateHistory.rate_date)).first()
    
    def calculate_gold_value(
        self,
        weight_grams: Decimal,
        karat: int,
        rate_24k: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate gold value based on weight and purity
        """
        if rate_24k is None:
            current_rates = self.get_current_rates()
            if not current_rates:
                raise HTTPException(
                    status_code=400,
                    detail="No current gold rates available"
                )
            rate_24k = current_rates.gold_rate_24k
        
        # Calculate purity percentage
        purity_percentage = Decimal(karat) / Decimal(24)
        
        # Calculate value
        value = weight_grams * rate_24k * purity_percentage
        
        return value.quantize(Decimal('0.01'))
    
    def get_rate_by_karat(self, karat: int) -> Decimal:
        """
        Get current gold rate for specific karat
        """
        current_rates = self.get_current_rates()
        if not current_rates:
            raise HTTPException(
                status_code=400,
                detail="No current gold rates available"
            )
        
        if karat == 24:
            return current_rates.gold_rate_24k
        elif karat == 22:
            return current_rates.gold_rate_22k
        elif karat == 18:
            return current_rates.gold_rate_18k
        else:
            # Calculate proportional rate
            purity_percentage = Decimal(karat) / Decimal(24)
            return (current_rates.gold_rate_24k * purity_percentage).quantize(Decimal('0.01'))
    
    def delete_rate(self, rate_id: str) -> bool:
        """
        Delete/deactivate gold rate
        """
        rate = self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.id == rate_id,
                GoldRateHistory.tenant_id == self.tenant_id
            )
        ).first()
        
        if not rate:
            raise HTTPException(status_code=404, detail="Gold rate not found")
        
        # Don't allow deletion of current rate
        if rate.is_current:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete current active rate"
            )
        
        rate.is_active = False
        self.db.add(rate)
        self.db.commit()
        
        return True
    
    def get_rate_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get gold rate statistics for a period
        """
        query = self.db.query(GoldRateHistory).filter(
            and_(
                GoldRateHistory.tenant_id == self.tenant_id,
                GoldRateHistory.is_active == True
            )
        )
        
        if start_date:
            query = query.filter(GoldRateHistory.rate_date >= start_date)
        if end_date:
            query = query.filter(GoldRateHistory.rate_date <= end_date)
        
        rates = query.all()
        
        if not rates:
            return {}
        
        rate_24k_values = [float(r.gold_rate_24k) for r in rates]
        
        return {
            "period_start": min(r.rate_date for r in rates),
            "period_end": max(r.rate_date for r in rates),
            "total_records": len(rates),
            "gold_24k": {
                "current": float(rates[0].gold_rate_24k) if rates else 0,
                "highest": max(rate_24k_values),
                "lowest": min(rate_24k_values),
                "average": sum(rate_24k_values) / len(rate_24k_values),
                "change": float(rates[0].gold_rate_24k - rates[-1].gold_rate_24k) if len(rates) > 1 else 0
            }
        }

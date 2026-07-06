"""
Appraisal Service
Manages comprehensive ornament appraisal workflow
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import json
from fastapi import HTTPException

from backend.shared.database.gold_loan_models import (
    AppraisalReport,
    GoldOrnament,
    GoldLoanAccount,
    GoldRateHistory
)
from backend.services.gold.schemas import (
    AppraisalReportCreateRequest,
    AppraisalReportUpdateRequest,
    AppraisalReportResponse
)
from backend.services.gold.gold_rate_service import GoldRateService


class AppraisalService:
    """Service for ornament appraisal"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.gold_rate_service = GoldRateService(db, tenant_id)
    
    def create_appraisal(
        self,
        appraisal_data: AppraisalReportCreateRequest
    ) -> AppraisalReport:
        """
        Create comprehensive appraisal report
        """
        # Get current gold rates
        current_rates = self.gold_rate_service.get_current_rates()
        if not current_rates:
            raise HTTPException(
                status_code=400,
                detail="No current gold rates available. Please update gold rates first."
            )
        
        # Calculate net gold weight
        net_weight = (
            appraisal_data.gross_weight_grams 
            - appraisal_data.stone_weight_grams 
            - appraisal_data.other_deductions_grams
        )
        
        # Get applicable gold rate based on karat
        applied_rate = self._get_rate_for_karat(
            current_rates,
            appraisal_data.verified_karat
        )
        
        # Calculate base value
        purity_percentage = appraisal_data.purity_percentage
        base_value = net_weight * applied_rate * (purity_percentage / Decimal("100"))
        
        # Apply adjustments
        condition_adjustment = base_value * (appraisal_data.condition_adjustment_percentage / Decimal("100"))
        market_adjustment = base_value * (appraisal_data.market_adjustment_percentage / Decimal("100"))
        
        # Calculate final values
        market_value = base_value + condition_adjustment + market_adjustment
        appraised_value = market_value * Decimal("0.95")  # 5% buffer for appraisal
        forced_sale_value = market_value * Decimal("0.75")  # 25% discount for forced sale
        
        # Generate appraisal number
        appraisal_number = self._generate_appraisal_number()
        
        # Create appraisal report
        appraisal = AppraisalReport(
            tenant_id=self.tenant_id,
            appraisal_number=appraisal_number,
            appraisal_date=appraisal_data.appraisal_date or datetime.utcnow(),
            appraisal_type=appraisal_data.appraisal_type,
            gold_loan_id=appraisal_data.gold_loan_id,
            ornament_id=appraisal_data.ornament_id,
            customer_id=appraisal_data.customer_id,
            ornament_type=appraisal_data.ornament_type,
            ornament_description=appraisal_data.ornament_description,
            quantity=appraisal_data.quantity,
            claimed_karat=appraisal_data.claimed_karat,
            verified_karat=appraisal_data.verified_karat,
            purity_percentage=purity_percentage,
            gross_weight_grams=appraisal_data.gross_weight_grams,
            stone_weight_grams=appraisal_data.stone_weight_grams,
            other_deductions_grams=appraisal_data.other_deductions_grams,
            net_gold_weight_grams=net_weight,
            hallmark_present=appraisal_data.hallmark_present,
            hallmark_number=appraisal_data.hallmark_number,
            hallmark_center=appraisal_data.hallmark_center,
            manufacturer_mark=appraisal_data.manufacturer_mark,
            condition=appraisal_data.condition,
            wear_and_tear=appraisal_data.wear_and_tear,
            defects=appraisal_data.defects,
            current_gold_rate_24k=current_rates.gold_rate_24k,
            applied_gold_rate=applied_rate,
            base_value=base_value,
            condition_adjustment_percentage=appraisal_data.condition_adjustment_percentage,
            market_adjustment_percentage=appraisal_data.market_adjustment_percentage,
            market_value=market_value,
            appraised_value=appraised_value,
            forced_sale_value=forced_sale_value,
            comparable_items=appraisal_data.comparable_items,
            market_reference=appraisal_data.market_reference,
            appraised_by=self.user_id,
            appraiser_name=appraisal_data.appraiser_name,
            appraiser_license=appraisal_data.appraiser_license,
            appraiser_experience_years=appraisal_data.appraiser_experience_years,
            photo_urls=json.dumps(appraisal_data.photo_urls) if appraisal_data.photo_urls else None,
            video_url=appraisal_data.video_url,
            status="Draft",
            previous_appraisal_id=appraisal_data.previous_appraisal_id,
            remarks=appraisal_data.remarks
        )
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        
        return appraisal
    
    def update_appraisal(
        self,
        appraisal_id: str,
        appraisal_data: AppraisalReportUpdateRequest
    ) -> AppraisalReport:
        """
        Update appraisal report
        """
        appraisal = self.get_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")
        
        # Only allow updates for Draft or Rejected status
        if appraisal.status not in ["Draft", "Rejected"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update appraisal with status: {appraisal.status}"
            )
        
        # Update fields
        if appraisal_data.verified_karat is not None:
            appraisal.verified_karat = appraisal_data.verified_karat
        if appraisal_data.purity_percentage is not None:
            appraisal.purity_percentage = appraisal_data.purity_percentage
        if appraisal_data.gross_weight_grams is not None:
            appraisal.gross_weight_grams = appraisal_data.gross_weight_grams
        if appraisal_data.stone_weight_grams is not None:
            appraisal.stone_weight_grams = appraisal_data.stone_weight_grams
        if appraisal_data.other_deductions_grams is not None:
            appraisal.other_deductions_grams = appraisal_data.other_deductions_grams
        
        # Recalculate if weights changed
        if any([
            appraisal_data.gross_weight_grams,
            appraisal_data.stone_weight_grams,
            appraisal_data.other_deductions_grams
        ]):
            appraisal.net_gold_weight_grams = (
                appraisal.gross_weight_grams 
                - appraisal.stone_weight_grams 
                - appraisal.other_deductions_grams
            )
        
        if appraisal_data.condition is not None:
            appraisal.condition = appraisal_data.condition
        if appraisal_data.condition_adjustment_percentage is not None:
            appraisal.condition_adjustment_percentage = appraisal_data.condition_adjustment_percentage
        if appraisal_data.market_adjustment_percentage is not None:
            appraisal.market_adjustment_percentage = appraisal_data.market_adjustment_percentage
        if appraisal_data.appraised_value is not None:
            appraisal.appraised_value = appraisal_data.appraised_value
        if appraisal_data.remarks is not None:
            appraisal.remarks = appraisal_data.remarks
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        
        return appraisal
    
    def submit_appraisal(self, appraisal_id: str) -> AppraisalReport:
        """
        Submit appraisal for verification
        """
        appraisal = self.get_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")
        
        if appraisal.status != "Draft":
            raise HTTPException(
                status_code=400,
                detail=f"Can only submit draft appraisals (current status: {appraisal.status})"
            )
        
        appraisal.status = "Submitted"
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        
        return appraisal
    
    def verify_appraisal(
        self,
        appraisal_id: str,
        verification_status: str,
        remarks: Optional[str] = None
    ) -> AppraisalReport:
        """
        Verify/approve or reject appraisal
        """
        appraisal = self.get_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")
        
        if appraisal.status != "Submitted":
            raise HTTPException(
                status_code=400,
                detail=f"Can only verify submitted appraisals (current status: {appraisal.status})"
            )
        
        appraisal.verified_by = self.user_id
        appraisal.verification_date = datetime.utcnow()
        appraisal.verification_status = verification_status
        
        if verification_status == "Approved":
            appraisal.status = "Approved"
            
            # Update ornament if linked
            if appraisal.ornament_id:
                self._update_ornament_from_appraisal(appraisal)
        else:
            appraisal.status = "Rejected"
        
        if remarks:
            appraisal.remarks = f"{appraisal.remarks or ''}\nVerification: {remarks}"
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        
        return appraisal
    
    def generate_certificate(
        self,
        appraisal_id: str,
        valid_days: int = 180
    ) -> AppraisalReport:
        """
        Generate appraisal certificate
        """
        appraisal = self.get_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")
        
        if appraisal.status != "Approved":
            raise HTTPException(
                status_code=400,
                detail="Certificate can only be generated for approved appraisals"
            )
        
        # Generate certificate number
        certificate_number = f"APPR-CERT-{appraisal.appraisal_number}"
        
        appraisal.certificate_number = certificate_number
        appraisal.certificate_issued_date = datetime.utcnow()
        appraisal.certificate_valid_until = datetime.utcnow() + timedelta(days=valid_days)
        appraisal.next_appraisal_due_date = datetime.utcnow() + timedelta(days=valid_days)
        
        # In real implementation, generate PDF certificate
        # appraisal.certificate_url = generate_appraisal_certificate_pdf(appraisal)
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        
        return appraisal
    
    def create_reappraisal(
        self,
        previous_appraisal_id: str,
        appraisal_type: str = "Re-appraisal"
    ) -> AppraisalReport:
        """
        Create re-appraisal based on previous appraisal
        """
        previous = self.get_appraisal(previous_appraisal_id)
        if not previous:
            raise HTTPException(status_code=404, detail="Previous appraisal not found")
        
        # Get current gold rates
        current_rates = self.gold_rate_service.get_current_rates()
        if not current_rates:
            raise HTTPException(
                status_code=400,
                detail="No current gold rates available"
            )
        
        # Create new appraisal with previous data
        appraisal_number = self._generate_appraisal_number()
        
        applied_rate = self._get_rate_for_karat(current_rates, previous.verified_karat)
        base_value = previous.net_gold_weight_grams * applied_rate * (previous.purity_percentage / Decimal("100"))
        
        # Apply same adjustments
        condition_adjustment = base_value * (previous.condition_adjustment_percentage / Decimal("100"))
        market_adjustment = base_value * (previous.market_adjustment_percentage / Decimal("100"))
        
        market_value = base_value + condition_adjustment + market_adjustment
        appraised_value = market_value * Decimal("0.95")
        forced_sale_value = market_value * Decimal("0.75")
        
        new_appraisal = AppraisalReport(
            tenant_id=self.tenant_id,
            appraisal_number=appraisal_number,
            appraisal_date=datetime.utcnow(),
            appraisal_type=appraisal_type,
            gold_loan_id=previous.gold_loan_id,
            ornament_id=previous.ornament_id,
            customer_id=previous.customer_id,
            ornament_type=previous.ornament_type,
            ornament_description=previous.ornament_description,
            quantity=previous.quantity,
            claimed_karat=previous.claimed_karat,
            verified_karat=previous.verified_karat,
            purity_percentage=previous.purity_percentage,
            gross_weight_grams=previous.gross_weight_grams,
            stone_weight_grams=previous.stone_weight_grams,
            other_deductions_grams=previous.other_deductions_grams,
            net_gold_weight_grams=previous.net_gold_weight_grams,
            hallmark_present=previous.hallmark_present,
            hallmark_number=previous.hallmark_number,
            hallmark_center=previous.hallmark_center,
            manufacturer_mark=previous.manufacturer_mark,
            condition=previous.condition,
            current_gold_rate_24k=current_rates.gold_rate_24k,
            applied_gold_rate=applied_rate,
            base_value=base_value,
            condition_adjustment_percentage=previous.condition_adjustment_percentage,
            market_adjustment_percentage=previous.market_adjustment_percentage,
            market_value=market_value,
            appraised_value=appraised_value,
            forced_sale_value=forced_sale_value,
            appraised_by=self.user_id,
            appraiser_name=previous.appraiser_name,
            appraiser_license=previous.appraiser_license,
            status="Draft",
            previous_appraisal_id=previous_appraisal_id,
            remarks=f"Re-appraisal of {previous.appraisal_number}"
        )
        
        self.db.add(new_appraisal)
        self.db.commit()
        self.db.refresh(new_appraisal)
        
        return new_appraisal
    
    def get_appraisal(self, appraisal_id: str) -> Optional[AppraisalReport]:
        """Get appraisal by ID"""
        return self.db.query(AppraisalReport).filter(
            and_(
                AppraisalReport.id == appraisal_id,
                AppraisalReport.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_appraisals(
        self,
        customer_id: Optional[str] = None,
        loan_id: Optional[str] = None,
        ornament_id: Optional[str] = None,
        appraisal_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AppraisalReport]:
        """List appraisals with filters"""
        query = self.db.query(AppraisalReport).filter(
            AppraisalReport.tenant_id == self.tenant_id
        )
        
        if customer_id:
            query = query.filter(AppraisalReport.customer_id == customer_id)
        if loan_id:
            query = query.filter(AppraisalReport.gold_loan_id == loan_id)
        if ornament_id:
            query = query.filter(AppraisalReport.ornament_id == ornament_id)
        if appraisal_type:
            query = query.filter(AppraisalReport.appraisal_type == appraisal_type)
        if status:
            query = query.filter(AppraisalReport.status == status)
        if start_date:
            query = query.filter(AppraisalReport.appraisal_date >= start_date)
        if end_date:
            query = query.filter(AppraisalReport.appraisal_date <= end_date)
        
        return query.order_by(desc(AppraisalReport.appraisal_date)).all()
    
    def get_appraisal_history(
        self,
        ornament_id: str
    ) -> List[AppraisalReport]:
        """Get complete appraisal history for an ornament"""
        return self.db.query(AppraisalReport).filter(
            and_(
                AppraisalReport.ornament_id == ornament_id,
                AppraisalReport.tenant_id == self.tenant_id
            )
        ).order_by(desc(AppraisalReport.appraisal_date)).all()
    
    def get_appraisals_due_for_renewal(
        self,
        days_ahead: int = 30
    ) -> List[AppraisalReport]:
        """Get appraisals due for renewal"""
        due_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return self.db.query(AppraisalReport).filter(
            and_(
                AppraisalReport.tenant_id == self.tenant_id,
                AppraisalReport.status == "Approved",
                AppraisalReport.next_appraisal_due_date <= due_date
            )
        ).all()
    
    def compare_appraisals(
        self,
        appraisal_id1: str,
        appraisal_id2: str
    ) -> Dict[str, Any]:
        """Compare two appraisals"""
        appraisal1 = self.get_appraisal(appraisal_id1)
        appraisal2 = self.get_appraisal(appraisal_id2)
        
        if not appraisal1 or not appraisal2:
            raise HTTPException(status_code=404, detail="One or both appraisals not found")
        
        return {
            "appraisal_1": {
                "appraisal_number": appraisal1.appraisal_number,
                "appraisal_date": appraisal1.appraisal_date,
                "appraised_value": float(appraisal1.appraised_value),
                "gold_rate_24k": float(appraisal1.current_gold_rate_24k),
                "net_weight_grams": float(appraisal1.net_gold_weight_grams)
            },
            "appraisal_2": {
                "appraisal_number": appraisal2.appraisal_number,
                "appraisal_date": appraisal2.appraisal_date,
                "appraised_value": float(appraisal2.appraised_value),
                "gold_rate_24k": float(appraisal2.current_gold_rate_24k),
                "net_weight_grams": float(appraisal2.net_gold_weight_grams)
            },
            "comparison": {
                "value_change": float(appraisal2.appraised_value - appraisal1.appraised_value),
                "value_change_percentage": float(
                    ((appraisal2.appraised_value - appraisal1.appraised_value) / appraisal1.appraised_value) * 100
                ),
                "gold_rate_change": float(appraisal2.current_gold_rate_24k - appraisal1.current_gold_rate_24k),
                "days_between": (appraisal2.appraisal_date - appraisal1.appraisal_date).days
            }
        }
    
    # ==================== Helper Methods ====================
    
    def _get_rate_for_karat(
        self,
        gold_rates: GoldRateHistory,
        karat: int
    ) -> Decimal:
        """Get gold rate for specific karat"""
        if karat == 24:
            return gold_rates.gold_rate_24k
        elif karat == 22:
            return gold_rates.gold_rate_22k
        elif karat == 18:
            return gold_rates.gold_rate_18k
        else:
            # Calculate proportional rate
            purity_percentage = Decimal(karat) / Decimal(24)
            return (gold_rates.gold_rate_24k * purity_percentage).quantize(Decimal('0.01'))
    
    def _update_ornament_from_appraisal(
        self,
        appraisal: AppraisalReport
    ) -> None:
        """Update ornament details from approved appraisal"""
        ornament = self.db.query(GoldOrnament).filter(
            and_(
                GoldOrnament.id == appraisal.ornament_id,
                GoldOrnament.tenant_id == self.tenant_id
            )
        ).first()
        
        if ornament:
            ornament.purity_karat = appraisal.verified_karat
            ornament.purity_percentage = appraisal.purity_percentage
            ornament.gross_weight_grams = appraisal.gross_weight_grams
            ornament.stone_weight_grams = appraisal.stone_weight_grams
            ornament.net_weight_grams = appraisal.net_gold_weight_grams
            ornament.gold_rate_per_gram = appraisal.applied_gold_rate
            ornament.market_value = appraisal.market_value
            ornament.appraised_value = appraisal.appraised_value
            ornament.hallmark_available = appraisal.hallmark_present
            ornament.hallmark_number = appraisal.hallmark_number
            
            self.db.add(ornament)
    
    def _generate_appraisal_number(self) -> str:
        """Generate unique appraisal number"""
        count = self.db.query(func.count(AppraisalReport.id)).filter(
            AppraisalReport.tenant_id == self.tenant_id
        ).scalar()
        
        return f"APPR-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"

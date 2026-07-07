"""
CRILC Service - Large Credit Identification & Reporting
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
import uuid

from backend.shared.database.compliance_models import (
    CRILCBorrower, CRILCFacility, CRILCQuarterlyReturn,
    BorrowerType, SMAStatus, AssetClassification, ExposureType
)
from backend.shared.database.loan_models import LoanAccount
from backend.shared.database.customer_models import Customer
from .schemas import (
    CRILCBorrowerCreate, CRILCBorrowerUpdate, CRILCBorrowerResponse,
    CRILCFacilityCreate, CRILCFacilityUpdate, CRILCFacilityResponse,
    CRILCQuarterlyReturnCreate, CRILCQuarterlyReturnResponse,
    LargeCreditIdentificationRequest
)


class CRILCService:
    """Service for CRILC operations"""
    
    # RBI Large Credit Threshold (₹5 Crore)
    LARGE_CREDIT_THRESHOLD = Decimal('50000000')
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # ========================================================================
    # BORROWER MANAGEMENT
    # ========================================================================
    
    def create_borrower(
        self,
        data: CRILCBorrowerCreate,
        user_id: UUID
    ) -> CRILCBorrower:
        """Create CRILC borrower"""
        
        # Generate borrower code
        borrower_code = self._generate_borrower_code()
        
        borrower = CRILCBorrower(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            borrower_code=borrower_code,
            borrower_name=data.borrower_name,
            borrower_type=data.borrower_type,
            pan_number=data.pan_number,
            cin_number=data.cin_number,
            gstin=data.gstin,
            registered_address=data.registered_address,
            city=data.city,
            state=data.state,
            pincode=data.pincode,
            industry_code=data.industry_code,
            industry_name=data.industry_name,
            nature_of_business=data.nature_of_business,
            year_of_incorporation=data.year_of_incorporation,
            annual_turnover=data.annual_turnover,
            net_worth=data.net_worth,
            financial_year=data.financial_year,
            customer_id=data.customer_id,
            is_part_of_group=data.is_part_of_group,
            group_name=data.group_name,
            internal_rating=data.internal_rating,
            external_rating=data.external_rating,
            rating_agency=data.rating_agency,
            rating_date=data.rating_date,
            total_credit_exposure=Decimal('0'),
            funded_exposure=Decimal('0'),
            non_funded_exposure=Decimal('0'),
            is_large_credit=False,
            current_sma_status=SMAStatus.STANDARD,
            current_asset_classification=AssetClassification.STANDARD,
            days_past_due=0,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(borrower)
        self.db.commit()
        self.db.refresh(borrower)
        
        return borrower
    
    def update_borrower(
        self,
        borrower_id: UUID,
        data: CRILCBorrowerUpdate,
        user_id: UUID
    ) -> Optional[CRILCBorrower]:
        """Update CRILC borrower"""
        
        borrower = self.db.query(CRILCBorrower).filter(
            CRILCBorrower.id == borrower_id,
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_deleted == False
        ).first()
        
        if not borrower:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(borrower, key, value)
        
        borrower.updated_by = user_id
        borrower.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(borrower)
        
        return borrower
    
    def get_borrower(self, borrower_id: UUID) -> Optional[CRILCBorrower]:
        """Get borrower by ID"""
        return self.db.query(CRILCBorrower).filter(
            CRILCBorrower.id == borrower_id,
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_deleted == False
        ).first()
    
    def list_borrowers(
        self,
        skip: int = 0,
        limit: int = 100,
        is_large_credit: Optional[bool] = None,
        sma_status: Optional[str] = None,
        industry_code: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[CRILCBorrower]:
        """List CRILC borrowers with filters"""
        
        query = self.db.query(CRILCBorrower).filter(
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_deleted == False
        )
        
        if is_large_credit is not None:
            query = query.filter(CRILCBorrower.is_large_credit == is_large_credit)
        
        if sma_status:
            query = query.filter(CRILCBorrower.current_sma_status == sma_status)
        
        if industry_code:
            query = query.filter(CRILCBorrower.industry_code == industry_code)
        
        if state:
            query = query.filter(CRILCBorrower.state == state)
        
        query = query.order_by(CRILCBorrower.total_credit_exposure.desc())
        
        return query.offset(skip).limit(limit).all()
    
    # ========================================================================
    # FACILITY MANAGEMENT
    # ========================================================================
    
    def add_facility(
        self,
        data: CRILCFacilityCreate,
        user_id: UUID
    ) -> CRILCFacility:
        """Add facility to borrower"""
        
        facility_id_str = self._generate_facility_id(data.borrower_id)
        
        facility = CRILCFacility(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            borrower_id=data.borrower_id,
            loan_account_id=data.loan_account_id,
            facility_id=facility_id_str,
            facility_type=data.facility_type,
            exposure_type=data.exposure_type,
            sanctioned_amount=data.sanctioned_amount,
            outstanding_amount=data.outstanding_amount,
            overdue_amount=data.overdue_amount,
            sanction_date=data.sanction_date,
            disbursement_date=data.disbursement_date,
            maturity_date=data.maturity_date,
            security_type=data.security_type,
            security_value=data.security_value,
            collateral_details=data.collateral_details,
            interest_rate=data.interest_rate,
            days_past_due=0,
            asset_classification=AssetClassification.STANDARD,
            is_active=True,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        
        # Update borrower exposure
        self._update_borrower_exposure(data.borrower_id)
        
        return facility
    
    def update_facility(
        self,
        facility_id: UUID,
        data: CRILCFacilityUpdate,
        user_id: UUID
    ) -> Optional[CRILCFacility]:
        """Update facility"""
        
        facility = self.db.query(CRILCFacility).filter(
            CRILCFacility.id == facility_id,
            CRILCFacility.tenant_id == self.tenant_id,
            CRILCFacility.is_deleted == False
        ).first()
        
        if not facility:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(facility, key, value)
        
        facility.updated_by = user_id
        facility.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(facility)
        
        # Update borrower exposure
        self._update_borrower_exposure(facility.borrower_id)
        
        return facility
    
    def get_borrower_facilities(
        self,
        borrower_id: UUID
    ) -> List[CRILCFacility]:
        """Get all facilities for a borrower"""
        return self.db.query(CRILCFacility).filter(
            CRILCFacility.borrower_id == borrower_id,
            CRILCFacility.tenant_id == self.tenant_id,
            CRILCFacility.is_deleted == False
        ).all()
    
    # ========================================================================
    # LARGE CREDIT IDENTIFICATION
    # ========================================================================
    
    def identify_large_credits(
        self,
        request: LargeCreditIdentificationRequest
    ) -> Dict[str, Any]:
        """Identify large credits based on threshold"""
        
        threshold = request.threshold_amount or self.LARGE_CREDIT_THRESHOLD
        as_on_date = request.as_on_date
        
        # Get all active borrowers
        borrowers = self.db.query(CRILCBorrower).filter(
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_active == True,
            CRILCBorrower.is_deleted == False
        ).all()
        
        large_credits_identified = []
        large_credits_removed = []
        
        for borrower in borrowers:
            # Calculate total exposure
            facilities = self.get_borrower_facilities(borrower.id)
            
            funded = sum(
                f.outstanding_amount for f in facilities
                if f.exposure_type == ExposureType.FUNDED and f.is_active
            )
            
            non_funded = sum(
                f.outstanding_amount for f in facilities
                if f.exposure_type == ExposureType.NON_FUNDED and f.is_active
            )
            
            total_exposure = funded + non_funded
            
            # Group exposure (if applicable)
            if request.include_group_exposure and borrower.is_part_of_group:
                # In production, calculate group exposure
                # For now, use individual exposure
                pass
            
            # Check threshold
            was_large_credit = borrower.is_large_credit
            is_large_credit_now = total_exposure >= threshold
            
            if is_large_credit_now != was_large_credit:
                if is_large_credit_now:
                    borrower.is_large_credit = True
                    borrower.large_credit_since = as_on_date
                    large_credits_identified.append({
                        'borrower_id': str(borrower.id),
                        'borrower_name': borrower.borrower_name,
                        'total_exposure': float(total_exposure),
                        'threshold': float(threshold)
                    })
                else:
                    borrower.is_large_credit = False
                    borrower.large_credit_since = None
                    large_credits_removed.append({
                        'borrower_id': str(borrower.id),
                        'borrower_name': borrower.borrower_name,
                        'total_exposure': float(total_exposure)
                    })
            
            # Update exposures
            borrower.total_credit_exposure = total_exposure
            borrower.funded_exposure = funded
            borrower.non_funded_exposure = non_funded
        
        self.db.commit()
        
        # Count large credits
        large_credit_count = self.db.query(func.count(CRILCBorrower.id)).filter(
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_large_credit == True,
            CRILCBorrower.is_active == True,
            CRILCBorrower.is_deleted == False
        ).scalar()
        
        return {
            'threshold_amount': float(threshold),
            'as_on_date': as_on_date.isoformat(),
            'total_large_credits': large_credit_count,
            'newly_identified': len(large_credits_identified),
            'removed_from_list': len(large_credits_removed),
            'identified_borrowers': large_credits_identified,
            'removed_borrowers': large_credits_removed
        }
    
    # ========================================================================
    # QUARTERLY RETURN GENERATION
    # ========================================================================
    
    def generate_quarterly_return(
        self,
        data: CRILCQuarterlyReturnCreate,
        user_id: UUID
    ) -> CRILCQuarterlyReturn:
        """Generate CRILC quarterly return"""
        
        return_number = self._generate_return_number(data.reporting_quarter)
        
        # Get all large credit borrowers
        large_borrowers = self.db.query(CRILCBorrower).filter(
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_large_credit == True,
            CRILCBorrower.is_active == True,
            CRILCBorrower.is_deleted == False
        ).all()
        
        # Calculate aggregates
        total_funded = Decimal('0')
        total_non_funded = Decimal('0')
        sma_counts = {
            'sma_0': 0, 'sma_0_amount': Decimal('0'),
            'sma_1': 0, 'sma_1_amount': Decimal('0'),
            'sma_2': 0, 'sma_2_amount': Decimal('0'),
            'npa': 0, 'npa_amount': Decimal('0')
        }
        
        data_snapshot = []
        
        for borrower in large_borrowers:
            total_funded += borrower.funded_exposure or Decimal('0')
            total_non_funded += borrower.non_funded_exposure or Decimal('0')
            
            # SMA classification
            if borrower.current_sma_status == SMAStatus.SMA_0:
                sma_counts['sma_0'] += 1
                sma_counts['sma_0_amount'] += borrower.total_credit_exposure
            elif borrower.current_sma_status == SMAStatus.SMA_1:
                sma_counts['sma_1'] += 1
                sma_counts['sma_1_amount'] += borrower.total_credit_exposure
            elif borrower.current_sma_status == SMAStatus.SMA_2:
                sma_counts['sma_2'] += 1
                sma_counts['sma_2_amount'] += borrower.total_credit_exposure
            elif borrower.current_sma_status in [
                SMAStatus.NPA_SUBSTANDARD,
                SMAStatus.NPA_DOUBTFUL,
                SMAStatus.NPA_LOSS
            ]:
                sma_counts['npa'] += 1
                sma_counts['npa_amount'] += borrower.total_credit_exposure
            
            # Add to snapshot
            data_snapshot.append({
                'borrower_id': str(borrower.id),
                'borrower_code': borrower.borrower_code,
                'borrower_name': borrower.borrower_name,
                'pan': borrower.pan_number,
                'total_exposure': float(borrower.total_credit_exposure),
                'funded': float(borrower.funded_exposure or 0),
                'non_funded': float(borrower.non_funded_exposure or 0),
                'sma_status': borrower.current_sma_status,
                'dpd': borrower.days_past_due
            })
        
        total_exposure = total_funded + total_non_funded
        
        # Create return
        quarterly_return = CRILCQuarterlyReturn(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            return_number=return_number,
            reporting_quarter=data.reporting_quarter,
            reporting_year=data.reporting_year,
            as_on_date=data.as_on_date,
            status='draft',
            total_large_borrowers=len(large_borrowers),
            total_funded_exposure=total_funded,
            total_non_funded_exposure=total_non_funded,
            total_exposure=total_exposure,
            sma_0_count=sma_counts['sma_0'],
            sma_0_amount=sma_counts['sma_0_amount'],
            sma_1_count=sma_counts['sma_1'],
            sma_1_amount=sma_counts['sma_1_amount'],
            sma_2_count=sma_counts['sma_2'],
            sma_2_amount=sma_counts['sma_2_amount'],
            npa_count=sma_counts['npa'],
            npa_amount=sma_counts['npa_amount'],
            data_snapshot=data_snapshot,
            remarks=data.remarks,
            prepared_by=user_id,
            prepared_date=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(quarterly_return)
        self.db.commit()
        self.db.refresh(quarterly_return)
        
        return quarterly_return
    
    def get_quarterly_return(
        self,
        return_id: UUID
    ) -> Optional[CRILCQuarterlyReturn]:
        """Get quarterly return"""
        return self.db.query(CRILCQuarterlyReturn).filter(
            CRILCQuarterlyReturn.id == return_id,
            CRILCQuarterlyReturn.tenant_id == self.tenant_id,
            CRILCQuarterlyReturn.is_deleted == False
        ).first()
    
    def list_quarterly_returns(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[CRILCQuarterlyReturn]:
        """List quarterly returns"""
        return self.db.query(CRILCQuarterlyReturn).filter(
            CRILCQuarterlyReturn.tenant_id == self.tenant_id,
            CRILCQuarterlyReturn.is_deleted == False
        ).order_by(
            CRILCQuarterlyReturn.as_on_date.desc()
        ).offset(skip).limit(limit).all()
    
    def approve_quarterly_return(
        self,
        return_id: UUID,
        user_id: UUID
    ) -> Optional[CRILCQuarterlyReturn]:
        """Approve quarterly return"""
        
        quarterly_return = self.get_quarterly_return(return_id)
        if not quarterly_return:
            return None
        
        quarterly_return.status = 'approved'
        quarterly_return.approved_by = user_id
        quarterly_return.approved_date = datetime.utcnow()
        quarterly_return.updated_by = user_id
        quarterly_return.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(quarterly_return)
        
        return quarterly_return
    
    def submit_quarterly_return(
        self,
        return_id: UUID,
        submission_reference: str,
        user_id: UUID
    ) -> Optional[CRILCQuarterlyReturn]:
        """Submit quarterly return"""
        
        quarterly_return = self.get_quarterly_return(return_id)
        if not quarterly_return or quarterly_return.status != 'approved':
            return None
        
        quarterly_return.status = 'submitted'
        quarterly_return.submitted_date = datetime.utcnow()
        quarterly_return.submission_reference = submission_reference
        quarterly_return.updated_by = user_id
        quarterly_return.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(quarterly_return)
        
        return quarterly_return
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_borrower_code(self) -> str:
        """Generate unique borrower code"""
        count = self.db.query(func.count(CRILCBorrower.id)).filter(
            CRILCBorrower.tenant_id == self.tenant_id
        ).scalar() or 0
        return f"CRLC{self.tenant_id[:4].upper()}{count + 1:06d}"
    
    def _generate_facility_id(self, borrower_id: UUID) -> str:
        """Generate unique facility ID"""
        count = self.db.query(func.count(CRILCFacility.id)).filter(
            CRILCFacility.borrower_id == borrower_id,
            CRILCFacility.tenant_id == self.tenant_id
        ).scalar() or 0
        return f"FAC{str(borrower_id)[:8].upper()}{count + 1:04d}"
    
    def _generate_return_number(self, quarter: str) -> str:
        """Generate return number"""
        count = self.db.query(func.count(CRILCQuarterlyReturn.id)).filter(
            CRILCQuarterlyReturn.tenant_id == self.tenant_id,
            CRILCQuarterlyReturn.reporting_quarter == quarter
        ).scalar() or 0
        return f"CRILC{quarter}{count + 1:03d}"
    
    def _update_borrower_exposure(self, borrower_id: UUID) -> None:
        """Update borrower total exposure"""
        
        facilities = self.get_borrower_facilities(borrower_id)
        
        funded = sum(
            f.outstanding_amount for f in facilities
            if f.exposure_type == ExposureType.FUNDED and f.is_active
        )
        
        non_funded = sum(
            f.outstanding_amount for f in facilities
            if f.exposure_type == ExposureType.NON_FUNDED and f.is_active
        )
        
        total = funded + non_funded
        
        borrower = self.get_borrower(borrower_id)
        if borrower:
            borrower.funded_exposure = funded
            borrower.non_funded_exposure = non_funded
            borrower.total_credit_exposure = total
            
            # Check large credit threshold
            if total >= self.LARGE_CREDIT_THRESHOLD:
                if not borrower.is_large_credit:
                    borrower.is_large_credit = True
                    borrower.large_credit_since = date.today()
            else:
                if borrower.is_large_credit:
                    borrower.is_large_credit = False
                    borrower.large_credit_since = None
            
            self.db.commit()

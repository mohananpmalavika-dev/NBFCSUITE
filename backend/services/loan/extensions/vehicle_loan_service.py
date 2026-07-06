"""
Vehicle Loan Extension Service
Business logic for vehicle loan specific operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from backend.shared.database.vehicle_loan_models import (
    VehicleLoanDetails, VehicleDealer, VehicleRTOTracking,
    VehicleInsurance, VehicleInsuranceClaim, VehicleManufacturerModel,
    VehicleType, VehicleCondition, HypothecationStatus, InsuranceStatus
)
from backend.shared.database.loan_models import LoanApplication

logger = logging.getLogger(__name__)


class VehicleLoanService:
    """Service for vehicle loan operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============================================
    # Vehicle Details Management
    # ============================================
    
    def create_vehicle_details(
        self,
        loan_application_id: int,
        vehicle_data: dict,
        user_id: str
    ) -> VehicleLoanDetails:
        """Create vehicle details for loan application"""
        
        # Validate loan application exists
        loan_app = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.id == loan_application_id,
                LoanApplication.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan_app:
            raise ValueError("Loan application not found")
        
        # Check if vehicle details already exist
        existing = self.db.query(VehicleLoanDetails).filter(
            and_(
                VehicleLoanDetails.loan_application_id == loan_application_id,
                VehicleLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("Vehicle details already exist for this loan application")
        
        # Validate chassis/engine uniqueness
        if vehicle_data.get('chassis_number'):
            existing_chassis = self.db.query(VehicleLoanDetails).filter(
                and_(
                    VehicleLoanDetails.chassis_number == vehicle_data['chassis_number'],
                    VehicleLoanDetails.tenant_id == self.tenant_id
                )
            ).first()
            if existing_chassis:
                raise ValueError(f"Chassis number {vehicle_data['chassis_number']} already exists")
        
        # Create vehicle details
        vehicle_details = VehicleLoanDetails(
            tenant_id=self.tenant_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **vehicle_data
        )
        
        self.db.add(vehicle_details)
        self.db.commit()
        self.db.refresh(vehicle_details)
        
        logger.info(f"Vehicle details created for loan application {loan_application_id}")
        
        return vehicle_details
    
    def get_vehicle_details(self, loan_application_id: int) -> Optional[VehicleLoanDetails]:
        """Get vehicle details by loan application ID"""
        return self.db.query(VehicleLoanDetails).filter(
            and_(
                VehicleLoanDetails.loan_application_id == loan_application_id,
                VehicleLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
    
    def update_vehicle_details(
        self,
        vehicle_id: int,
        vehicle_data: dict,
        user_id: str
    ) -> Optional[VehicleLoanDetails]:
        """Update vehicle details"""
        
        vehicle = self.db.query(VehicleLoanDetails).filter(
            and_(
                VehicleLoanDetails.id == vehicle_id,
                VehicleLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
        
        if not vehicle:
            return None
        
        # Update fields
        for field, value in vehicle_data.items():
            if hasattr(vehicle, field):
                setattr(vehicle, field, value)
        
        vehicle.updated_by = user_id
        vehicle.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(vehicle)
        
        logger.info(f"Vehicle details updated for ID {vehicle_id}")
        
        return vehicle
    
    def calculate_ltv(
        self,
        on_road_price: Decimal,
        financed_amount: Decimal
    ) -> Decimal:
        """Calculate Loan-to-Value ratio"""
        if on_road_price == 0:
            return Decimal("0")
        return (financed_amount / on_road_price) * 100
    
    # ============================================
    # Dealer Management
    # ============================================
    
    def create_dealer(self, dealer_data: dict, user_id: str) -> VehicleDealer:
        """Create new vehicle dealer"""
        
        # Check if dealer code exists
        existing = self.db.query(VehicleDealer).filter(
            and_(
                VehicleDealer.dealer_code == dealer_data['dealer_code'],
                VehicleDealer.tenant_id == self.tenant_id,
                VehicleDealer.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Dealer code {dealer_data['dealer_code']} already exists")
        
        dealer = VehicleDealer(
            tenant_id=self.tenant_id,
            created_by=user_id,
            updated_by=user_id,
            **dealer_data
        )
        
        self.db.add(dealer)
        self.db.commit()
        self.db.refresh(dealer)
        
        logger.info(f"Dealer created: {dealer.dealer_code}")
        
        return dealer
    
    def get_dealer(self, dealer_id: int) -> Optional[VehicleDealer]:
        """Get dealer by ID"""
        return self.db.query(VehicleDealer).filter(
            and_(
                VehicleDealer.id == dealer_id,
                VehicleDealer.tenant_id == self.tenant_id,
                VehicleDealer.is_deleted == False
            )
        ).first()
    
    def list_dealers(
        self,
        is_active: Optional[bool] = None,
        brand: Optional[str] = None
    ) -> List[VehicleDealer]:
        """List dealers with filters"""
        
        query = self.db.query(VehicleDealer).filter(
            and_(
                VehicleDealer.tenant_id == self.tenant_id,
                VehicleDealer.is_deleted == False
            )
        )
        
        if is_active is not None:
            query = query.filter(VehicleDealer.is_active == is_active)
        
        if brand:
            query = query.filter(VehicleDealer.brand == brand)
        
        return query.order_by(VehicleDealer.dealer_name).all()
    
    # ============================================
    # RTO & Hypothecation Management
    # ============================================
    
    def create_rto_tracking(
        self,
        vehicle_loan_id: int,
        loan_application_id: int,
        rto_data: dict,
        user_id: str
    ) -> VehicleRTOTracking:
        """Initialize RTO tracking for vehicle loan"""
        
        # Check if already exists
        existing = self.db.query(VehicleRTOTracking).filter(
            and_(
                VehicleRTOTracking.vehicle_loan_id == vehicle_loan_id,
                VehicleRTOTracking.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("RTO tracking already exists for this vehicle loan")
        
        rto_tracking = VehicleRTOTracking(
            tenant_id=self.tenant_id,
            vehicle_loan_id=vehicle_loan_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **rto_data
        )
        
        self.db.add(rto_tracking)
        self.db.commit()
        self.db.refresh(rto_tracking)
        
        logger.info(f"RTO tracking created for vehicle loan {vehicle_loan_id}")
        
        return rto_tracking
    
    def update_hypothecation_status(
        self,
        rto_tracking_id: int,
        status: HypothecationStatus,
        updates: dict,
        user_id: str
    ) -> Optional[VehicleRTOTracking]:
        """Update hypothecation status"""
        
        rto_tracking = self.db.query(VehicleRTOTracking).filter(
            and_(
                VehicleRTOTracking.id == rto_tracking_id,
                VehicleRTOTracking.tenant_id == self.tenant_id
            )
        ).first()
        
        if not rto_tracking:
            return None
        
        # Update status
        rto_tracking.hypothecation_status = status
        
        # Update related fields based on status
        if status == HypothecationStatus.SUBMITTED:
            rto_tracking.form35_submitted = True
            rto_tracking.form35_submission_date = updates.get('submission_date', date.today())
        
        elif status == HypothecationStatus.MARKED:
            rto_tracking.hypothecation_marked_date = updates.get('marked_date', date.today())
            rto_tracking.rc_book_updated = True
            
            # Update vehicle details
            vehicle = self.db.query(VehicleLoanDetails).filter(
                VehicleLoanDetails.id == rto_tracking.vehicle_loan_id
            ).first()
            if vehicle:
                vehicle.hypothecation_status = HypothecationStatus.MARKED
        
        elif status == HypothecationStatus.NOC_ISSUED:
            rto_tracking.noc_generated_date = updates.get('noc_date', date.today())
        
        elif status == HypothecationStatus.REMOVED:
            rto_tracking.hypothecation_removed_date = updates.get('removed_date', date.today())
            
            # Update vehicle details
            vehicle = self.db.query(VehicleLoanDetails).filter(
                VehicleLoanDetails.id == rto_tracking.vehicle_loan_id
            ).first()
            if vehicle:
                vehicle.hypothecation_status = HypothecationStatus.REMOVED
        
        # Update additional fields
        for field, value in updates.items():
            if hasattr(rto_tracking, field):
                setattr(rto_tracking, field, value)
        
        rto_tracking.updated_by = user_id
        rto_tracking.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(rto_tracking)
        
        logger.info(f"Hypothecation status updated to {status} for RTO tracking {rto_tracking_id}")
        
        return rto_tracking
    
    def get_pending_hypothecations(self) -> List[VehicleRTOTracking]:
        """Get all pending hypothecation cases"""
        return self.db.query(VehicleRTOTracking).filter(
            and_(
                VehicleRTOTracking.tenant_id == self.tenant_id,
                VehicleRTOTracking.hypothecation_status.in_([
                    HypothecationStatus.PENDING,
                    HypothecationStatus.SUBMITTED
                ])
            )
        ).order_by(VehicleRTOTracking.created_at.asc()).all()
    
    def get_noc_required_cases(self) -> List[VehicleRTOTracking]:
        """Get cases where loan is closed but NOC not issued"""
        return self.db.query(VehicleRTOTracking).filter(
            and_(
                VehicleRTOTracking.tenant_id == self.tenant_id,
                VehicleRTOTracking.loan_closed_date.isnot(None),
                VehicleRTOTracking.noc_generated_date.is_(None),
                VehicleRTOTracking.hypothecation_status == HypothecationStatus.MARKED
            )
        ).all()
    
    # ============================================
    # Insurance Management
    # ============================================
    
    def create_insurance_policy(
        self,
        vehicle_loan_id: int,
        loan_application_id: int,
        customer_id: str,
        insurance_data: dict,
        user_id: str
    ) -> VehicleInsurance:
        """Create insurance policy for vehicle loan"""
        
        # Check if policy number already exists
        existing = self.db.query(VehicleInsurance).filter(
            and_(
                VehicleInsurance.policy_number == insurance_data['policy_number'],
                VehicleInsurance.tenant_id == self.tenant_id,
                VehicleInsurance.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Policy number {insurance_data['policy_number']} already exists")
        
        insurance = VehicleInsurance(
            tenant_id=self.tenant_id,
            vehicle_loan_id=vehicle_loan_id,
            loan_application_id=loan_application_id,
            customer_id=customer_id,
            created_by=user_id,
            updated_by=user_id,
            **insurance_data
        )
        
        self.db.add(insurance)
        self.db.commit()
        self.db.refresh(insurance)
        
        logger.info(f"Insurance policy created: {insurance.policy_number}")
        
        return insurance
    
    def get_insurance_policy(self, policy_id: int) -> Optional[VehicleInsurance]:
        """Get insurance policy by ID"""
        return self.db.query(VehicleInsurance).filter(
            and_(
                VehicleInsurance.id == policy_id,
                VehicleInsurance.tenant_id == self.tenant_id,
                VehicleInsurance.is_deleted == False
            )
        ).first()
    
    def get_vehicle_insurances(self, vehicle_loan_id: int) -> List[VehicleInsurance]:
        """Get all insurance policies for a vehicle loan"""
        return self.db.query(VehicleInsurance).filter(
            and_(
                VehicleInsurance.vehicle_loan_id == vehicle_loan_id,
                VehicleInsurance.tenant_id == self.tenant_id,
                VehicleInsurance.is_deleted == False
            )
        ).order_by(VehicleInsurance.policy_start_date.desc()).all()
    
    def get_expiring_insurances(self, days: int = 30) -> List[VehicleInsurance]:
        """Get insurance policies expiring in next X days"""
        today = date.today()
        expiry_date = today + timedelta(days=days)
        
        return self.db.query(VehicleInsurance).filter(
            and_(
                VehicleInsurance.tenant_id == self.tenant_id,
                VehicleInsurance.status == InsuranceStatus.ACTIVE,
                VehicleInsurance.policy_end_date >= today,
                VehicleInsurance.policy_end_date <= expiry_date,
                VehicleInsurance.is_deleted == False
            )
        ).order_by(VehicleInsurance.policy_end_date.asc()).all()
    
    def mark_insurance_expired(self, insurance_id: int) -> Optional[VehicleInsurance]:
        """Mark insurance as expired"""
        
        insurance = self.get_insurance_policy(insurance_id)
        if not insurance:
            return None
        
        insurance.status = InsuranceStatus.EXPIRED
        insurance.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(insurance)
        
        logger.info(f"Insurance policy marked as expired: {insurance.policy_number}")
        
        return insurance
    
    def send_renewal_reminder(self, insurance_id: int) -> bool:
        """Send renewal reminder for insurance"""
        
        insurance = self.get_insurance_policy(insurance_id)
        if not insurance:
            return False
        
        # Update reminder sent flag
        insurance.renewal_notice_sent = True
        insurance.renewal_notice_date = date.today()
        insurance.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Renewal reminder sent for policy: {insurance.policy_number}")
        
        # TODO: Integrate with notification service to send actual reminder
        
        return True
    
    def update_lien_status(
        self,
        insurance_id: int,
        lien_marked: bool,
        lien_holder_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[VehicleInsurance]:
        """Update lien marking status on insurance"""
        
        insurance = self.get_insurance_policy(insurance_id)
        if not insurance:
            return None
        
        insurance.lien_marked = lien_marked
        
        if lien_marked:
            insurance.lien_holder_name = lien_holder_name
            insurance.lien_marked_date = date.today()
        else:
            insurance.lien_removed_date = date.today()
        
        insurance.updated_by = user_id
        insurance.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(insurance)
        
        logger.info(f"Lien status updated for policy: {insurance.policy_number}")
        
        return insurance
    
    # ============================================
    # Insurance Claims Management
    # ============================================
    
    def create_insurance_claim(
        self,
        insurance_id: int,
        claim_data: dict,
        user_id: str
    ) -> VehicleInsuranceClaim:
        """Create insurance claim"""
        
        # Validate insurance exists
        insurance = self.get_insurance_policy(insurance_id)
        if not insurance:
            raise ValueError("Insurance policy not found")
        
        if insurance.status != InsuranceStatus.ACTIVE:
            raise ValueError("Insurance policy is not active")
        
        # Check if claim number exists
        existing = self.db.query(VehicleInsuranceClaim).filter(
            and_(
                VehicleInsuranceClaim.claim_number == claim_data['claim_number'],
                VehicleInsuranceClaim.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError(f"Claim number {claim_data['claim_number']} already exists")
        
        claim = VehicleInsuranceClaim(
            tenant_id=self.tenant_id,
            insurance_id=insurance_id,
            created_by=user_id,
            updated_by=user_id,
            **claim_data
        )
        
        self.db.add(claim)
        
        # Update insurance claims count
        insurance.claims_count += 1
        insurance.last_claim_date = claim_data.get('claim_date', date.today())
        
        self.db.commit()
        self.db.refresh(claim)
        
        logger.info(f"Insurance claim created: {claim.claim_number}")
        
        return claim
    
    def update_claim_status(
        self,
        claim_id: int,
        status: str,
        updates: dict,
        user_id: str
    ) -> Optional[VehicleInsuranceClaim]:
        """Update insurance claim status"""
        
        claim = self.db.query(VehicleInsuranceClaim).filter(
            and_(
                VehicleInsuranceClaim.id == claim_id,
                VehicleInsuranceClaim.tenant_id == self.tenant_id
            )
        ).first()
        
        if not claim:
            return None
        
        claim.claim_status = status
        
        # Update related fields
        for field, value in updates.items():
            if hasattr(claim, field):
                setattr(claim, field, value)
        
        # Update insurance total claim amount if settled
        if status == "settled" and updates.get('settled_amount'):
            insurance = self.get_insurance_policy(claim.insurance_id)
            if insurance:
                insurance.total_claim_amount += Decimal(str(updates['settled_amount']))
        
        claim.updated_by = user_id
        claim.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(claim)
        
        logger.info(f"Claim status updated to {status} for claim {claim.claim_number}")
        
        return claim
    
    # ============================================
    # Master Data Management
    # ============================================
    
    def create_vehicle_model(self, model_data: dict) -> VehicleManufacturerModel:
        """Create vehicle manufacturer/model master data"""
        
        model = VehicleManufacturerModel(
            tenant_id=self.tenant_id,
            **model_data
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        
        logger.info(f"Vehicle model created: {model.manufacturer} {model.model}")
        
        return model
    
    def search_vehicle_models(
        self,
        vehicle_type: Optional[VehicleType] = None,
        manufacturer: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[VehicleManufacturerModel]:
        """Search vehicle models"""
        
        query = self.db.query(VehicleManufacturerModel).filter(
            and_(
                VehicleManufacturerModel.tenant_id == self.tenant_id,
                VehicleManufacturerModel.is_active == True,
                VehicleManufacturerModel.is_deleted == False
            )
        )
        
        if vehicle_type:
            query = query.filter(VehicleManufacturerModel.vehicle_type == vehicle_type)
        
        if manufacturer:
            query = query.filter(VehicleManufacturerModel.manufacturer.ilike(f"%{manufacturer}%"))
        
        if search:
            query = query.filter(
                or_(
                    VehicleManufacturerModel.manufacturer.ilike(f"%{search}%"),
                    VehicleManufacturerModel.model.ilike(f"%{search}%"),
                    VehicleManufacturerModel.variant.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(
            VehicleManufacturerModel.manufacturer,
            VehicleManufacturerModel.model
        ).all()
    
    # ============================================
    # Reporting & Analytics
    # ============================================
    
    def get_vehicle_loan_summary(self, loan_application_id: int) -> dict:
        """Get complete summary of vehicle loan"""
        
        vehicle = self.get_vehicle_details(loan_application_id)
        if not vehicle:
            return {}
        
        rto_tracking = self.db.query(VehicleRTOTracking).filter(
            VehicleRTOTracking.vehicle_loan_id == vehicle.id
        ).first()
        
        insurances = self.get_vehicle_insurances(vehicle.id)
        active_insurance = next((i for i in insurances if i.status == InsuranceStatus.ACTIVE), None)
        
        return {
            "vehicle_details": vehicle,
            "rto_tracking": rto_tracking,
            "insurance_policies": insurances,
            "active_insurance": active_insurance,
            "hypothecation_status": rto_tracking.hypothecation_status if rto_tracking else None,
            "insurance_status": active_insurance.status if active_insurance else None,
            "is_compliant": self._check_compliance(vehicle, rto_tracking, active_insurance)
        }
    
    def _check_compliance(
        self,
        vehicle: VehicleLoanDetails,
        rto_tracking: Optional[VehicleRTOTracking],
        insurance: Optional[VehicleInsurance]
    ) -> dict:
        """Check compliance status"""
        
        issues = []
        
        # Check hypothecation
        if not rto_tracking or rto_tracking.hypothecation_status != HypothecationStatus.MARKED:
            issues.append("Hypothecation not marked at RTO")
        
        # Check insurance
        if not insurance or insurance.status != InsuranceStatus.ACTIVE:
            issues.append("No active insurance policy")
        elif insurance.policy_end_date < date.today():
            issues.append("Insurance policy expired")
        
        # Check lien marking
        if insurance and not insurance.lien_marked:
            issues.append("Lien not marked on insurance")
        
        return {
            "is_compliant": len(issues) == 0,
            "issues": issues
        }

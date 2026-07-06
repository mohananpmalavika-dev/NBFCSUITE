"""
Vehicle Loan Router
API endpoints for vehicle loan extension
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.loan.extensions.vehicle_loan_service import VehicleLoanService
from backend.services.loan.extensions import vehicle_schemas as schemas


router = APIRouter(prefix="/vehicle-loans", tags=["Vehicle Loans"])


# ============================================
# Vehicle Details Endpoints
# ============================================

@router.post("/details", response_model=dict)
async def create_vehicle_details(
    data: schemas.VehicleDetailsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create vehicle details for loan application"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        vehicle_data = data.model_dump(exclude={"loan_application_id"})
        vehicle = service.create_vehicle_details(
            loan_application_id=data.loan_application_id,
            vehicle_data=vehicle_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.VehicleDetailsResponse.model_validate(vehicle),
            message="Vehicle details created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/details/{loan_application_id}", response_model=dict)
async def get_vehicle_details(
    loan_application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get vehicle details by loan application ID"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        vehicle = service.get_vehicle_details(loan_application_id)
        
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle details not found")
        
        return success_response(
            data=schemas.VehicleDetailsResponse.model_validate(vehicle)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/details/{vehicle_id}", response_model=dict)
async def update_vehicle_details(
    vehicle_id: int,
    data: schemas.VehicleDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update vehicle details"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        vehicle_data = data.model_dump(exclude_unset=True)
        vehicle = service.update_vehicle_details(
            vehicle_id=vehicle_id,
            vehicle_data=vehicle_data,
            user_id=current_user["user_id"]
        )
        
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        
        return success_response(
            data=schemas.VehicleDetailsResponse.model_validate(vehicle),
            message="Vehicle details updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Dealer Endpoints
# ============================================

@router.post("/dealers", response_model=dict)
async def create_dealer(
    data: schemas.DealerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new vehicle dealer"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        dealer_data = data.model_dump()
        dealer = service.create_dealer(dealer_data, current_user["user_id"])
        
        return success_response(
            data=schemas.DealerResponse.model_validate(dealer),
            message="Dealer created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dealers", response_model=dict)
async def list_dealers(
    is_active: Optional[bool] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List vehicle dealers"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        dealers = service.list_dealers(is_active=is_active, brand=brand)
        
        return success_response(
            data=[schemas.DealerResponse.model_validate(d) for d in dealers]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dealers/{dealer_id}", response_model=dict)
async def get_dealer(
    dealer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dealer by ID"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        dealer = service.get_dealer(dealer_id)
        
        if not dealer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dealer not found")
        
        return success_response(
            data=schemas.DealerResponse.model_validate(dealer)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# RTO & Hypothecation Endpoints
# ============================================

@router.post("/rto-tracking", response_model=dict)
async def create_rto_tracking(
    data: schemas.RTOTrackingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initialize RTO tracking for vehicle loan"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        rto_data = data.model_dump(exclude={"vehicle_loan_id", "loan_application_id"})
        rto_tracking = service.create_rto_tracking(
            vehicle_loan_id=data.vehicle_loan_id,
            loan_application_id=data.loan_application_id,
            rto_data=rto_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.RTOTrackingResponse.model_validate(rto_tracking),
            message="RTO tracking created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/rto-tracking/{rto_id}/status", response_model=dict)
async def update_hypothecation_status(
    rto_id: int,
    data: schemas.HypothecationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update hypothecation status"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude={"status"}, exclude_unset=True)
        rto_tracking = service.update_hypothecation_status(
            rto_tracking_id=rto_id,
            status=data.status,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not rto_tracking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RTO tracking not found")
        
        return success_response(
            data=schemas.RTOTrackingResponse.model_validate(rto_tracking),
            message="Hypothecation status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rto-tracking/pending", response_model=dict)
async def get_pending_hypothecations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all pending hypothecation cases"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        pending = service.get_pending_hypothecations()
        
        return success_response(
            data=[schemas.RTOTrackingResponse.model_validate(r) for r in pending]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/rto-tracking/noc-required", response_model=dict)
async def get_noc_required_cases(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cases where loan is closed but NOC not issued"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        cases = service.get_noc_required_cases()
        
        return success_response(
            data=[schemas.RTOTrackingResponse.model_validate(r) for r in cases]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Insurance Endpoints
# ============================================

@router.post("/insurance", response_model=dict)
async def create_insurance_policy(
    data: schemas.InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create insurance policy for vehicle loan"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        insurance_data = data.model_dump(exclude={"vehicle_loan_id", "loan_application_id", "customer_id"})
        insurance = service.create_insurance_policy(
            vehicle_loan_id=data.vehicle_loan_id,
            loan_application_id=data.loan_application_id,
            customer_id=data.customer_id,
            insurance_data=insurance_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.InsuranceResponse.model_validate(insurance),
            message="Insurance policy created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/insurance/{vehicle_loan_id}", response_model=dict)
async def get_vehicle_insurances(
    vehicle_loan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all insurance policies for a vehicle loan"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        insurances = service.get_vehicle_insurances(vehicle_loan_id)
        
        return success_response(
            data=[schemas.InsuranceResponse.model_validate(i) for i in insurances]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/insurance/expiring/{days}", response_model=dict)
async def get_expiring_insurances(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get insurance policies expiring in next X days"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        insurances = service.get_expiring_insurances(days)
        
        return success_response(
            data=[schemas.InsuranceExpiryAlert(
                id=i.id,
                policy_number=i.policy_number,
                vehicle_loan_id=i.vehicle_loan_id,
                customer_id=str(i.customer_id),
                policy_end_date=i.policy_end_date,
                days_to_expiry=(i.policy_end_date - date.today()).days,
                insurance_company=i.insurance_company
            ) for i in insurances]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/insurance/{insurance_id}/renewal-reminder", response_model=dict)
async def send_renewal_reminder(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send renewal reminder for insurance"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        result = service.send_renewal_reminder(insurance_id)
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(message="Renewal reminder sent successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/insurance/{insurance_id}/lien", response_model=dict)
async def update_lien_status(
    insurance_id: int,
    lien_marked: bool,
    lien_holder_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update lien marking status on insurance"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        insurance = service.update_lien_status(
            insurance_id=insurance_id,
            lien_marked=lien_marked,
            lien_holder_name=lien_holder_name,
            user_id=current_user["user_id"]
        )
        
        if not insurance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(
            data=schemas.InsuranceResponse.model_validate(insurance),
            message="Lien status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Insurance Claim Endpoints
# ============================================

@router.post("/insurance/claims", response_model=dict)
async def create_insurance_claim(
    data: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create insurance claim"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        claim_data = data.model_dump(exclude={"insurance_id"})
        claim = service.create_insurance_claim(
            insurance_id=data.insurance_id,
            claim_data=claim_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.ClaimResponse.model_validate(claim),
            message="Insurance claim created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/insurance/claims/{claim_id}/status", response_model=dict)
async def update_claim_status(
    claim_id: int,
    data: schemas.ClaimStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update insurance claim status"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude={"claim_status"}, exclude_unset=True)
        claim = service.update_claim_status(
            claim_id=claim_id,
            status=data.claim_status,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
        
        return success_response(
            data=schemas.ClaimResponse.model_validate(claim),
            message="Claim status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Vehicle Model Endpoints
# ============================================

@router.post("/models", response_model=dict)
async def create_vehicle_model(
    data: schemas.VehicleModelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create vehicle model master data"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        
        model_data = data.model_dump()
        model = service.create_vehicle_model(model_data)
        
        return success_response(
            data=schemas.VehicleModelResponse.model_validate(model),
            message="Vehicle model created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/models", response_model=dict)
async def search_vehicle_models(
    vehicle_type: Optional[schemas.VehicleTypeEnum] = None,
    manufacturer: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search vehicle models"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        models = service.search_vehicle_models(
            vehicle_type=vehicle_type,
            manufacturer=manufacturer,
            search=search
        )
        
        return success_response(
            data=[schemas.VehicleModelResponse.model_validate(m) for m in models]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Summary Endpoint
# ============================================

@router.get("/summary/{loan_application_id}", response_model=dict)
async def get_vehicle_loan_summary(
    loan_application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get complete vehicle loan summary"""
    try:
        service = VehicleLoanService(db, current_user["tenant_id"])
        summary = service.get_vehicle_loan_summary(loan_application_id)
        
        if not summary:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle loan not found")
        
        # Convert to response schema
        result = {
            "vehicle_details": schemas.VehicleDetailsResponse.model_validate(summary["vehicle_details"]) if summary.get("vehicle_details") else None,
            "rto_tracking": schemas.RTOTrackingResponse.model_validate(summary["rto_tracking"]) if summary.get("rto_tracking") else None,
            "active_insurance": schemas.InsuranceResponse.model_validate(summary["active_insurance"]) if summary.get("active_insurance") else None,
            "insurance_policies": [schemas.InsuranceResponse.model_validate(i) for i in summary.get("insurance_policies", [])],
            "hypothecation_status": summary.get("hypothecation_status"),
            "insurance_status": summary.get("insurance_status"),
            "is_compliant": summary["is_compliant"]
        }
        
        return success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""
eKYC Integration API Router
Endpoints for Aadhaar eKYC verification

Features:
- Initiate Aadhaar OTP
- Verify OTP and fetch eKYC data
- Auto-fill customer information
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .ekyc_service import EKYCService

router = APIRouter(prefix="/api/v1/ekyc", tags=["eKYC Verification"])


# Schemas
class InitiateEKYCRequest(BaseModel):
    customer_id: int
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    mobile_number: str = Field(..., min_length=10, max_length=10)


class VerifyOTPRequest(BaseModel):
    customer_id: int
    transaction_id: str
    otp: str = Field(..., min_length=6, max_length=6)


# Endpoints
@router.post("/initiate")
async def initiate_ekyc(
    request: InitiateEKYCRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Initiate eKYC by sending OTP to Aadhaar-registered mobile
    
    Returns transaction ID for OTP verification
    """
    try:
        service = EKYCService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('ekyc_config', {})
        )
        
        result = service.initiate_ekyc(
            customer_id=request.customer_id,
            aadhaar_number=request.aadhaar_number,
            mobile_number=request.mobile_number
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Verify OTP and fetch eKYC data
    
    Returns complete eKYC information including:
    - Name, DOB, Gender
    - Address
    - Photo
    """
    try:
        service = EKYCService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('ekyc_config', {})
        )
        
        result = service.verify_otp_and_fetch(
            customer_id=request.customer_id,
            transaction_id=request.transaction_id,
            otp=request.otp
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/data/{customer_id}")
async def get_ekyc_data(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get latest eKYC data for customer"""
    try:
        service = EKYCService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('ekyc_config', {})
        )
        
        data = service.get_ekyc_data(customer_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="No eKYC data found")
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

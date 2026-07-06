"""
eKYC (Aadhaar) API Router
FastAPI routes for Aadhaar eKYC operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .ekyc_service import EKYCService
from .schemas import (
    AadhaarOTPInitRequest, AadhaarOTPInitResponse,
    AadhaarOTPVerifyRequest, AadhaarOTPVerifyResponse,
    BiometricVerifyRequest, BiometricVerifyResponse
)

router = APIRouter(prefix="/customers/{customer_id}/ekyc", tags=["eKYC / Aadhaar"])


def get_ekyc_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> EKYCService:
    """Dependency to get eKYC service"""
    return EKYCService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# AADHAAR OTP VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/aadhaar/otp/initiate", response_model=AadhaarOTPInitResponse)
async def initiate_aadhaar_otp(
    customer_id: int,
    data: AadhaarOTPInitRequest,
    service: EKYCService = Depends(get_ekyc_service)
):
    """
    Initiate Aadhaar OTP verification
    
    Step 1 of OTP-based eKYC:
    - Sends OTP to Aadhaar-linked mobile number
    - Returns request_id for verification step
    - OTP valid for 10 minutes
    
    Requires:
    - Valid 12-digit Aadhaar number
    - Customer consent for eKYC
    """
    try:
        result = await service.initiate_aadhaar_otp(
            customer_id=customer_id,
            aadhaar_number=data.aadhaar_number
        )
        
        return AadhaarOTPInitResponse(
            success=True,
            request_id=result["request_id"],
            message=result.get("message", "OTP sent successfully"),
            expires_at=result["expires_at"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OTP: {str(e)}"
        )



@router.post("/aadhaar/otp/verify", response_model=AadhaarOTPVerifyResponse)
async def verify_aadhaar_otp(
    customer_id: int,
    data: AadhaarOTPVerifyRequest,
    service: EKYCService = Depends(get_ekyc_service)
):
    """
    Verify Aadhaar OTP and complete eKYC
    
    Step 2 of OTP-based eKYC:
    - Verifies OTP
    - Fetches eKYC data from UIDAI
    - Updates customer record with verified data
    - Marks Aadhaar as verified in KYC
    
    Returns:
    - Verified demographic data (name, DOB, address)
    - Photo (base64 encoded)
    - KYC completion status
    """
    try:
        result = await service.complete_aadhaar_otp_verification(
            customer_id=customer_id,
            aadhaar_number=data.aadhaar_number,
            otp=data.otp,
            request_id=data.request_id
        )
        
        if not result.get("verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "OTP verification failed")
            )
        
        return AadhaarOTPVerifyResponse(
            success=True,
            verified=True,
            message="Aadhaar verified successfully",
            ekyc_data={
                "name": result.get("name"),
                "date_of_birth": result.get("date_of_birth"),
                "gender": result.get("gender"),
                "address": result.get("address"),
                "photo": result.get("photo"),
                "mobile": result.get("mobile"),
                "email": result.get("email"),
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )



# ============================================================================
# BIOMETRIC VERIFICATION ENDPOINT
# ============================================================================

@router.post("/aadhaar/biometric", response_model=BiometricVerifyResponse)
async def verify_with_biometric(
    customer_id: int,
    data: BiometricVerifyRequest,
    service: EKYCService = Depends(get_ekyc_service)
):
    """
    Verify Aadhaar using biometric authentication
    
    Alternative to OTP-based verification:
    - Uses fingerprint or iris scan
    - More secure than OTP
    - Requires biometric device
    
    Process:
    1. Capture biometric data (fingerprint/iris)
    2. Send to UIDAI for authentication
    3. Fetch eKYC data on success
    4. Update customer record
    
    Returns:
    - Verified demographic data
    - Photo
    - KYC completion status
    """
    try:
        result = await service.verify_with_biometric(
            customer_id=customer_id,
            aadhaar_number=data.aadhaar_number,
            biometric_data=data.biometric_data
        )
        
        if not result.get("verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Biometric verification failed"
            )
        
        return BiometricVerifyResponse(
            success=True,
            verified=True,
            message="Biometric verification successful",
            ekyc_data={
                "name": result.get("name"),
                "date_of_birth": result.get("date_of_birth"),
                "gender": result.get("gender"),
                "address": result.get("address"),
                "photo": result.get("photo"),
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed biometric verification: {str(e)}"
        )

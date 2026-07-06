"""
DigiLocker API Router
FastAPI routes for DigiLocker document operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .digilocker_service import DigiLockerService
from .schemas import (
    DigiLockerAuthInitResponse, DigiLockerAuthCompleteRequest,
    DigiLockerAuthCompleteResponse, DigiLockerDocumentResponse,
    DigiLockerFetchDocumentRequest, CustomerDocumentResponse
)

router = APIRouter(prefix="/customers/{customer_id}/digilocker", tags=["DigiLocker"])


def get_digilocker_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DigiLockerService:
    """Dependency to get DigiLocker service"""
    return DigiLockerService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# DIGILOCKER OAUTH FLOW ENDPOINTS
# ============================================================================

@router.post("/authorize", response_model=DigiLockerAuthInitResponse)
async def initiate_digilocker_auth(
    customer_id: int,
    redirect_uri: str = Query(..., description="OAuth callback URL"),
    service: DigiLockerService = Depends(get_digilocker_service)
):
    """
    Initiate DigiLocker OAuth authorization
    
    Step 1 of DigiLocker integration:
    - Generates authorization URL
    - Returns URL to redirect customer
    - Provides state for CSRF protection
    
    Flow:
    1. Call this endpoint to get authorization URL
    2. Redirect customer to authorization URL
    3. Customer logs into DigiLocker and grants access
    4. DigiLocker redirects to your callback URL with code
    5. Call /complete endpoint with the code
    
    Requires:
    - Valid redirect_uri (must be registered with DigiLocker)
    """
    try:
        result = await service.initiate_authorization(
            customer_id=customer_id,
            redirect_uri=redirect_uri
        )
        
        return DigiLockerAuthInitResponse(
            authorization_url=result["authorization_url"],
            state=result["state"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate authorization: {str(e)}"
        )



@router.post("/complete", response_model=DigiLockerAuthCompleteResponse)
async def complete_digilocker_auth(
    customer_id: int,
    data: DigiLockerAuthCompleteRequest,
    service: DigiLockerService = Depends(get_digilocker_service)
):
    """
    Complete DigiLocker OAuth authorization
    
    Step 2 of DigiLocker integration:
    - Exchanges authorization code for access token
    - Fetches list of available documents
    - Returns access token and document list
    
    The access token should be stored temporarily (client-side)
    to fetch individual documents in subsequent calls.
    
    Security:
    - Validate state parameter matches the one from /authorize
    - Access token expires (typically 1 hour)
    - Use token only for fetching documents
    """
    try:
        result = await service.complete_authorization(
            customer_id=customer_id,
            code=data.code,
            redirect_uri=data.redirect_uri
        )
        
        return DigiLockerAuthCompleteResponse(
            success=True,
            access_token=result["access_token"],
            expires_in=result["expires_in"],
            documents=result["documents"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete authorization: {str(e)}"
        )


# ============================================================================
# DOCUMENT FETCH ENDPOINTS
# ============================================================================

@router.get("/documents", response_model=List[DigiLockerDocumentResponse])
async def get_available_documents(
    customer_id: int,
    access_token: str = Query(..., description="DigiLocker access token"),
    service: DigiLockerService = Depends(get_digilocker_service)
):
    """
    Get list of documents in customer's DigiLocker
    
    Returns all issued documents available:
    - Aadhaar Card
    - PAN Card
    - Driving License
    - Vehicle Registration
    - Education Certificates
    - And more...
    
    Each document includes:
    - URI (used to fetch the document)
    - Name
    - Type
    - Issuer
    - Issue date
    """
    try:
        documents = await service.get_available_documents(
            customer_id=customer_id,
            access_token=access_token
        )
        
        return [DigiLockerDocumentResponse(**doc) for doc in documents]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {str(e)}"
        )


@router.post("/documents/fetch", response_model=CustomerDocumentResponse)
async def fetch_and_store_document(
    customer_id: int,
    data: DigiLockerFetchDocumentRequest,
    service: DigiLockerService = Depends(get_digilocker_service)
):
    """
    Fetch document from DigiLocker and store in system
    
    Process:
    1. Fetch document content from DigiLocker
    2. Upload to file storage (S3/MinIO)
    3. Create document record in database
    4. Link to customer
    5. Log in timeline
    
    Parameters:
    - access_token: From /complete endpoint
    - document_uri: From /documents list (e.g., "AADHAAR-123456")
    - document_type_id: Document type UUID from master data
    
    Returns:
    - Created CustomerDocument record
    - Document can now be verified by operations team
    """
    try:
        document = await service.fetch_and_store_document(
            customer_id=customer_id,
            access_token=data.access_token,
            document_uri=data.document_uri,
            document_type_id=data.document_type_id
        )
        
        return document
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch and store document: {str(e)}"
        )

"""
Customer Document API Router
FastAPI routes for document operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.customer_models import DocumentStatus
from .document_service import CustomerDocumentService
from .schemas import CustomerDocumentCreate, CustomerDocumentResponse

router = APIRouter(prefix="/customers/{customer_id}/documents", tags=["Customer Documents"])


def get_document_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CustomerDocumentService:
    """Dependency to get document service"""
    return CustomerDocumentService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


@router.post("", response_model=CustomerDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    customer_id: int,
    data: CustomerDocumentCreate,
    service: CustomerDocumentService = Depends(get_document_service)
):
    """
    Upload customer document
    
    - Checks for duplicates
    - Sets status to PENDING
    - Records upload timestamp
    
    Note: document_url should be obtained from separate file upload endpoint
    """
    # Ensure customer_id matches
    data.customer_id = customer_id
    
    try:
        document = await service.create_document(data)
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[CustomerDocumentResponse])
async def get_documents(
    customer_id: int,
    document_type_id: Optional[int] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    service: CustomerDocumentService = Depends(get_document_service)
):
    """
    Get all documents for a customer
    
    Optional filters:
    - document_type_id: Filter by document type (Aadhaar, PAN, etc.)
    - status: Filter by status (pending, verified, rejected, expired)
    """
    doc_status = DocumentStatus[status.upper()] if status else None
    
    documents = await service.get_customer_documents(
        customer_id=customer_id,
        document_type_id=document_type_id,
        status=doc_status
    )
    return documents


@router.get("/pending", response_model=List[CustomerDocumentResponse])
async def get_pending_documents(
    customer_id: int,
    service: CustomerDocumentService = Depends(get_document_service)
):
    """Get all pending verification documents"""
    documents = await service.get_pending_verifications()
    # Filter for this customer
    return [d for d in documents if d.customer_id == customer_id]


@router.get("/{document_id}", response_model=CustomerDocumentResponse)
async def get_document(
    customer_id: int,
    document_id: int,
    service: CustomerDocumentService = Depends(get_document_service)
):
    """Get document by ID"""
    document = await service.get_document(document_id)
    if not document or document.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document


@router.post("/{document_id}/verify", response_model=CustomerDocumentResponse)
async def verify_document(
    customer_id: int,
    document_id: int,
    status: str = Query(..., description="Status: verified or rejected"),
    remarks: Optional[str] = Query(None, description="Verification remarks"),
    service: CustomerDocumentService = Depends(get_document_service)
):
    """
    Verify or reject a document
    
    - status: "verified" or "rejected"
    - remarks: Optional verification notes
    - Records verifier and timestamp
    """
    if status.lower() not in ["verified", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'verified' or 'rejected'"
        )
    
    doc_status = DocumentStatus.VERIFIED if status.lower() == "verified" else DocumentStatus.REJECTED
    
    document = await service.verify_document(document_id, doc_status, remarks)
    if not document or document.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document


@router.post("/{document_id}/check-expiry")
async def check_document_expiry(
    customer_id: int,
    document_id: int,
    service: CustomerDocumentService = Depends(get_document_service)
):
    """
    Check if document is expired
    
    - Compares expiry_date with current date
    - Updates document status if expired
    """
    is_expired = await service.check_expiry(document_id)
    return {
        "document_id": document_id,
        "is_expired": is_expired,
        "message": "Document is expired" if is_expired else "Document is valid"
    }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    customer_id: int,
    document_id: int,
    service: CustomerDocumentService = Depends(get_document_service)
):
    """Soft delete document"""
    success = await service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return None

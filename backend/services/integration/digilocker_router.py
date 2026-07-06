"""
DigiLocker Integration API Router
Endpoints for DigiLocker document fetching

Features:
- OAuth authorization
- Fetch government-verified documents
- Auto-verified status
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .digilocker_service import DigiLockerService

router = APIRouter(prefix="/api/v1/digilocker", tags=["DigiLocker Integration"])


# Schemas
class FetchDocumentsRequest(BaseModel):
    customer_id: int
    authorization_code: str


# Endpoints
@router.get("/authorize-url/{customer_id}")
async def get_authorization_url(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get DigiLocker OAuth authorization URL
    
    Redirect user to this URL to authorize access to their DigiLocker
    """
    try:
        service = DigiLockerService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('digilocker_config', {})
        )
        
        auth_url = service.get_authorization_url(customer_id)
        
        return {
            'authorization_url': auth_url,
            'customer_id': customer_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fetch-documents")
async def fetch_documents(
    request: FetchDocumentsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch documents from DigiLocker
    
    Call this after user authorizes access
    Returns list of fetched government-verified documents
    """
    try:
        service = DigiLockerService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('digilocker_config', {})
        )
        
        result = service.fetch_documents(
            customer_id=request.customer_id,
            authorization_code=request.authorization_code
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documents/{customer_id}")
async def get_customer_documents(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all DigiLocker documents for customer"""
    try:
        from backend.shared.database.integration_models import DigiLockerDocument
        
        documents = db.query(DigiLockerDocument).filter(
            DigiLockerDocument.customer_id == customer_id,
            DigiLockerDocument.tenant_id == current_user['tenant_id']
        ).all()
        
        return {
            'customer_id': customer_id,
            'documents': [
                {
                    'id': doc.id,
                    'document_type': doc.document_type,
                    'document_name': doc.document_name,
                    'issuer_name': doc.issuer_name,
                    'is_verified': doc.is_verified,
                    'verified_by_govt': doc.verified_by_govt,
                    'fetched_at': doc.fetched_at.isoformat() if doc.fetched_at else None
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

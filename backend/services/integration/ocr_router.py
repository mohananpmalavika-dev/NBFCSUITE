"""
OCR and Document Verification API Router
Endpoints for automated document processing

Features:
- OCR processing for documents
- Data extraction (Aadhaar, PAN, DL, Passport)
- Face matching
- Auto-verification
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .ocr_service import OCRService

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR & Document Verification"])


# Schemas
class ProcessDocumentRequest(BaseModel):
    customer_id: int
    document_id: int
    document_url: str
    document_type: str  # Aadhaar, PAN, DL, Passport


class FaceMatchRequest(BaseModel):
    source_image_url: str
    target_image_url: str


# Endpoints
@router.post("/process-document")
async def process_document(
    request: ProcessDocumentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Process document with OCR
    
    Automatically extracts data from identity documents
    Returns extracted data with confidence score
    """
    try:
        service = OCRService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('ocr_config', {})
        )
        
        result = service.process_document(
            customer_id=request.customer_id,
            document_id=request.document_id,
            document_url=request.document_url,
            document_type=request.document_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/face-match")
async def compare_faces(
    request: FaceMatchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Compare faces for verification
    
    Uses AWS Rekognition to match document photo with live photo/selfie
    """
    try:
        service = OCRService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('ocr_config', {})
        )
        
        result = service.compare_faces(
            source_image_url=request.source_image_url,
            target_image_url=request.target_image_url
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results/{document_id}")
async def get_ocr_result(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get OCR results for document"""
    try:
        from backend.shared.database.integration_models import DocumentOCRResult
        
        ocr_result = db.query(DocumentOCRResult).filter(
            DocumentOCRResult.document_id == document_id,
            DocumentOCRResult.tenant_id == current_user['tenant_id']
        ).first()
        
        if not ocr_result:
            raise HTTPException(status_code=404, detail="OCR result not found")
        
        return {
            'ocr_id': ocr_result.id,
            'document_id': document_id,
            'document_type': ocr_result.document_type,
            'ocr_status': ocr_result.ocr_status,
            'extracted_data': ocr_result.extracted_data,
            'confidence_score': float(ocr_result.confidence_score or 0),
            'auto_verified': ocr_result.auto_verified,
            'verification_status': ocr_result.verification_status,
            'processed_at': ocr_result.processed_at.isoformat() if ocr_result.processed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}/documents")
async def get_customer_ocr_results(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all OCR results for customer"""
    try:
        from backend.shared.database.integration_models import DocumentOCRResult
        
        results = db.query(DocumentOCRResult).filter(
            DocumentOCRResult.customer_id == customer_id,
            DocumentOCRResult.tenant_id == current_user['tenant_id']
        ).all()
        
        return {
            'customer_id': customer_id,
            'documents': [
                {
                    'ocr_id': r.id,
                    'document_id': r.document_id,
                    'document_type': r.document_type,
                    'auto_verified': r.auto_verified,
                    'confidence_score': float(r.confidence_score or 0),
                    'verification_status': r.verification_status
                }
                for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

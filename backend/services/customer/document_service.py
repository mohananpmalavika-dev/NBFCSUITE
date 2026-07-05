"""
Customer Document Service
Business logic for customer document operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, date

from backend.shared.database.customer_models import (
    CustomerDocument, DocumentStatus
)
from .schemas import CustomerDocumentCreate


class CustomerDocumentService:
    """Service for customer document operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_document(self, data: CustomerDocumentCreate) -> CustomerDocument:
        """Create new customer document"""
        
        # Check if document already exists
        existing = await self.get_by_document_number(
            data.customer_id, 
            data.document_type_id, 
            data.document_number
        )
        
        if existing:
            raise ValueError("Document with this number already exists for this customer")
        
        # Create document
        document = CustomerDocument(
            tenant_id=self.tenant_id,
            customer_id=data.customer_id,
            document_type_id=data.document_type_id,
            document_number=data.document_number,
            document_name=data.document_name,
            document_url=data.document_url,
            issue_date=data.issue_date,
            expiry_date=data.expiry_date,
            status=DocumentStatus.PENDING,
            uploaded_by=self.user_id,
            uploaded_date=datetime.utcnow(),
            created_by=self.user_id
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def get_customer_documents(
        self, 
        customer_id: int,
        document_type_id: Optional[int] = None,
        status: Optional[DocumentStatus] = None
    ) -> List[CustomerDocument]:
        """Get all documents for a customer"""
        
        query = select(CustomerDocument).where(
            and_(
                CustomerDocument.customer_id == customer_id,
                CustomerDocument.tenant_id == self.tenant_id,
                CustomerDocument.is_deleted == False
            )
        )
        
        if document_type_id:
            query = query.where(CustomerDocument.document_type_id == document_type_id)
        
        if status:
            query = query.where(CustomerDocument.status == status)
        
        query = query.order_by(CustomerDocument.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_document(self, document_id: int) -> Optional[CustomerDocument]:
        """Get document by ID"""
        query = select(CustomerDocument).where(
            and_(
                CustomerDocument.id == document_id,
                CustomerDocument.tenant_id == self.tenant_id,
                CustomerDocument.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_document_number(
        self, 
        customer_id: int, 
        document_type_id: int, 
        document_number: Optional[str]
    ) -> Optional[CustomerDocument]:
        """Check if document exists"""
        if not document_number:
            return None
        
        query = select(CustomerDocument).where(
            and_(
                CustomerDocument.customer_id == customer_id,
                CustomerDocument.document_type_id == document_type_id,
                CustomerDocument.document_number == document_number,
                CustomerDocument.tenant_id == self.tenant_id,
                CustomerDocument.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def verify_document(
        self, 
        document_id: int, 
        status: DocumentStatus, 
        remarks: Optional[str] = None
    ) -> Optional[CustomerDocument]:
        """Verify or reject a document"""
        document = await self.get_document(document_id)
        if not document:
            return None
        
        document.status = status
        document.verified_by = self.user_id
        document.verified_date = datetime.utcnow()
        document.verification_remarks = remarks
        document.updated_by = self.user_id
        document.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(document)
        
        return document
    
    async def delete_document(self, document_id: int) -> bool:
        """Soft delete document"""
        document = await self.get_document(document_id)
        if not document:
            return False
        
        document.is_deleted = True
        document.updated_by = self.user_id
        document.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def check_expiry(self, document_id: int) -> bool:
        """Check if document is expired"""
        document = await self.get_document(document_id)
        if not document or not document.expiry_date:
            return False
        
        is_expired = document.expiry_date < date.today()
        
        if is_expired and not document.is_expired:
            document.is_expired = True
            document.status = DocumentStatus.EXPIRED
            await self.db.commit()
        
        return is_expired
    
    async def get_pending_verifications(self) -> List[CustomerDocument]:
        """Get all documents pending verification"""
        query = select(CustomerDocument).where(
            and_(
                CustomerDocument.tenant_id == self.tenant_id,
                CustomerDocument.status == DocumentStatus.PENDING,
                CustomerDocument.is_deleted == False
            )
        ).order_by(CustomerDocument.uploaded_date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

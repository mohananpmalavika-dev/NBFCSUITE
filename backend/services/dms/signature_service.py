"""
Signature Service
Manages digital signatures and e-signature workflows
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.shared.database.dms_models import (
    DocumentSignature, Document, DocumentVersion,
    SignatureStatus, SignatureType
)
from .schemas import (
    SignatureRequest, SignatureAction, SignatureResponse
)


class SignatureService:
    """Service for e-signature management"""

    def __init__(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tenant_id: str
    ):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def request_signature(
        self,
        signature_data: SignatureRequest
    ) -> SignatureResponse:
        """
        Request a signature on a document
        
        Args:
            signature_data: Signature request details
            
        Returns:
            SignatureResponse: Created signature request
        """
        # Verify document exists
        doc_query = select(Document).where(
            and_(
                Document.id == signature_data.document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        doc_result = await self.db.execute(doc_query)
        document = doc_result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Get current version
        if not document.current_version_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no version to sign"
            )

        # Get signer information
        from backend.shared.database.models import User
        user_query = select(User).where(User.id == signature_data.signer_id)
        user_result = await self.db.execute(user_query)
        signer = user_result.scalar_one_or_none()

        if not signer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signer not found"
            )

        # Set expiry if not provided (default 7 days)
        expires_at = signature_data.expires_at or (datetime.utcnow() + timedelta(days=7))

        # Create signature request
        signature = DocumentSignature(
            tenant_id=self.tenant_id,
            document_id=signature_data.document_id,
            version_id=document.current_version_id,
            signer_id=signature_data.signer_id,
            signer_name=signer.full_name or signer.username,
            signer_email=signer.email,
            signer_title=getattr(signer, 'title', None),
            signature_type=signature_data.signature_type,
            status=SignatureStatus.PENDING,
            expires_at=expires_at,
            created_by=self.user_id
        )
        self.db.add(signature)
        await self.db.commit()
        await self.db.refresh(signature)

        return SignatureResponse.model_validate(signature)

    async def get_signature(self, signature_id: uuid.UUID) -> SignatureResponse:
        """Get signature by ID"""
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.id == signature_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        signature = result.scalar_one_or_none()

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )

        return SignatureResponse.model_validate(signature)

    async def process_signature(
        self,
        signature_id: uuid.UUID,
        action: SignatureAction
    ) -> SignatureResponse:
        """
        Process a signature (sign/reject)
        
        Args:
            signature_id: Signature ID
            action: Signature action
            
        Returns:
            SignatureResponse: Updated signature
        """
        # Get signature
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.id == signature_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        signature = result.scalar_one_or_none()

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )

        # Check if user is the signer
        if signature.signer_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to process this signature"
            )

        # Check if already processed
        if signature.status != SignatureStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Signature already {signature.status}"
            )

        # Check expiry
        if signature.expires_at and signature.expires_at < datetime.utcnow():
            signature.status = SignatureStatus.EXPIRED
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature request has expired"
            )

        # Process action
        signature.status = action.status
        signature.verification_method = action.verification_method

        if action.status == SignatureStatus.SIGNED:
            signature.signature_data = action.signature_data
            signature.signed_at = datetime.utcnow()
            
            # TODO: Generate signature hash for verification
            import hashlib
            if action.signature_data:
                signature.signature_hash = hashlib.sha256(
                    action.signature_data.encode()
                ).hexdigest()

        elif action.status == SignatureStatus.REJECTED:
            signature.rejection_reason = action.rejection_reason
            signature.rejected_at = datetime.utcnow()

        signature.updated_by = self.user_id
        await self.db.commit()
        await self.db.refresh(signature)

        return SignatureResponse.model_validate(signature)

    async def get_document_signatures(
        self,
        document_id: uuid.UUID
    ) -> List[SignatureResponse]:
        """Get all signatures for a document"""
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.document_id == document_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        ).order_by(DocumentSignature.created_at.desc())

        result = await self.db.execute(query)
        signatures = result.scalars().all()

        return [SignatureResponse.model_validate(s) for s in signatures]

    async def get_pending_signatures(
        self,
        signer_id: Optional[uuid.UUID] = None
    ) -> List[SignatureResponse]:
        """Get pending signatures for a user"""
        target_user = signer_id or self.user_id

        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.signer_id == target_user,
                DocumentSignature.status == SignatureStatus.PENDING,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        ).order_by(DocumentSignature.expires_at.asc())

        result = await self.db.execute(query)
        signatures = result.scalars().all()

        # Check for expired signatures
        now = datetime.utcnow()
        for signature in signatures:
            if signature.expires_at and signature.expires_at < now:
                signature.status = SignatureStatus.EXPIRED
                signature.updated_by = self.user_id

        await self.db.commit()

        # Filter out expired ones
        active_signatures = [s for s in signatures if s.status == SignatureStatus.PENDING]

        return [SignatureResponse.model_validate(s) for s in active_signatures]

    async def cancel_signature(
        self,
        signature_id: uuid.UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a signature request"""
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.id == signature_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        signature = result.scalar_one_or_none()

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )

        # Check if already processed
        if signature.status != SignatureStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel signature with status {signature.status}"
            )

        # Soft delete
        signature.is_deleted = True
        signature.deleted_at = datetime.utcnow()
        signature.deleted_by = self.user_id
        signature.rejection_reason = reason or "Cancelled by requester"

        await self.db.commit()
        return True

    async def resend_signature_request(
        self,
        signature_id: uuid.UUID,
        new_expiry: Optional[datetime] = None
    ) -> SignatureResponse:
        """Resend/extend a signature request"""
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.id == signature_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        signature = result.scalar_one_or_none()

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )

        # Only resend if pending or expired
        if signature.status not in [SignatureStatus.PENDING, SignatureStatus.EXPIRED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot resend signature with status {signature.status}"
            )

        # Update expiry and reset status
        signature.expires_at = new_expiry or (datetime.utcnow() + timedelta(days=7))
        signature.status = SignatureStatus.PENDING
        signature.updated_by = self.user_id

        await self.db.commit()
        await self.db.refresh(signature)

        # TODO: Send notification to signer

        return SignatureResponse.model_validate(signature)

    async def verify_signature(
        self,
        signature_id: uuid.UUID
    ) -> dict:
        """
        Verify the integrity of a signature
        
        Returns:
            dict: Verification result with details
        """
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.id == signature_id,
                DocumentSignature.tenant_id == self.tenant_id,
                DocumentSignature.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        signature = result.scalar_one_or_none()

        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )

        # Check if signed
        if signature.status != SignatureStatus.SIGNED:
            return {
                "valid": False,
                "reason": f"Signature status is {signature.status}",
                "signature_id": str(signature.id),
                "signer_name": signature.signer_name,
                "signed_at": None
            }

        # Verify hash (if available)
        hash_valid = True
        if signature.signature_data and signature.signature_hash:
            import hashlib
            calculated_hash = hashlib.sha256(
                signature.signature_data.encode()
            ).hexdigest()
            hash_valid = (calculated_hash == signature.signature_hash)

        # Check certificate validity (for qualified signatures)
        cert_valid = True
        if signature.signature_type == SignatureType.QUALIFIED:
            if signature.certificate_valid_until:
                cert_valid = signature.certificate_valid_until > datetime.utcnow()

        return {
            "valid": hash_valid and cert_valid,
            "signature_id": str(signature.id),
            "signer_name": signature.signer_name,
            "signer_email": signature.signer_email,
            "signature_type": signature.signature_type,
            "signed_at": signature.signed_at,
            "hash_valid": hash_valid,
            "certificate_valid": cert_valid,
            "certificate_issuer": signature.certificate_issuer,
            "certificate_expiry": signature.certificate_valid_until
        }

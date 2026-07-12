"""
Document Management Service
Core business logic for document operations
"""

import os
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from backend.shared.database.dms_models import (
    Document, DocumentVersion, DocumentStatus, DocumentType,
    DocumentCategory, AccessLevel, DocumentComment, DocumentAuditLog
)
from .schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentListResponse, DocumentSearchRequest, DocumentVersionCreate,
    DocumentVersionResponse, CommentCreate, CommentResponse,
    AuditLogResponse, DocumentStatistics, UserDocumentStats
)


class DocumentService:
    """Service for document management operations"""

    # File upload configuration
    ALLOWED_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.zip', '.rar', '.7z', '.msg', '.eml'
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    STORAGE_BASE_PATH = "dms_storage"

    def __init__(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tenant_id: str
    ):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id
        self._ensure_storage_directory()

    def _ensure_storage_directory(self):
        """Ensure storage directory exists"""
        storage_path = Path(self.STORAGE_BASE_PATH) / self.tenant_id
        storage_path.mkdir(parents=True, exist_ok=True)

    def _generate_document_number(self) -> str:
        """Generate unique document number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"DOC-{timestamp}-{random_suffix}"

    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()

    def _get_storage_path(self, document_id: uuid.UUID, version: int, filename: str) -> Path:
        """Get storage path for document version"""
        # Organize by tenant/document_id/version/filename
        storage_path = (
            Path(self.STORAGE_BASE_PATH) /
            self.tenant_id /
            str(document_id) /
            f"v{version}"
        )
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path / filename

    def _validate_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file"""
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension {file_ext} not allowed"
        return True, None

    async def _log_audit(
        self,
        document_id: uuid.UUID,
        action: str,
        action_category: str,
        description: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        version_id: Optional[uuid.UUID] = None
    ):
        """Log document audit trail"""
        audit_log = DocumentAuditLog(
            tenant_id=self.tenant_id,
            document_id=document_id,
            version_id=version_id,
            action=action,
            action_category=action_category,
            description=description,
            user_id=self.user_id,
            old_values=old_values,
            new_values=new_values,
            created_by=self.user_id
        )
        self.db.add(audit_log)

    async def create_document(
        self,
        document_data: DocumentCreate,
        file: Optional[UploadFile] = None
    ) -> DocumentResponse:
        """
        Create a new document
        
        Args:
            document_data: Document metadata
            file: Optional file upload
            
        Returns:
            DocumentResponse: Created document
        """
        # Validate file if provided
        if file:
            is_valid, error_msg = self._validate_file(file)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # Read file content
            content = await file.read()
            if len(content) > self.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE / (1024 * 1024)} MB"
                )

        # Generate document number
        document_number = self._generate_document_number()

        # Create document
        document = Document(
            tenant_id=self.tenant_id,
            document_number=document_number,
            title=document_data.title,
            description=document_data.description,
            document_type=document_data.document_type,
            category=document_data.category,
            access_level=document_data.access_level,
            status=DocumentStatus.DRAFT,
            owner_id=self.user_id,
            department=document_data.department,
            tags=document_data.tags,
            custom_fields=document_data.custom_fields,
            effective_date=document_data.effective_date,
            expiry_date=document_data.expiry_date,
            review_date=document_data.review_date,
            parent_document_id=document_data.parent_document_id,
            reference_number=document_data.reference_number,
            created_by=self.user_id
        )

        # Handle file upload
        if file:
            file_hash = self._calculate_file_hash(content)
            storage_path = self._get_storage_path(document.id, 1, file.filename)
            
            # Save file to disk
            with open(storage_path, 'wb') as f:
                f.write(content)
            
            # Update document with file info
            document.file_name = file.filename
            document.file_type = file.content_type
            document.file_size = len(content)
            document.file_path = str(storage_path)
            document.file_hash = file_hash
            document.version_number = 1

            # Create version record
            version = DocumentVersion(
                tenant_id=self.tenant_id,
                document_id=document.id,
                version_number=1,
                file_name=file.filename,
                file_type=file.content_type,
                file_size=len(content),
                file_path=str(storage_path),
                file_hash=file_hash,
                version_notes="Initial version",
                is_major_version=True,
                uploaded_by=self.user_id,
                created_by=self.user_id
            )
            self.db.add(version)
            document.current_version_id = version.id

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        # Log audit
        await self._log_audit(
            document_id=document.id,
            action="created",
            action_category="modification",
            description=f"Document '{document.title}' created"
        )
        await self.db.commit()

        return DocumentResponse.model_validate(document)

    async def get_document(self, document_id: uuid.UUID) -> Optional[DocumentResponse]:
        """Get document by ID with access control"""
        query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Update view count
        document.view_count += 1
        document.last_accessed_at = datetime.utcnow()
        document.last_accessed_by = self.user_id
        await self.db.commit()

        # Log audit
        await self._log_audit(
            document_id=document.id,
            action="viewed",
            action_category="access",
            description=f"Document '{document.title}' viewed"
        )
        await self.db.commit()

        return DocumentResponse.model_validate(document)

    async def update_document(
        self,
        document_id: uuid.UUID,
        document_data: DocumentUpdate
    ) -> DocumentResponse:
        """Update document metadata"""
        # Get document
        query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check if document is locked
        if document.is_locked and document.locked_by != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Document is locked by another user"
            )

        # Store old values for audit
        old_values = {}
        new_values = {}

        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and hasattr(document, field):
                old_values[field] = getattr(document, field)
                setattr(document, field, value)
                new_values[field] = value

        document.updated_by = self.user_id
        await self.db.commit()
        await self.db.refresh(document)

        # Log audit
        await self._log_audit(
            document_id=document.id,
            action="updated",
            action_category="modification",
            description=f"Document '{document.title}' updated",
            old_values=old_values,
            new_values=new_values
        )
        await self.db.commit()

        return DocumentResponse.model_validate(document)

    async def upload_version(
        self,
        document_id: uuid.UUID,
        file: UploadFile,
        version_data: DocumentVersionCreate
    ) -> DocumentVersionResponse:
        """Upload a new version of the document"""
        # Validate file
        is_valid, error_msg = self._validate_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Get document
        query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Read file content
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum limit"
            )

        # Calculate new version number
        new_version_number = document.version_number + 1
        file_hash = self._calculate_file_hash(content)
        storage_path = self._get_storage_path(document.id, new_version_number, file.filename)

        # Save file to disk
        with open(storage_path, 'wb') as f:
            f.write(content)

        # Create version record
        version = DocumentVersion(
            tenant_id=self.tenant_id,
            document_id=document.id,
            version_number=new_version_number,
            file_name=file.filename,
            file_type=file.content_type,
            file_size=len(content),
            file_path=str(storage_path),
            file_hash=file_hash,
            version_notes=version_data.version_notes,
            is_major_version=version_data.is_major_version,
            changes_summary=version_data.changes_summary,
            uploaded_by=self.user_id,
            created_by=self.user_id
        )
        self.db.add(version)

        # Update document
        document.version_number = new_version_number
        document.file_name = file.filename
        document.file_type = file.content_type
        document.file_size = len(content)
        document.file_path = str(storage_path)
        document.file_hash = file_hash
        document.current_version_id = version.id
        document.updated_by = self.user_id

        await self.db.commit()
        await self.db.refresh(version)

        # Log audit
        await self._log_audit(
            document_id=document.id,
            version_id=version.id,
            action="version_uploaded",
            action_category="modification",
            description=f"Version {new_version_number} uploaded for '{document.title}'"
        )
        await self.db.commit()

        return DocumentVersionResponse.model_validate(version)

    async def search_documents(
        self,
        search_params: DocumentSearchRequest
    ) -> DocumentListResponse:
        """Search documents with filters"""
        query = select(Document).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )

        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.where(
                or_(
                    Document.title.ilike(search_term),
                    Document.description.ilike(search_term),
                    Document.document_number.ilike(search_term)
                )
            )

        if search_params.document_type:
            query = query.where(Document.document_type == search_params.document_type)

        if search_params.category:
            query = query.where(Document.category == search_params.category)

        if search_params.status:
            query = query.where(Document.status == search_params.status)

        if search_params.access_level:
            query = query.where(Document.access_level == search_params.access_level)

        if search_params.department:
            query = query.where(Document.department == search_params.department)

        if search_params.owner_id:
            query = query.where(Document.owner_id == search_params.owner_id)

        if search_params.from_date:
            query = query.where(Document.created_at >= search_params.from_date)

        if search_params.to_date:
            query = query.where(Document.created_at <= search_params.to_date)

        if search_params.expiring_soon:
            thirty_days_later = datetime.utcnow() + timedelta(days=30)
            query = query.where(
                and_(
                    Document.expiry_date.isnot(None),
                    Document.expiry_date <= thirty_days_later
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination and sorting
        query = query.order_by(desc(Document.created_at))
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)

        # Execute query
        result = await self.db.execute(query)
        documents = result.scalars().all()

        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            total=total,
            page=search_params.page,
            page_size=search_params.page_size
        )

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """Soft delete document"""
        query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Soft delete
        document.is_deleted = True
        document.deleted_at = datetime.utcnow()
        document.deleted_by = self.user_id
        document.status = DocumentStatus.DELETED

        await self.db.commit()

        # Log audit
        await self._log_audit(
            document_id=document.id,
            action="deleted",
            action_category="modification",
            description=f"Document '{document.title}' deleted"
        )
        await self.db.commit()

        return True

    async def get_document_versions(
        self,
        document_id: uuid.UUID
    ) -> List[DocumentVersionResponse]:
        """Get all versions of a document"""
        query = select(DocumentVersion).where(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.tenant_id == self.tenant_id,
                DocumentVersion.is_deleted == False
            )
        ).order_by(desc(DocumentVersion.version_number))

        result = await self.db.execute(query)
        versions = result.scalars().all()

        return [DocumentVersionResponse.model_validate(v) for v in versions]

    async def add_comment(self, comment_data: CommentCreate) -> CommentResponse:
        """Add comment to document"""
        comment = DocumentComment(
            tenant_id=self.tenant_id,
            document_id=comment_data.document_id,
            version_id=comment_data.version_id,
            parent_comment_id=comment_data.parent_comment_id,
            comment_text=comment_data.comment_text,
            comment_type=comment_data.comment_type,
            author_id=self.user_id,
            page_number=comment_data.page_number,
            position_x=comment_data.position_x,
            position_y=comment_data.position_y,
            created_by=self.user_id
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)

        return CommentResponse.model_validate(comment)

    async def get_document_statistics(self) -> DocumentStatistics:
        """Get document statistics for the tenant"""
        # Total documents
        total_query = select(func.count(Document.id)).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_documents = total_result.scalar()

        # By status
        status_query = select(
            Document.status,
            func.count(Document.id)
        ).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        ).group_by(Document.status)
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}

        # By type
        type_query = select(
            Document.document_type,
            func.count(Document.id)
        ).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        ).group_by(Document.document_type)
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}

        # By category
        category_query = select(
            Document.category,
            func.count(Document.id)
        ).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        ).group_by(Document.category)
        category_result = await self.db.execute(category_query)
        by_category = {row[0]: row[1] for row in category_result.all()}

        # Expiring soon
        thirty_days_later = datetime.utcnow() + timedelta(days=30)
        expiring_query = select(func.count(Document.id)).where(
            and_(
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False,
                Document.expiry_date.isnot(None),
                Document.expiry_date <= thirty_days_later
            )
        )
        expiring_result = await self.db.execute(expiring_query)
        expiring_soon = expiring_result.scalar()

        return DocumentStatistics(
            total_documents=total_documents,
            by_status=by_status,
            by_type=by_type,
            by_category=by_category,
            expiring_soon=expiring_soon,
            pending_approvals=0,  # Implemented in workflow service
            pending_signatures=0  # Implemented in signature service
        )

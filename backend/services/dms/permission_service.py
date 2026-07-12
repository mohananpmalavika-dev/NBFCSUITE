"""
Permission Service
Manages document access control and permissions
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from backend.shared.database.dms_models import (
    DocumentPermission, Document
)
from .schemas import PermissionCreate, PermissionResponse


class PermissionService:
    """Service for document permission management"""

    def __init__(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tenant_id: str
    ):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def grant_permission(
        self,
        permission_data: PermissionCreate
    ) -> PermissionResponse:
        """
        Grant permission to a user, role, or department
        
        Args:
            permission_data: Permission details
            
        Returns:
            PermissionResponse: Created permission
        """
        # Verify document exists
        doc_query = select(Document).where(
            and_(
                Document.id == permission_data.document_id,
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

        # Check if permission already exists
        existing_query = select(DocumentPermission).where(
            and_(
                DocumentPermission.document_id == permission_data.document_id,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        )

        if permission_data.user_id:
            existing_query = existing_query.where(
                DocumentPermission.user_id == permission_data.user_id
            )
        elif permission_data.role_id:
            existing_query = existing_query.where(
                DocumentPermission.role_id == permission_data.role_id
            )
        elif permission_data.department:
            existing_query = existing_query.where(
                DocumentPermission.department == permission_data.department
            )

        existing_result = await self.db.execute(existing_query)
        existing_permission = existing_result.scalar_one_or_none()

        if existing_permission:
            # Update existing permission
            existing_permission.can_view = permission_data.can_view
            existing_permission.can_download = permission_data.can_download
            existing_permission.can_edit = permission_data.can_edit
            existing_permission.can_delete = permission_data.can_delete
            existing_permission.can_share = permission_data.can_share
            existing_permission.can_approve = permission_data.can_approve
            existing_permission.valid_from = permission_data.valid_from
            existing_permission.valid_until = permission_data.valid_until
            existing_permission.grant_reason = permission_data.grant_reason
            existing_permission.updated_by = self.user_id

            await self.db.commit()
            await self.db.refresh(existing_permission)
            return PermissionResponse.model_validate(existing_permission)

        # Create new permission
        permission = DocumentPermission(
            tenant_id=self.tenant_id,
            document_id=permission_data.document_id,
            user_id=permission_data.user_id,
            role_id=permission_data.role_id,
            department=permission_data.department,
            can_view=permission_data.can_view,
            can_download=permission_data.can_download,
            can_edit=permission_data.can_edit,
            can_delete=permission_data.can_delete,
            can_share=permission_data.can_share,
            can_approve=permission_data.can_approve,
            valid_from=permission_data.valid_from,
            valid_until=permission_data.valid_until,
            granted_by=self.user_id,
            grant_reason=permission_data.grant_reason,
            created_by=self.user_id
        )
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return PermissionResponse.model_validate(permission)

    async def revoke_permission(
        self,
        permission_id: uuid.UUID
    ) -> bool:
        """Revoke a permission"""
        query = select(DocumentPermission).where(
            and_(
                DocumentPermission.id == permission_id,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        permission = result.scalar_one_or_none()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        # Soft delete
        permission.is_deleted = True
        permission.deleted_at = datetime.utcnow()
        permission.deleted_by = self.user_id

        await self.db.commit()
        return True

    async def get_document_permissions(
        self,
        document_id: uuid.UUID
    ) -> List[PermissionResponse]:
        """Get all permissions for a document"""
        query = select(DocumentPermission).where(
            and_(
                DocumentPermission.document_id == document_id,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        ).order_by(DocumentPermission.created_at.desc())

        result = await self.db.execute(query)
        permissions = result.scalars().all()

        return [PermissionResponse.model_validate(p) for p in permissions]

    async def check_permission(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        permission_type: str
    ) -> bool:
        """
        Check if a user has a specific permission on a document
        
        Args:
            document_id: Document ID
            user_id: User ID
            permission_type: One of: view, download, edit, delete, share, approve
            
        Returns:
            bool: True if user has permission
        """
        # Get document
        doc_query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        doc_result = await self.db.execute(doc_query)
        document = doc_result.scalar_one_or_none()

        if not document:
            return False

        # Owner always has full permission
        if document.owner_id == user_id:
            return True

        # Check explicit user permission
        user_query = select(DocumentPermission).where(
            and_(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        )

        # Check validity period
        now = datetime.utcnow()
        user_query = user_query.where(
            or_(
                DocumentPermission.valid_from.is_(None),
                DocumentPermission.valid_from <= now
            )
        ).where(
            or_(
                DocumentPermission.valid_until.is_(None),
                DocumentPermission.valid_until >= now
            )
        )

        user_result = await self.db.execute(user_query)
        user_permission = user_result.scalar_one_or_none()

        if user_permission:
            # Check specific permission
            permission_field = f"can_{permission_type}"
            if hasattr(user_permission, permission_field):
                return getattr(user_permission, permission_field)

        # TODO: Check role-based and department-based permissions
        # This would require user role and department information

        # Default deny
        return False

    async def get_user_accessible_documents(
        self,
        user_id: Optional[uuid.UUID] = None,
        permission_type: str = "view"
    ) -> List[uuid.UUID]:
        """
        Get list of document IDs accessible to a user
        
        Args:
            user_id: User ID (defaults to current user)
            permission_type: Permission type to check
            
        Returns:
            List[uuid.UUID]: List of accessible document IDs
        """
        target_user = user_id or self.user_id
        now = datetime.utcnow()

        # Get documents owned by user
        owned_query = select(Document.id).where(
            and_(
                Document.owner_id == target_user,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        owned_result = await self.db.execute(owned_query)
        owned_ids = [row[0] for row in owned_result.all()]

        # Get documents with explicit permission
        permission_field = f"can_{permission_type}"
        perm_query = select(DocumentPermission.document_id).where(
            and_(
                DocumentPermission.user_id == target_user,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        ).where(
            or_(
                DocumentPermission.valid_from.is_(None),
                DocumentPermission.valid_from <= now
            )
        ).where(
            or_(
                DocumentPermission.valid_until.is_(None),
                DocumentPermission.valid_until >= now
            )
        )

        # Filter by permission type
        if permission_type == "view":
            perm_query = perm_query.where(DocumentPermission.can_view == True)
        elif permission_type == "download":
            perm_query = perm_query.where(DocumentPermission.can_download == True)
        elif permission_type == "edit":
            perm_query = perm_query.where(DocumentPermission.can_edit == True)
        elif permission_type == "delete":
            perm_query = perm_query.where(DocumentPermission.can_delete == True)
        elif permission_type == "share":
            perm_query = perm_query.where(DocumentPermission.can_share == True)
        elif permission_type == "approve":
            perm_query = perm_query.where(DocumentPermission.can_approve == True)

        perm_result = await self.db.execute(perm_query)
        perm_ids = [row[0] for row in perm_result.all()]

        # Combine and deduplicate
        all_ids = list(set(owned_ids + perm_ids))
        return all_ids

    async def bulk_grant_permission(
        self,
        document_ids: List[uuid.UUID],
        user_id: Optional[uuid.UUID] = None,
        role_id: Optional[uuid.UUID] = None,
        department: Optional[str] = None,
        permissions: dict = None
    ) -> int:
        """
        Grant permissions to multiple documents at once
        
        Args:
            document_ids: List of document IDs
            user_id: Target user ID
            role_id: Target role ID
            department: Target department
            permissions: Dict of permissions to grant
            
        Returns:
            int: Number of permissions created
        """
        if not any([user_id, role_id, department]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one target (user, role, department) must be specified"
            )

        permissions = permissions or {
            "can_view": True,
            "can_download": False,
            "can_edit": False,
            "can_delete": False,
            "can_share": False,
            "can_approve": False
        }

        count = 0
        for document_id in document_ids:
            try:
                permission_data = PermissionCreate(
                    document_id=document_id,
                    user_id=user_id,
                    role_id=role_id,
                    department=department,
                    **permissions
                )
                await self.grant_permission(permission_data)
                count += 1
            except Exception:
                # Continue on error
                pass

        return count

    async def update_permission(
        self,
        permission_id: uuid.UUID,
        updates: dict
    ) -> PermissionResponse:
        """Update an existing permission"""
        query = select(DocumentPermission).where(
            and_(
                DocumentPermission.id == permission_id,
                DocumentPermission.tenant_id == self.tenant_id,
                DocumentPermission.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        permission = result.scalar_one_or_none()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        # Update fields
        for field, value in updates.items():
            if hasattr(permission, field):
                setattr(permission, field, value)

        permission.updated_by = self.user_id
        await self.db.commit()
        await self.db.refresh(permission)

        return PermissionResponse.model_validate(permission)

"""
Template Service

Service for managing notification templates with variable support.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.shared.database.notification_models import NotificationTemplate
from backend.services.notification.schemas import (
    NotificationTemplateCreate,
    NotificationTemplateUpdate
)


class TemplateService:
    """Service for managing notification templates"""

    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    async def create_template(
        self,
        data: NotificationTemplateCreate
    ) -> NotificationTemplate:
        """Create a new notification template"""
        # Check if code already exists
        existing = await self.get_template_by_code(data.template_code)
        if existing:
            raise ValueError(f"Template with code '{data.template_code}' already exists")
        
        template = NotificationTemplate(
            template_code=data.template_code,
            template_name=data.template_name,
            channel=data.channel.value,
            category=data.category.value,
            subject=data.subject,
            body_template=data.body_template,
            variables=data.variables,
            example_data=data.example_data,
            priority=data.priority.value,
            retry_enabled=data.retry_enabled,
            max_retries=data.max_retries,
            retry_interval_seconds=data.retry_interval_seconds,
            is_active=data.is_active,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template

    async def update_template(
        self,
        template_id: int,
        data: NotificationTemplateUpdate
    ) -> NotificationTemplate:
        """Update an existing template"""
        template = await self.get_template(template_id)
        
        if not template:
            raise ValueError("Template not found")
        
        # Update fields
        if data.template_name is not None:
            template.template_name = data.template_name
        if data.subject is not None:
            template.subject = data.subject
        if data.body_template is not None:
            template.body_template = data.body_template
        if data.variables is not None:
            template.variables = data.variables
        if data.example_data is not None:
            template.example_data = data.example_data
        if data.priority is not None:
            template.priority = data.priority.value
        if data.retry_enabled is not None:
            template.retry_enabled = data.retry_enabled
        if data.max_retries is not None:
            template.max_retries = data.max_retries
        if data.retry_interval_seconds is not None:
            template.retry_interval_seconds = data.retry_interval_seconds
        if data.is_active is not None:
            template.is_active = data.is_active
        
        template.updated_by = self.user_id
        template.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(template)
        
        return template

    async def get_template(self, template_id: int) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.id == template_id,
                NotificationTemplate.tenant_id == self.tenant_id,
                NotificationTemplate.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_template_by_code(self, template_code: str) -> Optional[NotificationTemplate]:
        """Get template by code"""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.template_code == template_code,
                NotificationTemplate.tenant_id == self.tenant_id,
                NotificationTemplate.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        channel: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[NotificationTemplate], int]:
        """List templates with filters"""
        conditions = [
            NotificationTemplate.tenant_id == self.tenant_id,
            NotificationTemplate.is_deleted == False
        ]
        
        if channel:
            conditions.append(NotificationTemplate.channel == channel)
        
        if category:
            conditions.append(NotificationTemplate.category == category)
        
        if is_active is not None:
            conditions.append(NotificationTemplate.is_active == is_active)
        
        # Count query
        count_query = select(func.count(NotificationTemplate.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Data query
        query = select(NotificationTemplate).where(
            and_(*conditions)
        ).order_by(
            NotificationTemplate.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        templates = list(result.scalars().all())
        
        return templates, total

    async def delete_template(self, template_id: int) -> bool:
        """Soft delete a template"""
        template = await self.get_template(template_id)
        
        if not template:
            return False
        
        template.is_deleted = True
        template.is_active = False
        template.updated_by = self.user_id
        template.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return True


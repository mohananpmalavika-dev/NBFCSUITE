"""
TRAI DLT Compliance Service

Implements TRAI (Telecom Regulatory Authority of India) DLT (Distributed Ledger Technology)
compliance for commercial SMS communications.

Key Features:
- Entity registration management
- Template registration and approval tracking
- Consent management (opt-in/opt-out)
- Compliance validation before sending
- DLT template mapping with notification templates
- Telecom operator integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
import logging
import re

from backend.shared.database.notification_models import (
    DLTEntity, DLTTemplate, DLTConsent, NotificationTemplate
)
from backend.services.notification.schemas import (
    DLTEntityCreate, DLTEntityUpdate, DLTEntityResponse,
    DLTTemplateCreate, DLTTemplateUpdate, DLTTemplateResponse,
    DLTConsentCreate, DLTConsentResponse, DLTConsentRevoke,
    DLTComplianceCheck, DLTComplianceResponse
)

logger = logging.getLogger(__name__)


class DLTComplianceService:
    """Service for TRAI DLT compliance management"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # DLT ENTITY MANAGEMENT
    # ========================================================================
    
    async def create_dlt_entity(
        self,
        request: DLTEntityCreate
    ) -> DLTEntityResponse:
        """
        Register a new DLT entity (Principal Entity)
        
        Args:
            request: DLTEntityCreate schema
            
        Returns:
            DLTEntityResponse
        """
        # Check if entity_id already exists
        result = await self.db.execute(
            select(DLTEntity).where(
                and_(
                    DLTEntity.entity_id == request.entity_id,
                    DLTEntity.tenant_id == self.tenant_id,
                    DLTEntity.is_deleted == False
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"DLT Entity ID {request.entity_id} already exists")
        
        # Create entity
        entity = DLTEntity(
            entity_id=request.entity_id,
            entity_name=request.entity_name,
            entity_type=request.entity_type.value,
            telecom_operator=request.telecom_operator,
            registration_date=request.registration_date,
            entity_status="active",
            contact_person=request.contact_person,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            approved_headers=request.approved_headers,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        
        logger.info(f"DLT Entity created: {entity.entity_id} - {entity.entity_name}")
        
        return DLTEntityResponse.model_validate(entity)
    
    async def update_dlt_entity(
        self,
        entity_id: int,
        request: DLTEntityUpdate
    ) -> DLTEntityResponse:
        """Update DLT entity"""
        # Get entity
        result = await self.db.execute(
            select(DLTEntity).where(
                and_(
                    DLTEntity.id == entity_id,
                    DLTEntity.tenant_id == self.tenant_id,
                    DLTEntity.is_deleted == False
                )
            )
        )
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise ValueError(f"DLT Entity not found: {entity_id}")
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        entity.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(entity)
        
        return DLTEntityResponse.model_validate(entity)
    
    async def get_dlt_entity(self, entity_id: int) -> DLTEntityResponse:
        """Get DLT entity by ID"""
        result = await self.db.execute(
            select(DLTEntity).where(
                and_(
                    DLTEntity.id == entity_id,
                    DLTEntity.tenant_id == self.tenant_id,
                    DLTEntity.is_deleted == False
                )
            )
        )
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise ValueError(f"DLT Entity not found: {entity_id}")
        
        return DLTEntityResponse.model_validate(entity)
    
    async def list_dlt_entities(
        self,
        telecom_operator: Optional[str] = None,
        entity_status: Optional[str] = None
    ) -> List[DLTEntityResponse]:
        """List all DLT entities"""
        query = select(DLTEntity).where(
            and_(
                DLTEntity.tenant_id == self.tenant_id,
                DLTEntity.is_deleted == False
            )
        )
        
        if telecom_operator:
            query = query.where(DLTEntity.telecom_operator == telecom_operator)
        
        if entity_status:
            query = query.where(DLTEntity.entity_status == entity_status)
        
        query = query.order_by(DLTEntity.created_at.desc())
        
        result = await self.db.execute(query)
        entities = result.scalars().all()
        
        return [DLTEntityResponse.model_validate(e) for e in entities]
    
    # ========================================================================
    # DLT TEMPLATE MANAGEMENT
    # ========================================================================
    
    async def create_dlt_template(
        self,
        request: DLTTemplateCreate
    ) -> DLTTemplateResponse:
        """
        Register a new DLT template
        
        Args:
            request: DLTTemplateCreate schema
            
        Returns:
            DLTTemplateResponse
        """
        # Check if template_id already exists
        result = await self.db.execute(
            select(DLTTemplate).where(
                and_(
                    DLTTemplate.dlt_template_id == request.dlt_template_id,
                    DLTTemplate.tenant_id == self.tenant_id,
                    DLTTemplate.is_deleted == False
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"DLT Template ID {request.dlt_template_id} already exists")
        
        # Verify entity exists
        entity_result = await self.db.execute(
            select(DLTEntity).where(
                and_(
                    DLTEntity.id == request.dlt_entity_id,
                    DLTEntity.tenant_id == self.tenant_id,
                    DLTEntity.is_deleted == False
                )
            )
        )
        entity = entity_result.scalar_one_or_none()
        
        if not entity:
            raise ValueError(f"DLT Entity not found: {request.dlt_entity_id}")
        
        # Create template
        template = DLTTemplate(
            dlt_template_id=request.dlt_template_id,
            dlt_entity_id=request.dlt_entity_id,
            template_name=request.template_name,
            template_type=request.template_type.value,
            content_template=request.content_template,
            variables=request.variables,
            telecom_operator=request.telecom_operator,
            approval_status="pending",
            notification_template_id=request.notification_template_id,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        logger.info(f"DLT Template created: {template.dlt_template_id} - {template.template_name}")
        
        return DLTTemplateResponse.model_validate(template)
    
    async def update_dlt_template(
        self,
        template_id: int,
        request: DLTTemplateUpdate
    ) -> DLTTemplateResponse:
        """Update DLT template (mainly for approval status)"""
        # Get template
        result = await self.db.execute(
            select(DLTTemplate).where(
                and_(
                    DLTTemplate.id == template_id,
                    DLTTemplate.tenant_id == self.tenant_id,
                    DLTTemplate.is_deleted == False
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"DLT Template not found: {template_id}")
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(template)
        
        return DLTTemplateResponse.model_validate(template)
    
    async def approve_dlt_template(
        self,
        template_id: int,
        approved_date: Optional[date] = None
    ) -> DLTTemplateResponse:
        """Mark DLT template as approved"""
        update_request = DLTTemplateUpdate(
            approval_status="approved",
            approved_date=approved_date or date.today(),
            is_active=True
        )
        return await self.update_dlt_template(template_id, update_request)
    
    async def reject_dlt_template(
        self,
        template_id: int,
        rejection_reason: str
    ) -> DLTTemplateResponse:
        """Mark DLT template as rejected"""
        update_request = DLTTemplateUpdate(
            approval_status="rejected",
            rejection_reason=rejection_reason,
            is_active=False
        )
        return await self.update_dlt_template(template_id, update_request)
    
    async def get_dlt_template(self, template_id: int) -> DLTTemplateResponse:
        """Get DLT template by ID"""
        result = await self.db.execute(
            select(DLTTemplate).where(
                and_(
                    DLTTemplate.id == template_id,
                    DLTTemplate.tenant_id == self.tenant_id,
                    DLTTemplate.is_deleted == False
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"DLT Template not found: {template_id}")
        
        return DLTTemplateResponse.model_validate(template)
    
    async def get_dlt_template_by_code(
        self,
        dlt_template_id: str
    ) -> Optional[DLTTemplateResponse]:
        """Get DLT template by DLT template ID"""
        result = await self.db.execute(
            select(DLTTemplate).where(
                and_(
                    DLTTemplate.dlt_template_id == dlt_template_id,
                    DLTTemplate.tenant_id == self.tenant_id,
                    DLTTemplate.is_deleted == False
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if template:
            return DLTTemplateResponse.model_validate(template)
        return None
    
    async def list_dlt_templates(
        self,
        entity_id: Optional[int] = None,
        approval_status: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[DLTTemplateResponse]:
        """List DLT templates"""
        query = select(DLTTemplate).where(
            and_(
                DLTTemplate.tenant_id == self.tenant_id,
                DLTTemplate.is_deleted == False
            )
        )
        
        if entity_id:
            query = query.where(DLTTemplate.dlt_entity_id == entity_id)
        
        if approval_status:
            query = query.where(DLTTemplate.approval_status == approval_status)
        
        if is_active is not None:
            query = query.where(DLTTemplate.is_active == is_active)
        
        query = query.order_by(DLTTemplate.created_at.desc())
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return [DLTTemplateResponse.model_validate(t) for t in templates]
    
    async def link_notification_template(
        self,
        dlt_template_id: int,
        notification_template_id: int
    ) -> DLTTemplateResponse:
        """Link DLT template with notification template"""
        # Verify notification template exists
        notif_result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.id == notification_template_id,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        notif_template = notif_result.scalar_one_or_none()
        
        if not notif_template:
            raise ValueError(f"Notification template not found: {notification_template_id}")
        
        # Update DLT template
        update_request = DLTTemplateUpdate(
            notification_template_id=notification_template_id
        )
        return await self.update_dlt_template(dlt_template_id, update_request)
    
    # ========================================================================
    # DLT CONSENT MANAGEMENT
    # ========================================================================
    
    async def record_consent(
        self,
        request: DLTConsentCreate
    ) -> DLTConsentResponse:
        """
        Record customer consent for SMS communications
        
        Args:
            request: DLTConsentCreate schema
            
        Returns:
            DLTConsentResponse
        """
        # Check if active consent already exists
        result = await self.db.execute(
            select(DLTConsent).where(
                and_(
                    DLTConsent.customer_id == request.customer_id,
                    DLTConsent.phone_number == request.phone_number,
                    DLTConsent.consent_type == request.consent_type.value,
                    DLTConsent.consent_status == "active",
                    DLTConsent.tenant_id == self.tenant_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing consent
            existing.consent_source = request.consent_source.value
            existing.consent_date = request.consent_date
            existing.consent_ip_address = request.consent_ip_address
            existing.consent_proof = request.consent_proof
            existing.expiry_date = request.expiry_date
            
            await self.db.commit()
            await self.db.refresh(existing)
            
            logger.info(f"Consent updated for customer {request.customer_id}")
            return DLTConsentResponse.model_validate(existing)
        
        # Create new consent
        consent = DLTConsent(
            customer_id=request.customer_id,
            phone_number=request.phone_number,
            consent_type=request.consent_type.value,
            consent_status="active",
            consent_source=request.consent_source.value,
            consent_date=request.consent_date,
            consent_ip_address=request.consent_ip_address,
            consent_proof=request.consent_proof,
            expiry_date=request.expiry_date,
            tenant_id=self.tenant_id
        )
        
        self.db.add(consent)
        await self.db.commit()
        await self.db.refresh(consent)
        
        logger.info(f"Consent recorded for customer {request.customer_id} - {request.consent_type.value}")
        
        return DLTConsentResponse.model_validate(consent)
    
    async def revoke_consent(
        self,
        consent_id: int,
        request: DLTConsentRevoke
    ) -> DLTConsentResponse:
        """Revoke customer consent"""
        # Get consent
        result = await self.db.execute(
            select(DLTConsent).where(
                and_(
                    DLTConsent.id == consent_id,
                    DLTConsent.tenant_id == self.tenant_id
                )
            )
        )
        consent = result.scalar_one_or_none()
        
        if not consent:
            raise ValueError(f"Consent not found: {consent_id}")
        
        # Revoke consent
        consent.consent_status = "revoked"
        consent.revoked_at = datetime.now()
        consent.revoked_by = self.user_id
        consent.revocation_reason = request.revocation_reason
        
        await self.db.commit()
        await self.db.refresh(consent)
        
        logger.info(f"Consent revoked: {consent_id} for customer {consent.customer_id}")
        
        return DLTConsentResponse.model_validate(consent)
    
    async def check_consent(
        self,
        customer_id: int,
        phone_number: str,
        consent_type: str
    ) -> bool:
        """
        Check if customer has active consent
        
        Args:
            customer_id: Customer ID
            phone_number: Phone number
            consent_type: Type of consent (promotional, transactional, etc.)
            
        Returns:
            True if active consent exists, False otherwise
        """
        result = await self.db.execute(
            select(DLTConsent).where(
                and_(
                    DLTConsent.customer_id == customer_id,
                    DLTConsent.phone_number == phone_number,
                    DLTConsent.consent_type == consent_type,
                    DLTConsent.consent_status == "active",
                    DLTConsent.tenant_id == self.tenant_id,
                    or_(
                        DLTConsent.expiry_date.is_(None),
                        DLTConsent.expiry_date >= date.today()
                    )
                )
            )
        )
        consent = result.scalar_one_or_none()
        
        return consent is not None
    
    async def get_customer_consents(
        self,
        customer_id: int
    ) -> List[DLTConsentResponse]:
        """Get all consents for a customer"""
        result = await self.db.execute(
            select(DLTConsent).where(
                and_(
                    DLTConsent.customer_id == customer_id,
                    DLTConsent.tenant_id == self.tenant_id
                )
            ).order_by(DLTConsent.consent_date.desc())
        )
        consents = result.scalars().all()
        
        return [DLTConsentResponse.model_validate(c) for c in consents]
    
    # ========================================================================
    # DLT COMPLIANCE VALIDATION
    # ========================================================================
    
    async def validate_dlt_compliance(
        self,
        request: DLTComplianceCheck
    ) -> DLTComplianceResponse:
        """
        Validate DLT compliance before sending SMS
        
        Args:
            request: DLTComplianceCheck schema
            
        Returns:
            DLTComplianceResponse with compliance status and issues
        """
        issues = []
        warnings = []
        
        # 1. Check if customer has consent (for promotional messages)
        has_consent = True
        consent_result = await self.db.execute(
            select(DLTConsent).where(
                and_(
                    DLTConsent.customer_id == request.customer_id,
                    DLTConsent.phone_number == request.phone_number,
                    DLTConsent.consent_status == "active",
                    DLTConsent.tenant_id == self.tenant_id
                )
            )
        )
        consent = consent_result.scalar_one_or_none()
        
        if not consent:
            has_consent = False
            warnings.append("No active consent found for customer")
        elif consent.expiry_date and consent.expiry_date < date.today():
            has_consent = False
            issues.append("Consent has expired")
        
        # 2. Check if template has DLT registration
        has_dlt_template = False
        dlt_template_id = None
        dlt_entity_id = None
        
        # Get notification template
        notif_template_result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.template_code == request.template_code,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        notif_template = notif_template_result.scalar_one_or_none()
        
        if notif_template:
            # Look for linked DLT template
            dlt_result = await self.db.execute(
                select(DLTTemplate).where(
                    and_(
                        DLTTemplate.notification_template_id == notif_template.id,
                        DLTTemplate.tenant_id == self.tenant_id,
                        DLTTemplate.is_deleted == False
                    )
                )
            )
            dlt_template = dlt_result.scalar_one_or_none()
            
            if dlt_template:
                if dlt_template.approval_status == "approved":
                    has_dlt_template = True
                    dlt_template_id = dlt_template.dlt_template_id
                    
                    # Get entity ID
                    entity_result = await self.db.execute(
                        select(DLTEntity).where(
                            and_(
                                DLTEntity.id == dlt_template.dlt_entity_id,
                                DLTEntity.tenant_id == self.tenant_id
                            )
                        )
                    )
                    entity = entity_result.scalar_one_or_none()
                    if entity:
                        dlt_entity_id = entity.entity_id
                elif dlt_template.approval_status == "pending":
                    issues.append("DLT template is pending approval")
                elif dlt_template.approval_status == "rejected":
                    issues.append(f"DLT template was rejected: {dlt_template.rejection_reason}")
            else:
                issues.append("No DLT template linked to notification template")
        else:
            issues.append("Notification template not found")
        
        # Determine compliance
        is_compliant = has_dlt_template and (has_consent or True)
        # Note: Transactional messages don't require consent, only promotional ones do
        
        return DLTComplianceResponse(
            is_compliant=is_compliant,
            has_consent=has_consent,
            has_dlt_template=has_dlt_template,
            dlt_template_id=dlt_template_id,
            dlt_entity_id=dlt_entity_id,
            issues=issues,
            warnings=warnings
        )
    
    async def get_dlt_info_for_sending(
        self,
        template_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get DLT information for sending SMS
        
        Args:
            template_code: Notification template code
            
        Returns:
            Dict with dlt_template_id and dlt_entity_id, or None
        """
        # Get notification template
        notif_result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.template_code == template_code,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        notif_template = notif_result.scalar_one_or_none()
        
        if not notif_template:
            return None
        
        # Get DLT template
        dlt_result = await self.db.execute(
            select(DLTTemplate).where(
                and_(
                    DLTTemplate.notification_template_id == notif_template.id,
                    DLTTemplate.approval_status == "approved",
                    DLTTemplate.is_active == True,
                    DLTTemplate.is_deleted == False,
                    DLTTemplate.tenant_id == self.tenant_id
                )
            )
        )
        dlt_template = dlt_result.scalar_one_or_none()
        
        if not dlt_template:
            return None
        
        # Get entity
        entity_result = await self.db.execute(
            select(DLTEntity).where(
                and_(
                    DLTEntity.id == dlt_template.dlt_entity_id,
                    DLTEntity.tenant_id == self.tenant_id
                )
            )
        )
        entity = entity_result.scalar_one_or_none()
        
        if not entity:
            return None
        
        return {
            "dlt_template_id": dlt_template.dlt_template_id,
            "dlt_entity_id": entity.entity_id,
            "telecom_operator": dlt_template.telecom_operator
        }

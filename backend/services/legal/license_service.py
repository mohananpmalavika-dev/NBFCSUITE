"""
Legal License Management - Service Layer
Business logic for license operations, renewals, and compliance tracking
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from typing import List, Optional, Tuple
from datetime import date, datetime, timedelta
from uuid import UUID
import uuid

from .license_models import (
    License,
    LicenseRenewal,
    LicenseComplianceCheck,
    LicenseDocument,
    LicenseReminder,
    LicenseStatus,
    RenewalStatus,
    ComplianceStatus,
)
from .license_schemas import (
    LicenseCreate,
    LicenseUpdate,
    LicenseRenewalCreate,
    LicenseRenewalUpdate,
    LicenseComplianceCheckCreate,
    LicenseComplianceCheckUpdate,
    LicenseDocumentCreate,
    LicenseFilterParams,
    LicenseStatistics,
    LicenseReminderCreate,
)


class LicenseService:
    """Service class for license management operations"""

    @staticmethod
    async def create_license(
        db: AsyncSession,
        license_data: LicenseCreate,
        tenant_id: str,
        user_id: UUID
    ) -> License:
        """Create a new license"""
        # Calculate next renewal date if renewable
        next_renewal_date = None
        if license_data.is_renewable and license_data.expiry_date:
            next_renewal_date = license_data.expiry_date - timedelta(days=license_data.renewal_notice_days)
        
        # Calculate next compliance check date
        next_compliance_check_date = None
        if license_data.issue_date:
            next_compliance_check_date = license_data.issue_date + timedelta(days=365)  # Default 1 year
        
        license_dict = license_data.model_dump()
        license = License(
            **license_dict,
            tenant_id=tenant_id,
            next_renewal_date=next_renewal_date,
            next_compliance_check_date=next_compliance_check_date,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(license)
        await db.commit()
        await db.refresh(license)
        
        # Create audit log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "created",
            "user_id": str(user_id),
            "details": "License created"
        }
        license.audit_log = [audit_entry]
        await db.commit()
        
        return license

    @staticmethod
    async def get_license(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str
    ) -> Optional[License]:
        """Get license by ID with all related data"""
        query = select(License).where(
            and_(
                License.id == license_id,
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_licenses(
        db: AsyncSession,
        tenant_id: str,
        filters: LicenseFilterParams
    ) -> Tuple[List[License], int]:
        """List licenses with filtering and pagination"""
        # Build base query
        query = select(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.license_type:
            query = query.where(License.license_type == filters.license_type)
        
        if filters.status:
            query = query.where(License.status == filters.status)
        
        if filters.renewal_status:
            query = query.where(License.renewal_status == filters.renewal_status)
        
        if filters.compliance_status:
            query = query.where(License.compliance_status == filters.compliance_status)
        
        if filters.is_renewable is not None:
            query = query.where(License.is_renewable == filters.is_renewable)
        
        if filters.is_perpetual is not None:
            query = query.where(License.is_perpetual == filters.is_perpetual)
        
        if filters.expiring_in_days:
            target_date = date.today() + timedelta(days=filters.expiring_in_days)
            query = query.where(
                and_(
                    License.expiry_date.isnot(None),
                    License.expiry_date <= target_date,
                    License.expiry_date >= date.today()
                )
            )
        
        if filters.issue_date_from:
            query = query.where(License.issue_date >= filters.issue_date_from)
        
        if filters.issue_date_to:
            query = query.where(License.issue_date <= filters.issue_date_to)
        
        if filters.expiry_date_from:
            query = query.where(License.expiry_date >= filters.expiry_date_from)
        
        if filters.expiry_date_to:
            query = query.where(License.expiry_date <= filters.expiry_date_to)
        
        if filters.issuing_authority:
            query = query.where(License.issuing_authority.ilike(f"%{filters.issuing_authority}%"))
        
        if filters.responsible_department:
            query = query.where(License.responsible_department.ilike(f"%{filters.responsible_department}%"))
        
        if filters.criticality_level:
            query = query.where(License.criticality_level == filters.criticality_level)
        
        if filters.tags:
            for tag in filters.tags:
                query = query.where(License.tags.contains([tag]))
        
        if filters.search_query:
            search_pattern = f"%{filters.search_query}%"
            query = query.where(
                or_(
                    License.license_number.ilike(search_pattern),
                    License.license_name.ilike(search_pattern),
                    License.description.ilike(search_pattern),
                    License.issuing_authority.ilike(search_pattern)
                )
            )
        
        # Count total records
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(getattr(License, filters.sort_by)))
        else:
            query = query.order_by(desc(getattr(License, filters.sort_by)))
        
        # Apply pagination
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
        
        result = await db.execute(query)
        licenses = result.scalars().all()
        
        return licenses, total

    @staticmethod
    async def update_license(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        license_data: LicenseUpdate,
        user_id: UUID
    ) -> Optional[License]:
        """Update license"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return None
        
        # Track changes for audit
        changes = []
        update_data = license_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(license, field) and getattr(license, field) != value:
                old_value = getattr(license, field)
                changes.append(f"{field}: {old_value} -> {value}")
                setattr(license, field, value)
        
        license.updated_by = user_id
        license.updated_at = datetime.utcnow()
        
        # Add audit log entry
        if changes:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "updated",
                "user_id": str(user_id),
                "changes": changes
            }
            if license.audit_log:
                license.audit_log.append(audit_entry)
            else:
                license.audit_log = [audit_entry]
        
        await db.commit()
        await db.refresh(license)
        
        return license

    @staticmethod
    async def delete_license(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        user_id: UUID
    ) -> bool:
        """Soft delete license"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return False
        
        license.is_deleted = True
        license.deleted_at = datetime.utcnow()
        license.deleted_by = user_id
        
        # Add audit log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "deleted",
            "user_id": str(user_id)
        }
        if license.audit_log:
            license.audit_log.append(audit_entry)
        else:
            license.audit_log = [audit_entry]
        
        await db.commit()
        return True

    @staticmethod
    async def get_license_statistics(
        db: AsyncSession,
        tenant_id: str
    ) -> LicenseStatistics:
        """Get license statistics"""
        # Total licenses
        total_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        )
        total_result = await db.execute(total_query)
        total_licenses = total_result.scalar() or 0
        
        # Active licenses
        active_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.status == LicenseStatus.ACTIVE
            )
        )
        active_result = await db.execute(active_query)
        active_licenses = active_result.scalar() or 0
        
        # Expired licenses
        expired_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.status == LicenseStatus.EXPIRED
            )
        )
        expired_result = await db.execute(expired_query)
        expired_licenses = expired_result.scalar() or 0
        
        # Expiring soon (next 30 days)
        expiring_date = date.today() + timedelta(days=30)
        expiring_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.expiry_date.isnot(None),
                License.expiry_date <= expiring_date,
                License.expiry_date >= date.today()
            )
        )
        expiring_result = await db.execute(expiring_query)
        expiring_soon = expiring_result.scalar() or 0
        
        # Pending renewals
        pending_renewals_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.renewal_status == RenewalStatus.PENDING
            )
        )
        pending_result = await db.execute(pending_renewals_query)
        pending_renewals = pending_result.scalar() or 0
        
        # Non-compliant licenses
        non_compliant_query = select(func.count()).select_from(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.compliance_status == ComplianceStatus.NON_COMPLIANT
            )
        )
        non_compliant_result = await db.execute(non_compliant_query)
        non_compliant_licenses = non_compliant_result.scalar() or 0
        
        # Licenses by type
        type_query = select(
            License.license_type,
            func.count(License.id)
        ).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        ).group_by(License.license_type)
        type_result = await db.execute(type_query)
        licenses_by_type = {row[0].value: row[1] for row in type_result}
        
        # Licenses by status
        status_query = select(
            License.status,
            func.count(License.id)
        ).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        ).group_by(License.status)
        status_result = await db.execute(status_query)
        licenses_by_status = {row[0].value: row[1] for row in status_result}
        
        # Licenses by compliance status
        compliance_query = select(
            License.compliance_status,
            func.count(License.id)
        ).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False
            )
        ).group_by(License.compliance_status)
        compliance_result = await db.execute(compliance_query)
        licenses_by_compliance_status = {row[0].value: row[1] for row in compliance_result}
        
        # Total renewal fees due (for pending renewals)
        fees_query = select(func.sum(License.renewal_fee)).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.renewal_status == RenewalStatus.PENDING,
                License.renewal_fee.isnot(None)
            )
        )
        fees_result = await db.execute(fees_query)
        total_renewal_fees_due = fees_result.scalar() or 0
        
        # Average renewal time
        avg_query = select(func.avg(LicenseRenewal.processing_days)).where(
            LicenseRenewal.renewal_status == RenewalStatus.COMPLETED
        )
        avg_result = await db.execute(avg_query)
        average_renewal_time_days = avg_result.scalar() or 0
        
        return LicenseStatistics(
            total_licenses=total_licenses,
            active_licenses=active_licenses,
            expired_licenses=expired_licenses,
            expiring_soon=expiring_soon,
            pending_renewals=pending_renewals,
            non_compliant_licenses=non_compliant_licenses,
            licenses_by_type=licenses_by_type,
            licenses_by_status=licenses_by_status,
            licenses_by_compliance_status=licenses_by_compliance_status,
            total_renewal_fees_due=total_renewal_fees_due,
            average_renewal_time_days=float(average_renewal_time_days)
        )

    # ============================================
    # RENEWAL OPERATIONS
    # ============================================

    @staticmethod
    async def create_renewal(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        renewal_data: LicenseRenewalCreate,
        user_id: UUID
    ) -> Optional[LicenseRenewal]:
        """Create a new renewal record"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return None
        
        # Get next renewal number
        max_query = select(func.max(LicenseRenewal.renewal_number)).where(
            LicenseRenewal.license_id == license_id
        )
        max_result = await db.execute(max_query)
        max_number = max_result.scalar() or 0
        
        renewal_dict = renewal_data.model_dump()
        renewal = LicenseRenewal(
            **renewal_dict,
            license_id=license_id,
            renewal_number=max_number + 1,
            created_by=user_id
        )
        
        # Update license renewal status
        license.renewal_status = RenewalStatus.PENDING
        
        db.add(renewal)
        await db.commit()
        await db.refresh(renewal)
        
        return renewal

    @staticmethod
    async def update_renewal(
        db: AsyncSession,
        renewal_id: UUID,
        tenant_id: str,
        renewal_data: LicenseRenewalUpdate,
        user_id: UUID
    ) -> Optional[LicenseRenewal]:
        """Update renewal record"""
        query = select(LicenseRenewal).where(LicenseRenewal.id == renewal_id)
        result = await db.execute(query)
        renewal = result.scalar_one_or_none()
        
        if not renewal:
            return None
        
        # Verify license belongs to tenant
        license = await LicenseService.get_license(db, renewal.license_id, tenant_id)
        if not license:
            return None
        
        update_data = renewal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(renewal, field, value)
        
        renewal.updated_at = datetime.utcnow()
        
        # If renewal completed, update parent license
        if renewal_data.renewal_status == RenewalStatus.COMPLETED and renewal_data.new_expiry_date:
            license.expiry_date = renewal_data.new_expiry_date
            license.last_renewal_date = date.today()
            license.renewal_status = RenewalStatus.NOT_REQUIRED
            license.status = LicenseStatus.ACTIVE
            
            # Calculate next renewal date
            if license.is_renewable:
                license.next_renewal_date = renewal_data.new_expiry_date - timedelta(days=license.renewal_notice_days)
        
        await db.commit()
        await db.refresh(renewal)
        
        return renewal

    # ============================================
    # COMPLIANCE CHECK OPERATIONS
    # ============================================

    @staticmethod
    async def create_compliance_check(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        check_data: LicenseComplianceCheckCreate,
        user_id: UUID
    ) -> Optional[LicenseComplianceCheck]:
        """Create a compliance check record"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return None
        
        # Get next check number
        max_query = select(func.max(LicenseComplianceCheck.check_number)).where(
            LicenseComplianceCheck.license_id == license_id
        )
        max_result = await db.execute(max_query)
        max_number = max_result.scalar() or 0
        
        check_dict = check_data.model_dump()
        check = LicenseComplianceCheck(
            **check_dict,
            license_id=license_id,
            check_number=max_number + 1,
            created_by=user_id
        )
        
        # Update license compliance status
        license.compliance_status = check_data.compliance_status
        license.last_compliance_check_date = check_data.check_date
        
        if check_data.next_check_due_date:
            license.next_compliance_check_date = check_data.next_check_due_date
        
        db.add(check)
        await db.commit()
        await db.refresh(check)
        
        return check

    @staticmethod
    async def update_compliance_check(
        db: AsyncSession,
        check_id: UUID,
        tenant_id: str,
        check_data: LicenseComplianceCheckUpdate,
        user_id: UUID
    ) -> Optional[LicenseComplianceCheck]:
        """Update compliance check record"""
        query = select(LicenseComplianceCheck).where(LicenseComplianceCheck.id == check_id)
        result = await db.execute(query)
        check = result.scalar_one_or_none()
        
        if not check:
            return None
        
        # Verify license belongs to tenant
        license = await LicenseService.get_license(db, check.license_id, tenant_id)
        if not license:
            return None
        
        update_data = check_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(check, field, value)
        
        check.updated_at = datetime.utcnow()
        
        # Update license compliance status if changed
        if check_data.compliance_status:
            license.compliance_status = check_data.compliance_status
        
        await db.commit()
        await db.refresh(check)
        
        return check

    # ============================================
    # DOCUMENT OPERATIONS
    # ============================================

    @staticmethod
    async def add_document(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        document_data: LicenseDocumentCreate,
        user_id: UUID
    ) -> Optional[LicenseDocument]:
        """Add document to license"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return None
        
        document_dict = document_data.model_dump()
        document = LicenseDocument(
            **document_dict,
            license_id=license_id,
            uploaded_by=user_id
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        return document

    # ============================================
    # REMINDER OPERATIONS
    # ============================================

    @staticmethod
    async def create_reminder(
        db: AsyncSession,
        license_id: UUID,
        tenant_id: str,
        reminder_data: LicenseReminderCreate,
        user_id: UUID
    ) -> Optional[LicenseReminder]:
        """Create a reminder for license"""
        license = await LicenseService.get_license(db, license_id, tenant_id)
        if not license:
            return None
        
        reminder_dict = reminder_data.model_dump()
        reminder = LicenseReminder(
            **reminder_dict,
            license_id=license_id,
            created_by=user_id
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        
        return reminder

    @staticmethod
    async def get_expiring_licenses(
        db: AsyncSession,
        tenant_id: str,
        days: int = 30
    ) -> List[License]:
        """Get licenses expiring within specified days"""
        target_date = date.today() + timedelta(days=days)
        query = select(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.expiry_date.isnot(None),
                License.expiry_date <= target_date,
                License.expiry_date >= date.today()
            )
        ).order_by(License.expiry_date)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_non_compliant_licenses(
        db: AsyncSession,
        tenant_id: str
    ) -> List[License]:
        """Get non-compliant licenses"""
        query = select(License).where(
            and_(
                License.tenant_id == tenant_id,
                License.is_deleted == False,
                License.compliance_status == ComplianceStatus.NON_COMPLIANT
            )
        ).order_by(License.last_compliance_check_date)
        
        result = await db.execute(query)
        return result.scalars().all()

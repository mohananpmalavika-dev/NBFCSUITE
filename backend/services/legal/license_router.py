"""
Legal License Management - API Router
REST API endpoints for license management, renewals, and compliance tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.database.models import User
from .license_service import LicenseService
from .license_scheduler import trigger_reminder_check_now, get_reminder_statistics
from .license_schemas import (
    LicenseCreate,
    LicenseUpdate,
    LicenseResponse,
    LicenseListResponse,
    LicenseRenewalCreate,
    LicenseRenewalUpdate,
    LicenseRenewalResponse,
    LicenseComplianceCheckCreate,
    LicenseComplianceCheckUpdate,
    LicenseComplianceCheckResponse,
    LicenseDocumentCreate,
    LicenseDocumentResponse,
    LicenseFilterParams,
    LicenseStatistics,
    LicenseReminderCreate,
    LicenseReminderResponse,
)
from .license_models import (
    LicenseType,
    LicenseStatus,
    RenewalStatus,
    ComplianceStatus,
)


router = APIRouter(prefix="/api/v1/legal/licenses", tags=["Legal - License Management"])


def map_license_to_response(license) -> LicenseResponse:
    """Map license model to response schema with computed fields"""
    response = LicenseResponse.from_orm(license)
    
    # Calculate days until expiry
    if license.expiry_date and not license.is_perpetual:
        delta = (license.expiry_date - date.today()).days
        response.days_until_expiry = delta
        response.is_expiring_soon = 0 <= delta <= license.renewal_notice_days
        response.is_expired = delta < 0
        
        # Check if renewal action required
        response.requires_renewal_action = (
            license.is_renewable and
            0 <= delta <= license.renewal_submission_deadline_days and
            license.renewal_status == RenewalStatus.NOT_REQUIRED
        )
    
    return response


# ============================================
# LICENSE CRUD ENDPOINTS
# ============================================

@router.post("", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
async def create_license(
    license_data: LicenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new license
    
    - **license_number**: Unique license number (required)
    - **license_name**: License name/title (required)
    - **license_type**: Type of license (NBFC, RBI, Business, etc.)
    - **issuing_authority**: Authority that issued the license
    - **issue_date**: License issue date
    - **expiry_date**: License expiry date (optional for perpetual licenses)
    - **is_renewable**: Whether license can be renewed
    - **compliance_requirements**: List of compliance requirements
    """
    license = await LicenseService.create_license(
        db=db,
        license_data=license_data,
        tenant_id=tenant_id,
        user_id=current_user.id
    )
    return map_license_to_response(license)


@router.get("", response_model=LicenseListResponse)
async def list_licenses(
    license_type: Optional[LicenseType] = None,
    status: Optional[LicenseStatus] = None,
    renewal_status: Optional[RenewalStatus] = None,
    compliance_status: Optional[ComplianceStatus] = None,
    is_renewable: Optional[bool] = None,
    is_perpetual: Optional[bool] = None,
    expiring_in_days: Optional[int] = None,
    issue_date_from: Optional[date] = None,
    issue_date_to: Optional[date] = None,
    expiry_date_from: Optional[date] = None,
    expiry_date_to: Optional[date] = None,
    issuing_authority: Optional[str] = None,
    responsible_department: Optional[str] = None,
    criticality_level: Optional[str] = None,
    search_query: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List licenses with filtering, search, and pagination
    
    - **license_type**: Filter by license type
    - **status**: Filter by license status
    - **renewal_status**: Filter by renewal status
    - **compliance_status**: Filter by compliance status
    - **expiring_in_days**: Get licenses expiring within N days
    - **search_query**: Search in license number, name, description
    """
    filters = LicenseFilterParams(
        license_type=license_type,
        status=status,
        renewal_status=renewal_status,
        compliance_status=compliance_status,
        is_renewable=is_renewable,
        is_perpetual=is_perpetual,
        expiring_in_days=expiring_in_days,
        issue_date_from=issue_date_from,
        issue_date_to=issue_date_to,
        expiry_date_from=expiry_date_from,
        expiry_date_to=expiry_date_to,
        issuing_authority=issuing_authority,
        responsible_department=responsible_department,
        criticality_level=criticality_level,
        search_query=search_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    licenses, total = await LicenseService.list_licenses(
        db=db,
        tenant_id=tenant_id,
        filters=filters
    )
    
    items = [map_license_to_response(license) for license in licenses]
    total_pages = (total + page_size - 1) // page_size
    
    return LicenseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/statistics", response_model=LicenseStatistics)
async def get_license_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get license statistics and analytics
    
    Returns:
    - Total licenses count
    - Active/expired/expiring soon counts
    - Pending renewals
    - Non-compliant licenses
    - Licenses by type, status, and compliance status
    - Total renewal fees due
    - Average renewal time
    """
    stats = await LicenseService.get_license_statistics(db=db, tenant_id=tenant_id)
    return stats


@router.get("/expiring", response_model=List[LicenseResponse])
async def get_expiring_licenses(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get licenses expiring within specified days
    
    - **days**: Number of days to look ahead (default: 30)
    """
    licenses = await LicenseService.get_expiring_licenses(
        db=db,
        tenant_id=tenant_id,
        days=days
    )
    return [map_license_to_response(license) for license in licenses]


@router.get("/non-compliant", response_model=List[LicenseResponse])
async def get_non_compliant_licenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all non-compliant licenses"""
    licenses = await LicenseService.get_non_compliant_licenses(
        db=db,
        tenant_id=tenant_id
    )
    return [map_license_to_response(license) for license in licenses]


@router.get("/{license_id}", response_model=LicenseResponse)
async def get_license(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get license by ID with all related data
    
    Returns:
    - License details
    - All renewal records
    - Compliance check history
    - Associated documents
    - Reminder history
    """
    license = await LicenseService.get_license(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id
    )
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return map_license_to_response(license)


@router.patch("/{license_id}", response_model=LicenseResponse)
async def update_license(
    license_id: UUID,
    license_data: LicenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update license
    
    - All changes are tracked in audit log
    - Status updates trigger appropriate workflows
    """
    license = await LicenseService.update_license(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        license_data=license_data,
        user_id=current_user.id
    )
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return map_license_to_response(license)


@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete license (soft delete)
    
    - License is marked as deleted but not removed from database
    - All related data remains intact for audit purposes
    """
    success = await LicenseService.delete_license(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )


# ============================================
# RENEWAL ENDPOINTS
# ============================================

@router.post("/{license_id}/renewals", response_model=LicenseRenewalResponse, status_code=status.HTTP_201_CREATED)
async def create_renewal(
    license_id: UUID,
    renewal_data: LicenseRenewalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Initiate license renewal
    
    - **renewal_due_date**: Date by which renewal should be completed
    - **application_number**: Renewal application reference number
    - **renewal_fee_paid**: Amount paid for renewal
    """
    renewal = await LicenseService.create_renewal(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        renewal_data=renewal_data,
        user_id=current_user.id
    )
    
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return LicenseRenewalResponse.from_orm(renewal)


@router.patch("/renewals/{renewal_id}", response_model=LicenseRenewalResponse)
async def update_renewal(
    renewal_id: UUID,
    renewal_data: LicenseRenewalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update license renewal
    
    - Update renewal status (PENDING, IN_PROGRESS, SUBMITTED, COMPLETED)
    - Track approval workflow
    - When completed, updates parent license expiry date
    """
    renewal = await LicenseService.update_renewal(
        db=db,
        renewal_id=renewal_id,
        tenant_id=tenant_id,
        renewal_data=renewal_data,
        user_id=current_user.id
    )
    
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )
    
    return LicenseRenewalResponse.from_orm(renewal)


@router.get("/{license_id}/renewals", response_model=List[LicenseRenewalResponse])
async def list_renewals(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all renewals for a license
    
    - Returns complete renewal history
    - Ordered by renewal number (latest first)
    """
    license = await LicenseService.get_license(db=db, license_id=license_id, tenant_id=tenant_id)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    renewals = sorted(license.renewals, key=lambda r: r.renewal_number, reverse=True)
    return [LicenseRenewalResponse.from_orm(renewal) for renewal in renewals]


# ============================================
# COMPLIANCE CHECK ENDPOINTS
# ============================================

@router.post("/{license_id}/compliance-checks", response_model=LicenseComplianceCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_compliance_check(
    license_id: UUID,
    check_data: LicenseComplianceCheckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Record a compliance check
    
    - **check_date**: Date of compliance check
    - **compliance_status**: Result of the check (COMPLIANT, NON_COMPLIANT, etc.)
    - **findings**: Detailed findings from the check
    - **action_items**: Required corrective actions
    """
    check = await LicenseService.create_compliance_check(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        check_data=check_data,
        user_id=current_user.id
    )
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return LicenseComplianceCheckResponse.from_orm(check)


@router.patch("/compliance-checks/{check_id}", response_model=LicenseComplianceCheckResponse)
async def update_compliance_check(
    check_id: UUID,
    check_data: LicenseComplianceCheckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update compliance check
    
    - Update compliance status
    - Add findings and recommendations
    - Mark actions as completed
    """
    check = await LicenseService.update_compliance_check(
        db=db,
        check_id=check_id,
        tenant_id=tenant_id,
        check_data=check_data,
        user_id=current_user.id
    )
    
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found"
        )
    
    return LicenseComplianceCheckResponse.from_orm(check)


@router.get("/{license_id}/compliance-checks", response_model=List[LicenseComplianceCheckResponse])
async def list_compliance_checks(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all compliance checks for a license
    
    - Returns complete compliance history
    - Ordered by check date (latest first)
    """
    license = await LicenseService.get_license(db=db, license_id=license_id, tenant_id=tenant_id)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    checks = sorted(license.compliance_checks, key=lambda c: c.check_date, reverse=True)
    return [LicenseComplianceCheckResponse.from_orm(check) for check in checks]


# ============================================
# DOCUMENT ENDPOINTS
# ============================================

@router.post("/{license_id}/documents", response_model=LicenseDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document(
    license_id: UUID,
    document_data: LicenseDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Add document to license
    
    - **document_name**: Display name for the document
    - **document_type**: Type (Certificate, Application, Approval, etc.)
    - **file_url**: URL to the stored file
    - **is_confidential**: Mark document as confidential
    """
    document = await LicenseService.add_document(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        document_data=document_data,
        user_id=current_user.id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return LicenseDocumentResponse.from_orm(document)


@router.get("/{license_id}/documents", response_model=List[LicenseDocumentResponse])
async def list_documents(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all documents associated with a license"""
    license = await LicenseService.get_license(db=db, license_id=license_id, tenant_id=tenant_id)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return [LicenseDocumentResponse.from_orm(doc) for doc in license.documents if not doc.is_deleted]


# ============================================
# REMINDER ENDPOINTS
# ============================================

@router.post("/{license_id}/reminders", response_model=LicenseReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    license_id: UUID,
    reminder_data: LicenseReminderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a reminder for license
    
    - **reminder_type**: Type of reminder (renewal, compliance, expiry)
    - **reminder_date**: When to send the reminder
    - **recipients**: List of email addresses to notify
    """
    reminder = await LicenseService.create_reminder(
        db=db,
        license_id=license_id,
        tenant_id=tenant_id,
        reminder_data=reminder_data,
        user_id=current_user.id
    )
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    return LicenseReminderResponse.from_orm(reminder)


@router.get("/{license_id}/reminders", response_model=List[LicenseReminderResponse])
async def list_reminders(
    license_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all reminders for a license"""
    license = await LicenseService.get_license(db=db, license_id=license_id, tenant_id=tenant_id)
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    reminders = sorted(license.reminders, key=lambda r: r.reminder_date, reverse=True)
    return [LicenseReminderResponse.from_orm(reminder) for reminder in reminders]


# ============================================
# BULK OPERATIONS
# ============================================

@router.post("/bulk/status-update", status_code=status.HTTP_200_OK)
async def bulk_update_status(
    license_ids: List[UUID],
    new_status: LicenseStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Bulk update license status
    
    - Update multiple licenses at once
    - Useful for batch status changes
    """
    updated_count = 0
    
    for license_id in license_ids:
        update_data = LicenseUpdate(status=new_status)
        license = await LicenseService.update_license(
            db=db,
            license_id=license_id,
            tenant_id=tenant_id,
            license_data=update_data,
            user_id=current_user.id
        )
        if license:
            updated_count += 1
    
    return {
        "success": True,
        "message": f"Updated {updated_count} out of {len(license_ids)} licenses",
        "updated_count": updated_count
    }


# ============================================
# REMINDER SYSTEM ENDPOINTS
# ============================================

@router.post("/reminders/trigger-check", status_code=status.HTTP_200_OK)
async def trigger_reminder_check(
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger reminder check
    
    - Checks all licenses for renewal and compliance reminders
    - Sends notifications as needed
    - Returns statistics about reminders sent
    """
    try:
        stats = await trigger_reminder_check_now()
        return {
            "success": True,
            "message": "Reminder check completed",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger reminder check: {str(e)}"
        )


@router.get("/reminders/statistics", status_code=status.HTTP_200_OK)
async def get_reminder_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
):
    """
    Get reminder statistics
    
    - Returns statistics for reminders sent in the last N days
    - Includes counts by type, success rate, etc.
    """
    try:
        stats = await get_reminder_statistics(days)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reminder statistics: {str(e)}"
        )

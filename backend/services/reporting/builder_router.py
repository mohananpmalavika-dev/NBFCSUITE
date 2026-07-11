"""
Custom Report Builder Router
API endpoints for building custom reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import math

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.reporting_models import CustomReportBuilder
from backend.services.reporting import schemas


router = APIRouter(prefix="/reports/builder", tags=["Reporting - Custom Builder"])


@router.get("/datasources", response_model=dict)
async def get_available_datasources(
    current_user: dict = Depends(get_current_user)
):
    """Get available data sources for custom report builder"""
    datasources = [
        {
            "table": "customers",
            "label": "Customers",
            "fields": [
                {"name": "customer_code", "label": "Customer Code", "type": "string"},
                {"name": "first_name", "label": "First Name", "type": "string"},
                {"name": "last_name", "label": "Last Name", "type": "string"},
                {"name": "email", "label": "Email", "type": "string"},
                {"name": "phone", "label": "Phone", "type": "string"},
                {"name": "date_of_birth", "label": "Date of Birth", "type": "date"},
                {"name": "created_at", "label": "Onboarding Date", "type": "datetime"}
            ]
        },
        {
            "table": "loan_accounts",
            "label": "Loan Accounts",
            "fields": [
                {"name": "account_number", "label": "Account Number", "type": "string"},
                {"name": "sanctioned_amount", "label": "Sanctioned Amount", "type": "number"},
                {"name": "principal_outstanding", "label": "Outstanding", "type": "number"},
                {"name": "interest_rate", "label": "Interest Rate", "type": "number"},
                {"name": "tenure_months", "label": "Tenure", "type": "number"},
                {"name": "status", "label": "Status", "type": "string"},
                {"name": "disbursement_date", "label": "Disbursement Date", "type": "date"}
            ]
        },
        {
            "table": "loan_applications",
            "label": "Loan Applications",
            "fields": [
                {"name": "application_number", "label": "Application Number", "type": "string"},
                {"name": "requested_amount", "label": "Requested Amount", "type": "number"},
                {"name": "status", "label": "Status", "type": "string"},
                {"name": "created_at", "label": "Application Date", "type": "datetime"}
            ]
        },
        {
            "table": "loan_repayments",
            "label": "Repayments",
            "fields": [
                {"name": "payment_date", "label": "Payment Date", "type": "date"},
                {"name": "amount", "label": "Amount", "type": "number"},
                {"name": "payment_method", "label": "Payment Method", "type": "string"},
                {"name": "status", "label": "Status", "type": "string"}
            ]
        }
    ]
    
    return success_response(
        data=datasources,
        message="Data sources retrieved successfully"
    )


@router.get("/aggregations", response_model=dict)
async def get_available_aggregations(
    current_user: dict = Depends(get_current_user)
):
    """Get available aggregation functions"""
    aggregations = [
        {"value": "COUNT", "label": "Count", "types": ["all"]},
        {"value": "SUM", "label": "Sum", "types": ["number"]},
        {"value": "AVG", "label": "Average", "types": ["number"]},
        {"value": "MIN", "label": "Minimum", "types": ["number", "date"]},
        {"value": "MAX", "label": "Maximum", "types": ["number", "date"]},
        {"value": "COUNT_DISTINCT", "label": "Count Distinct", "types": ["all"]}
    ]
    
    return success_response(
        data=aggregations,
        message="Aggregation functions retrieved"
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_custom_report(
    data: schemas.CustomReportBuilderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create custom report"""
    try:
        report = CustomReportBuilder(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return success_response(
            data=schemas.CustomReportBuilderResponse.model_validate(report),
            message="Custom report created successfully"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def list_custom_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List custom reports"""
    try:
        query = select(CustomReportBuilder).where(
            CustomReportBuilder.tenant_id == current_user["tenant_id"],
            CustomReportBuilder.is_deleted == False
        )
        
        # Count
        count_query = select(func.count()).select_from(CustomReportBuilder).where(
            CustomReportBuilder.tenant_id == current_user["tenant_id"],
            CustomReportBuilder.is_deleted == False
        )
        
        total = await db.scalar(count_query)
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(CustomReportBuilder.created_at.desc())
        
        result = await db.execute(query)
        reports = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.CustomReportBuilderResponse.model_validate(r) for r in reports],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} custom reports"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{report_id}", response_model=dict)
async def get_custom_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get custom report by ID"""
    try:
        result = await db.execute(
            select(CustomReportBuilder).where(
                CustomReportBuilder.id == report_id,
                CustomReportBuilder.tenant_id == current_user["tenant_id"],
                CustomReportBuilder.is_deleted == False
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom report not found"
            )
        
        return success_response(
            data=schemas.CustomReportBuilderResponse.model_validate(report),
            message="Custom report retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{report_id}", response_model=dict)
async def update_custom_report(
    report_id: int,
    data: schemas.CustomReportBuilderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update custom report"""
    try:
        result = await db.execute(
            select(CustomReportBuilder).where(
                CustomReportBuilder.id == report_id,
                CustomReportBuilder.tenant_id == current_user["tenant_id"],
                CustomReportBuilder.is_deleted == False
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom report not found"
            )
        
        # Update
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)
        
        report.updated_by = current_user["user_id"]
        
        await db.commit()
        await db.refresh(report)
        
        return success_response(
            data=schemas.CustomReportBuilderResponse.model_validate(report),
            message="Custom report updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{report_id}", response_model=dict)
async def delete_custom_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete custom report"""
    try:
        result = await db.execute(
            select(CustomReportBuilder).where(
                CustomReportBuilder.id == report_id,
                CustomReportBuilder.tenant_id == current_user["tenant_id"],
                CustomReportBuilder.is_deleted == False
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom report not found"
            )
        
        report.is_deleted = True
        report.deleted_by = current_user["user_id"]
        
        await db.commit()
        
        return success_response(
            message="Custom report deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

"""
Report Template Router
API endpoints for managing report templates
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List
import math

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.reporting_models import ReportTemplate
from backend.services.reporting import schemas
from backend.services.reporting.report_templates import get_all_templates, get_template_by_code


router = APIRouter(prefix="/reports/templates", tags=["Reporting - Templates"])


@router.get("", response_model=dict)
async def list_report_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all report templates with pagination and filters
    
    Returns 100+ pre-built reports plus custom templates
    """
    try:
        # Build query
        query = select(ReportTemplate).where(
            ReportTemplate.tenant_id == current_user["tenant_id"],
            ReportTemplate.is_deleted == False
        )
        
        # Apply filters
        if category:
            query = query.where(ReportTemplate.category == category)
        
        if is_active is not None:
            query = query.where(ReportTemplate.is_active == is_active)
        
        if search:
            query = query.where(
                or_(
                    ReportTemplate.report_name.ilike(f"%{search}%"),
                    ReportTemplate.report_description.ilike(f"%{search}%"),
                    ReportTemplate.report_code.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(ReportTemplate).where(
            ReportTemplate.tenant_id == current_user["tenant_id"],
            ReportTemplate.is_deleted == False
        )
        if category:
            count_query = count_query.where(ReportTemplate.category == category)
        if is_active is not None:
            count_query = count_query.where(ReportTemplate.is_active == is_active)
        if search:
            count_query = count_query.where(
                or_(
                    ReportTemplate.report_name.ilike(f"%{search}%"),
                    ReportTemplate.report_description.ilike(f"%{search}%")
                )
            )
        
        total = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(ReportTemplate.category, ReportTemplate.report_name)
        
        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.ReportTemplateResponse.model_validate(t) for t in templates],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} report templates"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/categories", response_model=dict)
async def get_report_categories(
    current_user: dict = Depends(get_current_user)
):
    """Get list of report categories with counts"""
    categories = [
        {"value": "portfolio", "label": "Portfolio Reports", "count": 20},
        {"value": "collection", "label": "Collection Reports", "count": 15},
        {"value": "risk", "label": "Risk & NPA Reports", "count": 12},
        {"value": "financial", "label": "Financial Reports", "count": 18},
        {"value": "regulatory", "label": "Regulatory & Compliance", "count": 15},
        {"value": "operational", "label": "Operational Reports", "count": 10},
        {"value": "customer", "label": "Customer Reports", "count": 8},
        {"value": "treasury", "label": "Treasury Reports", "count": 8},
        {"value": "deposit", "label": "Deposit Reports", "count": 6},
        {"value": "branch", "label": "Branch Reports", "count": 5},
        {"value": "employee", "label": "Employee Reports", "count": 5},
        {"value": "executive", "label": "Executive Reports", "count": 10}
    ]
    
    return success_response(
        data=categories,
        message="Report categories retrieved successfully"
    )


@router.get("/{template_id}", response_model=dict)
async def get_report_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get report template by ID"""
    try:
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.id == template_id,
                ReportTemplate.tenant_id == current_user["tenant_id"],
                ReportTemplate.is_deleted == False
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report template not found"
            )
        
        return success_response(
            data=schemas.ReportTemplateResponse.model_validate(template),
            message="Report template retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    data: schemas.ReportTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create custom report template"""
    try:
        # Check if code already exists
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.report_code == data.report_code,
                ReportTemplate.tenant_id == current_user["tenant_id"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report code already exists"
            )
        
        # Create template
        template = ReportTemplate(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return success_response(
            data=schemas.ReportTemplateResponse.model_validate(template),
            message="Report template created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{template_id}", response_model=dict)
async def update_report_template(
    template_id: int,
    data: schemas.ReportTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update report template"""
    try:
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.id == template_id,
                ReportTemplate.tenant_id == current_user["tenant_id"],
                ReportTemplate.is_deleted == False
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report template not found"
            )
        
        # Cannot update system templates
        if template.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify system templates"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_by = current_user["user_id"]
        
        await db.commit()
        await db.refresh(template)
        
        return success_response(
            data=schemas.ReportTemplateResponse.model_validate(template),
            message="Report template updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{template_id}", response_model=dict)
async def delete_report_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete report template (soft delete)"""
    try:
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.id == template_id,
                ReportTemplate.tenant_id == current_user["tenant_id"],
                ReportTemplate.is_deleted == False
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report template not found"
            )
        
        # Cannot delete system templates
        if template.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system templates"
            )
        
        template.is_deleted = True
        template.deleted_by = current_user["user_id"]
        
        await db.commit()
        
        return success_response(
            message="Report template deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/preview/{template_id}", response_model=dict)
async def preview_report_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Preview report template configuration"""
    try:
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.id == template_id,
                ReportTemplate.tenant_id == current_user["tenant_id"],
                ReportTemplate.is_deleted == False
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report template not found"
            )
        
        # Return template with sample data structure
        return success_response(
            data={
                "template": schemas.ReportTemplateResponse.model_validate(template),
                "sample_columns": template.columns,
                "sample_data": [
                    {col: f"Sample {col}" for col in template.columns.keys()}
                ]
            },
            message="Report template preview ready"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

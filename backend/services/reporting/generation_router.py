"""
Report Generation Router
API endpoints for generating and managing reports
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from typing import Optional
from datetime import datetime, timedelta
import math
import json

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.reporting_models import (
    ReportTemplate, GeneratedReport, ScheduledReport
)
from backend.services.reporting import schemas


router = APIRouter(prefix="/reports", tags=["Reporting - Generation"])


async def execute_report_query(
    db: AsyncSession,
    template: ReportTemplate,
    parameters: dict,
    tenant_id: str
) -> dict:
    """Execute report query and return results"""
    try:
        # Add tenant_id to parameters
        params = {**parameters, "tenant_id": tenant_id}
        
        # Execute query
        result = await db.execute(text(template.query_template), params)
        rows = result.fetchall()
        
        # Convert to list of dicts
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        
        return {
            "data": data,
            "row_count": len(data),
            "columns": list(columns)
        }
        
    except Exception as e:
        raise Exception(f"Query execution failed: {str(e)}")


@router.post("/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: schemas.GenerateReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate report from template
    
    Executes report query and returns results
    """
    try:
        # Get template
        if not request.template_id and not request.custom_report_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either template_id or custom_report_id required"
            )
        
        template = None
        if request.template_id:
            result = await db.execute(
                select(ReportTemplate).where(
                    ReportTemplate.id == request.template_id,
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
        
        # Create generated report record
        generated = GeneratedReport(
            tenant_id=current_user["tenant_id"],
            template_id=request.template_id,
            custom_report_id=request.custom_report_id,
            report_name=template.report_name,
            report_category=template.category,
            parameters=request.parameters or {},
            filters=request.filters or {},
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end,
            file_format=request.file_format,
            status=schemas.ReportStatus.IN_PROGRESS,
            generated_by=current_user["user_id"],
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(generated)
        await db.commit()
        await db.refresh(generated)
        
        # Execute query
        start_time = datetime.utcnow()
        
        try:
            # Prepare parameters
            params = request.parameters or {}
            if request.date_range_start:
                params["date_from"] = request.date_range_start
            if request.date_range_end:
                params["date_to"] = request.date_range_end
            
            # Execute report
            result = await execute_report_query(
                db, template, params, current_user["tenant_id"]
            )
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update generated report
            generated.status = schemas.ReportStatus.COMPLETED
            generated.row_count = result["row_count"]
            generated.execution_time_ms = execution_time
            generated.result_data = result["data"][:1000]  # Limit stored data
            generated.expires_at = datetime.utcnow() + timedelta(days=30)
            
            await db.commit()
            await db.refresh(generated)
            
            return success_response(
                data={
                    "report": schemas.GeneratedReportResponse.model_validate(generated),
                    "data": result["data"],
                    "columns": result["columns"]
                },
                message=f"Report generated successfully with {result['row_count']} rows"
            )
            
        except Exception as e:
            # Update with error
            generated.status = schemas.ReportStatus.FAILED
            generated.error_message = str(e)
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Report generation failed: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/generated", response_model=dict)
async def list_generated_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List generated reports with pagination"""
    try:
        # Build query
        query = select(GeneratedReport).where(
            GeneratedReport.tenant_id == current_user["tenant_id"],
            GeneratedReport.is_deleted == False
        )
        
        # Apply filters
        if status_filter:
            query = query.where(GeneratedReport.status == status_filter)
        
        if category:
            query = query.where(GeneratedReport.report_category == category)
        
        if start_date:
            query = query.where(GeneratedReport.generation_date >= start_date)
        
        if end_date:
            query = query.where(GeneratedReport.generation_date <= end_date)
        
        # Get total count
        count_query = select(func.count()).select_from(GeneratedReport).where(
            GeneratedReport.tenant_id == current_user["tenant_id"],
            GeneratedReport.is_deleted == False
        )
        
        if status_filter:
            count_query = count_query.where(GeneratedReport.status == status_filter)
        if category:
            count_query = count_query.where(GeneratedReport.report_category == category)
        if start_date:
            count_query = count_query.where(GeneratedReport.generation_date >= start_date)
        if end_date:
            count_query = count_query.where(GeneratedReport.generation_date <= end_date)
        
        total = await db.scalar(count_query)
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(GeneratedReport.generation_date.desc())
        
        # Execute
        result = await db.execute(query)
        reports = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.GeneratedReportResponse.model_validate(r) for r in reports],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} generated reports"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/generated/{report_id}", response_model=dict)
async def get_generated_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get generated report by ID"""
    try:
        result = await db.execute(
            select(GeneratedReport).where(
                GeneratedReport.id == report_id,
                GeneratedReport.tenant_id == current_user["tenant_id"],
                GeneratedReport.is_deleted == False
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated report not found"
            )
        
        # Update access tracking
        report.accessed_count += 1
        report.last_accessed_at = datetime.utcnow()
        await db.commit()
        
        return success_response(
            data={
                "report": schemas.GeneratedReportResponse.model_validate(report),
                "data": report.result_data
            },
            message="Generated report retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/generated/{report_id}", response_model=dict)
async def delete_generated_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete generated report"""
    try:
        result = await db.execute(
            select(GeneratedReport).where(
                GeneratedReport.id == report_id,
                GeneratedReport.tenant_id == current_user["tenant_id"],
                GeneratedReport.is_deleted == False
            )
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated report not found"
            )
        
        report.is_deleted = True
        report.deleted_by = current_user["user_id"]
        
        await db.commit()
        
        return success_response(
            message="Generated report deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/schedule", response_model=dict, status_code=status.HTTP_201_CREATED)
async def schedule_report(
    data: schemas.ScheduledReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Schedule automated report generation"""
    try:
        # Verify template exists
        result = await db.execute(
            select(ReportTemplate).where(
                ReportTemplate.id == data.template_id,
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
        
        # Create scheduled report
        scheduled = ScheduledReport(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        # Calculate next run time
        # TODO: Implement proper scheduling logic
        scheduled.next_run_at = datetime.utcnow() + timedelta(days=1)
        
        db.add(scheduled)
        await db.commit()
        await db.refresh(scheduled)
        
        return success_response(
            data=schemas.ScheduledReportResponse.model_validate(scheduled),
            message="Report scheduled successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/schedule/list", response_model=dict)
async def list_scheduled_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List scheduled reports"""
    try:
        query = select(ScheduledReport).where(
            ScheduledReport.tenant_id == current_user["tenant_id"],
            ScheduledReport.is_deleted == False
        )
        
        if is_active is not None:
            query = query.where(ScheduledReport.is_active == is_active)
        
        # Get total
        count_query = select(func.count()).select_from(ScheduledReport).where(
            ScheduledReport.tenant_id == current_user["tenant_id"],
            ScheduledReport.is_deleted == False
        )
        if is_active is not None:
            count_query = count_query.where(ScheduledReport.is_active == is_active)
        
        total = await db.scalar(count_query)
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(ScheduledReport.next_run_at)
        
        result = await db.execute(query)
        scheduled_reports = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.ScheduledReportResponse.model_validate(s) for s in scheduled_reports],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} scheduled reports"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/schedule/{schedule_id}", response_model=dict)
async def delete_scheduled_report(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete scheduled report"""
    try:
        result = await db.execute(
            select(ScheduledReport).where(
                ScheduledReport.id == schedule_id,
                ScheduledReport.tenant_id == current_user["tenant_id"],
                ScheduledReport.is_deleted == False
            )
        )
        scheduled = result.scalar_one_or_none()
        
        if not scheduled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled report not found"
            )
        
        scheduled.is_deleted = True
        scheduled.deleted_by = current_user["user_id"]
        
        await db.commit()
        
        return success_response(
            message="Scheduled report deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

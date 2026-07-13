"""
CRM Customer Service API Routes
Ticket Management, Knowledge Base, SLA Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from backend.shared.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.auth.dependencies import get_current_user
from backend.crm.services.service_service import TicketService, KnowledgeBaseService, SLAService
from backend.shared.schemas.crm_service_schemas import (
    TicketCreate, TicketUpdate, TicketResponse, TicketListParams, TicketListResponse,
    TicketCommentCreate, TicketCommentResponse,
    TicketStatusUpdate, TicketAssignmentUpdate, TicketSatisfactionUpdate,
    KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticleResponse,
    KnowledgeArticleListParams, KnowledgeArticleListResponse,
    ArticleFeedbackUpdate,
    SLACreate, SLAUpdate, SLAResponse, SLAListParams, SLAListResponse,
    TicketAPIResponse, TicketListAPIResponse,
    KnowledgeArticleAPIResponse, KnowledgeArticleListAPIResponse,
    SLAAPIResponse, SLAListAPIResponse,
    TicketStats, ServiceDashboardAPIResponse
)

# Create routers
ticket_router = APIRouter()
knowledge_router = APIRouter()
sla_router = APIRouter()


# ============================================================================
# TICKET ROUTES
# ============================================================================

@ticket_router.post("/tickets", response_model=TicketAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ticket"""
    try:
        service = TicketService(db)
        ticket = await service.create_ticket(data, current_user["tenant_id"], current_user["user_id"])
        
        return TicketAPIResponse(
            success=True,
            message="Ticket created successfully",
            data=TicketResponse.from_orm(ticket)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@ticket_router.get("/tickets", response_model=TicketListAPIResponse)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    account_id: Optional[UUID] = None,
    sla_breached: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List tickets with filters"""
    try:
        params = TicketListParams(
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            priority=priority,
            category=category,
            assigned_to=assigned_to,
            account_id=account_id,
            sla_breached=sla_breached
        )
        
        service = TicketService(db)
        result = await service.list_tickets(params, current_user["tenant_id"])
        
        return TicketListAPIResponse(
            success=True,
            data=TicketListResponse(**result)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@ticket_router.get("/tickets/{ticket_id}", response_model=TicketAPIResponse)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket by ID"""
    try:
        service = TicketService(db)
        ticket = await service.get_ticket(str(ticket_id), current_user["tenant_id"])
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return TicketAPIResponse(
            success=True,
            data=TicketResponse.from_orm(ticket)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@ticket_router.put("/tickets/{ticket_id}", response_model=TicketAPIResponse)
async def update_ticket(
    ticket_id: UUID,
    data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update ticket"""
    try:
        service = TicketService(db)
        ticket = await service.update_ticket(str(ticket_id), data, current_user["tenant_id"], current_user["user_id"])
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return TicketAPIResponse(
            success=True,
            message="Ticket updated successfully",
            data=TicketResponse.from_orm(ticket)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@ticket_router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete ticket"""
    try:
        service = TicketService(db)
        success = await service.delete_ticket(str(ticket_id), current_user["tenant_id"], current_user["user_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return {"success": True, "message": "Ticket deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@ticket_router.post("/tickets/{ticket_id}/comments")
async def add_ticket_comment(
    ticket_id: UUID,
    data: TicketCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add comment to ticket"""
    try:
        data.ticket_id = ticket_id
        service = TicketService(db)
        comment = await service.add_comment(str(ticket_id), data, current_user["tenant_id"], current_user["user_id"])
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "data": TicketCommentResponse.from_orm(comment)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@ticket_router.get("/tickets/stats/overview")
async def get_ticket_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket statistics"""
    try:
        service = TicketService(db)
        stats = await service.get_ticket_stats(current_user["tenant_id"])
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



# ============================================================================
# KNOWLEDGE BASE ROUTES
# ============================================================================

@knowledge_router.post("/knowledge/articles", response_model=KnowledgeArticleAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: KnowledgeArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create knowledge base article"""
    try:
        service = KnowledgeBaseService(db)
        article = await service.create_article(data, current_user["tenant_id"], current_user["user_id"])
        
        return KnowledgeArticleAPIResponse(
            success=True,
            message="Article created successfully",
            data=KnowledgeArticleResponse.from_orm(article)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.get("/knowledge/articles", response_model=KnowledgeArticleListAPIResponse)
async def list_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    is_featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List knowledge base articles"""
    try:
        params = KnowledgeArticleListParams(
            skip=skip,
            limit=limit,
            search=search,
            category=category,
            status=status,
            is_featured=is_featured
        )
        
        service = KnowledgeBaseService(db)
        result = await service.list_articles(params, current_user["tenant_id"])
        
        return KnowledgeArticleListAPIResponse(
            success=True,
            data=KnowledgeArticleListResponse(**result)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.get("/knowledge/articles/{article_id}", response_model=KnowledgeArticleAPIResponse)
async def get_article(
    article_id: UUID,
    increment_view: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get article by ID"""
    try:
        service = KnowledgeBaseService(db)
        article = await service.get_article(str(article_id), current_user["tenant_id"], increment_view)
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        return KnowledgeArticleAPIResponse(
            success=True,
            data=KnowledgeArticleResponse.from_orm(article)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.get("/knowledge/articles/slug/{slug}", response_model=KnowledgeArticleAPIResponse)
async def get_article_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get article by slug"""
    try:
        service = KnowledgeBaseService(db)
        article = await service.get_article_by_slug(slug, current_user["tenant_id"])
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        return KnowledgeArticleAPIResponse(
            success=True,
            data=KnowledgeArticleResponse.from_orm(article)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.put("/knowledge/articles/{article_id}", response_model=KnowledgeArticleAPIResponse)
async def update_article(
    article_id: UUID,
    data: KnowledgeArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update article"""
    try:
        service = KnowledgeBaseService(db)
        article = await service.update_article(str(article_id), data, current_user["tenant_id"], current_user["user_id"])
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        return KnowledgeArticleAPIResponse(
            success=True,
            message="Article updated successfully",
            data=KnowledgeArticleResponse.from_orm(article)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.delete("/knowledge/articles/{article_id}")
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete article"""
    try:
        service = KnowledgeBaseService(db)
        success = await service.delete_article(str(article_id), current_user["tenant_id"], current_user["user_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        return {"success": True, "message": "Article deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@knowledge_router.post("/knowledge/articles/{article_id}/feedback")
async def record_article_feedback(
    article_id: UUID,
    data: ArticleFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Record article feedback (helpful/not helpful)"""
    try:
        service = KnowledgeBaseService(db)
        success = await service.record_feedback(str(article_id), data.helpful, current_user["tenant_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        return {"success": True, "message": "Feedback recorded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



# ============================================================================
# SLA ROUTES
# ============================================================================

@sla_router.post("/slas", response_model=SLAAPIResponse, status_code=status.HTTP_201_CREATED)
async def create_sla(
    data: SLACreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create SLA"""
    try:
        service = SLAService(db)
        sla = await service.create_sla(data, current_user["tenant_id"], current_user["user_id"])
        
        return SLAAPIResponse(
            success=True,
            message="SLA created successfully",
            data=SLAResponse.from_orm(sla)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sla_router.get("/slas", response_model=SLAListAPIResponse)
async def list_slas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List SLAs"""
    try:
        params = SLAListParams(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            category=category
        )
        
        service = SLAService(db)
        result = await service.list_slas(params, current_user["tenant_id"])
        
        return SLAListAPIResponse(
            success=True,
            data=SLAListResponse(**result)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sla_router.get("/slas/{sla_id}", response_model=SLAAPIResponse)
async def get_sla(
    sla_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get SLA by ID"""
    try:
        service = SLAService(db)
        sla = await service.get_sla(str(sla_id), current_user["tenant_id"])
        
        if not sla:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA not found"
            )
        
        return SLAAPIResponse(
            success=True,
            data=SLAResponse.from_orm(sla)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sla_router.put("/slas/{sla_id}", response_model=SLAAPIResponse)
async def update_sla(
    sla_id: UUID,
    data: SLAUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update SLA"""
    try:
        service = SLAService(db)
        sla = await service.update_sla(str(sla_id), data, current_user["tenant_id"], current_user["user_id"])
        
        if not sla:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA not found"
            )
        
        return SLAAPIResponse(
            success=True,
            message="SLA updated successfully",
            data=SLAResponse.from_orm(sla)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sla_router.delete("/slas/{sla_id}")
async def delete_sla(
    sla_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete SLA"""
    try:
        service = SLAService(db)
        success = await service.delete_sla(str(sla_id), current_user["tenant_id"], current_user["user_id"])
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA not found"
            )
        
        return {"success": True, "message": "SLA deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@sla_router.get("/slas/violations/list")
async def get_sla_violations(
    ticket_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get SLA violations"""
    try:
        service = SLAService(db)
        violations = await service.get_sla_violations(
            current_user["tenant_id"],
            str(ticket_id) if ticket_id else None
        )
        
        return {
            "success": True,
            "data": violations
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

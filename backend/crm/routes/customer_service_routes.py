"""
CRM Customer Service Routes
API endpoints for ticket management, knowledge base, and SLA tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, check_permission
from backend.crm.services.customer_service import CustomerServiceService
from backend.crm.schemas.customer_service_schemas import (
    TicketCreate, TicketUpdate, TicketResponse, TicketDetailResponse,
    TicketListResponse, TicketAssign, TicketResolve, TicketClose,
    TicketReopen, TicketRating, TicketCommentCreate, TicketCommentResponse,
    SLAPolicyCreate, SLAPolicyUpdate, SLAPolicyResponse, SLAMetricsResponse,
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    KnowledgeBaseListResponse, KnowledgeBaseSearchResponse,
    KnowledgeBaseFeedbackCreate, TicketFilterParams,
    TicketStatistics, DashboardResponse
)

router = APIRouter(prefix="/api/v1/crm/customer-service", tags=["CRM - Customer Service"])


# ==================== TICKET MANAGEMENT ====================

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new support ticket"""
    try:
        ticket = CustomerServiceService.create_ticket(
            db, ticket_data,
            current_user["tenant_id"],
            current_user["id"]
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket details"""
    ticket = CustomerServiceService.get_ticket(db, ticket_id, current_user["tenant_id"])
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    # Get comments and activities
    comments = CustomerServiceService.get_ticket_comments(db, ticket_id, current_user["tenant_id"])
    
    # Build response
    response = TicketDetailResponse.model_validate(ticket)
    response.comments = comments
    response.activities = ticket.activities
    
    return response


@router.get("/tickets/number/{ticket_number}", response_model=TicketDetailResponse)
async def get_ticket_by_number(
    ticket_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket by ticket number"""
    ticket = CustomerServiceService.get_ticket_by_number(db, ticket_number, current_user["tenant_id"])
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    
    comments = CustomerServiceService.get_ticket_comments(db, ticket.id, current_user["tenant_id"])
    response = TicketDetailResponse.model_validate(ticket)
    response.comments = comments
    response.activities = ticket.activities
    
    return response


@router.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    status: Optional[List[str]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    category: Optional[List[str]] = Query(None),
    assigned_to_user_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    channel: Optional[List[str]] = Query(None),
    sla_status: Optional[List[str]] = Query(None),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    search_query: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List tickets with filtering and pagination"""
    filters = TicketFilterParams(
        status=status,
        priority=priority,
        category=category,
        assigned_to_user_id=assigned_to_user_id,
        customer_id=customer_id,
        channel=channel,
        sla_status=sla_status,
        from_date=from_date,
        to_date=to_date,
        search_query=search_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    tickets, total = CustomerServiceService.list_tickets(db, current_user["tenant_id"], filters)
    total_pages = (total + page_size - 1) // page_size
    
    return TicketListResponse(
        tickets=tickets,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update ticket details"""
    try:
        ticket = CustomerServiceService.update_ticket(
            db, ticket_id, current_user["tenant_id"],
            ticket_data, current_user["id"]
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tickets/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: int,
    assign_data: TicketAssign,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Assign ticket to user or team"""
    try:
        ticket = CustomerServiceService.assign_ticket(
            db, ticket_id, current_user["tenant_id"],
            assign_data, current_user["id"]
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tickets/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket(
    ticket_id: int,
    resolve_data: TicketResolve,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark ticket as resolved"""
    try:
        ticket = CustomerServiceService.resolve_ticket(
            db, ticket_id, current_user["tenant_id"],
            resolve_data, current_user["id"]
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tickets/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    ticket_id: int,
    close_data: TicketClose,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Close a ticket"""
    try:
        ticket = CustomerServiceService.close_ticket(
            db, ticket_id, current_user["tenant_id"],
            current_user["id"], close_data.closing_notes
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tickets/{ticket_id}/reopen", response_model=TicketResponse)
async def reopen_ticket(
    ticket_id: int,
    reopen_data: TicketReopen,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reopen a closed ticket"""
    try:
        ticket = CustomerServiceService.reopen_ticket(
            db, ticket_id, current_user["tenant_id"],
            reopen_data.reason, current_user["id"]
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tickets/{ticket_id}/rating", response_model=TicketResponse)
async def add_ticket_rating(
    ticket_id: int,
    rating_data: TicketRating,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add customer satisfaction rating"""
    try:
        ticket = CustomerServiceService.add_ticket_rating(
            db, ticket_id, current_user["tenant_id"],
            rating_data.rating, rating_data.feedback
        )
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== TICKET COMMENTS ====================

@router.post("/tickets/{ticket_id}/comments", response_model=TicketCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_ticket_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add comment to ticket"""
    try:
        comment = CustomerServiceService.add_comment(
            db, ticket_id, current_user["tenant_id"],
            comment_data, current_user["id"]
        )
        return comment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tickets/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: int,
    include_internal: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all comments for a ticket"""
    try:
        comments = CustomerServiceService.get_ticket_comments(
            db, ticket_id, current_user["tenant_id"], include_internal
        )
        return comments
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== SLA MANAGEMENT ====================

@router.post("/sla-policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_sla_policy(
    sla_data: SLAPolicyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create SLA policy"""
    try:
        sla_policy = CustomerServiceService.create_sla_policy(
            db, sla_data, current_user["tenant_id"], current_user["id"]
        )
        return sla_policy
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sla-policies", response_model=List[SLAPolicyResponse])
async def list_sla_policies(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all SLA policies"""
    policies = CustomerServiceService.get_sla_policies(db, current_user["tenant_id"], active_only)
    return policies


@router.get("/sla-policies/{sla_id}", response_model=SLAPolicyResponse)
async def get_sla_policy(
    sla_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get SLA policy by ID"""
    from backend.shared.database.crm_customer_service_models import SLAPolicy
    
    policy = db.query(SLAPolicy).filter(
        SLAPolicy.id == sla_id,
        SLAPolicy.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA policy not found")
    
    return policy


@router.put("/sla-policies/{sla_id}", response_model=SLAPolicyResponse)
async def update_sla_policy(
    sla_id: int,
    sla_data: SLAPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update SLA policy"""
    try:
        policy = CustomerServiceService.update_sla_policy(
            db, sla_id, current_user["tenant_id"], sla_data
        )
        return policy
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sla-metrics", response_model=SLAMetricsResponse)
async def get_sla_metrics(
    from_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get SLA compliance metrics"""
    metrics = CustomerServiceService.get_sla_metrics(db, current_user["tenant_id"], from_date)
    return SLAMetricsResponse(**metrics)


# ==================== KNOWLEDGE BASE ====================

@router.post("/knowledge-base", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base_article(
    article_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create knowledge base article"""
    try:
        article = CustomerServiceService.create_article(
            db, article_data, current_user["tenant_id"], current_user["id"]
        )
        return article
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/knowledge-base", response_model=KnowledgeBaseListResponse)
async def list_knowledge_base_articles(
    category: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List knowledge base articles"""
    from backend.shared.database.crm_customer_service_models import KnowledgeBaseArticle
    from sqlalchemy import desc
    
    query = db.query(KnowledgeBaseArticle).filter(
        KnowledgeBaseArticle.tenant_id == current_user["tenant_id"],
        KnowledgeBaseArticle.is_deleted == False
    )
    
    if category:
        query = query.filter(KnowledgeBaseArticle.category == category)
    
    if status:
        query = query.filter(KnowledgeBaseArticle.status == status)
    
    total = query.count()
    
    articles = query.order_by(desc(KnowledgeBaseArticle.created_at))\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return KnowledgeBaseListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/knowledge-base/{article_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base article by ID"""
    from backend.shared.database.crm_customer_service_models import KnowledgeBaseArticle
    
    article = db.query(KnowledgeBaseArticle).filter(
        KnowledgeBaseArticle.id == article_id,
        KnowledgeBaseArticle.tenant_id == current_user["tenant_id"],
        KnowledgeBaseArticle.is_deleted == False
    ).first()
    
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    # Increment view count
    CustomerServiceService.increment_article_view(db, article_id, current_user["tenant_id"])
    
    return article


@router.get("/knowledge-base/slug/{slug}", response_model=KnowledgeBaseResponse)
async def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get knowledge base article by slug"""
    from backend.shared.database.crm_customer_service_models import KnowledgeBaseArticle
    
    article = db.query(KnowledgeBaseArticle).filter(
        KnowledgeBaseArticle.slug == slug,
        KnowledgeBaseArticle.tenant_id == current_user["tenant_id"],
        KnowledgeBaseArticle.is_deleted == False
    ).first()
    
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    CustomerServiceService.increment_article_view(db, article.id, current_user["tenant_id"])
    
    return article


@router.put("/knowledge-base/{article_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base_article(
    article_id: int,
    article_data: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update knowledge base article"""
    try:
        article = CustomerServiceService.update_article(
            db, article_id, current_user["tenant_id"],
            article_data, current_user["id"]
        )
        return article
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/knowledge-base/{article_id}/publish", response_model=KnowledgeBaseResponse)
async def publish_knowledge_base_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Publish knowledge base article"""
    try:
        article = CustomerServiceService.publish_article(
            db, article_id, current_user["tenant_id"], current_user["id"]
        )
        return article
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/knowledge-base/search", response_model=KnowledgeBaseSearchResponse)
async def search_knowledge_base(
    q: str = Query(..., min_length=3, description="Search query"),
    category: Optional[str] = None,
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search knowledge base articles"""
    articles = CustomerServiceService.search_articles(
        db, current_user["tenant_id"], q, category, public_only
    )
    
    return KnowledgeBaseSearchResponse(
        articles=articles,
        total=len(articles),
        search_query=q
    )


@router.post("/knowledge-base/{article_id}/feedback")
async def add_article_feedback(
    article_id: int,
    feedback_data: KnowledgeBaseFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add feedback to knowledge base article"""
    try:
        feedback = CustomerServiceService.add_article_feedback(
            db, article_id, current_user["tenant_id"],
            feedback_data.is_helpful, feedback_data.rating,
            feedback_data.comment, current_user["id"]
        )
        return {"message": "Feedback recorded successfully", "id": feedback.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/knowledge-base/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Soft delete knowledge base article"""
    from backend.shared.database.crm_customer_service_models import KnowledgeBaseArticle
    
    article = db.query(KnowledgeBaseArticle).filter(
        KnowledgeBaseArticle.id == article_id,
        KnowledgeBaseArticle.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    
    article.is_deleted = True
    db.commit()
    
    return None


# ==================== DASHBOARD & STATISTICS ====================

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get customer service dashboard data"""
    
    # Get ticket statistics
    stats = CustomerServiceService.get_ticket_statistics(
        db, current_user["tenant_id"], from_date, to_date
    )
    
    # Get SLA metrics
    sla_metrics = CustomerServiceService.get_sla_metrics(
        db, current_user["tenant_id"], from_date
    )
    
    # Get tickets by category, priority, channel
    from backend.shared.database.crm_customer_service_models import Ticket
    from sqlalchemy import func
    
    query = db.query(Ticket).filter(
        Ticket.tenant_id == current_user["tenant_id"],
        Ticket.is_deleted == False
    )
    
    if from_date:
        query = query.filter(Ticket.created_at >= from_date)
    if to_date:
        query = query.filter(Ticket.created_at <= to_date)
    
    # Tickets by category
    category_counts = db.query(
        Ticket.category,
        func.count(Ticket.id)
    ).filter(
        Ticket.tenant_id == current_user["tenant_id"],
        Ticket.is_deleted == False
    ).group_by(Ticket.category).all()
    
    tickets_by_category = {str(cat): count for cat, count in category_counts}
    
    # Tickets by priority
    priority_counts = db.query(
        Ticket.priority,
        func.count(Ticket.id)
    ).filter(
        Ticket.tenant_id == current_user["tenant_id"],
        Ticket.is_deleted == False
    ).group_by(Ticket.priority).all()
    
    tickets_by_priority = {str(pri): count for pri, count in priority_counts}
    
    # Tickets by channel
    channel_counts = db.query(
        Ticket.channel,
        func.count(Ticket.id)
    ).filter(
        Ticket.tenant_id == current_user["tenant_id"],
        Ticket.is_deleted == False
    ).group_by(Ticket.channel).all()
    
    tickets_by_channel = {str(ch): count for ch, count in channel_counts}
    
    return DashboardResponse(
        statistics=TicketStatistics(**stats),
        sla_metrics=SLAMetricsResponse(**sla_metrics),
        top_agents=[],  # TODO: Implement agent performance
        ticket_trends=[],  # TODO: Implement trends
        tickets_by_category=tickets_by_category,
        tickets_by_priority=tickets_by_priority,
        tickets_by_channel=tickets_by_channel
    )


@router.get("/statistics", response_model=TicketStatistics)
async def get_ticket_statistics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket statistics"""
    stats = CustomerServiceService.get_ticket_statistics(
        db, current_user["tenant_id"], from_date, to_date
    )
    return TicketStatistics(**stats)

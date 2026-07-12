"""
CRM Customer Service Business Logic
Ticket Management, Knowledge Base, SLA Tracking
"""

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import re

from backend.shared.database.connection import Database
from backend.shared.database.crm_service_models import (
    Ticket, TicketComment, TicketAttachment,
    KnowledgeArticle, ArticleAttachment,
    SLA, SLAViolation,
    TicketStatus, TicketPriority, SLAMetricType
)
from backend.shared.schemas.crm_service_schemas import (
    TicketCreate, TicketUpdate, TicketListParams,
    TicketCommentCreate, TicketCommentUpdate,
    KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticleListParams,
    SLACreate, SLAUpdate, SLAListParams,
    SLAViolationCreate,
    TicketStats, ServiceDashboard
)


class TicketService:
    """Service for ticket management operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def generate_ticket_number(self) -> str:
        """Generate unique ticket number: TKT-YYYYMMDD-XXXX"""
        today = datetime.now()
        prefix = f"TKT-{today.strftime('%Y%m%d')}"
        
        # Get count of tickets created today
        session = self.db.sync_session
        result = session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.ticket_number.like(f"{prefix}%"))
        )
        count = result.scalar() or 0
        
        return f"{prefix}-{str(count + 1).zfill(4)}"

    
    async def calculate_sla_due_dates(self, ticket: Ticket, sla: SLA) -> Dict[str, datetime]:
        """Calculate SLA due dates based on business hours"""
        created_at = ticket.created_at or datetime.now()
        
        if not sla.use_business_hours:
            # Simple calculation without business hours
            first_response_due = created_at + timedelta(minutes=sla.first_response_time)
            resolution_due = created_at + timedelta(minutes=sla.resolution_time)
        else:
            # Calculate with business hours
            first_response_due = self._add_business_minutes(
                created_at, sla.first_response_time, sla
            )
            resolution_due = self._add_business_minutes(
                created_at, sla.resolution_time, sla
            )
        
        return {
            "first_response_due": first_response_due,
            "resolution_due": resolution_due
        }
    
    def _add_business_minutes(self, start_time: datetime, minutes: int, sla: SLA) -> datetime:
        """Add business minutes to a datetime"""
        current = start_time
        remaining_minutes = minutes
        
        # Parse business hours
        start_hour, start_min = map(int, sla.business_hours_start.split(':'))
        end_hour, end_min = map(int, sla.business_hours_end.split(':'))
        
        while remaining_minutes > 0:
            # Check if current day is a business day (1=Monday, 7=Sunday)
            weekday = current.isoweekday()
            
            if weekday in sla.business_days:
                # Check if within business hours
                business_start = current.replace(hour=start_hour, minute=start_min, second=0)
                business_end = current.replace(hour=end_hour, minute=end_min, second=0)
                
                if current < business_start:
                    current = business_start
                
                if current < business_end:
                    # Calculate minutes until end of business day
                    minutes_until_eod = int((business_end - current).total_seconds() / 60)
                    
                    if remaining_minutes <= minutes_until_eod:
                        return current + timedelta(minutes=remaining_minutes)
                    else:
                        remaining_minutes -= minutes_until_eod
                        current = business_end
            
            # Move to next day
            current = (current + timedelta(days=1)).replace(hour=start_hour, minute=start_min, second=0)
        
        return current

    
    async def create_ticket(self, data: TicketCreate, tenant_id: str, user_id: str) -> Ticket:
        """Create a new ticket"""
        session = self.db.sync_session
        
        # Generate ticket number
        ticket_number = await self.generate_ticket_number()
        
        # Get applicable SLA
        if not data.sla_id:
            sla = await self.get_default_sla_for_ticket(data.priority, data.category, tenant_id)
            data.sla_id = sla.id if sla else None
        
        # Create ticket
        ticket = Ticket(
            tenant_id=tenant_id,
            ticket_number=ticket_number,
            subject=data.subject,
            description=data.description,
            category=data.category,
            priority=data.priority,
            status=data.status,
            channel=data.channel,
            account_id=data.account_id,
            contact_name=data.contact_name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            assigned_to=data.assigned_to,
            assigned_team=data.assigned_team,
            sla_id=data.sla_id,
            parent_ticket_id=data.parent_ticket_id,
            related_article_id=data.related_article_id,
            tags=data.tags,
            custom_fields=data.custom_fields,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Calculate SLA due dates
        if data.sla_id:
            sla = session.get(SLA, data.sla_id)
            if sla:
                due_dates = await self.calculate_sla_due_dates(ticket, sla)
                ticket.first_response_due = due_dates["first_response_due"]
                ticket.resolution_due = due_dates["resolution_due"]
        
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        
        # Add system comment
        await self.add_comment(ticket.id, TicketCommentCreate(
            ticket_id=ticket.id,
            comment_type="system",
            content=f"Ticket created via {data.channel}",
            is_system=True
        ), tenant_id, user_id)
        
        return ticket

    
    async def get_default_sla_for_ticket(self, priority: TicketPriority, category: str, tenant_id: str) -> Optional[SLA]:
        """Get the most specific SLA for a ticket"""
        session = self.db.sync_session
        
        # Try to find exact match
        result = session.execute(
            select(SLA)
            .where(
                and_(
                    SLA.tenant_id == tenant_id,
                    SLA.status == "active",
                    SLA.priority == priority,
                    SLA.category == category
                )
            )
            .order_by(SLA.display_order)
            .limit(1)
        )
        sla = result.scalar_one_or_none()
        if sla:
            return sla
        
        # Try priority match
        result = session.execute(
            select(SLA)
            .where(
                and_(
                    SLA.tenant_id == tenant_id,
                    SLA.status == "active",
                    SLA.priority == priority,
                    SLA.category.is_(None)
                )
            )
            .order_by(SLA.display_order)
            .limit(1)
        )
        sla = result.scalar_one_or_none()
        if sla:
            return sla
        
        # Get default SLA
        result = session.execute(
            select(SLA)
            .where(
                and_(
                    SLA.tenant_id == tenant_id,
                    SLA.status == "active",
                    SLA.is_default == True
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_ticket(self, ticket_id: str, tenant_id: str) -> Optional[Ticket]:
        """Get ticket by ID"""
        session = self.db.sync_session
        result = session.execute(
            select(Ticket)
            .where(and_(Ticket.id == ticket_id, Ticket.tenant_id == tenant_id, Ticket.is_deleted == False))
            .options(selectinload(Ticket.comments), selectinload(Ticket.attachments))
        )
        return result.scalar_one_or_none()

    
    async def update_ticket(self, ticket_id: str, data: TicketUpdate, tenant_id: str, user_id: str) -> Optional[Ticket]:
        """Update ticket"""
        session = self.db.sync_session
        ticket = await self.get_ticket(ticket_id, tenant_id)
        
        if not ticket:
            return None
        
        old_status = ticket.status
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        ticket.updated_by = user_id
        
        # Track status changes
        if data.status and data.status != old_status:
            if data.status == TicketStatus.IN_PROGRESS and not ticket.first_response_at:
                ticket.first_response_at = datetime.now()
            elif data.status == TicketStatus.RESOLVED and not ticket.resolved_at:
                ticket.resolved_at = datetime.now()
            elif data.status == TicketStatus.CLOSED and not ticket.closed_at:
                ticket.closed_at = datetime.now()
            
            # Add system comment
            await self.add_comment(ticket.id, TicketCommentCreate(
                ticket_id=ticket.id,
                comment_type="status_change",
                content=f"Status changed from {old_status} to {data.status}",
                is_system=True
            ), tenant_id, user_id)
        
        # Check SLA breach
        await self.check_sla_breach(ticket)
        
        session.commit()
        session.refresh(ticket)
        
        return ticket
    
    async def check_sla_breach(self, ticket: Ticket):
        """Check if ticket has breached SLA"""
        now = datetime.now()
        
        # Check first response SLA
        if ticket.first_response_due and not ticket.first_response_at:
            if now > ticket.first_response_due:
                ticket.sla_breached = True
                await self.create_sla_violation(ticket, SLAMetricType.FIRST_RESPONSE)
        
        # Check resolution SLA
        if ticket.resolution_due and not ticket.resolved_at:
            if now > ticket.resolution_due:
                ticket.sla_breached = True
                await self.create_sla_violation(ticket, SLAMetricType.RESOLUTION)

    
    async def create_sla_violation(self, ticket: Ticket, metric_type: SLAMetricType):
        """Create SLA violation record"""
        session = self.db.sync_session
        
        # Check if violation already exists
        existing = session.execute(
            select(SLAViolation)
            .where(
                and_(
                    SLAViolation.ticket_id == ticket.id,
                    SLAViolation.metric_type == metric_type,
                    SLAViolation.is_resolved == False
                )
            )
        ).scalar_one_or_none()
        
        if existing:
            return existing
        
        due_at = ticket.first_response_due if metric_type == SLAMetricType.FIRST_RESPONSE else ticket.resolution_due
        
        violation = SLAViolation(
            tenant_id=ticket.tenant_id,
            ticket_id=ticket.id,
            sla_id=ticket.sla_id,
            metric_type=metric_type,
            due_at=due_at,
            violated_at=datetime.now(),
            breach_duration=datetime.now() - due_at if due_at else None
        )
        
        session.add(violation)
        session.commit()
        
        return violation
    
    async def list_tickets(self, params: TicketListParams, tenant_id: str) -> Dict[str, Any]:
        """List tickets with filters and pagination"""
        session = self.db.sync_session
        
        query = select(Ticket).where(and_(Ticket.tenant_id == tenant_id, Ticket.is_deleted == False))
        
        # Apply filters
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    Ticket.ticket_number.ilike(search_term),
                    Ticket.subject.ilike(search_term),
                    Ticket.description.ilike(search_term)
                )
            )
        
        if params.status:
            query = query.where(Ticket.status == params.status)
        
        if params.priority:
            query = query.where(Ticket.priority == params.priority)
        
        if params.category:
            query = query.where(Ticket.category == params.category)
        
        if params.assigned_to:
            query = query.where(Ticket.assigned_to == params.assigned_to)
        
        if params.account_id:
            query = query.where(Ticket.account_id == params.account_id)
        
        if params.sla_breached is not None:
            query = query.where(Ticket.sla_breached == params.sla_breached)
        
        if params.created_from:
            query = query.where(Ticket.created_at >= params.created_from)
        
        if params.created_to:
            query = query.where(Ticket.created_at <= params.created_to)
        
        # Get total count
        total_result = session.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Ticket.created_at))
        query = query.offset(params.skip).limit(params.limit)
        
        result = session.execute(query)
        tickets = result.scalars().all()
        
        return {
            "tickets": tickets,
            "total": total,
            "page": (params.skip // params.limit) + 1,
            "page_size": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit
        }

    
    async def delete_ticket(self, ticket_id: str, tenant_id: str, user_id: str) -> bool:
        """Soft delete ticket"""
        session = self.db.sync_session
        ticket = await self.get_ticket(ticket_id, tenant_id)
        
        if not ticket:
            return False
        
        ticket.is_deleted = True
        ticket.updated_by = user_id
        session.commit()
        
        return True
    
    async def add_comment(self, ticket_id: str, data: TicketCommentCreate, tenant_id: str, user_id: str) -> TicketComment:
        """Add comment to ticket"""
        session = self.db.sync_session
        
        comment = TicketComment(
            tenant_id=tenant_id,
            ticket_id=ticket_id,
            comment_type=data.comment_type,
            content=data.content,
            is_internal=data.is_internal,
            is_system=data.is_system,
            created_by=user_id,
            updated_by=user_id
        )
        
        session.add(comment)
        session.commit()
        session.refresh(comment)
        
        # Update ticket's first response time if this is first non-system comment
        if not data.is_system:
            ticket = session.get(Ticket, ticket_id)
            if ticket and not ticket.first_response_at:
                ticket.first_response_at = datetime.now()
                session.commit()
        
        return comment
    
    async def get_ticket_stats(self, tenant_id: str) -> TicketStats:
        """Get ticket statistics"""
        session = self.db.sync_session
        
        # Total tickets
        total = session.execute(
            select(func.count(Ticket.id)).where(
                and_(Ticket.tenant_id == tenant_id, Ticket.is_deleted == False)
            )
        ).scalar() or 0
        
        # By status
        status_counts = {}
        for status in TicketStatus:
            count = session.execute(
                select(func.count(Ticket.id)).where(
                    and_(
                        Ticket.tenant_id == tenant_id,
                        Ticket.is_deleted == False,
                        Ticket.status == status
                    )
                )
            ).scalar() or 0
            status_counts[status.value] = count
        
        # SLA breached
        sla_breached = session.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.is_deleted == False,
                    Ticket.sla_breached == True
                )
            )
        ).scalar() or 0
        
        # Average response time
        avg_response = session.execute(
            select(func.avg(
                func.extract('epoch', Ticket.first_response_at - Ticket.created_at) / 60
            )).where(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.is_deleted == False,
                    Ticket.first_response_at.isnot(None)
                )
            )
        ).scalar()
        
        # Average resolution time
        avg_resolution = session.execute(
            select(func.avg(
                func.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 60
            )).where(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.is_deleted == False,
                    Ticket.resolved_at.isnot(None)
                )
            )
        ).scalar()
        
        # Average satisfaction
        avg_satisfaction = session.execute(
            select(func.avg(Ticket.satisfaction_rating)).where(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.is_deleted == False,
                    Ticket.satisfaction_rating.isnot(None)
                )
            )
        ).scalar()
        
        return TicketStats(
            total_tickets=total,
            new_tickets=status_counts.get('new', 0),
            open_tickets=status_counts.get('open', 0),
            in_progress_tickets=status_counts.get('in_progress', 0),
            pending_tickets=status_counts.get('pending_customer', 0) + status_counts.get('pending_internal', 0),
            resolved_tickets=status_counts.get('resolved', 0),
            closed_tickets=status_counts.get('closed', 0),
            sla_breached_tickets=sla_breached,
            avg_first_response_time=float(avg_response) if avg_response else None,
            avg_resolution_time=float(avg_resolution) if avg_resolution else None,
            avg_satisfaction_rating=float(avg_satisfaction) if avg_satisfaction else None
        )


class KnowledgeBaseService:
    """Service for knowledge base operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def generate_article_number(self) -> str:
        """Generate unique article number: KB-XXXXXX"""
        session = self.db.sync_session
        result = session.execute(select(func.count(KnowledgeArticle.id)))
        count = result.scalar() or 0
        
        return f"KB-{str(count + 1).zfill(6)}"

    
    async def create_article(self, data: KnowledgeArticleCreate, tenant_id: str, user_id: str) -> KnowledgeArticle:
        """Create knowledge base article"""
        session = self.db.sync_session
        
        article_number = await self.generate_article_number()
        
        # Ensure slug is unique
        slug = data.slug
        counter = 1
        while True:
            existing = session.execute(
                select(KnowledgeArticle).where(KnowledgeArticle.slug == slug)
            ).scalar_one_or_none()
            
            if not existing:
                break
            
            slug = f"{data.slug}-{counter}"
            counter += 1
        
        article = KnowledgeArticle(
            tenant_id=tenant_id,
            article_number=article_number,
            title=data.title,
            slug=slug,
            content=data.content,
            excerpt=data.excerpt,
            category=data.category,
            status=data.status,
            tags=data.tags,
            related_products=data.related_products,
            meta_description=data.meta_description,
            keywords=data.keywords,
            parent_article_id=data.parent_article_id,
            is_featured=data.is_featured,
            display_order=data.display_order,
            author_id=user_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        if data.status == "published":
            article.published_at = datetime.now()
        
        session.add(article)
        session.commit()
        session.refresh(article)
        
        return article
    
    async def get_article(self, article_id: str, tenant_id: str, increment_view: bool = False) -> Optional[KnowledgeArticle]:
        """Get article by ID"""
        session = self.db.sync_session
        result = session.execute(
            select(KnowledgeArticle)
            .where(and_(
                KnowledgeArticle.id == article_id,
                KnowledgeArticle.tenant_id == tenant_id,
                KnowledgeArticle.is_deleted == False
            ))
            .options(selectinload(KnowledgeArticle.attachments))
        )
        article = result.scalar_one_or_none()
        
        if article and increment_view:
            article.view_count += 1
            session.commit()
        
        return article
    
    async def get_article_by_slug(self, slug: str, tenant_id: str) -> Optional[KnowledgeArticle]:
        """Get article by slug"""
        session = self.db.sync_session
        result = session.execute(
            select(KnowledgeArticle)
            .where(and_(
                KnowledgeArticle.slug == slug,
                KnowledgeArticle.tenant_id == tenant_id,
                KnowledgeArticle.is_deleted == False
            ))
            .options(selectinload(KnowledgeArticle.attachments))
        )
        return result.scalar_one_or_none()

    
    async def update_article(self, article_id: str, data: KnowledgeArticleUpdate, tenant_id: str, user_id: str) -> Optional[KnowledgeArticle]:
        """Update article"""
        session = self.db.sync_session
        article = await self.get_article(article_id, tenant_id)
        
        if not article:
            return None
        
        old_status = article.status
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_by = user_id
        article.version += 1
        
        # Handle publishing
        if data.status and data.status != old_status:
            if data.status == "published" and not article.published_at:
                article.published_at = datetime.now()
            elif data.status != "published":
                article.published_at = None
        
        session.commit()
        session.refresh(article)
        
        return article
    
    async def list_articles(self, params: KnowledgeArticleListParams, tenant_id: str) -> Dict[str, Any]:
        """List articles with filters"""
        session = self.db.sync_session
        
        query = select(KnowledgeArticle).where(
            and_(KnowledgeArticle.tenant_id == tenant_id, KnowledgeArticle.is_deleted == False)
        )
        
        # Apply filters
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    KnowledgeArticle.title.ilike(search_term),
                    KnowledgeArticle.content.ilike(search_term),
                    KnowledgeArticle.excerpt.ilike(search_term)
                )
            )
        
        if params.category:
            query = query.where(KnowledgeArticle.category == params.category)
        
        if params.status:
            query = query.where(KnowledgeArticle.status == params.status)
        
        if params.tags:
            query = query.where(KnowledgeArticle.tags.overlap(params.tags))
        
        if params.is_featured is not None:
            query = query.where(KnowledgeArticle.is_featured == params.is_featured)
        
        if params.author_id:
            query = query.where(KnowledgeArticle.author_id == params.author_id)
        
        # Get total
        total_result = session.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        # Apply ordering and pagination
        query = query.order_by(
            desc(KnowledgeArticle.is_featured),
            asc(KnowledgeArticle.display_order),
            desc(KnowledgeArticle.published_at)
        )
        query = query.offset(params.skip).limit(params.limit)
        
        result = session.execute(query)
        articles = result.scalars().all()
        
        return {
            "articles": articles,
            "total": total,
            "page": (params.skip // params.limit) + 1,
            "page_size": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit
        }
    
    async def delete_article(self, article_id: str, tenant_id: str, user_id: str) -> bool:
        """Soft delete article"""
        session = self.db.sync_session
        article = await self.get_article(article_id, tenant_id)
        
        if not article:
            return False
        
        article.is_deleted = True
        article.updated_by = user_id
        session.commit()
        
        return True
    
    async def record_feedback(self, article_id: str, helpful: bool, tenant_id: str) -> bool:
        """Record article feedback"""
        session = self.db.sync_session
        article = await self.get_article(article_id, tenant_id)
        
        if not article:
            return False
        
        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        session.commit()
        
        return True


class SLAService:
    """Service for SLA management operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_sla(self, data: SLACreate, tenant_id: str, user_id: str) -> SLA:
        """Create SLA"""
        session = self.db.sync_session
        
        # If setting as default, unset other defaults
        if data.is_default:
            session.execute(
                select(SLA).where(
                    and_(SLA.tenant_id == tenant_id, SLA.is_default == True)
                )
            )
            for sla in session.scalars():
                sla.is_default = False
        
        sla = SLA(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            status=data.status,
            priority=data.priority,
            category=data.category,
            first_response_time=data.first_response_time,
            resolution_time=data.resolution_time,
            escalation_time=data.escalation_time,
            use_business_hours=data.use_business_hours,
            business_hours_start=data.business_hours_start,
            business_hours_end=data.business_hours_end,
            business_days=data.business_days,
            escalation_enabled=data.escalation_enabled,
            escalate_to=data.escalate_to,
            is_default=data.is_default,
            display_order=data.display_order,
            created_by=user_id,
            updated_by=user_id
        )
        
        session.add(sla)
        session.commit()
        session.refresh(sla)
        
        return sla

    
    async def get_sla(self, sla_id: str, tenant_id: str) -> Optional[SLA]:
        """Get SLA by ID"""
        session = self.db.sync_session
        result = session.execute(
            select(SLA).where(
                and_(SLA.id == sla_id, SLA.tenant_id == tenant_id, SLA.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_sla(self, sla_id: str, data: SLAUpdate, tenant_id: str, user_id: str) -> Optional[SLA]:
        """Update SLA"""
        session = self.db.sync_session
        sla = await self.get_sla(sla_id, tenant_id)
        
        if not sla:
            return None
        
        # If setting as default, unset other defaults
        if data.is_default and data.is_default != sla.is_default:
            other_slas = session.execute(
                select(SLA).where(
                    and_(
                        SLA.tenant_id == tenant_id,
                        SLA.id != sla_id,
                        SLA.is_default == True
                    )
                )
            ).scalars().all()
            for other_sla in other_slas:
                other_sla.is_default = False
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sla, field, value)
        
        sla.updated_by = user_id
        session.commit()
        session.refresh(sla)
        
        return sla
    
    async def list_slas(self, params: SLAListParams, tenant_id: str) -> Dict[str, Any]:
        """List SLAs with filters"""
        session = self.db.sync_session
        
        query = select(SLA).where(and_(SLA.tenant_id == tenant_id, SLA.is_deleted == False))
        
        if params.status:
            query = query.where(SLA.status == params.status)
        
        if params.priority:
            query = query.where(SLA.priority == params.priority)
        
        if params.category:
            query = query.where(SLA.category == params.category)
        
        # Get total
        total_result = session.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()
        
        # Apply ordering and pagination
        query = query.order_by(asc(SLA.display_order), asc(SLA.name))
        query = query.offset(params.skip).limit(params.limit)
        
        result = session.execute(query)
        slas = result.scalars().all()
        
        return {
            "slas": slas,
            "total": total,
            "page": (params.skip // params.limit) + 1,
            "page_size": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit
        }
    
    async def delete_sla(self, sla_id: str, tenant_id: str, user_id: str) -> bool:
        """Soft delete SLA"""
        session = self.db.sync_session
        sla = await self.get_sla(sla_id, tenant_id)
        
        if not sla:
            return False
        
        sla.is_deleted = True
        sla.updated_by = user_id
        session.commit()
        
        return True
    
    async def get_sla_violations(self, tenant_id: str, ticket_id: Optional[str] = None) -> List[SLAViolation]:
        """Get SLA violations"""
        session = self.db.sync_session
        
        query = select(SLAViolation).where(SLAViolation.tenant_id == tenant_id)
        
        if ticket_id:
            query = query.where(SLAViolation.ticket_id == ticket_id)
        
        query = query.order_by(desc(SLAViolation.violated_at))
        
        result = session.execute(query)
        return result.scalars().all()

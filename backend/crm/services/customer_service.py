"""
CRM Customer Service - Service Layer
Business logic for ticket management, knowledge base, and SLA tracking
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import re

from backend.shared.database.crm_customer_service_models import (
    Ticket, TicketComment, TicketAttachment, TicketActivity,
    SLAPolicy, KnowledgeBaseArticle, KnowledgeBaseFeedback,
    TicketTemplate, TicketStatus, TicketPriority, SLAStatus
)
from backend.crm.schemas.customer_service_schemas import (
    TicketCreate, TicketUpdate, TicketAssign, TicketResolve,
    TicketCommentCreate, SLAPolicyCreate, SLAPolicyUpdate,
    KnowledgeBaseCreate, KnowledgeBaseUpdate, TicketFilterParams
)


class CustomerServiceService:
    """Customer Service Business Logic"""

    # ==================== TICKET MANAGEMENT ====================

    @staticmethod
    def create_ticket(
        db: Session,
        ticket_data: TicketCreate,
        tenant_id: int,
        created_by_user_id: int
    ) -> Ticket:
        """Create a new support ticket"""
        
        # Generate ticket number
        ticket_number = CustomerServiceService._generate_ticket_number(db, tenant_id)
        
        # Get customer details
        from backend.shared.database.customer_models import Customer
        customer = db.query(Customer).filter(
            Customer.id == ticket_data.customer_id,
            Customer.tenant_id == tenant_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Find applicable SLA policy
        sla_policy = CustomerServiceService._find_applicable_sla(
            db, tenant_id, ticket_data.priority.value, 
            ticket_data.category.value, ticket_data.channel.value
        )
        
        # Calculate SLA due times
        sla_first_response_due = None
        sla_resolution_due = None
        
        if sla_policy:
            now = datetime.utcnow()
            sla_first_response_due = CustomerServiceService._calculate_sla_due_time(
                now, sla_policy.first_response_time, sla_policy
            )
            sla_resolution_due = CustomerServiceService._calculate_sla_due_time(
                now, sla_policy.resolution_time, sla_policy
            )
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            customer_id=ticket_data.customer_id,
            customer_name=customer.full_name,
            customer_email=customer.email,
            customer_phone=customer.phone,
            subject=ticket_data.subject,
            description=ticket_data.description,
            category=ticket_data.category,
            priority=ticket_data.priority,
            status=TicketStatus.NEW,
            channel=ticket_data.channel,
            assigned_to_user_id=ticket_data.assigned_to_user_id,
            assigned_to_team=ticket_data.assigned_to_team,
            tags=ticket_data.tags,
            related_entity_type=ticket_data.related_entity_type,
            related_entity_id=ticket_data.related_entity_id,
            sla_policy_id=sla_policy.id if sla_policy else None,
            sla_first_response_due=sla_first_response_due,
            sla_resolution_due=sla_resolution_due,
            tenant_id=tenant_id,
            branch_id=ticket_data.branch_id,
            created_by_user_id=created_by_user_id
        )
        
        db.add(ticket)
        db.flush()
        
        # Log activity
        CustomerServiceService._log_activity(
            db, ticket.id, "created", 
            f"Ticket created with priority {ticket_data.priority.value}",
            created_by_user_id
        )
        
        # Auto-assign if configured
        if ticket_data.assigned_to_user_id:
            ticket.assigned_at = datetime.utcnow()
            CustomerServiceService._log_activity(
                db, ticket.id, "assigned",
                f"Ticket assigned to user {ticket_data.assigned_to_user_id}",
                created_by_user_id
            )
        
        db.commit()
        db.refresh(ticket)
        
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: int, tenant_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        return db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False
        ).first()

    @staticmethod
    def get_ticket_by_number(db: Session, ticket_number: str, tenant_id: int) -> Optional[Ticket]:
        """Get ticket by ticket number"""
        return db.query(Ticket).filter(
            Ticket.ticket_number == ticket_number,
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False
        ).first()

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        ticket_data: TicketUpdate,
        updated_by_user_id: int
    ) -> Ticket:
        """Update ticket details"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Track changes for activity log
        changes = []
        
        update_data = ticket_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            old_value = getattr(ticket, field)
            if old_value != value:
                changes.append((field, old_value, value))
                setattr(ticket, field, value)
        
        if changes:
            ticket.updated_by_user_id = updated_by_user_id
            
            # Log changes
            for field, old_val, new_val in changes:
                CustomerServiceService._log_activity(
                    db, ticket.id, f"{field}_changed",
                    f"{field.replace('_', ' ').title()} changed",
                    updated_by_user_id, str(old_val), str(new_val)
                )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def assign_ticket(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        assign_data: TicketAssign,
        assigned_by_user_id: int
    ) -> Ticket:
        """Assign ticket to user or team"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.assigned_to_user_id = assign_data.assigned_to_user_id
        ticket.assigned_to_team = assign_data.assigned_to_team
        ticket.assigned_at = datetime.utcnow()
        
        if ticket.status == TicketStatus.NEW:
            ticket.status = TicketStatus.OPEN
        
        # Log activity
        assign_info = []
        if assign_data.assigned_to_user_id:
            assign_info.append(f"user {assign_data.assigned_to_user_id}")
        if assign_data.assigned_to_team:
            assign_info.append(f"team {assign_data.assigned_to_team}")
        
        CustomerServiceService._log_activity(
            db, ticket.id, "assigned",
            f"Ticket assigned to {' and '.join(assign_info)}",
            assigned_by_user_id
        )
        
        if assign_data.notes:
            CustomerServiceService._add_comment(
                db, ticket.id, assign_data.notes,
                assigned_by_user_id, is_internal=True
            )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def resolve_ticket(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        resolve_data: TicketResolve,
        resolved_by_user_id: int
    ) -> Ticket:
        """Mark ticket as resolved"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution = resolve_data.resolution
        ticket.resolved_at = datetime.utcnow()
        ticket.resolved_by_user_id = resolved_by_user_id
        
        # Update SLA
        if ticket.sla_first_response_due and not ticket.sla_first_response_at:
            ticket.sla_first_response_at = datetime.utcnow()
        
        CustomerServiceService._log_activity(
            db, ticket.id, "resolved",
            "Ticket marked as resolved",
            resolved_by_user_id
        )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def close_ticket(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        closed_by_user_id: int,
        closing_notes: Optional[str] = None
    ) -> Ticket:
        """Close a ticket"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        if ticket.status != TicketStatus.RESOLVED:
            raise ValueError("Only resolved tickets can be closed")
        
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.utcnow()
        ticket.closed_by_user_id = closed_by_user_id
        
        CustomerServiceService._log_activity(
            db, ticket.id, "closed",
            "Ticket closed",
            closed_by_user_id
        )
        
        if closing_notes:
            CustomerServiceService._add_comment(
                db, ticket.id, closing_notes,
                closed_by_user_id, is_internal=True
            )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def reopen_ticket(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        reason: str,
        reopened_by_user_id: int
    ) -> Ticket:
        """Reopen a closed ticket"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            raise ValueError("Only resolved or closed tickets can be reopened")
        
        ticket.status = TicketStatus.REOPENED
        ticket.resolved_at = None
        ticket.closed_at = None
        
        CustomerServiceService._log_activity(
            db, ticket.id, "reopened",
            f"Ticket reopened: {reason}",
            reopened_by_user_id
        )
        
        CustomerServiceService._add_comment(
            db, ticket.id, f"Ticket reopened. Reason: {reason}",
            reopened_by_user_id, is_internal=False
        )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def add_ticket_rating(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        rating: int,
        feedback: Optional[str] = None
    ) -> Ticket:
        """Add customer satisfaction rating to ticket"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.customer_satisfaction_rating = rating
        ticket.customer_feedback = feedback
        
        CustomerServiceService._log_activity(
            db, ticket.id, "rated",
            f"Customer rated ticket: {rating}/5",
            None
        )
        
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def list_tickets(
        db: Session,
        tenant_id: int,
        filters: TicketFilterParams
    ) -> Tuple[List[Ticket], int]:
        """List tickets with filtering and pagination"""
        query = db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False
        )
        
        # Apply filters
        if filters.status:
            query = query.filter(Ticket.status.in_(filters.status))
        
        if filters.priority:
            query = query.filter(Ticket.priority.in_(filters.priority))
        
        if filters.category:
            query = query.filter(Ticket.category.in_(filters.category))
        
        if filters.assigned_to_user_id:
            query = query.filter(Ticket.assigned_to_user_id == filters.assigned_to_user_id)
        
        if filters.customer_id:
            query = query.filter(Ticket.customer_id == filters.customer_id)
        
        if filters.channel:
            query = query.filter(Ticket.channel.in_(filters.channel))
        
        if filters.sla_status:
            query = query.filter(Ticket.sla_status.in_(filters.sla_status))
        
        if filters.from_date:
            query = query.filter(Ticket.created_at >= filters.from_date)
        
        if filters.to_date:
            query = query.filter(Ticket.created_at <= filters.to_date)
        
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    Ticket.ticket_number.ilike(search),
                    Ticket.subject.ilike(search),
                    Ticket.description.ilike(search),
                    Ticket.customer_name.ilike(search)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if filters.sort_order == "desc":
            query = query.order_by(desc(getattr(Ticket, filters.sort_by)))
        else:
            query = query.order_by(asc(getattr(Ticket, filters.sort_by)))
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        tickets = query.all()
        return tickets, total

    # ==================== TICKET COMMENTS ====================

    @staticmethod
    def add_comment(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        comment_data: TicketCommentCreate,
        user_id: int
    ) -> TicketComment:
        """Add comment to ticket"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        comment = CustomerServiceService._add_comment(
            db, ticket_id, comment_data.comment,
            user_id, comment_data.is_internal, comment_data.is_solution
        )
        
        # Update first response SLA if this is the first response
        if not ticket.sla_first_response_at and not comment_data.is_internal:
            ticket.sla_first_response_at = datetime.utcnow()
            CustomerServiceService._update_sla_status(db, ticket)
        
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def _add_comment(
        db: Session,
        ticket_id: int,
        comment_text: str,
        user_id: int,
        is_internal: bool = False,
        is_solution: bool = False
    ) -> TicketComment:
        """Internal method to add comment"""
        comment = TicketComment(
            ticket_id=ticket_id,
            comment=comment_text,
            is_internal=is_internal,
            is_solution=is_solution,
            created_by_user_id=user_id
        )
        db.add(comment)
        return comment

    @staticmethod
    def get_ticket_comments(
        db: Session,
        ticket_id: int,
        tenant_id: int,
        include_internal: bool = True
    ) -> List[TicketComment]:
        """Get all comments for a ticket"""
        ticket = CustomerServiceService.get_ticket(db, ticket_id, tenant_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        query = db.query(TicketComment).filter(TicketComment.ticket_id == ticket_id)
        
        if not include_internal:
            query = query.filter(TicketComment.is_internal == False)
        
        return query.order_by(TicketComment.created_at).all()

    # ==================== SLA MANAGEMENT ====================

    @staticmethod
    def create_sla_policy(
        db: Session,
        sla_data: SLAPolicyCreate,
        tenant_id: int,
        created_by_user_id: int
    ) -> SLAPolicy:
        """Create SLA policy"""
        sla_policy = SLAPolicy(
            **sla_data.model_dump(),
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id
        )
        
        db.add(sla_policy)
        db.commit()
        db.refresh(sla_policy)
        return sla_policy

    @staticmethod
    def update_sla_policy(
        db: Session,
        sla_id: int,
        tenant_id: int,
        sla_data: SLAPolicyUpdate
    ) -> SLAPolicy:
        """Update SLA policy"""
        sla_policy = db.query(SLAPolicy).filter(
            SLAPolicy.id == sla_id,
            SLAPolicy.tenant_id == tenant_id
        ).first()
        
        if not sla_policy:
            raise ValueError("SLA policy not found")
        
        update_data = sla_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sla_policy, field, value)
        
        db.commit()
        db.refresh(sla_policy)
        return sla_policy

    @staticmethod
    def get_sla_policies(
        db: Session,
        tenant_id: int,
        active_only: bool = True
    ) -> List[SLAPolicy]:
        """Get all SLA policies"""
        query = db.query(SLAPolicy).filter(SLAPolicy.tenant_id == tenant_id)
        
        if active_only:
            query = query.filter(SLAPolicy.is_active == True)
        
        return query.order_by(SLAPolicy.priority_order).all()

    @staticmethod
    def _find_applicable_sla(
        db: Session,
        tenant_id: int,
        priority: str,
        category: str,
        channel: str
    ) -> Optional[SLAPolicy]:
        """Find applicable SLA policy for ticket"""
        policies = db.query(SLAPolicy).filter(
            SLAPolicy.tenant_id == tenant_id,
            SLAPolicy.is_active == True
        ).order_by(SLAPolicy.priority_order).all()
        
        for policy in policies:
            # Check if policy applies
            priority_match = (not policy.applies_to_priority or 
                            priority in policy.applies_to_priority)
            category_match = (not policy.applies_to_category or 
                            category in policy.applies_to_category)
            channel_match = (not policy.applies_to_channel or 
                           channel in policy.applies_to_channel)
            
            if priority_match and category_match and channel_match:
                return policy
        
        return None

    @staticmethod
    def _calculate_sla_due_time(
        start_time: datetime,
        duration_minutes: int,
        sla_policy: SLAPolicy
    ) -> datetime:
        """Calculate SLA due time considering business hours"""
        if not sla_policy.business_hours_only:
            # Simple addition
            return start_time + timedelta(minutes=duration_minutes)
        
        # Calculate with business hours
        current_time = start_time
        remaining_minutes = duration_minutes
        
        while remaining_minutes > 0:
            # Check if current time is within business hours
            if (sla_policy.business_start_hour <= current_time.hour < sla_policy.business_end_hour and
                (sla_policy.include_weekends or current_time.weekday() < 5)):
                
                # Calculate minutes until end of business day
                end_of_day = current_time.replace(
                    hour=sla_policy.business_end_hour,
                    minute=0, second=0, microsecond=0
                )
                minutes_available = int((end_of_day - current_time).total_seconds() / 60)
                
                if remaining_minutes <= minutes_available:
                    return current_time + timedelta(minutes=remaining_minutes)
                else:
                    remaining_minutes -= minutes_available
                    current_time = end_of_day
            
            # Move to next business day start
            current_time = current_time + timedelta(days=1)
            current_time = current_time.replace(
                hour=sla_policy.business_start_hour,
                minute=0, second=0, microsecond=0
            )
            
            # Skip weekends if needed
            while not sla_policy.include_weekends and current_time.weekday() >= 5:
                current_time = current_time + timedelta(days=1)
        
        return current_time

    @staticmethod
    def _update_sla_status(db: Session, ticket: Ticket):
        """Update ticket SLA status"""
        if not ticket.sla_resolution_due:
            return
        
        now = datetime.utcnow()
        time_until_due = (ticket.sla_resolution_due - now).total_seconds() / 60
        
        if time_until_due < 0:
            ticket.sla_status = SLAStatus.BREACHED
        elif time_until_due < 60:  # Less than 1 hour
            ticket.sla_status = SLAStatus.APPROACHING_BREACH
        else:
            ticket.sla_status = SLAStatus.WITHIN_SLA

    @staticmethod
    def get_sla_metrics(db: Session, tenant_id: int, from_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get SLA compliance metrics"""
        query = db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False
        )
        
        if from_date:
            query = query.filter(Ticket.created_at >= from_date)
        
        tickets = query.all()
        
        total = len(tickets)
        within_sla = sum(1 for t in tickets if t.sla_status == SLAStatus.WITHIN_SLA)
        approaching = sum(1 for t in tickets if t.sla_status == SLAStatus.APPROACHING_BREACH)
        breached = sum(1 for t in tickets if t.sla_status == SLAStatus.BREACHED)
        
        # Calculate average response/resolution times
        first_response_times = [
            (t.sla_first_response_at - t.created_at).total_seconds() / 60
            for t in tickets if t.sla_first_response_at
        ]
        resolution_times = [
            (t.resolved_at - t.created_at).total_seconds() / 60
            for t in tickets if t.resolved_at
        ]
        
        return {
            "total_tickets": total,
            "within_sla": within_sla,
            "approaching_breach": approaching,
            "breached": breached,
            "average_first_response_time": sum(first_response_times) / len(first_response_times) if first_response_times else 0,
            "average_resolution_time": sum(resolution_times) / len(resolution_times) if resolution_times else 0,
            "sla_compliance_rate": (within_sla / total * 100) if total > 0 else 0
        }

    # ==================== KNOWLEDGE BASE ====================

    @staticmethod
    def create_article(
        db: Session,
        article_data: KnowledgeBaseCreate,
        tenant_id: int,
        created_by_user_id: int
    ) -> KnowledgeBaseArticle:
        """Create knowledge base article"""
        
        # Generate article number and slug
        article_number = CustomerServiceService._generate_article_number(db, tenant_id)
        slug = CustomerServiceService._generate_slug(article_data.title)
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.slug == slug,
            KnowledgeBaseArticle.tenant_id == tenant_id
        ).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        article = KnowledgeBaseArticle(
            article_number=article_number,
            slug=slug,
            title=article_data.title,
            summary=article_data.summary,
            content=article_data.content,
            category=article_data.category,
            keywords=article_data.keywords,
            tags=article_data.tags,
            is_public=article_data.is_public,
            is_internal=article_data.is_internal,
            related_articles=article_data.related_articles,
            meta_description=article_data.meta_description,
            meta_keywords=article_data.meta_keywords,
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def update_article(
        db: Session,
        article_id: int,
        tenant_id: int,
        article_data: KnowledgeBaseUpdate,
        updated_by_user_id: int
    ) -> KnowledgeBaseArticle:
        """Update knowledge base article"""
        article = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.tenant_id == tenant_id,
            KnowledgeBaseArticle.is_deleted == False
        ).first()
        
        if not article:
            raise ValueError("Article not found")
        
        update_data = article_data.model_dump(exclude_unset=True)
        
        # Update slug if title changed
        if "title" in update_data:
            new_slug = CustomerServiceService._generate_slug(update_data["title"])
            if new_slug != article.slug:
                # Ensure unique
                base_slug = new_slug
                counter = 1
                while db.query(KnowledgeBaseArticle).filter(
                    KnowledgeBaseArticle.slug == new_slug,
                    KnowledgeBaseArticle.tenant_id == tenant_id,
                    KnowledgeBaseArticle.id != article_id
                ).first():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                update_data["slug"] = new_slug
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_by_user_id = updated_by_user_id
        
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def publish_article(
        db: Session,
        article_id: int,
        tenant_id: int,
        published_by_user_id: int
    ) -> KnowledgeBaseArticle:
        """Publish knowledge base article"""
        article = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.tenant_id == tenant_id,
            KnowledgeBaseArticle.is_deleted == False
        ).first()
        
        if not article:
            raise ValueError("Article not found")
        
        from backend.shared.database.crm_customer_service_models import KnowledgeBaseStatus
        article.status = KnowledgeBaseStatus.PUBLISHED
        article.published_at = datetime.utcnow()
        article.published_by_user_id = published_by_user_id
        
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def search_articles(
        db: Session,
        tenant_id: int,
        search_query: str,
        category: Optional[str] = None,
        public_only: bool = False
    ) -> List[KnowledgeBaseArticle]:
        """Search knowledge base articles"""
        from backend.shared.database.crm_customer_service_models import KnowledgeBaseStatus
        
        query = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.tenant_id == tenant_id,
            KnowledgeBaseArticle.is_deleted == False,
            KnowledgeBaseArticle.status == KnowledgeBaseStatus.PUBLISHED
        )
        
        if public_only:
            query = query.filter(KnowledgeBaseArticle.is_public == True)
        
        if category:
            query = query.filter(KnowledgeBaseArticle.category == category)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                or_(
                    KnowledgeBaseArticle.title.ilike(search),
                    KnowledgeBaseArticle.summary.ilike(search),
                    KnowledgeBaseArticle.content.ilike(search),
                    KnowledgeBaseArticle.keywords.cast(String).ilike(search)
                )
            )
        
        return query.order_by(desc(KnowledgeBaseArticle.view_count)).limit(20).all()

    @staticmethod
    def increment_article_view(db: Session, article_id: int, tenant_id: int):
        """Increment article view count"""
        article = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.tenant_id == tenant_id
        ).first()
        
        if article:
            article.view_count = (article.view_count or 0) + 1
            db.commit()

    @staticmethod
    def add_article_feedback(
        db: Session,
        article_id: int,
        tenant_id: int,
        is_helpful: bool,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        user_id: Optional[int] = None,
        customer_id: Optional[int] = None
    ) -> KnowledgeBaseFeedback:
        """Add feedback to knowledge base article"""
        article = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.tenant_id == tenant_id
        ).first()
        
        if not article:
            raise ValueError("Article not found")
        
        feedback = KnowledgeBaseFeedback(
            article_id=article_id,
            is_helpful=is_helpful,
            rating=rating,
            comment=comment,
            user_id=user_id,
            customer_id=customer_id
        )
        
        db.add(feedback)
        
        # Update article metrics
        if is_helpful:
            article.helpful_count = (article.helpful_count or 0) + 1
        else:
            article.not_helpful_count = (article.not_helpful_count or 0) + 1
        
        if rating:
            # Recalculate average rating
            feedbacks = db.query(KnowledgeBaseFeedback).filter(
                KnowledgeBaseFeedback.article_id == article_id,
                KnowledgeBaseFeedback.rating.isnot(None)
            ).all()
            ratings = [f.rating for f in feedbacks] + [rating]
            article.average_rating = sum(ratings) / len(ratings)
        
        db.commit()
        db.refresh(feedback)
        return feedback

    # ==================== UTILITY METHODS ====================

    @staticmethod
    def _generate_ticket_number(db: Session, tenant_id: int) -> str:
        """Generate unique ticket number"""
        from datetime import datetime
        
        # Format: TKT-YYYYMMDD-XXXX
        today = datetime.utcnow()
        prefix = f"TKT-{today.strftime('%Y%m%d')}"
        
        # Get last ticket number for today
        last_ticket = db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.ticket_number.like(f"{prefix}%")
        ).order_by(desc(Ticket.ticket_number)).first()
        
        if last_ticket:
            last_num = int(last_ticket.ticket_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}-{new_num:04d}"

    @staticmethod
    def _generate_article_number(db: Session, tenant_id: int) -> str:
        """Generate unique article number"""
        # Format: KB-XXXXX
        last_article = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.tenant_id == tenant_id
        ).order_by(desc(KnowledgeBaseArticle.id)).first()
        
        if last_article:
            last_num = int(last_article.article_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"KB-{new_num:05d}"

    @staticmethod
    def _generate_slug(title: str) -> str:
        """Generate URL-friendly slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')[:100]

    @staticmethod
    def _log_activity(
        db: Session,
        ticket_id: int,
        activity_type: str,
        description: str,
        user_id: Optional[int] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ):
        """Log ticket activity"""
        activity = TicketActivity(
            ticket_id=ticket_id,
            activity_type=activity_type,
            description=description,
            old_value=old_value,
            new_value=new_value,
            created_by_user_id=user_id
        )
        db.add(activity)

    @staticmethod
    def get_ticket_statistics(
        db: Session,
        tenant_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get ticket statistics"""
        query = db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False
        )
        
        if from_date:
            query = query.filter(Ticket.created_at >= from_date)
        if to_date:
            query = query.filter(Ticket.created_at <= to_date)
        
        tickets = query.all()
        
        total = len(tickets)
        new = sum(1 for t in tickets if t.status == TicketStatus.NEW)
        open_tickets = sum(1 for t in tickets if t.status == TicketStatus.OPEN)
        in_progress = sum(1 for t in tickets if t.status == TicketStatus.IN_PROGRESS)
        resolved = sum(1 for t in tickets if t.status == TicketStatus.RESOLVED)
        closed = sum(1 for t in tickets if t.status == TicketStatus.CLOSED)
        
        # Calculate average resolution time
        resolution_times = [
            (t.resolved_at - t.created_at).total_seconds() / 3600
            for t in tickets if t.resolved_at
        ]
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Calculate customer satisfaction
        ratings = [t.customer_satisfaction_rating for t in tickets if t.customer_satisfaction_rating]
        avg_satisfaction = sum(ratings) / len(ratings) if ratings else None
        
        return {
            "total_tickets": total,
            "new_tickets": new,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress,
            "resolved_tickets": resolved,
            "closed_tickets": closed,
            "average_resolution_time": avg_resolution,
            "customer_satisfaction_avg": avg_satisfaction
        }

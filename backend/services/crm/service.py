"""
CRM Lead Management Service
Business logic for lead capture, scoring, assignment, and follow-up tracking
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, case, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import re

from backend.shared.database.crm_lead_models import (
    Lead, LeadFollowUp, LeadActivity, LeadScoringRule, LeadAssignmentRule,
    LeadSource, LeadStatus, LeadPriority, LeadTemperature,
    FollowUpStatus, FollowUpType
)
from .schemas import (
    LeadCreate, LeadUpdate, LeadFilters, LeadResponse, LeadListItem,
    LeadFollowUpCreate, LeadFollowUpUpdate, LeadFollowUpComplete,
    LeadActivityCreate, LeadAssignRequest, LeadQualifyRequest,
    LeadConvertRequest, LeadLostRequest, BulkLeadAssignRequest,
    LeadDashboardStats, PaginatedLeadResponse, PaginatedFollowUpResponse
)


class CRMLeadService:
    """CRM Lead Management Service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # LEAD CAPTURE (Multi-Channel)
    # ========================================================================
    
    def create_lead(
        self,
        lead_data: LeadCreate,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Lead:
        """
        Create new lead from any channel
        Auto-generates lead code, checks duplicates, scores, and assigns
        """
        # Generate full name
        full_name = f"{lead_data.first_name} {lead_data.last_name or ''}".strip()
        
        # Generate unique lead code
        lead_code = self._generate_lead_code()
        
        # Check for duplicates
        duplicate_lead = self._check_duplicate(lead_data.mobile, lead_data.email)
        
        # Create lead object
        lead = Lead(
            **lead_data.dict(),
            lead_code=lead_code,
            full_name=full_name,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        if duplicate_lead:
            lead.is_duplicate = True
            lead.duplicate_of_lead_id = duplicate_lead.id
            lead.status = LeadStatus.DUPLICATE
        
        self.db.add(lead)
        self.db.flush()  # Get ID
        
        # Auto-score lead
        self._calculate_lead_score(lead)
        
        # Auto-assign lead
        if not duplicate_lead:
            self._auto_assign_lead(lead)
        
        # Log activity
        self._log_activity(
            lead_id=lead.id,
            activity_type="lead_created",
            activity_title=f"Lead created from {lead_data.source.value}",
            user_id=user_id,
            is_system=True
        )
        
        self.db.commit()
        self.db.refresh(lead)
        
        return lead

    
    def get_lead(self, lead_id: int, tenant_id: Optional[int] = None) -> Optional[Lead]:
        """Get lead by ID"""
        query = self.db.query(Lead).filter(Lead.id == lead_id)
        if tenant_id:
            query = query.filter(Lead.tenant_id == tenant_id)
        return query.first()
    
    def get_lead_by_code(self, lead_code: str, tenant_id: Optional[int] = None) -> Optional[Lead]:
        """Get lead by code"""
        query = self.db.query(Lead).filter(Lead.lead_code == lead_code)
        if tenant_id:
            query = query.filter(Lead.tenant_id == tenant_id)
        return query.first()
    
    def update_lead(
        self,
        lead_id: int,
        lead_data: LeadUpdate,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[Lead]:
        """Update lead details"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        # Track changes for activity log
        changes = {}
        update_data = lead_data.dict(exclude_unset=True)
        
        for field, new_value in update_data.items():
            old_value = getattr(lead, field, None)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                setattr(lead, field, new_value)
        
        # Update full name if name changed
        if "first_name" in update_data or "last_name" in update_data:
            lead.full_name = f"{lead.first_name} {lead.last_name or ''}".strip()
        
        # Recalculate score if relevant fields changed
        if any(f in update_data for f in ["monthly_income", "loan_amount_required", "occupation"]):
            self._calculate_lead_score(lead)

        
        # Log changes
        if changes:
            for field, change in changes.items():
                self._log_activity(
                    lead_id=lead.id,
                    activity_type="lead_updated",
                    activity_title=f"Lead {field} updated",
                    user_id=user_id,
                    old_value={"value": str(change["old"])},
                    new_value={"value": str(change["new"])}
                )
        
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def list_leads(
        self,
        filters: LeadFilters,
        tenant_id: Optional[int] = None
    ) -> Tuple[List[Lead], int]:
        """List leads with filters and pagination"""
        query = self.db.query(Lead).filter(Lead.is_deleted == False)
        
        if tenant_id:
            query = query.filter(Lead.tenant_id == tenant_id)
        
        # Apply filters
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Lead.full_name.ilike(search_term),
                    Lead.mobile.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.lead_code.ilike(search_term)
                )
            )
        
        if filters.source:
            query = query.filter(Lead.source == filters.source)
        
        if filters.status:
            query = query.filter(Lead.status == filters.status)

        
        if filters.priority:
            query = query.filter(Lead.priority == filters.priority)
        
        if filters.temperature:
            query = query.filter(Lead.lead_temperature == filters.temperature)
        
        if filters.assigned_to_user_id:
            query = query.filter(Lead.assigned_to_user_id == filters.assigned_to_user_id)
        
        if filters.is_qualified is not None:
            query = query.filter(Lead.is_qualified == filters.is_qualified)
        
        if filters.min_score:
            query = query.filter(Lead.lead_score >= filters.min_score)
        
        if filters.max_score:
            query = query.filter(Lead.lead_score <= filters.max_score)
        
        if filters.created_from:
            query = query.filter(Lead.created_at >= filters.created_from)
        
        if filters.created_to:
            query = query.filter(Lead.created_at <= filters.created_to)
        
        if filters.next_follow_up_from:
            query = query.filter(Lead.next_follow_up_date >= filters.next_follow_up_from)
        
        if filters.next_follow_up_to:
            query = query.filter(Lead.next_follow_up_date <= filters.next_follow_up_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Lead.created_at))
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
        
        leads = query.all()
        return leads, total

    
    # ========================================================================
    # LEAD SCORING
    # ========================================================================
    
    def _calculate_lead_score(self, lead: Lead) -> int:
        """
        Calculate lead score based on scoring rules
        Returns the calculated score
        """
        total_score = 0
        score_breakdown = {}
        
        # Get active scoring rules
        rules = self.db.query(LeadScoringRule).filter(
            LeadScoringRule.is_active == True,
            LeadScoringRule.tenant_id == lead.tenant_id
        ).order_by(LeadScoringRule.priority).all()
        
        for rule in rules:
            points = self._evaluate_scoring_rule(lead, rule)
            if points != 0:
                total_score += points
                score_breakdown[rule.rule_name] = points
                
                # Update rule execution
                rule.execution_count += 1
                rule.last_executed_date = datetime.utcnow()
        
        # Apply default scoring if no rules
        if not rules:
            total_score = self._default_lead_scoring(lead, score_breakdown)
        
        # Update lead score
        lead.lead_score = max(0, min(100, total_score))  # Cap between 0-100
        lead.score_breakdown = score_breakdown
        
        # Update temperature based on score
        if lead.lead_score >= 70:
            lead.lead_temperature = LeadTemperature.HOT
        elif lead.lead_score >= 40:
            lead.lead_temperature = LeadTemperature.WARM
        else:
            lead.lead_temperature = LeadTemperature.COLD

        
        return lead.lead_score
    
    def _evaluate_scoring_rule(self, lead: Lead, rule: LeadScoringRule) -> int:
        """Evaluate a single scoring rule against a lead"""
        field_value = getattr(lead, rule.field_name, None)
        rule_value = rule.field_value
        
        if field_value is None:
            return 0
        
        # Evaluate based on operator
        matched = False
        
        if rule.operator == "equals":
            matched = str(field_value) == str(rule_value)
        elif rule.operator == "not_equals":
            matched = str(field_value) != str(rule_value)
        elif rule.operator == "greater_than":
            matched = float(field_value) > float(rule_value)
        elif rule.operator == "less_than":
            matched = float(field_value) < float(rule_value)
        elif rule.operator == "contains":
            matched = str(rule_value).lower() in str(field_value).lower()
        elif rule.operator == "not_contains":
            matched = str(rule_value).lower() not in str(field_value).lower()
        elif rule.operator == "is_empty":
            matched = not field_value
        elif rule.operator == "is_not_empty":
            matched = bool(field_value)
        
        return rule.score_points if matched else 0
    
    def _default_lead_scoring(self, lead: Lead, breakdown: Dict) -> int:
        """Default scoring logic when no rules are configured"""
        score = 0
        
        # Income-based scoring
        if lead.monthly_income:
            if lead.monthly_income >= 100000:
                score += 20
                breakdown["high_income"] = 20
            elif lead.monthly_income >= 50000:
                score += 15
                breakdown["medium_income"] = 15
            elif lead.monthly_income >= 25000:
                score += 10
                breakdown["basic_income"] = 10

        
        # Loan amount scoring
        if lead.loan_amount_required:
            if lead.loan_amount_required >= 1000000:
                score += 15
                breakdown["large_loan"] = 15
            elif lead.loan_amount_required >= 500000:
                score += 10
                breakdown["medium_loan"] = 10
        
        # Occupation scoring
        if lead.occupation:
            occupation_lower = lead.occupation.lower()
            if any(word in occupation_lower for word in ["doctor", "engineer", "manager", "director"]):
                score += 15
                breakdown["professional"] = 15
            elif "business" in occupation_lower or "self" in occupation_lower:
                score += 10
                breakdown["business_owner"] = 10
        
        # Contact completeness
        if lead.email:
            score += 5
            breakdown["email_provided"] = 5
        
        if lead.company_name:
            score += 5
            breakdown["company_provided"] = 5
        
        # Source quality
        if lead.source in [LeadSource.REFERRAL, LeadSource.PARTNER]:
            score += 10
            breakdown["quality_source"] = 10
        elif lead.source == LeadSource.WEBSITE:
            score += 5
            breakdown["website_source"] = 5
        
        return score

    
    def recalculate_lead_score(self, lead_id: int, tenant_id: Optional[int] = None) -> Optional[Lead]:
        """Manually recalculate lead score"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        old_score = lead.lead_score
        new_score = self._calculate_lead_score(lead)
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="score_recalculated",
            activity_title="Lead score recalculated",
            old_value={"score": old_score},
            new_value={"score": new_score},
            is_system=True
        )
        
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    # ========================================================================
    # LEAD ASSIGNMENT & ROUTING
    # ========================================================================
    
    def assign_lead(
        self,
        lead_id: int,
        request: LeadAssignRequest,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[Lead]:
        """Manually assign lead to user"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        old_user_id = lead.assigned_to_user_id
        
        lead.assigned_to_user_id = request.user_id
        lead.assigned_date = datetime.utcnow()
        lead.auto_assigned = False

        
        # Get user name for activity log
        from backend.shared.database.models import User
        assigned_user = self.db.query(User).filter(User.id == request.user_id).first()
        user_name = assigned_user.full_name if assigned_user else f"User {request.user_id}"
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="lead_assigned",
            activity_title=f"Lead assigned to {user_name}",
            activity_description=request.notes,
            user_id=user_id,
            old_value={"user_id": old_user_id},
            new_value={"user_id": request.user_id}
        )
        
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def _auto_assign_lead(self, lead: Lead) -> bool:
        """Auto-assign lead based on assignment rules"""
        # Get active assignment rules
        rules = self.db.query(LeadAssignmentRule).filter(
            LeadAssignmentRule.is_active == True,
            LeadAssignmentRule.tenant_id == lead.tenant_id
        ).order_by(LeadAssignmentRule.priority).all()
        
        for rule in rules:
            if self._evaluate_assignment_rule(lead, rule):
                # Assign based on strategy
                assigned_user_id = self._execute_assignment_strategy(lead, rule)
                
                if assigned_user_id:
                    lead.assigned_to_user_id = assigned_user_id
                    lead.assigned_date = datetime.utcnow()
                    lead.auto_assigned = True
                    lead.assignment_rules_applied = {
                        "rule_id": rule.id,
                        "rule_name": rule.rule_name
                    }
                    
                    # Update rule stats
                    rule.execution_count += 1
                    rule.success_count += 1
                    rule.last_executed_date = datetime.utcnow()

                    
                    self._log_activity(
                        lead_id=lead.id,
                        activity_type="auto_assigned",
                        activity_title=f"Auto-assigned by rule: {rule.rule_name}",
                        is_system=True
                    )
                    
                    return True
                else:
                    rule.execution_count += 1
                    rule.failure_count += 1
        
        return False
    
    def _evaluate_assignment_rule(self, lead: Lead, rule: LeadAssignmentRule) -> bool:
        """Evaluate if lead matches assignment rule conditions"""
        conditions = rule.conditions
        
        # Simple condition evaluation
        for field, condition_value in conditions.items():
            lead_value = getattr(lead, field, None)
            
            if isinstance(condition_value, list):
                if lead_value not in condition_value:
                    return False
            elif lead_value != condition_value:
                return False
        
        return True
    
    def _execute_assignment_strategy(self, lead: Lead, rule: LeadAssignmentRule) -> Optional[int]:
        """Execute assignment strategy and return user ID"""
        from backend.shared.database.models import User
        
        if rule.assignment_type == "manual":
            return rule.assign_to_user_id
        
        elif rule.assignment_type == "round_robin":
            # Get team users or branch users
            query = self.db.query(User).filter(User.is_active == True)
            
            if rule.assign_to_branch_id:
                query = query.filter(User.branch_id == rule.assign_to_branch_id)
            
            users = query.all()
            
            if not users:
                return None
            
            # Simple round robin - assign to user with least leads
            user_lead_counts = []
            for user in users:
                count = self.db.query(Lead).filter(
                    Lead.assigned_to_user_id == user.id,
                    Lead.is_active == True
                ).count()
                user_lead_counts.append((user.id, count))

            
            # Sort by count and return user with least leads
            user_lead_counts.sort(key=lambda x: x[1])
            return user_lead_counts[0][0]
        
        elif rule.assignment_type == "load_balanced":
            # Similar to round robin but considers max_leads_per_user
            query = self.db.query(User).filter(User.is_active == True)
            
            if rule.assign_to_branch_id:
                query = query.filter(User.branch_id == rule.assign_to_branch_id)
            
            users = query.all()
            
            for user in users:
                current_leads = self.db.query(Lead).filter(
                    Lead.assigned_to_user_id == user.id,
                    Lead.is_active == True
                ).count()
                
                if rule.max_leads_per_user and current_leads >= rule.max_leads_per_user:
                    continue
                
                return user.id
            
            return None
        
        return rule.assign_to_user_id
    
    def bulk_assign_leads(
        self,
        request: BulkLeadAssignRequest,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Bulk assign multiple leads"""
        success_count = 0
        failed_leads = []
        
        for lead_id in request.lead_ids:
            lead = self.get_lead(lead_id, tenant_id)
            if lead:
                lead.assigned_to_user_id = request.user_id
                lead.assigned_date = datetime.utcnow()
                lead.auto_assigned = False
                
                self._log_activity(
                    lead_id=lead.id,
                    activity_type="bulk_assigned",
                    activity_title="Lead bulk assigned",
                    activity_description=request.notes,
                    user_id=user_id
                )
                success_count += 1
            else:
                failed_leads.append(lead_id)

        
        self.db.commit()
        
        return {
            "success": True,
            "assigned_count": success_count,
            "failed_count": len(failed_leads),
            "failed_lead_ids": failed_leads
        }
    
    # ========================================================================
    # FOLLOW-UP TRACKING
    # ========================================================================
    
    def create_follow_up(
        self,
        follow_up_data: LeadFollowUpCreate,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[LeadFollowUp]:
        """Create follow-up activity"""
        lead = self.get_lead(follow_up_data.lead_id, tenant_id)
        if not lead:
            return None
        
        # Use assigned user if not specified
        assigned_user = follow_up_data.assigned_to_user_id or lead.assigned_to_user_id or user_id
        
        follow_up = LeadFollowUp(
            **follow_up_data.dict(),
            assigned_to_user_id=assigned_user,
            tenant_id=tenant_id,
            status=FollowUpStatus.PENDING
        )
        
        self.db.add(follow_up)
        
        # Update lead's next follow-up date
        if not lead.next_follow_up_date or follow_up.scheduled_date < lead.next_follow_up_date:
            lead.next_follow_up_date = follow_up.scheduled_date
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="follow_up_scheduled",
            activity_title=f"Follow-up scheduled: {follow_up.subject}",
            user_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(follow_up)
        return follow_up

    
    def complete_follow_up(
        self,
        follow_up_id: int,
        completion_data: LeadFollowUpComplete,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[LeadFollowUp]:
        """Complete a follow-up activity"""
        follow_up = self.db.query(LeadFollowUp).filter(
            LeadFollowUp.id == follow_up_id
        ).first()
        
        if not follow_up or (tenant_id and follow_up.tenant_id != tenant_id):
            return None
        
        follow_up.status = FollowUpStatus.COMPLETED
        follow_up.completed_date = datetime.utcnow()
        follow_up.completed_by_user_id = user_id
        follow_up.outcome = completion_data.outcome
        follow_up.next_action = completion_data.next_action
        follow_up.customer_interested = completion_data.customer_interested
        follow_up.customer_response = completion_data.customer_response
        follow_up.duration_minutes = completion_data.duration_minutes
        
        # Update lead
        lead = follow_up.lead
        lead.last_contacted_date = datetime.utcnow()
        lead.follow_up_count += 1
        
        # Update response time for first contact
        if lead.follow_up_count == 1 and lead.created_at:
            hours_diff = (datetime.utcnow() - lead.created_at).total_seconds() / 3600
            lead.response_time_hours = int(hours_diff)
        
        # Update next follow-up date
        self._update_next_follow_up_date(lead)
        
        # Update lead status based on interest
        if completion_data.customer_interested is True:
            if lead.status == LeadStatus.NEW:
                lead.status = LeadStatus.CONTACTED
        elif completion_data.customer_interested is False:
            lead.status = LeadStatus.UNQUALIFIED
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="follow_up_completed",
            activity_title=f"Follow-up completed: {follow_up.subject}",
            activity_description=completion_data.outcome,
            user_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(follow_up)
        return follow_up

    
    def get_lead_follow_ups(
        self,
        lead_id: int,
        page: int = 1,
        page_size: int = 20,
        tenant_id: Optional[int] = None
    ) -> Tuple[List[LeadFollowUp], int]:
        """Get all follow-ups for a lead"""
        query = self.db.query(LeadFollowUp).filter(LeadFollowUp.lead_id == lead_id)
        
        if tenant_id:
            query = query.filter(LeadFollowUp.tenant_id == tenant_id)
        
        total = query.count()
        
        follow_ups = query.order_by(desc(LeadFollowUp.scheduled_date))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return follow_ups, total
    
    def get_overdue_follow_ups(
        self,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> List[LeadFollowUp]:
        """Get overdue follow-ups"""
        query = self.db.query(LeadFollowUp).filter(
            LeadFollowUp.status == FollowUpStatus.PENDING,
            LeadFollowUp.scheduled_date < datetime.utcnow()
        )
        
        if tenant_id:
            query = query.filter(LeadFollowUp.tenant_id == tenant_id)
        
        if user_id:
            query = query.filter(LeadFollowUp.assigned_to_user_id == user_id)
        
        # Update status to overdue
        overdue = query.all()
        for follow_up in overdue:
            follow_up.status = FollowUpStatus.OVERDUE
        
        self.db.commit()
        return overdue
    
    def _update_next_follow_up_date(self, lead: Lead):
        """Update lead's next follow-up date"""
        next_follow_up = self.db.query(LeadFollowUp).filter(
            LeadFollowUp.lead_id == lead.id,
            LeadFollowUp.status == FollowUpStatus.PENDING,
            LeadFollowUp.scheduled_date > datetime.utcnow()
        ).order_by(LeadFollowUp.scheduled_date).first()
        
        lead.next_follow_up_date = next_follow_up.scheduled_date if next_follow_up else None

    
    # ========================================================================
    # LEAD ACTIONS
    # ========================================================================
    
    def qualify_lead(
        self,
        lead_id: int,
        request: LeadQualifyRequest,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[Lead]:
        """Qualify or disqualify a lead"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        old_qualified = lead.is_qualified
        lead.is_qualified = request.is_qualified
        lead.qualification_reason = request.reason
        
        if request.is_qualified:
            lead.status = LeadStatus.QUALIFIED
            lead.priority = LeadPriority.HIGH
        else:
            lead.status = LeadStatus.UNQUALIFIED
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="lead_qualified" if request.is_qualified else "lead_disqualified",
            activity_title=f"Lead {'qualified' if request.is_qualified else 'disqualified'}",
            activity_description=request.reason,
            user_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def convert_lead(
        self,
        lead_id: int,
        request: LeadConvertRequest,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Convert lead to customer"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        result = {"lead_id": lead_id}
        
        # Create customer if requested
        if request.create_customer:
            from backend.shared.database.models import Customer
            
            customer = Customer(
                first_name=lead.first_name,
                last_name=lead.last_name,
                email=lead.email,
                mobile=lead.mobile,
                city_id=lead.city_id,
                state_id=lead.state_id,
                pincode=lead.pincode,
                occupation=lead.occupation,
                company_name=lead.company_name,
                monthly_income=lead.monthly_income,
                tenant_id=tenant_id,
                created_by_user_id=user_id
            )
            
            self.db.add(customer)
            self.db.flush()
            
            lead.converted_to_customer_id = customer.id
            result["customer_id"] = customer.id

        
        # Update lead status
        lead.is_converted = True
        lead.converted_date = datetime.utcnow()
        lead.status = LeadStatus.CONVERTED
        
        # Calculate conversion time
        if lead.created_at:
            hours_diff = (datetime.utcnow() - lead.created_at).total_seconds() / 3600
            lead.conversion_time_hours = int(hours_diff)
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="lead_converted",
            activity_title="Lead converted to customer",
            activity_description=request.notes,
            user_id=user_id
        )
        
        self.db.commit()
        return result
    
    def mark_lead_lost(
        self,
        lead_id: int,
        request: LeadLostRequest,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> Optional[Lead]:
        """Mark lead as lost"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return None
        
        lead.is_lost = True
        lead.lost_date = datetime.utcnow()
        lead.lost_reason = request.reason
        lead.lost_remarks = request.remarks
        lead.status = LeadStatus.LOST
        
        self._log_activity(
            lead_id=lead.id,
            activity_type="lead_lost",
            activity_title="Lead marked as lost",
            activity_description=f"{request.reason} - {request.remarks or ''}",
            user_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(lead)
        return lead

    
    # ========================================================================
    # DASHBOARD & ANALYTICS
    # ========================================================================
    
    def get_dashboard_stats(
        self,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> LeadDashboardStats:
        """Get lead dashboard statistics"""
        base_query = self.db.query(Lead).filter(Lead.is_deleted == False)
        
        if tenant_id:
            base_query = base_query.filter(Lead.tenant_id == tenant_id)
        
        if user_id:
            base_query = base_query.filter(Lead.assigned_to_user_id == user_id)
        
        # Count by status
        total_leads = base_query.count()
        new_leads = base_query.filter(Lead.status == LeadStatus.NEW).count()
        contacted_leads = base_query.filter(Lead.status == LeadStatus.CONTACTED).count()
        qualified_leads = base_query.filter(Lead.is_qualified == True).count()
        converted_leads = base_query.filter(Lead.is_converted == True).count()
        lost_leads = base_query.filter(Lead.is_lost == True).count()
        hot_leads = base_query.filter(Lead.lead_temperature == LeadTemperature.HOT).count()
        
        # Average score
        avg_score_result = base_query.with_entities(
            func.avg(Lead.lead_score)
        ).scalar()
        avg_score = float(avg_score_result) if avg_score_result else 0.0
        
        # Conversion rate
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0.0
        
        # Average conversion time
        avg_conversion_time = base_query.filter(
            Lead.is_converted == True,
            Lead.conversion_time_hours.isnot(None)
        ).with_entities(func.avg(Lead.conversion_time_hours)).scalar()
        
        # Overdue follow-ups
        overdue_follow_ups = self.db.query(LeadFollowUp).filter(
            LeadFollowUp.status == FollowUpStatus.PENDING,
            LeadFollowUp.scheduled_date < datetime.utcnow()
        )
        if tenant_id:
            overdue_follow_ups = overdue_follow_ups.filter(LeadFollowUp.tenant_id == tenant_id)
        if user_id:
            overdue_follow_ups = overdue_follow_ups.filter(LeadFollowUp.assigned_to_user_id == user_id)
        overdue_count = overdue_follow_ups.count()

        
        # Today's follow-ups
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_follow_ups = self.db.query(LeadFollowUp).filter(
            LeadFollowUp.status == FollowUpStatus.PENDING,
            LeadFollowUp.scheduled_date >= today_start,
            LeadFollowUp.scheduled_date < today_end
        )
        if tenant_id:
            today_follow_ups = today_follow_ups.filter(LeadFollowUp.tenant_id == tenant_id)
        if user_id:
            today_follow_ups = today_follow_ups.filter(LeadFollowUp.assigned_to_user_id == user_id)
        today_count = today_follow_ups.count()
        
        return LeadDashboardStats(
            total_leads=total_leads,
            new_leads=new_leads,
            contacted_leads=contacted_leads,
            qualified_leads=qualified_leads,
            converted_leads=converted_leads,
            lost_leads=lost_leads,
            hot_leads=hot_leads,
            overdue_follow_ups=overdue_count,
            avg_lead_score=round(avg_score, 2),
            avg_conversion_time_hours=float(avg_conversion_time) if avg_conversion_time else None,
            conversion_rate=round(conversion_rate, 2),
            today_follow_ups=today_count
        )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _generate_lead_code(self) -> str:
        """Generate unique lead code"""
        from datetime import datetime
        
        # Format: LD-YYMMDD-XXXX
        date_part = datetime.utcnow().strftime("%y%m%d")
        
        # Get today's count
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        count = self.db.query(Lead).filter(
            Lead.created_at >= today_start
        ).count() + 1
        
        return f"LD-{date_part}-{count:04d}"

    
    def _check_duplicate(self, mobile: str, email: Optional[str] = None) -> Optional[Lead]:
        """Check for duplicate leads"""
        query = self.db.query(Lead).filter(
            Lead.is_deleted == False,
            Lead.mobile == mobile
        )
        
        # Also check email if provided
        if email:
            query = query.filter(
                or_(
                    Lead.mobile == mobile,
                    Lead.email == email
                )
            )
        
        return query.first()
    
    def _log_activity(
        self,
        lead_id: int,
        activity_type: str,
        activity_title: str,
        activity_description: Optional[str] = None,
        user_id: Optional[int] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        is_system: bool = False
    ):
        """Log lead activity"""
        from backend.shared.database.models import User
        
        user_name = None
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            user_name = user.full_name if user else None
        
        activity = LeadActivity(
            lead_id=lead_id,
            activity_type=activity_type,
            activity_title=activity_title,
            activity_description=activity_description,
            performed_by_user_id=user_id,
            performed_by_name=user_name,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata,
            is_system_generated=is_system,
            activity_date=datetime.utcnow()
        )
        
        self.db.add(activity)
    
    def get_lead_activities(
        self,
        lead_id: int,
        page: int = 1,
        page_size: int = 50,
        tenant_id: Optional[int] = None
    ) -> Tuple[List[LeadActivity], int]:
        """Get lead activity history"""
        lead = self.get_lead(lead_id, tenant_id)
        if not lead:
            return [], 0
        
        query = self.db.query(LeadActivity).filter(LeadActivity.lead_id == lead_id)
        total = query.count()
        
        activities = query.order_by(desc(LeadActivity.activity_date))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return activities, total

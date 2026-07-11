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

"""
Business Rules Engine Database Models

Models for dynamic business rules management including:
- Rule categories and hierarchy
- Rule definitions with conditions and actions
- Rule evaluation history and audit trail
- Decision logging and override tracking
- Rule versioning
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, ForeignKey, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .connection import Base


class RuleCategory(Base):
    """
    Rule Category Model
    
    Hierarchical categorization of business rules for organization.
    Examples: credit_policy, eligibility, pricing, approval, risk_assessment
    """
    __tablename__ = "rule_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_code = Column(String(50), nullable=False, index=True)
    category_name = Column(String(200), nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer, ForeignKey('rule_categories.id'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    parent_category = relationship("RuleCategory", remote_side=[id], backref="sub_categories")
    rules = relationship("BusinessRule", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RuleCategory {self.category_code}: {self.category_name}>"


class BusinessRule(Base):
    """
    Business Rule Model
    
    Core model for storing business rule definitions.
    Rules are stored as JSON with conditions, actions, and metadata.
    Supports versioning, priority, and effective date management.
    """
    __tablename__ = "business_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(100), nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('rule_categories.id'), nullable=False)
    rule_type = Column(String(50), nullable=False)  # eligibility, scoring, pricing, approval
    description = Column(Text)
    priority = Column(Integer, default=100, nullable=False, index=True)  # 1-1000, lower = higher priority
    
    # Rule definition (JSON structure)
    rule_definition = Column(JSONB, nullable=False)
    
    # Evaluation strategy
    evaluation_strategy = Column(String(50), default='first_match')  # first_match, all_match, priority, best_match
    
    # Version management
    version = Column(Integer, default=1, nullable=False)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("RuleCategory", back_populates="rules")
    conditions = relationship("RuleCondition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("RuleAction", back_populates="rule", cascade="all, delete-orphan")
    evaluations = relationship("RuleEvaluation", back_populates="rule")
    versions = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BusinessRule {self.rule_code}: {self.rule_name} (v{self.version})>"



class RuleCondition(Base):
    """
    Rule Condition Model
    
    Individual conditions that make up a rule's evaluation logic.
    Supports complex conditions with grouping, operators, and data types.
    """
    __tablename__ = "rule_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey('business_rules.id'), nullable=False)
    condition_group = Column(Integer, default=1, nullable=False)  # For OR logic between groups
    sequence = Column(Integer, default=1, nullable=False)  # Order within group
    
    # Condition definition
    field_path = Column(String(200), nullable=False)  # JSON path: customer.age, loan.amount
    operator = Column(String(20), nullable=False)  # =, !=, <, <=, >, >=, in, not_in, between, contains, etc.
    value = Column(Text, nullable=False)  # Stored as JSON string
    data_type = Column(String(20), nullable=False)  # number, string, boolean, date, array
    
    # Modifiers
    is_negated = Column(Boolean, default=False)  # NOT condition
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Relationships
    rule = relationship("BusinessRule", back_populates="conditions")
    
    def __repr__(self):
        return f"<RuleCondition {self.field_path} {self.operator} {self.value}>"


class RuleAction(Base):
    """
    Rule Action Model
    
    Actions to execute when a rule matches.
    Examples: approve, reject, set_value, trigger_workflow, send_notification
    """
    __tablename__ = "rule_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey('business_rules.id'), nullable=False)
    
    # Action definition
    action_type = Column(String(50), nullable=False)  # approve, reject, set_value, calculate, trigger_workflow, etc.
    action_config = Column(JSONB, nullable=False)  # Action-specific configuration
    execution_order = Column(Integer, default=1, nullable=False)  # Order of execution
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Relationships
    rule = relationship("BusinessRule", back_populates="actions")
    
    def __repr__(self):
        return f"<RuleAction {self.action_type} for rule {self.rule_id}>"


class RuleEvaluation(Base):
    """
    Rule Evaluation Model
    
    Audit trail of rule evaluations.
    Records every rule evaluation with input, output, and execution details.
    """
    __tablename__ = "rule_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey('business_rules.id'), nullable=False)
    
    # Entity being evaluated
    entity_type = Column(String(50), nullable=False, index=True)  # loan_application, customer, deposit_account
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Evaluation data
    input_data = Column(JSONB, nullable=False)  # Snapshot of input data
    evaluation_result = Column(String(20), nullable=False, index=True)  # pass, fail, error
    matched = Column(Boolean, nullable=False)  # Did rule match?
    output_data = Column(JSONB)  # Result data (if any)
    
    # Performance
    execution_time_ms = Column(Integer)  # Execution time in milliseconds
    
    # Error handling
    error_message = Column(Text)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    evaluated_by = Column(Integer, nullable=False)  # User who triggered evaluation
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    rule = relationship("BusinessRule", back_populates="evaluations")
    
    def __repr__(self):
        return f"<RuleEvaluation {self.evaluation_id}: {self.evaluation_result}>"


class RuleDecision(Base):
    """
    Rule Decision Model
    
    Final decisions made by the rules engine after evaluating multiple rules.
    Aggregates results and provides decision rationale.
    """
    __tablename__ = "rule_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Entity for which decision was made
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Decision details
    decision_type = Column(String(50), nullable=False)  # credit_approval, eligibility_check, risk_assessment
    decision_result = Column(String(50), nullable=False, index=True)  # approved, rejected, manual_review
    confidence_score = Column(DECIMAL(5, 2))  # 0.00 to 100.00
    
    # Decision metadata
    rules_applied = Column(JSONB)  # List of rule IDs and their results
    decision_factors = Column(JSONB)  # Key factors that influenced decision
    recommendation = Column(Text)  # Human-readable recommendation
    
    # Override management
    override_applied = Column(Boolean, default=False)
    override_by = Column(Integer)  # User who overrode
    override_reason = Column(Text)
    override_at = Column(DateTime)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    decided_by = Column(Integer, nullable=False)  # User who triggered decision
    decided_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<RuleDecision {self.decision_id}: {self.decision_result}>"


class RuleVersion(Base):
    """
    Rule Version Model
    
    Version history for rules to track changes over time.
    Maintains complete snapshot of rule at each version.
    """
    __tablename__ = "rule_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey('business_rules.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Version snapshot
    rule_snapshot = Column(JSONB, nullable=False)  # Complete rule definition
    change_summary = Column(Text)  # What changed in this version
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    changed_by = Column(Integer, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rule = relationship("BusinessRule", back_populates="versions")
    
    def __repr__(self):
        return f"<RuleVersion {self.rule_id} v{self.version_number}>"

"""
Workflow Assignment Models
Defines data models for product-specific workflow assignment and configuration
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ApprovalLevel(str, Enum):
    """Approval levels"""
    BRANCH_MANAGER = "BRANCH_MANAGER"
    AREA_MANAGER = "AREA_MANAGER"
    REGIONAL_MANAGER = "REGIONAL_MANAGER"
    ZONAL_MANAGER = "ZONAL_MANAGER"
    CREDIT_MANAGER = "CREDIT_MANAGER"
    SENIOR_CREDIT_MANAGER = "SENIOR_CREDIT_MANAGER"
    CHIEF_CREDIT_OFFICER = "CHIEF_CREDIT_OFFICER"
    CREDIT_COMMITTEE = "CREDIT_COMMITTEE"
    MANAGING_DIRECTOR = "MANAGING_DIRECTOR"
    BOARD = "BOARD"


class CheckerLevel(str, Enum):
    """Checker levels for maker-checker"""
    CHECKER_1 = "CHECKER_1"
    CHECKER_2 = "CHECKER_2"
    CHECKER_3 = "CHECKER_3"
    SENIOR_CHECKER = "SENIOR_CHECKER"
    SUPERVISOR = "SUPERVISOR"


class SLAUnit(str, Enum):
    """SLA time units"""
    HOURS = "HOURS"
    DAYS = "DAYS"
    BUSINESS_DAYS = "BUSINESS_DAYS"


class StageType(str, Enum):
    """Workflow stage types"""
    DATA_ENTRY = "DATA_ENTRY"
    DOCUMENTATION = "DOCUMENTATION"
    VERIFICATION = "VERIFICATION"
    CREDIT_ASSESSMENT = "CREDIT_ASSESSMENT"
    LEGAL_OPINION = "LEGAL_OPINION"
    TECHNICAL_VALUATION = "TECHNICAL_VALUATION"
    APPROVAL = "APPROVAL"
    COMMITTEE_REVIEW = "COMMITTEE_REVIEW"
    DISBURSEMENT = "DISBURSEMENT"
    POST_DISBURSEMENT = "POST_DISBURSEMENT"


class AssignmentStatus(str, Enum):
    """Workflow assignment status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class CommitteeType(str, Enum):
    """Credit committee types"""
    BRANCH_COMMITTEE = "BRANCH_COMMITTEE"
    REGIONAL_COMMITTEE = "REGIONAL_COMMITTEE"
    CENTRAL_COMMITTEE = "CENTRAL_COMMITTEE"
    EXECUTIVE_COMMITTEE = "EXECUTIVE_COMMITTEE"
    BOARD_COMMITTEE = "BOARD_COMMITTEE"


# ============================================================================
# SLA CONFIGURATION
# ============================================================================

class SLAConfig(BaseModel):
    """SLA configuration for a stage"""
    sla_value: int = Field(ge=1, description="SLA value")
    sla_unit: SLAUnit
    warning_threshold_percentage: int = Field(70, ge=0, le=100, description="Warning at % of SLA")
    escalation_enabled: bool = False
    escalation_to: Optional[str] = None  # Role or user to escalate to
    auto_escalate_after_breach: bool = False


# ============================================================================
# APPROVAL CONFIGURATION
# ============================================================================

class ApprovalLevelConfig(BaseModel):
    """Approval level configuration"""
    level: ApprovalLevel
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    required_approvers: int = Field(1, ge=1, description="Number of approvers required")
    parallel_approval: bool = False  # All approve simultaneously vs sequential
    delegation_allowed: bool = True
    veto_power: bool = False  # Can reject without others


class ApprovalStage(BaseModel):
    """Approval stage configuration"""
    stage_name: str
    stage_type: StageType
    stage_order: int = Field(ge=1)
    description: str
    
    # SLA configuration
    sla_config: SLAConfig
    
    # Approval configuration
    approval_levels: List[ApprovalLevelConfig] = []
    skip_if_amount_below: Optional[float] = None
    auto_approve_conditions: Optional[Dict[str, Any]] = None
    
    # Assignment
    assigned_role: Optional[str] = None
    assigned_user_id: Optional[str] = None
    assign_to_originator: bool = False
    
    # Maker-Checker
    maker_checker_required: bool = False
    checker_level: Optional[CheckerLevel] = None
    
    # Conditional execution
    conditional_execution: bool = False
    execution_condition: Optional[Dict[str, Any]] = None
    
    # Stage controls
    mandatory: bool = True
    allow_skip: bool = False
    allow_parallel_execution: bool = False


# ============================================================================
# MAKER-CHECKER RULES
# ============================================================================

class MakerCheckerRule(BaseModel):
    """Maker-checker rule configuration"""
    rule_name: str
    applicable_stages: List[StageType] = []
    
    # Maker configuration
    maker_roles: List[str] = []
    maker_can_be_checker: bool = False
    
    # Checker configuration
    checker_level: CheckerLevel
    checker_roles: List[str] = []
    min_checkers: int = Field(1, ge=1)
    max_checkers: int = Field(1, ge=1)
    all_checkers_must_approve: bool = True
    
    # Amount-based rules
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    
    # Additional controls
    same_branch_required: bool = False
    senior_level_required: bool = False
    cooling_period_hours: Optional[int] = None


# ============================================================================
# COMMITTEE CONFIGURATION
# ============================================================================

class CommitteeMember(BaseModel):
    """Committee member configuration"""
    member_role: str
    member_name: Optional[str] = None
    member_user_id: Optional[str] = None
    is_chairman: bool = False
    voting_rights: bool = True
    required_for_quorum: bool = False


class CreditCommitteeConfig(BaseModel):
    """Credit committee configuration"""
    committee_type: CommitteeType
    committee_name: str
    
    # Amount thresholds
    min_amount: float = Field(ge=0)
    max_amount: Optional[float] = None
    
    # Members
    members: List[CommitteeMember] = []
    quorum_count: int = Field(ge=1)
    
    # Meeting configuration
    meeting_frequency: Optional[str] = None  # e.g., "WEEKLY", "MONTHLY"
    advance_notice_days: int = Field(2, ge=0)
    
    # Approval rules
    approval_threshold_percentage: int = Field(50, ge=1, le=100)
    chairman_veto: bool = False
    unanimous_required: bool = False
    
    # SLA
    sla_config: SLAConfig


# ============================================================================
# VERIFICATION STEPS
# ============================================================================

class DocumentVerificationStep(BaseModel):
    """Documentation verification step"""
    step_name: str
    document_types: List[str] = []  # Document types to verify
    verification_checklist: List[str] = []
    assigned_role: str
    sla_config: SLAConfig
    mandatory: bool = True


class LegalOpinionStep(BaseModel):
    """Legal opinion requirement"""
    step_name: str = "Legal Opinion"
    required_for_amount_above: Optional[float] = None
    required_for_product_types: List[str] = []
    legal_team_role: str = "LEGAL_OFFICER"
    opinion_checklist: List[str] = []
    sla_config: SLAConfig


class TechnicalValuationStep(BaseModel):
    """Technical valuation requirement"""
    step_name: str = "Technical Valuation"
    required_for_amount_above: Optional[float] = None
    required_for_property_types: List[str] = []
    valuer_panel: List[str] = []
    valuation_checklist: List[str] = []
    sla_config: SLAConfig
    independent_valuation_required: bool = True


# ============================================================================
# MAIN WORKFLOW ASSIGNMENT MODEL
# ============================================================================

class WorkflowAssignment(BaseModel):
    """Main workflow assignment model"""
    id: Optional[str] = None
    tenant_id: str
    
    # Assignment information
    assignment_code: str = Field(description="Unique assignment code")
    assignment_name: str
    description: str
    status: AssignmentStatus = AssignmentStatus.DRAFT
    
    # Product association
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    workflow_template_id: Optional[str] = None
    apply_to_all_products: bool = False
    
    # Workflow stages
    stages: List[ApprovalStage] = []
    
    # Approval configuration
    amount_based_routing: bool = True
    approval_matrix: List[ApprovalLevelConfig] = []
    
    # Maker-Checker rules
    maker_checker_rules: List[MakerCheckerRule] = []
    
    # Committee configuration
    credit_committees: List[CreditCommitteeConfig] = []
    
    # Verification steps
    documentation_verification: List[DocumentVerificationStep] = []
    legal_opinion_required: Optional[LegalOpinionStep] = None
    technical_valuation_required: Optional[TechnicalValuationStep] = None
    
    # Workflow controls
    allow_parallel_stages: bool = False
    allow_stage_skip: bool = False
    allow_backstep: bool = False
    auto_assignment_enabled: bool = True
    
    # SLA tracking
    overall_sla_days: Optional[int] = None
    sla_breach_notification: bool = True
    
    # Metadata
    effective_date: date
    expiry_date: Optional[date] = None
    priority: int = Field(10, ge=1, le=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# ============================================================================
# HELPER MODELS
# ============================================================================

class WorkflowAssignmentFilter(BaseModel):
    """Filter for listing workflow assignments"""
    status: Optional[AssignmentStatus] = None
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    workflow_template_id: Optional[str] = None
    search_term: Optional[str] = None


class WorkflowAssignmentStats(BaseModel):
    """Statistics for workflow assignments"""
    total_assignments: int = 0
    active_assignments: int = 0
    draft_assignments: int = 0
    assignments_by_product: Dict[str, int] = {}
    avg_stages_per_workflow: float = 0


class WorkflowAssignmentClone(BaseModel):
    """Clone workflow assignment request"""
    new_assignment_code: str
    new_assignment_name: Optional[str] = None
    new_product_id: Optional[str] = None


class ApprovalRouting(BaseModel):
    """Approval routing result"""
    loan_amount: float
    product_code: str
    required_approvers: List[ApprovalLevel]
    required_committees: List[CommitteeType]
    estimated_sla_days: int
    stages_to_execute: List[str]


class StageAssignment(BaseModel):
    """Stage assignment result"""
    stage_name: str
    assigned_to_role: Optional[str] = None
    assigned_to_user: Optional[str] = None
    sla_hours: int
    checker_required: bool
    checker_level: Optional[CheckerLevel] = None

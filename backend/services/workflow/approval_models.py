"""
Advanced Approval Workflow Models

Support for different approval patterns:
- Sequential Approval (one after another)
- Parallel Approval (all must approve)
- Any One Approval (first wins)
- Majority Approval (threshold-based)
- Conditional Approval (rule-based routing)
- Maker-Checker Pattern
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ApprovalType(str, Enum):
    """Approval workflow types"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ANY_ONE = "any_one"
    MAJORITY = "majority"
    CONDITIONAL = "conditional"


class ApprovalStatus(str, Enum):
    """Individual approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"
    DELEGATED = "delegated"


class ApprovalLevel(BaseModel):
    """Single approval level configuration"""
    level: int = Field(..., description="Level number (1, 2, 3...)")
    name: str = Field(..., description="Level name (e.g., 'Branch Manager')")
    
    # Assignment
    assigned_users: Optional[List[int]] = Field(None, description="Specific user IDs")
    assigned_roles: Optional[List[str]] = Field(None, description="Role names")
    assigned_groups: Optional[List[str]] = Field(None, description="Group names")
    
    # Approval settings
    approval_type: ApprovalType = ApprovalType.SEQUENTIAL
    threshold: Optional[int] = Field(None, description="For majority approval")
    threshold_percentage: Optional[float] = Field(None, description="Percentage threshold")
    
    # Conditions
    conditions: Optional[List[Dict[str, Any]]] = Field(None, description="Conditional routing rules")
    skip_conditions: Optional[List[Dict[str, Any]]] = Field(None, description="When to skip this level")
    
    # Timing
    sla_hours: Optional[int] = Field(None, description="SLA for this level")
    escalation_hours: Optional[int] = Field(None, description="Hours before escalation")
    escalate_to: Optional[List[int]] = Field(None, description="Escalate to user IDs")
    
    # Options
    allow_delegation: bool = True
    allow_comments: bool = True
    require_comments_on_reject: bool = True
    parallel_within_level: bool = False


class ApprovalChainConfig(BaseModel):
    """Complete approval chain configuration"""
    chain_id: str = Field(..., description="Unique chain identifier")
    name: str = Field(..., description="Chain name")
    description: Optional[str] = None
    
    # Entity configuration
    entity_type: str = Field(..., description="Entity type (loan, deposit, customer)")
    
    # Approval levels
    levels: List[ApprovalLevel] = Field(..., min_items=1)
    
    # Overall settings
    overall_type: ApprovalType = ApprovalType.SEQUENTIAL
    auto_approve_threshold: Optional[float] = Field(None, description="Auto-approve if score > threshold")
    
    # Maker-Checker
    maker_checker_enabled: bool = False
    maker_checker_same_level: bool = False  # Can maker approve at same level?
    
    # Notification
    notify_on_approval: bool = True
    notify_on_rejection: bool = True
    notify_initiator: bool = True
    
    # Advanced
    allow_skip_levels: bool = False
    allow_return_to_maker: bool = True
    version: int = 1


class ApprovalInstance(BaseModel):
    """Running approval instance"""
    instance_id: int
    chain_id: str
    entity_type: str
    entity_id: int
    
    # Maker info
    maker_id: int
    maker_action: str  # created, modified
    maker_timestamp: str
    
    # Status
    overall_status: str  # pending, approved, rejected, in_progress
    current_level: int
    
    # Approvals
    level_approvals: List[Dict[str, Any]]  # List of approvals per level
    
    # Metadata
    variables: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ApprovalAction(BaseModel):
    """Approval action request"""
    action: str = Field(..., description="approve, reject, delegate, return")
    comments: Optional[str] = None
    delegate_to: Optional[int] = Field(None, description="For delegation")
    return_to_level: Optional[int] = Field(None, description="For return action")
    attachments: Optional[List[str]] = None


class MakerCheckerConfig(BaseModel):
    """Maker-Checker configuration"""
    enabled: bool = True
    
    # Maker settings
    maker_roles: List[str] = Field(..., description="Roles that can be makers")
    maker_can_approve: bool = False
    
    # Checker settings
    checker_roles: List[str] = Field(..., description="Roles that can be checkers")
    checker_levels: List[int] = Field(..., description="Which levels are checkers")
    
    # Rules
    same_user_check: bool = False  # Can same user be maker and checker?
    minimum_checkers: int = 1
    
    # Auto-checks
    auto_checks: Optional[List[str]] = Field(None, description="Automated checks to run")


# ==================== PRE-BUILT APPROVAL CHAINS ====================

class ApprovalChainTemplates:
    """Pre-built approval chain templates"""
    
    @staticmethod
    def loan_approval_chain() -> ApprovalChainConfig:
        """Standard loan approval chain"""
        return ApprovalChainConfig(
            chain_id="loan_approval_standard",
            name="Standard Loan Approval Chain",
            description="Multi-level loan approval with conditional routing",
            entity_type="loan_application",
            overall_type=ApprovalType.SEQUENTIAL,
            maker_checker_enabled=True,
            levels=[
                ApprovalLevel(
                    level=1,
                    name="Loan Officer Review",
                    assigned_roles=["loan_officer"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=24,
                    conditions=[
                        {
                            "type": "simple",
                            "field": "loan_amount",
                            "operator": "<",
                            "value": 500000,
                            "action": "approve_and_complete"
                        }
                    ]
                ),
                ApprovalLevel(
                    level=2,
                    name="Branch Manager Approval",
                    assigned_roles=["branch_manager"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=48,
                    skip_conditions=[
                        {
                            "field": "loan_amount",
                            "operator": "<",
                            "value": 500000
                        }
                    ],
                    conditions=[
                        {
                            "type": "simple",
                            "field": "loan_amount",
                            "operator": "<",
                            "value": 2500000,
                            "action": "approve_and_complete"
                        }
                    ]
                ),
                ApprovalLevel(
                    level=3,
                    name="Credit Committee Review",
                    assigned_roles=["credit_committee_member"],
                    approval_type=ApprovalType.MAJORITY,
                    threshold=3,
                    threshold_percentage=60.0,
                    sla_hours=72,
                    parallel_within_level=True,
                    skip_conditions=[
                        {
                            "field": "loan_amount",
                            "operator": "<",
                            "value": 2500000
                        }
                    ]
                )
            ]
        )
    
    @staticmethod
    def parallel_approval_chain() -> ApprovalChainConfig:
        """Parallel approval chain (all teams must approve)"""
        return ApprovalChainConfig(
            chain_id="parallel_approval_all_teams",
            name="Parallel Approval - All Teams",
            description="Risk, Legal, and Finance must all approve",
            entity_type="high_value_transaction",
            overall_type=ApprovalType.PARALLEL,
            levels=[
                ApprovalLevel(
                    level=1,
                    name="Risk Team Approval",
                    assigned_roles=["risk_officer"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=24
                ),
                ApprovalLevel(
                    level=1,  # Same level = parallel
                    name="Legal Team Approval",
                    assigned_roles=["legal_officer"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=24
                ),
                ApprovalLevel(
                    level=1,  # Same level = parallel
                    name="Finance Team Approval",
                    assigned_roles=["finance_officer"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=24
                )
            ]
        )
    
    @staticmethod
    def any_one_approval_chain() -> ApprovalChainConfig:
        """Any one approval chain (first to approve wins)"""
        return ApprovalChainConfig(
            chain_id="any_one_regional_manager",
            name="Any Regional Manager Approval",
            description="Any one of the regional managers can approve",
            entity_type="regional_initiative",
            overall_type=ApprovalType.ANY_ONE,
            levels=[
                ApprovalLevel(
                    level=1,
                    name="Regional Manager Approval (Any)",
                    assigned_roles=["regional_manager_north", "regional_manager_south", 
                                   "regional_manager_east", "regional_manager_west"],
                    approval_type=ApprovalType.ANY_ONE,
                    sla_hours=48
                )
            ]
        )
    
    @staticmethod
    def maker_checker_chain() -> ApprovalChainConfig:
        """Simple maker-checker chain"""
        return ApprovalChainConfig(
            chain_id="maker_checker_simple",
            name="Maker-Checker Approval",
            description="Maker creates, checker approves (no self-approval)",
            entity_type="general_transaction",
            overall_type=ApprovalType.SEQUENTIAL,
            maker_checker_enabled=True,
            maker_checker_same_level=False,
            levels=[
                ApprovalLevel(
                    level=1,
                    name="Checker Approval",
                    assigned_roles=["approver", "supervisor"],
                    approval_type=ApprovalType.SEQUENTIAL,
                    sla_hours=24
                )
            ]
        )

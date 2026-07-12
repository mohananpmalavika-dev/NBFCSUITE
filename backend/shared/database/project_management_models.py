"""
Project Management Database Models
Manages projects, tasks, time tracking, budgets, and resources
"""

from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from decimal import Decimal
import enum

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class ProjectStatus(str, enum.Enum):
    """Project status"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(str, enum.Enum):
    """Project priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectType(str, enum.Enum):
    """Project type"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    RESEARCH = "research"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"
    INFRASTRUCTURE = "infrastructure"
    COMPLIANCE = "compliance"
    AUDIT = "audit"


class TaskStatus(str, enum.Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, enum.Enum):
    """Task type"""
    FEATURE = "feature"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    RESEARCH = "research"
    MEETING = "meeting"
    REVIEW = "review"


class TimeEntryStatus(str, enum.Enum):
    """Time entry status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    BILLED = "billed"


class BudgetStatus(str, enum.Enum):
    """Budget status"""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    CLOSED = "closed"


class ExpenseCategory(str, enum.Enum):
    """Expense category"""
    SALARY = "salary"
    CONTRACTOR = "contractor"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    TRAVEL = "travel"
    TRAINING = "training"
    INFRASTRUCTURE = "infrastructure"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    MISCELLANEOUS = "miscellaneous"


class ExpenseStatus(str, enum.Enum):
    """Expense status"""
    PLANNED = "planned"
    COMMITTED = "committed"
    ACTUAL = "actual"


class ResourceAllocationStatus(str, enum.Enum):
    """Resource allocation status"""
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============================================================================
# PROJECT MODELS
# ============================================================================

class Project(BaseModel):
    """
    Project entity
    Main project master with comprehensive details
    """
    __tablename__ = "pm_projects"
    
    # Basic Information
    project_code = Column(String(50), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    project_description = Column(Text, nullable=True)
    
    # Classification
    project_type = Column(SQLEnum(ProjectType), nullable=False, default=ProjectType.INTERNAL)
    project_priority = Column(SQLEnum(ProjectPriority), nullable=False, default=ProjectPriority.MEDIUM)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING, index=True)
    
    # Timeline
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Project Manager
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Sponsor & Stakeholders
    sponsor_name = Column(String(200), nullable=True)
    sponsor_email = Column(String(100), nullable=True)
    client_name = Column(String(200), nullable=True)
    client_contact = Column(String(100), nullable=True)
    
    # Department & Branch
    department_id = Column(UUID(as_uuid=True), ForeignKey("hrms_departments.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Budget
    estimated_budget = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    approved_budget = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    actual_cost = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    currency = Column(String(10), default="INR")
    
    # Progress
    progress_percentage = Column(Integer, default=0)
    health_status = Column(String(20), default="green")  # green, amber, red
    
    # Objectives & Goals
    objectives = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    deliverables = Column(Text, nullable=True)  # JSON array
    
    # Risk & Issues
    key_risks = Column(Text, nullable=True)
    current_issues = Column(Text, nullable=True)
    
    # Tags & Categories
    tags = Column(JSONB, nullable=True)  # Array of tags
    custom_fields = Column(JSONB, nullable=True)  # Flexible custom data
    
    # Attachments
    attachments = Column(JSONB, nullable=True)  # Array of attachment URLs
    
    # Flags
    is_billable = Column(Boolean, default=False)
    is_confidential = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    department = relationship("Department", foreign_keys=[department_id])
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan", lazy="select")
    milestones = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan", lazy="select")
    resources = relationship("ResourceAllocation", back_populates="project", cascade="all, delete-orphan", lazy="select")
    budgets = relationship("ProjectBudget", back_populates="project", cascade="all, delete-orphan", lazy="select")
    time_entries = relationship("TimeEntry", back_populates="project", lazy="select")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_project_code', 'tenant_id', 'project_code', unique=True),
        Index('idx_project_status', 'tenant_id', 'status'),
        Index('idx_project_manager', 'tenant_id', 'project_manager_id'),
        Index('idx_project_dates', 'tenant_id', 'planned_start_date', 'planned_end_date'),
    )
    
    def __repr__(self):
        return f"<Project(code={self.project_code}, name={self.project_name})>"


class ProjectMilestone(BaseModel):
    """
    Project Milestone entity
    Key milestones and checkpoints in a project
    """
    __tablename__ = "pm_project_milestones"
    
    # Basic Information
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_name = Column(String(200), nullable=False)
    milestone_description = Column(Text, nullable=True)
    
    # Timeline
    planned_date = Column(Date, nullable=False)
    actual_date = Column(Date, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)
    
    # Details
    deliverables = Column(Text, nullable=True)
    acceptance_criteria = Column(Text, nullable=True)
    
    # Order
    sequence_number = Column(Integer, nullable=False, default=1)
    
    # Relationships
    project = relationship("Project", back_populates="milestones")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_milestone_project', 'tenant_id', 'project_id'),
        Index('idx_milestone_dates', 'tenant_id', 'planned_date'),
    )
    
    def __repr__(self):
        return f"<ProjectMilestone(project_id={self.project_id}, name={self.milestone_name})>"


# ============================================================================
# TASK MODELS
# ============================================================================

class Task(BaseModel):
    """
    Task entity
    Individual tasks within projects
    """
    __tablename__ = "pm_tasks"
    
    # Basic Information
    task_code = Column(String(50), nullable=False, index=True)
    task_title = Column(String(300), nullable=False)
    task_description = Column(Text, nullable=True)
    
    # Project Link
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Parent Task (for subtasks)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("pm_tasks.id", ondelete="CASCADE"), nullable=True)
    
    # Classification
    task_type = Column(SQLEnum(TaskType), nullable=False, default=TaskType.FEATURE)
    task_priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.TODO, index=True)
    
    # Assignment
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    assigned_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    
    # Timeline
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True, index=True)
    
    # Effort Estimation
    estimated_hours = Column(Numeric(10, 2), nullable=True, default=Decimal('0.00'))
    actual_hours = Column(Numeric(10, 2), nullable=True, default=Decimal('0.00'))
    remaining_hours = Column(Numeric(10, 2), nullable=True, default=Decimal('0.00'))
    
    # Progress
    progress_percentage = Column(Integer, default=0)
    
    # Blocking Information
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(Text, nullable=True)
    blocked_by_task_id = Column(UUID(as_uuid=True), ForeignKey("pm_tasks.id", ondelete="SET NULL"), nullable=True)
    
    # Dependencies
    depends_on_task_ids = Column(JSONB, nullable=True)  # Array of task IDs
    
    # Tags & Labels
    labels = Column(JSONB, nullable=True)  # Array of labels
    tags = Column(JSONB, nullable=True)  # Array of tags
    
    # Checklist
    checklist_items = Column(JSONB, nullable=True)  # Array of checklist objects
    
    # Attachments
    attachments = Column(JSONB, nullable=True)  # Array of attachment URLs
    
    # Custom Fields
    custom_fields = Column(JSONB, nullable=True)
    
    # Flags
    is_milestone = Column(Boolean, default=False)
    is_billable = Column(Boolean, default=True)
    
    # Order
    display_order = Column(Integer, default=0)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    assigned_by = relationship("Employee", foreign_keys=[assigned_by_id])
    parent_task = relationship("Task", remote_side="Task.id", foreign_keys=[parent_task_id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task", foreign_keys=[parent_task_id], cascade="all, delete-orphan")
    blocked_by_task = relationship("Task", remote_side="Task.id", foreign_keys=[blocked_by_task_id])
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan", lazy="select")
    time_entries = relationship("TimeEntry", back_populates="task", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_task_code', 'tenant_id', 'task_code', unique=True),
        Index('idx_task_project', 'tenant_id', 'project_id', 'status'),
        Index('idx_task_assigned', 'tenant_id', 'assigned_to_id', 'status'),
        Index('idx_task_due_date', 'tenant_id', 'due_date'),
    )
    
    def __repr__(self):
        return f"<Task(code={self.task_code}, title={self.task_title})>"


class TaskComment(BaseModel):
    """
    Task Comment entity
    Comments and discussions on tasks
    """
    __tablename__ = "pm_task_comments"
    
    # Basic Information
    task_id = Column(UUID(as_uuid=True), ForeignKey("pm_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_text = Column(Text, nullable=False)
    
    # Author
    commented_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Parent Comment (for threaded comments)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("pm_task_comments.id", ondelete="CASCADE"), nullable=True)
    
    # Metadata
    is_internal = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    
    # Attachments
    attachments = Column(JSONB, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    commented_by = relationship("Employee", foreign_keys=[commented_by_id])
    parent_comment = relationship("TaskComment", remote_side="TaskComment.id", foreign_keys=[parent_comment_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_comment_task', 'tenant_id', 'task_id'),
        Index('idx_comment_created', 'tenant_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<TaskComment(task_id={self.task_id}, by={self.commented_by_id})>"


# ============================================================================
# TIME TRACKING MODELS
# ============================================================================

class TimeEntry(BaseModel):
    """
    Time Entry entity
    Track time spent on projects and tasks
    """
    __tablename__ = "pm_time_entries"
    
    # Basic Information
    entry_code = Column(String(50), nullable=False, index=True)
    
    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Project & Task
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("pm_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Time Details
    entry_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    hours = Column(Numeric(10, 2), nullable=False)
    
    # Description
    description = Column(Text, nullable=False)
    work_type = Column(String(100), nullable=True)  # development, testing, meeting, etc.
    
    # Status
    status = Column(SQLEnum(TimeEntryStatus), nullable=False, default=TimeEntryStatus.DRAFT, index=True)
    
    # Approval
    submitted_date = Column(DateTime, nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Billing
    is_billable = Column(Boolean, default=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    billing_amount = Column(Numeric(15, 2), nullable=True)
    is_billed = Column(Boolean, default=False)
    invoice_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    task = relationship("Task", back_populates="time_entries")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_time_entry_code', 'tenant_id', 'entry_code', unique=True),
        Index('idx_time_entry_emp_date', 'tenant_id', 'employee_id', 'entry_date'),
        Index('idx_time_entry_project', 'tenant_id', 'project_id', 'entry_date'),
        Index('idx_time_entry_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<TimeEntry(code={self.entry_code}, date={self.entry_date}, hours={self.hours})>"


# ============================================================================
# BUDGET MODELS
# ============================================================================

class ProjectBudget(BaseModel):
    """
    Project Budget entity
    Budget planning and tracking for projects
    """
    __tablename__ = "pm_project_budgets"
    
    # Basic Information
    budget_code = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Budget Details
    budget_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Fiscal Period
    fiscal_year = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Budget Amounts
    planned_budget = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    approved_budget = Column(Numeric(15, 2), nullable=True, default=Decimal('0.00'))
    revised_budget = Column(Numeric(15, 2), nullable=True)
    
    # Actual Costs
    committed_cost = Column(Numeric(15, 2), default=Decimal('0.00'))  # POs, Commitments
    actual_cost = Column(Numeric(15, 2), default=Decimal('0.00'))  # Invoices, Expenses
    available_budget = Column(Numeric(15, 2), default=Decimal('0.00'))
    
    # Variance
    budget_variance = Column(Numeric(15, 2), default=Decimal('0.00'))
    variance_percentage = Column(Numeric(5, 2), default=Decimal('0.00'))
    
    # Status
    status = Column(SQLEnum(BudgetStatus), nullable=False, default=BudgetStatus.DRAFT, index=True)
    
    # Approval
    submitted_date = Column(DateTime, nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Currency
    currency = Column(String(10), default="INR")
    
    # Alerts
    alert_threshold_percentage = Column(Integer, default=80)  # Alert when 80% consumed
    is_threshold_exceeded = Column(Boolean, default=False)
    
    # Relationships
    project = relationship("Project", back_populates="budgets")
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    expense_lines = relationship("BudgetExpenseLine", back_populates="budget", cascade="all, delete-orphan", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_budget_code', 'tenant_id', 'budget_code', unique=True),
        Index('idx_budget_project', 'tenant_id', 'project_id'),
        Index('idx_budget_status', 'tenant_id', 'status'),
        Index('idx_budget_fiscal', 'tenant_id', 'fiscal_year'),
    )
    
    def __repr__(self):
        return f"<ProjectBudget(code={self.budget_code}, project_id={self.project_id})>"


class BudgetExpenseLine(BaseModel):
    """
    Budget Expense Line entity
    Detailed breakdown of budget expenses by category
    """
    __tablename__ = "pm_budget_expense_lines"
    
    # Basic Information
    budget_id = Column(UUID(as_uuid=True), ForeignKey("pm_project_budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Expense Details
    expense_category = Column(SQLEnum(ExpenseCategory), nullable=False)
    description = Column(Text, nullable=True)
    
    # Amounts
    planned_amount = Column(Numeric(15, 2), nullable=False, default=Decimal('0.00'))
    committed_amount = Column(Numeric(15, 2), default=Decimal('0.00'))
    actual_amount = Column(Numeric(15, 2), default=Decimal('0.00'))
    variance = Column(Numeric(15, 2), default=Decimal('0.00'))
    
    # Status
    status = Column(SQLEnum(ExpenseStatus), nullable=False, default=ExpenseStatus.PLANNED)
    
    # Period
    expense_month = Column(String(7), nullable=True)  # YYYY-MM format
    
    # Reference
    reference_number = Column(String(100), nullable=True)
    vendor_name = Column(String(200), nullable=True)
    
    # Relationships
    budget = relationship("ProjectBudget", back_populates="expense_lines")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_expense_budget', 'tenant_id', 'budget_id'),
        Index('idx_expense_category', 'tenant_id', 'expense_category'),
        Index('idx_expense_month', 'tenant_id', 'expense_month'),
    )
    
    def __repr__(self):
        return f"<BudgetExpenseLine(budget_id={self.budget_id}, category={self.expense_category})>"


# ============================================================================
# RESOURCE ALLOCATION MODELS
# ============================================================================

class ResourceAllocation(BaseModel):
    """
    Resource Allocation entity
    Assign and track resources (employees) to projects
    """
    __tablename__ = "pm_resource_allocations"
    
    # Basic Information
    allocation_code = Column(String(50), nullable=False, index=True)
    
    # Project & Employee
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Role
    role_in_project = Column(String(100), nullable=False)  # Developer, Tester, Manager, etc.
    responsibilities = Column(Text, nullable=True)
    
    # Timeline
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Allocation Percentage
    allocation_percentage = Column(Integer, nullable=False, default=100)  # % of time allocated
    hours_per_week = Column(Numeric(5, 2), nullable=True)
    
    # Cost
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    is_billable = Column(Boolean, default=True)
    
    # Status
    status = Column(SQLEnum(ResourceAllocationStatus), nullable=False, default=ResourceAllocationStatus.PROPOSED, index=True)
    
    # Approval
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="resources")
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="resource_allocations")
    requested_by = relationship("Employee", foreign_keys=[requested_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_allocation_code', 'tenant_id', 'allocation_code', unique=True),
        Index('idx_allocation_project', 'tenant_id', 'project_id'),
        Index('idx_allocation_employee', 'tenant_id', 'employee_id', 'status'),
        Index('idx_allocation_dates', 'tenant_id', 'start_date', 'end_date'),
    )
    
    def __repr__(self):
        return f"<ResourceAllocation(code={self.allocation_code}, project_id={self.project_id})>"


# ============================================================================
# DOCUMENT MODELS
# ============================================================================

class ProjectDocument(BaseModel):
    """
    Project Document entity
    Store project-related documents
    """
    __tablename__ = "pm_project_documents"
    
    # Basic Information
    document_code = Column(String(50), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Details
    document_name = Column(String(300), nullable=False)
    document_type = Column(String(100), nullable=True)  # requirements, design, plan, report, etc.
    description = Column(Text, nullable=True)
    
    # File Information
    file_name = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Version Control
    version = Column(String(20), default="1.0")
    is_latest_version = Column(Boolean, default=True)
    
    # Upload Information
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Access Control
    is_public = Column(Boolean, default=False)
    is_confidential = Column(Boolean, default=False)
    
    # Tags
    tags = Column(JSONB, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    uploaded_by = relationship("Employee", foreign_keys=[uploaded_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_doc_code', 'tenant_id', 'document_code', unique=True),
        Index('idx_doc_project', 'tenant_id', 'project_id'),
        Index('idx_doc_type', 'tenant_id', 'document_type'),
    )
    
    def __repr__(self):
        return f"<ProjectDocument(code={self.document_code}, name={self.document_name})>"


# ============================================================================
# UPDATE EMPLOYEE MODEL WITH PROJECT MANAGEMENT RELATIONSHIPS
# ============================================================================

# These relationships should be added to the Employee model in hrms_models.py
# Employee.assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to", lazy="select")
# Employee.time_entries = relationship("TimeEntry", foreign_keys="TimeEntry.employee_id", back_populates="employee", lazy="select")
# Employee.resource_allocations = relationship("ResourceAllocation", foreign_keys="ResourceAllocation.employee_id", back_populates="employee", lazy="select")

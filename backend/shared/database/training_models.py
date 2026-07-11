"""
HRMS Training & Development Database Models
Training Calendar, Courses, Delivery, Assessment, Certification, LMS Integration, Skill Matrix
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

class TrainingType(str, enum.Enum):
    """Training type"""
    CLASSROOM = "classroom"
    ONLINE = "online"
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    CONFERENCE = "conference"
    ON_THE_JOB = "on_the_job"
    MENTORING = "mentoring"
    SELF_PACED = "self_paced"
    BLENDED = "blended"


class TrainingCategory(str, enum.Enum):
    """Training category"""
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"
    COMPLIANCE = "compliance"
    PRODUCT = "product"
    SALES = "sales"
    CUSTOMER_SERVICE = "customer_service"
    SAFETY = "safety"
    INDUCTION = "induction"
    PROFESSIONAL = "professional"


class TrainingStatus(str, enum.Enum):
    """Training status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class ParticipantStatus(str, enum.Enum):
    """Participant enrollment status"""
    NOMINATED = "nominated"
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    ABSENT = "absent"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"


class AssessmentType(str, enum.Enum):
    """Assessment type"""
    PRE_TEST = "pre_test"
    POST_TEST = "post_test"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PRACTICAL = "practical"
    PROJECT = "project"
    VIVA = "viva"
    CASE_STUDY = "case_study"


class CertificationStatus(str, enum.Enum):
    """Certification status"""
    PENDING = "pending"
    ISSUED = "issued"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RENEWED = "renewed"


class SkillLevel(str, enum.Enum):
    """Skill proficiency level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TrainingPriority(str, enum.Enum):
    """Training priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrainingDeliveryMode(str, enum.Enum):
    """Training delivery mode"""
    INSTRUCTOR_LED = "instructor_led"
    SELF_PACED = "self_paced"
    BLENDED = "blended"
    VIRTUAL = "virtual"


# ============================================================================
# TRAINING COURSE MASTER
# ============================================================================

class TrainingCourse(BaseModel):
    """
    Training Course Master
    Catalog of all available training courses
    """
    __tablename__ = "hrms_training_courses"
    
    # Course Identification
    course_code = Column(String(50), nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    course_description = Column(Text, nullable=True)
    
    # Classification
    training_type = Column(SQLEnum(TrainingType), nullable=False)
    training_category = Column(SQLEnum(TrainingCategory), nullable=False)
    delivery_mode = Column(SQLEnum(TrainingDeliveryMode), nullable=False, default=TrainingDeliveryMode.INSTRUCTOR_LED)
    
    # Course Details
    duration_hours = Column(Numeric(5, 2), nullable=False)
    duration_days = Column(Integer, nullable=True)
    max_participants = Column(Integer, nullable=True)
    min_participants = Column(Integer, nullable=True)
    
    # Target Audience
    target_designation_ids = Column(JSONB, nullable=True)  # List of designation IDs
    target_department_ids = Column(JSONB, nullable=True)  # List of department IDs
    experience_level_required = Column(String(100), nullable=True)
    
    # Prerequisites
    prerequisites = Column(Text, nullable=True)
    prerequisite_course_ids = Column(JSONB, nullable=True)  # List of prerequisite course IDs
    
    # Learning Objectives
    learning_objectives = Column(Text, nullable=True)
    syllabus = Column(Text, nullable=True)
    
    # Provider/Vendor Details
    internal_trainer_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    external_trainer_name = Column(String(200), nullable=True)
    external_trainer_organization = Column(String(200), nullable=True)
    external_trainer_contact = Column(String(100), nullable=True)
    
    # LMS Integration
    lms_course_id = Column(String(100), nullable=True)
    lms_course_url = Column(String(500), nullable=True)
    
    # Cost
    cost_per_participant = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="INR")
    
    # Materials
    training_materials_url = Column(String(500), nullable=True)
    course_materials = Column(JSONB, nullable=True)  # List of material links
    
    # Certification
    provides_certificate = Column(Boolean, default=False)
    certificate_template_id = Column(UUID(as_uuid=True), nullable=True)
    certificate_validity_months = Column(Integer, nullable=True)
    
    # Compliance
    is_mandatory = Column(Boolean, default=False)
    is_compliance_training = Column(Boolean, default=False)
    compliance_frequency_months = Column(Integer, nullable=True)  # How often to repeat
    
    # Status
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Ratings
    average_rating = Column(Numeric(3, 2), nullable=True)
    total_ratings = Column(Integer, default=0)
    
    # Relationships
    internal_trainer = relationship("Employee", foreign_keys=[internal_trainer_id])
    training_sessions = relationship("TrainingSession", back_populates="course", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_course_code', 'tenant_id', 'course_code', unique=True),
        Index('idx_tenant_course_type', 'tenant_id', 'training_type'),
        Index('idx_tenant_course_category', 'tenant_id', 'training_category'),
        Index('idx_tenant_course_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<TrainingCourse(code={self.course_code}, name={self.course_name})>"



# ============================================================================
# TRAINING CALENDAR & SESSIONS
# ============================================================================

class TrainingSession(BaseModel):
    """
    Training Session/Schedule
    Individual training instances scheduled in calendar
    """
    __tablename__ = "hrms_training_sessions"
    
    # Session Identification
    session_code = Column(String(50), nullable=False, index=True)
    session_name = Column(String(200), nullable=False)
    
    # Course Link
    course_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_courses.id", ondelete="CASCADE"), nullable=False)
    
    # Schedule
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)  # HH:MM format
    end_time = Column(String(10), nullable=True)
    
    # Location
    location_type = Column(String(20), nullable=False, default="physical")  # physical, virtual, hybrid
    venue = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    virtual_meeting_link = Column(String(500), nullable=True)
    virtual_meeting_id = Column(String(100), nullable=True)
    virtual_meeting_password = Column(String(100), nullable=True)
    
    # Trainer
    trainer_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    external_trainer_name = Column(String(200), nullable=True)
    co_trainers = Column(JSONB, nullable=True)  # List of employee IDs or names
    
    # Capacity
    max_participants = Column(Integer, nullable=False)
    enrolled_count = Column(Integer, default=0)
    confirmed_count = Column(Integer, default=0)
    attended_count = Column(Integer, default=0)
    
    # Status
    status = Column(SQLEnum(TrainingStatus), nullable=False, default=TrainingStatus.SCHEDULED)
    
    # Budget
    budget_allocated = Column(Numeric(15, 2), nullable=True)
    actual_cost = Column(Numeric(15, 2), nullable=True)
    
    # Approval
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Session Details
    session_notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Feedback
    average_feedback_rating = Column(Numeric(3, 2), nullable=True)
    feedback_count = Column(Integer, default=0)
    
    # LMS Integration
    lms_session_id = Column(String(100), nullable=True)
    
    # Relationships
    course = relationship("TrainingCourse", back_populates="training_sessions")
    trainer = relationship("Employee", foreign_keys=[trainer_id])
    requested_by = relationship("Employee", foreign_keys=[requested_by_id])
    approved_by = relationship("Employee", foreign_keys=[approved_by_id])
    participants = relationship("TrainingParticipant", back_populates="session", lazy="select")
    assessments = relationship("TrainingAssessment", back_populates="session", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_session_code', 'tenant_id', 'session_code', unique=True),
        Index('idx_tenant_session_course', 'tenant_id', 'course_id'),
        Index('idx_tenant_session_date', 'tenant_id', 'start_date'),
        Index('idx_tenant_session_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<TrainingSession(code={self.session_code}, course_id={self.course_id})>"


# ============================================================================
# TRAINING PARTICIPANTS
# ============================================================================

class TrainingParticipant(BaseModel):
    """
    Training Participants
    Employees enrolled/nominated for training sessions
    """
    __tablename__ = "hrms_training_participants"
    
    # Participant Details
    session_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_sessions.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    
    # Nomination
    nominated_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    nomination_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    nomination_reason = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(ParticipantStatus), nullable=False, default=ParticipantStatus.NOMINATED)
    
    # Registration
    registration_date = Column(DateTime, nullable=True)
    confirmation_date = Column(DateTime, nullable=True)
    
    # Attendance
    attended = Column(Boolean, default=False)
    attendance_percentage = Column(Numeric(5, 2), nullable=True)
    attendance_date = Column(DateTime, nullable=True)
    absence_reason = Column(Text, nullable=True)
    
    # Assessment Results
    pre_test_score = Column(Numeric(5, 2), nullable=True)
    post_test_score = Column(Numeric(5, 2), nullable=True)
    final_score = Column(Numeric(5, 2), nullable=True)
    passed = Column(Boolean, default=False)
    
    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_number = Column(String(100), nullable=True)
    certificate_issue_date = Column(Date, nullable=True)
    certificate_url = Column(String(500), nullable=True)
    
    # Feedback
    feedback_rating = Column(Integer, nullable=True)  # 1-5
    feedback_comments = Column(Text, nullable=True)
    feedback_submitted_date = Column(DateTime, nullable=True)
    
    # Cost
    cost_incurred = Column(Numeric(15, 2), nullable=True)
    
    # Cancellation
    cancelled_date = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # LMS Integration
    lms_enrollment_id = Column(String(100), nullable=True)
    lms_progress_percentage = Column(Integer, nullable=True)
    
    # Relationships
    session = relationship("TrainingSession", back_populates="participants")
    employee = relationship("Employee", foreign_keys=[employee_id])
    nominated_by = relationship("Employee", foreign_keys=[nominated_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_participant_session_emp', 'tenant_id', 'session_id', 'employee_id', unique=True),
        Index('idx_tenant_participant_employee', 'tenant_id', 'employee_id'),
        Index('idx_tenant_participant_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<TrainingParticipant(session_id={self.session_id}, employee_id={self.employee_id})>"


# ============================================================================
# ASSESSMENTS & EVALUATIONS
# ============================================================================

class TrainingAssessment(BaseModel):
    """
    Training Assessments
    Tests, quizzes, assignments for training evaluation
    """
    __tablename__ = "hrms_training_assessments"
    
    # Assessment Identification
    assessment_code = Column(String(50), nullable=False, index=True)
    assessment_name = Column(String(200), nullable=False)
    assessment_description = Column(Text, nullable=True)
    
    # Links
    course_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_courses.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_sessions.id", ondelete="CASCADE"), nullable=True)
    
    # Assessment Type
    assessment_type = Column(SQLEnum(AssessmentType), nullable=False)
    
    # Configuration
    total_marks = Column(Integer, nullable=False, default=100)
    passing_marks = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    
    # Questions
    questions = Column(JSONB, nullable=True)  # JSON structure for questions
    question_count = Column(Integer, nullable=True)
    
    # Schedule
    scheduled_date = Column(Date, nullable=True)
    start_time = Column(String(10), nullable=True)
    end_time = Column(String(10), nullable=True)
    
    # LMS Integration
    lms_assessment_id = Column(String(100), nullable=True)
    lms_assessment_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Statistics
    average_score = Column(Numeric(5, 2), nullable=True)
    highest_score = Column(Numeric(5, 2), nullable=True)
    lowest_score = Column(Numeric(5, 2), nullable=True)
    pass_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    course = relationship("TrainingCourse", foreign_keys=[course_id])
    session = relationship("TrainingSession", foreign_keys=[session_id])
    results = relationship("AssessmentResult", back_populates="assessment", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_assessment_code', 'tenant_id', 'assessment_code', unique=True),
        Index('idx_tenant_assessment_course', 'tenant_id', 'course_id'),
        Index('idx_tenant_assessment_session', 'tenant_id', 'session_id'),
    )
    
    def __repr__(self):
        return f"<TrainingAssessment(code={self.assessment_code}, name={self.assessment_name})>"


class AssessmentResult(BaseModel):
    """
    Assessment Results
    Individual employee assessment scores
    """
    __tablename__ = "hrms_assessment_results"
    
    # Links
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_assessments.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_participants.id", ondelete="CASCADE"), nullable=True)
    
    # Attempt Details
    attempt_number = Column(Integer, default=1)
    attempt_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Scores
    marks_obtained = Column(Numeric(5, 2), nullable=False)
    total_marks = Column(Integer, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    grade = Column(String(10), nullable=True)
    passed = Column(Boolean, default=False)
    
    # Time Tracking
    time_started = Column(DateTime, nullable=True)
    time_completed = Column(DateTime, nullable=True)
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Answers
    answers = Column(JSONB, nullable=True)  # JSON structure for answers
    
    # Evaluation
    evaluated_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    evaluated_date = Column(DateTime, nullable=True)
    evaluator_comments = Column(Text, nullable=True)
    
    # Status
    is_submitted = Column(Boolean, default=False)
    is_evaluated = Column(Boolean, default=False)
    
    # LMS Integration
    lms_result_id = Column(String(100), nullable=True)
    
    # Relationships
    assessment = relationship("TrainingAssessment", back_populates="results")
    employee = relationship("Employee", foreign_keys=[employee_id])
    evaluated_by = relationship("Employee", foreign_keys=[evaluated_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_result_assessment_emp', 'tenant_id', 'assessment_id', 'employee_id', 'attempt_number', unique=True),
        Index('idx_tenant_result_employee', 'tenant_id', 'employee_id'),
    )
    
    def __repr__(self):
        return f"<AssessmentResult(assessment_id={self.assessment_id}, employee_id={self.employee_id}, score={self.percentage}%)>"


# ============================================================================
# CERTIFICATIONS
# ============================================================================

class TrainingCertification(BaseModel):
    """
    Training Certifications
    Certificates issued to employees upon training completion
    """
    __tablename__ = "hrms_training_certifications"
    
    # Certificate Identification
    certificate_number = Column(String(100), nullable=False, index=True)
    certificate_name = Column(String(200), nullable=False)
    
    # Links
    course_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_courses.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_sessions.id", ondelete="SET NULL"), nullable=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_participants.id", ondelete="SET NULL"), nullable=True)
    
    # Certificate Details
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    
    # Status
    status = Column(SQLEnum(CertificationStatus), nullable=False, default=CertificationStatus.ISSUED)
    
    # Certificate Content
    certificate_url = Column(String(500), nullable=True)
    certificate_file_path = Column(String(500), nullable=True)
    certificate_template_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Issuing Authority
    issued_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    issuing_authority = Column(String(200), nullable=True)
    
    # Verification
    verification_code = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=True)
    
    # Renewal
    renewal_required = Column(Boolean, default=False)
    renewal_date = Column(Date, nullable=True)
    renewed_from_certificate_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_certifications.id", ondelete="SET NULL"), nullable=True)
    
    # Revocation
    revoked_date = Column(Date, nullable=True)
    revocation_reason = Column(Text, nullable=True)
    revoked_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    
    # Additional Details
    grade = Column(String(10), nullable=True)
    score_percentage = Column(Numeric(5, 2), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # LMS Integration
    lms_certificate_id = Column(String(100), nullable=True)
    
    # Relationships
    course = relationship("TrainingCourse", foreign_keys=[course_id])
    session = relationship("TrainingSession", foreign_keys=[session_id])
    employee = relationship("Employee", foreign_keys=[employee_id])
    issued_by = relationship("Employee", foreign_keys=[issued_by_id])
    revoked_by = relationship("Employee", foreign_keys=[revoked_by_id])
    renewed_from = relationship("TrainingCertification", foreign_keys=[renewed_from_certificate_id], remote_side="TrainingCertification.id")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_cert_number', 'tenant_id', 'certificate_number', unique=True),
        Index('idx_tenant_cert_employee', 'tenant_id', 'employee_id'),
        Index('idx_tenant_cert_course', 'tenant_id', 'course_id'),
        Index('idx_tenant_cert_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<TrainingCertification(number={self.certificate_number}, employee_id={self.employee_id})>"



# ============================================================================
# SKILL MATRIX
# ============================================================================

class Skill(BaseModel):
    """
    Skills Master
    Catalog of all skills/competencies
    """
    __tablename__ = "hrms_skills"
    
    # Skill Identification
    skill_code = Column(String(50), nullable=False, index=True)
    skill_name = Column(String(200), nullable=False)
    skill_description = Column(Text, nullable=True)
    
    # Category
    skill_category = Column(String(100), nullable=True)  # Technical, Soft Skills, Domain, etc.
    skill_type = Column(String(50), nullable=True)  # Hard Skill, Soft Skill, Certification, etc.
    
    # Parent Skill (for skill hierarchy)
    parent_skill_id = Column(UUID(as_uuid=True), ForeignKey("hrms_skills.id", ondelete="SET NULL"), nullable=True)
    
    # Related Training
    related_course_ids = Column(JSONB, nullable=True)  # List of training course IDs
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent_skill = relationship("Skill", remote_side="Skill.id", foreign_keys=[parent_skill_id])
    employee_skills = relationship("EmployeeSkill", back_populates="skill", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_skill_code', 'tenant_id', 'skill_code', unique=True),
        Index('idx_tenant_skill_category', 'tenant_id', 'skill_category'),
    )
    
    def __repr__(self):
        return f"<Skill(code={self.skill_code}, name={self.skill_name})>"


class EmployeeSkill(BaseModel):
    """
    Employee Skills
    Skills possessed by employees with proficiency levels
    """
    __tablename__ = "hrms_employee_skills"
    
    # Links
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("hrms_skills.id", ondelete="CASCADE"), nullable=False)
    
    # Proficiency
    proficiency_level = Column(SQLEnum(SkillLevel), nullable=False)
    proficiency_percentage = Column(Integer, nullable=True)  # 0-100
    
    # Certification/Proof
    is_certified = Column(Boolean, default=False)
    certification_name = Column(String(200), nullable=True)
    certification_date = Column(Date, nullable=True)
    certification_expiry = Column(Date, nullable=True)
    
    # Acquisition
    acquired_date = Column(Date, nullable=True)
    acquired_through = Column(String(100), nullable=True)  # Training, Self-learning, Experience
    training_course_id = Column(UUID(as_uuid=True), ForeignKey("hrms_training_courses.id", ondelete="SET NULL"), nullable=True)
    
    # Experience
    years_of_experience = Column(Numeric(5, 2), nullable=True)
    last_used_date = Column(Date, nullable=True)
    
    # Assessment
    assessed_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    assessment_date = Column(Date, nullable=True)
    assessment_score = Column(Integer, nullable=True)
    assessment_remarks = Column(Text, nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    verified_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    skill = relationship("Skill", back_populates="employee_skills")
    training_course = relationship("TrainingCourse", foreign_keys=[training_course_id])
    assessed_by = relationship("Employee", foreign_keys=[assessed_by_id])
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_emp_skill', 'tenant_id', 'employee_id', 'skill_id', unique=True),
        Index('idx_tenant_skill_employee', 'tenant_id', 'employee_id'),
        Index('idx_tenant_skill_level', 'tenant_id', 'proficiency_level'),
    )
    
    def __repr__(self):
        return f"<EmployeeSkill(employee_id={self.employee_id}, skill_id={self.skill_id}, level={self.proficiency_level})>"


# ============================================================================
# UPDATE EMPLOYEE MODEL WITH TRAINING RELATIONSHIPS
# ============================================================================

# These relationships should be added to the Employee model
# (Added via monkey patching or direct modification in hrms_models.py)
"""
Employee.training_participations = relationship("TrainingParticipant", foreign_keys="TrainingParticipant.employee_id", back_populates="employee", lazy="select")
Employee.training_certifications = relationship("TrainingCertification", foreign_keys="TrainingCertification.employee_id", back_populates="employee", lazy="select")
Employee.employee_skills = relationship("EmployeeSkill", foreign_keys="EmployeeSkill.employee_id", back_populates="employee", lazy="select")
Employee.assessment_results = relationship("AssessmentResult", foreign_keys="AssessmentResult.employee_id", back_populates="employee", lazy="select")
"""

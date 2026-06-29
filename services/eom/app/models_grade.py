import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


GRADE_STATUSES = [
    'draft',
    'hr_review',
    'finance_review',
    'executive_approval',
    'active',
]


class Grade(Base):
    __tablename__ = 'grade'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Enterprise hierarchy (EOM-010): Enterprise -> BU -> Dept -> Grade -> Designation -> Position -> Employee
    # For MVP/full coverage, we keep BU/department optional FKs so the module can be attached to enterprise structures.
    enterprise_id = Column(String(36), nullable=True)
    business_unit_id = Column(String(36), nullable=True)
    department_id = Column(String(36), nullable=True)

    # Directory columns
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    level = Column(String(64), nullable=True)  # e.g. G1/O1/M3/L1
    category = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    # Hierarchy (grade structure)
    parent_grade_id = Column(String(36), ForeignKey('grade.id'), nullable=True)

    # Career & eligibility hooks
    promotion_level = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parent = relationship('Grade', remote_side=[id], backref='children')


class GradeSalary(Base):
    __tablename__ = 'grade_salary'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    minimum_salary = Column(Float, nullable=True)
    mid_salary = Column(Float, nullable=True)
    maximum_salary = Column(Float, nullable=True)
    currency = Column(String(8), nullable=True)
    increment_policy = Column(String(256), nullable=True)
    bonus_eligibility = Column(String(256), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='salary')


class GradeBenefit(Base):
    __tablename__ = 'grade_benefit'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    medical = Column(String(256), nullable=True)
    insurance = Column(String(256), nullable=True)
    travel = Column(String(256), nullable=True)
    accommodation = Column(String(256), nullable=True)
    mobile = Column(String(256), nullable=True)
    vehicle_allowance = Column(String(256), nullable=True)
    stock_option = Column(String(256), nullable=True)
    gratuity = Column(String(256), nullable=True)

    # Additional matrix items per spec
    laptop = Column(String(256), nullable=True)
    wfh = Column(String(256), nullable=True)
    relocation = Column(String(256), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='benefit')


class GradeLeave(Base):
    __tablename__ = 'grade_leave'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    annual_leave = Column(String(256), nullable=True)
    sick_leave = Column(String(256), nullable=True)
    casual_leave = Column(String(256), nullable=True)
    maternity = Column(String(256), nullable=True)
    paternity = Column(String(256), nullable=True)
    special_leave = Column(String(256), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='leave_rules')


class GradeCompetency(Base):
    __tablename__ = 'grade_competency'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False)

    competency_type = Column(String(64), nullable=False)  # Leadership/Technical/Compliance...
    required_level = Column(String(64), nullable=True)       # Beginner/Intermediate/Advanced/Expert

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grade = relationship('Grade', backref='competencies')


class GradeTraining(Base):
    __tablename__ = 'grade_training'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False)

    training_name = Column(String(256), nullable=False)
    mandatory = Column(String(32), nullable=True, default='yes')
    required_level = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grade = relationship('Grade', backref='trainings')


class GradeApproval(Base):
    __tablename__ = 'grade_approval'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    loan_limit = Column(Float, nullable=True)
    expense_limit = Column(Float, nullable=True)
    purchase_limit = Column(Float, nullable=True)

    hr_approval = Column(String(64), nullable=True)
    finance_approval = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='approvals')


class GradeCareer(Base):
    __tablename__ = 'grade_career'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    entry = Column(String(256), nullable=True)
    promotion = Column(String(256), nullable=True)
    succession = Column(String(256), nullable=True)
    retirement = Column(String(256), nullable=True)

    # Career path as serialized sequence (e.g. "O1->O2->O3")
    career_path = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='career')


class GradeDocument(Base):
    __tablename__ = 'grade_document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False)

    document_type = Column(String(64), nullable=False)  # Policy, Salary Matrix...
    name = Column(String(256), nullable=True)
    file_reference = Column(String(256), nullable=True)
    status = Column(String(32), nullable=True, default='pending')

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grade = relationship('Grade', backref='documents')


class GradeHealth(Base):
    __tablename__ = 'grade_health'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    score = Column(Float, nullable=False, default=0)
    rating = Column(String(16), nullable=True)
    status = Column(String(32), nullable=True)  # setup-required/attention/strong etc.

    vacancies = Column(Float, nullable=True)
    training_completion_pct = Column(Float, nullable=True)
    competency_gap_pct = Column(Float, nullable=True)
    promotion_backlog_pct = Column(Float, nullable=True)
    salary_deviation_pct = Column(Float, nullable=True)
    succession_readiness_pct = Column(Float, nullable=True)

    issues = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    grade = relationship('Grade', backref='health')


class GradeAi(Base):
    __tablename__ = 'grade_ai'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grade_id = Column(String(36), ForeignKey('grade.id'), nullable=False, unique=True)

    insight_type = Column(String(64), nullable=True)  # salary_benchmark/anomaly/etc.
    insight = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    grade = relationship('Grade', backref='ai')


import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, func
from .db import Base


class DesignationCompetency(Base):
    __tablename__ = 'designation_competency'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False)
    competency_type = Column(String(64), nullable=False)
    required_level = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DesignationResponsibility(Base):
    __tablename__ = 'designation_responsibility'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False)
    responsibility_type = Column(String(32), nullable=True)  # primary/secondary
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DesignationRecruitment(Base):
    __tablename__ = 'designation_recruitment'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False, unique=True)

    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    certification = Column(Text, nullable=True)
    languages = Column(Text, nullable=True)
    mandatory_skills = Column(Text, nullable=True)
    preferred_skills = Column(Text, nullable=True)

    background_verification = Column(Text, nullable=True)
    medical_check = Column(Text, nullable=True)

    interview_panel = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    offer_workflow = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DesignationKPI(Base):
    __tablename__ = 'designation_kpi'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False)
    kpi_type = Column(String(64), nullable=True)  # business/operational/customer/financial/learning
    kpi_name = Column(String(256), nullable=True)
    target = Column(Float, nullable=True)
    unit = Column(String(64), nullable=True)
    weight = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DesignationApproval(Base):
    __tablename__ = 'designation_approval'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False, unique=True)

    loan_limit = Column(Float, nullable=True)
    expense_limit = Column(Float, nullable=True)
    purchase_limit = Column(Float, nullable=True)

    hr_approval = Column(String(64), nullable=True)
    vendor_approval = Column(String(64), nullable=True)
    travel_approval = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DesignationCareer(Base):
    __tablename__ = 'designation_career'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False, unique=True)

    entry = Column(Text, nullable=True)
    promotion = Column(Text, nullable=True)
    succession = Column(Text, nullable=True)
    retirement = Column(Text, nullable=True)

    career_path = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DesignationTraining(Base):
    __tablename__ = 'designation_training'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False)

    training_name = Column(String(256), nullable=False)
    mandatory = Column(String(32), nullable=True)
    required_level = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DesignationDocument(Base):
    __tablename__ = 'designation_document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False)

    document_type = Column(String(64), nullable=False)
    name = Column(String(256), nullable=True)
    file_reference = Column(String(256), nullable=True)
    status = Column(String(32), nullable=True, server_default='pending')

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DesignationHealth(Base):
    __tablename__ = 'designation_health'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey('designation.id'), nullable=False, unique=True)

    score = Column(Float, nullable=False, server_default='0')
    rating = Column(String(16), nullable=True)
    status = Column(String(32), nullable=True)

    vacancies = Column(Float, nullable=True, server_default='0')
    training_compliance_pct = Column(Float, nullable=True)
    competency_gap_pct = Column(Float, nullable=True)
    recruitment_time_days = Column(Float, nullable=True)
    performance_score_pct = Column(Float, nullable=True)
    succession_readiness_pct = Column(Float, nullable=True)

    issues = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


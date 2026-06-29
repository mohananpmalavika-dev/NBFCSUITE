import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Team(Base):
    __tablename__ = 'team'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    team_type = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    section_id = Column(String(36), ForeignKey('section.id'), nullable=True)
    team_lead = Column(String(128), nullable=True)
    deputy_lead = Column(String(128), nullable=True)
    reporting_manager = Column(String(128), nullable=True)
    shift = Column(String(64), nullable=True)
    capacity = Column(String(32), nullable=True)
    working_days = Column(String(128), nullable=True)
    business_calendar = Column(String(64), nullable=True)
    location = Column(String(256), nullable=True)
    primary_skills = Column(Text, nullable=True)
    secondary_skills = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    required_competencies = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    section = relationship('Section', backref='teams')


class TeamMember(Base):
    __tablename__ = 'team_member'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    employee_id = Column(String(36), nullable=False)
    employee_name = Column(String(256), nullable=True)
    role = Column(String(64), nullable=True)
    position_id = Column(String(36), nullable=True)
    join_date = Column(String(32), nullable=True)
    exit_date = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='members')


class TeamSkill(Base):
    __tablename__ = 'team_skill'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    employee_id = Column(String(36), nullable=False)
    skill_name = Column(String(128), nullable=False)
    level = Column(String(32), nullable=True)
    certification = Column(String(128), nullable=True)
    expiry_date = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='skills')


class TeamCapacity(Base):
    __tablename__ = 'team_capacity'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    total_positions = Column(Float, nullable=False, default=0)
    filled = Column(Float, nullable=False, default=0)
    vacant = Column(Float, nullable=False, default=0)
    available_capacity = Column(Float, nullable=True)
    utilization_pct = Column(Float, nullable=True)
    overtime = Column(Float, nullable=True, default=0)
    idle_pct = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='capacities')


class TeamProject(Base):
    __tablename__ = 'team_project'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    project_id = Column(String(36), nullable=False)
    project_name = Column(String(256), nullable=True)
    product = Column(String(128), nullable=True)
    process = Column(String(128), nullable=True)
    customer = Column(String(256), nullable=True)
    role = Column(String(64), nullable=True)
    start_date = Column(String(32), nullable=True)
    end_date = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='projects')


class TeamCalendar(Base):
    __tablename__ = 'team_calendar'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    calendar_type = Column(String(64), nullable=False)
    title = Column(String(256), nullable=True)
    event_date = Column(String(32), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='calendars')


class TeamAsset(Base):
    __tablename__ = 'team_asset'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    asset_type = Column(String(64), nullable=False)
    asset_name = Column(String(256), nullable=True)
    serial_number = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default='active')
    allocated_to = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='assets')


class TeamKpi(Base):
    __tablename__ = 'team_kpi'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    kpi_name = Column(String(128), nullable=False)
    target = Column(Float, nullable=True)
    actual = Column(Float, nullable=True)
    unit = Column(String(32), nullable=True)
    period = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='kpis')


class TeamHealth(Base):
    __tablename__ = 'team_health'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    score = Column(Float, nullable=False, default=0)
    rating = Column(String(16), nullable=True)
    capacity_utilization = Column(Float, nullable=True)
    productivity = Column(Float, nullable=True)
    sla_compliance = Column(Float, nullable=True)
    employee_satisfaction = Column(Float, nullable=True)
    attrition = Column(Float, nullable=True)
    training_completion = Column(Float, nullable=True)
    project_delivery = Column(Float, nullable=True)
    audit_findings = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='health_records')


class TeamAi(Base):
    __tablename__ = 'team_ai'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    insight_type = Column(String(64), nullable=False)
    insight = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='ai_insights')


class TeamDocument(Base):
    __tablename__ = 'team_document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    document_type = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    file_reference = Column(String(256), nullable=True)
    status = Column(String(32), nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='team_documents')


class TeamAudit(Base):
    __tablename__ = 'team_audit'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('team.id'), nullable=False)
    action = Column(String(64), nullable=False)
    payload = Column(Text, nullable=True)
    performed_by = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship('Team', backref='team_audit_trail')

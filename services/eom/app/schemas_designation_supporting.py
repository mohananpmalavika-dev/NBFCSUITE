from pydantic import BaseModel, Field
from typing import Optional, List


class DesignationCompetencyPayload(BaseModel):
    competency_type: str
    required_level: Optional[str] = None


class DesignationResponsibilityPayload(BaseModel):
    responsibility_type: Optional[str] = None
    description: Optional[str] = None


class DesignationRecruitmentPayload(BaseModel):
    education: Optional[str] = None
    experience: Optional[str] = None
    certification: Optional[str] = None
    languages: Optional[str] = None
    mandatory_skills: Optional[str] = None
    preferred_skills: Optional[str] = None
    background_verification: Optional[str] = None
    medical_check: Optional[str] = None

    interview_panel: Optional[str] = None
    assessment: Optional[str] = None
    offer_workflow: Optional[str] = None


class DesignationKpiPayload(BaseModel):
    kpi_type: Optional[str] = None
    kpi_name: Optional[str] = None
    target: Optional[float] = None
    unit: Optional[str] = None
    weight: Optional[float] = None


class DesignationApprovalPayload(BaseModel):
    loan_limit: Optional[float] = None
    expense_limit: Optional[float] = None
    purchase_limit: Optional[float] = None

    hr_approval: Optional[str] = None
    vendor_approval: Optional[str] = None
    travel_approval: Optional[str] = None


class DesignationCareerPayload(BaseModel):
    entry: Optional[str] = None
    promotion: Optional[str] = None
    succession: Optional[str] = None
    retirement: Optional[str] = None
    career_path: Optional[str] = None


class DesignationTrainingPayload(BaseModel):
    training_name: str
    mandatory: Optional[str] = None
    required_level: Optional[str] = None


class DesignationDocumentPayload(BaseModel):
    document_type: str
    name: Optional[str] = None
    file_reference: Optional[str] = None
    status: Optional[str] = None


class DesignationHealthResponse(BaseModel):
    score: float
    rating: Optional[str] = None
    status: Optional[str] = None
    vacancies: float
    training_compliance_pct: Optional[float] = None
    competency_gap_pct: Optional[float] = None
    recruitment_time_days: Optional[float] = None
    performance_score_pct: Optional[float] = None
    succession_readiness_pct: Optional[float] = None
    issues: List[str] = []


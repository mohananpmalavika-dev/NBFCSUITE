from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
from datetime import datetime


GradeStatus = Literal['draft', 'hr_review', 'finance_review', 'executive_approval', 'active']


class GradeSalaryPayload(BaseModel):
    minimum_salary: Optional[float] = None
    mid_salary: Optional[float] = None
    maximum_salary: Optional[float] = None
    currency: Optional[str] = None
    increment_policy: Optional[str] = None
    bonus_eligibility: Optional[str] = None


class GradeBenefitsPayload(BaseModel):
    medical: Optional[str] = None
    insurance: Optional[str] = None
    travel: Optional[str] = None
    accommodation: Optional[str] = None
    mobile: Optional[str] = None
    vehicle_allowance: Optional[str] = None
    stock_option: Optional[str] = None
    gratuity: Optional[str] = None
    laptop: Optional[str] = None
    wfh: Optional[str] = None
    relocation: Optional[str] = None


class GradeLeavePayload(BaseModel):
    annual_leave: Optional[str] = None
    sick_leave: Optional[str] = None
    casual_leave: Optional[str] = None
    maternity: Optional[str] = None
    paternity: Optional[str] = None
    special_leave: Optional[str] = None


class GradeCompetencyPayload(BaseModel):
    competency_type: str
    required_level: Optional[str] = None


class GradeTrainingPayload(BaseModel):
    training_name: str
    mandatory: Optional[str] = 'yes'
    required_level: Optional[str] = None


class GradeApprovalPayload(BaseModel):
    loan_limit: Optional[float] = None
    expense_limit: Optional[float] = None
    purchase_limit: Optional[float] = None
    hr_approval: Optional[str] = None
    finance_approval: Optional[str] = None


class GradeCareerPayload(BaseModel):
    entry: Optional[str] = None
    promotion: Optional[str] = None
    succession: Optional[str] = None
    retirement: Optional[str] = None
    career_path: Optional[str] = None


class GradeDocumentPayload(BaseModel):
    document_type: str
    name: Optional[str] = None
    file_reference: Optional[str] = None
    status: Optional[str] = 'pending'


class GradeCreatePayload(BaseModel):
    enterprise_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    department_id: Optional[str] = None

    code: str = Field(..., min_length=2)
    name: str
    level: Optional[str] = None
    category: Optional[str] = None
    status: Optional[GradeStatus] = 'draft'
    description: Optional[str] = None


class GradeUpdatePayload(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    status: Optional[GradeStatus] = None
    description: Optional[str] = None


class GradeResponse(BaseModel):
    id: str
    enterprise_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    department_id: Optional[str] = None

    code: str
    name: str
    level: Optional[str] = None
    category: Optional[str] = None
    status: GradeStatus
    description: Optional[str] = None

    promotion_level: Optional[str] = None
    parent_grade_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class GradeListResponse(BaseModel):
    total: int
    items: List[GradeResponse]


class GradeSalaryResponse(BaseModel):
    minimum_salary: Optional[float] = None
    mid_salary: Optional[float] = None
    maximum_salary: Optional[float] = None
    currency: Optional[str] = None
    increment_policy: Optional[str] = None
    bonus_eligibility: Optional[str] = None


class GradeBenefitsResponse(GradeBenefitsPayload):
    pass


class GradeLeaveResponse(GradeLeavePayload):
    pass


class GradeCompetencyResponse(BaseModel):
    competency_type: str
    required_level: Optional[str] = None


class GradeTrainingResponse(BaseModel):
    training_name: str
    mandatory: Optional[str] = None
    required_level: Optional[str] = None


class GradeApprovalResponse(GradeApprovalPayload):
    pass


class GradeCareerResponse(GradeCareerPayload):
    pass


class GradeDocumentResponse(BaseModel):
    id: Optional[str] = None
    document_type: str
    name: Optional[str] = None
    file_reference: Optional[str] = None
    status: Optional[str] = None


class GradeHealthResponse(BaseModel):
    score: float
    rating: Optional[str] = None
    status: Optional[str] = None

    vacancies: Optional[float] = None
    training_completion_pct: Optional[float] = None
    competency_gap_pct: Optional[float] = None
    promotion_backlog_pct: Optional[float] = None
    salary_deviation_pct: Optional[float] = None
    succession_readiness_pct: Optional[float] = None

    issues: List[str] = Field(default_factory=list)


class GradeTimelineItem(BaseModel):
    when: Optional[str] = None
    event: str
    payload: Any = None


class GradeAiInsight(BaseModel):
    insight_type: Optional[str] = None
    insight: Optional[str] = None
    recommendation: Optional[str] = None
    score: Optional[float] = None


class GradeProfilePayload(BaseModel):
    general: Optional[GradeUpdatePayload] = None
    salary: Optional[GradeSalaryPayload] = None
    benefits: Optional[GradeBenefitsPayload] = None
    leave: Optional[GradeLeavePayload] = None
    competencies: Optional[List[GradeCompetencyPayload]] = None
    training: Optional[List[GradeTrainingPayload]] = None
    approvals: Optional[GradeApprovalPayload] = None
    career: Optional[GradeCareerPayload] = None
    documents: Optional[List[GradeDocumentPayload]] = None


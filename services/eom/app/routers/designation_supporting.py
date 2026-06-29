from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db import SessionLocal
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event

from .. import models
from .. import models_designation
from .. import models_designation_supporting as ms
from ..schemas_designation_supporting import (
    DesignationCompetencyPayload,
    DesignationResponsibilityPayload,
    DesignationRecruitmentPayload,
    DesignationKpiPayload,
    DesignationApprovalPayload,
    DesignationCareerPayload,
    DesignationTrainingPayload,
    DesignationDocumentPayload,
    DesignationHealthResponse,
)

import json
from sqlalchemy import func


router = APIRouter(prefix="/eom", tags=["designation-supporting"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _designation_or_404(db: Session, designation_id: str) -> models_designation.Designation:
    d = db.query(models_designation.Designation).filter(models_designation.Designation.id == designation_id).first()
    if not d:
        raise HTTPException(status_code=404, detail='Designation not found')
    return d


def _rating_from_score(score: float) -> str:
    if score >= 90:
        return '★★★★★'
    if score >= 75:
        return '★★★★☆'
    if score >= 60:
        return '★★★☆☆'
    if score >= 45:
        return '★★☆☆☆'
    return '★☆☆☆☆'


def _status_from_score(score: float) -> str:
    return 'strong' if score >= 85 else 'attention' if score >= 60 else 'setup-required'


def compute_designation_health(db: Session, designation_id: str) -> dict:
    competencies_n = db.query(func.count(ms.DesignationCompetency.id)).filter(ms.DesignationCompetency.designation_id == designation_id).scalar() or 0
    trainings_n = db.query(func.count(ms.DesignationTraining.id)).filter(ms.DesignationTraining.designation_id == designation_id).scalar() or 0

    approvals = db.query(ms.DesignationApproval).filter(ms.DesignationApproval.designation_id == designation_id).first()
    career = db.query(ms.DesignationCareer).filter(ms.DesignationCareer.designation_id == designation_id).first()
    recruitment = db.query(ms.DesignationRecruitment).filter(ms.DesignationRecruitment.designation_id == designation_id).first()
    kpis_n = db.query(func.count(ms.DesignationKPI.id)).filter(ms.DesignationKPI.designation_id == designation_id).scalar() or 0

    training_completion_pct = min(100.0, float(trainings_n) * 15.0) if trainings_n else 0.0
    competency_gap_pct = max(0.0, 100.0 - min(100.0, float(competencies_n) * 20.0)) if competencies_n else 100.0

    # Simplified placeholders based on existence
    recruitment_time_days = 0.0 if recruitment else 30.0
    performance_score_pct = 0.0 if kpis_n < 3 else 85.0
    promotion_backlog_pct = 100.0 if (career is None or not career.promotion) else 25.0
    succession_readiness_pct = 0.0 if (career is None or not career.succession) else 80.0
    vacancies = 0.0

    weights = {
        'training': 0.25,
        'competency': 0.25,
        'promotion': 0.20,
        'kpi': 0.15,
        'succession': 0.15,
    }

    training_component = training_completion_pct
    competency_component = 100.0 - competency_gap_pct
    promotion_component = 100.0 - promotion_backlog_pct
    kpi_component = performance_score_pct
    succession_component = succession_readiness_pct

    score = round(
        training_component * weights['training']
        + competency_component * weights['competency']
        + promotion_component * weights['promotion']
        + kpi_component * weights['kpi']
        + succession_component * weights['succession'],
        2,
    )

    rating = _rating_from_score(score)
    status_label = _status_from_score(score)

    issues: List[str] = []
    if competencies_n < 3:
        issues.append('Competency framework incomplete')
    if trainings_n < 2:
        issues.append('Training requirements incomplete')
    if approvals is None:
        issues.append('Approval authority not configured')
    if career is None or not career.career_path:
        issues.append('Career path not configured')
    if recruitment is None:
        issues.append('Recruitment template not configured')
    if kpis_n < 3:
        issues.append('KPI set incomplete')

    row = db.query(ms.DesignationHealth).filter(ms.DesignationHealth.designation_id == designation_id).first()
    if row is None:
        row = ms.DesignationHealth(designation_id=designation_id)

    row.score = score
    row.rating = rating
    row.status = status_label
    row.vacancies = vacancies
    row.training_compliance_pct = training_completion_pct
    row.competency_gap_pct = competency_gap_pct
    row.recruitment_time_days = recruitment_time_days
    row.performance_score_pct = performance_score_pct
    row.succession_readiness_pct = succession_readiness_pct
    row.issues = json.dumps(issues)

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        'score': row.score,
        'rating': row.rating,
        'status': row.status,
        'vacancies': row.vacancies,
        'training_compliance_pct': row.training_compliance_pct,
        'competency_gap_pct': row.competency_gap_pct,
        'recruitment_time_days': row.recruitment_time_days,
        'performance_score_pct': row.performance_score_pct,
        'succession_readiness_pct': row.succession_readiness_pct,
        'issues': issues,
    }


@router.get('/designations/{id}/competencies')
def get_competencies(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    rows = db.query(ms.DesignationCompetency).filter(ms.DesignationCompetency.designation_id == id).all()
    return [{
        'competency_type': r.competency_type,
        'required_level': r.required_level,
    } for r in rows]


@router.put('/designations/{id}/competencies')
def set_competencies(
    id: str,
    payload: List[DesignationCompetencyPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    db.query(ms.DesignationCompetency).filter(ms.DesignationCompetency.designation_id == id).delete()
    rows = [ms.DesignationCompetency(designation_id=id, competency_type=p.competency_type, required_level=p.required_level) for p in payload]
    db.add_all(rows)
    db.commit()

    compute_designation_health(db, id)
    try:
        record_audit(db, 'designation', id, 'competencies_updated', [p.model_dump() for p in payload])
    except Exception:
        pass
    try:
        publish_event('COMPETENCY_UPDATED', {'id': id})
    except Exception:
        pass

    return rows


@router.get('/designations/{id}/career')
def get_career(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationCareer).filter(ms.DesignationCareer.designation_id == id).first()
    return row or {}


@router.put('/designations/{id}/career')
def set_career(
    id: str,
    payload: DesignationCareerPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationCareer).filter(ms.DesignationCareer.designation_id == id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = ms.DesignationCareer(designation_id=id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_designation_health(db, id)
    try:
        record_audit(db, 'designation', id, 'career_path_updated', data)
    except Exception:
        pass
    try:
        publish_event('CAREER_PATH_UPDATED', {'id': id})
    except Exception:
        pass
    return row


@router.get('/designations/{id}/health', response_model=DesignationHealthResponse)
def get_health(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    existing = db.query(ms.DesignationHealth).filter(ms.DesignationHealth.designation_id == id).first()
    if existing is None:
        return compute_designation_health(db, id)

    try:
        issues = json.loads(existing.issues) if existing.issues else []
    except Exception:
        issues = []

    return {
        'score': existing.score,
        'rating': existing.rating,
        'status': existing.status,
        'vacancies': existing.vacancies,
        'training_compliance_pct': existing.training_compliance_pct,
        'competency_gap_pct': existing.competency_gap_pct,
        'recruitment_time_days': existing.recruitment_time_days,
        'performance_score_pct': existing.performance_score_pct,
        'succession_readiness_pct': existing.succession_readiness_pct,
        'issues': issues,
    }


# MVP additional wiring endpoints (basic delete+replace semantics) 
# Responsibilities


@router.get('/designations/{id}/responsibilities')
def get_responsibilities(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    rows = db.query(ms.DesignationResponsibility).filter(ms.DesignationResponsibility.designation_id == id).all()
    return [{'responsibility_type': r.responsibility_type, 'description': r.description} for r in rows]


@router.put('/designations/{id}/responsibilities')
def set_responsibilities(
    id: str,
    payload: List[DesignationResponsibilityPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    db.query(ms.DesignationResponsibility).filter(ms.DesignationResponsibility.designation_id == id).delete()
    rows = [ms.DesignationResponsibility(designation_id=id, responsibility_type=p.responsibility_type, description=p.description) for p in payload]
    db.add_all(rows)
    db.commit()
    compute_designation_health(db, id)
    return rows


# Recruitment (one-to-one)
@router.put('/designations/{id}/recruitment')
def set_recruitment(
    id: str,
    payload: DesignationRecruitmentPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationRecruitment).filter(ms.DesignationRecruitment.designation_id == id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = ms.DesignationRecruitment(designation_id=id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_designation_health(db, id)
    return row


@router.get('/designations/{id}/recruitment')
def get_recruitment(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationRecruitment).filter(ms.DesignationRecruitment.designation_id == id).first()
    return row or {}


# KPIs (many)
@router.put('/designations/{id}/kpis')
def set_kpis(
    id: str,
    payload: List[DesignationKpiPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    db.query(ms.DesignationKPI).filter(ms.DesignationKPI.designation_id == id).delete()
    rows = [
        ms.DesignationKPI(
            designation_id=id,
            kpi_type=p.kpi_type,
            kpi_name=p.kpi_name,
            target=p.target,
            unit=p.unit,
            weight=p.weight,
        )
        for p in payload
    ]
    db.add_all(rows)
    db.commit()
    compute_designation_health(db, id)
    return rows


@router.get('/designations/{id}/kpis')
def get_kpis(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    rows = db.query(ms.DesignationKPI).filter(ms.DesignationKPI.designation_id == id).all()
    return [
        {
            'kpi_type': r.kpi_type,
            'kpi_name': r.kpi_name,
            'target': r.target,
            'unit': r.unit,
            'weight': r.weight,
        }
        for r in rows
    ]


# Approvals (one-to-one)
@router.put('/designations/{id}/approvals')
def set_approvals(
    id: str,
    payload: DesignationApprovalPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationApproval).filter(ms.DesignationApproval.designation_id == id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = ms.DesignationApproval(designation_id=id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_designation_health(db, id)
    return row


@router.get('/designations/{id}/approvals')
def get_approvals(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    row = db.query(ms.DesignationApproval).filter(ms.DesignationApproval.designation_id == id).first()
    return row or {}


# Training (many)
@router.put('/designations/{id}/training')
def set_training(
    id: str,
    payload: List[DesignationTrainingPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    db.query(ms.DesignationTraining).filter(ms.DesignationTraining.designation_id == id).delete()
    rows = [
        ms.DesignationTraining(
            designation_id=id,
            training_name=p.training_name,
            mandatory=p.mandatory,
            required_level=p.required_level,
        )
        for p in payload
    ]
    db.add_all(rows)
    db.commit()
    compute_designation_health(db, id)
    return rows


@router.get('/designations/{id}/training')
def get_training(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    rows = db.query(ms.DesignationTraining).filter(ms.DesignationTraining.designation_id == id).all()
    return [
        {
            'training_name': r.training_name,
            'mandatory': r.mandatory,
            'required_level': r.required_level,
        }
        for r in rows
    ]


# Documents (many)
@router.put('/designations/{id}/documents')
def set_documents(
    id: str,
    payload: List[DesignationDocumentPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    _designation_or_404(db, id)
    db.query(ms.DesignationDocument).filter(ms.DesignationDocument.designation_id == id).delete()
    rows = [
        ms.DesignationDocument(
            designation_id=id,
            document_type=p.document_type,
            name=p.name,
            file_reference=p.file_reference,
            status=p.status,
        )
        for p in payload
    ]
    db.add_all(rows)
    db.commit()
    compute_designation_health(db, id)
    return rows


@router.get('/designations/{id}/documents')
def get_documents(id: str, db: Session = Depends(get_db)):
    _designation_or_404(db, id)
    rows = db.query(ms.DesignationDocument).filter(ms.DesignationDocument.designation_id == id).all()
    return [
        {
            'id': r.id,
            'document_type': r.document_type,
            'name': r.name,
            'file_reference': r.file_reference,
            'status': r.status,
        }
        for r in rows
    ]


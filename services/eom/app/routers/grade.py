import os
import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import SessionLocal, engine
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event
from .. import models, models_enterprise_master

from .. import models_grade
from .. import schemas_grade


router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _grade_or_404(db: Session, id: str):
    g = db.query(models_grade.Grade).filter(models_grade.Grade.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail='Grade not found')
    return g


def _count_rows(db: Session, selectable):
    try:
        return db.query(selectable).count()
    except Exception:
        return 0


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


def compute_grade_health(db: Session, grade_id: str):
    # Deterministic score based on what we have; remaining metrics default to conservative assumptions.
    salary = db.query(models_grade.GradeSalary).filter(models_grade.GradeSalary.grade_id == grade_id).first()
    benefit = db.query(models_grade.GradeBenefit).filter(models_grade.GradeBenefit.grade_id == grade_id).first()
    leave = db.query(models_grade.GradeLeave).filter(models_grade.GradeLeave.grade_id == grade_id).first()
    competencies_n = db.query(func.count(models_grade.GradeCompetency.id)).filter(models_grade.GradeCompetency.grade_id == grade_id).scalar() or 0
    trainings_n = db.query(func.count(models_grade.GradeTraining.id)).filter(models_grade.GradeTraining.grade_id == grade_id).scalar() or 0
    approvals = db.query(models_grade.GradeApproval).filter(models_grade.GradeApproval.grade_id == grade_id).first()
    career = db.query(models_grade.GradeCareer).filter(models_grade.GradeCareer.grade_id == grade_id).first()

    # Convert existence checks into pct-based metrics.
    vacancies = 0.0
    training_completion_pct = min(100.0, float(trainings_n) * 15.0) if trainings_n else 0.0
    competency_gap_pct = max(0.0, 100.0 - min(100.0, float(competencies_n) * 20.0)) if competencies_n else 100.0
    promotion_backlog_pct = 100.0 if (career is None or not career.promotion) else 20.0
    salary_deviation_pct = 50.0 if salary is None else 10.0
    succession_readiness_pct = 0.0 if (career is None or not career.succession) else 80.0

    # Score composition
    weights = {
        'training': 0.25,
        'competency': 0.25,
        'promotion': 0.20,
        'salary': 0.15,
        'succession': 0.15,
    }

    training_component = training_completion_pct
    competency_component = 100.0 - competency_gap_pct
    promotion_component = 100.0 - promotion_backlog_pct
    salary_component = 100.0 - salary_deviation_pct
    succession_component = succession_readiness_pct

    score = round(
        training_component * weights['training']
        + competency_component * weights['competency']
        + promotion_component * weights['promotion']
        + salary_component * weights['salary']
        + succession_component * weights['succession'],
        2,
    )

    rating = _rating_from_score(score)
    status_label = _status_from_score(score)

    issues: List[str] = []
    if salary is None:
        issues.append('Salary band not configured')
    if benefit is None:
        issues.append('Benefits matrix not configured')
    if leave is None:
        issues.append('Leave rules not configured')
    if competencies_n < 3:
        issues.append('Competency framework incomplete')
    if trainings_n < 2:
        issues.append('Training requirements incomplete')
    if approvals is None:
        issues.append('Approval authority not configured')
    if career is None or not career.career_path:
        issues.append('Career path not configured')

    row = db.query(models_grade.GradeHealth).filter(models_grade.GradeHealth.grade_id == grade_id).first()
    if row is None:
        row = models_grade.GradeHealth(grade_id=grade_id)

    row.score = score
    row.rating = rating
    row.status = status_label
    row.vacancies = vacancies
    row.training_completion_pct = training_completion_pct
    row.competency_gap_pct = competency_gap_pct
    row.promotion_backlog_pct = promotion_backlog_pct
    row.salary_deviation_pct = salary_deviation_pct
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
        'training_completion_pct': row.training_completion_pct,
        'competency_gap_pct': row.competency_gap_pct,
        'promotion_backlog_pct': row.promotion_backlog_pct,
        'salary_deviation_pct': row.salary_deviation_pct,
        'succession_readiness_pct': row.succession_readiness_pct,
        'issues': issues,
    }


@router.get('/grades')
def list_grades(
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models_grade.Grade)
    if q:
        like = f"%{q}%"
        query = query.filter((models_grade.Grade.name.ilike(like)) | (models_grade.Grade.code.ilike(like)) | (models_grade.Grade.level.ilike(like)))
    if status:
        query = query.filter(models_grade.Grade.status == status)

    total = query.count()
    items = query.order_by(models_grade.Grade.created_at.desc()).limit(limit).offset(offset).all()

    return {
        'total': total,
        'items': [
            schemas_grade.GradeResponse(
                id=g.id,
                enterprise_id=g.enterprise_id,
                business_unit_id=g.business_unit_id,
                department_id=g.department_id,
                code=g.code,
                name=g.name,
                level=g.level,
                category=g.category,
                status=g.status,
                description=g.description,
                promotion_level=g.promotion_level,
                parent_grade_id=g.parent_grade_id,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
            for g in items
        ],
    }


@router.post('/grades', response_model=schemas_grade.GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(payload: schemas_grade.GradeCreatePayload, db: Session = Depends(get_db)):
    existing = db.query(models_grade.Grade).filter(models_grade.Grade.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Grade code already exists')

    g = models_grade.Grade(
        enterprise_id=payload.enterprise_id,
        business_unit_id=payload.business_unit_id,
        department_id=payload.department_id,
        code=payload.code,
        name=payload.name,
        level=payload.level,
        category=payload.category,
        status=payload.status,
        description=payload.description,
    )

    db.add(g)
    db.commit()
    db.refresh(g)

    try:
        record_audit(db, 'grade', g.id, 'created', {'code': g.code, 'name': g.name})
    except Exception:
        pass
    try:
        publish_event('GRADE_CREATED', {'id': g.id, 'code': g.code, 'name': g.name})
    except Exception:
        pass

    # Create baseline health row
    compute_grade_health(db, g.id)

    return g


@router.get('/grades/{id}', response_model=schemas_grade.GradeResponse)
def get_grade(id: str, db: Session = Depends(get_db)):
    return _grade_or_404(db, id)


@router.put('/grades/{id}', response_model=schemas_grade.GradeResponse)
def update_grade(
    id: str,
    payload: schemas_grade.GradeUpdatePayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(g, field, value)

    db.add(g)
    db.commit()
    db.refresh(g)

    try:
        record_audit(db, 'grade', g.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass

    try:
        publish_event('GRADE_UPDATED', {'id': g.id})
    except Exception:
        pass

    compute_grade_health(db, g.id)

    return g


_ALLOWED_STATUS_TRANSITIONS = {
    'draft': ['hr_review'],
    'hr_review': ['finance_review'],
    'finance_review': ['executive_approval'],
    'executive_approval': ['active'],
    'active': [],
}


@router.patch('/grades/{id}/status')
def set_grade_status(
    id: str,
    status_body: dict,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    if new_status not in schemas_grade.GradeStatus.__args__:  # type: ignore
        raise HTTPException(status_code=400, detail='Invalid status')

    allowed = _ALLOWED_STATUS_TRANSITIONS.get(g.status, [])
    if new_status not in allowed and new_status != g.status:
        raise HTTPException(status_code=400, detail=f'Invalid status transition from {g.status} to {new_status}')

    g.status = new_status
    db.add(g)
    db.commit()
    db.refresh(g)

    try:
        record_audit(db, 'grade', g.id, 'status_changed', {'status': new_status})
    except Exception:
        pass

    event = 'GRADE_ACTIVATED' if new_status == 'active' else 'GRADE_UPDATED'
    try:
        publish_event(event, {'id': g.id, 'status': new_status})
    except Exception:
        pass

    compute_grade_health(db, g.id)

    return {'id': g.id, 'status': g.status}


# ---- Tab section endpoints ----

def _replace_one_to_one(model, grade_id: str, payload: dict, unique_grade_fk: str = 'grade_id'):
    # Note: This helper is used only inside this module.
    def _apply(db: Session):
        row = db.query(model).filter(getattr(model, unique_grade_fk) == grade_id).first()
        if row is None:
            row = model(**{unique_grade_fk: grade_id})
        for k, v in payload.items():
            if hasattr(row, k):
                setattr(row, k, v)
        db.add(row)
        return row

    return _apply


@router.put('/grades/{id}/salary')
def update_salary(
    id: str,
    payload: schemas_grade.GradeSalaryPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeSalary).filter(models_grade.GradeSalary.grade_id == g.id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = models_grade.GradeSalary(grade_id=g.id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_grade_health(db, g.id)

    try:
        record_audit(db, 'grade', g.id, 'salary_updated', data)
    except Exception:
        pass
    try:
        publish_event('SALARY_BAND_UPDATED', {'id': g.id})
    except Exception:
        pass

    return row


@router.get('/grades/{id}/salary')
def get_salary(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeSalary).filter(models_grade.GradeSalary.grade_id == g.id).first()
    return row or {}


@router.put('/grades/{id}/benefits')
def update_benefits(
    id: str,
    payload: schemas_grade.GradeBenefitsPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeBenefit).filter(models_grade.GradeBenefit.grade_id == g.id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = models_grade.GradeBenefit(grade_id=g.id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_grade_health(db, g.id)

    try:
        record_audit(db, 'grade', g.id, 'benefits_updated', data)
    except Exception:
        pass
    try:
        publish_event('BENEFITS_UPDATED', {'id': g.id})
    except Exception:
        pass

    return row


@router.get('/grades/{id}/benefits')
def get_benefits(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeBenefit).filter(models_grade.GradeBenefit.grade_id == g.id).first()
    return row or {}


@router.put('/grades/{id}/leave')
def update_leave(
    id: str,
    payload: schemas_grade.GradeLeavePayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeLeave).filter(models_grade.GradeLeave.grade_id == g.id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = models_grade.GradeLeave(grade_id=g.id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'leave_updated', data)
    except Exception:
        pass
    return row


@router.get('/grades/{id}/leave')
def get_leave(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeLeave).filter(models_grade.GradeLeave.grade_id == g.id).first()
    return row or {}


@router.put('/grades/{id}/competencies')
def set_competencies(
    id: str,
    payload: List[schemas_grade.GradeCompetencyPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    db.query(models_grade.GradeCompetency).filter(models_grade.GradeCompetency.grade_id == g.id).delete()
    rows = []
    for item in payload:
        rows.append(models_grade.GradeCompetency(grade_id=g.id, competency_type=item.competency_type, required_level=item.required_level))
    db.add_all(rows)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'competencies_updated', [p.model_dump() for p in payload])
    except Exception:
        pass
    return rows


@router.get('/grades/{id}/competencies')
def get_competencies(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    rows = db.query(models_grade.GradeCompetency).filter(models_grade.GradeCompetency.grade_id == g.id).all()
    return [
        {'competency_type': r.competency_type, 'required_level': r.required_level}
        for r in rows
    ]


@router.put('/grades/{id}/training')
def set_training(
    id: str,
    payload: List[schemas_grade.GradeTrainingPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    db.query(models_grade.GradeTraining).filter(models_grade.GradeTraining.grade_id == g.id).delete()
    rows = []
    for item in payload:
        rows.append(models_grade.GradeTraining(grade_id=g.id, training_name=item.training_name, mandatory=item.mandatory, required_level=item.required_level))
    db.add_all(rows)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'training_updated', [p.model_dump() for p in payload])
    except Exception:
        pass
    return rows


@router.get('/grades/{id}/training')
def get_training(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    rows = db.query(models_grade.GradeTraining).filter(models_grade.GradeTraining.grade_id == g.id).all()
    return [
        {'training_name': r.training_name, 'mandatory': r.mandatory, 'required_level': r.required_level}
        for r in rows
    ]


@router.put('/grades/{id}/approvals')
def set_approvals(
    id: str,
    payload: schemas_grade.GradeApprovalPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeApproval).filter(models_grade.GradeApproval.grade_id == g.id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = models_grade.GradeApproval(grade_id=g.id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'approvals_updated', data)
    except Exception:
        pass
    return row


@router.get('/grades/{id}/approvals')
def get_approvals(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeApproval).filter(models_grade.GradeApproval.grade_id == g.id).first()
    return row or {}


@router.put('/grades/{id}/career')
def set_career(
    id: str,
    payload: schemas_grade.GradeCareerPayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeCareer).filter(models_grade.GradeCareer.grade_id == g.id).first()
    data = payload.model_dump(exclude_unset=True)
    if row is None:
        row = models_grade.GradeCareer(grade_id=g.id)
    for k, v in data.items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'career_updated', data)
    except Exception:
        pass
    try:
        publish_event('CAREER_PATH_UPDATED', {'id': g.id})
    except Exception:
        pass
    return row


@router.get('/grades/{id}/career')
def get_career(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeCareer).filter(models_grade.GradeCareer.grade_id == g.id).first()
    return row or {}


@router.put('/grades/{id}/documents')
def set_documents(
    id: str,
    payload: List[schemas_grade.GradeDocumentPayload],
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)
    db.query(models_grade.GradeDocument).filter(models_grade.GradeDocument.grade_id == g.id).delete()

    rows = []
    for item in payload:
        rows.append(
            models_grade.GradeDocument(
                grade_id=g.id,
                document_type=item.document_type,
                name=item.name,
                file_reference=item.file_reference,
                status=item.status,
            )
        )
    db.add_all(rows)
    db.commit()
    compute_grade_health(db, g.id)
    try:
        record_audit(db, 'grade', g.id, 'documents_updated', [p.model_dump() for p in payload])
    except Exception:
        pass
    return rows


@router.get('/grades/{id}/documents')
def get_documents(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    rows = db.query(models_grade.GradeDocument).filter(models_grade.GradeDocument.grade_id == g.id).all()
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


@router.get('/grades/{id}/health', response_model=schemas_grade.GradeHealthResponse)
def get_health(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    existing = db.query(models_grade.GradeHealth).filter(models_grade.GradeHealth.grade_id == g.id).first()
    if existing is None:
        computed = compute_grade_health(db, g.id)
        return computed

    try:
        issues = json.loads(existing.issues) if existing.issues else []
    except Exception:
        issues = []

    return {
        'score': existing.score,
        'rating': existing.rating,
        'status': existing.status,
        'vacancies': existing.vacancies,
        'training_completion_pct': existing.training_completion_pct,
        'competency_gap_pct': existing.competency_gap_pct,
        'promotion_backlog_pct': existing.promotion_backlog_pct,
        'salary_deviation_pct': existing.salary_deviation_pct,
        'succession_readiness_pct': existing.succession_readiness_pct,
        'issues': issues,
    }


@router.get('/grades/{id}/timeline')
def get_timeline(id: str):
    out = []
    log = os.path.join(os.path.dirname(__file__), '..', '..', 'var', 'events.log')
    try:
        with open(log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get('payload', {}).get('id') == id:
                        out.append({'when': r.get('ts'), 'event': r.get('type'), 'payload': r.get('payload')})
                except Exception:
                    continue
    except Exception:
        pass
    return out


@router.get('/grades/{id}/audit')
def get_audit(id: str, db: Session = Depends(get_db)):
    _grade_or_404(db, id)
    entries = (
        db.query(models.AuditEntry)
        .filter(models.AuditEntry.entity_type == 'grade', models.AuditEntry.entity_id == id)
        .order_by(models.AuditEntry.created_at.desc())
        .limit(100)
        .all()
    )

    return {
        'total': len(entries),
        'items': [
            {
                'id': item.id,
                'action': item.action,
                'payload': item.payload,
                'created_at': item.created_at,
            }
            for item in entries
        ],
    }


@router.get('/grades/{id}/ai')
def get_ai(id: str, db: Session = Depends(get_db)):
    g = _grade_or_404(db, id)
    row = db.query(models_grade.GradeAi).filter(models_grade.GradeAi.grade_id == g.id).first()
    if not row:
        return {}
    return {
        'insight_type': row.insight_type,
        'insight': row.insight,
        'recommendation': row.recommendation,
        'score': row.score,
    }


@router.put('/grades/{id}/profile')
def upsert_full_profile(
    id: str,
    payload: schemas_grade.GradeProfilePayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    g = _grade_or_404(db, id)

    if payload.general:
        data = payload.general.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(g, k, v)
        db.add(g)

    if payload.salary:
        row = db.query(models_grade.GradeSalary).filter(models_grade.GradeSalary.grade_id == g.id).first()
        if row is None:
            row = models_grade.GradeSalary(grade_id=g.id)
        for k, v in payload.salary.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        db.add(row)

    if payload.benefits:
        row = db.query(models_grade.GradeBenefit).filter(models_grade.GradeBenefit.grade_id == g.id).first()
        if row is None:
            row = models_grade.GradeBenefit(grade_id=g.id)
        for k, v in payload.benefits.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        db.add(row)

    if payload.leave:
        row = db.query(models_grade.GradeLeave).filter(models_grade.GradeLeave.grade_id == g.id).first()
        if row is None:
            row = models_grade.GradeLeave(grade_id=g.id)
        for k, v in payload.leave.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        db.add(row)

    if payload.competencies is not None:
        db.query(models_grade.GradeCompetency).filter(models_grade.GradeCompetency.grade_id == g.id).delete()
        for item in payload.competencies:
            db.add(models_grade.GradeCompetency(grade_id=g.id, competency_type=item.competency_type, required_level=item.required_level))

    if payload.training is not None:
        db.query(models_grade.GradeTraining).filter(models_grade.GradeTraining.grade_id == g.id).delete()
        for item in payload.training:
            db.add(models_grade.GradeTraining(grade_id=g.id, training_name=item.training_name, mandatory=item.mandatory, required_level=item.required_level))

    if payload.approvals:
        row = db.query(models_grade.GradeApproval).filter(models_grade.GradeApproval.grade_id == g.id).first()
        if row is None:
            row = models_grade.GradeApproval(grade_id=g.id)
        for k, v in payload.approvals.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        db.add(row)

    if payload.career:
        row = db.query(models_grade.GradeCareer).filter(models_grade.GradeCareer.grade_id == g.id).first()
        if row is None:
            row = models_grade.GradeCareer(grade_id=g.id)
        for k, v in payload.career.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        db.add(row)

    if payload.documents is not None:
        db.query(models_grade.GradeDocument).filter(models_grade.GradeDocument.grade_id == g.id).delete()
        for item in payload.documents:
            db.add(
                models_grade.GradeDocument(
                    grade_id=g.id,
                    document_type=item.document_type,
                    name=item.name,
                    file_reference=item.file_reference,
                    status=item.status,
                )
            )

    db.commit()

    compute_grade_health(db, g.id)

    try:
        record_audit(db, 'grade', g.id, 'profile_updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass

    try:
        publish_event('GRADE_UPDATED', {'id': g.id})
    except Exception:
        pass

    return {'id': g.id, 'status': g.status}


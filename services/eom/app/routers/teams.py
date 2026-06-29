from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..db import SessionLocal
from .. import models_team
from ..schemas_team import (
    TeamCreate, TeamResponse, TeamUpdate, TeamListResponse,
    TeamCapacityResponse, TeamWorkloadResponse, TeamHealthScoreResponse,
)
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_team(db: Session, team_id: str):
    team = db.query(models_team.Team).filter(models_team.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    return team


@router.post('/teams', response_model=TeamResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    existing = db.query(models_team.Team).filter(models_team.Team.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Team code already exists')

    if payload.section_id:
        from .. import models_section
        section = db.query(models_section.Section).filter(models_section.Section.id == payload.section_id).first()
        if not section:
            raise HTTPException(status_code=404, detail='Section not found')

    team = models_team.Team(**payload.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    try:
        record_audit(db, 'team', team.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('TEAM_CREATED', {'id': team.id, 'code': team.code, 'name': team.name})
    return team


@router.get('/teams', response_model=TeamListResponse)
def list_teams(q: Optional[str] = None, status: Optional[str] = None, section_id: Optional[str] = None, team_type: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_team.Team)
    if q:
        like = f"%{q}%"
        query = query.filter((models_team.Team.name.ilike(like)) | (models_team.Team.code.ilike(like)))
    if status:
        query = query.filter(models_team.Team.status == status)
    if section_id:
        query = query.filter(models_team.Team.section_id == section_id)
    if team_type:
        query = query.filter(models_team.Team.team_type == team_type)
    total = query.count()
    items = query.order_by(models_team.Team.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/teams/{team_id}', response_model=TeamResponse)
def get_team_endpoint(team_id: str, db: Session = Depends(get_db)):
    return get_team(db, team_id)


@router.put('/teams/{team_id}', response_model=TeamResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_team(team_id: str, payload: TeamUpdate, db: Session = Depends(get_db)):
    team = get_team(db, team_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    db.add(team)
    db.commit()
    db.refresh(team)
    try:
        record_audit(db, 'team', team.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('TEAM_UPDATED', {'id': team.id})
    return team


@router.patch('/teams/{team_id}/status', response_model=TeamResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_team_status(team_id: str, status_body: dict, db: Session = Depends(get_db)):
    team = get_team(db, team_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    team.status = new_status
    db.add(team)
    db.commit()
    db.refresh(team)
    try:
        record_audit(db, 'team', team.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('TEAM_STATUS_CHANGED', {'id': team.id, 'status': new_status})
    return team


@router.get('/teams/{team_id}/capacity', response_model=TeamCapacityResponse)
def team_capacity(team_id: str, db: Session = Depends(get_db)):
    team = get_team(db, team_id)
    cap = db.query(models_team.TeamCapacity).filter(models_team.TeamCapacity.team_id == team_id).order_by(models_team.TeamCapacity.recorded_at.desc()).first()
    if cap:
        return {
            'total_positions': int(cap.total_positions),
            'filled': int(cap.filled),
            'vacant': int(cap.vacant),
            'available_capacity': cap.available_capacity or 0,
            'utilization_pct': cap.utilization_pct or 0,
            'overtime': cap.overtime or 0,
            'idle_pct': cap.idle_pct or 0,
        }
    return {
        'total_positions': 0,
        'filled': 0,
        'vacant': 0,
        'available_capacity': 0,
        'utilization_pct': 0,
        'overtime': 0,
        'idle_pct': 0,
    }


@router.get('/teams/{team_id}/workload', response_model=TeamWorkloadResponse)
def team_workload(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    return {
        'assigned_tasks': 0,
        'completed': 0,
        'pending': 0,
        'overdue': 0,
        'average_sla': 0,
        'productivity': 0,
    }


@router.get('/teams/{team_id}/health', response_model=TeamHealthScoreResponse)
def team_health(team_id: str, db: Session = Depends(get_db)):
    team = get_team(db, team_id)
    health = db.query(models_team.TeamHealth).filter(models_team.TeamHealth.team_id == team_id).order_by(models_team.TeamHealth.recorded_at.desc()).first()
    if health:
        return {
            'score': health.score,
            'rating': health.rating or '★★★★☆',
            'capacity_utilization': health.capacity_utilization or 0,
            'productivity': health.productivity or 0,
            'sla_compliance': health.sla_compliance or 0,
            'employee_satisfaction': health.employee_satisfaction or 0,
            'attrition': health.attrition or 0,
            'training_completion': health.training_completion or 0,
            'project_delivery': health.project_delivery or 0,
            'audit_findings': health.audit_findings or 0,
        }
    score = 85 if team.status == 'active' else 50
    return {
        'score': float(score),
        'rating': '★★★★★' if score >= 85 else '★★★★☆' if score >= 70 else '★★★☆☆',
        'capacity_utilization': 0,
        'productivity': 0,
        'sla_compliance': 0,
        'employee_satisfaction': 0,
        'attrition': 0,
        'training_completion': 0,
        'project_delivery': 0,
        'audit_findings': 0,
    }


@router.get('/teams/{team_id}/members')
def team_members(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    members = db.query(models_team.TeamMember).filter(models_team.TeamMember.team_id == team_id, models_team.TeamMember.status == 'active').all()
    return {
        'total': len(members),
        'items': [
            {
                'id': m.id,
                'employee_id': m.employee_id,
                'employee_name': m.employee_name,
                'role': m.role,
                'position_id': m.position_id,
                'join_date': m.join_date,
            }
            for m in members
        ],
    }


@router.get('/teams/{team_id}/skills')
def team_skills(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    skills = db.query(models_team.TeamSkill).filter(models_team.TeamSkill.team_id == team_id).all()
    return {
        'total': len(skills),
        'items': [
            {
                'id': s.id,
                'employee_id': s.employee_id,
                'skill_name': s.skill_name,
                'level': s.level,
                'certification': s.certification,
                'expiry_date': s.expiry_date,
            }
            for s in skills
        ],
    }


# ─── Team Member Management ────────────────────────────────────────────────


@router.post('/teams/{team_id}/members', dependencies=[Depends(require_role('enterprise.admin'))])
def add_team_member(team_id: str, payload: dict, db: Session = Depends(get_db)):
    """Add a member to a team."""
    team = get_team(db, team_id)
    member = models_team.TeamMember(
        team_id=team_id,
        employee_id=payload.get('employee_id'),
        employee_name=payload.get('employee_name'),
        role=payload.get('role'),
        position_id=payload.get('position_id'),
        join_date=payload.get('join_date') or datetime.now().strftime('%Y-%m-%d'),
        status='active',
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    try:
        record_audit(db, 'team_member', member.id, 'added', payload)
    except Exception:
        pass
    publish_event('MEMBER_ADDED', {'team_id': team_id, 'employee_id': member.employee_id})
    return {'id': member.id, 'employee_id': member.employee_id, 'employee_name': member.employee_name, 'role': member.role}


@router.delete('/teams/{team_id}/members/{member_id}', dependencies=[Depends(require_role('enterprise.admin'))])
def remove_team_member(team_id: str, member_id: str, db: Session = Depends(get_db)):
    """Remove (soft-delete) a member from a team."""
    team = get_team(db, team_id)
    member = db.query(models_team.TeamMember).filter(models_team.TeamMember.id == member_id, models_team.TeamMember.team_id == team_id).first()
    if not member:
        raise HTTPException(status_code=404, detail='Team member not found')
    member.status = 'inactive'
    member.exit_date = datetime.now().strftime('%Y-%m-%d')
    db.add(member)
    db.commit()
    try:
        record_audit(db, 'team_member', member.id, 'removed', {})
    except Exception:
        pass
    publish_event('MEMBER_REMOVED', {'team_id': team_id, 'employee_id': member.employee_id})
    return {'detail': 'Member removed'}


# ─── Team Capacity Management ──────────────────────────────────────────────


@router.post('/teams/{team_id}/capacity', dependencies=[Depends(require_role('enterprise.admin'))])
def update_team_capacity(team_id: str, payload: dict, db: Session = Depends(get_db)):
    """Record a capacity snapshot for a team."""
    team = get_team(db, team_id)
    cap = models_team.TeamCapacity(
        team_id=team_id,
        total_positions=payload.get('total_positions', 0),
        filled=payload.get('filled', 0),
        vacant=payload.get('vacant', 0),
        available_capacity=payload.get('available_capacity'),
        utilization_pct=payload.get('utilization_pct'),
        overtime=payload.get('overtime', 0),
        idle_pct=payload.get('idle_pct'),
    )
    db.add(cap)
    db.commit()
    db.refresh(cap)
    publish_event('CAPACITY_UPDATED', {'team_id': team_id, 'utilization_pct': cap.utilization_pct})
    return {'id': cap.id, 'detail': 'Capacity recorded'}


# ─── Team Projects ─────────────────────────────────────────────────────────


@router.get('/teams/{team_id}/projects')
def team_projects(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    projects = db.query(models_team.TeamProject).filter(models_team.TeamProject.team_id == team_id).all()
    return {
        'total': len(projects),
        'items': [
            {
                'id': p.id,
                'project_id': p.project_id,
                'project_name': p.project_name,
                'product': p.product,
                'process': p.process,
                'customer': p.customer,
                'role': p.role,
                'start_date': p.start_date,
                'end_date': p.end_date,
                'status': p.status,
            }
            for p in projects
        ],
    }


@router.post('/teams/{team_id}/projects', dependencies=[Depends(require_role('enterprise.admin'))])
def add_team_project(team_id: str, payload: dict, db: Session = Depends(get_db)):
    get_team(db, team_id)
    project = models_team.TeamProject(
        team_id=team_id,
        project_id=payload.get('project_id'),
        project_name=payload.get('project_name'),
        product=payload.get('product'),
        process=payload.get('process'),
        customer=payload.get('customer'),
        role=payload.get('role'),
        start_date=payload.get('start_date'),
        end_date=payload.get('end_date'),
        status=payload.get('status', 'active'),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {'id': project.id, 'project_id': project.project_id, 'project_name': project.project_name}


# ─── Team Calendar ─────────────────────────────────────────────────────────


@router.get('/teams/{team_id}/calendar')
def team_calendar(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    entries = db.query(models_team.TeamCalendar).filter(models_team.TeamCalendar.team_id == team_id).all()
    return {
        'total': len(entries),
        'items': [
            {
                'id': e.id,
                'calendar_type': e.calendar_type,
                'title': e.title,
                'event_date': e.event_date,
                'description': e.description,
            }
            for e in entries
        ],
    }


@router.post('/teams/{team_id}/calendar', dependencies=[Depends(require_role('enterprise.admin'))])
def add_team_calendar_entry(team_id: str, payload: dict, db: Session = Depends(get_db)):
    get_team(db, team_id)
    entry = models_team.TeamCalendar(
        team_id=team_id,
        calendar_type=payload.get('calendar_type', 'event'),
        title=payload.get('title'),
        event_date=payload.get('event_date'),
        description=payload.get('description'),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {'id': entry.id, 'title': entry.title, 'event_date': entry.event_date}


# ─── Team KPIs ──────────────────────────────────────────────────────────────


@router.get('/teams/{team_id}/kpis')
def team_kpis(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    kpis = db.query(models_team.TeamKpi).filter(models_team.TeamKpi.team_id == team_id).all()
    return {
        'total': len(kpis),
        'items': [
            {
                'id': k.id,
                'kpi_name': k.kpi_name,
                'target': k.target,
                'actual': k.actual,
                'unit': k.unit,
                'period': k.period,
            }
            for k in kpis
        ],
    }


@router.post('/teams/{team_id}/kpis', dependencies=[Depends(require_role('enterprise.admin'))])
def add_team_kpi(team_id: str, payload: dict, db: Session = Depends(get_db)):
    get_team(db, team_id)
    kpi = models_team.TeamKpi(
        team_id=team_id,
        kpi_name=payload.get('kpi_name'),
        target=payload.get('target'),
        actual=payload.get('actual'),
        unit=payload.get('unit'),
        period=payload.get('period'),
    )
    db.add(kpi)
    db.commit()
    db.refresh(kpi)
    return {'id': kpi.id, 'kpi_name': kpi.kpi_name}


# ─── Team Assets ────────────────────────────────────────────────────────────


@router.get('/teams/{team_id}/assets')
def team_assets(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    assets = db.query(models_team.TeamAsset).filter(models_team.TeamAsset.team_id == team_id).all()
    return {
        'total': len(assets),
        'items': [
            {
                'id': a.id,
                'asset_type': a.asset_type,
                'asset_name': a.asset_name,
                'serial_number': a.serial_number,
                'status': a.status,
                'allocated_to': a.allocated_to,
            }
            for a in assets
        ],
    }


# ─── Team AI Insights ───────────────────────────────────────────────────────


@router.get('/teams/{team_id}/ai')
def team_ai_insights(team_id: str, db: Session = Depends(get_db)):
    get_team(db, team_id)
    insights = db.query(models_team.TeamAi).filter(models_team.TeamAi.team_id == team_id).order_by(models_team.TeamAi.created_at.desc()).all()
    return {
        'total': len(insights),
        'items': [
            {
                'id': i.id,
                'insight_type': i.insight_type,
                'insight': i.insight,
                'recommendation': i.recommendation,
                'score': i.score,
                'created_at': i.created_at,
            }
            for i in insights
        ],
    }


# ─── Workforce Planning (computed) ─────────────────────────────────────────


@router.get('/teams/{team_id}/workforce-planning')
def team_workforce_planning(team_id: str, db: Session = Depends(get_db)):
    team = get_team(db, team_id)
    cap = db.query(models_team.TeamCapacity).filter(models_team.TeamCapacity.team_id == team_id).order_by(models_team.TeamCapacity.recorded_at.desc()).first()
    total_pos = int(cap.total_positions) if cap else 0
    filled = int(cap.filled) if cap else 0
    vacant = int(cap.vacant) if cap else 0
    return {
        'required_employees': total_pos,
        'current_employees': filled,
        'vacancies': vacant,
        'forecast': max(0, int(total_pos * 1.1) - filled),
        'hiring_plan': max(0, vacant),
    }

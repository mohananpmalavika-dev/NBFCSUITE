from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import SessionLocal, engine
from .. import models, schemas
from .. import models_legal
from .. import models_geography
from .. import models_enterprise_master
from .. import schemas_enterprise_master
from ..events import publish_event
from ..auth import require_role
from ..audit import record_audit
from typing import Optional
import os
import json

models.Base.metadata.create_all(bind=engine)
models_enterprise_master.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _as_dict(row, fields: list[str]):
    if not row:
        return {}
    return {field: getattr(row, field) for field in fields}


def _replace_one_to_one(db: Session, model, enterprise_id: str, payload: dict):
    row = db.query(model).filter(model.enterprise_id == enterprise_id).first()
    if row is None:
        row = model(enterprise_id=enterprise_id)
    for field, value in payload.items():
        setattr(row, field, value)
    db.add(row)
    return row


def _replace_collection(db: Session, model, enterprise_id: str, items: list[dict]):
    db.query(model).filter(model.enterprise_id == enterprise_id).delete()
    rows = []
    for item in items:
        rows.append(model(enterprise_id=enterprise_id, **item))
    db.add_all(rows)
    return rows


def _profile_dict(db: Session, ent: models.Enterprise):
    branding = db.query(models_enterprise_master.EnterpriseBranding).filter_by(enterprise_id=ent.id).first()
    legal = db.query(models_enterprise_master.EnterpriseLegal).filter_by(enterprise_id=ent.id).first()
    finance = db.query(models_enterprise_master.EnterpriseFinance).filter_by(enterprise_id=ent.id).first()
    localization = db.query(models_enterprise_master.EnterpriseLocalization).filter_by(enterprise_id=ent.id).first()
    contact = db.query(models_enterprise_master.EnterpriseContact).filter_by(enterprise_id=ent.id).first()
    compliance = db.query(models_enterprise_master.EnterpriseCompliance).filter_by(enterprise_id=ent.id).first()
    integrations = db.query(models_enterprise_master.EnterpriseIntegration).filter_by(enterprise_id=ent.id).all()
    documents = db.query(models_enterprise_master.EnterpriseDocument).filter_by(enterprise_id=ent.id).all()
    settings = db.query(models_enterprise_master.EnterpriseSetting).filter_by(enterprise_id=ent.id).all()

    return {
        'enterprise': {
            'id': ent.id,
            'code': ent.code,
            'name': ent.name,
            'display_name': ent.display_name,
            'short_name': ent.short_name,
            'status': ent.status,
            'currency_code': ent.currency_code,
            'timezone': ent.timezone,
            'language': ent.language,
            'fiscal_year_start': ent.fiscal_year_start,
            'description': ent.description,
        },
        'branding': _as_dict(branding, ['logo_url', 'primary_color', 'secondary_color', 'theme', 'website', 'email_domain', 'mobile_app_name', 'portal_name']),
        'legal': _as_dict(legal, ['country', 'registration_number', 'incorporation_date', 'tax_number', 'gst_vat_number', 'pan', 'corporate_identity_number', 'regulatory_license']),
        'finance': _as_dict(finance, ['base_currency', 'financial_year', 'accounting_standard', 'tax_system', 'default_gl', 'default_cost_center', 'default_profit_center']),
        'localization': _as_dict(localization, ['language', 'time_zone', 'date_format', 'number_format', 'fiscal_calendar', 'holiday_calendar']),
        'contact': _as_dict(contact, ['corporate_address', 'head_office', 'email', 'phone', 'website', 'support_contact']),
        'compliance': _as_dict(compliance, ['aml_enabled', 'kyc_policy', 'data_retention', 'audit_retention', 'password_policy', 'session_policy']),
        'integrations': [
            _as_dict(item, ['id', 'integration_type', 'provider', 'status'])
            for item in integrations
        ],
        'documents': [
            _as_dict(item, ['id', 'document_type', 'name', 'status', 'ocr_metadata'])
            for item in documents
        ],
        'settings': [
            _as_dict(item, ['id', 'setting_group', 'setting_key', 'setting_value', 'inherited'])
            for item in settings
        ],
    }


def _enterprise_or_404(db: Session, id: str):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    return ent


def _safe_count(db: Session, selectable):
    try:
        return db.query(selectable).count()
    except Exception:
        return 0


def _health_score(profile: dict):
    checks = [
        ('General code', profile['enterprise'].get('code')),
        ('General name', profile['enterprise'].get('name')),
        ('Currency', profile['enterprise'].get('currency_code') or profile['finance'].get('base_currency')),
        ('Timezone', profile['enterprise'].get('timezone') or profile['localization'].get('time_zone')),
        ('Language', profile['enterprise'].get('language') or profile['localization'].get('language')),
        ('Fiscal year', profile['enterprise'].get('fiscal_year_start') or profile['finance'].get('financial_year')),
        ('Brand color', profile['branding'].get('primary_color')),
        ('Portal branding', profile['branding'].get('portal_name')),
        ('Legal registration', profile['legal'].get('registration_number')),
        ('Regulatory license', profile['legal'].get('regulatory_license')),
        ('Accounting standard', profile['finance'].get('accounting_standard')),
        ('Default GL', profile['finance'].get('default_gl')),
        ('Corporate address', profile['contact'].get('corporate_address')),
        ('Enterprise email', profile['contact'].get('email')),
        ('Support contact', profile['contact'].get('support_contact')),
        ('AML policy', profile['compliance'].get('aml_enabled')),
        ('KYC policy', profile['compliance'].get('kyc_policy')),
        ('Audit retention', profile['compliance'].get('audit_retention')),
        ('Security policy', profile['compliance'].get('password_policy')),
        ('Active integration', any(item.get('status') == 'active' for item in profile['integrations'])),
        ('Verified document', any(item.get('status') == 'verified' for item in profile['documents'])),
    ]
    passed = [name for name, value in checks if bool(value)]
    missing = [name for name, value in checks if not bool(value)]
    score = round((len(passed) / len(checks)) * 100)
    return {
        'score': score,
        'status': 'strong' if score >= 85 else 'attention' if score >= 60 else 'setup-required',
        'passed': passed,
        'missing': missing,
    }


@router.post('/enterprises', response_model=schemas.EnterpriseResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_enterprise(payload: schemas.EnterpriseCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Enterprise).filter(models.Enterprise.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Enterprise code already exists')
    ent = models.Enterprise(
        code=payload.code,
        name=payload.name,
        display_name=payload.display_name,
        short_name=payload.short_name,
        currency_code=payload.currency_code,
        timezone=payload.timezone,
        language=payload.language,
        fiscal_year_start=payload.fiscal_year_start,
        description=payload.description,
        status='active'
    )
    db.add(ent)
    db.commit()
    db.refresh(ent)

    # persist audit and publish domain event (placeholders)
    try:
        record_audit(db, 'enterprise', ent.id, 'created', {'code': ent.code, 'name': ent.name})
    except Exception:
        pass
    try:
        publish_event('ENTERPRISE_CREATED', {'id': ent.id, 'code': ent.code, 'name': ent.name})
    except Exception:
        pass

    return ent


@router.get('/enterprises', response_model=schemas.EnterpriseListResponse)
def list_enterprises(q: Optional[str] = None, status: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models.Enterprise)
    if q:
        like = f"%{q}%"
        query = query.filter((models.Enterprise.name.ilike(like)) | (models.Enterprise.code.ilike(like)))
    if status:
        query = query.filter(models.Enterprise.status == status)
    total = query.count()
    ents = query.order_by(models.Enterprise.created_at.desc()).limit(limit).offset(offset).all()
    # include pagination meta in headers – but for simplicity return an envelope
    return { 'total': total, 'items': ents }


@router.get('/enterprises/{id}', response_model=schemas.EnterpriseResponse)
def get_enterprise(id: str, db: Session = Depends(get_db)):
    return _enterprise_or_404(db, id)


@router.patch('/enterprises/{id}', response_model=schemas.EnterpriseResponse)
def update_enterprise(id: str, payload: schemas.EnterpriseUpdate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    ent = _enterprise_or_404(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ent, field, value)
    db.add(ent)
    db.commit()
    db.refresh(ent)
    try:
        record_audit(db, 'enterprise', ent.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('ENTERPRISE_UPDATED', {'id': ent.id})
    return ent


@router.delete('/enterprises/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_enterprise(id: str, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    ent = _enterprise_or_404(db, id)
    db.delete(ent)
    db.commit()
    try:
        record_audit(db, 'enterprise', id, 'deleted', None)
    except Exception:
        pass
    publish_event('ENTERPRISE_DELETED', {'id': id})
    return None


@router.post('/enterprises/{id}/status')
def set_enterprise_status(id: str, status_body: dict, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    ent = _enterprise_or_404(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    ent.status = new_status
    db.add(ent)
    db.commit()
    db.refresh(ent)
    try:
        record_audit(db, 'enterprise', id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('ENTERPRISE_STATUS_CHANGED', {'id': id, 'status': new_status})
    return {'id': id, 'status': new_status}


@router.get('/enterprises/{id}/health')
def enterprise_health(id: str, db: Session = Depends(get_db)):
    ent = _enterprise_or_404(db, id)
    profile = _profile_dict(db, ent)
    health = _health_score(profile)
    return {
        'id': ent.id,
        'status': ent.status,
        'ready': ent.status == 'active',
        'score': health['score'],
        'health_status': health['status'],
        'passed': health['passed'],
        'missing': health['missing'],
    }


@router.get('/enterprises/{id}/timeline')
def enterprise_timeline(id: str):
    # read from audit store when available; for now read file sink
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


@router.get('/enterprises/{id}/profile')
def get_enterprise_profile(id: str, db: Session = Depends(get_db)):
    ent = _enterprise_or_404(db, id)
    return _profile_dict(db, ent)


@router.put('/enterprises/{id}/profile')
def update_enterprise_profile(
    id: str,
    payload: schemas_enterprise_master.EnterpriseProfilePayload,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    ent = _enterprise_or_404(db, id)
    data = payload.model_dump()

    _replace_one_to_one(db, models_enterprise_master.EnterpriseBranding, id, data['branding'])
    _replace_one_to_one(db, models_enterprise_master.EnterpriseLegal, id, data['legal'])
    _replace_one_to_one(db, models_enterprise_master.EnterpriseFinance, id, data['finance'])
    _replace_one_to_one(db, models_enterprise_master.EnterpriseLocalization, id, data['localization'])
    _replace_one_to_one(db, models_enterprise_master.EnterpriseContact, id, data['contact'])
    _replace_one_to_one(db, models_enterprise_master.EnterpriseCompliance, id, data['compliance'])
    _replace_collection(db, models_enterprise_master.EnterpriseIntegration, id, data['integrations'])
    _replace_collection(db, models_enterprise_master.EnterpriseDocument, id, data['documents'])
    _replace_collection(db, models_enterprise_master.EnterpriseSetting, id, data['settings'])

    finance = data['finance']
    localization = data['localization']
    legal = data['legal']
    if finance.get('base_currency'):
        ent.currency_code = finance['base_currency']
    if localization.get('time_zone'):
        ent.timezone = localization['time_zone']
    if localization.get('language'):
        ent.language = localization['language']
    if finance.get('financial_year'):
        ent.fiscal_year_start = finance['financial_year']
    db.add(ent)
    db.commit()

    profile = _profile_dict(db, ent)
    health = _health_score(profile)
    record_audit(db, 'enterprise', id, 'profile_updated', {'sections': list(data.keys()), 'health_score': health['score']})
    publish_event('ENTERPRISE_CONFIGURATION_CHANGED', {'id': id, 'code': ent.code})
    publish_event('ENTERPRISE_HEALTH_CHANGED', {'id': id, 'score': health['score'], 'status': health['status']})
    if legal.get('regulatory_license') is None:
        publish_event('ENTERPRISE_LICENSE_MISSING', {'id': id})
    return {**profile, 'health': health}


@router.get('/enterprises/{id}/dashboard')
def get_enterprise_dashboard(id: str, db: Session = Depends(get_db)):
    ent = _enterprise_or_404(db, id)
    profile = _profile_dict(db, ent)
    health = _health_score(profile)
    branch_count = 0
    try:
        branch_count = db.query(models_geography.GeographyNode.id).filter(models_geography.GeographyNode.node_type == 'branch').count()
    except Exception:
        branch_count = 0

    return {
        'enterprise': profile['enterprise'],
        'health': health,
        'indicators': [
            {'label': 'Legal entities', 'value': _safe_count(db, models_legal.LegalEntity.id)},
            {'label': 'Business units', 'value': _safe_count(db, models_legal.BusinessUnit.id)},
            {'label': 'Branches', 'value': branch_count},
            {'label': 'Documents', 'value': len(profile['documents'])},
            {'label': 'Active integrations', 'value': len([item for item in profile['integrations'] if item.get('status') == 'active'])},
            {'label': 'AI score', 'value': health['score']},
        ],
        'perspectives': {
            'operational': ['Branches', 'Employees', 'Departments', 'Business units'],
            'financial': ['Revenue', 'Expenses', 'Budget', 'GL mappings', 'Profit centers'],
            'compliance': ['Licenses', 'Policies', 'Regulatory matters', 'Audit exceptions'],
            'technology': ['API status', 'Integrations', 'Security posture', 'Backups'],
            'ai': ['Enterprise summary', 'Growth forecast', 'Risk analysis', 'Optimization suggestions'],
        },
        'reports': [
            'Enterprise profile',
            'Enterprise health report',
            'Compliance report',
            'License register',
            'Configuration report',
            'Integration status',
            'Branding report',
            'Localization report',
        ],
    }


@router.get('/enterprises/{id}/settings')
def get_enterprise_settings(id: str, db: Session = Depends(get_db)):
    ent = _enterprise_or_404(db, id)
    settings = db.query(models_enterprise_master.EnterpriseSetting).filter_by(enterprise_id=ent.id).all()
    if settings:
        return {
            'enterprise_id': id,
            'items': [_as_dict(item, ['id', 'setting_group', 'setting_key', 'setting_value', 'inherited']) for item in settings],
        }
    default_groups = ['General', 'Branding', 'Finance', 'HR', 'Customer', 'Accounting', 'Loans', 'Deposits', 'Treasury', 'Forex', 'Security', 'Notifications', 'Workflow', 'AI', 'Reports']
    return {
        'enterprise_id': id,
        'items': [
            {'setting_group': group, 'setting_key': 'enabled', 'setting_value': 'true', 'inherited': True}
            for group in default_groups
        ],
    }


@router.get('/enterprises/{id}/audit')
def get_enterprise_audit(id: str, db: Session = Depends(get_db)):
    _enterprise_or_404(db, id)
    entries = (
        db.query(models.AuditEntry)
        .filter(models.AuditEntry.entity_type == 'enterprise', models.AuditEntry.entity_id == id)
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

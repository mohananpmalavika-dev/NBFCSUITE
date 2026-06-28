from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from ..db import SessionLocal
from .. import models, schemas
from .. import models_legal, schemas_legal
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event
from typing import Optional

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_legal_entity(db: Session, id: str):
    le = (
        db.query(models_legal.LegalEntity)
        .options(
            selectinload(models_legal.LegalEntity.registrations),
            selectinload(models_legal.LegalEntity.licenses),
            selectinload(models_legal.LegalEntity.taxes),
            selectinload(models_legal.LegalEntity.banks),
            selectinload(models_legal.LegalEntity.contacts),
            selectinload(models_legal.LegalEntity.documents),
            selectinload(models_legal.LegalEntity.compliances),
        )
        .filter(models_legal.LegalEntity.id == id)
        .first()
    )
    if not le:
        raise HTTPException(status_code=404, detail='Legal entity not found')
    return le


def attach_nested_collections(le, payload):
    if payload.registrations is not None:
        le.registrations.clear()
        for registration in payload.registrations:
            le.registrations.append(models_legal.LegalEntityRegistration(**registration.model_dump()))

    if payload.licenses is not None:
        le.licenses.clear()
        for license in payload.licenses:
            le.licenses.append(models_legal.LegalEntityLicense(**license.model_dump()))

    if payload.taxes is not None:
        le.taxes.clear()
        for tax in payload.taxes:
            le.taxes.append(models_legal.LegalEntityTax(**tax.model_dump()))

    if payload.banks is not None:
        le.banks.clear()
        for bank in payload.banks:
            le.banks.append(models_legal.LegalEntityBank(**bank.model_dump()))

    if payload.contacts is not None:
        le.contacts.clear()
        for contact in payload.contacts:
            le.contacts.append(models_legal.LegalEntityContact(**contact.model_dump()))

    if payload.documents is not None:
        le.documents.clear()
        for document in payload.documents:
            le.documents.append(models_legal.LegalEntityDocument(**document.model_dump()))

    if payload.compliances is not None:
        le.compliances.clear()
        for compliance in payload.compliances:
            le.compliances.append(models_legal.LegalEntityCompliance(**compliance.model_dump()))


@router.post('/legal-entities', response_model=schemas_legal.LegalEntityResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_legal(payload: schemas_legal.LegalEntityCreate, db: Session = Depends(get_db)):
    existing = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Legal entity code already exists')
    le = models_legal.LegalEntity(
        code=payload.code,
        name=payload.name,
        display_name=payload.display_name,
        legal_type=payload.legal_type,
        status=payload.status or 'draft',
        country=payload.country,
        incorporation_date=payload.incorporation_date,
        cin=payload.cin,
        pan=payload.pan,
        gst=payload.gst,
        tan=payload.tan,
        vat=payload.vat,
        service_tax=payload.service_tax,
        iec=payload.iec,
        primary_bank=payload.primary_bank,
        settlement_bank=payload.settlement_bank,
        escrow_account=payload.escrow_account,
        registered_office=payload.registered_office,
        corporate_office=payload.corporate_office,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        compliance_status=payload.compliance_status,
        risk_rating=payload.risk_rating,
        description=payload.description,
    )
    attach_nested_collections(le, payload)
    db.add(le)
    db.commit()
    db.refresh(le)
    try:
        record_audit(db, 'legal_entity', le.id, 'created', {'code': le.code, 'name': le.name})
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_CREATED', {'id': le.id, 'code': le.code, 'name': le.name})
    return le


@router.get('/legal-entities', response_model=schemas_legal.LegalEntityListResponse)
def list_legal(q: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_legal.LegalEntity)
    if q:
        like = f"%{q}%"
        query = query.filter((models_legal.LegalEntity.name.ilike(like)) | (models_legal.LegalEntity.code.ilike(like)))
    total = query.count()
    items = query.order_by(models_legal.LegalEntity.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/legal-entities/{id}', response_model=schemas_legal.LegalEntityResponse)
def get_legal(id: str, db: Session = Depends(get_db)):
    return get_legal_entity(db, id)


@router.patch('/legal-entities/{id}', response_model=schemas_legal.LegalEntityResponse)
def update_legal(id: str, payload: schemas_legal.LegalEntityUpdate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    le = get_legal_entity(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {
            'registrations', 'licenses', 'taxes', 'banks', 'contacts', 'documents', 'compliances'
        }:
            continue
        setattr(le, field, value)
    attach_nested_collections(le, payload)
    db.add(le)
    db.commit()
    db.refresh(le)
    try:
        record_audit(db, 'legal_entity', le.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_UPDATED', {'id': le.id})
    return le


@router.delete('/legal-entities/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_legal(id: str, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    le = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == id).first()
    if not le:
        raise HTTPException(status_code=404, detail='Legal entity not found')
    db.delete(le)
    db.commit()
    try:
        record_audit(db, 'legal_entity', id, 'deleted', None)
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_DELETED', {'id': id})
    return None


@router.get('/legal-entities/{id}/health', response_model=schemas_legal.LegalEntityHealthResponse)
def legal_entity_health(id: str, db: Session = Depends(get_db)):
    le = get_legal_entity(db, id)
    expired_licenses = sum(1 for license in le.licenses if license.expiry_date and license.expiry_date < date.today())
    compliance_issues = sum(1 for compliance in le.compliances if compliance.status and compliance.status.lower() not in {'compliant', 'ok', 'clear'})
    missing_registrations = 1 if len(le.registrations) == 0 else 0
    missing_bank_accounts = 1 if len(le.banks) == 0 else 0
    audit_pending = 0
    health_score = max(
        0,
        100 - missing_registrations * 20 - missing_bank_accounts * 15 - expired_licenses * 15 - compliance_issues * 10,
    )
    return {
        'health_score': health_score,
        'missing_registrations': missing_registrations,
        'expired_licenses': expired_licenses,
        'missing_bank_accounts': missing_bank_accounts,
        'compliance_issues': compliance_issues,
        'audit_pending': audit_pending,
    }


@router.get('/legal-entities/{id}/timeline', response_model=schemas_legal.LegalEntityTimelineListResponse)
def legal_entity_timeline(id: str, db: Session = Depends(get_db)):
    entries = (
        db.query(models.AuditEntry)
        .filter(models.AuditEntry.entity_type == 'legal_entity', models.AuditEntry.entity_id == id)
        .order_by(models.AuditEntry.created_at.desc())
        .all()
    )
    return {'total': len(entries), 'items': entries}


@router.get('/legal-entities/{id}/audit', response_model=schemas.AuditListResponse)
def legal_entity_audit(id: str, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models.AuditEntry).filter(models.AuditEntry.entity_type == 'legal_entity', models.AuditEntry.entity_id == id)
    total = query.count()
    items = query.order_by(models.AuditEntry.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/legal-entities/{id}/registrations', response_model=list[schemas_legal.LegalEntityRegistrationResponse])
def list_legal_entity_registrations(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityRegistration).filter(models_legal.LegalEntityRegistration.legal_entity_id == id).order_by(models_legal.LegalEntityRegistration.created_at.desc()).all()


@router.post('/legal-entities/{id}/registrations', response_model=schemas_legal.LegalEntityRegistrationResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_registration(id: str, payload: schemas_legal.LegalEntityRegistrationCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    le = get_legal_entity(db, id)
    registration = models_legal.LegalEntityRegistration(**payload.model_dump(), legal_entity=le)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


@router.get('/legal-entities/{id}/licenses', response_model=list[schemas_legal.LegalEntityLicenseResponse])
def list_legal_entity_licenses(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityLicense).filter(models_legal.LegalEntityLicense.legal_entity_id == id).order_by(models_legal.LegalEntityLicense.created_at.desc()).all()


@router.post('/legal-entities/{id}/licenses', response_model=schemas_legal.LegalEntityLicenseResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_license(id: str, payload: schemas_legal.LegalEntityLicenseCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    license = models_legal.LegalEntityLicense(**payload.model_dump())
    license.legal_entity_id = id
    db.add(license)
    db.commit()
    db.refresh(license)
    return license


@router.get('/legal-entities/{id}/taxes', response_model=list[schemas_legal.LegalEntityTaxResponse])
def list_legal_entity_taxes(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityTax).filter(models_legal.LegalEntityTax.legal_entity_id == id).order_by(models_legal.LegalEntityTax.created_at.desc()).all()


@router.post('/legal-entities/{id}/taxes', response_model=schemas_legal.LegalEntityTaxResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_tax(id: str, payload: schemas_legal.LegalEntityTaxCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    tax = models_legal.LegalEntityTax(**payload.model_dump())
    tax.legal_entity_id = id
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


@router.get('/legal-entities/{id}/banks', response_model=list[schemas_legal.LegalEntityBankResponse])
def list_legal_entity_banks(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityBank).filter(models_legal.LegalEntityBank.legal_entity_id == id).order_by(models_legal.LegalEntityBank.created_at.desc()).all()


@router.post('/legal-entities/{id}/banks', response_model=schemas_legal.LegalEntityBankResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_bank(id: str, payload: schemas_legal.LegalEntityBankCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    bank = models_legal.LegalEntityBank(**payload.model_dump())
    bank.legal_entity_id = id
    db.add(bank)
    db.commit()
    db.refresh(bank)
    return bank


@router.get('/legal-entities/{id}/contacts', response_model=list[schemas_legal.LegalEntityContactResponse])
def list_legal_entity_contacts(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityContact).filter(models_legal.LegalEntityContact.legal_entity_id == id).order_by(models_legal.LegalEntityContact.created_at.desc()).all()


@router.post('/legal-entities/{id}/contacts', response_model=schemas_legal.LegalEntityContactResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_contact(id: str, payload: schemas_legal.LegalEntityContactCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    contact = models_legal.LegalEntityContact(**payload.model_dump())
    contact.legal_entity_id = id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get('/legal-entities/{id}/documents', response_model=list[schemas_legal.LegalEntityDocumentResponse])
def list_legal_entity_documents(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityDocument).filter(models_legal.LegalEntityDocument.legal_entity_id == id).order_by(models_legal.LegalEntityDocument.created_at.desc()).all()


@router.post('/legal-entities/{id}/documents', response_model=schemas_legal.LegalEntityDocumentResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_document(id: str, payload: schemas_legal.LegalEntityDocumentCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    document = models_legal.LegalEntityDocument(**payload.model_dump())
    document.legal_entity_id = id
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get('/legal-entities/{id}/compliances', response_model=list[schemas_legal.LegalEntityComplianceResponse])
def list_legal_entity_compliances(id: str, db: Session = Depends(get_db)):
    get_legal_entity(db, id)
    return db.query(models_legal.LegalEntityCompliance).filter(models_legal.LegalEntityCompliance.legal_entity_id == id).order_by(models_legal.LegalEntityCompliance.created_at.desc()).all()


@router.post('/legal-entities/{id}/compliances', response_model=schemas_legal.LegalEntityComplianceResponse, status_code=status.HTTP_201_CREATED)
def add_legal_entity_compliance(id: str, payload: schemas_legal.LegalEntityComplianceCreate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    get_legal_entity(db, id)
    compliance = models_legal.LegalEntityCompliance(**payload.model_dump())
    compliance.legal_entity_id = id
    db.add(compliance)
    db.commit()
    db.refresh(compliance)
    return compliance

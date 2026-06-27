from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
DOCUMENT_STORAGE_ROOT = os.getenv("DOCUMENT_STORAGE_ROOT", "data/documents")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DocumentRecord(Base):
    __tablename__ = "document_records"

    id = Column(String, primary_key=True)
    subject_type = Column(String)
    subject_id = Column(String)
    document_category = Column(String, nullable=True)
    document_type = Column(String)
    document_name = Column(String)
    document_url = Column(String)
    version = Column(String, default="1")
    status = Column(String, default="active")
    expiry_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_latest = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    storage_location = Column(String, default="local")
    storage_path = Column(String(1000), nullable=True)
    ocr_extracted_data = Column(JSON, nullable=True)
    ocr_status = Column(String, default="pending")
    signature_status = Column(String, default="unsigned")
    watermark_applied = Column(Boolean, default=False)
    expiry_alert_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentCreate(BaseModel):
    id: Optional[str] = None
    subject_type: str
    subject_id: str
    document_category: Optional[str] = None
    document_type: str
    document_name: str
    document_url: str
    expiry_date: Optional[datetime] = None
    created_by: Optional[str] = None
    storage_location: Optional[str] = "local"
    storage_path: Optional[str] = None
    metadata: Optional[dict] = None
    version: Optional[str] = None


class DocumentUpdate(BaseModel):
    document_category: Optional[str] = None
    document_name: Optional[str] = None
    document_url: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    expiry_date: Optional[datetime] = None
    created_by: Optional[str] = None
    storage_location: Optional[str] = None
    storage_path: Optional[str] = None
    metadata: Optional[dict] = None
    ocr_extracted_data: Optional[dict] = None
    ocr_status: Optional[str] = None
    signature_status: Optional[str] = None
    watermark_applied: Optional[bool] = None
    expiry_alert_sent: Optional[bool] = None


class DocumentResponse(BaseModel):
    id: str
    subject_type: str
    subject_id: str
    document_category: Optional[str] = None
    document_type: str
    document_name: str
    document_url: str
    version: str
    status: str
    expiry_date: Optional[datetime] = None
    metadata: Optional[dict] = None
    is_latest: bool
    created_by: Optional[str] = None
    storage_location: str
    storage_path: Optional[str] = None
    ocr_extracted_data: Optional[dict] = None
    ocr_status: str
    signature_status: str
    watermark_applied: bool
    expiry_alert_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    skip: int
    limit: int
    total: int


app = FastAPI(title="document-service", version="0.1.0")

DOCUMENT_STATUSES = {"pending", "verified", "rejected", "expired", "signed", "active"}


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "document"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def get_document_or_404(document_id: str, db: Session) -> DocumentRecord:
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


def ensure_storage_root() -> None:
    os.makedirs(DOCUMENT_STORAGE_ROOT, exist_ok=True)


def save_uploaded_file(customer_id: str, file: UploadFile) -> str:
    ensure_storage_root()
    target_folder = os.path.join(DOCUMENT_STORAGE_ROOT, customer_id)
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, f"{uuid4()}_{file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


@app.post("/documents", response_model=DocumentResponse)
async def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    existing_versions = db.query(DocumentRecord).filter(
        DocumentRecord.subject_type == document.subject_type,
        DocumentRecord.subject_id == document.subject_id,
        DocumentRecord.document_category == document.document_category,
        DocumentRecord.document_type == document.document_type,
        DocumentRecord.is_latest == True,
    ).all()

    for existing in existing_versions:
        existing.is_latest = False

    new_version = str(len(existing_versions) + 1)
    new_doc = DocumentRecord(
        id=document.id or str(uuid4()),
        subject_type=document.subject_type,
        subject_id=document.subject_id,
        document_category=document.document_category,
        document_type=document.document_type,
        document_name=document.document_name,
        document_url=document.document_url,
        version=new_version,
        status="active",
        expiry_date=document.expiry_date,
        metadata=document.metadata,
        is_latest=True,
        created_by=document.created_by,
        storage_location=document.storage_location or "local",
        storage_path=document.storage_path,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    subject_type: str = Form(...),
    subject_id: str = Form(...),
    document_category: Optional[str] = Form(None),
    document_type: str = Form(...),
    document_name: str = Form(...),
    file: UploadFile = File(...),
    expiry_date: Optional[datetime] = Form(None),
    created_by: Optional[str] = Form(None),
    storage_location: Optional[str] = Form("local"),
    metadata: Optional[str] = Form(None),
):
    db_metadata = None
    if metadata:
        try:
            db_metadata = json.loads(metadata)
        except ValueError:
            db_metadata = {"metadata_text": metadata}

    document_id = str(uuid4())
    file_path = save_uploaded_file(subject_id, file)
    payload = DocumentCreate(
        id=document_id,
        subject_type=subject_type,
        subject_id=subject_id,
        document_category=document_category,
        document_type=document_type,
        document_name=document_name,
        document_url=f"/documents/{document_id}/download",
        version="1",
        expiry_date=expiry_date,
        created_by=created_by,
        storage_location=storage_location,
        storage_path=file_path,
        metadata={
            "uploaded_filename": file.filename,
            **(db_metadata or {}),
        },
    )
    return await create_document(payload, db)


@app.get("/documents/expiring", response_model=DocumentListResponse)
async def list_expiring_documents(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    days: int = Query(30, ge=0, le=365),
    include_expired: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    cutoff = datetime.utcnow() + timedelta(days=days)
    query = db.query(DocumentRecord).filter(DocumentRecord.expiry_date.isnot(None))
    if include_expired:
        query = query.filter(DocumentRecord.expiry_date <= cutoff)
    else:
        query = query.filter(
            DocumentRecord.expiry_date >= datetime.utcnow(),
            DocumentRecord.expiry_date <= cutoff,
            DocumentRecord.status != "expired",
        )
    if subject_type:
        query = query.filter(DocumentRecord.subject_type == subject_type)
    if subject_id:
        query = query.filter(DocumentRecord.subject_id == subject_id)

    total = query.count()
    documents = query.order_by(DocumentRecord.expiry_date.asc()).offset(skip).limit(limit).all()
    return {"items": documents, "skip": skip, "limit": limit, "total": total}


@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    return get_document_or_404(document_id, db)


@app.get("/documents/versions", response_model=DocumentListResponse)
async def list_document_versions(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    document_category: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(DocumentRecord)
    if subject_type:
        query = query.filter(DocumentRecord.subject_type == subject_type)
    if subject_id:
        query = query.filter(DocumentRecord.subject_id == subject_id)
    if document_category:
        query = query.filter(DocumentRecord.document_category == document_category)
    if document_type:
        query = query.filter(DocumentRecord.document_type == document_type)
    total = query.count()
    documents = query.order_by(DocumentRecord.version.desc()).offset(skip).limit(limit).all()
    return {"items": documents, "skip": skip, "limit": limit, "total": total}


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    document_category: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(DocumentRecord)
    if subject_type:
        query = query.filter(DocumentRecord.subject_type == subject_type)
    if subject_id:
        query = query.filter(DocumentRecord.subject_id == subject_id)
    if document_category:
        query = query.filter(DocumentRecord.document_category == document_category)
    if document_type:
        query = query.filter(DocumentRecord.document_type == document_type)
    if status:
        query = query.filter(DocumentRecord.status == status)
    total = query.count()
    documents = query.order_by(DocumentRecord.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": documents, "skip": skip, "limit": limit, "total": total}


@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, update_data: DocumentUpdate, db: Session = Depends(get_db)):
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    updated_fields = update_data.model_dump(exclude_unset=True)
    if "status" in updated_fields and updated_fields["status"] not in DOCUMENT_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {', '.join(sorted(DOCUMENT_STATUSES))}",
        )
    for field, value in updated_fields.items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return document


@app.put("/documents/{document_id}/expire", response_model=DocumentResponse)
async def expire_document(document_id: str, db: Session = Depends(get_db)):
    document = get_document_or_404(document_id, db)
    if document.status == "rejected":
        raise HTTPException(status_code=409, detail="Rejected documents cannot be expired")

    metadata = dict(document.metadata or {})
    metadata["expired_at"] = datetime.utcnow().isoformat()
    metadata["previous_status"] = document.status
    document.status = "expired"
    document.metadata = metadata
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    return document


@app.put("/documents/{document_id}/sign", response_model=DocumentResponse)
async def sign_document(document_id: str, signer: Optional[str] = Query(None), db: Session = Depends(get_db)):
    document = get_document_or_404(document_id, db)
    if document.signature_status == "signed":
        return document

    metadata = dict(document.metadata or {})
    metadata["signed_by"] = signer or "system"
    metadata["signed_at"] = datetime.utcnow().isoformat()
    document.signature_status = "signed"
    document.status = "signed"
    document.metadata = metadata
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    return document


@app.get("/documents/{document_id}/download")
async def download_document(document_id: str, db: Session = Depends(get_db)):
    document = get_document_or_404(document_id, db)
    if document.storage_location != "local" or not document.storage_path:
        raise HTTPException(status_code=404, detail="Document file not available for download")
    if not os.path.exists(document.storage_path):
        raise HTTPException(status_code=404, detail="Stored document file not found")
    return FileResponse(
        path=document.storage_path,
        filename=document.document_name,
        media_type="application/octet-stream",
    )


@app.put("/documents/{document_id}/watermark", response_model=DocumentResponse)
async def watermark_document(document_id: str, watermark_text: Optional[str] = Query("NBFC-DMS"), db: Session = Depends(get_db)):
    document = get_document_or_404(document_id, db)
    document.watermark_applied = True
    document.updated_at = datetime.utcnow()
    metadata = dict(document.metadata or {})
    metadata["watermark_text"] = watermark_text
    metadata["watermark_applied_at"] = datetime.utcnow().isoformat()
    document.metadata = metadata
    db.commit()
    db.refresh(document)
    return document


@app.get("/documents/expiry-alerts", response_model=DocumentListResponse)
async def expiry_alerts(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    days: int = Query(30, ge=0, le=365),
    include_sent: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    cutoff = datetime.utcnow() + timedelta(days=days)
    query = db.query(DocumentRecord).filter(
        DocumentRecord.expiry_date.isnot(None),
        DocumentRecord.expiry_date <= cutoff,
        DocumentRecord.status != "expired",
    )
    if not include_sent:
        query = query.filter(DocumentRecord.expiry_alert_sent == False)
    if subject_type:
        query = query.filter(DocumentRecord.subject_type == subject_type)
    if subject_id:
        query = query.filter(DocumentRecord.subject_id == subject_id)

    total = query.count()
    documents = query.order_by(DocumentRecord.expiry_date.asc()).offset(skip).limit(limit).all()
    return {"items": documents, "skip": skip, "limit": limit, "total": total}


@app.put("/documents/{document_id}/alert-sent", response_model=DocumentResponse)
async def mark_expiry_alert_sent(document_id: str, db: Session = Depends(get_db)):
    document = get_document_or_404(document_id, db)
    document.expiry_alert_sent = True
    document.metadata = dict(document.metadata or {}, expiry_alert_sent_at=datetime.utcnow().isoformat())
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    return document


@app.get("/")
async def root():
    return {"service": "document", "version": "0.1.0"}

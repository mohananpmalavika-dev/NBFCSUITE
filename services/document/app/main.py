from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DocumentRecord(Base):
    __tablename__ = "document_records"

    id = Column(String, primary_key=True)
    subject_type = Column(String)
    subject_id = Column(String)
    document_type = Column(String)
    document_name = Column(String)
    document_url = Column(String)
    version = Column(String, default="1.0")
    status = Column(String, default="pending")
    expiry_date = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentCreate(BaseModel):
    subject_type: str
    subject_id: str
    document_type: str
    document_name: str
    document_url: str
    expiry_date: Optional[datetime] = None
    metadata: Optional[dict] = None


class DocumentUpdate(BaseModel):
    document_name: Optional[str] = None
    document_url: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    expiry_date: Optional[datetime] = None
    metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: str
    subject_type: str
    subject_id: str
    document_type: str
    document_name: str
    document_url: str
    version: str
    status: str
    expiry_date: Optional[datetime] = None
    metadata: Optional[dict] = None
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

DOCUMENT_STATUSES = {"pending", "verified", "rejected", "expired"}


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


@app.post("/documents", response_model=DocumentResponse)
async def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = DocumentRecord(
        id=str(uuid4()),
        subject_type=document.subject_type,
        subject_id=document.subject_id,
        document_type=document.document_type,
        document_name=document.document_name,
        document_url=document.document_url,
        expiry_date=document.expiry_date,
        metadata=document.metadata,
        status="pending"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


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
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
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
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
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


@app.get("/")
async def root():
    return {"service": "document", "version": "0.1.0"}

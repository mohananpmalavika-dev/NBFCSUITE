from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime
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


app = FastAPI(title="document-service", version="0.1.0")


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


@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.get("/documents")
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
    documents = query.offset(skip).limit(limit).all()
    return {"items": documents, "skip": skip, "limit": limit, "total": len(documents)}


@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, update_data: DocumentUpdate, db: Session = Depends(get_db)):
    document = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    updated_fields = update_data.model_dump(exclude_unset=True)
    for field, value in updated_fields.items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return document


@app.get("/")
async def root():
    return {"service": "document", "version": "0.1.0"}

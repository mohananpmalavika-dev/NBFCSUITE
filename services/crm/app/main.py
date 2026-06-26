from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, Float, JSON
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


class Lead(Base):
    __tablename__ = "crm_leads"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=True)
    source = Column(String)
    status = Column(String, default="new")
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)


class Campaign(Base):
    __tablename__ = "crm_campaigns"

    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)


class Opportunity(Base):
    __tablename__ = "crm_opportunities"

    id = Column(String, primary_key=True)
    lead_id = Column(String)
    product_code = Column(String)
    stage = Column(String, default="prospecting")
    value = Column(Float)
    probability = Column(Float)
    close_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeadCreate(BaseModel):
    source: str
    assigned_to: Optional[str] = None
    metadata: Optional[dict] = None


class LeadResponse(BaseModel):
    id: str
    source: str
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    budget: float


class CampaignResponse(BaseModel):
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    budget: float
    status: str

    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    lead_id: str
    product_code: str
    value: float
    probability: float
    close_date: Optional[datetime] = None


class OpportunityResponse(BaseModel):
    id: str
    lead_id: str
    product_code: str
    stage: str
    value: float
    probability: float
    close_date: Optional[datetime]

    class Config:
        from_attributes = True


app = FastAPI(title="crm-service", version="0.1.0")


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
    return {"status": "ok", "service": "crm"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/leads", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    new_lead = Lead(
        id=str(uuid4()),
        source=lead.source,
        assigned_to=lead.assigned_to,
        metadata=lead.metadata,
        status="new"
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead


@app.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    if assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)
    return query.offset(skip).limit(limit).all()


@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    new_campaign = Campaign(
        id=str(uuid4()),
        name=campaign.name,
        description=campaign.description,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        budget=campaign.budget,
        status="planned"
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign


@app.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Campaign)
    if status:
        query = query.filter(Campaign.status == status)
    return query.offset(skip).limit(limit).all()


@app.post("/opportunities", response_model=OpportunityResponse)
async def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    new_opportunity = Opportunity(
        id=str(uuid4()),
        lead_id=opportunity.lead_id,
        product_code=opportunity.product_code,
        value=opportunity.value,
        probability=opportunity.probability,
        close_date=opportunity.close_date,
        stage="prospecting"
    )
    db.add(new_opportunity)
    db.commit()
    db.refresh(new_opportunity)
    return new_opportunity


@app.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    stage: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity)
    if stage:
        query = query.filter(Opportunity.stage == stage)
    return query.offset(skip).limit(limit).all()


@app.post("/leads/{lead_id}/assign")
async def assign_lead(lead_id: str, assigned_to: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.assigned_to = assigned_to
    lead.status = "contacted"
    db.commit()
    return {"lead_id": lead.id, "assigned_to": lead.assigned_to, "status": lead.status}


@app.post("/leads/{lead_id}/qualify")
async def qualify_lead(lead_id: str, qualified: bool, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = "qualified" if qualified else "disqualified"
    db.commit()
    return {"lead_id": lead.id, "status": lead.status}


@app.get("/")
async def root():
    return {"service": "crm", "version": "0.1.0"}

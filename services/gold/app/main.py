from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(
    title="Gold Lending Service",
    description="AI-powered Gold Lending Operating System - Phase 1: Product Configuration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Product(BaseModel):
    id: str
    name: str
    description: str | None = None
    max_ltv: float | None = None
    min_weight: float | None = None
    max_weight: float | None = None


# In-memory product store for initial scaffolding
_PRODUCTS: List[Product] = [
    Product(id="gold-001", name="Gold Jewel Loan", description="Standard branch gold loan", max_ltv=0.75, min_weight=5.0, max_weight=1000.0),
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/gold/products", response_model=List[Product])
def list_products():
    return _PRODUCTS


@app.post("/api/v1/gold/products", response_model=Product)
def create_product(p: Product):
    # simple uniqueness check
    if any(x.id == p.id for x in _PRODUCTS):
        raise HTTPException(status_code=400, detail="product id exists")
    _PRODUCTS.append(p)
    return p


@app.get("/api/v1/gold/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    for p in _PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="not found")
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GoldLoanApplication(Base):
    __tablename__ = "gold_loan_applications"

    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    branch_id = Column(String, index=True, nullable=True)
    requested_amount = Column(Float)
    gold_rate_per_gram = Column(Float)
    ltv_percent = Column(Float, default=75.0)
    eligible_amount = Column(Float, default=0.0)
    approved_amount = Column(Float, nullable=True)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GoldOrnament(Base):
    __tablename__ = "gold_ornaments"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("gold_loan_applications.id"), index=True)
    ornament_type = Column(String)
    description = Column(String, nullable=True)
    gross_weight_grams = Column(Float)
    stone_weight_grams = Column(Float, default=0.0)
    net_weight_grams = Column(Float)
    purity_karat = Column(Float, default=22.0)
    purity_percent = Column(Float, default=91.6)
    appraised_value = Column(Float)
    cataloged_at = Column(DateTime, default=datetime.utcnow)


class VaultPacket(Base):
    __tablename__ = "gold_vault_packets"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("gold_loan_applications.id"), unique=True)
    packet_number = Column(String, unique=True, index=True)
    branch_id = Column(String, index=True, nullable=True)
    vault_location = Column(String)
    sealed_by_user_id = Column(String)
    seal_reference = Column(String)
    status = Column(String, default="stored")
    stored_at = Column(DateTime, default=datetime.utcnow)


class AuctionCase(Base):
    __tablename__ = "gold_auction_cases"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("gold_loan_applications.id"), index=True)
    trigger_reason = Column(String)
    reserve_price = Column(Float)
    auction_date = Column(DateTime)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldLoanCreate(BaseModel):
    customer_id: str
    branch_id: Optional[str] = None
    requested_amount: float = Field(gt=0)
    gold_rate_per_gram: float = Field(gt=0)
    ltv_percent: float = Field(default=75.0, gt=0, le=90)


class GoldLoanResponse(BaseModel):
    id: str
    customer_id: str
    branch_id: Optional[str]
    requested_amount: float
    gold_rate_per_gram: float
    ltv_percent: float
    eligible_amount: float
    approved_amount: Optional[float]
    status: str

    class Config:
        from_attributes = True


class OrnamentCreate(BaseModel):
    ornament_type: str
    description: Optional[str] = None
    gross_weight_grams: float = Field(gt=0)
    stone_weight_grams: float = Field(default=0, ge=0)
    purity_karat: float = Field(default=22, gt=0, le=24)


class OrnamentResponse(BaseModel):
    id: str
    application_id: str
    ornament_type: str
    description: Optional[str]
    gross_weight_grams: float
    stone_weight_grams: float
    net_weight_grams: float
    purity_karat: float
    purity_percent: float
    appraised_value: float

    class Config:
        from_attributes = True


class PurityTestRequest(BaseModel):
    purity_karat: float = Field(gt=0, le=24)
    notes: Optional[str] = None


class VaultPacketCreate(BaseModel):
    vault_location: str
    sealed_by_user_id: str
    seal_reference: str


class VaultPacketResponse(BaseModel):
    id: str
    application_id: str
    packet_number: str
    branch_id: Optional[str]
    vault_location: str
    sealed_by_user_id: str
    seal_reference: str
    status: str
    stored_at: datetime

    class Config:
        from_attributes = True


class AuctionCreate(BaseModel):
    trigger_reason: str
    auction_date: datetime
    reserve_price: Optional[float] = None


class AuctionResponse(BaseModel):
    id: str
    application_id: str
    trigger_reason: str
    reserve_price: float
    auction_date: datetime
    status: str

    class Config:
        from_attributes = True


app = FastAPI(title="gold-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


# Import and include routers
from .routers import products, journey, appraisal, catalog, vault, loan, repayment, collections
from .models import product as product_models
from .models import journey as journey_models
from .models import appraisal as appraisal_models
from .models import catalog as catalog_models
from .models import vault as vault_models
from .models import loan as loan_models
from .models import repayment as repayment_models
from .models import collections as collections_models

# Override the get_db dependency in routers
products.get_db = get_db
journey.get_db = get_db
appraisal.get_db = get_db
catalog.get_db = get_db
vault.get_db = get_db
loan.get_db = get_db
repayment.get_db = get_db
collections.get_db = get_db

# Include routers
app.include_router(products.router, prefix="/api/v1/gold")
app.include_router(journey.router, prefix="/api/v1/gold")
app.include_router(appraisal.router, prefix="/api/v1/gold")
app.include_router(catalog.router, prefix="/api/v1/gold")
app.include_router(vault.router, prefix="/api/v1/gold")
app.include_router(loan.router, prefix="/api/v1/gold")
app.include_router(repayment.router, prefix="/api/v1/gold")
app.include_router(collections.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gold"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _get_application(application_id: str, db: Session) -> GoldLoanApplication:
    application = db.query(GoldLoanApplication).filter(GoldLoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Gold loan application not found")
    return application


def _recalculate_application_value(application: GoldLoanApplication, db: Session) -> None:
    ornaments = db.query(GoldOrnament).filter(GoldOrnament.application_id == application.id).all()
    total_value = sum(ornament.appraised_value or 0 for ornament in ornaments)
    application.eligible_amount = round(total_value * application.ltv_percent / 100, 2)
    application.approved_amount = min(application.requested_amount, application.eligible_amount) if ornaments else None
    if ornaments and application.status == "draft":
        application.status = "appraised"


@app.post("/gold-loans", response_model=GoldLoanResponse)
async def create_gold_loan(application: GoldLoanCreate, db: Session = Depends(get_db)):
    record = GoldLoanApplication(
        id=str(uuid4()),
        customer_id=application.customer_id,
        branch_id=application.branch_id,
        requested_amount=application.requested_amount,
        gold_rate_per_gram=application.gold_rate_per_gram,
        ltv_percent=application.ltv_percent,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/gold-loans", response_model=List[GoldLoanResponse])
async def list_gold_loans(
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GoldLoanApplication)
    if customer_id:
        query = query.filter(GoldLoanApplication.customer_id == customer_id)
    if branch_id:
        query = query.filter(GoldLoanApplication.branch_id == branch_id)
    if status:
        query = query.filter(GoldLoanApplication.status == status)
    return query.order_by(GoldLoanApplication.created_at.desc()).all()


@app.post("/gold-loans/{application_id}/ornaments", response_model=OrnamentResponse)
async def catalog_ornament(application_id: str, ornament: OrnamentCreate, db: Session = Depends(get_db)):
    application = _get_application(application_id, db)
    net_weight = round(max(0.0, ornament.gross_weight_grams - ornament.stone_weight_grams), 3)
    purity_percent = round((ornament.purity_karat / 24) * 100, 2)
    appraised_value = round(net_weight * application.gold_rate_per_gram * purity_percent / 100, 2)
    record = GoldOrnament(
        id=str(uuid4()),
        application_id=application.id,
        ornament_type=ornament.ornament_type,
        description=ornament.description,
        gross_weight_grams=ornament.gross_weight_grams,
        stone_weight_grams=ornament.stone_weight_grams,
        net_weight_grams=net_weight,
        purity_karat=ornament.purity_karat,
        purity_percent=purity_percent,
        appraised_value=appraised_value,
    )
    db.add(record)
    _recalculate_application_value(application, db)
    db.commit()
    db.refresh(record)
    return record


@app.post("/ornaments/{ornament_id}/purity-test", response_model=OrnamentResponse)
async def record_purity_test(ornament_id: str, request: PurityTestRequest, db: Session = Depends(get_db)):
    ornament = db.query(GoldOrnament).filter(GoldOrnament.id == ornament_id).first()
    if not ornament:
        raise HTTPException(status_code=404, detail="Ornament not found")
    application = _get_application(ornament.application_id, db)
    ornament.purity_karat = request.purity_karat
    ornament.purity_percent = round((request.purity_karat / 24) * 100, 2)
    ornament.appraised_value = round(ornament.net_weight_grams * application.gold_rate_per_gram * ornament.purity_percent / 100, 2)
    _recalculate_application_value(application, db)
    db.commit()
    db.refresh(ornament)
    return ornament


@app.post("/gold-loans/{application_id}/vault", response_model=VaultPacketResponse)
async def store_in_vault(application_id: str, packet: VaultPacketCreate, db: Session = Depends(get_db)):
    application = _get_application(application_id, db)
    existing = db.query(VaultPacket).filter(VaultPacket.application_id == application_id).first()
    if existing:
        return existing
    if not application.approved_amount:
        raise HTTPException(status_code=400, detail="Application must be appraised before vault storage")
    record = VaultPacket(
        id=str(uuid4()),
        application_id=application.id,
        packet_number=f"GLP-{str(uuid4())[:10].upper()}",
        branch_id=application.branch_id,
        vault_location=packet.vault_location,
        sealed_by_user_id=packet.sealed_by_user_id,
        seal_reference=packet.seal_reference,
    )
    application.status = "vaulted"
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/gold-loans/{application_id}/receipt")
async def get_customer_receipt(application_id: str, db: Session = Depends(get_db)):
    application = _get_application(application_id, db)
    ornaments = db.query(GoldOrnament).filter(GoldOrnament.application_id == application_id).all()
    packet = db.query(VaultPacket).filter(VaultPacket.application_id == application_id).first()
    return {
        "application_id": application.id,
        "customer_id": application.customer_id,
        "branch_id": application.branch_id,
        "status": application.status,
        "requested_amount": application.requested_amount,
        "eligible_amount": application.eligible_amount,
        "approved_amount": application.approved_amount,
        "ornaments": ornaments,
        "vault_packet": packet,
        "issued_at": datetime.utcnow(),
    }


@app.post("/gold-loans/{application_id}/auction", response_model=AuctionResponse)
async def create_auction_case(application_id: str, auction: AuctionCreate, db: Session = Depends(get_db)):
    application = _get_application(application_id, db)
    reserve_price = auction.reserve_price or round((application.eligible_amount or application.requested_amount) * 1.05, 2)
    record = AuctionCase(
        id=str(uuid4()),
        application_id=application.id,
        trigger_reason=auction.trigger_reason,
        reserve_price=reserve_price,
        auction_date=auction.auction_date,
    )
    application.status = "auction_scheduled"
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/")
async def root():
    return {"service": "gold", "version": "0.1.0"}


# Backwards-compatible product endpoints (in-memory stub)
from typing import List as _List


class Product(BaseModel):
    id: str
    name: str
    description: str | None = None
    max_ltv: float | None = None
    min_weight: float | None = None
    max_weight: float | None = None


_PRODUCTS: _List[Product] = [
    Product(id="gold-001", name="Gold Jewel Loan", description="Standard branch gold loan", max_ltv=0.75, min_weight=5.0, max_weight=1000.0),
]


@app.get("/api/v1/gold/products", response_model=_List[Product])
async def list_products_stub():
    return _PRODUCTS


@app.post("/api/v1/gold/products", response_model=Product)
async def create_product_stub(p: Product):
    if any(x.id == p.id for x in _PRODUCTS):
        raise HTTPException(status_code=400, detail="product id exists")
    _PRODUCTS.append(p)
    return p


@app.get("/api/v1/gold/products/{product_id}", response_model=Product)
async def get_product_stub(product_id: str):
    for p in _PRODUCTS:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="not found")

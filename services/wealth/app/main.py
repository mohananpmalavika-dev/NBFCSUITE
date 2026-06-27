from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, JSON, String, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MutualFundScheme(Base):
    __tablename__ = "wealth_mutual_fund_schemes"
    __table_args__ = (UniqueConstraint("tenant_id", "scheme_code", name="uq_wealth_scheme_tenant_code"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    scheme_code = Column(String, index=True, nullable=False)
    scheme_name = Column(String, nullable=False)
    fund_house = Column(String)
    category = Column(String)
    risk_level = Column(String, default="moderate")
    nav = Column(Float, default=10.0)
    expense_ratio = Column(Float, default=0.0)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WealthInvestment(Base):
    __tablename__ = "wealth_investments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    scheme_id = Column(String, index=True, nullable=False)
    transaction_type = Column(String, default="purchase")
    amount = Column(Float, default=0.0)
    nav = Column(Float, default=0.0)
    units = Column(Float, default=0.0)
    folio_number = Column(String, index=True, nullable=True)
    reference = Column(String, index=True, nullable=True)
    status = Column(String, default="posted")
    transaction_date = Column(DateTime, default=datetime.utcnow)


class SIPMandate(Base):
    __tablename__ = "wealth_sip_mandates"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    scheme_id = Column(String, index=True, nullable=False)
    amount = Column(Float)
    frequency = Column(String, default="monthly")
    start_date = Column(DateTime)
    next_run_date = Column(DateTime)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class SchemeCreate(BaseModel):
    tenant_id: str
    scheme_code: str
    scheme_name: str
    fund_house: str
    category: str
    risk_level: str = "moderate"
    nav: float = Field(default=10.0, gt=0)
    expense_ratio: float = Field(default=0.0, ge=0)


class SchemeResponse(BaseModel):
    id: str
    tenant_id: str
    scheme_code: str
    scheme_name: str
    fund_house: str
    category: str
    risk_level: str
    nav: float
    expense_ratio: float
    is_active: str

    class Config:
        from_attributes = True


class NAVUpdate(BaseModel):
    nav: float = Field(gt=0)


class InvestmentCreate(BaseModel):
    tenant_id: str
    customer_id: str
    scheme_code: str
    amount: float = Field(gt=0)
    transaction_type: str = Field(default="purchase", pattern="^(purchase|redemption)$")
    folio_number: Optional[str] = None
    reference: Optional[str] = None


class InvestmentResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    scheme_id: str
    transaction_type: str
    amount: float
    nav: float
    units: float
    folio_number: Optional[str]
    reference: Optional[str]
    status: str
    transaction_date: datetime

    class Config:
        from_attributes = True


class SIPCreate(BaseModel):
    tenant_id: str
    customer_id: str
    scheme_code: str
    amount: float = Field(gt=0)
    frequency: str = Field(default="monthly", pattern="^(monthly|quarterly)$")
    start_date: Optional[datetime] = None


class SIPResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    scheme_id: str
    amount: float
    frequency: str
    start_date: datetime
    next_run_date: datetime
    status: str

    class Config:
        from_attributes = True


app = FastAPI(title="wealth-service", version="0.1.0")


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
    return {"status": "ok", "service": "wealth"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _scheme_by_code(tenant_id: str, scheme_code: str, db: Session) -> MutualFundScheme:
    scheme = (
        db.query(MutualFundScheme)
        .filter(MutualFundScheme.tenant_id == tenant_id, MutualFundScheme.scheme_code == scheme_code)
        .first()
    )
    if not scheme:
        raise HTTPException(status_code=404, detail="Mutual fund scheme not found for tenant")
    if str(scheme.is_active).lower() not in {"true", "1", "yes", "active"}:
        raise HTTPException(status_code=400, detail="Scheme is inactive")
    return scheme


def _portfolio_positions(tenant_id: str, customer_id: str, db: Session) -> list[dict]:
    schemes = {
        scheme.id: scheme
        for scheme in db.query(MutualFundScheme).filter(MutualFundScheme.tenant_id == tenant_id).all()
    }
    positions: dict[str, dict] = {}
    investments = (
        db.query(WealthInvestment)
        .filter(WealthInvestment.tenant_id == tenant_id, WealthInvestment.customer_id == customer_id)
        .all()
    )
    for investment in investments:
        scheme = schemes.get(investment.scheme_id)
        if not scheme:
            continue
        if scheme.id not in positions:
            positions[scheme.id] = {
                "scheme_id": scheme.id,
                "scheme_code": scheme.scheme_code,
                "scheme_name": scheme.scheme_name,
                "category": scheme.category,
                "risk_level": scheme.risk_level,
                "units": 0.0,
                "invested_amount": 0.0,
                "current_value": 0.0,
            }
        sign = -1 if investment.transaction_type == "redemption" else 1
        positions[scheme.id]["units"] += sign * (investment.units or 0.0)
        positions[scheme.id]["invested_amount"] += sign * (investment.amount or 0.0)

    rows = []
    for position in positions.values():
        scheme = schemes[position["scheme_id"]]
        position["units"] = round(position["units"], 4)
        position["invested_amount"] = round(position["invested_amount"], 2)
        position["current_value"] = round(position["units"] * scheme.nav, 2)
        position["unrealized_gain"] = round(position["current_value"] - position["invested_amount"], 2)
        rows.append(position)
    return rows


@app.post("/schemes", response_model=SchemeResponse)
async def create_scheme(payload: SchemeCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(MutualFundScheme)
        .filter(MutualFundScheme.tenant_id == payload.tenant_id, MutualFundScheme.scheme_code == payload.scheme_code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Scheme code already exists for tenant")
    scheme = MutualFundScheme(id=str(uuid4()), **payload.model_dump())
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return scheme


@app.get("/schemes", response_model=List[SchemeResponse])
async def list_schemes(
    tenant_id: str = Query(...),
    category: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(MutualFundScheme).filter(MutualFundScheme.tenant_id == tenant_id)
    if category:
        query = query.filter(MutualFundScheme.category == category)
    if risk_level:
        query = query.filter(MutualFundScheme.risk_level == risk_level)
    return query.order_by(MutualFundScheme.scheme_name.asc()).all()


@app.post("/schemes/{scheme_code}/nav", response_model=SchemeResponse)
async def update_nav(
    scheme_code: str,
    payload: NAVUpdate,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    scheme = _scheme_by_code(tenant_id, scheme_code, db)
    scheme.nav = payload.nav
    scheme.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scheme)
    return scheme


@app.post("/investments", response_model=InvestmentResponse)
async def create_investment(payload: InvestmentCreate, db: Session = Depends(get_db)):
    scheme = _scheme_by_code(payload.tenant_id, payload.scheme_code, db)
    units = round(payload.amount / scheme.nav, 4)
    investment = WealthInvestment(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        customer_id=payload.customer_id,
        scheme_id=scheme.id,
        transaction_type=payload.transaction_type,
        amount=payload.amount,
        nav=scheme.nav,
        units=units,
        folio_number=payload.folio_number,
        reference=payload.reference or f"WM-{str(uuid4())[:10].upper()}",
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment


@app.get("/investments", response_model=List[InvestmentResponse])
async def list_investments(
    tenant_id: str = Query(...),
    customer_id: Optional[str] = Query(None),
    scheme_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(WealthInvestment).filter(WealthInvestment.tenant_id == tenant_id)
    if customer_id:
        query = query.filter(WealthInvestment.customer_id == customer_id)
    if scheme_id:
        query = query.filter(WealthInvestment.scheme_id == scheme_id)
    return query.order_by(WealthInvestment.transaction_date.desc()).all()


@app.post("/sips", response_model=SIPResponse)
async def create_sip(payload: SIPCreate, db: Session = Depends(get_db)):
    scheme = _scheme_by_code(payload.tenant_id, payload.scheme_code, db)
    start_date = payload.start_date or datetime.utcnow()
    sip = SIPMandate(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        customer_id=payload.customer_id,
        scheme_id=scheme.id,
        amount=payload.amount,
        frequency=payload.frequency,
        start_date=start_date,
        next_run_date=start_date,
    )
    db.add(sip)
    db.commit()
    db.refresh(sip)
    return sip


@app.get("/sips", response_model=List[SIPResponse])
async def list_sips(
    tenant_id: str = Query(...),
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(SIPMandate).filter(SIPMandate.tenant_id == tenant_id)
    if customer_id:
        query = query.filter(SIPMandate.customer_id == customer_id)
    if status:
        query = query.filter(SIPMandate.status == status)
    return query.order_by(SIPMandate.created_at.desc()).all()


@app.post("/sips/{sip_id}/run", response_model=InvestmentResponse)
async def run_sip(sip_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    sip = db.query(SIPMandate).filter(SIPMandate.id == sip_id, SIPMandate.tenant_id == tenant_id).first()
    if not sip:
        raise HTTPException(status_code=404, detail="SIP mandate not found for tenant")
    if sip.status != "active":
        raise HTTPException(status_code=400, detail="SIP mandate is not active")
    scheme = db.query(MutualFundScheme).filter(MutualFundScheme.id == sip.scheme_id, MutualFundScheme.tenant_id == tenant_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found for tenant")
    investment = WealthInvestment(
        id=str(uuid4()),
        tenant_id=tenant_id,
        customer_id=sip.customer_id,
        scheme_id=sip.scheme_id,
        transaction_type="purchase",
        amount=sip.amount,
        nav=scheme.nav,
        units=round(sip.amount / scheme.nav, 4),
        reference=f"SIP-{str(uuid4())[:10].upper()}",
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment


@app.get("/portfolio/{customer_id}")
async def portfolio(customer_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    positions = _portfolio_positions(tenant_id, customer_id, db)
    invested = round(sum(row["invested_amount"] for row in positions), 2)
    current_value = round(sum(row["current_value"] for row in positions), 2)
    by_category: dict[str, float] = {}
    for row in positions:
        by_category[row["category"]] = round(by_category.get(row["category"], 0.0) + row["current_value"], 2)
    return {
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "positions": positions,
        "invested_amount": invested,
        "current_value": current_value,
        "unrealized_gain": round(current_value - invested, 2),
        "allocation_by_category": by_category,
        "generated_at": datetime.utcnow(),
    }


@app.get("/")
async def root():
    return {"service": "wealth", "version": "0.1.0"}

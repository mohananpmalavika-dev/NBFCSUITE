from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from ..models import Customer, CustomerAddress, KYCDocument, CustomerFinancialProfile
from ..schemas import (
    CustomerCreate, CustomerResponse, CustomerUpdate, AddressCreate,
    FinancialProfileUpdate, FinancialProfileResponse
)
from ..db import get_db
from uuid import uuid4

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(
        (Customer.email == customer.email) | (Customer.phone == customer.phone)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")

    new_customer = Customer(
        id=str(uuid4()),
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        dob=customer.dob,
        gender=customer.gender,
        branch_id=customer.branch_id,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, update_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_fields = update_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("")
async def list_customers(skip: int = Query(0), limit: int = Query(20), kyc_status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Customer)
    if kyc_status:
        query = query.filter(Customer.kyc_status == kyc_status)
    total = query.count()
    customers = query.offset(skip).limit(limit).all()
    return {"items": customers, "total": total, "skip": skip, "limit": limit}


@router.post("/{customer_id}/addresses")
async def add_address(customer_id: str, address: AddressCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    new_address = CustomerAddress(
        id=str(uuid4()),
        customer_id=customer_id,
        address_type=address.address_type,
        street=address.street,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        is_primary=address.is_primary,
    )
    db.add(new_address)
    db.commit()
    return {"message": "Address added successfully"}


@router.get("/{customer_id}/addresses")
async def get_addresses(customer_id: str, db: Session = Depends(get_db)):
    addresses = db.query(CustomerAddress).filter(CustomerAddress.customer_id == customer_id).all()
    return {"addresses": addresses}


@router.post("/{customer_id}/kyc-documents")
async def upload_kyc_document(customer_id: str, document_type: str, document_number: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    document_url = f"s3://nbfcsuite-kyc/{customer_id}/{file.filename}"
    kyc_doc = KYCDocument(
        id=str(uuid4()),
        customer_id=customer_id,
        document_type=document_type,
        document_number=document_number,
        document_url=document_url,
        verification_status="pending",
    )
    db.add(kyc_doc)
    db.commit()
    all_docs = db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).count()
    if all_docs >= 2:
        customer.kyc_status = "submitted"
        db.commit()
    return {"message": "Document uploaded successfully", "document_url": document_url, "kyc_status": customer.kyc_status}


@router.get("/{customer_id}/kyc-documents")
async def get_kyc_documents(customer_id: str, db: Session = Depends(get_db)):
    documents = db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).all()
    return {"customer_id": customer_id, "documents": documents}


@router.get("/{customer_id}/financial-profile", response_model=FinancialProfileResponse)
async def get_financial_profile(customer_id: str, db: Session = Depends(get_db)):
    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile


@router.post("/{customer_id}/financial-profile", response_model=FinancialProfileResponse)
async def create_or_update_financial_profile(customer_id: str, profile_data: FinancialProfileUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        profile = CustomerFinancialProfile(id=str(uuid4()), customer_id=customer_id)
        db.add(profile)

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{customer_id}/risk-profile", response_model=FinancialProfileResponse)
async def get_risk_profile(customer_id: str, db: Session = Depends(get_db)):
    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile






@router.put("/{customer_id}/risk-profile", response_model=FinancialProfileResponse)
async def update_risk_profile(customer_id: str, profile_data: FinancialProfileUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = profile_data.model_dump(exclude_unset=True)
    allowed_fields = {"assets", "liabilities", "behavior_score", "risk_level", "credit_score"}
    unexpected_fields = set(update_data) - allowed_fields
    if unexpected_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Risk profile only accepts: {', '.join(sorted(allowed_fields))}",
        )

    risk_level = update_data.get("risk_level")
    if risk_level and risk_level not in {"low", "medium", "high", "critical"}:
        raise HTTPException(
            status_code=422,
            detail="risk_level must be one of low, medium, high, critical",
        )

    credit_score = update_data.get("credit_score")
    if credit_score is not None and not 300 <= credit_score <= 900:
        raise HTTPException(status_code=422, detail="credit_score must be between 300 and 900")

    try:
        profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
        if not profile:
            profile = CustomerFinancialProfile(id=str(uuid4()), customer_id=customer_id)
            db.add(profile)

        for key, value in update_data.items():
            setattr(profile, key, value)
        profile.last_updated = datetime.utcnow()

        db.commit()
        db.refresh(profile)
    except Exception:
        db.rollback()
        raise

    return profile


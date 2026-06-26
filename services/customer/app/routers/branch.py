from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ..models import BranchOffice, AreaOffice, Customer, CustomerBranchTransaction
from ..schemas import (
    AssignBranchRequest,
    BranchOfficeCreate,
    BranchResponse,
    BranchScopeResponse,
    BranchTransactionCreate,
    BranchTransactionResponse,
    BranchUpdate,
)
from ..db import get_db
from uuid import uuid4

router = APIRouter(prefix="", tags=["branches"])


def _set_active(value):
    if value is None:
        return value
    return str(value).lower()


@router.post("/branches", response_model=BranchResponse)
async def create_branch(branch: BranchOfficeCreate, db: Session = Depends(get_db)):
    area_office = db.query(AreaOffice).filter(AreaOffice.id == branch.area_office_id).first()
    if not area_office:
        raise HTTPException(status_code=404, detail="Area office not found")

    new_branch = BranchOffice(
        id=str(uuid4()),
        area_office_id=branch.area_office_id,
        name=branch.name,
        code=branch.code,
        branch_type=branch.branch_type,
        address=branch.address,
        city=branch.city,
        state=branch.state,
        postal_code=branch.postal_code,
        country=branch.country,
        contact_email=branch.contact_email,
        contact_phone=branch.contact_phone,
        is_active=str(branch.is_active).lower(),
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch


@router.get("/branches", response_model=list[BranchResponse])
async def list_branches(
    area_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(BranchOffice)
    if area_id:
        query = query.filter(BranchOffice.area_office_id == area_id)
    return query.offset(skip).limit(limit).all()


@router.get("/branches/{branch_id}", response_model=BranchResponse)
async def get_branch(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.put("/branches/{branch_id}", response_model=BranchResponse)
async def update_branch(branch_id: str, update: BranchUpdate, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = update.model_dump(exclude_unset=True)
    area_id = update_data.pop("area_id", None)
    if area_id:
        area = db.query(AreaOffice).filter(AreaOffice.id == area_id).first()
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        branch.area_office_id = area_id

    for field, value in update_data.items():
        if field == "is_active":
            value = _set_active(value)
        setattr(branch, field, value)

    db.commit()
    db.refresh(branch)
    return branch


@router.delete("/branches/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(branch)
    db.commit()
    return None


@router.get("/branches/{branch_id}/scope", response_model=BranchScopeResponse)
async def get_branch_scope(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    area = branch.area_office
    region = area.regional_office
    zone = region.zonal_office
    organization = zone.head_office
    return {
        "organization_id": organization.id,
        "organization_name": organization.name,
        "zone_id": zone.id,
        "zone_name": zone.name,
        "region_id": region.id,
        "region_name": region.name,
        "area_id": area.id,
        "area_name": area.name,
        "branch_id": branch.id,
        "branch_name": branch.name,
    }


@router.post("/customers/{customer_id}/assign-branch")
async def assign_customer_branch(
    customer_id: str,
    assignment: AssignBranchRequest | None = Body(None),
    branch_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    selected_branch_id = branch_id or (assignment.branch_id if assignment else None)
    if not selected_branch_id:
        raise HTTPException(status_code=422, detail="branch_id is required")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    branch = db.query(BranchOffice).filter(BranchOffice.id == selected_branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    customer.branch_id = selected_branch_id
    db.commit()
    db.refresh(customer)
    return {"message": "Customer assigned to branch", "branch_id": selected_branch_id}


@router.post("/customers/{customer_id}/transactions", response_model=BranchTransactionResponse)
async def create_customer_transaction(customer_id: str, transaction: BranchTransactionCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    branch_id = customer.branch_id
    if not branch_id:
        raise HTTPException(status_code=400, detail="Customer is not assigned to a branch")

    new_transaction = CustomerBranchTransaction(
        id=str(uuid4()),
        customer_id=customer_id,
        branch_id=branch_id,
        transaction_type=transaction.transaction_type,
        amount=str(transaction.amount),
        currency=transaction.currency,
        status=transaction.status,
        metadata_=transaction.metadata,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@router.get("/branches/{branch_id}/transactions", response_model=list[BranchTransactionResponse])
async def get_branch_transactions(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    transactions = db.query(CustomerBranchTransaction).filter(CustomerBranchTransaction.branch_id == branch_id).all()
    return transactions


@router.get("/customers/{customer_id}/transactions", response_model=list[BranchTransactionResponse])
async def get_customer_transactions(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    transactions = db.query(CustomerBranchTransaction).filter(CustomerBranchTransaction.customer_id == customer_id).all()
    return transactions

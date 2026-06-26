from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import BranchOffice, AreaOffice, Customer, CustomerBranchTransaction
from ..schemas import BranchOfficeCreate, BranchResponse, BranchTransactionCreate, BranchTransactionResponse
from ..db import get_db
from uuid import uuid4

router = APIRouter(prefix="", tags=["branches"])


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


@router.get("/branches/{branch_id}", response_model=BranchResponse)
async def get_branch(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.post("/customers/{customer_id}/assign-branch")
async def assign_customer_branch(customer_id: str, branch_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    customer.branch_id = branch_id
    db.commit()
    db.refresh(customer)
    return {"message": "Customer assigned to branch", "branch_id": branch_id}


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
        metadata=transaction.metadata,
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

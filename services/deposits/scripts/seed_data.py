"""
Seed Script - Load Default Data
Populates database with sample products, accounts, and test data
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, timedelta
import uuid

from app.database import SessionLocal, init_db
from app.models import (
    DepositProduct, InterestSlab, DepositAccount, 
    Nominee, DepositType, InterestMethod, PayoutFrequency,
    DepositAccountStatus
)


def seed_products(db: Session):
    """Seed default deposit products"""
    print("🌱 Seeding deposit products...")
    
    products = [
        {
            "id": uuid.uuid4(),
            "code": "FD_REGULAR",
            "name": "Fixed Deposit - Regular",
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "min_amount": Decimal('10000'),
            "max_amount": Decimal('10000000'),
            "min_tenure_days": 90,
            "max_tenure_days": 3650,
            "interest_method": InterestMethod.SIMPLE,
            "default_interest_rate": Decimal('7.0'),
            "senior_citizen_rate_bonus": Decimal('0.5'),
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "premature_allowed": True,
            "premature_penalty_percentage": Decimal('1.0'),
            "auto_renewal_allowed": True,
            "tds_applicable": True,
            "tds_rate": Decimal('10.0'),
            "status": "ACTIVE",
            "effective_from": date.today()
        },
        {
            "id": uuid.uuid4(),
            "code": "FD_SENIOR_CITIZEN",
            "name": "Fixed Deposit - Senior Citizen",
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "min_amount": Decimal('10000'),
            "max_amount": Decimal('10000000'),
            "min_tenure_days": 180,
            "max_tenure_days": 3650,
            "interest_method": InterestMethod.SIMPLE,
            "default_interest_rate": Decimal('7.5'),
            "senior_citizen_rate_bonus": Decimal('0.5'),
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "premature_allowed": True,
            "auto_renewal_allowed": True,
            "tds_applicable": True,
            "status": "ACTIVE",
            "effective_from": date.today()
        },
        {
            "id": uuid.uuid4(),
            "code": "FD_MONTHLY_INTEREST",
            "name": "Fixed Deposit - Monthly Interest",
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "min_amount": Decimal('25000'),
            "max_amount": Decimal('10000000'),
            "min_tenure_days": 365,
            "max_tenure_days": 3650,
            "interest_method": InterestMethod.SIMPLE,
            "default_interest_rate": Decimal('6.75'),
            "senior_citizen_rate_bonus": Decimal('0.5'),
            "payout_frequency": PayoutFrequency.MONTHLY,
            "premature_allowed": True,
            "auto_renewal_allowed": True,
            "tds_applicable": True,
            "status": "ACTIVE",
            "effective_from": date.today()
        },
        {
            "id": uuid.uuid4(),
            "code": "FD_CUMULATIVE",
            "name": "Fixed Deposit - Cumulative",
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "min_amount": Decimal('10000'),
            "max_amount": Decimal('10000000'),
            "min_tenure_days": 365,
            "max_tenure_days": 3650,
            "interest_method": InterestMethod.COMPOUND_QUARTERLY,
            "default_interest_rate": Decimal('7.25'),
            "senior_citizen_rate_bonus": Decimal('0.5'),
            "payout_frequency": PayoutFrequency.CUMULATIVE,
            "premature_allowed": True,
            "auto_renewal_allowed": True,
            "tds_applicable": True,
            "status": "ACTIVE",
            "effective_from": date.today()
        },
        {
            "id": uuid.uuid4(),
            "code": "RD_REGULAR",
            "name": "Recurring Deposit - Regular",
            "deposit_type": DepositType.RECURRING_DEPOSIT,
            "min_amount": Decimal('500'),
            "max_amount": Decimal('100000'),
            "min_tenure_days": 180,
            "max_tenure_days": 3650,
            "interest_method": InterestMethod.SIMPLE,
            "default_interest_rate": Decimal('7.0'),
            "senior_citizen_rate_bonus": Decimal('0.5'),
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "premature_allowed": True,
            "auto_renewal_allowed": False,
            "tds_applicable": True,
            "status": "ACTIVE",
            "effective_from": date.today()
        }
    ]
    
    for product_data in products:
        existing = db.query(DepositProduct).filter(
            DepositProduct.code == product_data["code"]
        ).first()
        
        if not existing:
            product = DepositProduct(**product_data)
            db.add(product)
            print(f"  ✅ Created: {product.name}")
        else:
            print(f"  ⏭️  Skipped: {product_data['name']} (already exists)")
    
    db.commit()
    print(f"✅ Products seeded!\n")


def seed_interest_slabs(db: Session):
    """Seed interest rate slabs"""
    print("🌱 Seeding interest slabs...")
    
    # Get FD_REGULAR product
    product = db.query(DepositProduct).filter(
        DepositProduct.code == "FD_REGULAR"
    ).first()
    
    if not product:
        print("  ⚠️  FD_REGULAR product not found")
        return
    
    slabs = [
        {
            "product_id": product.id,
            "min_amount": Decimal('10000'),
            "max_amount": Decimal('99999'),
            "min_tenure_days": 90,
            "max_tenure_days": 179,
            "interest_rate": Decimal('6.5'),
            "senior_citizen_rate": Decimal('7.0')
        },
        {
            "product_id": product.id,
            "min_amount": Decimal('10000'),
            "max_amount": Decimal('99999'),
            "min_tenure_days": 180,
            "max_tenure_days": 364,
            "interest_rate": Decimal('7.0'),
            "senior_citizen_rate": Decimal('7.5')
        },
        {
            "product_id": product.id,
            "min_amount": Decimal('100000'),
            "max_amount": Decimal('499999'),
            "min_tenure_days": 365,
            "max_tenure_days": 729,
            "interest_rate": Decimal('7.5'),
            "senior_citizen_rate": Decimal('8.0')
        },
        {
            "product_id": product.id,
            "min_amount": Decimal('500000'),
            "max_amount": None,
            "min_tenure_days": 365,
            "max_tenure_days": None,
            "interest_rate": Decimal('8.0'),
            "senior_citizen_rate": Decimal('8.5')
        }
    ]
    
    for slab_data in slabs:
        slab = InterestSlab(**slab_data)
        db.add(slab)
        print(f"  ✅ Added slab: ₹{slab.min_amount} - ₹{slab.max_amount or 'No Limit'}, {slab.interest_rate}%")
    
    db.commit()
    print(f"✅ Interest slabs seeded!\n")


def seed_sample_accounts(db: Session):
    """Seed sample deposit accounts for testing"""
    print("🌱 Seeding sample accounts...")
    
    # Get products
    fd_regular = db.query(DepositProduct).filter(
        DepositProduct.code == "FD_REGULAR"
    ).first()
    
    rd_regular = db.query(DepositProduct).filter(
        DepositProduct.code == "RD_REGULAR"
    ).first()
    
    if not fd_regular or not rd_regular:
        print("  ⚠️  Products not found")
        return
    
    # Sample FD accounts
    fd_accounts = [
        {
            "account_number": "FD20240101001",
            "customer_id": uuid.uuid4(),
            "cif_number": "CIF001",
            "product_id": fd_regular.id,
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "principal_amount": Decimal('100000'),
            "interest_rate": Decimal('7.0'),
            "is_senior_citizen": False,
            "open_date": date.today() - timedelta(days=30),
            "maturity_date": date.today() + timedelta(days=335),
            "maturity_amount": Decimal('107000'),
            "interest_method": InterestMethod.SIMPLE,
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "status": DepositAccountStatus.ACTIVE,
            "branch_code": "BR001"
        },
        {
            "account_number": "FD20240101002",
            "customer_id": uuid.uuid4(),
            "cif_number": "CIF002",
            "product_id": fd_regular.id,
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "principal_amount": Decimal('500000'),
            "interest_rate": Decimal('8.0'),
            "is_senior_citizen": True,
            "open_date": date.today() - timedelta(days=60),
            "maturity_date": date.today() + timedelta(days=305),
            "maturity_amount": Decimal('540000'),
            "interest_method": InterestMethod.SIMPLE,
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "status": DepositAccountStatus.ACTIVE,
            "branch_code": "BR001"
        },
        {
            "account_number": "FD20240101003",
            "customer_id": uuid.uuid4(),
            "cif_number": "CIF003",
            "product_id": fd_regular.id,
            "deposit_type": DepositType.FIXED_DEPOSIT,
            "principal_amount": Decimal('200000'),
            "interest_rate": Decimal('7.5'),
            "is_senior_citizen": False,
            "open_date": date.today() - timedelta(days=300),
            "maturity_date": date.today() + timedelta(days=65),
            "maturity_amount": Decimal('215000'),
            "interest_method": InterestMethod.SIMPLE,
            "payout_frequency": PayoutFrequency.ON_MATURITY,
            "status": DepositAccountStatus.ACTIVE,
            "branch_code": "BR002"
        }
    ]
    
    for acc_data in fd_accounts:
        account = DepositAccount(**acc_data)
        db.add(account)
        print(f"  ✅ Created FD: {account.account_number} - ₹{account.principal_amount}")
    
    db.commit()
    print(f"✅ Sample accounts seeded!\n")


def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("   DEPOSIT OS - DATABASE SEEDING")
    print("="*60 + "\n")
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized!\n")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_products(db)
        seed_interest_slabs(db)
        seed_sample_accounts(db)
        
        print("\n" + "="*60)
        print("   ✅ SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
        # Summary
        products_count = db.query(DepositProduct).count()
        slabs_count = db.query(InterestSlab).count()
        accounts_count = db.query(DepositAccount).count()
        
        print("📊 Database Summary:")
        print(f"   • Products: {products_count}")
        print(f"   • Interest Slabs: {slabs_count}")
        print(f"   • Sample Accounts: {accounts_count}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

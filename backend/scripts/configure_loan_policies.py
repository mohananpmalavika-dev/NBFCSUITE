"""
Script to configure initial loan policies
Run this after database migration to setup default loan policies
"""

import sys
import os
from decimal import Decimal
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database.loan_models import LoanPolicy, LoanType, RepaymentFrequency
from shared.config import settings
import uuid

# Database connection
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_loan_policies(tenant_id: int = 1):
    """Create default loan policies for different loan types"""
    
    db = SessionLocal()
    
    try:
        policies = [
            # Personal Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-PERSONAL-001",
                "policy_name": "Personal Loan Policy",
                "loan_type": LoanType.PERSONAL,
                "min_service_months": 12,
                "min_loan_amount": Decimal("10000.00"),
                "max_loan_amount": Decimal("500000.00"),
                "max_loan_as_salary_multiple": Decimal("5.00"),
                "max_emi_as_salary_percentage": Decimal("40.00"),
                "interest_rate": Decimal("10.50"),
                "min_tenure_months": 6,
                "max_tenure_months": 60,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("1.00"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("2.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Personal loan for employees with minimum 1 year service",
            },
            
            # Vehicle Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-VEHICLE-001",
                "policy_name": "Vehicle Loan Policy",
                "loan_type": LoanType.VEHICLE,
                "min_service_months": 6,
                "min_loan_amount": Decimal("50000.00"),
                "max_loan_amount": Decimal("1000000.00"),
                "max_loan_as_salary_multiple": Decimal("10.00"),
                "max_emi_as_salary_percentage": Decimal("45.00"),
                "interest_rate": Decimal("9.00"),
                "min_tenure_months": 12,
                "max_tenure_months": 84,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("1.50"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("3.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Vehicle loan for two-wheelers and four-wheelers",
            },
            
            # Home Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-HOME-001",
                "policy_name": "Home Loan Policy",
                "loan_type": LoanType.HOME,
                "min_service_months": 24,
                "min_loan_amount": Decimal("500000.00"),
                "max_loan_amount": Decimal("5000000.00"),
                "max_loan_as_salary_multiple": Decimal("20.00"),
                "max_emi_as_salary_percentage": Decimal("50.00"),
                "interest_rate": Decimal("8.50"),
                "min_tenure_months": 60,
                "max_tenure_months": 240,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.50"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("1.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Home loan for property purchase/construction",
            },
            
            # Education Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-EDUCATION-001",
                "policy_name": "Education Loan Policy",
                "loan_type": LoanType.EDUCATION,
                "min_service_months": 6,
                "min_loan_amount": Decimal("25000.00"),
                "max_loan_amount": Decimal("300000.00"),
                "max_loan_as_salary_multiple": Decimal("3.00"),
                "max_emi_as_salary_percentage": Decimal("35.00"),
                "interest_rate": Decimal("8.00"),
                "min_tenure_months": 12,
                "max_tenure_months": 60,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.50"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("0.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Education loan for higher studies",
            },
            
            # Medical Emergency Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-MEDICAL-001",
                "policy_name": "Medical Emergency Loan Policy",
                "loan_type": LoanType.MEDICAL,
                "min_service_months": 3,
                "min_loan_amount": Decimal("10000.00"),
                "max_loan_amount": Decimal("200000.00"),
                "max_loan_as_salary_multiple": Decimal("2.00"),
                "max_emi_as_salary_percentage": Decimal("30.00"),
                "interest_rate": Decimal("6.00"),
                "min_tenure_months": 6,
                "max_tenure_months": 36,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.00"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("0.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "auto_approve_below_amount": Decimal("50000.00"),
                "is_active": True,
                "effective_from": date.today(),
                "description": "Interest-subsidized loan for medical emergencies",
            },
            
            # Salary Advance
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-ADVANCE-001",
                "policy_name": "Salary Advance Policy",
                "loan_type": LoanType.SALARY_ADVANCE,
                "min_service_months": 3,
                "min_loan_amount": Decimal("5000.00"),
                "max_loan_amount": Decimal("50000.00"),
                "max_loan_as_salary_multiple": Decimal("1.00"),
                "max_emi_as_salary_percentage": Decimal("50.00"),
                "interest_rate": Decimal("0.00"),
                "min_tenure_months": 1,
                "max_tenure_months": 6,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.00"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("0.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": False,
                "requires_finance_approval": False,
                "auto_approve_below_amount": Decimal("25000.00"),
                "is_active": True,
                "effective_from": date.today(),
                "description": "Interest-free salary advance up to 1 month salary",
            },
            
            # Marriage Loan
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-MARRIAGE-001",
                "policy_name": "Marriage Loan Policy",
                "loan_type": LoanType.MARRIAGE,
                "min_service_months": 12,
                "min_loan_amount": Decimal("50000.00"),
                "max_loan_amount": Decimal("300000.00"),
                "max_loan_as_salary_multiple": Decimal("3.00"),
                "max_emi_as_salary_percentage": Decimal("35.00"),
                "interest_rate": Decimal("7.50"),
                "min_tenure_months": 12,
                "max_tenure_months": 36,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.50"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("1.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": True,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Special loan for marriage expenses",
            },
            
            # Festival Advance
            {
                "id": uuid.uuid4(),
                "tenant_id": tenant_id,
                "policy_code": "POL-FESTIVAL-001",
                "policy_name": "Festival Advance Policy",
                "loan_type": LoanType.FESTIVAL_ADVANCE,
                "min_service_months": 6,
                "min_loan_amount": Decimal("10000.00"),
                "max_loan_amount": Decimal("100000.00"),
                "max_loan_as_salary_multiple": Decimal("1.50"),
                "max_emi_as_salary_percentage": Decimal("40.00"),
                "interest_rate": Decimal("0.00"),
                "min_tenure_months": 3,
                "max_tenure_months": 12,
                "repayment_frequency": RepaymentFrequency.MONTHLY,
                "processing_fee_percentage": Decimal("0.00"),
                "prepayment_allowed": True,
                "prepayment_penalty_percentage": Decimal("0.00"),
                "max_active_loans_per_employee": 1,
                "requires_manager_approval": True,
                "requires_hr_approval": True,
                "requires_finance_approval": False,
                "is_active": True,
                "effective_from": date.today(),
                "description": "Interest-free festival advance",
            },
        ]
        
        for policy_data in policies:
            # Check if policy already exists
            existing = db.query(LoanPolicy).filter_by(
                tenant_id=policy_data["tenant_id"],
                policy_code=policy_data["policy_code"]
            ).first()
            
            if existing:
                print(f"Policy {policy_data['policy_code']} already exists, skipping...")
                continue
            
            policy = LoanPolicy(**policy_data)
            db.add(policy)
            print(f"Created policy: {policy_data['policy_code']} - {policy_data['policy_name']}")
        
        db.commit()
        print(f"\n✅ Successfully configured {len(policies)} loan policies!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error configuring loan policies: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Configuring Loan Policies...")
    print("-" * 50)
    
    # Get tenant_id from command line argument or use default
    tenant_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print(f"Tenant ID: {tenant_id}\n")
    
    create_loan_policies(tenant_id)
    
    print("\n" + "=" * 50)
    print("✨ Loan policy configuration complete!")
    print("=" * 50)

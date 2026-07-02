"""
Seed Gold Loan Products
Creates initial product configurations for various gold loan types
"""
import os
import sys
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.product import (
    GoldProduct, GoldProductInterest, GoldProductTenure, GoldProductLimits,
    GoldProductCharge, GoldProductDocument, GoldProductEligibility,
    GoldProductWorkflow, GoldProductChannel, GoldProductTax, Base
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_gold_jewel_loan(db):
    """Standard Gold Jewel Loan - Most common product"""
    product_id = str(uuid4())
    
    product = GoldProduct(
        id=product_id,
        product_code="GL-JEWEL-001",
        product_name="Gold Jewel Loan",
        product_type="jewel_loan",
        description="Standard gold loan against jewellery for personal use",
        is_active=True,
        display_order=1
    )
    db.add(product)
    
    # Interest Configuration
    interest = GoldProductInterest(
        id=str(uuid4()),
        product_id=product_id,
        interest_type="reducing",
        rate_type="fixed",
        base_rate=12.0,
        min_rate=10.0,
        max_rate=18.0,
        penal_interest=2.0,
        compounding_frequency="monthly"
    )
    db.add(interest)
    
    # Tenure Configuration
    tenure = GoldProductTenure(
        id=str(uuid4()),
        product_id=product_id,
        min_tenure_months=3,
        max_tenure_months=36,
        default_tenure_months=12,
        tenure_unit="months",
        renewal_allowed=True,
        max_renewals=3,
        auto_renewal=False
    )
    db.add(tenure)
    
    # Limits Configuration
    limits = GoldProductLimits(
        id=str(uuid4()),
        product_id=product_id,
        min_loan_amount=5000.0,
        max_loan_amount=5000000.0,
        ltv_percent=75.0,
        min_ltv=70.0,
        max_ltv=80.0,
        min_gold_weight_grams=5.0,
        max_gold_weight_grams=2000.0,
        purity_threshold_karat=18.0
    )
    db.add(limits)
    
    # Charges
    charges = [
        GoldProductCharge(
            id=str(uuid4()),
            product_id=product_id,
            charge_code="PROCESSING",
            charge_name="Processing Fee",
            charge_type="percentage",
            charge_percentage=1.0,
            min_charge=500.0,
            max_charge=10000.0,
            charge_frequency="one_time",
            is_mandatory=True,
            is_refundable=False,
            tax_applicable=True
        ),
        GoldProductCharge(
            id=str(uuid4()),
            product_id=product_id,
            charge_code="APPRAISAL",
            charge_name="Gold Appraisal Fee",
            charge_type="flat",
            charge_amount=200.0,
            charge_frequency="one_time",
            is_mandatory=True,
            is_refundable=False,
            tax_applicable=True
        ),
        GoldProductCharge(
            id=str(uuid4()),
            product_id=product_id,
            charge_code="VAULT",
            charge_name="Vault Storage Fee",
            charge_type="flat",
            charge_amount=100.0,
            charge_frequency="monthly",
            is_mandatory=True,
            is_refundable=False,
            tax_applicable=True
        )
    ]
    for charge in charges:
        db.add(charge)
    
    # Documents
    documents = [
        GoldProductDocument(
            id=str(uuid4()),
            product_id=product_id,
            document_type="AADHAR",
            document_name="Aadhar Card",
            is_mandatory=True,
            verification_required=True,
            document_category="kyc"
        ),
        GoldProductDocument(
            id=str(uuid4()),
            product_id=product_id,
            document_type="PAN",
            document_name="PAN Card",
            is_mandatory=True,
            verification_required=True,
            document_category="kyc"
        ),
        GoldProductDocument(
            id=str(uuid4()),
            product_id=product_id,
            document_type="PHOTO",
            document_name="Passport Size Photo",
            is_mandatory=True,
            verification_required=False,
            document_category="kyc"
        )
    ]
    for doc in documents:
        db.add(doc)
    
    # Eligibility Rules
    eligibility = [
        GoldProductEligibility(
            id=str(uuid4()),
            product_id=product_id,
            rule_type="age",
            rule_name="Minimum Age",
            rule_operator="gte",
            rule_value={"value": 21},
            is_mandatory=True,
            error_message="Customer must be at least 21 years old"
        ),
        GoldProductEligibility(
            id=str(uuid4()),
            product_id=product_id,
            rule_type="age",
            rule_name="Maximum Age",
            rule_operator="lte",
            rule_value={"value": 65},
            is_mandatory=True,
            error_message="Customer must be below 65 years old"
        )
    ]
    for rule in eligibility:
        db.add(rule)
    
    # Workflow
    workflow = [
        GoldProductWorkflow(
            id=str(uuid4()),
            product_id=product_id,
            stage_order=1,
            stage_name="Gold Appraisal",
            stage_type="user",
            approver_role="GOLD_APPRAISER",
            sla_hours=2,
            is_parallel=False
        ),
        GoldProductWorkflow(
            id=str(uuid4()),
            product_id=product_id,
            stage_order=2,
            stage_name="Credit Assessment",
            stage_type="ai",
            approver_role="AI_CREDIT_ENGINE",
            sla_hours=1,
            is_parallel=False,
            auto_approve_conditions={"amount_below": 100000, "customer_segment": "prime"}
        ),
        GoldProductWorkflow(
            id=str(uuid4()),
            product_id=product_id,
            stage_order=3,
            stage_name="Branch Manager Approval",
            stage_type="role",
            approver_role="BRANCH_MANAGER",
            amount_min=0,
            amount_max=500000,
            sla_hours=24,
            is_parallel=False
        )
    ]
    for stage in workflow:
        db.add(stage)
    
    # Channels
    channels = [
        GoldProductChannel(
            id=str(uuid4()),
            product_id=product_id,
            channel_type="branch",
            is_enabled=True,
            requires_verification=True,
            instant_approval_limit=50000.0
        ),
        GoldProductChannel(
            id=str(uuid4()),
            product_id=product_id,
            channel_type="mobile",
            is_enabled=True,
            requires_verification=True,
            instant_approval_limit=25000.0
        )
    ]
    for channel in channels:
        db.add(channel)
    
    # Tax
    tax = GoldProductTax(
        id=str(uuid4()),
        product_id=product_id,
        tax_type="gst",
        tax_name="Goods and Services Tax",
        tax_percentage=18.0,
        tax_category="charges",
        hsn_sac_code="997159",
        is_active=True
    )
    db.add(tax)


def seed_gold_bullet_loan(db):
    """Gold Bullet Loan - Interest paid monthly, principal at maturity"""
    product_id = str(uuid4())
    
    product = GoldProduct(
        id=product_id,
        product_code="GL-BULLET-001",
        product_name="Gold Bullet Loan",
        product_type="bullet_loan",
        description="Gold loan with monthly interest payments and principal at maturity",
        is_active=True,
        display_order=2
    )
    db.add(product)
    
    interest = GoldProductInterest(
        id=str(uuid4()),
        product_id=product_id,
        interest_type="simple",
        rate_type="fixed",
        base_rate=11.0,
        min_rate=9.0,
        max_rate=15.0,
        penal_interest=2.5,
        compounding_frequency="none"
    )
    db.add(interest)
    
    tenure = GoldProductTenure(
        id=str(uuid4()),
        product_id=product_id,
        min_tenure_months=6,
        max_tenure_months=24,
        default_tenure_months=12,
        tenure_unit="months",
        renewal_allowed=True,
        max_renewals=2,
        auto_renewal=False
    )
    db.add(tenure)
    
    limits = GoldProductLimits(
        id=str(uuid4()),
        product_id=product_id,
        min_loan_amount=25000.0,
        max_loan_amount=10000000.0,
        ltv_percent=70.0,
        min_ltv=65.0,
        max_ltv=75.0,
        min_gold_weight_grams=20.0,
        max_gold_weight_grams=5000.0,
        purity_threshold_karat=20.0
    )
    db.add(limits)


def seed_gold_od(db):
    """Gold Overdraft - Flexible withdrawal and repayment"""
    product_id = str(uuid4())
    
    product = GoldProduct(
        id=product_id,
        product_code="GL-OD-001",
        product_name="Gold Overdraft",
        product_type="od",
        description="Overdraft facility against gold with flexible withdrawals",
        is_active=True,
        display_order=3
    )
    db.add(product)
    
    interest = GoldProductInterest(
        id=str(uuid4()),
        product_id=product_id,
        interest_type="reducing",
        rate_type="floating",
        base_rate=13.5,
        min_rate=11.0,
        max_rate=16.0,
        penal_interest=3.0,
        compounding_frequency="daily"
    )
    db.add(interest)
    
    tenure = GoldProductTenure(
        id=str(uuid4()),
        product_id=product_id,
        min_tenure_months=12,
        max_tenure_months=60,
        default_tenure_months=24,
        tenure_unit="months",
        renewal_allowed=True,
        max_renewals=5,
        auto_renewal=True
    )
    db.add(tenure)
    
    limits = GoldProductLimits(
        id=str(uuid4()),
        product_id=product_id,
        min_loan_amount=50000.0,
        max_loan_amount=20000000.0,
        ltv_percent=65.0,
        min_ltv=60.0,
        max_ltv=70.0,
        min_gold_weight_grams=50.0,
        max_gold_weight_grams=10000.0,
        purity_threshold_karat=22.0
    )
    db.add(limits)


def seed_instant_gold_loan(db):
    """Instant Gold Loan - Quick approval with AI"""
    product_id = str(uuid4())
    
    product = GoldProduct(
        id=product_id,
        product_code="GL-INSTANT-001",
        product_name="Instant Gold Loan",
        product_type="instant",
        description="AI-powered instant gold loan with quick disbursement",
        is_active=True,
        display_order=4
    )
    db.add(product)
    
    interest = GoldProductInterest(
        id=str(uuid4()),
        product_id=product_id,
        interest_type="flat",
        rate_type="fixed",
        base_rate=14.0,
        min_rate=12.0,
        max_rate=18.0,
        penal_interest=2.0,
        compounding_frequency="monthly"
    )
    db.add(interest)
    
    tenure = GoldProductTenure(
        id=str(uuid4()),
        product_id=product_id,
        min_tenure_months=1,
        max_tenure_months=12,
        default_tenure_months=3,
        tenure_unit="months",
        renewal_allowed=True,
        max_renewals=2,
        auto_renewal=False
    )
    db.add(tenure)
    
    limits = GoldProductLimits(
        id=str(uuid4()),
        product_id=product_id,
        min_loan_amount=1000.0,
        max_loan_amount=200000.0,
        ltv_percent=75.0,
        min_ltv=70.0,
        max_ltv=80.0,
        min_gold_weight_grams=1.0,
        max_gold_weight_grams=200.0,
        purity_threshold_karat=18.0
    )
    db.add(limits)
    
    # Workflow for instant approval
    workflow = [
        GoldProductWorkflow(
            id=str(uuid4()),
            product_id=product_id,
            stage_order=1,
            stage_name="AI Auto Appraisal",
            stage_type="ai",
            approver_role="AI_INSTANT_ENGINE",
            sla_hours=0,
            is_parallel=False,
            auto_approve_conditions={"amount_below": 50000, "weight_below": 50}
        )
    ]
    for stage in workflow:
        db.add(stage)
    
    # Mobile-first channel
    channels = [
        GoldProductChannel(
            id=str(uuid4()),
            product_id=product_id,
            channel_type="mobile",
            is_enabled=True,
            requires_verification=False,
            instant_approval_limit=50000.0
        ),
        GoldProductChannel(
            id=str(uuid4()),
            product_id=product_id,
            channel_type="web",
            is_enabled=True,
            requires_verification=False,
            instant_approval_limit=50000.0
        )
    ]
    for channel in channels:
        db.add(channel)


def main():
    """Seed all gold loan products"""
    db = SessionLocal()
    
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("Seeding Gold Jewel Loan...")
        seed_gold_jewel_loan(db)
        
        print("Seeding Gold Bullet Loan...")
        seed_gold_bullet_loan(db)
        
        print("Seeding Gold Overdraft...")
        seed_gold_od(db)
        
        print("Seeding Instant Gold Loan...")
        seed_instant_gold_loan(db)
        
        db.commit()
        print("✓ Successfully seeded all gold loan products!")
        
    except Exception as e:
        print(f"✗ Error seeding products: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

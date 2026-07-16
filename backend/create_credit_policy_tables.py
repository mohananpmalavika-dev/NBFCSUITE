"""
Direct table creation for Credit Policy Integration
Creates all 11 tables for the credit policy module
"""
import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Credit Policy Integration - Database Setup")
print("=" * 70)

# Import SQLAlchemy and models
print("\n📦 Loading database connection...")
from shared.database.connection import engine, Base

print("📦 Loading credit policy models...")
from services.credit_policy.credit_policy_models import (
    CreditPolicy, RiskBasedPricing, ScoreBasedRate, LTVRatio,
    ExposureLimit, ConcentrationLimit, SectoralCap,
    AutoApprovalCriteria, ManualReviewTrigger, DecisionMatrix, CounterOfferRule
)

print(f"✅ Loaded {len([CreditPolicy, RiskBasedPricing, ScoreBasedRate, LTVRatio, ExposureLimit, ConcentrationLimit, SectoralCap, AutoApprovalCriteria, ManualReviewTrigger, DecisionMatrix, CounterOfferRule])} model classes")

# Create tables
print("\n🔨 Creating credit policy tables...")
try:
    Base.metadata.create_all(
        bind=engine,
        tables=[
            CreditPolicy.__table__,
            RiskBasedPricing.__table__,
            ScoreBasedRate.__table__,
            LTVRatio.__table__,
            ExposureLimit.__table__,
            ConcentrationLimit.__table__,
            SectoralCap.__table__,
            AutoApprovalCriteria.__table__,
            ManualReviewTrigger.__table__,
            DecisionMatrix.__table__,
            CounterOfferRule.__table__
        ],
        checkfirst=True
    )
    
    print("✅ Tables created successfully!")
    
    # Verify
    print("\n🔍 Verifying tables...")
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    credit_policy_tables = [
        'credit_policies',
        'risk_based_pricing',
        'score_based_rates',
        'ltv_ratios',
        'exposure_limits',
        'concentration_limits',
        'sectoral_caps',
        'auto_approval_criteria',
        'manual_review_triggers',
        'decision_matrix',
        'counter_offer_rules'
    ]
    
    found_tables = [t for t in credit_policy_tables if t in tables]
    
    print(f"✅ Found {len(found_tables)}/{len(credit_policy_tables)} tables:")
    for table in found_tables:
        print(f"   ✓ {table}")
    
    missing_tables = [t for t in credit_policy_tables if t not in tables]
    if missing_tables:
        print(f"\n⚠️ Missing tables:")
        for table in missing_tables:
            print(f"   ✗ {table}")
    
    print("\n" + "=" * 70)
    print("✅ Database setup complete!")
    print("=" * 70)
    print("\nCredit Policy Integration is now ready!")
    print("\nNext steps:")
    print("1. Start the backend server: python main.py")
    print("2. Access credit policy API at: http://localhost:8000/api/credit-policy")
    print("3. View API docs at: http://localhost:8000/docs")
    print("4. Test with sample policy creation")
    
except Exception as e:
    print(f"\n❌ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

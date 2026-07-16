"""
Script to create Credit Policy Integration tables
Run this to set up the database schema for credit policy module
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir.parent))

from sqlalchemy import text
from backend.shared.database.connection import engine, Base

# Import credit policy models
from backend.services.credit_policy.credit_policy_models import (
    CreditPolicy, RiskBasedPricing, ScoreBasedRate, LTVRatio,
    ExposureLimit, ConcentrationLimit, SectoralCap,
    AutoApprovalCriteria, ManualReviewTrigger, DecisionMatrix, CounterOfferRule
)


async def create_credit_policy_tables():
    """Create credit policy tables"""
    print("=" * 60)
    print("Credit Policy Integration - Database Setup")
    print("=" * 60)
    
    # Import the migration module to execute
    from alembic.versions import _001_create_credit_policy_tables
    
    print("\n📦 Creating credit policy tables...")
    
    try:
        async with engine.begin() as conn:
            # Run the upgrade function
            await conn.run_sync(_001_create_credit_policy_tables.upgrade)
            
        print("✅ Credit policy tables created successfully!")
        
        # Verify tables
        print("\n🔍 Verifying tables...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%credit%' OR table_name LIKE '%policy%'
                OR table_name LIKE '%exposure%' OR table_name LIKE '%decision%'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
        if tables:
            print(f"✅ Found {len(tables)} credit policy related tables:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("⚠️ No credit policy tables found. Migration may have failed.")
        
        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the backend server: python main.py")
        print("2. Access credit policy API at: http://localhost:8000/api/credit-policy")
        print("3. View API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("\nStarting credit policy database setup...")
    success = asyncio.run(create_credit_policy_tables())
    sys.exit(0 if success else 1)

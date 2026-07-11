"""
CRM Tables Creation Script
Use this if alembic migration doesn't work
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from backend.shared.database.connection import engine, Base


async def create_crm_tables():
    """Create CRM tables manually"""
    
    print("=" * 60)
    print("CRM Lead Management - Table Creation")
    print("=" * 60)
    
    try:
        # Import CRM models
        print("\n1. Importing CRM models...")
        from backend.shared.database.crm_lead_models import (
            Lead, LeadFollowUp, LeadActivity, 
            LeadScoringRule, LeadAssignmentRule
        )
        print("✅ Models imported successfully")
        
        # Create tables
        print("\n2. Creating CRM tables...")
        async with engine.begin() as conn:
            # Create only CRM tables
            def create_tables(sync_conn):
                Base.metadata.create_all(
                    bind=sync_conn,
                    tables=[
                        Lead.__table__,
                        LeadFollowUp.__table__,
                        LeadActivity.__table__,
                        LeadScoringRule.__table__,
                        LeadAssignmentRule.__table__
                    ],
                    checkfirst=True
                )
            
            await conn.run_sync(create_tables)
        
        print("✅ Tables created successfully!")
        
        # Verify tables
        print("\n3. Verifying tables...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                      AND table_name LIKE 'crm_%'
                    ORDER BY table_name
                """)
            )
            tables = [row[0] for row in result]
            
            print(f"✅ Found {len(tables)} CRM tables:")
            for table in tables:
                print(f"   - {table}")
        
        if len(tables) == 5:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! All CRM tables created.")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Load initial data: python load_crm_initial_data.py")
            print("2. Restart backend server")
            print("3. Visit http://localhost:8000/docs")
            print("4. Look for 'CRM - Lead Management' section")
            return True
        else:
            print(f"\n❌ ERROR: Expected 5 tables, found {len(tables)}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nStarting CRM table creation...")
    success = asyncio.run(create_crm_tables())
    sys.exit(0 if success else 1)

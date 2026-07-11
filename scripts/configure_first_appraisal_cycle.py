"""
Configure First Appraisal Cycle
Script to create initial appraisal cycle for performance management
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.shared.database.connection import AsyncSessionLocal, engine
from backend.shared.database.hrms_models import (
    AppraisalCycle, AppraisalCycleStatus,
    Employee
)
from backend.shared.database.models import Tenant


async def configure_first_cycle():
    """Create the first appraisal cycle"""
    
    print("=" * 60)
    print("PERFORMANCE MANAGEMENT - FIRST CYCLE CONFIGURATION")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Get default tenant
        result = await session.execute(select(Tenant).where(Tenant.id == "default"))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            print("❌ Default tenant not found. Please run init-db first.")
            return False
        
        print(f"✓ Using tenant: {tenant.name}")
        
        # Check if cycle already exists
        result = await session.execute(
            select(AppraisalCycle).where(
                AppraisalCycle.tenant_id == tenant.id,
                AppraisalCycle.cycle_code == "APR-2024-25"
            )
        )
        existing_cycle = result.scalar_one_or_none()
        
        if existing_cycle:
            print(f"⚠️  Appraisal cycle 'APR-2024-25' already exists!")
            print(f"   Cycle: {existing_cycle.cycle_name}")
            print(f"   Status: {existing_cycle.status}")
            return True
        
        # Get current date and calculate fiscal year dates
        today = date.today()
        current_year = today.year
        
        # Fiscal year: April 1 to March 31
        if today.month >= 4:
            fiscal_start = date(current_year, 4, 1)
            fiscal_end = date(current_year + 1, 3, 31)
            fiscal_year = f"{current_year}-{str(current_year + 1)[-2:]}"
        else:
            fiscal_start = date(current_year - 1, 4, 1)
            fiscal_end = date(current_year, 3, 31)
            fiscal_year = f"{current_year - 1}-{str(current_year)[-2:]}"
        
        print(f"\n📅 Fiscal Year: {fiscal_year}")
        print(f"   Start: {fiscal_start}")
        print(f"   End: {fiscal_end}")
        
        # Calculate phase dates
        # Goal Setting: April (1 month)
        goal_setting_start = fiscal_start
        goal_setting_end = goal_setting_start + timedelta(days=30)
        
        # Self Assessment: January (1 month before end)
        self_assessment_start = fiscal_end - timedelta(days=90)
        self_assessment_end = self_assessment_start + timedelta(days=30)
        
        # Manager Review: February (1 month)
        manager_review_start = self_assessment_end + timedelta(days=1)
        manager_review_end = manager_review_start + timedelta(days=30)
        
        # HR Review: March (until end)
        hr_review_start = manager_review_end + timedelta(days=1)
        hr_review_end = fiscal_end
        
        # Create appraisal cycle
        cycle = AppraisalCycle(
            id=str(uuid4()),
            tenant_id=tenant.id,
            cycle_code="APR-2024-25",
            cycle_name=f"Annual Performance Appraisal {fiscal_year}",
            cycle_description="Annual performance review cycle with goal setting, self-assessment, 360 feedback, and manager review",
            fiscal_year=fiscal_year,
            start_date=fiscal_start,
            end_date=fiscal_end,
            
            # Phase deadlines
            goal_setting_start=goal_setting_start,
            goal_setting_end=goal_setting_end,
            self_assessment_start=self_assessment_start,
            self_assessment_end=self_assessment_end,
            manager_review_start=manager_review_start,
            manager_review_end=manager_review_end,
            hr_review_start=hr_review_start,
            hr_review_end=hr_review_end,
            
            # Configuration
            enable_360_feedback=True,
            enable_self_assessment=True,
            enable_goal_setting=True,
            
            # Status
            status=AppraisalCycleStatus.ACTIVE,
            
            # Statistics (will be updated as appraisals are created)
            total_employees=0,
            completed_appraisals=0,
            
            is_active=True
        )
        
        session.add(cycle)
        await session.commit()
        await session.refresh(cycle)
        
        print(f"\n✅ Appraisal cycle created successfully!")
        print(f"   Cycle Code: {cycle.cycle_code}")
        print(f"   Cycle Name: {cycle.cycle_name}")
        print(f"   Status: {cycle.status}")
        
        print(f"\n📋 Phase Timeline:")
        print(f"   Goal Setting:     {goal_setting_start} to {goal_setting_end}")
        print(f"   Self Assessment:  {self_assessment_start} to {self_assessment_end}")
        print(f"   Manager Review:   {manager_review_start} to {manager_review_end}")
        print(f"   HR Review:        {hr_review_start} to {hr_review_end}")
        
        print(f"\n⚙️  Configuration:")
        print(f"   Goal Setting: {'Enabled' if cycle.enable_goal_setting else 'Disabled'}")
        print(f"   Self Assessment: {'Enabled' if cycle.enable_self_assessment else 'Disabled'}")
        print(f"   360 Feedback: {'Enabled' if cycle.enable_360_feedback else 'Disabled'}")
        
        # Count employees for statistics
        result = await session.execute(
            select(Employee).where(
                Employee.tenant_id == tenant.id,
                Employee.is_active == True
            )
        )
        employees = result.scalars().all()
        employee_count = len(employees)
        
        # Update cycle statistics
        cycle.total_employees = employee_count
        await session.commit()
        
        print(f"\n👥 Employee Statistics:")
        print(f"   Total Employees: {employee_count}")
        print(f"   Appraisals to be created: {employee_count}")
        
        print(f"\n🎉 Configuration Complete!")
        print(f"\nNext Steps:")
        print(f"   1. Communicate cycle timeline to all employees")
        print(f"   2. Employees can start setting goals")
        print(f"   3. Managers can approve goals")
        print(f"   4. Monitor progress via Performance Dashboard")
        
        return True


async def main():
    """Main execution"""
    try:
        success = await configure_first_cycle()
        if success:
            print(f"\n{'=' * 60}")
            print("✅ SUCCESS: First appraisal cycle configured!")
            print(f"{'=' * 60}\n")
        else:
            print(f"\n{'=' * 60}")
            print("❌ FAILED: Could not configure appraisal cycle")
            print(f"{'=' * 60}\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

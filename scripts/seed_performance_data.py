"""
Seed Performance Management Sample Data
Creates sample goals and appraisals for testing
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from uuid import uuid4
from decimal import Decimal

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.shared.database.connection import AsyncSessionLocal, engine
from backend.shared.database.hrms_models import (
    AppraisalCycle, PerformanceGoal, EmployeeAppraisal,
    Employee, GoalType, GoalPriority, GoalStatus,
    AppraisalStatus
)
from backend.shared.database.models import Tenant


async def seed_sample_data():
    """Create sample performance data"""
    
    print("=" * 60)
    print("PERFORMANCE MANAGEMENT - SAMPLE DATA SEEDING")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Get default tenant
        result = await session.execute(select(Tenant).where(Tenant.id == "default"))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            print("❌ Default tenant not found")
            return False
        
        # Get active appraisal cycle
        result = await session.execute(
            select(AppraisalCycle).where(
                AppraisalCycle.tenant_id == tenant.id,
                AppraisalCycle.status == "active"
            ).limit(1)
        )
        cycle = result.scalar_one_or_none()
        
        if not cycle:
            print("❌ No active appraisal cycle found. Run configure_first_appraisal_cycle.py first.")
            return False
        
        print(f"✓ Using cycle: {cycle.cycle_name}")
        
        # Get employees
        result = await session.execute(
            select(Employee).where(
                Employee.tenant_id == tenant.id,
                Employee.is_active == True
            ).limit(5)
        )
        employees = result.scalars().all()
        
        if len(employees) == 0:
            print("❌ No employees found. Create employees first.")
            return False
        
        print(f"✓ Found {len(employees)} employees")
        
        goals_created = 0
        appraisals_created = 0
        
        # Create goals and appraisals for each employee
        for idx, employee in enumerate(employees):
            print(f"\n👤 Processing Employee: {employee.employee_code}")
            
            # Create appraisal for employee
            appraisal = EmployeeAppraisal(
                id=str(uuid4()),
                tenant_id=tenant.id,
                appraisal_code=f"APR-{employee.employee_code}-{cycle.fiscal_year}",
                employee_id=employee.id,
                appraisal_cycle_id=cycle.id,
                status=AppraisalStatus.GOAL_SETTING_PENDING,
                is_active=True
            )
            session.add(appraisal)
            appraisals_created += 1
            
            # Create 3-5 goals for each employee
            goal_templates = [
                {
                    "title": "Complete Project Deliverables",
                    "description": "Deliver all assigned project milestones on time and within quality standards",
                    "type": GoalType.PROJECT,
                    "priority": GoalPriority.HIGH,
                    "target": "100%",
                    "uom": "%",
                    "weightage": 30
                },
                {
                    "title": "Improve Team Collaboration",
                    "description": "Enhance cross-functional collaboration and knowledge sharing",
                    "type": GoalType.KRA,
                    "priority": GoalPriority.MEDIUM,
                    "target": "4/5",
                    "uom": "rating",
                    "weightage": 20
                },
                {
                    "title": "Customer Satisfaction Score",
                    "description": "Maintain high customer satisfaction ratings",
                    "type": GoalType.KPI,
                    "priority": GoalPriority.HIGH,
                    "target": "90",
                    "uom": "%",
                    "weightage": 25
                },
                {
                    "title": "Professional Development",
                    "description": "Complete certification or training program",
                    "type": GoalType.OBJECTIVE,
                    "priority": GoalPriority.MEDIUM,
                    "target": "1",
                    "uom": "course",
                    "weightage": 15
                },
                {
                    "title": "Process Improvement Initiative",
                    "description": "Identify and implement process improvements",
                    "type": GoalType.KRA,
                    "priority": GoalPriority.LOW,
                    "target": "2",
                    "uom": "initiatives",
                    "weightage": 10
                }
            ]
            
            for goal_idx, template in enumerate(goal_templates[:4]):  # Create 4 goals
                goal = PerformanceGoal(
                    id=str(uuid4()),
                    tenant_id=tenant.id,
                    goal_code=f"G-{employee.employee_code}-{cycle.fiscal_year}-{goal_idx + 1:02d}",
                    goal_title=template["title"],
                    goal_description=template["description"],
                    goal_type=template["type"],
                    goal_priority=template["priority"],
                    employee_id=employee.id,
                    appraisal_cycle_id=cycle.id,
                    measurement_criteria=f"Measured by {template['uom']}",
                    target_value=template["target"],
                    uom=template["uom"],
                    weightage=Decimal(str(template["weightage"])),
                    start_date=cycle.start_date,
                    target_date=cycle.end_date - timedelta(days=60),
                    progress_percentage=0,
                    status=GoalStatus.DRAFT,
                    is_active=True
                )
                session.add(goal)
                goals_created += 1
            
            print(f"   ✓ Created {4} goals")
            print(f"   ✓ Created appraisal record")
        
        await session.commit()
        
        print(f"\n{'=' * 60}")
        print(f"✅ SAMPLE DATA CREATED SUCCESSFULLY!")
        print(f"{'=' * 60}")
        print(f"\n📊 Summary:")
        print(f"   Employees Processed: {len(employees)}")
        print(f"   Goals Created: {goals_created}")
        print(f"   Appraisals Created: {appraisals_created}")
        
        print(f"\n🎯 Goal Distribution:")
        print(f"   KRA Goals: {goals_created // 3}")
        print(f"   KPI Goals: {goals_created // 4}")
        print(f"   Project Goals: {goals_created // 5}")
        print(f"   Objective Goals: {goals_created // 5}")
        
        print(f"\n📝 What's Next:")
        print(f"   1. Login as an employee to view and submit goals")
        print(f"   2. Login as a manager to approve goals")
        print(f"   3. Use Performance Dashboard to monitor progress")
        print(f"   4. Employees can track goal progress")
        print(f"   5. Complete self-assessment during review period")
        
        return True


async def main():
    """Main execution"""
    try:
        success = await seed_sample_data()
        if success:
            print(f"\n{'=' * 60}")
            print("✅ SUCCESS: Sample data seeded!")
            print(f"{'=' * 60}\n")
        else:
            print(f"\n{'=' * 60}")
            print("❌ FAILED: Could not seed sample data")
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

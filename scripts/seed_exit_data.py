#!/usr/bin/env python3
"""
Exit Management Seed Data Script
Creates sample data for testing Exit Management module
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
from uuid import uuid4

from sqlalchemy import select
from backend.shared.database.connection import get_async_session
from backend.shared.database.hrms_models import (
    Resignation, ExitClearance, ExitSettlement, SettlementComponent, ExitDocument,
    ResignationType, ResignationStatus, ClearanceStatus, SettlementStatus,
    SettlementComponentType, ExitDocumentType, Employee
)

# ANSI color codes
class Colors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


async def get_sample_employees(session, tenant_id: str, count: int = 5):
    """Get sample employees from database"""
    result = await session.execute(
        select(Employee)
        .where(Employee.tenant_id == tenant_id)
        .where(Employee.is_active == True)
        .limit(count)
    )
    employees = result.scalars().all()
    
    if not employees:
        print_error("No employees found in database. Please create employees first.")
        return []
    
    print_success(f"Found {len(employees)} employees for sample data")
    return employees


async def create_resignation_with_workflow(session, employee, tenant_id: str, status: ResignationStatus):
    """Create a resignation with appropriate workflow data based on status"""
    
    resignation_date = date.today() - timedelta(days=random.randint(1, 30))
    last_working_date = resignation_date + timedelta(days=random.randint(30, 60))
    
    resignation_data = {
        'tenant_id': tenant_id,
        'resignation_code': f'RES{datetime.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}',
        'employee_id': employee.id,
        'resignation_type': random.choice(list(ResignationType)),
        'resignation_date': resignation_date,
        'last_working_date': last_working_date,
        'notice_period_days': 30,
        'status': status,
        'reason_category': random.choice([
            'Better Opportunity', 'Higher Salary', 'Career Growth',
            'Work-Life Balance', 'Personal Reasons', 'Further Education'
        ]),
        'reason_details': 'Sample resignation reason for testing purposes',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Add workflow data based on status
    if status in [ResignationStatus.UNDER_REVIEW, ResignationStatus.APPROVED, ResignationStatus.COMPLETED]:
        resignation_data['manager_reviewed_date'] = datetime.now() - timedelta(days=5)
        resignation_data['manager_comments'] = 'Sample manager review comments'
        resignation_data['manager_recommendation'] = 'approve'
        
        resignation_data['hr_reviewed_date'] = datetime.now() - timedelta(days=3)
        resignation_data['hr_comments'] = 'Sample HR review comments'
        resignation_data['re_employment_eligible'] = True
    
    if status in [ResignationStatus.APPROVED, ResignationStatus.COMPLETED]:
        resignation_data['approved_date'] = datetime.now() - timedelta(days=2)
        resignation_data['approval_comments'] = 'Resignation approved'
        resignation_data['actual_last_working_date'] = last_working_date
    
    if status == ResignationStatus.COMPLETED:
        resignation_data['exit_interview_scheduled'] = True
        resignation_data['exit_interview_date'] = datetime.now() - timedelta(days=1)
        resignation_data['exit_interview_notes'] = 'Exit interview conducted successfully'
        resignation_data['handover_completed'] = True
        resignation_data['handover_notes'] = 'All assets and responsibilities handed over'
    
    if status == ResignationStatus.REJECTED:
        resignation_data['rejected_date'] = datetime.now() - timedelta(days=1)
        resignation_data['rejection_reason'] = 'Sample rejection reason for testing'
    
    resignation = Resignation(**resignation_data)
    session.add(resignation)
    await session.flush()
    
    return resignation


async def create_clearances_for_resignation(session, resignation, tenant_id: str):
    """Create default clearances for a resignation"""
    
    default_clearances = [
        {
            'clearance_from': 'IT Department',
            'clearance_type': 'IT Assets',
            'description': 'Return laptop, mobile, access cards',
            'checklist_items': '["Laptop", "Mobile Phone", "Access Card", "VPN Token"]',
            'is_mandatory': True,
            'status': random.choice([ClearanceStatus.PENDING, ClearanceStatus.IN_PROGRESS, ClearanceStatus.COMPLETED])
        },
        {
            'clearance_from': 'Admin Department',
            'clearance_type': 'Administrative',
            'description': 'Return keys, ID card, office supplies',
            'checklist_items': '["Office Keys", "ID Card", "Office Supplies"]',
            'is_mandatory': True,
            'status': random.choice([ClearanceStatus.PENDING, ClearanceStatus.IN_PROGRESS, ClearanceStatus.COMPLETED])
        },
        {
            'clearance_from': 'Finance Department',
            'clearance_type': 'Financial',
            'description': 'Settle advances, expenses, loans',
            'checklist_items': '["Clear Advances", "Submit Expenses", "Loan Settlement"]',
            'is_mandatory': True,
            'status': random.choice([ClearanceStatus.PENDING, ClearanceStatus.IN_PROGRESS, ClearanceStatus.COMPLETED])
        },
        {
            'clearance_from': 'HR Department',
            'clearance_type': 'HR',
            'description': 'Exit interview, documentation',
            'checklist_items': '["Exit Interview", "Documentation", "Feedback Form"]',
            'is_mandatory': True,
            'status': random.choice([ClearanceStatus.PENDING, ClearanceStatus.COMPLETED])
        },
        {
            'clearance_from': 'Reporting Manager',
            'clearance_type': 'Handover',
            'description': 'Knowledge transfer and handover',
            'checklist_items': '["Project Handover", "Knowledge Transfer", "Access Transfer"]',
            'is_mandatory': True,
            'status': random.choice([ClearanceStatus.PENDING, ClearanceStatus.COMPLETED])
        }
    ]
    
    clearances = []
    for clearance_data in default_clearances:
        clearance = ExitClearance(
            tenant_id=tenant_id,
            resignation_id=resignation.id,
            due_date=resignation.last_working_date - timedelta(days=7),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **clearance_data
        )
        
        # Add clearance remarks if completed
        if clearance.status == ClearanceStatus.COMPLETED:
            clearance.cleared_date = datetime.now() - timedelta(days=random.randint(1, 5))
            clearance.clearance_remarks = f'All items cleared from {clearance.clearance_from}'
        
        session.add(clearance)
        clearances.append(clearance)
    
    await session.flush()
    return clearances


async def create_settlement_for_resignation(session, resignation, employee, tenant_id: str):
    """Create Full & Final settlement for a resignation"""
    
    settlement_data = {
        'tenant_id': tenant_id,
        'settlement_code': f'FNF{datetime.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}',
        'resignation_id': resignation.id,
        'employee_id': employee.id,
        'status': random.choice([SettlementStatus.CALCULATED, SettlementStatus.APPROVED, SettlementStatus.PAID]),
        'settlement_from_date': resignation.resignation_date.replace(day=1),
        'settlement_to_date': resignation.last_working_date,
        
        # Salary
        'basic_salary_days': random.randint(15, 30),
        'basic_salary_amount': Decimal(random.randint(20000, 50000)),
        
        # Leave
        'total_leave_balance': Decimal(random.randint(5, 20)),
        'encashable_leaves': Decimal(random.randint(5, 15)),
        'leave_encashment_amount': Decimal(random.randint(5000, 15000)),
        
        # Notice period
        'notice_period_shortfall_days': random.randint(0, 10),
        'notice_pay_recovery': Decimal(random.randint(0, 10000)),
        
        # Gratuity
        'years_of_service': Decimal(random.randint(2, 10)),
        'gratuity_eligible': True,
        'gratuity_amount': Decimal(random.randint(50000, 200000)),
        
        # Bonus
        'bonus_amount': Decimal(random.randint(10000, 30000)),
        'incentive_amount': Decimal(random.randint(5000, 15000)),
        
        # Reimbursements
        'pending_reimbursement_amount': Decimal(random.randint(0, 5000)),
        
        # Recoveries
        'loan_recovery': Decimal(random.randint(0, 20000)),
        'advance_recovery': Decimal(random.randint(0, 5000)),
        'asset_loss_recovery': Decimal(random.randint(0, 3000)),
        'other_recovery': Decimal(0),
        
        # Tax
        'tds_amount': Decimal(random.randint(5000, 15000)),
        'professional_tax': Decimal(200),
        
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Calculate totals
    gross_payable = (
        settlement_data['basic_salary_amount'] +
        settlement_data['leave_encashment_amount'] +
        settlement_data['gratuity_amount'] +
        settlement_data['bonus_amount'] +
        settlement_data['incentive_amount'] +
        settlement_data['pending_reimbursement_amount']
    )
    
    total_deductions = (
        settlement_data['notice_pay_recovery'] +
        settlement_data['loan_recovery'] +
        settlement_data['advance_recovery'] +
        settlement_data['asset_loss_recovery'] +
        settlement_data['tds_amount'] +
        settlement_data['professional_tax']
    )
    
    settlement_data['gross_payable'] = gross_payable
    settlement_data['total_deductions'] = total_deductions
    settlement_data['net_payable'] = gross_payable - total_deductions
    
    # Add workflow data based on status
    if settlement_data['status'] in [SettlementStatus.CALCULATED, SettlementStatus.APPROVED, SettlementStatus.PAID]:
        settlement_data['calculated_date'] = datetime.now() - timedelta(days=3)
        settlement_data['calculation_remarks'] = 'Settlement calculated as per company policy'
    
    if settlement_data['status'] in [SettlementStatus.APPROVED, SettlementStatus.PAID]:
        settlement_data['approved_date'] = datetime.now() - timedelta(days=2)
        settlement_data['approval_remarks'] = 'Settlement approved for payment'
    
    if settlement_data['status'] == SettlementStatus.PAID:
        settlement_data['payment_date'] = datetime.now() - timedelta(days=1)
        settlement_data['payment_mode'] = 'bank_transfer'
        settlement_data['payment_reference'] = f'PAY{random.randint(100000, 999999)}'
        settlement_data['finance_processed_date'] = datetime.now() - timedelta(days=1)
        settlement_data['finance_remarks'] = 'Payment processed successfully'
    
    settlement = ExitSettlement(**settlement_data)
    session.add(settlement)
    await session.flush()
    
    return settlement


async def create_documents_for_resignation(session, resignation, employee, tenant_id: str):
    """Create exit documents for a resignation"""
    
    document_types = [
        (ExitDocumentType.EXPERIENCE_LETTER, 'Experience Letter', 'Employment experience certificate'),
        (ExitDocumentType.RELIEVING_LETTER, 'Relieving Letter', 'Official relieving letter'),
        (ExitDocumentType.SERVICE_CERTIFICATE, 'Service Certificate', 'Service certificate for records')
    ]
    
    documents = []
    for doc_type, doc_name, description in document_types:
        document = ExitDocument(
            tenant_id=tenant_id,
            document_code=f'DOC{datetime.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}',
            resignation_id=resignation.id,
            employee_id=employee.id,
            document_type=doc_type,
            document_name=doc_name,
            description=description,
            is_generated=True,
            is_approved=random.choice([True, False]),
            is_issued=random.choice([True, False]),
            generated_date=datetime.now() - timedelta(days=2),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if document.is_approved:
            document.approved_date = datetime.now() - timedelta(days=1)
            document.approval_remarks = 'Document approved for issuance'
        
        if document.is_issued:
            document.issued_date = datetime.now()
            document.issue_remarks = 'Document issued to employee'
            document.delivery_mode = 'email'
            document.is_digitally_signed = True
        
        session.add(document)
        documents.append(document)
    
    await session.flush()
    return documents


async def seed_data(tenant_id: str = None):
    """Main seed data function"""
    print(f"{Colors.BOLD}Exit Management Seed Data Generator{Colors.ENDC}\n")
    
    if not tenant_id:
        print_info("No tenant ID provided. Using default tenant.")
        tenant_id = str(uuid4())
    
    async with get_async_session() as session:
        async with session.begin():
            # Get sample employees
            employees = await get_sample_employees(session, tenant_id)
            
            if not employees:
                print_error("Cannot proceed without employees")
                return
            
            print_info(f"Creating sample resignations for {len(employees)} employees...\n")
            
            # Create resignations with different statuses
            statuses = [
                ResignationStatus.SUBMITTED,
                ResignationStatus.UNDER_REVIEW,
                ResignationStatus.APPROVED,
                ResignationStatus.COMPLETED,
                ResignationStatus.REJECTED
            ]
            
            total_created = {
                'resignations': 0,
                'clearances': 0,
                'settlements': 0,
                'documents': 0
            }
            
            for i, employee in enumerate(employees[:len(statuses)]):
                status = statuses[i]
                
                print_info(f"Creating resignation for {employee.first_name} {employee.last_name} ({status.value})...")
                
                # Create resignation
                resignation = await create_resignation_with_workflow(session, employee, tenant_id, status)
                total_created['resignations'] += 1
                print_success(f"  Created resignation: {resignation.resignation_code}")
                
                # Create clearances
                if status in [ResignationStatus.UNDER_REVIEW, ResignationStatus.APPROVED, ResignationStatus.COMPLETED]:
                    clearances = await create_clearances_for_resignation(session, resignation, tenant_id)
                    total_created['clearances'] += len(clearances)
                    print_success(f"  Created {len(clearances)} clearances")
                
                # Create settlement
                if status in [ResignationStatus.APPROVED, ResignationStatus.COMPLETED]:
                    settlement = await create_settlement_for_resignation(session, resignation, employee, tenant_id)
                    total_created['settlements'] += 1
                    print_success(f"  Created settlement: {settlement.settlement_code}")
                
                # Create documents
                if status in [ResignationStatus.APPROVED, ResignationStatus.COMPLETED]:
                    documents = await create_documents_for_resignation(session, resignation, employee, tenant_id)
                    total_created['documents'] += len(documents)
                    print_success(f"  Created {len(documents)} documents")
                
                print()  # Blank line
            
            print(f"\n{Colors.BOLD}Seed Data Summary:{Colors.ENDC}")
            print(f"  Resignations: {total_created['resignations']}")
            print(f"  Clearances: {total_created['clearances']}")
            print(f"  Settlements: {total_created['settlements']}")
            print(f"  Documents: {total_created['documents']}")
            print(f"\n{Colors.OKGREEN}Seed data created successfully!{Colors.ENDC}")


async def main():
    """Main entry point"""
    print("=" * 70)
    print("Exit Management Seed Data Script".center(70))
    print("=" * 70 + "\n")
    
    # Get tenant ID from environment or use default
    tenant_id = os.getenv('TENANT_ID')
    
    await seed_data(tenant_id)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Seed data creation interrupted{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

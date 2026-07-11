"""add_hrms_loans_module

Revision ID: 012_add_hrms_loans_module
Revises: 011_add_rbi_returns_module
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012_add_hrms_loans_module'
down_revision = '011_add_rbi_returns_module'
branch_labels = None
depends_on = None


def upgrade():
    # Create loan policy table
    op.create_table(
        'hrms_loan_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('policy_code', sa.String(50), nullable=False),
        sa.Column('policy_name', sa.String(200), nullable=False),
        sa.Column('loan_type', sa.Enum('personal', 'vehicle', 'home', 'education', 'medical', 
                                       'marriage', 'salary_advance', 'emergency', 'festival_advance', 
                                       'other', name='loantype'), nullable=False),
        
        # Eligibility
        sa.Column('min_service_months', sa.Integer, nullable=False, server_default='6'),
        sa.Column('min_employment_type', sa.String(50)),
        sa.Column('allowed_employment_statuses', sa.Text),
        sa.Column('allowed_designations', sa.Text),
        sa.Column('allowed_departments', sa.Text),
        
        # Limits
        sa.Column('min_loan_amount', sa.Numeric(15, 2), nullable=False, server_default='10000.00'),
        sa.Column('max_loan_amount', sa.Numeric(15, 2), nullable=False, server_default='500000.00'),
        sa.Column('max_loan_as_salary_multiple', sa.Numeric(5, 2)),
        sa.Column('max_emi_as_salary_percentage', sa.Numeric(5, 2), nullable=False, server_default='40.00'),
        
        # Interest & Tenure
        sa.Column('interest_rate', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('min_tenure_months', sa.Integer, nullable=False, server_default='6'),
        sa.Column('max_tenure_months', sa.Integer, nullable=False, server_default='60'),
        
        # Repayment
        sa.Column('repayment_frequency', sa.Enum('monthly', 'quarterly', 'half_yearly', 'annual', 
                                                 'bullet', name='repaymentfrequency'), 
                  nullable=False, server_default='monthly'),
        sa.Column('processing_fee_percentage', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('prepayment_allowed', sa.Boolean, server_default='true'),
        sa.Column('prepayment_penalty_percentage', sa.Numeric(5, 2), server_default='0.00'),
        
        # Restrictions
        sa.Column('max_active_loans_per_employee', sa.Integer, server_default='1'),
        sa.Column('min_gap_between_loans_months', sa.Integer, server_default='0'),
        
        # Approval Workflow
        sa.Column('requires_manager_approval', sa.Boolean, server_default='true'),
        sa.Column('requires_hr_approval', sa.Boolean, server_default='true'),
        sa.Column('requires_finance_approval', sa.Boolean, server_default='true'),
        sa.Column('auto_approve_below_amount', sa.Numeric(15, 2)),
        
        # Documents
        sa.Column('required_documents', sa.Text),
        
        # Status
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('effective_from', sa.Date),
        sa.Column('effective_to', sa.Date),
        sa.Column('description', sa.Text),
        
        # Audit
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, server_default='false')
    )
    
    # Indexes for loan policies
    op.create_index('idx_tenant_loan_policy_code', 'hrms_loan_policies', ['tenant_id', 'policy_code'], unique=True)
    op.create_index('idx_loan_policy_type', 'hrms_loan_policies', ['tenant_id', 'loan_type', 'is_active'])

    
    # Create employee loan table
    op.create_table(
        'hrms_employee_loans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('loan_code', sa.String(50), nullable=False),
        
        # References
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_type', sa.Enum('personal', 'vehicle', 'home', 'education', 'medical', 
                                       'marriage', 'salary_advance', 'emergency', 'festival_advance', 
                                       'other', name='loantype'), nullable=False),
        
        # Loan Details
        sa.Column('loan_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('interest_rate', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('tenure_months', sa.Integer, nullable=False),
        sa.Column('repayment_frequency', sa.Enum('monthly', 'quarterly', 'half_yearly', 'annual', 
                                                 'bullet', name='repaymentfrequency'), 
                  nullable=False, server_default='monthly'),
        
        # EMI
        sa.Column('emi_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_interest', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_repayment_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('processing_fee', sa.Numeric(15, 2), server_default='0.00'),
        
        # Application
        sa.Column('application_date', sa.Date, nullable=False),
        sa.Column('purpose', sa.Text, nullable=False),
        sa.Column('reason_for_loan', sa.Text),
        sa.Column('attachment_urls', sa.Text),
        
        # Disbursement
        sa.Column('disbursement_date', sa.Date),
        sa.Column('disbursement_mode', sa.String(20)),
        sa.Column('disbursement_reference', sa.String(100)),
        sa.Column('disbursed_amount', sa.Numeric(15, 2)),
        
        # Repayment
        sa.Column('repayment_start_date', sa.Date),
        sa.Column('first_emi_date', sa.Date),
        sa.Column('last_emi_date', sa.Date),
        
        # Outstanding
        sa.Column('principal_outstanding', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('interest_outstanding', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_outstanding', sa.Numeric(15, 2), server_default='0.00'),
        
        # Paid
        sa.Column('principal_paid', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('interest_paid', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_paid', sa.Numeric(15, 2), server_default='0.00'),
        
        # Status
        sa.Column('status', sa.Enum('draft', 'submitted', 'pending_approval', 'approved', 'rejected', 
                                    'disbursed', 'active', 'closed', 'cancelled', 'written_off', 
                                    name='loanstatus'), nullable=False, server_default='draft'),
        sa.Column('submitted_date', sa.DateTime),
        
        # Manager Approval
        sa.Column('manager_approver_id', postgresql.UUID(as_uuid=True)),
        sa.Column('manager_approval_status', sa.String(20)),
        sa.Column('manager_approval_date', sa.DateTime),
        sa.Column('manager_comments', sa.Text),
        
        # HR Approval
        sa.Column('hr_approver_id', postgresql.UUID(as_uuid=True)),
        sa.Column('hr_approval_status', sa.String(20)),
        sa.Column('hr_approval_date', sa.DateTime),
        sa.Column('hr_comments', sa.Text),
        
        # Finance Approval
        sa.Column('finance_approver_id', postgresql.UUID(as_uuid=True)),
        sa.Column('finance_approval_status', sa.String(20)),
        sa.Column('finance_approval_date', sa.DateTime),
        sa.Column('finance_comments', sa.Text),
        
        # Final
        sa.Column('approved_date', sa.DateTime),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('rejected_date', sa.DateTime),
        sa.Column('rejected_by', postgresql.UUID(as_uuid=True)),
        sa.Column('rejection_reason', sa.Text),
        
        # Closure
        sa.Column('closure_date', sa.Date),
        sa.Column('closure_reason', sa.String(50)),
        sa.Column('closure_remarks', sa.Text),
        
        # Prepayment
        sa.Column('prepayment_allowed_after_months', sa.Integer, server_default='0'),
        sa.Column('prepayment_penalty_percentage', sa.Numeric(5, 2), server_default='0.00'),
        
        # Bank Details
        sa.Column('bank_name', sa.String(100)),
        sa.Column('bank_account_number', sa.String(30)),
        sa.Column('bank_ifsc_code', sa.String(11)),
        
        # Guarantor
        sa.Column('guarantor_employee_id', postgresql.UUID(as_uuid=True)),
        sa.Column('guarantor_name', sa.String(200)),
        sa.Column('guarantor_relation', sa.String(50)),
        sa.Column('guarantor_contact', sa.String(20)),
        
        # Flags
        sa.Column('is_deducting_from_salary', sa.Boolean, server_default='true'),
        sa.Column('is_overdue', sa.Boolean, server_default='false'),
        sa.Column('days_overdue', sa.Integer, server_default='0'),
        
        # Audit
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, server_default='false'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['employee_id'], ['hrms_employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['hrms_loan_policies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['manager_approver_id'], ['hrms_employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['hr_approver_id'], ['hrms_employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['finance_approver_id'], ['hrms_employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['guarantor_employee_id'], ['hrms_employees.id'], ondelete='SET NULL'),
    )
    
    # Indexes for employee loans
    op.create_index('idx_tenant_loan_code', 'hrms_employee_loans', ['tenant_id', 'loan_code'], unique=True)
    op.create_index('idx_tenant_loan_emp', 'hrms_employee_loans', ['tenant_id', 'employee_id', 'status'])
    op.create_index('idx_loan_status', 'hrms_employee_loans', ['tenant_id', 'status', 'is_deleted'])
    op.create_index('idx_loan_type', 'hrms_employee_loans', ['tenant_id', 'loan_type', 'status'])
    op.create_index('idx_loan_disbursement', 'hrms_employee_loans', ['tenant_id', 'disbursement_date'])

    
    # Create EMI schedule table
    op.create_table(
        'hrms_loan_emi_schedule',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('loan_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # EMI Details
        sa.Column('emi_number', sa.Integer, nullable=False),
        sa.Column('emi_due_date', sa.Date, nullable=False),
        
        # Amount Breakdown
        sa.Column('emi_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('principal_component', sa.Numeric(15, 2), nullable=False),
        sa.Column('interest_component', sa.Numeric(15, 2), nullable=False),
        
        # Balance
        sa.Column('opening_principal_balance', sa.Numeric(15, 2), nullable=False),
        sa.Column('closing_principal_balance', sa.Numeric(15, 2), nullable=False),
        
        # Payment
        sa.Column('payment_date', sa.Date),
        sa.Column('amount_paid', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('principal_paid', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('interest_paid', sa.Numeric(15, 2), server_default='0.00'),
        
        # Status
        sa.Column('status', sa.Enum('pending', 'paid', 'overdue', 'partially_paid', 'waived', 
                                    name='emistatus'), nullable=False, server_default='pending'),
        sa.Column('is_overdue', sa.Boolean, server_default='false'),
        sa.Column('days_overdue', sa.Integer, server_default='0'),
        sa.Column('penalty_amount', sa.Numeric(15, 2), server_default='0.00'),
        
        # Payment Reference
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('payroll_run_id', postgresql.UUID(as_uuid=True)),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True)),
        
        # Waiver
        sa.Column('is_waived', sa.Boolean, server_default='false'),
        sa.Column('waived_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('waiver_reason', sa.Text),
        sa.Column('waived_by', postgresql.UUID(as_uuid=True)),
        sa.Column('waived_date', sa.DateTime),
        
        sa.Column('remarks', sa.Text),
        
        # Audit
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, server_default='false'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['loan_id'], ['hrms_employee_loans.id'], ondelete='CASCADE'),
    )
    
    # Indexes for EMI schedule
    op.create_index('idx_tenant_emi_loan', 'hrms_loan_emi_schedule', ['tenant_id', 'loan_id', 'emi_number'])
    op.create_index('idx_emi_due_date', 'hrms_loan_emi_schedule', ['tenant_id', 'emi_due_date', 'status'])
    op.create_index('idx_emi_status', 'hrms_loan_emi_schedule', ['tenant_id', 'status', 'is_overdue'])
    
    # Create loan transactions table
    op.create_table(
        'hrms_loan_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('transaction_code', sa.String(50), nullable=False),
        
        # References
        sa.Column('loan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('emi_schedule_id', postgresql.UUID(as_uuid=True)),
        
        # Transaction Details
        sa.Column('transaction_type', sa.Enum('disbursement', 'emi_payment', 'prepayment', 
                                             'foreclosure', 'waiver', 'adjustment', 'reversal', 
                                             name='transactiontype'), nullable=False),
        sa.Column('transaction_date', sa.Date, nullable=False),
        
        # Amount
        sa.Column('transaction_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('principal_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('interest_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('penalty_amount', sa.Numeric(15, 2), server_default='0.00'),
        
        # Balance After Transaction
        sa.Column('principal_outstanding', sa.Numeric(15, 2), nullable=False),
        sa.Column('interest_outstanding', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_outstanding', sa.Numeric(15, 2), nullable=False),
        
        # Payment
        sa.Column('payment_mode', sa.String(20)),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('payroll_run_id', postgresql.UUID(as_uuid=True)),
        
        # Reversal
        sa.Column('is_reversed', sa.Boolean, server_default='false'),
        sa.Column('reversed_by_transaction_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reversal_reason', sa.Text),
        sa.Column('reversal_date', sa.DateTime),
        
        sa.Column('remarks', sa.Text),
        sa.Column('processed_by', postgresql.UUID(as_uuid=True)),
        
        # Audit
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, server_default='false'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['loan_id'], ['hrms_employee_loans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['emi_schedule_id'], ['hrms_loan_emi_schedule.id'], ondelete='SET NULL'),
    )
    
    # Indexes for transactions
    op.create_index('idx_tenant_txn_code', 'hrms_loan_transactions', ['tenant_id', 'transaction_code'], unique=True)
    op.create_index('idx_txn_loan', 'hrms_loan_transactions', ['tenant_id', 'loan_id', 'transaction_date'])
    op.create_index('idx_txn_type', 'hrms_loan_transactions', ['tenant_id', 'transaction_type', 'transaction_date'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('hrms_loan_transactions')
    op.drop_table('hrms_loan_emi_schedule')
    op.drop_table('hrms_employee_loans')
    op.drop_table('hrms_loan_policies')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS emistatus')
    op.execute('DROP TYPE IF EXISTS loanstatus')
    op.execute('DROP TYPE IF EXISTS repaymentfrequency')
    op.execute('DROP TYPE IF EXISTS loantype')

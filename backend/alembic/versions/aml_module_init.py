"""AML/CFT Module Initial Migration

Revision ID: aml_001
Revises: 
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'aml_001'
down_revision = None  # Update this to point to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Create AML/CFT tables
    This migration creates all tables for:
    - Transaction Monitoring
    - AML Alerts
    - CTR (Cash Transaction Reports)
    - STR (Suspicious Transaction Reports)
    - PEP (Politically Exposed Person) Screening
    - Sanction List Screening
    - Audit Logs
    """
    
    # Import AML models to create tables
    from backend.shared.database import aml_models
    from backend.shared.database.models import Base
    from backend.shared.database.session import engine
    
    # Create all AML tables
    Base.metadata.create_all(bind=engine, tables=[
        aml_models.AMLTransactionMonitoring.__table__,
        aml_models.AMLMonitoringRule.__table__,
        aml_models.AMLAlert.__table__,
        aml_models.AMLAlertWorkflow.__table__,
        aml_models.AMLCTRReport.__table__,
        aml_models.AMLSTRReport.__table__,
        aml_models.AMLPEPScreening.__table__,
        aml_models.AMLSanctionList.__table__,
        aml_models.AMLSanctionScreening.__table__,
        aml_models.AMLAuditLog.__table__,
    ])


def downgrade():
    """Drop AML/CFT tables"""
    op.drop_table('aml_audit_logs')
    op.drop_table('aml_sanction_screening')
    op.drop_table('aml_sanction_lists')
    op.drop_table('aml_pep_screening')
    op.drop_table('aml_str_reports')
    op.drop_table('aml_ctr_reports')
    op.drop_table('aml_alert_workflows')
    op.drop_table('aml_alerts')
    op.drop_table('aml_monitoring_rules')
    op.drop_table('aml_transaction_monitoring')

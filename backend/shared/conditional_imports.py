"""
Conditional Module Imports
Imports modules only if their feature flags are enabled to save memory
"""
from backend.shared.config import settings
import logging

logger = logging.getLogger(__name__)

def get_enabled_routers():
    """
    Dynamically import and return only the routers for enabled modules
    This reduces memory usage by not loading disabled modules
    """
    routers = []
    
    # Core modules (always enabled)
    logger.info("Loading core modules...")
    from backend.services.auth.router import router as auth_router
    from backend.services.dashboard.router import router as dashboard_router
    routers.append(("auth", auth_router, "/api/auth"))
    routers.append(("dashboard", dashboard_router, "/api/dashboard"))
    
    # Master Data
    if settings.ENABLE_MASTERDATA:
        logger.info("Loading masterdata module...")
        from backend.services.masterdata.router import router as masterdata_router
        routers.append(("masterdata", masterdata_router, "/api/masterdata"))
    
    # Customer Management
    if settings.ENABLE_CUSTOMERS:
        logger.info("Loading customer module...")
        from backend.services.customer.router import router as customer_router
        from backend.services.customer.timeline_router import router as customer_timeline_router
        routers.append(("customers", customer_router, "/api/customers"))
        routers.append(("customer_timeline", customer_timeline_router, "/api/customers"))
        
        # Customer sub-modules (only if main module enabled)
        if settings.ENABLE_EKYC:
            from backend.services.customer.ekyc_router import router as customer_ekyc_router
            routers.append(("customer_ekyc", customer_ekyc_router, "/api/customers"))
        
        if settings.ENABLE_DIGILOCKER:
            from backend.services.customer.digilocker_router import router as customer_digilocker_router
            routers.append(("customer_digilocker", customer_digilocker_router, "/api/customers"))
    
    # Loan Management
    if settings.ENABLE_LOANS:
        logger.info("Loading loan module...")
        from backend.services.loan import router as loan_router
        routers.append(("loans", loan_router, "/api/loans"))
        
        # Loan extensions
        if settings.ENABLE_VEHICLE_LOANS:
            from backend.services.loan.extensions import vehicle_loan_router
            routers.append(("vehicle_loans", vehicle_loan_router, "/api/loans"))
        
        if settings.ENABLE_PROPERTY_LOANS:
            from backend.services.loan.extensions import property_loan_router
            routers.append(("property_loans", property_loan_router, "/api/loans"))
        
        if settings.ENABLE_NACH:
            from backend.services.lms.nach_router import router as nach_router
            routers.append(("nach", nach_router, "/api/lms"))
        
        if settings.ENABLE_RESTRUCTURING:
            from backend.services.lms.restructuring_router import router as restructuring_router
            routers.append(("restructuring", restructuring_router, "/api/lms"))
    
    # Gold Loans
    if settings.ENABLE_GOLD_LOANS:
        logger.info("Loading gold loans module...")
        from backend.services.gold.router import router as gold_loan_router
        routers.append(("gold_loans", gold_loan_router, "/api/gold-loans"))
    
    # Accounting
    if settings.ENABLE_ACCOUNTING:
        logger.info("Loading accounting module...")
        from backend.services.accounting.router import router as accounting_router
        routers.append(("accounting", accounting_router, "/api/accounting"))
        
        from backend.services.accounting.tds_router import router as tds_router
        from backend.services.accounting.gst_router import router as gst_router
        from backend.services.accounting.asset_router import router as asset_router
        routers.append(("tds", tds_router, "/api/accounting"))
        routers.append(("gst", gst_router, "/api/accounting"))
        routers.append(("assets", asset_router, "/api/accounting"))
    
    # Deposits
    if settings.ENABLE_DEPOSITS:
        logger.info("Loading deposits module...")
        from backend.services.deposit import (
            product_router, 
            account_router, 
            interest_router,
            passbook_router,
            statement_router,
            certificate_router,
            batch_router,
            reports_router
        )
        routers.append(("deposit_products", product_router, "/api/deposits"))
        routers.append(("deposit_accounts", account_router, "/api/deposits"))
        routers.append(("deposit_interest", interest_router, "/api/deposits"))
        routers.append(("deposit_passbook", passbook_router, "/api/deposits"))
        routers.append(("deposit_statement", statement_router, "/api/deposits"))
        routers.append(("deposit_certificate", certificate_router, "/api/deposits"))
        routers.append(("deposit_batch", batch_router, "/api/deposits"))
        routers.append(("deposit_reports", reports_router, "/api/deposits"))
    
    # Workflow
    if settings.ENABLE_WORKFLOW:
        logger.info("Loading workflow module...")
        from backend.services.workflow import template_router, instance_router, task_router
        routers.append(("workflow_templates", template_router, "/api/workflow"))
        routers.append(("workflow_instances", instance_router, "/api/workflow"))
        routers.append(("workflow_tasks", task_router, "/api/workflow"))
    
    # Rules Engine
    if settings.ENABLE_RULES_ENGINE:
        logger.info("Loading rules engine...")
        from backend.services.rules import category_router, evaluation_router, decision_router as rules_decision_router
        routers.append(("rules_categories", category_router, "/api/rules"))
        routers.append(("rules_evaluation", evaluation_router, "/api/rules"))
        routers.append(("rules_decision", rules_decision_router, "/api/rules"))
    
    # Decision Engine
    if settings.ENABLE_DECISION_ENGINE:
        logger.info("Loading decision engine...")
        from backend.services.decision import router as decision_router
        routers.append(("decision", decision_router, "/api/decision"))
    
    # Notifications
    if settings.ENABLE_NOTIFICATIONS:
        logger.info("Loading notifications module...")
        from backend.services.notification import router as notification_router
        routers.append(("notifications", notification_router, "/api/notifications"))
    
    # Bureau Integration
    if settings.ENABLE_BUREAU_INTEGRATION:
        logger.info("Loading bureau integration...")
        from backend.services.integration.bureau_router import router as bureau_integration_router
        routers.append(("bureau", bureau_integration_router, "/api/integration"))
    
    # Bank Statement Analysis
    if settings.ENABLE_BANK_STATEMENT:
        logger.info("Loading bank statement analysis...")
        from backend.services.integration.bank_statement_router import router as bank_statement_router
        routers.append(("bank_statement", bank_statement_router, "/api/integration"))
    
    # OCR
    if settings.ENABLE_OCR:
        logger.info("Loading OCR module...")
        from backend.services.integration.ocr_router import router as ocr_router
        routers.append(("ocr", ocr_router, "/api/integration"))
    
    # Compliance
    if settings.ENABLE_COMPLIANCE:
        logger.info("Loading compliance module...")
        from backend.services.compliance.router import router as compliance_router
        routers.append(("compliance", compliance_router, "/api/compliance"))
    
    # Risk Management
    if settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Loading risk management...")
        from backend.services.risk.router import router as risk_router
        routers.append(("risk", risk_router, "/api/risk"))
    
    # Treasury
    if settings.ENABLE_TREASURY:
        logger.info("Loading treasury module...")
        from backend.services.treasury.bank_account_router import router as treasury_bank_account_router
        from backend.services.treasury.cash_position_router import router as treasury_cash_position_router
        from backend.services.treasury.reconciliation_router import router as treasury_reconciliation_router
        from backend.services.treasury.fund_transfer_router import router as treasury_fund_transfer_router
        routers.append(("treasury_bank_accounts", treasury_bank_account_router, "/api/treasury"))
        routers.append(("treasury_cash", treasury_cash_position_router, "/api/treasury"))
        routers.append(("treasury_reconciliation", treasury_reconciliation_router, "/api/treasury"))
        routers.append(("treasury_transfers", treasury_fund_transfer_router, "/api/treasury"))
    
    # ALM
    if settings.ENABLE_ALM:
        logger.info("Loading ALM module...")
        from backend.services.treasury.alm_router import router as alm_router
        routers.append(("alm", alm_router, "/api/treasury/alm"))
    
    # Branch Operations
    if settings.ENABLE_BRANCH:
        logger.info("Loading branch module...")
        from backend.services.branch import (
            organization_router as branch_organization_router, 
            branch_router, 
            day_operation_router, 
            cash_router, 
            performance_router
        )
        routers.append(("branch_org", branch_organization_router, "/api/branch"))
        routers.append(("branches", branch_router, "/api/branch"))
        routers.append(("branch_operations", day_operation_router, "/api/branch"))
        routers.append(("branch_cash", cash_router, "/api/branch"))
        routers.append(("branch_performance", performance_router, "/api/branch"))
    
    # HRMS
    if settings.ENABLE_HRMS:
        logger.info("Loading HRMS module...")
        from backend.services.hrms import (
            employee_router, 
            department_router, 
            designation_router,
            ess_router
        )
        routers.append(("employees", employee_router, "/api/hrms"))
        routers.append(("departments", department_router, "/api/hrms"))
        routers.append(("designations", designation_router, "/api/hrms"))
        routers.append(("ess", ess_router, "/api/hrms/ess"))
    
    # CRM
    if settings.ENABLE_CRM:
        logger.info("Loading CRM module...")
        from backend.services.crm.account_router import router as crm_account_router
        from backend.services.crm.contact_router import router as crm_contact_router
        routers.append(("crm_accounts", crm_account_router, "/api/crm"))
        routers.append(("crm_contacts", crm_contact_router, "/api/crm"))
        
        if settings.ENABLE_CRM_OPPORTUNITIES:
            from backend.services.crm.opportunity_router import router as crm_opportunity_router
            routers.append(("crm_opportunities", crm_opportunity_router, "/api/crm"))
        
        if settings.ENABLE_CRM_SALES:
            from backend.services.crm.sales_router import router as crm_sales_router
            routers.append(("crm_sales", crm_sales_router, "/api/crm"))
        
        if settings.ENABLE_CRM_SERVICE:
            from backend.services.crm.service_router import router as crm_service_router
            routers.append(("crm_service", crm_service_router, "/api/crm"))
    
    # DMS
    if settings.ENABLE_DMS:
        logger.info("Loading DMS module...")
        from backend.services.dms.router import router as dms_router
        routers.append(("dms", dms_router, "/api/dms"))
    
    # Legal
    if settings.ENABLE_LEGAL:
        logger.info("Loading legal module...")
        from backend.services.legal.contract_router import router as legal_contract_router
        from backend.services.legal.license_router import router as legal_license_router
        routers.append(("legal_contracts", legal_contract_router, "/api/legal"))
        routers.append(("legal_licenses", legal_license_router, "/api/legal"))
    
    # Insurance
    if settings.ENABLE_INSURANCE:
        logger.info("Loading insurance module...")
        from backend.services.insurance import (
            policy_router as insurance_policy_router,
            premium_router as insurance_premium_router,
            claim_router as insurance_claim_router,
            commission_router as insurance_commission_router
        )
        routers.append(("insurance_policies", insurance_policy_router, "/api/insurance"))
        routers.append(("insurance_premiums", insurance_premium_router, "/api/insurance"))
        routers.append(("insurance_claims", insurance_claim_router, "/api/insurance"))
        routers.append(("insurance_commissions", insurance_commission_router, "/api/insurance"))
    
    # File Upload (utility - always enable if customers or loans enabled)
    if settings.ENABLE_CUSTOMERS or settings.ENABLE_LOANS:
        from backend.services.file_upload.router import router as file_upload_router
        routers.append(("file_upload", file_upload_router, "/api/files"))
    
    logger.info(f"Total routers loaded: {len(routers)}")
    return routers

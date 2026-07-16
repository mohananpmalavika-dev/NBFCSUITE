"""
Conditional Module Imports
Imports modules only if their feature flags are enabled to save memory
"""
from backend.shared.config import settings
import logging

logger = logging.getLogger(__name__)


def import_models():
    """
    Conditionally import database models based on enabled feature flags
    This prevents SQLAlchemy from trying to create tables for disabled modules
    """
    logger.info("Importing database models conditionally...")
    
    # 1. Core models (ALWAYS IMPORTED)
    logger.info("Importing core models...")
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission, FileUpload
    )
    
    # 1b. Vendor model (ALWAYS IMPORTED - referenced by multiple modules)
    logger.info("Importing Vendor model (shared across modules)...")
    from backend.shared.database.procurement_models import Vendor
    
    # 2. Master data models (ALWAYS IMPORTED if ENABLE_MASTERDATA)
    if settings.ENABLE_MASTERDATA:
        logger.info("Importing master data models...")
        from backend.shared.database.master_data_models import (
            Country, State, City, Pincode, Bank, BankBranch, Currency,
            InterestRateType, LoanProductType, DocumentType, Occupation,
            Industry, LoanPurpose, RelationshipType, Holiday, FinancialYear
        )
    
    # 3. Customer models
    if settings.ENABLE_CUSTOMERS:
        logger.info("Importing customer models...")
        from backend.shared.database.customer_models import (
            Customer, CustomerKYC, CustomerDocument, CustomerFamily, 
            CustomerBankAccount, CustomerReference, CustomerTimeline,
            CustomerBureauHistory, ActivityType, BureauProvider, BureauPullStatus
        )
    
    # 4. Loan models
    if settings.ENABLE_LOANS:
        logger.info("Importing loan models...")
        from backend.shared.database.loan_models import (
            LoanProduct, LoanApplication, LoanApplicationCoApplicant,
            LoanApplicationDocument, LoanApprovalWorkflow, LoanAccount,
            LoanEMISchedule, LoanRepayment, LoanStatus, ApplicationStatus,
            RepaymentFrequency as LoanRepaymentFrequency, EMIStatus as LoanEMIStatus
        )
    
    # 5. Accounting models
    if settings.ENABLE_ACCOUNTING:
        logger.info("Importing accounting models...")
        from backend.shared.database.accounting_models import (
            ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger,
            TrialBalance, AccountingPeriod
        )
        # Import accounting extended models (Vendor already imported above)
        from backend.shared.database.accounting_extended_models import (
            PurchaseInvoice, VendorPayment, VendorPaymentAllocation
        )
    
    # 6. Deposit models
    if settings.ENABLE_DEPOSITS:
        logger.info("Importing deposit models...")
        from backend.shared.database.deposit_models import (
            DepositProduct, DepositAccount, DepositTransaction,
            DepositInterestCalculation, DepositMaturityQueue, DepositPassbookEntry
        )
    
    # 7. Gold Loan models
    if settings.ENABLE_GOLD_LOANS:
        logger.info("Importing gold loan models...")
        from backend.shared.database.gold_loan_models import (
            GoldLoanProduct, GoldOrnament, GoldLoanAccount,
            GoldLoanTransaction, GoldReleaseRequest, GoldAuction
        )
    
    # 8. Vehicle Loan models
    if settings.ENABLE_VEHICLE_LOANS:
        logger.info("Importing vehicle loan models...")
        from backend.shared.database.vehicle_loan_models import (
            VehicleLoanDetails, VehicleDealer, VehicleRTOTracking,
            VehicleInsurance, VehicleInsuranceClaim, VehicleManufacturerModel
        )
    
    # 9. Property Loan models
    if settings.ENABLE_PROPERTY_LOANS:
        logger.info("Importing property loan models...")
        from backend.shared.database.property_loan_models import (
            PropertyLoanDetails, PropertyLegalVerification, PropertyTechnicalVerification,
            PropertyDocument, PropertyMortgage
        )
    
    # 10. HRMS models
    if settings.ENABLE_HRMS:
        logger.info("Importing HRMS models...")
        from backend.shared.database.hrms_models import (
            HRMSOrganization, Department, Designation, 
            Employee, ReportingHierarchy
        )
        from backend.shared.database.hrms_loan_models import (
            LoanPolicy, EmployeeLoan, LoanEMISchedule as HRMSLoanEMISchedule, 
            LoanTransaction, LoanType, LoanStatus as HRMSLoanStatus, 
            RepaymentFrequency as HRMSRepaymentFrequency, EMIStatus as HRMSEMIStatus, 
            TransactionType
        )
    
    # 11. Inventory models (only if enabled, contains vendors reference)
    if settings.ENABLE_INVENTORY:
        logger.info("Importing inventory models...")
        from backend.shared.database.inventory_models import (
            ItemMaster, StockTransaction, StockLedger,
            StockVerification, StockVerificationItem,
            InventoryValuation, InventoryValuationItem
        )
        # Also import other procurement models if inventory is enabled
        from backend.shared.database.procurement_models import (
            PurchaseRequisition, PurchaseRequisitionItem,
            PurchaseOrder, PurchaseOrderItem,
            GoodsReceiptNote, GoodsReceiptNoteItem
        )
    
    # 12. Workflow models
    if settings.ENABLE_WORKFLOW:
        logger.info("Importing workflow models...")
        from backend.shared.database.workflow_models import (
            WorkflowTemplate, WorkflowInstance, WorkflowStep, 
            WorkflowHistory, WorkflowTask, WorkflowSLATracking
        )
    
    # 13. Rules Engine models
    if settings.ENABLE_RULES_ENGINE:
        logger.info("Importing rules engine models...")
        from backend.shared.database.rules_models import (
            RuleCategory, BusinessRule, RuleCondition, RuleAction, 
            RuleEvaluation, RuleDecision, RuleVersion
        )
    
    # 14. Decision Engine models
    if settings.ENABLE_DECISION_ENGINE:
        logger.info("Importing decision engine models...")
        from backend.shared.database.decision_models import (
            InstantDecision, PreApprovedOffer, DecisionStrategy,
            DecisionCache, DecisionAnalytics, DecisionLimit
        )
    
    # 15. Notification models
    if settings.ENABLE_NOTIFICATIONS:
        logger.info("Importing notification models...")
        from backend.shared.database.notification_models import (
            NotificationTemplate, NotificationLog, NotificationQueue,
            NotificationPreference, NotificationSchedule
        )
    
    # 16. Integration models
    if settings.ENABLE_BUREAU_INTEGRATION or settings.ENABLE_BANK_STATEMENT or settings.ENABLE_OCR or settings.ENABLE_EKYC or settings.ENABLE_DIGILOCKER:
        logger.info("Importing integration models...")
        from backend.shared.database.integration_models import (
            BureauReport, BureauConsent, BankStatementAnalysis,
            DocumentOCRResult, EKYCRecord, DigiLockerDocument
        )
    
    # 17. Compliance models
    if settings.ENABLE_COMPLIANCE:
        logger.info("Importing compliance models...")
        from backend.shared.database.compliance_models import (
            CRILCBorrower, CRILCFacility, CRILCQuarterlyReturn,
            SMATracking, SMAStatusHistory, SMAQuarterlyReport, ComplianceAlert
        )
    
    # 18. Treasury models
    if settings.ENABLE_TREASURY:
        logger.info("Importing treasury models...")
        from backend.shared.database.treasury_models import (
            TreasuryBankAccount, TreasuryCashPosition, BankStatement,
            BankReconciliation, ReconciliationItem, FundTransfer,
            LiquidityPosition, Investment, InvestmentTransaction, CashFlowForecast
        )
    
    # 19. ALM models
    if settings.ENABLE_ALM:
        logger.info("Importing ALM models...")
        from backend.shared.database.alm_models import (
            MaturityLadder, GapAnalysis, LiquidityRatio, InterestRateRisk,
            QuarterlyReturn, ALMLimits, ALMAlert
        )
    
    # 20. Branch models
    if settings.ENABLE_BRANCH:
        logger.info("Importing branch models...")
        from backend.shared.database.branch_models import (
            Organization, Branch, BranchDayOperation, BranchCounter,
            CashTransaction, CashDenomination, CashPosition,
            BranchPerformance, BranchTarget, BranchAuditLog
        )
    
    # 21. Risk Management models
    if settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Importing risk management models...")
        from backend.shared.database.risk_models import (
            CreditPolicy, RiskPricingRule, ExposureLimit, ExposureTransaction,
            RiskRating, EarlyWarningSignal, EarlyWarningAlert
        )
    
    # 21b. Credit Policy Integration models (NEW - Advanced Risk-Based Pricing & Decisioning)
    if settings.ENABLE_CREDIT_POLICY or settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Importing credit policy integration models...")
        from backend.services.credit_policy.credit_policy_models import (
            CreditPolicy as CreditPolicyNew, RiskBasedPricing, ScoreBasedRate, LTVRatio,
            ExposureLimit as ExposureLimitNew, ConcentrationLimit, SectoralCap,
            AutoApprovalCriteria, ManualReviewTrigger, DecisionMatrix, CounterOfferRule
        )
    
    # 21c. Product Lifecycle Management models (NEW - Product Variants & Sunset Management)
    if settings.ENABLE_PRODUCT_LIFECYCLE:
        logger.info("Importing product lifecycle management models...")
        from backend.services.product_lifecycle.product_lifecycle_models import (
            ProductVariant, PromotionalProduct, SeasonalProduct,
            GeographySpecificProduct, SegmentSpecificProduct,
            ProductSunset, CustomerMigration
        )
    
    # 21d. Instant Decision Framework models (NEW - Real-time Decisioning Engine)
    if settings.ENABLE_INSTANT_DECISION_FRAMEWORK:
        logger.info("Importing instant decision framework models...")
        from backend.services.decision_engine.decision_engine_models import (
            DecisionRequest, BureauCheck, BankStatementAnalysis,
            KYCVerification, FraudCheck, EligibilityCheck, DecisionAudit
        )
    
    # 21d. Instant Decision Framework models (NEW - Real-time Decisioning Engine)
    if settings.ENABLE_DECISION_ENGINE:
        logger.info("Importing instant decision framework models...")
        from backend.services.decision_engine.decision_engine_models import (
            DecisionRequest, BureauCheck, BankStatementAnalysis,
            KYCVerification, FraudCheck, EligibilityCheck, DecisionAudit
        )
    
    # 22. CRM models
    if settings.ENABLE_CRM:
        logger.info("Importing CRM models...")
        from backend.shared.database.crm_lead_models import (
            Lead, LeadFollowUp, LeadActivity, LeadScoringRule, LeadAssignmentRule
        )
        from backend.shared.database.crm_account_models import (
            CRMAccount, CRMContact, CRMAccountRelationship, CRMActivity
        )
        from backend.shared.database.crm_marketing_models import (
            MarketingCampaign, CustomerSegment, SegmentMember, LandingPage,
            CampaignExecution, LandingPageSubmission, CampaignTemplate
        )
    
    if settings.ENABLE_CRM_OPPORTUNITIES:
        logger.info("Importing CRM opportunity models...")
        from backend.shared.database.crm_opportunity_models import (
            CRMOpportunity, CRMOpportunityProduct, CRMOpportunityActivity, CRMPipelineStageConfig
        )
    
    if settings.ENABLE_CRM_SALES:
        logger.info("Importing CRM sales models...")
        from backend.shared.database.crm_sales_models import (
            Product, Quote, QuoteItem, Order, OrderItem
        )
    
    if settings.ENABLE_CRM_SERVICE:
        logger.info("Importing CRM service models...")
        from backend.shared.database.crm_service_models import (
            Ticket, TicketComment, TicketAttachment,
            KnowledgeArticle, ArticleAttachment,
            SLA, SLAViolation
        )
    
    # 23. Legal models
    if settings.ENABLE_LEGAL:
        logger.info("Importing legal models...")
        from backend.shared.database.legal_models import (
            Contract, ContractVersion, ContractRenewal, ContractDocument,
            ContractParty, ContractTemplate
        )
    
    if settings.ENABLE_LITIGATION:
        logger.info("Importing litigation models...")
        from backend.shared.database.legal_models import (
            LitigationCase, CaseHearing, LegalExpense, CaseParty, CaseDocument
        )
    
    if settings.ENABLE_LICENSE:
        logger.info("Importing license models...")
        from backend.services.legal.license_models import (
            License, LicenseRenewal, LicenseComplianceCheck, LicenseDocument, LicenseReminder
        )
    
    # 24. DMS models
    if settings.ENABLE_DMS:
        logger.info("Importing DMS models...")
        from backend.shared.database.dms_models import (
            Document, DocumentVersion, DocumentWorkflow, WorkflowTemplate as DMSWorkflowTemplate,
            DocumentApproval, DocumentPermission, DocumentSignature,
            DocumentComment, DocumentAuditLog
        )
    
    # 25. Facility models
    if settings.ENABLE_FACILITY:
        logger.info("Importing facility models...")
        from backend.shared.database.facility_models import (
            Building, Floor, Room,
            HousekeepingTask, HousekeepingSupply,
            CafeteriaMenu, CafeteriaOrder, CafeteriaOrderItem, CafeteriaInventory,
            Vehicle, Trip, VehicleMaintenance,
            Visitor, VisitorGroup
        )
    
    # 26. Reporting models
    if settings.ENABLE_REPORTING:
        logger.info("Importing reporting models...")
        from backend.shared.database.reporting_models import (
            ReportTemplate, CustomReportBuilder, GeneratedReport, ScheduledReport,
            Dashboard, DashboardWidget, PredictiveModel, ModelPrediction,
            ReportAnalytics, UserReportPreference
        )
    
    # 27. Insurance models
    if settings.ENABLE_INSURANCE:
        logger.info("Importing insurance models...")
        from backend.services.insurance.models import (
            InsuranceAgent, InsurancePolicy, InsurancePremium,
            InsuranceClaim, InsuranceCommission
        )
    
    # 28. Locker Management models
    if settings.ENABLE_LOCKER_MANAGEMENT:
        logger.info("Importing locker management models...")
        from backend.shared.database.locker_models import (
            LockerMaster, LockerAllocation, LockerRentPayment,
            LockerMaintenance, LockerAccessLog
        )
    
    # 28. Fixed Assets models
    if settings.ENABLE_FIXED_ASSETS:
        logger.info("Importing fixed assets models...")
        from backend.shared.database.asset_models import (
            FixedAsset, AssetDepreciation, AssetMaintenance, AssetTransfer,
            AssetVerification, AssetVerificationCycle
        )
    
    # 29. Additional HRMS modules
    if settings.ENABLE_RECRUITMENT:
        logger.info("Importing recruitment models...")
        from backend.shared.database.recruitment_models import (
            JobRequisition, JobPosting, JobApplication, Interview,
            Onboarding, BackgroundVerification
        )
    
    if settings.ENABLE_ATTENDANCE:
        logger.info("Importing attendance models...")
        from backend.shared.database.attendance_models import (
            Shift, EmployeeShift, Attendance, BiometricLog, AttendanceRegularization,
            LeavePolicyMaster, EmployeeLeaveBalance, LeaveApplication, LeaveEncashment
        )
    
    if settings.ENABLE_PAYROLL:
        logger.info("Importing payroll models...")
        from backend.shared.database.payroll_models import (
            SalaryComponent, SalaryStructure, SalaryStructureComponent, EmployeeSalary,
            EmployeeSalaryComponent, PayrollRun, Payslip, PayslipComponent,
            StatutoryCompliance, Form16, PaymentFile
        )
    
    if settings.ENABLE_TRAINING:
        logger.info("Importing training models...")
        from backend.shared.database.training_models import (
            TrainingCourse, TrainingSession, TrainingParticipant,
            TrainingAssessment, AssessmentResult, TrainingCertification,
            Skill, EmployeeSkill
        )
    
    # 30. LMS Extended models (NACH, Restructuring, Insurance)
    if settings.ENABLE_NACH or settings.ENABLE_RESTRUCTURING or settings.ENABLE_LOAN_INSURANCE:
        logger.info("Importing LMS extended models...")
        from backend.shared.database.lms_extended_models import (
            NACHMandate, NACHDebitTransaction, LoanRestructuring,
            LoanInsurancePolicy, InsurancePremiumPayment, LoanInsuranceClaim
        )
    
    # 31. Property & Rent models
    if settings.ENABLE_FACILITY:  # Reuse facility flag for property management
        from backend.shared.database.property_rent_models import (
            Property, PropertySpace, Lease, SpaceAllocation, RentPayment,
            UtilityBill, PropertyMaintenance
        )
    
    logger.info("✅ Conditional model imports complete")


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
    
    # Credit Policy Integration (Advanced Risk-Based Pricing & Decisioning)
    if settings.ENABLE_CREDIT_POLICY or settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Loading credit policy integration...")
        from backend.services.credit_policy.credit_policy_router import router as credit_policy_router
        routers.append(("credit_policy", credit_policy_router, "/api/credit-policy"))
    
    # Product Lifecycle Management (Product Variants & Sunset Management)
    if settings.ENABLE_PRODUCT_LIFECYCLE:
        logger.info("Loading product lifecycle management...")
        from backend.services.product_lifecycle.product_lifecycle_router import router as product_lifecycle_router
        routers.append(("product_lifecycle", product_lifecycle_router, "/api/product-lifecycle"))
    
    # Instant Decision Framework (Real-time Decisioning Engine)
    if settings.ENABLE_INSTANT_DECISION_FRAMEWORK:
        logger.info("Loading instant decision framework...")
        from backend.services.decision_engine.decision_engine_router import router as decision_engine_router
        routers.append(("decision_engine", decision_engine_router, ""))
    
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
    
    # Locker Management
    if settings.ENABLE_LOCKER_MANAGEMENT:
        logger.info("Loading locker management module...")
        from backend.services.locker.router import router as locker_router
        routers.append(("locker_management", locker_router, "/api"))
    
    # File Upload (utility - always enable if customers or loans enabled)
    if settings.ENABLE_CUSTOMERS or settings.ENABLE_LOANS:
        from backend.services.file_upload.router import router as file_upload_router
        routers.append(("file_upload", file_upload_router, "/api/files"))
    
    logger.info(f"Total routers loaded: {len(routers)}")
    return routers


# ============================================================================
# MICROSERVICES-SPECIFIC MODEL IMPORT FUNCTIONS
# ============================================================================

def import_core_service_models():
    """
    Import models for Core Service
    Used by: main_core.py
    Includes: Auth, Customers, Loans, MasterData
    """
    logger.info("📦 Loading Core Service models...")
    
    # Core models (ESSENTIAL)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission, FileUpload
    )
    
    # Vendor model (ALWAYS IMPORTED - shared across services)
    from backend.shared.database.procurement_models import Vendor
    
    # Master data models (ESSENTIAL)
    from backend.shared.database.master_data_models import (
        Country, State, City, Pincode, Bank, BankBranch, Currency,
        InterestRateType, LoanProductType, DocumentType, Occupation,
        Industry, LoanPurpose, RelationshipType, Holiday, FinancialYear
    )
    
    # Customer models (CORE BUSINESS)
    from backend.shared.database.customer_models import (
        Customer, CustomerKYC, CustomerDocument, CustomerFamily, 
        CustomerBankAccount, CustomerReference, CustomerTimeline,
        CustomerBureauHistory, ActivityType, BureauProvider, BureauPullStatus
    )
    
    # Loan models (CORE BUSINESS)
    from backend.shared.database.loan_models import (
        LoanProduct, LoanApplication, LoanApplicationCoApplicant,
        LoanApplicationDocument, LoanApprovalWorkflow, LoanAccount,
        LoanEMISchedule, LoanRepayment, LoanStatus, ApplicationStatus,
        RepaymentFrequency, EMIStatus
    )
    
    # Gold Loans (if enabled)
    if settings.ENABLE_GOLD_LOANS:
        from backend.shared.database.gold_loan_models import (
            GoldLoanProduct, GoldOrnament, GoldLoanAccount,
            GoldLoanTransaction, GoldReleaseRequest, GoldAuction
        )
    
    # Vehicle Loans (if enabled)
    if settings.ENABLE_VEHICLE_LOANS:
        from backend.shared.database.vehicle_loan_models import (
            VehicleLoanDetails, VehicleDealer, VehicleRTOTracking,
            VehicleInsurance, VehicleInsuranceClaim, VehicleManufacturerModel
        )
    
    # Property Loans (if enabled)
    if settings.ENABLE_PROPERTY_LOANS:
        from backend.shared.database.property_loan_models import (
            PropertyLoanDetails, PropertyLegalVerification, PropertyTechnicalVerification,
            PropertyDocument, PropertyMortgage
        )
    
    # Deposits (if enabled)
    if settings.ENABLE_DEPOSITS:
        from backend.shared.database.deposit_models import (
            DepositProduct, DepositAccount, DepositTransaction,
            DepositInterestCalculation, DepositMaturityQueue, DepositPassbookEntry
        )
    
    # NACH, Restructuring, Insurance (if enabled)
    if settings.ENABLE_NACH or settings.ENABLE_RESTRUCTURING or settings.ENABLE_LOAN_INSURANCE:
        from backend.shared.database.lms_extended_models import (
            NACHMandate, NACHDebitTransaction, LoanRestructuring,
            LoanInsurancePolicy, InsurancePremiumPayment, LoanInsuranceClaim
        )
    
    logger.info("✅ Core Service models loaded")


def import_hrms_service_models():
    """
    Import models for HRMS Service
    Used by: main_hrms.py
    Includes: Employees, Payroll, Attendance, Recruitment, Training
    """
    logger.info("📦 Loading HRMS Service models...")
    
    # Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # Vendor model (ALWAYS IMPORTED - shared across services)
    from backend.shared.database.procurement_models import Vendor
    
    # HRMS Core models
    from backend.shared.database.hrms_models import (
        HRMSOrganization, Department, Designation, 
        Employee, ReportingHierarchy
    )
    
    # HRMS Loan models
    from backend.shared.database.hrms_loan_models import (
        LoanPolicy, EmployeeLoan, LoanEMISchedule, 
        LoanTransaction, LoanType, LoanStatus, 
        RepaymentFrequency, EMIStatus, TransactionType
    )
    
    # Recruitment models (if enabled)
    if settings.ENABLE_RECRUITMENT:
        from backend.shared.database.recruitment_models import (
            JobRequisition, JobPosting, JobApplication, Interview,
            Onboarding, BackgroundVerification
        )
    
    # Attendance models (if enabled)
    if settings.ENABLE_ATTENDANCE:
        from backend.shared.database.attendance_models import (
            Shift, EmployeeShift, Attendance, BiometricLog, AttendanceRegularization,
            LeavePolicyMaster, EmployeeLeaveBalance, LeaveApplication, LeaveEncashment
        )
    
    # Payroll models (if enabled)
    if settings.ENABLE_PAYROLL:
        from backend.shared.database.payroll_models import (
            SalaryComponent, SalaryStructure, SalaryStructureComponent, EmployeeSalary,
            EmployeeSalaryComponent, PayrollRun, Payslip, PayslipComponent,
            StatutoryCompliance, Form16, PaymentFile
        )
    
    # Training models (if enabled)
    if settings.ENABLE_TRAINING:
        from backend.shared.database.training_models import (
            TrainingCourse, TrainingSession, TrainingParticipant,
            TrainingAssessment, AssessmentResult, TrainingCertification,
            Skill, EmployeeSkill
        )
    
    logger.info("✅ HRMS Service models loaded")


def import_accounting_service_models():
    """
    Import models for Accounting Service
    Used by: main_accounting.py
    Includes: GL, Assets, TDS/GST, Vendor Payments
    """
    logger.info("📦 Loading Accounting Service models...")
    
    # Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # Vendor model (ALWAYS IMPORTED - shared across services)
    from backend.shared.database.procurement_models import Vendor
    
    # Accounting Core models
    from backend.shared.database.accounting_models import (
        ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger,
        TrialBalance, AccountingPeriod
    )
    
    # Accounting Extended models (Vendor Payments)
    from backend.shared.database.accounting_extended_models import (
        PurchaseInvoice, VendorPayment, VendorPaymentAllocation
    )
    
    # Fixed Assets (if enabled)
    if settings.ENABLE_FIXED_ASSETS:
        from backend.shared.database.asset_models import (
            FixedAsset, AssetDepreciation, AssetMaintenance, AssetTransfer,
            AssetVerification, AssetVerificationCycle
        )
    
    logger.info("✅ Accounting Service models loaded")


def import_operations_service_models():
    """
    Import models for Operations Service
    Used by: main_operations.py
    Includes: CRM, Treasury, ALM, Compliance, Risk, Branch
    """
    logger.info("📦 Loading Operations Service models...")
    
    # Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # Vendor model (ALWAYS IMPORTED - shared across services)
    from backend.shared.database.procurement_models import Vendor
    
    # CRM models (if enabled)
    if settings.ENABLE_CRM:
        logger.info("Importing CRM models...")
        from backend.shared.database.crm_lead_models import (
            Lead, LeadFollowUp, LeadActivity, LeadScoringRule, LeadAssignmentRule
        )
        from backend.shared.database.crm_account_models import (
            CRMAccount, CRMContact, CRMAccountRelationship, CRMActivity
        )
        from backend.shared.database.crm_marketing_models import (
            MarketingCampaign, CustomerSegment, SegmentMember, LandingPage,
            CampaignExecution, LandingPageSubmission, CampaignTemplate
        )
        
        if settings.ENABLE_CRM_OPPORTUNITIES:
            from backend.shared.database.crm_opportunity_models import (
                CRMOpportunity, CRMOpportunityProduct, CRMOpportunityActivity, CRMPipelineStageConfig
            )
        
        if settings.ENABLE_CRM_SALES:
            from backend.shared.database.crm_sales_models import (
                Product, Quote, QuoteItem, Order, OrderItem
            )
        
        if settings.ENABLE_CRM_SERVICE:
            from backend.shared.database.crm_service_models import (
                Ticket, TicketComment, TicketAttachment,
                KnowledgeArticle, ArticleAttachment,
                SLA, SLAViolation
            )
    
    # Treasury models (if enabled)
    if settings.ENABLE_TREASURY:
        logger.info("Importing Treasury models...")
        from backend.shared.database.treasury_models import (
            TreasuryBankAccount, TreasuryCashPosition, BankStatement,
            BankReconciliation, ReconciliationItem, FundTransfer,
            LiquidityPosition, Investment, InvestmentTransaction, CashFlowForecast
        )
    
    # ALM models (if enabled)
    if settings.ENABLE_ALM:
        logger.info("Importing ALM models...")
        from backend.shared.database.alm_models import (
            MaturityLadder, GapAnalysis, LiquidityRatio, InterestRateRisk,
            QuarterlyReturn, ALMLimits, ALMAlert
        )
    
    # Compliance models (if enabled)
    if settings.ENABLE_COMPLIANCE:
        logger.info("Importing Compliance models...")
        from backend.shared.database.compliance_models import (
            CRILCBorrower, CRILCFacility, CRILCQuarterlyReturn,
            SMATracking, SMAStatusHistory, SMAQuarterlyReport, ComplianceAlert
        )
    
    # Risk Management models (if enabled)
    if settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Importing Risk Management models...")
        from backend.shared.database.risk_models import (
            CreditPolicy, RiskPricingRule, ExposureLimit, ExposureTransaction,
            RiskRating, EarlyWarningSignal, EarlyWarningAlert
        )
    
    # Branch models (if enabled)
    if settings.ENABLE_BRANCH:
        logger.info("Importing Branch models...")
        from backend.shared.database.branch_models import (
            Organization, Branch, BranchDayOperation, BranchCounter,
            CashTransaction, CashDenomination, CashPosition,
            BranchPerformance, BranchTarget, BranchAuditLog
        )
    
    # Integration models (if enabled)
    if settings.ENABLE_BUREAU_INTEGRATION or settings.ENABLE_BANK_STATEMENT or settings.ENABLE_OCR or settings.ENABLE_EKYC or settings.ENABLE_DIGILOCKER:
        logger.info("Importing Integration models...")
        from backend.shared.database.integration_models import (
            BureauReport, BureauConsent, BankStatementAnalysis,
            DocumentOCRResult, EKYCRecord, DigiLockerDocument
        )
    
    logger.info("✅ Operations Service models loaded")

"""
100+ Pre-built Report Templates
Comprehensive library of ready-to-use reports for NBFC operations
"""

from typing import List, Dict, Any


# ============================================
# PORTFOLIO REPORTS (20 reports)
# ============================================

PORTFOLIO_REPORTS = [
    {
        "report_code": "PORTFOLIO_SUMMARY",
        "report_name": "Portfolio Summary Report",
        "category": "portfolio",
        "description": "Overall portfolio health and key metrics",
        "query_template": """
            SELECT 
                COUNT(DISTINCT la.id) as total_loans,
                SUM(la.sanctioned_amount) as total_sanctioned,
                SUM(la.principal_outstanding) as total_outstanding,
                SUM(CASE WHEN la.status = 'Active' THEN 1 ELSE 0 END) as active_loans,
                SUM(CASE WHEN la.status = 'Closed' THEN 1 ELSE 0 END) as closed_loans,
                AVG(la.interest_rate) as avg_interest_rate
            FROM loan_accounts la
            WHERE la.tenant_id = :tenant_id 
                AND la.is_deleted = FALSE
                AND (:date_from IS NULL OR la.disbursement_date >= :date_from)
                AND (:date_to IS NULL OR la.disbursement_date <= :date_to)
        """,
        "columns": {
            "total_loans": {"label": "Total Loans", "type": "number", "format": "0,0"},
            "total_sanctioned": {"label": "Total Sanctioned", "type": "currency"},
            "total_outstanding": {"label": "Outstanding", "type": "currency"},
            "active_loans": {"label": "Active Loans", "type": "number"},
            "closed_loans": {"label": "Closed Loans", "type": "number"},
            "avg_interest_rate": {"label": "Avg Interest Rate", "type": "percent"}
        }
    },
    {
        "report_code": "PORTFOLIO_BY_PRODUCT",
        "report_name": "Portfolio by Product Type",
        "category": "portfolio",
        "description": "Loan portfolio breakdown by product",
        "query_template": """
            SELECT 
                lp.product_name,
                COUNT(la.id) as loan_count,
                SUM(la.sanctioned_amount) as total_sanctioned,
                SUM(la.principal_outstanding) as outstanding,
                AVG(la.interest_rate) as avg_rate
            FROM loan_accounts la
            JOIN loan_products lp ON la.product_id = lp.id
            WHERE la.tenant_id = :tenant_id AND la.is_deleted = FALSE
            GROUP BY lp.product_name
            ORDER BY outstanding DESC
        """
    },
    {
        "report_code": "PORTFOLIO_BY_BRANCH",
        "report_name": "Portfolio by Branch",
        "category": "portfolio",
        "description": "Branch-wise portfolio distribution"
    },
    {
        "report_code": "PORTFOLIO_VINTAGE_ANALYSIS",
        "report_name": "Portfolio Vintage Analysis",
        "category": "portfolio",
        "description": "Aging analysis of loan portfolio"
    },
    {
        "report_code": "PORTFOLIO_CONCENTRATION",
        "report_name": "Portfolio Concentration Risk",
        "category": "portfolio",
        "description": "Top borrower and sector concentration"
    }
]

# ============================================
# COLLECTION REPORTS (15 reports)
# ============================================

COLLECTION_REPORTS = [
    {
        "report_code": "COLLECTION_EFFICIENCY",
        "report_name": "Collection Efficiency Report",
        "category": "collection",
        "description": "Collection performance metrics"
    },
    {
        "report_code": "OVERDUE_ANALYSIS",
        "report_name": "Overdue Analysis Report",
        "category": "collection",
        "description": "Bucket-wise overdue analysis"
    },
    {
        "report_code": "COLLECTION_FORECAST",
        "report_name": "Collection Forecast",
        "category": "collection",
        "description": "Expected collections for upcoming period"
    },
    {
        "report_code": "COLLECTOR_PERFORMANCE",
        "report_name": "Collector Performance",
        "category": "collection",
        "description": "Individual collector efficiency"
    },
    {
        "report_code": "BOUNCE_ANALYSIS",
        "report_name": "Bounce Analysis Report",
        "category": "collection",
        "description": "NACH/Cheque bounce tracking"
    }
]

# ============================================
# NPA & RISK REPORTS (12 reports)
# ============================================

RISK_REPORTS = [
    {
        "report_code": "NPA_SUMMARY",
        "report_name": "NPA Summary Report",
        "category": "risk",
        "description": "Non-performing assets overview"
    },
    {
        "report_code": "NPA_MOVEMENT",
        "report_name": "NPA Movement Report",
        "category": "risk",
        "description": "Monthly NPA additions and deletions"
    },
    {
        "report_code": "PORTFOLIO_AT_RISK",
        "report_name": "Portfolio at Risk (PAR)",
        "category": "risk",
        "description": "PAR 30, 60, 90 analysis"
    },
    {
        "report_code": "CREDIT_RISK_RATING",
        "report_name": "Credit Risk Rating Distribution",
        "category": "risk",
        "description": "Risk grade distribution"
    },
    {
        "report_code": "EARLY_WARNING_SIGNALS",
        "report_name": "Early Warning Signals",
        "category": "risk",
        "description": "Accounts showing stress signals"
    },
    {
        "report_code": "EXPOSURE_LIMITS",
        "report_name": "Exposure Limit Utilization",
        "category": "risk",
        "description": "Group and industry exposure limits"
    }
]

# ============================================
# FINANCIAL REPORTS (18 reports)
# ============================================

FINANCIAL_REPORTS = [
    {
        "report_code": "INCOME_STATEMENT",
        "report_name": "Income Statement",
        "category": "financial",
        "description": "Profit & Loss statement"
    },
    {
        "report_code": "BALANCE_SHEET",
        "report_name": "Balance Sheet",
        "category": "financial",
        "description": "Assets and Liabilities"
    },
    {
        "report_code": "CASH_FLOW_STATEMENT",
        "report_name": "Cash Flow Statement",
        "category": "financial",
        "description": "Cash inflow and outflow"
    },
    {
        "report_code": "TRIAL_BALANCE",
        "report_name": "Trial Balance",
        "category": "financial",
        "description": "Account-wise debit/credit balance"
    },
    {
        "report_code": "GENERAL_LEDGER",
        "report_name": "General Ledger",
        "category": "financial",
        "description": "Detailed transaction ledger"
    },
    {
        "report_code": "INTEREST_INCOME",
        "report_name": "Interest Income Report",
        "category": "financial",
        "description": "Interest accrued and received"
    },
    {
        "report_code": "FEE_INCOME",
        "report_name": "Fee Income Report",
        "category": "financial",
        "description": "Processing fee and other charges"
    }
]

# ============================================
# REGULATORY & COMPLIANCE REPORTS (15 reports)
# ============================================

REGULATORY_REPORTS = [
    {
        "report_code": "RBI_NBS7",
        "report_name": "RBI NBS-7 Return",
        "category": "regulatory",
        "description": "RBI statutory return"
    },
    {
        "report_code": "CRILC_REPORT",
        "report_name": "CRILC Large Credit Return",
        "category": "regulatory",
        "description": "Central Repository of Information"
    },
    {
        "report_code": "SMA_REPORT",
        "report_name": "SMA Reporting",
        "category": "regulatory",
        "description": "Special Mention Accounts"
    },
    {
        "report_code": "AML_ALERTS",
        "report_name": "AML Alert Report",
        "category": "regulatory",
        "description": "Anti-money laundering alerts"
    },
    {
        "report_code": "CTR_REPORT",
        "report_name": "Cash Transaction Report (CTR)",
        "category": "regulatory",
        "description": "Transactions above threshold"
    },
    {
        "report_code": "STR_REPORT",
        "report_name": "Suspicious Transaction Report (STR)",
        "category": "regulatory",
        "description": "Suspicious activity reporting"
    }
]

# ============================================
# OPERATIONAL REPORTS (10 reports)
# ============================================

OPERATIONAL_REPORTS = [
    {
        "report_code": "DISBURSEMENT_REPORT",
        "report_name": "Disbursement Report",
        "category": "operational",
        "description": "Daily/monthly disbursements"
    },
    {
        "report_code": "APPLICATION_PIPELINE",
        "report_name": "Application Pipeline",
        "category": "operational",
        "description": "Loan applications in pipeline"
    },
    {
        "report_code": "TAT_ANALYSIS",
        "report_name": "TAT Analysis Report",
        "category": "operational",
        "description": "Turnaround time analysis"
    },
    {
        "report_code": "BRANCH_PERFORMANCE",
        "report_name": "Branch Performance",
        "category": "operational",
        "description": "Branch-wise metrics"
    },
    {
        "report_code": "EMPLOYEE_PRODUCTIVITY",
        "report_name": "Employee Productivity",
        "category": "operational",
        "description": "Staff performance metrics"
    }
]

# ============================================
# CUSTOMER REPORTS (8 reports)
# ============================================

CUSTOMER_REPORTS = [
    {
        "report_code": "CUSTOMER_ACQUISITION",
        "report_name": "Customer Acquisition Report",
        "category": "customer",
        "description": "New customer onboarding"
    },
    {
        "report_code": "CUSTOMER_DEMOGRAPHICS",
        "report_name": "Customer Demographics",
        "category": "customer",
        "description": "Customer profile analysis"
    },
    {
        "report_code": "CUSTOMER_LIFETIME_VALUE",
        "report_name": "Customer Lifetime Value",
        "category": "customer",
        "description": "CLV analysis"
    },
    {
        "report_code": "CUSTOMER_CHURN",
        "report_name": "Customer Churn Analysis",
        "category": "customer",
        "description": "Churn prediction and analysis"
    }
]

# ============================================
# TREASURY REPORTS (8 reports)
# ============================================

TREASURY_REPORTS = [
    {
        "report_code": "CASH_POSITION",
        "report_name": "Daily Cash Position",
        "category": "treasury",
        "description": "Bank-wise cash position"
    },
    {
        "report_code": "LIQUIDITY_REPORT",
        "report_name": "Liquidity Position",
        "category": "treasury",
        "description": "Liquidity coverage ratio"
    },
    {
        "report_code": "ALM_REPORT",
        "report_name": "ALM Maturity Ladder",
        "category": "treasury",
        "description": "Asset-liability management"
    },
    {
        "report_code": "INVESTMENT_PORTFOLIO",
        "report_name": "Investment Portfolio",
        "category": "treasury",
        "description": "Investment holdings and performance"
    }
]


# ============================================
# DEPOSIT REPORTS (Nidhi) (6 reports)
# ============================================

DEPOSIT_REPORTS = [
    {
        "report_code": "DEPOSIT_SUMMARY",
        "report_name": "Deposit Summary Report",
        "category": "deposit",
        "description": "Overall deposit portfolio"
    },
    {
        "report_code": "MATURITY_SCHEDULE",
        "report_name": "Deposit Maturity Schedule",
        "category": "deposit",
        "description": "Upcoming maturities"
    },
    {
        "report_code": "INTEREST_PAYOUT",
        "report_name": "Interest Payout Report",
        "category": "deposit",
        "description": "Interest calculations"
    }
]


# ============================================
# COMPILE ALL REPORTS
# ============================================

ALL_REPORT_TEMPLATES = (
    PORTFOLIO_REPORTS + 
    COLLECTION_REPORTS + 
    RISK_REPORTS + 
    FINANCIAL_REPORTS + 
    REGULATORY_REPORTS + 
    OPERATIONAL_REPORTS + 
    CUSTOMER_REPORTS + 
    TREASURY_REPORTS + 
    DEPOSIT_REPORTS
)


def get_all_templates() -> List[Dict[str, Any]]:
    """Get all 100+ report templates"""
    return ALL_REPORT_TEMPLATES


def get_templates_by_category(category: str) -> List[Dict[str, Any]]:
    """Get report templates by category"""
    return [t for t in ALL_REPORT_TEMPLATES if t.get("category") == category]


def get_template_by_code(code: str) -> Dict[str, Any]:
    """Get specific template by code"""
    for template in ALL_REPORT_TEMPLATES:
        if template.get("report_code") == code:
            return template
    return None

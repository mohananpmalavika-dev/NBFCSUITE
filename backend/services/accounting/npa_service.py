"""
NPA Management Service
Handles Non-Performing Asset classification, provisioning, and reporting
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum

from backend.shared.database.accounting_models import (
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    GeneralLedger,
    JournalEntryType,
    AccountType
)


class NPACategory(str, Enum):
    """NPA Categories as per RBI norms"""
    STANDARD = "STANDARD"  # 0-30 DPD
    SPECIAL_MENTION_0 = "SMA_0"  # 1-30 DPD
    SPECIAL_MENTION_1 = "SMA_1"  # 31-60 DPD
    SPECIAL_MENTION_2 = "SMA_2"  # 61-90 DPD
    SUBSTANDARD = "SUBSTANDARD"  # 91-365 DPD
    DOUBTFUL_1 = "DOUBTFUL_1"  # 366-730 DPD (1-2 years)
    DOUBTFUL_2 = "DOUBTFUL_2"  # 731-1095 DPD (2-3 years)
    DOUBTFUL_3 = "DOUBTFUL_3"  # 1096+ DPD (3+ years)
    LOSS = "LOSS"  # Identified loss assets


class ProvisioningRate(str, Enum):
    """Provisioning rates as per RBI norms"""
    STANDARD = "0.25"  # 0.25% for standard assets
    SPECIAL_MENTION = "0.00"  # No provisioning for SMA
    SUBSTANDARD_SECURED = "15.00"  # 15% for secured substandard
    SUBSTANDARD_UNSECURED = "25.00"  # 25% for unsecured substandard
    DOUBTFUL_1_SECURED = "25.00"  # 25% for secured doubtful 1 year
    DOUBTFUL_1_UNSECURED = "100.00"  # 100% for unsecured portion
    DOUBTFUL_2_SECURED = "40.00"  # 40% for secured doubtful 2 years
    DOUBTFUL_3_SECURED = "100.00"  # 100% for secured doubtful 3 years
    LOSS = "100.00"  # 100% for loss assets


class NPAService:
    """Service for NPA management and provisioning"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    
    # ========================================================================
    # NPA Classification Logic
    # ========================================================================
    
    def classify_asset(
        self,
        days_past_due: int,
        is_restructured: bool = False,
        is_written_off: bool = False
    ) -> NPACategory:
        """
        Classify asset based on DPD (Days Past Due)
        As per RBI prudential norms for NBFCs
        """
        if is_written_off:
            return NPACategory.LOSS
        
        if days_past_due <= 0:
            return NPACategory.STANDARD
        elif days_past_due <= 30:
            return NPACategory.SPECIAL_MENTION_0
        elif days_past_due <= 60:
            return NPACategory.SPECIAL_MENTION_1
        elif days_past_due <= 90:
            return NPACategory.SPECIAL_MENTION_2
        elif days_past_due <= 365:
            return NPACategory.SUBSTANDARD
        elif days_past_due <= 730:
            return NPACategory.DOUBTFUL_1
        elif days_past_due <= 1095:
            return NPACategory.DOUBTFUL_2
        else:
            return NPACategory.DOUBTFUL_3
    
    def calculate_provisioning_rate(
        self,
        npa_category: NPACategory,
        is_secured: bool = True,
        security_coverage_ratio: Decimal = Decimal("100.00")
    ) -> Decimal:
        """
        Calculate provisioning rate based on NPA category and security
        Returns provisioning percentage
        """
        if npa_category == NPACategory.STANDARD:
            return Decimal(ProvisioningRate.STANDARD.value)
        
        elif npa_category in [
            NPACategory.SPECIAL_MENTION_0,
            NPACategory.SPECIAL_MENTION_1,
            NPACategory.SPECIAL_MENTION_2
        ]:
            return Decimal(ProvisioningRate.SPECIAL_MENTION.value)
        
        elif npa_category == NPACategory.SUBSTANDARD:
            if is_secured:
                return Decimal(ProvisioningRate.SUBSTANDARD_SECURED.value)
            else:
                return Decimal(ProvisioningRate.SUBSTANDARD_UNSECURED.value)
        
        elif npa_category == NPACategory.DOUBTFUL_1:
            if is_secured:
                # 25% on secured portion + 100% on unsecured portion
                secured_portion = min(security_coverage_ratio, Decimal("100.00"))
                unsecured_portion = Decimal("100.00") - secured_portion
                
                provisioning = (
                    (secured_portion * Decimal(ProvisioningRate.DOUBTFUL_1_SECURED.value) / Decimal("100.00")) +
                    (unsecured_portion * Decimal(ProvisioningRate.DOUBTFUL_1_UNSECURED.value) / Decimal("100.00"))
                )
                return provisioning
            else:
                return Decimal(ProvisioningRate.DOUBTFUL_1_UNSECURED.value)
        
        elif npa_category == NPACategory.DOUBTFUL_2:
            if is_secured:
                # 40% on secured portion + 100% on unsecured portion
                secured_portion = min(security_coverage_ratio, Decimal("100.00"))
                unsecured_portion = Decimal("100.00") - secured_portion
                
                provisioning = (
                    (secured_portion * Decimal(ProvisioningRate.DOUBTFUL_2_SECURED.value) / Decimal("100.00")) +
                    (unsecured_portion * Decimal(ProvisioningRate.DOUBTFUL_1_UNSECURED.value) / Decimal("100.00"))
                )
                return provisioning
            else:
                return Decimal(ProvisioningRate.DOUBTFUL_1_UNSECURED.value)
        
        elif npa_category == NPACategory.DOUBTFUL_3:
            # 100% provisioning for Doubtful 3
            return Decimal(ProvisioningRate.DOUBTFUL_3_SECURED.value)
        
        elif npa_category == NPACategory.LOSS:
            return Decimal(ProvisioningRate.LOSS.value)
        
        return Decimal("0.00")
    
    def calculate_provisioning_amount(
        self,
        outstanding_principal: Decimal,
        npa_category: NPACategory,
        is_secured: bool = True,
        security_coverage_ratio: Decimal = Decimal("100.00"),
        existing_provision: Decimal = Decimal("0.00")
    ) -> Dict[str, Decimal]:
        """
        Calculate required provisioning amount
        Returns dict with required_provision, additional_provision, and provisioning_rate
        """
        provisioning_rate = self.calculate_provisioning_rate(
            npa_category=npa_category,
            is_secured=is_secured,
            security_coverage_ratio=security_coverage_ratio
        )
        
        required_provision = (outstanding_principal * provisioning_rate / Decimal("100.00"))
        additional_provision = max(required_provision - existing_provision, Decimal("0.00"))
        
        return {
            "required_provision": required_provision,
            "additional_provision": additional_provision,
            "provisioning_rate": provisioning_rate,
            "outstanding_principal": outstanding_principal,
            "existing_provision": existing_provision
        }
    
    # ========================================================================
    # Loan Asset Classification
    # ========================================================================
    
    async def classify_loan_portfolio(
        self,
        as_of_date: date
    ) -> List[Dict[str, Any]]:
        """
        Classify entire loan portfolio as of a specific date
        This would typically query loan accounts from LMS
        """
        # This is a placeholder - in production, this would query actual loan accounts
        # from the LMS service and calculate DPD for each loan
        
        # Query would look like:
        # SELECT loan_id, customer_id, outstanding_principal, last_payment_date,
        #        security_value, is_secured, days_past_due
        # FROM loan_accounts
        # WHERE tenant_id = self.tenant_id AND status = 'ACTIVE'
        
        classifications = []
        
        # For now, return structure that would be populated from actual loan data
        return classifications
    
    async def get_loan_classification(
        self,
        loan_account_id: int,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Get classification for a specific loan account
        """
        # This would query the loan account and calculate classification
        # Placeholder for structure
        
        return {
            "loan_account_id": loan_account_id,
            "as_of_date": as_of_date,
            "days_past_due": 0,
            "npa_category": NPACategory.STANDARD,
            "outstanding_principal": Decimal("0.00"),
            "provisioning_required": Decimal("0.00"),
            "provisioning_rate": Decimal("0.00")
        }

    
    # ========================================================================
    # Asset Classification Register
    # ========================================================================
    
    async def generate_asset_classification_register(
        self,
        as_of_date: date,
        category_filter: Optional[NPACategory] = None
    ) -> Dict[str, Any]:
        """
        Generate Asset Classification Register
        Shows all loans by classification category
        """
        # In production, this would query actual loan data
        # For now, structure the expected output
        
        register = {
            "as_of_date": as_of_date,
            "generated_at": datetime.utcnow(),
            "summary": {
                "total_accounts": 0,
                "total_outstanding": Decimal("0.00"),
                "total_provision": Decimal("0.00"),
                "npa_ratio": Decimal("0.00")
            },
            "categories": {}
        }
        
        # Structure for each category
        for category in NPACategory:
            if category_filter and category != category_filter:
                continue
            
            register["categories"][category.value] = {
                "category": category.value,
                "account_count": 0,
                "total_outstanding": Decimal("0.00"),
                "total_provision": Decimal("0.00"),
                "provisioning_rate": self.calculate_provisioning_rate(category),
                "accounts": []
            }
        
        return register
    
    async def get_npa_summary(
        self,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Get summary of NPA statistics
        """
        summary = {
            "as_of_date": as_of_date,
            "total_portfolio": {
                "account_count": 0,
                "outstanding_amount": Decimal("0.00")
            },
            "standard_assets": {
                "account_count": 0,
                "outstanding_amount": Decimal("0.00"),
                "percentage": Decimal("0.00")
            },
            "sma_assets": {
                "account_count": 0,
                "outstanding_amount": Decimal("0.00"),
                "percentage": Decimal("0.00")
            },
            "npa_assets": {
                "account_count": 0,
                "outstanding_amount": Decimal("0.00"),
                "percentage": Decimal("0.00")
            },
            "gross_npa_ratio": Decimal("0.00"),
            "net_npa_ratio": Decimal("0.00"),
            "total_provision": Decimal("0.00")
        }
        
        return summary

    
    # ========================================================================
    # NPA Movement Reports
    # ========================================================================
    
    async def generate_npa_movement_report(
        self,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """
        Generate NPA Movement Report
        Shows movement of accounts between categories
        """
        movement_report = {
            "from_date": from_date,
            "to_date": to_date,
            "generated_at": datetime.utcnow(),
            "opening_balance": {
                "npa_accounts": 0,
                "npa_amount": Decimal("0.00")
            },
            "additions": {
                "fresh_npa": {
                    "account_count": 0,
                    "amount": Decimal("0.00"),
                    "accounts": []
                },
                "increased_provision": {
                    "account_count": 0,
                    "amount": Decimal("0.00")
                }
            },
            "reductions": {
                "upgrades": {
                    "account_count": 0,
                    "amount": Decimal("0.00"),
                    "accounts": []
                },
                "recoveries": {
                    "account_count": 0,
                    "amount": Decimal("0.00"),
                    "accounts": []
                },
                "write_offs": {
                    "account_count": 0,
                    "amount": Decimal("0.00"),
                    "accounts": []
                }
            },
            "closing_balance": {
                "npa_accounts": 0,
                "npa_amount": Decimal("0.00")
            },
            "movements_by_category": {}
        }
        
        # Structure for category-wise movement
        for category in NPACategory:
            movement_report["movements_by_category"][category.value] = {
                "opening": 0,
                "additions": 0,
                "upgrades": 0,
                "downgrades": 0,
                "closing": 0
            }
        
        return movement_report

    
    async def generate_vintage_analysis(
        self,
        as_of_date: date,
        cohort_by: str = "month"  # month, quarter, year
    ) -> Dict[str, Any]:
        """
        Generate vintage analysis report
        Shows NPA rates by loan origination cohorts
        """
        vintage_report = {
            "as_of_date": as_of_date,
            "cohort_by": cohort_by,
            "cohorts": []
        }
        
        # Each cohort would show:
        # - Origination period
        # - Total loans originated
        # - Current outstanding
        # - NPA amount
        # - NPA percentage
        # - Age buckets
        
        return vintage_report
    
    # ========================================================================
    # Provisioning Accounting Entries
    # ========================================================================
    
    async def create_provisioning_entry(
        self,
        loan_account_id: int,
        provision_amount: Decimal,
        npa_category: NPACategory,
        as_of_date: date,
        narration: Optional[str] = None
    ) -> JournalEntry:
        """
        Create accounting entry for loan loss provision
        """
        from backend.services.accounting.accounting_service import AccountingService
        
        accounting_service = AccountingService(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id
        )
        
        if narration is None:
            narration = f"Loan loss provision - Loan #{loan_account_id} - {npa_category.value}"
        
        line_items = [
            # Debit: Provision Expense
            {
                "account_id": await self._get_system_account("PROVISION_EXPENSE"),
                "debit_amount": provision_amount,
                "credit_amount": Decimal("0.00"),
                "description": f"Provision for {npa_category.value} asset"
            },
            # Credit: Provision for Loan Losses
            {
                "account_id": await self._get_system_account("PROVISION_LIABILITY"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": provision_amount,
                "description": f"Provision created for Loan #{loan_account_id}"
            }
        ]
        
        return await accounting_service.create_journal_entry(
            entry_date=as_of_date,
            narration=narration,
            line_items=line_items,
            entry_type=JournalEntryType.PROVISION,
            reference_type="loan_provision",
            reference_id=loan_account_id,
            auto_post=True
        )

    
    async def reverse_provisioning_entry(
        self,
        loan_account_id: int,
        provision_amount: Decimal,
        as_of_date: date,
        narration: Optional[str] = None
    ) -> JournalEntry:
        """
        Reverse provisioning entry (on upgrade or recovery)
        """
        from backend.services.accounting.accounting_service import AccountingService
        
        accounting_service = AccountingService(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id
        )
        
        if narration is None:
            narration = f"Reversal of loan loss provision - Loan #{loan_account_id}"
        
        line_items = [
            # Debit: Provision for Loan Losses (reverse)
            {
                "account_id": await self._get_system_account("PROVISION_LIABILITY"),
                "debit_amount": provision_amount,
                "credit_amount": Decimal("0.00"),
                "description": f"Reversal of provision for Loan #{loan_account_id}"
            },
            # Credit: Provision Expense (or Other Income)
            {
                "account_id": await self._get_system_account("PROVISION_REVERSAL_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": provision_amount,
                "description": "Provision reversal income"
            }
        ]
        
        return await accounting_service.create_journal_entry(
            entry_date=as_of_date,
            narration=narration,
            line_items=line_items,
            entry_type=JournalEntryType.PROVISION,
            reference_type="loan_provision_reversal",
            reference_id=loan_account_id,
            auto_post=True
        )
    
    async def create_write_off_entry(
        self,
        loan_account_id: int,
        write_off_amount: Decimal,
        provision_available: Decimal,
        as_of_date: date,
        narration: Optional[str] = None
    ) -> JournalEntry:
        """
        Create write-off entry for loss assets
        """
        from backend.services.accounting.accounting_service import AccountingService
        
        accounting_service = AccountingService(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id
        )
        
        if narration is None:
            narration = f"Write-off of loan - Loan #{loan_account_id}"
        
        line_items = []
        
        # Use provision to absorb write-off
        if provision_available > 0:
            provision_used = min(provision_available, write_off_amount)
            
            line_items.append({
                "account_id": await self._get_system_account("PROVISION_LIABILITY"),
                "debit_amount": provision_used,
                "credit_amount": Decimal("0.00"),
                "description": "Utilization of provision for write-off"
            })
        else:
            provision_used = Decimal("0.00")
        
        # Any shortfall goes to bad debt expense
        shortfall = write_off_amount - provision_used
        if shortfall > 0:
            line_items.append({
                "account_id": await self._get_system_account("BAD_DEBT_EXPENSE"),
                "debit_amount": shortfall,
                "credit_amount": Decimal("0.00"),
                "description": "Bad debt expense for write-off"
            })
        
        # Credit loan asset account
        line_items.append({
            "account_id": await self._get_system_account("LOAN_ASSET"),
            "debit_amount": Decimal("0.00"),
            "credit_amount": write_off_amount,
            "description": f"Write-off of Loan #{loan_account_id}"
        })
        
        return await accounting_service.create_journal_entry(
            entry_date=as_of_date,
            narration=narration,
            line_items=line_items,
            entry_type=JournalEntryType.WRITE_OFF,
            reference_type="loan_write_off",
            reference_id=loan_account_id,
            auto_post=True
        )
    
    # ========================================================================
    # Regulatory Reports
    # ========================================================================
    
    async def generate_rbi_npa_return(
        self,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Generate NPA return as per RBI format
        """
        rbi_report = {
            "reporting_date": as_of_date,
            "reporting_entity": "NBFC",
            "gross_advances": Decimal("0.00"),
            "gross_npa": Decimal("0.00"),
            "gross_npa_ratio": Decimal("0.00"),
            "provisions_held": Decimal("0.00"),
            "net_npa": Decimal("0.00"),
            "net_npa_ratio": Decimal("0.00"),
            "category_wise_npa": {
                "substandard": Decimal("0.00"),
                "doubtful": Decimal("0.00"),
                "loss": Decimal("0.00")
            },
            "sector_wise_npa": {},
            "security_wise_npa": {
                "secured": Decimal("0.00"),
                "unsecured": Decimal("0.00")
            }
        }
        
        return rbi_report

    
    async def generate_provisioning_coverage_ratio(
        self,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Calculate Provisioning Coverage Ratio (PCR)
        PCR = (Provisions Held / Gross NPAs) * 100
        """
        # This would calculate from actual data
        pcr_report = {
            "as_of_date": as_of_date,
            "gross_npa": Decimal("0.00"),
            "provisions_held": Decimal("0.00"),
            "pcr_percentage": Decimal("0.00"),
            "category_wise_pcr": {
                "substandard": Decimal("0.00"),
                "doubtful_1": Decimal("0.00"),
                "doubtful_2": Decimal("0.00"),
                "doubtful_3": Decimal("0.00"),
                "loss": Decimal("0.00")
            },
            "required_provision": Decimal("0.00"),
            "shortfall": Decimal("0.00")
        }
        
        return pcr_report
    
    # ========================================================================
    # Batch Processing
    # ========================================================================
    
    async def run_monthly_npa_classification(
        self,
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Run monthly NPA classification for entire portfolio
        Returns summary of classifications and provisions created
        """
        result = {
            "as_of_date": as_of_date,
            "processed_at": datetime.utcnow(),
            "total_accounts_processed": 0,
            "classifications": {
                category.value: 0 for category in NPACategory
            },
            "provisions_created": Decimal("0.00"),
            "journal_entries": []
        }
        
        # In production, this would:
        # 1. Query all active loans
        # 2. Calculate DPD for each
        # 3. Classify each loan
        # 4. Calculate required provisions
        # 5. Create provisioning entries
        # 6. Update loan records with classification
        
        return result
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _get_system_account(self, account_key: str) -> int:
        """Get system account ID by key"""
        account_map = {
            "LOAN_ASSET": "1100",
            "PROVISION_LIABILITY": "2400",
            "PROVISION_EXPENSE": "6050",
            "PROVISION_REVERSAL_INCOME": "4020",
            "BAD_DEBT_EXPENSE": "6060"
        }
        
        account_code = account_map.get(account_key)
        if not account_code:
            raise ValueError(f"Unknown system account: {account_key}")
        
        query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.account_code == account_code,
                ChartOfAccounts.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"System account not found: {account_code}")
        
        return account.id

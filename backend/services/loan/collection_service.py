"""
Loan Collection Service
Handles overdue detection, penal interest calculation, DPD tracking, and collection queue
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.loan_models import (
    LoanAccount,
    LoanEMISchedule,
    LoanProduct
)


class LoanCollectionService:
    """Service for managing collections and overdues"""
    
    # DPD Buckets for collection management
    DPD_BUCKETS = {
        "current": (0, 0),
        "bucket_1_30": (1, 30),
        "bucket_31_60": (31, 60),
        "bucket_61_90": (61, 90),
        "bucket_91_180": (91, 180),
        "bucket_180_plus": (181, 999999)
    }
    
    # NPA Classification
    NPA_CLASSIFICATION = {
        "standard": (0, 89),
        "sub_standard": (90, 179),
        "doubtful": (180, 364),
        "loss": (365, 999999)
    }
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def calculate_penal_interest(
        self,
        emi_id: int,
        overdue_days: int,
        overdue_amount: Decimal,
        penal_rate: Decimal
    ) -> Decimal:
        """
        Calculate penal interest for overdue EMI
        Formula: Overdue Amount × Penal Rate × Days / 365
        
        Args:
            emi_id: EMI schedule ID
            overdue_days: Number of days overdue
            overdue_amount: Amount that is overdue
            penal_rate: Penal interest rate (annual %)
            
        Returns:
            Penal interest amount
        """
        if overdue_days <= 0 or overdue_amount <= 0:
            return Decimal("0.00")
        
        # Calculate daily penal rate
        daily_rate = penal_rate / Decimal("36500")  # Convert annual % to daily decimal
        
        # Calculate penal interest
        penal_interest = overdue_amount * daily_rate * Decimal(str(overdue_days))
        
        return penal_interest.quantize(Decimal("0.01"))
    
    async def update_overdue_status(
        self,
        account_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update overdue status for all or specific loan accounts
        Calculates overdue days, penal interest, and DPD
        
        Args:
            account_id: Specific loan account ID (if None, updates all active accounts)
            
        Returns:
            Summary of updates
        """
        today = date.today()
        
        # Build query for loan accounts
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False,
            LoanAccount.status.in_(["active", "overdue"])
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        updated_accounts = 0
        updated_emis = 0
        total_penal_calculated = Decimal("0.00")
        
        for account in accounts:
            # Get loan product for penal rate
            product_query = select(LoanProduct).where(LoanProduct.id == account.loan_product_id)
            product_result = await self.db.execute(product_query)
            product = product_result.scalar_one_or_none()
            
            if not product:
                continue
            
            penal_rate = product.penal_interest_rate
            grace_days = product.grace_period_days or 0
            
            # Get all pending/overdue EMIs
            emi_query = select(LoanEMISchedule).where(
                and_(
                    LoanEMISchedule.loan_account_id == account.id,
                    LoanEMISchedule.tenant_id == self.tenant_id,
                    LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
                )
            ).order_by(LoanEMISchedule.due_date)
            
            emi_result = await self.db.execute(emi_query)
            emis = emi_result.scalars().all()
            
            account_has_overdue = False
            max_dpd = 0
            account_penal = Decimal("0.00")
            
            for emi in emis:
                if emi.due_date < today:
                    # Calculate overdue days
                    days_overdue = (today - emi.due_date).days
                    
                    # Apply grace period
                    effective_overdue = max(0, days_overdue - grace_days)
                    
                    if effective_overdue > 0:
                        account_has_overdue = True
                        emi.overdue_days = effective_overdue
                        emi.status = "overdue"
                        
                        # Calculate unpaid amount
                        unpaid_amount = emi.emi_amount - emi.paid_amount
                        
                        # Calculate penal interest (only on unpaid amount)
                        if unpaid_amount > 0:
                            penal_interest = await self.calculate_penal_interest(
                                emi.id,
                                effective_overdue,
                                unpaid_amount,
                                penal_rate
                            )
                            emi.penal_interest = penal_interest
                            account_penal += penal_interest
                            total_penal_calculated += penal_interest
                        
                        # Track maximum DPD
                        max_dpd = max(max_dpd, effective_overdue)
                        
                        updated_emis += 1
                    else:
                        emi.overdue_days = 0
                        emi.penal_interest = Decimal("0.00")
                else:
                    # Future EMI
                    emi.overdue_days = 0
                    emi.penal_interest = Decimal("0.00")
                
                emi.updated_at = datetime.now()
            
            # Update account overdue status
            if account_has_overdue:
                account.status = "overdue"
                account.overdue_days = max_dpd
                account.dpd = max_dpd
                account.penal_interest_outstanding = account_penal
                
                # Update NPA classification
                npa_status = self._get_npa_classification(max_dpd)
                if account.npa_status != npa_status:
                    account.npa_status = npa_status
                    if npa_status != "standard":
                        account.npa_date = today
                        account.status = "npa"
            else:
                account.status = "active"
                account.overdue_days = 0
                account.dpd = 0
                account.penal_interest_outstanding = Decimal("0.00")
                
                if account.npa_status and account.npa_status != "standard":
                    account.npa_status = "standard"
                    account.npa_date = None
            
            account.updated_at = datetime.now()
            account.updated_by = self.user_id
            updated_accounts += 1
        
        await self.db.commit()
        
        return {
            "accounts_updated": updated_accounts,
            "emis_updated": updated_emis,
            "total_penal_interest_calculated": float(total_penal_calculated),
            "update_date": today.isoformat()
        }
    
    def _get_npa_classification(self, dpd: int) -> str:
        """Get NPA classification based on DPD"""
        for classification, (min_dpd, max_dpd) in self.NPA_CLASSIFICATION.items():
            if min_dpd <= dpd <= max_dpd:
                return classification
        return "loss"
    
    def _get_dpd_bucket(self, dpd: int) -> str:
        """Get DPD bucket name based on DPD"""
        for bucket, (min_dpd, max_dpd) in self.DPD_BUCKETS.items():
            if min_dpd <= dpd <= max_dpd:
                return bucket
        return "bucket_180_plus"
    
    async def get_overdue_accounts(
        self,
        dpd_bucket: Optional[str] = None,
        min_overdue_amount: Optional[Decimal] = None,
        customer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get list of overdue loan accounts
        
        Args:
            dpd_bucket: Filter by DPD bucket (current, bucket_1_30, etc.)
            min_overdue_amount: Minimum overdue amount filter
            customer_id: Filter by customer
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of overdue accounts with details
        """
        # Build query conditions
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False,
            LoanAccount.status.in_(["overdue", "npa"])
        ]
        
        if customer_id:
            conditions.append(LoanAccount.customer_id == customer_id)
        
        if dpd_bucket and dpd_bucket in self.DPD_BUCKETS:
            min_dpd, max_dpd = self.DPD_BUCKETS[dpd_bucket]
            conditions.append(and_(
                LoanAccount.dpd >= min_dpd,
                LoanAccount.dpd <= max_dpd
            ))
        
        # Count total
        count_query = select(func.count(LoanAccount.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get accounts
        query = select(LoanAccount).where(and_(*conditions)).order_by(
            desc(LoanAccount.dpd),
            desc(LoanAccount.total_outstanding)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        # Build response
        overdue_list = []
        for account in accounts:
            # Calculate overdue EMI amount
            emi_query = select(LoanEMISchedule).where(
                and_(
                    LoanEMISchedule.loan_account_id == account.id,
                    LoanEMISchedule.tenant_id == self.tenant_id,
                    LoanEMISchedule.status == "overdue"
                )
            )
            emi_result = await self.db.execute(emi_query)
            overdue_emis = emi_result.scalars().all()
            
            overdue_emi_amount = sum(
                (emi.emi_amount - emi.paid_amount + emi.penal_interest)
                for emi in overdue_emis
            )
            
            # Apply minimum amount filter if provided
            if min_overdue_amount and overdue_emi_amount < min_overdue_amount:
                total -= 1  # Adjust count
                continue
            
            overdue_list.append({
                "loan_account_id": account.id,
                "loan_account_number": account.loan_account_number,
                "customer_id": account.customer_id,
                "sanctioned_amount": float(account.sanctioned_amount),
                "total_outstanding": float(account.total_outstanding),
                "outstanding_principal": float(account.outstanding_principal),
                "outstanding_interest": float(account.outstanding_interest),
                "penal_interest_outstanding": float(account.penal_interest_outstanding),
                "overdue_days": account.overdue_days,
                "dpd": account.dpd,
                "dpd_bucket": self._get_dpd_bucket(account.dpd),
                "npa_status": account.npa_status,
                "overdue_emis_count": len(overdue_emis),
                "overdue_emi_amount": float(overdue_emi_amount),
                "last_payment_date": account.last_payment_date.isoformat() if account.last_payment_date else None,
                "last_payment_amount": float(account.last_payment_amount) if account.last_payment_amount else None,
                "status": account.status,
                "disbursement_date": account.disbursement_date.isoformat()
            })
        
        return {
            "overdue_accounts": overdue_list,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    async def get_collection_queue(
        self,
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate collection queue with prioritization
        Priority: High (DPD > 60), Medium (DPD 30-60), Low (DPD < 30)
        
        Args:
            priority: Filter by priority (high, medium, low)
            
        Returns:
            Collection queue with accounts grouped by priority
        """
        # Get all overdue accounts
        query = select(LoanAccount).where(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False,
                LoanAccount.status.in_(["overdue", "npa"]),
                LoanAccount.dpd > 0
            )
        ).order_by(desc(LoanAccount.dpd))
        
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        # Categorize by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for account in accounts:
            # Calculate overdue amount
            emi_query = select(LoanEMISchedule).where(
                and_(
                    LoanEMISchedule.loan_account_id == account.id,
                    LoanEMISchedule.tenant_id == self.tenant_id,
                    LoanEMISchedule.status == "overdue"
                )
            )
            emi_result = await self.db.execute(emi_query)
            overdue_emis = emi_result.scalars().all()
            
            overdue_amount = sum(
                (emi.emi_amount - emi.paid_amount + emi.penal_interest)
                for emi in overdue_emis
            )
            
            account_info = {
                "loan_account_id": account.id,
                "loan_account_number": account.loan_account_number,
                "customer_id": account.customer_id,
                "dpd": account.dpd,
                "dpd_bucket": self._get_dpd_bucket(account.dpd),
                "npa_status": account.npa_status,
                "total_outstanding": float(account.total_outstanding),
                "overdue_amount": float(overdue_amount),
                "overdue_emis_count": len(overdue_emis),
                "penal_interest": float(account.penal_interest_outstanding),
                "last_payment_date": account.last_payment_date.isoformat() if account.last_payment_date else None
            }
            
            # Categorize by DPD
            if account.dpd > 60:
                account_info["priority"] = "high"
                high_priority.append(account_info)
            elif account.dpd > 30:
                account_info["priority"] = "medium"
                medium_priority.append(account_info)
            else:
                account_info["priority"] = "low"
                low_priority.append(account_info)
        
        # Filter by priority if specified
        if priority:
            if priority == "high":
                filtered = high_priority
            elif priority == "medium":
                filtered = medium_priority
            elif priority == "low":
                filtered = low_priority
            else:
                filtered = high_priority + medium_priority + low_priority
        else:
            filtered = high_priority + medium_priority + low_priority
        
        # Calculate summary
        total_overdue_amount = sum(acc["overdue_amount"] for acc in filtered)
        total_penal_interest = sum(acc["penal_interest"] for acc in filtered)
        
        return {
            "queue": filtered,
            "summary": {
                "total_accounts": len(filtered),
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "total_overdue_amount": total_overdue_amount,
                "total_penal_interest": total_penal_interest
            }
        }
    
    async def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics and metrics
        
        Returns:
            Collection metrics and KPIs
        """
        # Get all accounts
        all_accounts_query = select(LoanAccount).where(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False,
                LoanAccount.status.in_(["active", "overdue", "npa"])
            )
        )
        all_result = await self.db.execute(all_accounts_query)
        all_accounts = all_result.scalars().all()
        
        # Calculate metrics
        total_accounts = len(all_accounts)
        overdue_accounts = len([a for a in all_accounts if a.status in ["overdue", "npa"]])
        
        total_portfolio = sum(a.outstanding_principal for a in all_accounts)
        overdue_portfolio = sum(
            a.outstanding_principal for a in all_accounts 
            if a.status in ["overdue", "npa"]
        )
        
        total_penal = sum(a.penal_interest_outstanding for a in all_accounts)
        
        # DPD bucket distribution
        bucket_distribution = {bucket: 0 for bucket in self.DPD_BUCKETS.keys()}
        for account in all_accounts:
            bucket = self._get_dpd_bucket(account.dpd)
            bucket_distribution[bucket] += 1
        
        # NPA distribution
        npa_distribution = {
            "standard": 0,
            "sub_standard": 0,
            "doubtful": 0,
            "loss": 0
        }
        for account in all_accounts:
            if account.npa_status:
                npa_distribution[account.npa_status] += 1
            else:
                npa_distribution["standard"] += 1
        
        # Collection efficiency (simplified)
        collection_efficiency = (
            ((total_portfolio - overdue_portfolio) / total_portfolio * 100)
            if total_portfolio > 0 else 100.0
        )
        
        return {
            "total_accounts": total_accounts,
            "overdue_accounts": overdue_accounts,
            "overdue_percentage": (overdue_accounts / total_accounts * 100) if total_accounts > 0 else 0,
            "total_portfolio": float(total_portfolio),
            "overdue_portfolio": float(overdue_portfolio),
            "overdue_portfolio_percentage": (float(overdue_portfolio) / float(total_portfolio) * 100) if total_portfolio > 0 else 0,
            "total_penal_interest": float(total_penal),
            "collection_efficiency": float(collection_efficiency),
            "dpd_bucket_distribution": bucket_distribution,
            "npa_distribution": npa_distribution
        }

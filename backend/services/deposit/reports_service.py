"""
Reports and Analytics Service

Provides comprehensive reporting and analytics for deposits
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case, extract
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction,
    DepositInterestCalculation
)
from backend.shared.common.response import CustomException


class ReportsService:
    """Service for reports and analytics"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard"""
        # Overall statistics
        total_accounts = self.db.query(func.count(DepositAccount.id)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).scalar()
        
        active_accounts = self.db.query(func.count(DepositAccount.id)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).scalar()
        
        # Balance totals
        balances = self.db.query(
            func.sum(DepositAccount.principal_amount).label('total_principal'),
            func.sum(DepositAccount.current_balance).label('total_balance'),
            func.sum(DepositAccount.interest_earned).label('total_interest')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).first()
        
        # By account type
        by_type = self.db.query(
            DepositAccount.account_type,
            func.count(DepositAccount.id).label('count'),
            func.sum(DepositAccount.current_balance).label('balance')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.account_type).all()
        
        # Maturity in next 30 days
        maturity_soon = self.db.query(func.count(DepositAccount.id)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date <= date.today() + timedelta(days=30),
                DepositAccount.maturity_date >= date.today(),
                DepositAccount.is_deleted == False
            )
        ).scalar()
        
        # Today's transactions
        today_txns = self.db.query(
            func.count(DepositTransaction.id).label('count'),
            func.sum(DepositTransaction.amount).label('amount')
        ).join(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositTransaction.transaction_date == date.today()
            )
        ).first()
        
        return {
            "summary": {
                "total_accounts": total_accounts or 0,
                "active_accounts": active_accounts or 0,
                "total_principal": float(balances.total_principal or 0),
                "total_balance": float(balances.total_balance or 0),
                "total_interest": float(balances.total_interest or 0)
            },
            "by_type": [
                {
                    "account_type": t.account_type,
                    "count": t.count,
                    "balance": float(t.balance or 0)
                }
                for t in by_type
            ],
            "maturity_alerts": {
                "maturing_soon": maturity_soon or 0
            },
            "today_transactions": {
                "count": today_txns.count or 0,
                "amount": float(today_txns.amount or 0)
            },
            "as_of_date": date.today().isoformat()
        }
    
    def get_deposit_summary(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        account_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get deposit summary"""
        query = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        )
        
        if from_date:
            query = query.filter(DepositAccount.opening_date >= from_date)
        
        if to_date:
            query = query.filter(DepositAccount.opening_date <= to_date)
        
        if account_type:
            query = query.filter(DepositAccount.account_type == account_type)
        
        # Status breakdown
        status_breakdown = self.db.query(
            DepositAccount.status,
            func.count(DepositAccount.id).label('count'),
            func.sum(DepositAccount.current_balance).label('balance')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.status).all()
        
        total_count = query.count()
        total_balance = query.with_entities(
            func.sum(DepositAccount.current_balance)
        ).scalar() or 0
        
        return {
            "period": {
                "from": from_date.isoformat() if from_date else None,
                "to": to_date.isoformat() if to_date else None
            },
            "filter": {
                "account_type": account_type
            },
            "total_accounts": total_count,
            "total_balance": float(total_balance),
            "status_breakdown": [
                {
                    "status": s.status,
                    "count": s.count,
                    "balance": float(s.balance or 0)
                }
                for s in status_breakdown
            ]
        }
    
    def get_maturity_calendar(
        self,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Get maturity calendar"""
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date.between(from_date, to_date),
                DepositAccount.is_deleted == False
            )
        ).order_by(DepositAccount.maturity_date).all()
        
        calendar = []
        total_maturity_amount = Decimal('0')
        
        for account in accounts:
            calendar.append({
                "account_number": account.account_number,
                "account_type": account.account_type,
                "customer_id": str(account.customer_id),
                "maturity_date": account.maturity_date.isoformat(),
                "principal_amount": float(account.principal_amount),
                "maturity_amount": float(account.maturity_amount or account.current_balance),
                "auto_renewal": account.auto_renewal,
                "days_to_maturity": (account.maturity_date - date.today()).days
            })
            
            total_maturity_amount += (account.maturity_amount or account.current_balance)
        
        return {
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat()
            },
            "total_accounts": len(calendar),
            "total_maturity_amount": float(total_maturity_amount),
            "accounts": calendar
        }
    
    def get_interest_accrual_report(
        self,
        from_date: date,
        to_date: date,
        account_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get interest accrual report"""
        query = self.db.query(
            func.sum(DepositInterestCalculation.interest_amount).label('total_interest'),
            func.sum(DepositInterestCalculation.tds_amount).label('total_tds'),
            func.sum(DepositInterestCalculation.net_interest).label('net_interest'),
            func.count(DepositInterestCalculation.id).label('calculation_count')
        ).join(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositInterestCalculation.calculation_period_end.between(from_date, to_date)
            )
        )
        
        if account_type:
            query = query.filter(DepositAccount.account_type == account_type)
        
        result = query.first()
        
        # By account type
        by_type = self.db.query(
            DepositAccount.account_type,
            func.sum(DepositInterestCalculation.interest_amount).label('interest'),
            func.sum(DepositInterestCalculation.tds_amount).label('tds')
        ).join(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositInterestCalculation.calculation_period_end.between(from_date, to_date)
            )
        ).group_by(DepositAccount.account_type).all()
        
        return {
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat()
            },
            "summary": {
                "total_interest": float(result.total_interest or 0),
                "total_tds": float(result.total_tds or 0),
                "net_interest": float(result.net_interest or 0),
                "calculation_count": result.calculation_count or 0
            },
            "by_type": [
                {
                    "account_type": t.account_type,
                    "interest": float(t.interest or 0),
                    "tds": float(t.tds or 0)
                }
                for t in by_type
            ]
        }
    
    def get_aging_analysis(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get aging analysis"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Define age buckets
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).all()
        
        buckets = {
            "0-6 months": {"count": 0, "balance": Decimal('0')},
            "6-12 months": {"count": 0, "balance": Decimal('0')},
            "1-2 years": {"count": 0, "balance": Decimal('0')},
            "2-5 years": {"count": 0, "balance": Decimal('0')},
            "5+ years": {"count": 0, "balance": Decimal('0')}
        }
        
        for account in accounts:
            age_days = (as_of_date - account.opening_date).days
            
            if age_days < 180:
                bucket = "0-6 months"
            elif age_days < 365:
                bucket = "6-12 months"
            elif age_days < 730:
                bucket = "1-2 years"
            elif age_days < 1825:
                bucket = "2-5 years"
            else:
                bucket = "5+ years"
            
            buckets[bucket]["count"] += 1
            buckets[bucket]["balance"] += account.current_balance
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "buckets": {
                bucket: {
                    "count": data["count"],
                    "balance": float(data["balance"])
                }
                for bucket, data in buckets.items()
            }
        }
    
    def get_product_performance(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get product performance"""
        query = self.db.query(
            DepositProduct.product_code,
            DepositProduct.product_name,
            DepositProduct.product_type,
            func.count(DepositAccount.id).label('account_count'),
            func.sum(DepositAccount.principal_amount).label('total_principal'),
            func.sum(DepositAccount.current_balance).label('total_balance'),
            func.sum(DepositAccount.interest_earned).label('total_interest')
        ).join(
            DepositAccount,
            DepositAccount.deposit_product_id == DepositProduct.id
        ).filter(
            and_(
                DepositProduct.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        )
        
        if from_date:
            query = query.filter(DepositAccount.opening_date >= from_date)
        
        if to_date:
            query = query.filter(DepositAccount.opening_date <= to_date)
        
        products = query.group_by(
            DepositProduct.product_code,
            DepositProduct.product_name,
            DepositProduct.product_type
        ).all()
        
        performance = []
        for p in products:
            performance.append({
                "product_code": p.product_code,
                "product_name": p.product_name,
                "product_type": p.product_type,
                "account_count": p.account_count or 0,
                "total_principal": float(p.total_principal or 0),
                "total_balance": float(p.total_balance or 0),
                "total_interest": float(p.total_interest or 0),
                "avg_account_size": float(p.total_balance / p.account_count) if p.account_count > 0 else 0
            })
        
        return {
            "period": {
                "from": from_date.isoformat() if from_date else None,
                "to": to_date.isoformat() if to_date else None
            },
            "products": performance
        }
    
    def get_dormancy_report(self) -> Dict[str, Any]:
        """Get dormancy report"""
        dormant = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'dormant',
                DepositAccount.is_deleted == False
            )
        ).all()
        
        # Near dormant (no transaction in 18 months)
        cutoff_date = date.today() - timedelta(days=540)
        
        near_dormant = []
        active_accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.account_type == 'savings',
                DepositAccount.is_deleted == False
            )
        ).all()
        
        for account in active_accounts:
            last_txn = self.db.query(DepositTransaction).filter(
                and_(
                    DepositTransaction.deposit_account_id == account.id,
                    DepositTransaction.transaction_type.in_(['deposit', 'withdrawal'])
                )
            ).order_by(DepositTransaction.transaction_date.desc()).first()
            
            if last_txn and last_txn.transaction_date < cutoff_date:
                near_dormant.append({
                    "account_number": account.account_number,
                    "last_transaction_date": last_txn.transaction_date.isoformat(),
                    "days_inactive": (date.today() - last_txn.transaction_date).days,
                    "balance": float(account.current_balance)
                })
        
        dormant_list = [
            {
                "account_number": acc.account_number,
                "customer_id": str(acc.customer_id),
                "balance": float(acc.current_balance),
                "opening_date": acc.opening_date.isoformat()
            }
            for acc in dormant
        ]
        
        return {
            "dormant_accounts": {
                "count": len(dormant_list),
                "accounts": dormant_list
            },
            "near_dormant_accounts": {
                "count": len(near_dormant),
                "accounts": near_dormant[:50]  # Limit to 50
            }
        }
    
    def get_tds_summary(
        self,
        financial_year: str,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get TDS summary"""
        # Parse FY
        fy_start_year, fy_end_year = map(int, financial_year.split('-'))
        
        if quarter:
            quarter_dates = {
                1: (date(fy_start_year, 4, 1), date(fy_start_year, 6, 30)),
                2: (date(fy_start_year, 7, 1), date(fy_start_year, 9, 30)),
                3: (date(fy_start_year, 10, 1), date(fy_start_year, 12, 31)),
                4: (date(fy_end_year, 1, 1), date(fy_end_year, 3, 31))
            }
            period_start, period_end = quarter_dates[quarter]
        else:
            period_start = date(fy_start_year, 4, 1)
            period_end = date(fy_end_year, 3, 31)
        
        summary = self.db.query(
            func.sum(DepositInterestCalculation.interest_amount).label('total_interest'),
            func.sum(DepositInterestCalculation.tds_amount).label('total_tds'),
            func.count(DepositInterestCalculation.id).label('calculation_count')
        ).filter(
            and_(
                DepositInterestCalculation.tenant_id == self.tenant_id,
                DepositInterestCalculation.tds_applicable == True,
                DepositInterestCalculation.calculation_period_end.between(period_start, period_end)
            )
        ).first()
        
        return {
            "financial_year": financial_year,
            "quarter": quarter,
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "total_interest": float(summary.total_interest or 0),
            "total_tds": float(summary.total_tds or 0),
            "calculation_count": summary.calculation_count or 0
        }
    
    def get_transaction_volume_report(
        self,
        from_date: date,
        to_date: date,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """Get transaction volume report"""
        # Group transactions by period
        if group_by == "day":
            group_field = func.date(DepositTransaction.transaction_date)
        elif group_by == "week":
            group_field = func.date_trunc('week', DepositTransaction.transaction_date)
        else:  # month
            group_field = func.date_trunc('month', DepositTransaction.transaction_date)
        
        volumes = self.db.query(
            group_field.label('period'),
            func.count(DepositTransaction.id).label('count'),
            func.sum(DepositTransaction.amount).label('amount')
        ).join(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositTransaction.transaction_date.between(from_date, to_date)
            )
        ).group_by('period').order_by('period').all()
        
        return {
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat()
            },
            "group_by": group_by,
            "data": [
                {
                    "period": v.period.isoformat() if v.period else None,
                    "count": v.count or 0,
                    "amount": float(v.amount or 0)
                }
                for v in volumes
            ]
        }

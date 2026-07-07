"""
Regulatory Compliance Service

Handles regulatory reporting including:
- RBI deposit returns
- DICGC reporting
- Deposit concentration reports
- KYC tracking
- Compliance dashboards
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction
)
from backend.shared.database.customer_models import Customer
from backend.shared.common.response import CustomException


class RegulatoryService:
    """Service for regulatory compliance and reporting"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def generate_rbi_deposit_return(
        self,
        return_date: date,
        return_type: str = 'quarterly'  # monthly, quarterly, annual
    ) -> Dict[str, Any]:
        """Generate RBI deposit return"""
        # Get all active deposits
        deposits = self.db.query(
            DepositAccount.account_type,
            func.count(DepositAccount.id).label('account_count'),
            func.sum(DepositAccount.principal_amount).label('total_principal'),
            func.sum(DepositAccount.current_balance).label('total_balance'),
            func.sum(DepositAccount.interest_earned).label('total_interest')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.account_type).all()
        
        # Deposit classification
        by_type = []
        total_deposits = Decimal('0')
        
        for dep in deposits:
            balance = dep.total_balance or Decimal('0')
            total_deposits += balance
            
            by_type.append({
                "deposit_type": dep.account_type,
                "account_count": dep.account_count,
                "outstanding_balance": float(balance),
                "principal_amount": float(dep.total_principal or 0),
                "interest_accrued": float(dep.total_interest or 0)
            })
        
        # Maturity profile (within 1 year, 1-3 years, 3-5 years, 5+ years)
        maturity_profile = self._get_maturity_profile(return_date)
        
        # Interest rate-wise classification
        rate_wise = self._get_rate_wise_classification()
        
        # Top depositors (for concentration risk)
        top_depositors = self._get_top_depositors(limit=20)
        
        return {
            "return_type": return_type,
            "return_date": return_date.isoformat(),
            "reporting_entity": {
                "name": "NBFC/Nidhi Company Name",  # TODO: Get from tenant
                "registration_number": "RBI-XXXXXX"
            },
            "summary": {
                "total_deposits": float(total_deposits),
                "total_accounts": sum(d['account_count'] for d in by_type)
            },
            "by_deposit_type": by_type,
            "maturity_profile": maturity_profile,
            "rate_wise_classification": rate_wise,
            "top_depositors": top_depositors
        }
    
    def generate_dicgc_report(
        self,
        reporting_date: date
    ) -> Dict[str, Any]:
        """Generate DICGC (Deposit Insurance) report"""
        # DICGC insurance limit (₹5 lakh per depositor)
        insurance_limit = Decimal('500000')
        
        # Group deposits by customer
        customer_deposits = self.db.query(
            DepositAccount.customer_id,
            func.sum(DepositAccount.current_balance).label('total_balance')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.customer_id).all()
        
        insured_amount = Decimal('0')
        uninsured_amount = Decimal('0')
        insured_count = 0
        partially_insured_count = 0
        
        for cust_dep in customer_deposits:
            balance = cust_dep.total_balance or Decimal('0')
            
            if balance <= insurance_limit:
                insured_amount += balance
                insured_count += 1
            else:
                insured_amount += insurance_limit
                uninsured_amount += (balance - insurance_limit)
                partially_insured_count += 1
        
        total_deposits = insured_amount + uninsured_amount
        coverage_ratio = (insured_amount / total_deposits * 100) if total_deposits > 0 else 0
        
        return {
            "reporting_date": reporting_date.isoformat(),
            "insurance_limit": float(insurance_limit),
            "summary": {
                "total_depositors": len(customer_deposits),
                "total_deposits": float(total_deposits),
                "insured_amount": float(insured_amount),
                "uninsured_amount": float(uninsured_amount),
                "coverage_ratio": float(coverage_ratio)
            },
            "depositor_classification": {
                "fully_insured": insured_count,
                "partially_insured": partially_insured_count
            }
        }
    
    def generate_concentration_report(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Generate deposit concentration report"""
        if not as_of_date:
            as_of_date = date.today()
        
        # Get total deposits
        total_deposits = self.db.query(
            func.sum(DepositAccount.current_balance)
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).scalar() or Decimal('0')
        
        # Top 10 depositors
        top_10 = self._get_customer_concentration(10)
        top_10_amount = sum(d['total_balance'] for d in top_10)
        top_10_percentage = (top_10_amount / float(total_deposits) * 100) if total_deposits > 0 else 0
        
        # Top 20 depositors
        top_20 = self._get_customer_concentration(20)
        top_20_amount = sum(d['total_balance'] for d in top_20)
        top_20_percentage = (top_20_amount / float(total_deposits) * 100) if total_deposits > 0 else 0
        
        # Single depositor > 10% of total
        large_depositors = [d for d in top_20 if d['percentage'] > 10.0]
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "total_deposits": float(total_deposits),
            "concentration_metrics": {
                "top_10_depositors": {
                    "amount": top_10_amount,
                    "percentage": float(top_10_percentage),
                    "depositors": top_10
                },
                "top_20_depositors": {
                    "amount": top_20_amount,
                    "percentage": float(top_20_percentage)
                },
                "large_depositors_above_10_percent": {
                    "count": len(large_depositors),
                    "depositors": large_depositors
                }
            },
            "risk_assessment": self._assess_concentration_risk(top_10_percentage, len(large_depositors))
        }
    
    def get_kyc_compliance_report(self) -> Dict[str, Any]:
        """Get KYC compliance status for depositors"""
        # Get all active depositors
        depositors = self.db.query(
            DepositAccount.customer_id,
            func.count(DepositAccount.id).label('account_count'),
            func.sum(DepositAccount.current_balance).label('total_balance')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.customer_id).all()
        
        # Check KYC status
        kyc_compliant = 0
        kyc_pending = 0
        kyc_expired = 0
        
        pending_list = []
        
        for dep in depositors:
            customer = self.db.query(Customer).filter(
                Customer.id == dep.customer_id
            ).first()
            
            if customer:
                # Check KYC status (assuming kyc_verified and kyc_expiry_date fields)
                if hasattr(customer, 'kyc_verified') and customer.kyc_verified:
                    if hasattr(customer, 'kyc_expiry_date') and customer.kyc_expiry_date:
                        if customer.kyc_expiry_date > date.today():
                            kyc_compliant += 1
                        else:
                            kyc_expired += 1
                            pending_list.append({
                                "customer_id": str(customer.id),
                                "customer_name": f"{customer.first_name} {customer.last_name}",
                                "total_balance": float(dep.total_balance or 0),
                                "kyc_status": "expired",
                                "kyc_expiry_date": customer.kyc_expiry_date.isoformat()
                            })
                    else:
                        kyc_compliant += 1
                else:
                    kyc_pending += 1
                    pending_list.append({
                        "customer_id": str(customer.id),
                        "customer_name": f"{customer.first_name} {customer.last_name}",
                        "total_balance": float(dep.total_balance or 0),
                        "kyc_status": "pending"
                    })
        
        total_depositors = len(depositors)
        compliance_rate = (kyc_compliant / total_depositors * 100) if total_depositors > 0 else 0
        
        return {
            "as_of_date": date.today().isoformat(),
            "summary": {
                "total_depositors": total_depositors,
                "kyc_compliant": kyc_compliant,
                "kyc_pending": kyc_pending,
                "kyc_expired": kyc_expired,
                "compliance_rate": float(compliance_rate)
            },
            "pending_kyc": pending_list[:50]  # Limit to 50
        }
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive compliance dashboard"""
        today = date.today()
        
        # Basic metrics
        total_accounts = self.db.query(func.count(DepositAccount.id)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).scalar()
        
        total_balance = self.db.query(func.sum(DepositAccount.current_balance)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).scalar() or Decimal('0')
        
        # Concentration risk
        top_10 = self._get_customer_concentration(10)
        concentration_percentage = sum(d['percentage'] for d in top_10)
        
        # Maturity risk
        maturing_30_days = self.db.query(func.count(DepositAccount.id)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date <= today + timedelta(days=30),
                DepositAccount.maturity_date >= today,
                DepositAccount.is_deleted == False
            )
        ).scalar()
        
        # Compliance status
        compliance_score = self._calculate_compliance_score()
        
        return {
            "as_of_date": today.isoformat(),
            "overall_metrics": {
                "total_accounts": total_accounts or 0,
                "total_deposits": float(total_balance),
                "compliance_score": compliance_score
            },
            "risk_indicators": {
                "concentration_risk": {
                    "top_10_percentage": float(concentration_percentage),
                    "risk_level": "High" if concentration_percentage > 50 else "Medium" if concentration_percentage > 30 else "Low"
                },
                "maturity_risk": {
                    "maturing_in_30_days": maturing_30_days or 0
                }
            },
            "compliance_areas": {
                "kyc_compliance": self.get_kyc_compliance_report()['summary'],
                "dicgc_coverage": self.generate_dicgc_report(today)['summary']
            }
        }
    
    # Helper methods
    
    def _get_maturity_profile(self, reference_date: date) -> Dict[str, Any]:
        """Get maturity profile"""
        one_year = reference_date + timedelta(days=365)
        three_years = reference_date + timedelta(days=1095)
        five_years = reference_date + timedelta(days=1825)
        
        within_1_year = self.db.query(func.sum(DepositAccount.maturity_amount)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date <= one_year,
                DepositAccount.maturity_date > reference_date
            )
        ).scalar() or Decimal('0')
        
        one_to_three = self.db.query(func.sum(DepositAccount.maturity_amount)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date > one_year,
                DepositAccount.maturity_date <= three_years
            )
        ).scalar() or Decimal('0')
        
        three_to_five = self.db.query(func.sum(DepositAccount.maturity_amount)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date > three_years,
                DepositAccount.maturity_date <= five_years
            )
        ).scalar() or Decimal('0')
        
        above_five = self.db.query(func.sum(DepositAccount.maturity_amount)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date > five_years
            )
        ).scalar() or Decimal('0')
        
        return {
            "within_1_year": float(within_1_year),
            "1_to_3_years": float(one_to_three),
            "3_to_5_years": float(three_to_five),
            "above_5_years": float(above_five)
        }
    
    def _get_rate_wise_classification(self) -> List[Dict[str, Any]]:
        """Get rate-wise deposit classification"""
        rate_bands = self.db.query(
            case(
                (DepositAccount.interest_rate < 5, "Below 5%"),
                (DepositAccount.interest_rate < 7, "5-7%"),
                (DepositAccount.interest_rate < 9, "7-9%"),
                (DepositAccount.interest_rate >= 9, "Above 9%")
            ).label('rate_band'),
            func.count(DepositAccount.id).label('account_count'),
            func.sum(DepositAccount.current_balance).label('total_balance')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by('rate_band').all()
        
        return [
            {
                "rate_band": band.rate_band,
                "account_count": band.account_count,
                "total_balance": float(band.total_balance or 0)
            }
            for band in rate_bands
        ]
    
    def _get_top_depositors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top depositors"""
        return self._get_customer_concentration(limit)
    
    def _get_customer_concentration(self, limit: int) -> List[Dict[str, Any]]:
        """Get customer concentration"""
        total_deposits = self.db.query(func.sum(DepositAccount.current_balance)).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).scalar() or Decimal('1')
        
        customer_deposits = self.db.query(
            DepositAccount.customer_id,
            func.sum(DepositAccount.current_balance).label('total_balance'),
            func.count(DepositAccount.id).label('account_count')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.customer_id).order_by(
            func.sum(DepositAccount.current_balance).desc()
        ).limit(limit).all()
        
        result = []
        for cust_dep in customer_deposits:
            balance = cust_dep.total_balance or Decimal('0')
            percentage = (balance / total_deposits * 100) if total_deposits > 0 else 0
            
            customer = self.db.query(Customer).filter(
                Customer.id == cust_dep.customer_id
            ).first()
            
            result.append({
                "customer_id": str(cust_dep.customer_id),
                "customer_name": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
                "account_count": cust_dep.account_count,
                "total_balance": float(balance),
                "percentage": float(percentage)
            })
        
        return result
    
    def _assess_concentration_risk(
        self,
        top_10_percentage: float,
        large_depositors_count: int
    ) -> Dict[str, Any]:
        """Assess concentration risk"""
        if top_10_percentage > 50 or large_depositors_count > 3:
            risk_level = "High"
            recommendation = "High concentration risk. Diversify deposit base."
        elif top_10_percentage > 30 or large_depositors_count > 1:
            risk_level = "Medium"
            recommendation = "Moderate concentration risk. Monitor large depositors."
        else:
            risk_level = "Low"
            recommendation = "Acceptable concentration levels."
        
        return {
            "risk_level": risk_level,
            "recommendation": recommendation,
            "top_10_percentage": float(top_10_percentage),
            "large_depositors_count": large_depositors_count
        }
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        # Simple scoring based on multiple factors
        scores = []
        
        # KYC compliance
        kyc_report = self.get_kyc_compliance_report()
        scores.append(kyc_report['summary']['compliance_rate'])
        
        # Concentration risk (inverse - lower is better)
        top_10 = self._get_customer_concentration(10)
        concentration = sum(d['percentage'] for d in top_10)
        concentration_score = max(0, 100 - concentration) if concentration > 50 else 100
        scores.append(concentration_score)
        
        # Average score
        return sum(scores) / len(scores) if scores else 0

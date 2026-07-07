"""
SMA (Special Mention Account) Service
Real-time tracking and quarterly reporting
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
import uuid

from backend.shared.database.compliance_models import (
    SMATracking, SMAStatusHistory, SMAQuarterlyReport, ComplianceAlert,
    CRILCBorrower, SMAStatus, AssetClassification
)
from backend.shared.database.loan_models import LoanAccount, LoanEMISchedule
from .schemas import (
    SMATrackingCreate, SMATrackingResponse,
    SMAQuarterlyReportCreate, SMAQuarterlyReportResponse,
    SMACalculationRequest, SMADashboardStats,
    ComplianceAlertCreate
)


class SMAService:
    """Service for SMA tracking and reporting"""
    
    # SMA Classification Rules (as per RBI)
    SMA_0_DPD = (1, 30)    # 1-30 days overdue
    SMA_1_DPD = (31, 60)   # 31-60 days overdue
    SMA_2_DPD = (61, 90)   # 61-90 days overdue
    NPA_DPD = 91           # >90 days = NPA
    
    # Provision Percentages
    PROVISION_RATES = {
        AssetClassification.STANDARD: Decimal('0.40'),
        AssetClassification.SUB_STANDARD: Decimal('15.00'),
        AssetClassification.DOUBTFUL_1: Decimal('25.00'),
        AssetClassification.DOUBTFUL_2: Decimal('40.00'),
        AssetClassification.DOUBTFUL_3: Decimal('100.00'),
        AssetClassification.LOSS: Decimal('100.00')
    }
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # ========================================================================
    # SMA CALCULATION & TRACKING
    # ========================================================================
    
    def calculate_sma_status(
        self,
        request: SMACalculationRequest,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Calculate SMA status for all or specific loan accounts"""
        
        as_on_date = request.as_on_date
        loan_account_ids = request.loan_account_ids
        calculate_provisions = request.calculate_provisions
        
        # Get loan accounts
        query = self.db.query(LoanAccount).filter(
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        )
        
        if loan_account_ids:
            query = query.filter(LoanAccount.id.in_(loan_account_ids))
        else:
            # Only active accounts
            query = query.filter(
                LoanAccount.status.in_(['active', 'overdue', 'npa'])
            )
        
        loan_accounts = query.all()
        
        results = []
        sma_status_changes = []
        alerts_created = []
        
        for loan in loan_accounts:
            # Calculate DPD (Days Past Due)
            dpd = self._calculate_dpd(loan, as_on_date)
            
            # Determine SMA status
            sma_status = self._determine_sma_status(dpd)
            
            # Get borrower (or create if doesn't exist)
            borrower = self._get_or_create_borrower_for_loan(loan, user_id)
            
            # Get previous tracking
            previous_tracking = self.db.query(SMATracking).filter(
                SMATracking.loan_account_id == loan.id,
                SMATracking.tenant_id == self.tenant_id,
                SMATracking.is_deleted == False
            ).order_by(SMATracking.as_on_date.desc()).first()
            
            previous_status = previous_tracking.current_sma_status if previous_tracking else SMAStatus.STANDARD
            
            # Calculate outstanding amounts
            outstanding_data = self._calculate_outstanding_amounts(loan, as_on_date)
            
            # Calculate asset classification and provisions
            asset_classification = self._determine_asset_classification(dpd, sma_status)
            provision_percentage = self.PROVISION_RATES.get(asset_classification, Decimal('0'))
            provision_required = (outstanding_data['total_outstanding'] * provision_percentage / 100) if calculate_provisions else Decimal('0')
            
            # Create tracking record
            tracking = SMATracking(
                id=uuid.uuid4(),
                tenant_id=self.tenant_id,
                borrower_id=borrower.id,
                loan_account_id=loan.id,
                as_on_date=as_on_date,
                reporting_quarter=self._get_reporting_quarter(as_on_date),
                current_sma_status=sma_status,
                previous_sma_status=previous_status,
                days_past_due=dpd,
                days_in_current_status=self._calculate_days_in_status(
                    previous_tracking, sma_status, as_on_date
                ),
                principal_outstanding=outstanding_data['principal_outstanding'],
                interest_outstanding=outstanding_data['interest_outstanding'],
                total_outstanding=outstanding_data['total_outstanding'],
                principal_overdue=outstanding_data['principal_overdue'],
                interest_overdue=outstanding_data['interest_overdue'],
                total_overdue=outstanding_data['total_overdue'],
                installment_amount=loan.emi_amount,
                last_payment_date=loan.last_payment_date,
                last_payment_amount=loan.last_payment_amount,
                next_due_date=loan.next_due_date,
                asset_classification=asset_classification,
                provision_required=provision_required,
                provision_percentage=provision_percentage,
                alert_triggered=False,
                follow_up_required=False,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(tracking)
            
            # Track status changes
            if sma_status != previous_status:
                self._record_status_change(
                    borrower.id,
                    loan.id,
                    previous_status,
                    sma_status,
                    as_on_date,
                    dpd,
                    outstanding_data['total_outstanding'],
                    outstanding_data['total_overdue'],
                    "auto_calculation",
                    user_id
                )
                
                sma_status_changes.append({
                    'loan_account_number': loan.loan_account_number,
                    'from_status': previous_status,
                    'to_status': sma_status,
                    'dpd': dpd
                })
                
                # Create alert if status degraded
                if self._is_status_degradation(previous_status, sma_status):
                    alert = self._create_sma_alert(
                        borrower.id,
                        loan.id,
                        sma_status,
                        dpd,
                        outstanding_data['total_outstanding'],
                        user_id
                    )
                    tracking.alert_triggered = True
                    alerts_created.append(str(alert.id))
            
            # Update borrower's current status
            borrower.current_sma_status = sma_status
            borrower.current_asset_classification = asset_classification
            borrower.days_past_due = dpd
            
            results.append({
                'loan_account_id': str(loan.id),
                'loan_account_number': loan.loan_account_number,
                'borrower_name': borrower.borrower_name,
                'sma_status': sma_status,
                'dpd': dpd,
                'total_outstanding': float(outstanding_data['total_outstanding']),
                'total_overdue': float(outstanding_data['total_overdue']),
                'provision_required': float(provision_required)
            })
        
        self.db.commit()
        
        return {
            'as_on_date': as_on_date.isoformat(),
            'accounts_processed': len(results),
            'status_changes': len(sma_status_changes),
            'alerts_created': len(alerts_created),
            'results': results,
            'status_changes_detail': sma_status_changes
        }
    
    # ========================================================================
    # SMA TRACKING QUERIES
    # ========================================================================
    
    def get_sma_tracking(
        self,
        tracking_id: UUID
    ) -> Optional[SMATracking]:
        """Get SMA tracking record"""
        return self.db.query(SMATracking).filter(
            SMATracking.id == tracking_id,
            SMATracking.tenant_id == self.tenant_id,
            SMATracking.is_deleted == False
        ).first()
    
    def list_sma_tracking(
        self,
        as_on_date: Optional[date] = None,
        sma_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SMATracking]:
        """List SMA tracking records"""
        
        query = self.db.query(SMATracking).filter(
            SMATracking.tenant_id == self.tenant_id,
            SMATracking.is_deleted == False
        )
        
        if as_on_date:
            query = query.filter(SMATracking.as_on_date == as_on_date)
        
        if sma_status:
            query = query.filter(SMATracking.current_sma_status == sma_status)
        
        query = query.order_by(
            SMATracking.as_on_date.desc(),
            SMATracking.days_past_due.desc()
        )
        
        return query.offset(skip).limit(limit).all()
    
    def get_loan_sma_history(
        self,
        loan_account_id: UUID
    ) -> List[SMATracking]:
        """Get SMA history for a loan account"""
        return self.db.query(SMATracking).filter(
            SMATracking.loan_account_id == loan_account_id,
            SMATracking.tenant_id == self.tenant_id,
            SMATracking.is_deleted == False
        ).order_by(SMATracking.as_on_date.desc()).all()
    
    def get_status_change_history(
        self,
        loan_account_id: Optional[UUID] = None,
        borrower_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SMAStatusHistory]:
        """Get status change history"""
        
        query = self.db.query(SMAStatusHistory).filter(
            SMAStatusHistory.tenant_id == self.tenant_id,
            SMAStatusHistory.is_deleted == False
        )
        
        if loan_account_id:
            query = query.filter(SMAStatusHistory.loan_account_id == loan_account_id)
        
        if borrower_id:
            query = query.filter(SMAStatusHistory.borrower_id == borrower_id)
        
        query = query.order_by(SMAStatusHistory.change_date.desc())
        
        return query.offset(skip).limit(limit).all()
    
    # ========================================================================
    # DASHBOARD & STATISTICS
    # ========================================================================
    
    def get_dashboard_stats(
        self,
        as_on_date: Optional[date] = None
    ) -> SMADashboardStats:
        """Get SMA dashboard statistics"""
        
        if not as_on_date:
            as_on_date = date.today()
        
        # Get latest tracking for each loan account
        subquery = self.db.query(
            SMATracking.loan_account_id,
            func.max(SMATracking.as_on_date).label('max_date')
        ).filter(
            SMATracking.tenant_id == self.tenant_id,
            SMATracking.as_on_date <= as_on_date,
            SMATracking.is_deleted == False
        ).group_by(SMATracking.loan_account_id).subquery()
        
        trackings = self.db.query(SMATracking).join(
            subquery,
            and_(
                SMATracking.loan_account_id == subquery.c.loan_account_id,
                SMATracking.as_on_date == subquery.c.max_date
            )
        ).filter(
            SMATracking.tenant_id == self.tenant_id
        ).all()
        
        stats = {
            'total_accounts': len(trackings),
            'standard': {'count': 0, 'amount': Decimal('0')},
            'sma_0': {'count': 0, 'amount': Decimal('0')},
            'sma_1': {'count': 0, 'amount': Decimal('0')},
            'sma_2': {'count': 0, 'amount': Decimal('0')},
            'npa': {'count': 0, 'amount': Decimal('0')},
            'total_exposure': Decimal('0'),
            'provision_required': Decimal('0')
        }
        
        for tracking in trackings:
            stats['total_exposure'] += tracking.total_outstanding
            stats['provision_required'] += tracking.provision_required
            
            if tracking.current_sma_status == SMAStatus.STANDARD:
                stats['standard']['count'] += 1
                stats['standard']['amount'] += tracking.total_outstanding
            elif tracking.current_sma_status == SMAStatus.SMA_0:
                stats['sma_0']['count'] += 1
                stats['sma_0']['amount'] += tracking.total_outstanding
            elif tracking.current_sma_status == SMAStatus.SMA_1:
                stats['sma_1']['count'] += 1
                stats['sma_1']['amount'] += tracking.total_outstanding
            elif tracking.current_sma_status == SMAStatus.SMA_2:
                stats['sma_2']['count'] += 1
                stats['sma_2']['amount'] += tracking.total_outstanding
            else:
                stats['npa']['count'] += 1
                stats['npa']['amount'] += tracking.total_outstanding
        
        # Get open alerts count
        alerts_count = self.db.query(func.count(ComplianceAlert.id)).filter(
            ComplianceAlert.tenant_id == self.tenant_id,
            ComplianceAlert.status == 'open',
            ComplianceAlert.is_deleted == False
        ).scalar() or 0
        
        return SMADashboardStats(
            total_accounts=stats['total_accounts'],
            standard_count=stats['standard']['count'],
            standard_amount=stats['standard']['amount'],
            sma_0_count=stats['sma_0']['count'],
            sma_0_amount=stats['sma_0']['amount'],
            sma_1_count=stats['sma_1']['count'],
            sma_1_amount=stats['sma_1']['amount'],
            sma_2_count=stats['sma_2']['count'],
            sma_2_amount=stats['sma_2']['amount'],
            npa_count=stats['npa']['count'],
            npa_amount=stats['npa']['amount'],
            total_exposure=stats['total_exposure'],
            provision_required=stats['provision_required'],
            alerts_open=alerts_count
        )
    
    # ========================================================================
    # QUARTERLY REPORT GENERATION
    # ========================================================================
    
    def generate_quarterly_report(
        self,
        data: SMAQuarterlyReportCreate,
        user_id: UUID
    ) -> SMAQuarterlyReport:
        """Generate SMA quarterly report"""
        
        report_number = self._generate_report_number(data.reporting_quarter)
        as_on_date = data.as_on_date
        quarter = data.reporting_quarter
        
        # Get SMA tracking for the quarter
        quarter_trackings = self.db.query(SMATracking).filter(
            SMATracking.tenant_id == self.tenant_id,
            SMATracking.reporting_quarter == quarter,
            SMATracking.as_on_date == as_on_date,
            SMATracking.is_deleted == False
        ).all()
        
        # Calculate statistics
        sma_0 = {'count': 0, 'amount': Decimal('0'), 'new': 0, 'regularized': 0, 'upgraded': 0}
        sma_1 = {'count': 0, 'amount': Decimal('0'), 'new': 0, 'regularized': 0, 'upgraded': 0}
        sma_2 = {'count': 0, 'amount': Decimal('0'), 'new': 0, 'regularized': 0, 'slipped': 0}
        
        for tracking in quarter_trackings:
            if tracking.current_sma_status == SMAStatus.SMA_0:
                sma_0['count'] += 1
                sma_0['amount'] += tracking.total_outstanding
                if tracking.previous_sma_status == SMAStatus.STANDARD:
                    sma_0['new'] += 1
                elif tracking.previous_sma_status == SMAStatus.SMA_1:
                    sma_0['regularized'] += 1
            
            elif tracking.current_sma_status == SMAStatus.SMA_1:
                sma_1['count'] += 1
                sma_1['amount'] += tracking.total_outstanding
                if tracking.previous_sma_status == SMAStatus.SMA_0:
                    sma_1['new'] += 1
                    sma_0['upgraded'] += 1
                elif tracking.previous_sma_status == SMAStatus.SMA_2:
                    sma_1['regularized'] += 1
            
            elif tracking.current_sma_status == SMAStatus.SMA_2:
                sma_2['count'] += 1
                sma_2['amount'] += tracking.total_outstanding
                if tracking.previous_sma_status == SMAStatus.SMA_1:
                    sma_2['new'] += 1
                    sma_1['upgraded'] += 1
            
            elif tracking.current_sma_status in [
                SMAStatus.NPA_SUBSTANDARD,
                SMAStatus.NPA_DOUBTFUL,
                SMAStatus.NPA_LOSS
            ]:
                if tracking.previous_sma_status == SMAStatus.SMA_2:
                    sma_2['slipped'] += 1
        
        # Create report
        report = SMAQuarterlyReport(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            report_number=report_number,
            reporting_quarter=data.reporting_quarter,
            reporting_year=data.reporting_year,
            as_on_date=as_on_date,
            status='draft',
            sma_0_accounts=sma_0['count'],
            sma_0_amount=sma_0['amount'],
            sma_0_new_additions=sma_0['new'],
            sma_0_regularized=sma_0['regularized'],
            sma_0_upgraded_to_sma1=sma_0['upgraded'],
            sma_1_accounts=sma_1['count'],
            sma_1_amount=sma_1['amount'],
            sma_1_new_additions=sma_1['new'],
            sma_1_regularized=sma_1['regularized'],
            sma_1_upgraded_to_sma2=sma_1['upgraded'],
            sma_2_accounts=sma_2['count'],
            sma_2_amount=sma_2['amount'],
            sma_2_new_additions=sma_2['new'],
            sma_2_regularized=sma_2['regularized'],
            sma_2_slipped_to_npa=sma_2['slipped'],
            remarks=data.remarks,
            prepared_by=user_id,
            prepared_date=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _calculate_dpd(self, loan: LoanAccount, as_on_date: date) -> int:
        """Calculate Days Past Due"""
        if not loan.next_due_date or as_on_date < loan.next_due_date:
            return 0
        return (as_on_date - loan.next_due_date).days
    
    def _determine_sma_status(self, dpd: int) -> SMAStatus:
        """Determine SMA status based on DPD"""
        if dpd == 0:
            return SMAStatus.STANDARD
        elif self.SMA_0_DPD[0] <= dpd <= self.SMA_0_DPD[1]:
            return SMAStatus.SMA_0
        elif self.SMA_1_DPD[0] <= dpd <= self.SMA_1_DPD[1]:
            return SMAStatus.SMA_1
        elif self.SMA_2_DPD[0] <= dpd <= self.SMA_2_DPD[1]:
            return SMAStatus.SMA_2
        else:
            return SMAStatus.NPA_SUBSTANDARD
    
    def _determine_asset_classification(
        self,
        dpd: int,
        sma_status: SMAStatus
    ) -> AssetClassification:
        """Determine asset classification"""
        if dpd == 0 or sma_status in [SMAStatus.STANDARD, SMAStatus.SMA_0, SMAStatus.SMA_1, SMAStatus.SMA_2]:
            return AssetClassification.STANDARD
        elif dpd <= 365:
            return AssetClassification.SUB_STANDARD
        elif dpd <= 730:
            return AssetClassification.DOUBTFUL_1
        elif dpd <= 1095:
            return AssetClassification.DOUBTFUL_2
        else:
            return AssetClassification.LOSS
    
    def _calculate_outstanding_amounts(
        self,
        loan: LoanAccount,
        as_on_date: date
    ) -> Dict[str, Decimal]:
        """Calculate outstanding and overdue amounts"""
        
        # Get overdue EMIs
        overdue_emis = self.db.query(LoanEMISchedule).filter(
            LoanEMISchedule.loan_account_id == loan.id,
            LoanEMISchedule.due_date < as_on_date,
            LoanEMISchedule.status.in_(['pending', 'partially_paid', 'overdue']),
            LoanEMISchedule.tenant_id == self.tenant_id
        ).all()
        
        principal_overdue = sum(
            (emi.principal_component - emi.paid_principal) for emi in overdue_emis
        )
        interest_overdue = sum(
            (emi.interest_component - emi.paid_interest) for emi in overdue_emis
        )
        
        return {
            'principal_outstanding': loan.outstanding_principal,
            'interest_outstanding': loan.outstanding_interest,
            'total_outstanding': loan.total_outstanding,
            'principal_overdue': principal_overdue,
            'interest_overdue': interest_overdue,
            'total_overdue': principal_overdue + interest_overdue
        }
    
    def _get_reporting_quarter(self, as_on_date: date) -> str:
        """Get reporting quarter from date"""
        month = as_on_date.month
        year = as_on_date.year
        
        if month <= 3:
            quarter = 'Q4'
            fy_year = f"FY{year-1}-{str(year)[2:]}"
        elif month <= 6:
            quarter = 'Q1'
            fy_year = f"FY{year}-{str(year+1)[2:]}"
        elif month <= 9:
            quarter = 'Q2'
            fy_year = f"FY{year}-{str(year+1)[2:]}"
        else:
            quarter = 'Q3'
            fy_year = f"FY{year}-{str(year+1)[2:]}"
        
        return f"{quarter}{fy_year}"
    
    def _calculate_days_in_status(
        self,
        previous_tracking: Optional[SMATracking],
        current_status: SMAStatus,
        as_on_date: date
    ) -> int:
        """Calculate days in current status"""
        if not previous_tracking:
            return 0
        
        if previous_tracking.current_sma_status == current_status:
            return previous_tracking.days_in_current_status + 1
        else:
            return 1
    
    def _get_or_create_borrower_for_loan(
        self,
        loan: LoanAccount,
        user_id: UUID
    ) -> CRILCBorrower:
        """Get or create CRILC borrower for loan account"""
        
        # Check if borrower exists
        borrower = self.db.query(CRILCBorrower).filter(
            CRILCBorrower.customer_id == loan.customer_id,
            CRILCBorrower.tenant_id == self.tenant_id,
            CRILCBorrower.is_deleted == False
        ).first()
        
        if borrower:
            return borrower
        
        # Create new borrower (simplified)
        from .crilc_service import CRILCService
        crilc_service = CRILCService(self.db, self.tenant_id)
        
        # Get customer details
        from shared.database.customer_models import Customer
        customer = self.db.query(Customer).filter(
            Customer.id == loan.customer_id
        ).first()
        
        if not customer:
            raise ValueError(f"Customer not found for loan {loan.id}")
        
        from .schemas import CRILCBorrowerCreate
        borrower_data = CRILCBorrowerCreate(
            borrower_name=f"{customer.first_name} {customer.last_name}",
            borrower_type='individual',
            pan_number=customer.pan_number,
            customer_id=customer.id
        )
        
        return crilc_service.create_borrower(borrower_data, user_id)
    
    def _record_status_change(
        self,
        borrower_id: UUID,
        loan_account_id: UUID,
        from_status: SMAStatus,
        to_status: SMAStatus,
        change_date: date,
        dpd: int,
        outstanding: Decimal,
        overdue: Decimal,
        triggered_by: str,
        user_id: UUID
    ) -> None:
        """Record SMA status change in history"""
        
        history = SMAStatusHistory(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            borrower_id=borrower_id,
            loan_account_id=loan_account_id,
            from_status=from_status,
            to_status=to_status,
            change_date=change_date,
            dpd_at_change=dpd,
            outstanding_at_change=outstanding,
            overdue_at_change=overdue,
            change_reason=f"Status changed from {from_status} to {to_status} due to {dpd} days overdue",
            triggered_by=triggered_by,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(history)
    
    def _is_status_degradation(
        self,
        from_status: SMAStatus,
        to_status: SMAStatus
    ) -> bool:
        """Check if status change is a degradation"""
        status_order = [
            SMAStatus.STANDARD,
            SMAStatus.SMA_0,
            SMAStatus.SMA_1,
            SMAStatus.SMA_2,
            SMAStatus.NPA_SUBSTANDARD,
            SMAStatus.NPA_DOUBTFUL,
            SMAStatus.NPA_LOSS
        ]
        
        try:
            from_idx = status_order.index(from_status)
            to_idx = status_order.index(to_status)
            return to_idx > from_idx
        except ValueError:
            return False
    
    def _create_sma_alert(
        self,
        borrower_id: UUID,
        loan_account_id: UUID,
        sma_status: SMAStatus,
        dpd: int,
        outstanding: Decimal,
        user_id: UUID
    ) -> ComplianceAlert:
        """Create compliance alert for SMA status change"""
        
        severity_map = {
            SMAStatus.SMA_0: 'low',
            SMAStatus.SMA_1: 'medium',
            SMAStatus.SMA_2: 'high',
            SMAStatus.NPA_SUBSTANDARD: 'critical'
        }
        
        alert = ComplianceAlert(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            alert_type='sma_status_change',
            alert_category='sma',
            severity=severity_map.get(sma_status, 'medium'),
            borrower_id=borrower_id,
            loan_account_id=loan_account_id,
            alert_message=f"Account moved to {sma_status} with {dpd} days overdue",
            alert_details={
                'sma_status': sma_status,
                'dpd': dpd,
                'outstanding_amount': float(outstanding)
            },
            status='open',
            due_date=date.today() + timedelta(days=7),
            is_overdue=False,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(alert)
        return alert
    
    def _generate_report_number(self, quarter: str) -> str:
        """Generate SMA report number"""
        count = self.db.query(func.count(SMAQuarterlyReport.id)).filter(
            SMAQuarterlyReport.tenant_id == self.tenant_id,
            SMAQuarterlyReport.reporting_quarter == quarter
        ).scalar() or 0
        return f"SMA{quarter}{count + 1:03d}"

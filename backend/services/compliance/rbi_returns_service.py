"""
RBI Returns Automation Service
NBS-7, Statutory Returns, XBRL Generation, Compliance Calendar
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Dict, Any, Optional, List, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from backend.shared.database.compliance_models import (
    RBIReturnMaster, NBS7Return, StatutoryReturn, XBRLDocument,
    ComplianceCalendar, ReturnSubmissionHistory,
    RBIReturnType, XBRLTaxonomy, SubmissionStatus, ComplianceEventType
)
from backend.shared.database.loan_models import LoanAccount, LoanEMISchedule
from backend.shared.database.deposit_models import DepositAccount
from backend.shared.database.accounting_models import GeneralLedger, ChartOfAccounts
from backend.shared.common.response import CustomException
from .schemas import (
    NBS7ReturnCreate, NBS7ReturnUpdate, NBS7ReturnGenerateRequest,
    StatutoryReturnCreate, StatutoryReturnUpdate,
    XBRLDocumentCreate, XBRLGenerateRequest,
    ComplianceCalendarCreate, ComplianceCalendarUpdate
)


class RBIReturnsService:
    """Service for RBI Returns Management"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # RBI RETURN MASTER MANAGEMENT
    # ========================================================================
    
    def get_return_masters(
        self,
        return_type: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[RBIReturnMaster]:
        """Get list of RBI return masters"""
        query = self.db.query(RBIReturnMaster).filter(
            RBIReturnMaster.tenant_id == self.tenant_id
        )
        
        if return_type:
            query = query.filter(RBIReturnMaster.return_type == return_type)
        
        if is_active is not None:
            query = query.filter(RBIReturnMaster.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def create_return_master(self, data: Dict[str, Any]) -> RBIReturnMaster:
        """Create RBI return master configuration"""
        master = RBIReturnMaster(
            tenant_id=self.tenant_id,
            **data
        )
        self.db.add(master)
        self.db.commit()
        self.db.refresh(master)
        return master
    
    # ========================================================================
    # NBS-7 RETURN MANAGEMENT
    # ========================================================================
    
    def generate_nbs7_return(
        self,
        request: NBS7ReturnGenerateRequest
    ) -> NBS7Return:
        """Auto-generate NBS-7 return from system data"""
        
        # Generate return number
        return_number = self._generate_return_number("NBS7", request.reporting_period)
        
        # Calculate due date
        due_date = self._calculate_due_date(
            request.period_end_date,
            days_after=30  # NBS-7 typically due 30 days after period end
        )
        
        # Fetch financial data from system
        financial_data = self._fetch_financial_data(
            request.period_start_date,
            request.period_end_date,
            request.as_on_date
        )
        
        # Create NBS7 return
        nbs7_return = NBS7Return(
            tenant_id=self.tenant_id,
            return_number=return_number,
            reporting_period=request.reporting_period,
            period_start_date=request.period_start_date,
            period_end_date=request.period_end_date,
            as_on_date=request.as_on_date,
            financial_year=request.financial_year,
            quarter=request.quarter,
            due_date=due_date,
            status=SubmissionStatus.DRAFT,
            prepared_by=self.user_id,
            prepared_date=datetime.utcnow(),
            remarks=request.remarks,
            **financial_data
        )
        
        # Calculate derived fields
        self._calculate_nbs7_totals(nbs7_return)
        
        self.db.add(nbs7_return)
        self.db.commit()
        self.db.refresh(nbs7_return)
        
        # Create audit trail
        self._create_submission_history(
            return_type="nbs7",
            nbs7_return_id=nbs7_return.id,
            action="created",
            new_status=SubmissionStatus.DRAFT.value
        )
        
        return nbs7_return
    
    def _fetch_financial_data(
        self,
        start_date: date,
        end_date: date,
        as_on_date: date
    ) -> Dict[str, Decimal]:
        """Fetch financial data from accounting system"""
        
        data = {}
        
        # LOANS & ADVANCES - Fetch from LoanAccount
        loans_query = self.db.query(
            func.sum(LoanAccount.sanctioned_amount).label('total_loans'),
            func.sum(LoanAccount.outstanding_principal).label('outstanding')
        ).filter(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False,
                LoanAccount.disbursement_date <= as_on_date
            )
        ).first()
        
        data['term_loans'] = loans_query.outstanding or Decimal('0')
        data['total_loans'] = loans_query.outstanding or Decimal('0')
        
        # NPA CALCULATION - Loans overdue > 90 days
        npa_query = self.db.query(
            func.sum(LoanAccount.outstanding_principal).label('gross_npa')
        ).filter(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False,
                LoanAccount.days_past_due > 90
            )
        ).first()
        
        data['gross_npa'] = npa_query.gross_npa or Decimal('0')
        
        # PROVISIONS - Standard 0.25%, NPA provisions
        data['provision_standard_assets'] = data['total_loans'] * Decimal('0.0025')
        data['provision_npa'] = data['gross_npa'] * Decimal('0.25')  # Simplified
        
        # DEPOSITS (if applicable)
        deposits_query = self.db.query(
            func.sum(DepositAccount.current_balance).label('total_deposits')
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active'
            )
        ).first()
        
        data['public_deposits'] = deposits_query.total_deposits or Decimal('0')
        
        # FETCH FROM GENERAL LEDGER
        # This is a simplified version - in production, map account codes properly
        gl_balances = self._fetch_gl_balances(as_on_date)
        
        # Assets
        data['cash_bank_balances'] = gl_balances.get('cash_bank', Decimal('0'))
        data['government_securities'] = gl_balances.get('govt_securities', Decimal('0'))
        data['corporate_bonds'] = gl_balances.get('corporate_bonds', Decimal('0'))
        data['fixed_assets_gross'] = gl_balances.get('fixed_assets', Decimal('0'))
        data['accumulated_depreciation'] = gl_balances.get('depreciation', Decimal('0'))
        data['other_assets'] = gl_balances.get('other_assets', Decimal('0'))
        
        # Liabilities
        data['share_capital'] = gl_balances.get('share_capital', Decimal('0'))
        data['reserves_surplus'] = gl_balances.get('reserves', Decimal('0'))
        data['bank_borrowings'] = gl_balances.get('bank_borrowings', Decimal('0'))
        data['debentures'] = gl_balances.get('debentures', Decimal('0'))
        data['other_liabilities'] = gl_balances.get('other_liabilities', Decimal('0'))
        
        # Income Statement (Period-based)
        income_data = self._fetch_income_statement(start_date, end_date)
        data.update(income_data)
        
        return data
    
    def _fetch_gl_balances(self, as_on_date: date) -> Dict[str, Decimal]:
        """Fetch general ledger balances"""
        balances = {}
        
        # Query GL for balances as on date
        # This is simplified - actual implementation would use proper account mappings
        gl_query = self.db.query(
            ChartOfAccounts.account_code,
            func.sum(GeneralLedger.debit_amount - GeneralLedger.credit_amount).label('balance')
        ).join(
            ChartOfAccounts,
            GeneralLedger.account_id == ChartOfAccounts.id
        ).filter(
            and_(
                GeneralLedger.tenant_id == self.tenant_id,
                GeneralLedger.transaction_date <= as_on_date
            )
        ).group_by(ChartOfAccounts.account_code).all()
        
        # Map account codes to categories (simplified mapping)
        account_mapping = {
            '1000': 'cash_bank',
            '1100': 'govt_securities',
            '1200': 'corporate_bonds',
            '1800': 'fixed_assets',
            '1850': 'depreciation',
            '1900': 'other_assets',
            '3000': 'share_capital',
            '3100': 'reserves',
            '4000': 'bank_borrowings',
            '4100': 'debentures',
            '4900': 'other_liabilities'
        }
        
        for gl_record in gl_query:
            category = account_mapping.get(gl_record.account_code[:4])
            if category:
                balances[category] = gl_record.balance or Decimal('0')
        
        return balances
    
    def _fetch_income_statement(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Decimal]:
        """Fetch income statement data for period"""
        data = {}
        
        # Query income and expense accounts from GL
        income_expense = self.db.query(
            ChartOfAccounts.account_type,
            func.sum(GeneralLedger.credit_amount - GeneralLedger.debit_amount).label('amount')
        ).join(
            ChartOfAccounts,
            GeneralLedger.account_id == ChartOfAccounts.id
        ).filter(
            and_(
                GeneralLedger.tenant_id == self.tenant_id,
                GeneralLedger.transaction_date >= start_date,
                GeneralLedger.transaction_date <= end_date,
                ChartOfAccounts.account_type.in_(['income', 'expense'])
            )
        ).group_by(ChartOfAccounts.account_type).all()
        
        for record in income_expense:
            if record.account_type == 'income':
                data['interest_income'] = record.amount or Decimal('0')
            elif record.account_type == 'expense':
                data['interest_expenditure'] = abs(record.amount or Decimal('0'))
        
        return data
    
    def _calculate_nbs7_totals(self, nbs7: NBS7Return):
        """Calculate all derived totals for NBS-7 return"""
        
        # Assets - Loans
        nbs7.total_loans = (
            nbs7.term_loans + nbs7.hire_purchase + nbs7.leasing +
            nbs7.bills_discounted + nbs7.other_loans
        )
        
        # Provisions
        nbs7.total_provisions = nbs7.provision_standard_assets + nbs7.provision_npa
        nbs7.net_loans_advances = nbs7.total_loans - nbs7.total_provisions
        
        # Investments
        nbs7.total_investments = (
            nbs7.government_securities + nbs7.corporate_bonds +
            nbs7.mutual_funds + nbs7.shares_equity + nbs7.other_investments
        )
        
        # Fixed Assets
        nbs7.fixed_assets_net = nbs7.fixed_assets_gross - nbs7.accumulated_depreciation
        
        # Total Assets
        nbs7.total_assets = (
            nbs7.net_loans_advances + nbs7.total_investments +
            nbs7.fixed_assets_net + nbs7.cash_bank_balances + nbs7.other_assets
        )
        
        # Liabilities - Capital & Reserves
        nbs7.total_capital_reserves = nbs7.share_capital + nbs7.reserves_surplus
        
        # Borrowings
        nbs7.total_borrowings = (
            nbs7.bank_borrowings + nbs7.debentures + nbs7.commercial_paper +
            nbs7.subordinated_debt + nbs7.other_borrowings
        )
        
        # Total Liabilities
        nbs7.total_liabilities = (
            nbs7.total_capital_reserves + nbs7.total_borrowings +
            nbs7.public_deposits + nbs7.other_liabilities + nbs7.provisions_liabilities
        )
        
        # Income Statement
        nbs7.total_income = nbs7.interest_income + nbs7.other_income
        nbs7.total_expenditure = (
            nbs7.interest_expenditure + nbs7.operating_expenses + nbs7.provisions_write_offs
        )
        nbs7.profit_before_tax = nbs7.total_income - nbs7.total_expenditure
        nbs7.profit_after_tax = nbs7.profit_before_tax - nbs7.tax_provision
        
        # NPA Ratio
        if nbs7.total_loans > 0:
            nbs7.npa_ratio = (nbs7.gross_npa / nbs7.total_loans) * Decimal('100')
        else:
            nbs7.npa_ratio = Decimal('0')
        
        nbs7.net_npa = nbs7.gross_npa - nbs7.provision_npa
        
        # CRAR Calculation
        nbs7.total_capital = nbs7.tier1_capital + nbs7.tier2_capital
        if nbs7.risk_weighted_assets > 0:
            nbs7.crar_percentage = (nbs7.total_capital / nbs7.risk_weighted_assets) * Decimal('100')
        else:
            nbs7.crar_percentage = Decimal('0')
    
    def get_nbs7_return(self, return_id: UUID) -> Optional[NBS7Return]:
        """Get NBS-7 return by ID"""
        return self.db.query(NBS7Return).filter(
            and_(
                NBS7Return.id == return_id,
                NBS7Return.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_nbs7_returns(
        self,
        financial_year: Optional[str] = None,
        quarter: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[NBS7Return]:
        """List NBS-7 returns with filters"""
        query = self.db.query(NBS7Return).filter(
            NBS7Return.tenant_id == self.tenant_id
        )
        
        if financial_year:
            query = query.filter(NBS7Return.financial_year == financial_year)
        
        if quarter:
            query = query.filter(NBS7Return.quarter == quarter)
        
        if status:
            query = query.filter(NBS7Return.status == status)
        
        return query.order_by(desc(NBS7Return.created_at)).offset(skip).limit(limit).all()
    
    def update_nbs7_return(
        self,
        return_id: UUID,
        data: NBS7ReturnUpdate
    ) -> Optional[NBS7Return]:
        """Update NBS-7 return"""
        nbs7 = self.get_nbs7_return(return_id)
        
        if not nbs7:
            return None
        
        # Only allow updates for DRAFT status
        if nbs7.status != SubmissionStatus.DRAFT:
            raise CustomException(
                message="Can only update draft returns",
                error_code="INVALID_STATUS"
            )
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nbs7, field, value)
        
        # Recalculate totals
        self._calculate_nbs7_totals(nbs7)
        
        nbs7.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(nbs7)
        
        return nbs7
    
    def approve_nbs7_return(self, return_id: UUID) -> Optional[NBS7Return]:
        """Approve NBS-7 return"""
        nbs7 = self.get_nbs7_return(return_id)
        
        if not nbs7:
            return None
        
        if nbs7.status not in [SubmissionStatus.DRAFT, SubmissionStatus.PENDING_REVIEW]:
            raise CustomException(
                message="Return cannot be approved in current status",
                error_code="INVALID_STATUS"
            )
        
        nbs7.status = SubmissionStatus.APPROVED
        nbs7.approved_by = self.user_id
        nbs7.approved_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(nbs7)
        
        # Create audit trail
        self._create_submission_history(
            return_type="nbs7",
            nbs7_return_id=nbs7.id,
            action="approved",
            previous_status=SubmissionStatus.DRAFT.value,
            new_status=SubmissionStatus.APPROVED.value
        )
        
        return nbs7
    
    def submit_nbs7_return(
        self,
        return_id: UUID,
        submission_reference: str
    ) -> Optional[NBS7Return]:
        """Submit NBS-7 return to RBI"""
        nbs7 = self.get_nbs7_return(return_id)
        
        if not nbs7:
            return None
        
        if nbs7.status != SubmissionStatus.APPROVED:
            raise CustomException(
                message="Return must be approved before submission",
                error_code="NOT_APPROVED"
            )
        
        nbs7.status = SubmissionStatus.SUBMITTED
        nbs7.submitted_date = datetime.utcnow()
        nbs7.submission_reference = submission_reference
        
        # Check if overdue
        if nbs7.submitted_date.date() > nbs7.due_date:
            nbs7.is_overdue = True
            nbs7.days_overdue = (nbs7.submitted_date.date() - nbs7.due_date).days
        
        self.db.commit()
        self.db.refresh(nbs7)
        
        # Create audit trail
        self._create_submission_history(
            return_type="nbs7",
            nbs7_return_id=nbs7.id,
            action="submitted",
            previous_status=SubmissionStatus.APPROVED.value,
            new_status=SubmissionStatus.SUBMITTED.value,
            comments=f"Submission Reference: {submission_reference}"
        )
        
        return nbs7
    
    # ========================================================================
    # STATUTORY RETURNS MANAGEMENT
    # ========================================================================
    
    def create_statutory_return(
        self,
        data: StatutoryReturnCreate
    ) -> StatutoryReturn:
        """Create statutory return"""
        
        return_number = self._generate_return_number(
            data.return_type,
            data.reporting_period
        )
        
        # Get return master for due date calculation
        return_master = self.db.query(RBIReturnMaster).filter(
            RBIReturnMaster.id == data.return_master_id
        ).first()
        
        due_date = self._calculate_due_date(
            data.period_end_date,
            days_after=return_master.due_days_after_period if return_master else 30
        )
        
        statutory_return = StatutoryReturn(
            tenant_id=self.tenant_id,
            return_number=return_number,
            return_master_id=data.return_master_id,
            return_type=data.return_type,
            reporting_period=data.reporting_period,
            period_start_date=data.period_start_date,
            period_end_date=data.period_end_date,
            as_on_date=data.as_on_date,
            financial_year=data.financial_year,
            return_data=data.return_data,
            schedules=data.schedules,
            summary_data=data.summary_data,
            due_date=due_date,
            status=SubmissionStatus.DRAFT,
            prepared_by=self.user_id,
            prepared_date=datetime.utcnow(),
            remarks=data.remarks,
            internal_notes=data.internal_notes
        )
        
        self.db.add(statutory_return)
        self.db.commit()
        self.db.refresh(statutory_return)
        
        # Create audit trail
        self._create_submission_history(
            return_type=data.return_type,
            statutory_return_id=statutory_return.id,
            action="created",
            new_status=SubmissionStatus.DRAFT.value
        )
        
        return statutory_return
    
    def get_statutory_return(self, return_id: UUID) -> Optional[StatutoryReturn]:
        """Get statutory return by ID"""
        return self.db.query(StatutoryReturn).filter(
            and_(
                StatutoryReturn.id == return_id,
                StatutoryReturn.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_statutory_returns(
        self,
        return_type: Optional[str] = None,
        financial_year: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[StatutoryReturn]:
        """List statutory returns with filters"""
        query = self.db.query(StatutoryReturn).filter(
            StatutoryReturn.tenant_id == self.tenant_id
        )
        
        if return_type:
            query = query.filter(StatutoryReturn.return_type == return_type)
        
        if financial_year:
            query = query.filter(StatutoryReturn.financial_year == financial_year)
        
        if status:
            query = query.filter(StatutoryReturn.status == status)
        
        return query.order_by(desc(StatutoryReturn.created_at)).offset(skip).limit(limit).all()
    
    def validate_statutory_return(self, return_id: UUID) -> Dict[str, Any]:
        """Validate statutory return data"""
        statutory_return = self.get_statutory_return(return_id)
        
        if not statutory_return:
            raise CustomException(message="Return not found", error_code="NOT_FOUND")
        
        errors = []
        warnings = []
        
        # Get validation rules from return master
        return_master = self.db.query(RBIReturnMaster).filter(
            RBIReturnMaster.id == statutory_return.return_master_id
        ).first()
        
        if return_master and return_master.validation_rules:
            # Apply validation rules
            rules = return_master.validation_rules
            return_data = statutory_return.return_data
            
            # Example validations (customize based on rules)
            for field, rule in rules.items():
                if rule.get('required') and field not in return_data:
                    errors.append({
                        'field': field,
                        'message': f'{field} is required'
                    })
                
                if field in return_data:
                    value = return_data[field]
                    
                    # Min/max validation
                    if 'min' in rule and value < rule['min']:
                        errors.append({
                            'field': field,
                            'message': f'{field} must be >= {rule["min"]}'
                        })
                    
                    if 'max' in rule and value > rule['max']:
                        warnings.append({
                            'field': field,
                            'message': f'{field} exceeds maximum of {rule["max"]}'
                        })
        
        # Update validation status
        statutory_return.validation_status = 'passed' if len(errors) == 0 else 'failed'
        statutory_return.validation_errors = errors
        statutory_return.validation_warnings = warnings
        
        self.db.commit()
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    # ========================================================================
    # XBRL DOCUMENT GENERATION
    # ========================================================================
    
    def generate_xbrl_document(
        self,
        request: XBRLGenerateRequest
    ) -> XBRLDocument:
        """Generate XBRL document from return data"""
        
        # Fetch return data
        if request.return_type in ['nbs_7_monthly', 'nbs_7_quarterly']:
            source_return = self.get_nbs7_return(request.return_id)
            nbs7_return_id = request.return_id
            statutory_return_id = None
        else:
            source_return = self.get_statutory_return(request.return_id)
            nbs7_return_id = None
            statutory_return_id = request.return_id
        
        if not source_return:
            raise CustomException(message="Source return not found", error_code="NOT_FOUND")
        
        # Generate XBRL content
        xbrl_content = self._generate_xbrl_content(
            source_return,
            request.taxonomy_version,
            request.entity_identifier,
            request.entity_name
        )
        
        # Generate document number
        document_number = f"XBRL-{request.return_type.upper()}-{source_return.reporting_period}"
        
        # Create XBRL document
        xbrl_doc = XBRLDocument(
            tenant_id=self.tenant_id,
            document_number=document_number,
            document_name=f"XBRL Document - {source_return.reporting_period}",
            return_type=request.return_type,
            nbs7_return_id=nbs7_return_id,
            statutory_return_id=statutory_return_id,
            taxonomy_version=request.taxonomy_version,
            reporting_period=source_return.reporting_period,
            period_start_date=source_return.period_start_date,
            period_end_date=source_return.period_end_date,
            xbrl_content=xbrl_content,
            entity_identifier=request.entity_identifier,
            entity_name=request.entity_name,
            status='draft',
            generated_by=self.user_id,
            generated_date=datetime.utcnow()
        )
        
        # Validate if requested
        if request.include_validation:
            validation_result = self._validate_xbrl(xbrl_content)
            xbrl_doc.is_valid = validation_result['is_valid']
            xbrl_doc.validation_errors = validation_result['errors']
            xbrl_doc.validation_date = datetime.utcnow()
            xbrl_doc.status = 'validated' if validation_result['is_valid'] else 'draft'
        
        self.db.add(xbrl_doc)
        self.db.commit()
        self.db.refresh(xbrl_doc)
        
        return xbrl_doc
    
    def _generate_xbrl_content(
        self,
        return_data: Any,
        taxonomy: str,
        entity_id: str,
        entity_name: str
    ) -> str:
        """Generate XBRL XML content"""
        
        # Create XBRL root element
        root = ET.Element('xbrl', {
            'xmlns': 'http://www.xbrl.org/2003/instance',
            'xmlns:xbrli': 'http://www.xbrl.org/2003/instance',
            'xmlns:rbi': f'http://www.rbi.org.in/taxonomy/{taxonomy}'
        })
        
        # Add context
        context = ET.SubElement(root, 'context', {'id': 'current'})
        entity = ET.SubElement(context, 'entity')
        identifier = ET.SubElement(entity, 'identifier', {
            'scheme': 'http://www.rbi.org.in'
        })
        identifier.text = entity_id
        
        period = ET.SubElement(context, 'period')
        start_date = ET.SubElement(period, 'startDate')
        start_date.text = return_data.period_start_date.isoformat()
        end_date = ET.SubElement(period, 'endDate')
        end_date.text = return_data.period_end_date.isoformat()
        
        # Add unit for monetary values
        unit = ET.SubElement(root, 'unit', {'id': 'INR'})
        measure = ET.SubElement(unit, 'measure')
        measure.text = 'iso4217:INR'
        
        # Add facts from return data
        if isinstance(return_data, NBS7Return):
            self._add_nbs7_facts(root, return_data)
        elif isinstance(return_data, StatutoryReturn):
            self._add_statutory_facts(root, return_data)
        
        # Convert to pretty XML string
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    def _add_nbs7_facts(self, root: ET.Element, nbs7: NBS7Return):
        """Add NBS-7 specific facts to XBRL"""
        
        facts = {
            'TotalLoans': str(nbs7.total_loans),
            'TotalProvisions': str(nbs7.total_provisions),
            'NetLoansAdvances': str(nbs7.net_loans_advances),
            'TotalInvestments': str(nbs7.total_investments),
            'TotalAssets': str(nbs7.total_assets),
            'ShareCapital': str(nbs7.share_capital),
            'ReservesSurplus': str(nbs7.reserves_surplus),
            'TotalBorrowings': str(nbs7.total_borrowings),
            'PublicDeposits': str(nbs7.public_deposits),
            'TotalLiabilities': str(nbs7.total_liabilities),
            'GrossNPA': str(nbs7.gross_npa),
            'NetNPA': str(nbs7.net_npa),
            'NPARatio': str(nbs7.npa_ratio),
            'CRAR': str(nbs7.crar_percentage),
            'ProfitAfterTax': str(nbs7.profit_after_tax)
        }
        
        for fact_name, fact_value in facts.items():
            fact = ET.SubElement(root, f'rbi:{fact_name}', {
                'contextRef': 'current',
                'unitRef': 'INR',
                'decimals': '2'
            })
            fact.text = fact_value
    
    def _add_statutory_facts(self, root: ET.Element, statutory: StatutoryReturn):
        """Add statutory return facts to XBRL"""
        
        # Add facts from return_data JSON
        for key, value in statutory.return_data.items():
            fact = ET.SubElement(root, f'rbi:{key}', {
                'contextRef': 'current',
                'unitRef': 'INR' if isinstance(value, (int, float)) else None
            })
            fact.text = str(value)
    
    def _validate_xbrl(self, xbrl_content: str) -> Dict[str, Any]:
        """Validate XBRL document"""
        
        errors = []
        warnings = []
        
        try:
            # Parse XML
            ET.fromstring(xbrl_content)
            
            # Basic validation checks
            if '<xbrl' not in xbrl_content:
                errors.append({'message': 'Invalid XBRL root element'})
            
            if '<context' not in xbrl_content:
                errors.append({'message': 'Missing context element'})
            
            if '<unit' not in xbrl_content:
                warnings.append({'message': 'Missing unit definition'})
            
        except ET.ParseError as e:
            errors.append({'message': f'XML parsing error: {str(e)}'})
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_xbrl_document(self, document_id: UUID) -> Optional[XBRLDocument]:
        """Get XBRL document by ID"""
        return self.db.query(XBRLDocument).filter(
            and_(
                XBRLDocument.id == document_id,
                XBRLDocument.tenant_id == self.tenant_id
            )
        ).first()
    
    # ========================================================================
    # COMPLIANCE CALENDAR MANAGEMENT
    # ========================================================================
    
    def create_calendar_event(
        self,
        data: ComplianceCalendarCreate
    ) -> ComplianceCalendar:
        """Create compliance calendar event"""
        
        event = ComplianceCalendar(
            tenant_id=self.tenant_id,
            event_code=data.event_code,
            event_title=data.event_title,
            event_type=data.event_type,
            description=data.description,
            requirements=data.requirements,
            event_date=data.event_date,
            event_time=data.event_time,
            due_date=data.due_date or data.event_date,
            priority=data.priority,
            category=data.category,
            return_master_id=data.return_master_id,
            nbs7_return_id=data.nbs7_return_id,
            statutory_return_id=data.statutory_return_id,
            is_recurring=data.is_recurring,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_day=data.recurrence_day,
            assigned_to=data.assigned_to,
            assigned_by=self.user_id,
            assigned_date=datetime.utcnow() if data.assigned_to else None,
            reminder_enabled=data.reminder_enabled,
            reminder_days_before=data.reminder_days_before,
            notes=data.notes,
            status='pending'
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def get_calendar_event(self, event_id: UUID) -> Optional[ComplianceCalendar]:
        """Get calendar event by ID"""
        return self.db.query(ComplianceCalendar).filter(
            and_(
                ComplianceCalendar.id == event_id,
                ComplianceCalendar.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_calendar_events(
        self,
        event_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        assigned_to: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceCalendar]:
        """List calendar events with filters"""
        query = self.db.query(ComplianceCalendar).filter(
            ComplianceCalendar.tenant_id == self.tenant_id
        )
        
        if event_type:
            query = query.filter(ComplianceCalendar.event_type == event_type)
        
        if priority:
            query = query.filter(ComplianceCalendar.priority == priority)
        
        if status:
            query = query.filter(ComplianceCalendar.status == status)
        
        if from_date:
            query = query.filter(ComplianceCalendar.event_date >= from_date)
        
        if to_date:
            query = query.filter(ComplianceCalendar.event_date <= to_date)
        
        if assigned_to:
            query = query.filter(ComplianceCalendar.assigned_to == assigned_to)
        
        return query.order_by(ComplianceCalendar.event_date).offset(skip).limit(limit).all()
    
    def update_calendar_event(
        self,
        event_id: UUID,
        data: ComplianceCalendarUpdate
    ) -> Optional[ComplianceCalendar]:
        """Update calendar event"""
        event = self.get_calendar_event(event_id)
        
        if not event:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        event.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def complete_calendar_event(
        self,
        event_id: UUID,
        completion_notes: Optional[str] = None,
        actual_effort_hours: Optional[Decimal] = None
    ) -> Optional[ComplianceCalendar]:
        """Mark calendar event as completed"""
        event = self.get_calendar_event(event_id)
        
        if not event:
            return None
        
        event.status = 'completed'
        event.completion_date = datetime.utcnow()
        event.completed_by = self.user_id
        event.actual_effort_hours = actual_effort_hours
        
        if completion_notes:
            event.internal_comments = (
                f"{event.internal_comments or ''}\n\nCompletion Notes: {completion_notes}"
            )
        
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def get_upcoming_deadlines(
        self,
        days_ahead: int = 30,
        limit: int = 10
    ) -> List[ComplianceCalendar]:
        """Get upcoming compliance deadlines"""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        return self.db.query(ComplianceCalendar).filter(
            and_(
                ComplianceCalendar.tenant_id == self.tenant_id,
                ComplianceCalendar.due_date >= today,
                ComplianceCalendar.due_date <= end_date,
                ComplianceCalendar.status.in_(['pending', 'in_progress'])
            )
        ).order_by(ComplianceCalendar.due_date).limit(limit).all()
    
    # ========================================================================
    # DASHBOARD & ANALYTICS
    # ========================================================================
    
    def get_returns_dashboard_stats(self) -> Dict[str, Any]:
        """Get RBI returns dashboard statistics"""
        
        today = date.today()
        
        # Count returns by status
        nbs7_stats = self.db.query(
            NBS7Return.status,
            func.count(NBS7Return.id).label('count')
        ).filter(
            NBS7Return.tenant_id == self.tenant_id
        ).group_by(NBS7Return.status).all()
        
        statutory_stats = self.db.query(
            StatutoryReturn.status,
            func.count(StatutoryReturn.id).label('count')
        ).filter(
            StatutoryReturn.tenant_id == self.tenant_id
        ).group_by(StatutoryReturn.status).all()
        
        # Overdue returns
        overdue_nbs7 = self.db.query(func.count(NBS7Return.id)).filter(
            and_(
                NBS7Return.tenant_id == self.tenant_id,
                NBS7Return.due_date < today,
                NBS7Return.status != SubmissionStatus.SUBMITTED
            )
        ).scalar() or 0
        
        overdue_statutory = self.db.query(func.count(StatutoryReturn.id)).filter(
            and_(
                StatutoryReturn.tenant_id == self.tenant_id,
                StatutoryReturn.due_date < today,
                StatutoryReturn.status != SubmissionStatus.SUBMITTED
            )
        ).scalar() or 0
        
        # Returns due in next 30 days
        due_soon = self.db.query(
            func.count(NBS7Return.id)
        ).filter(
            and_(
                NBS7Return.tenant_id == self.tenant_id,
                NBS7Return.due_date >= today,
                NBS7Return.due_date <= today + timedelta(days=30),
                NBS7Return.status != SubmissionStatus.SUBMITTED
            )
        ).scalar() or 0
        
        # Upcoming deadlines
        upcoming = self.get_upcoming_deadlines(days_ahead=30, limit=5)
        
        # Recent submissions
        recent = self.db.query(NBS7Return).filter(
            and_(
                NBS7Return.tenant_id == self.tenant_id,
                NBS7Return.status == SubmissionStatus.SUBMITTED
            )
        ).order_by(desc(NBS7Return.submitted_date)).limit(5).all()
        
        # On-time submission rate
        total_submitted = self.db.query(func.count(NBS7Return.id)).filter(
            and_(
                NBS7Return.tenant_id == self.tenant_id,
                NBS7Return.status == SubmissionStatus.SUBMITTED
            )
        ).scalar() or 0
        
        on_time_submitted = self.db.query(func.count(NBS7Return.id)).filter(
            and_(
                NBS7Return.tenant_id == self.tenant_id,
                NBS7Return.status == SubmissionStatus.SUBMITTED,
                NBS7Return.is_overdue == False
            )
        ).scalar() or 0
        
        on_time_rate = (on_time_submitted / total_submitted * 100) if total_submitted > 0 else 100.0
        
        return {
            'total_returns_due': due_soon,
            'overdue_returns': overdue_nbs7 + overdue_statutory,
            'submitted_this_month': len([r for r in recent if r.submitted_date and r.submitted_date.month == today.month]),
            'pending_approval': sum(s.count for s in nbs7_stats if s.status == SubmissionStatus.PENDING_APPROVAL),
            'draft_returns': sum(s.count for s in nbs7_stats if s.status == SubmissionStatus.DRAFT),
            'nbs7_monthly_status': {s.status.value: s.count for s in nbs7_stats},
            'statutory_returns_status': {s.status.value: s.count for s in statutory_stats},
            'upcoming_deadlines': [
                {
                    'event_title': e.event_title,
                    'due_date': e.due_date.isoformat(),
                    'priority': e.priority,
                    'days_remaining': (e.due_date - today).days
                }
                for e in upcoming
            ],
            'recent_submissions': [
                {
                    'return_number': r.return_number,
                    'reporting_period': r.reporting_period,
                    'submitted_date': r.submitted_date.isoformat() if r.submitted_date else None,
                    'is_overdue': r.is_overdue
                }
                for r in recent
            ],
            'compliance_score': on_time_rate,
            'on_time_submission_rate': on_time_rate
        }
    
    def get_compliance_calendar_summary(self) -> Dict[str, Any]:
        """Get compliance calendar summary"""
        
        today = date.today()
        
        # Total events
        total = self.db.query(func.count(ComplianceCalendar.id)).filter(
            ComplianceCalendar.tenant_id == self.tenant_id
        ).scalar() or 0
        
        # Upcoming events (next 30 days)
        upcoming = self.db.query(func.count(ComplianceCalendar.id)).filter(
            and_(
                ComplianceCalendar.tenant_id == self.tenant_id,
                ComplianceCalendar.event_date >= today,
                ComplianceCalendar.event_date <= today + timedelta(days=30),
                ComplianceCalendar.status != 'completed'
            )
        ).scalar() or 0
        
        # Overdue events
        overdue = self.db.query(func.count(ComplianceCalendar.id)).filter(
            and_(
                ComplianceCalendar.tenant_id == self.tenant_id,
                ComplianceCalendar.due_date < today,
                ComplianceCalendar.status != 'completed'
            )
        ).scalar() or 0
        
        # Completed events
        completed = self.db.query(func.count(ComplianceCalendar.id)).filter(
            and_(
                ComplianceCalendar.tenant_id == self.tenant_id,
                ComplianceCalendar.status == 'completed'
            )
        ).scalar() or 0
        
        # By priority
        by_priority = self.db.query(
            ComplianceCalendar.priority,
            func.count(ComplianceCalendar.id).label('count')
        ).filter(
            ComplianceCalendar.tenant_id == self.tenant_id
        ).group_by(ComplianceCalendar.priority).all()
        
        # By status
        by_status = self.db.query(
            ComplianceCalendar.status,
            func.count(ComplianceCalendar.id).label('count')
        ).filter(
            ComplianceCalendar.tenant_id == self.tenant_id
        ).group_by(ComplianceCalendar.status).all()
        
        # Upcoming critical events
        critical = self.db.query(ComplianceCalendar).filter(
            and_(
                ComplianceCalendar.tenant_id == self.tenant_id,
                ComplianceCalendar.priority == 'critical',
                ComplianceCalendar.event_date >= today,
                ComplianceCalendar.status != 'completed'
            )
        ).order_by(ComplianceCalendar.event_date).limit(5).all()
        
        return {
            'total_events': total,
            'upcoming_events': upcoming,
            'overdue_events': overdue,
            'completed_events': completed,
            'events_this_month': upcoming,  # Simplified
            'events_this_quarter': upcoming,  # Simplified
            'by_priority': {p.priority: p.count for p in by_priority},
            'by_status': {s.status: s.count for s in by_status},
            'upcoming_critical': critical
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _generate_return_number(self, return_type: str, period: str) -> str:
        """Generate unique return number"""
        prefix = return_type.upper().replace('_', '')[:6]
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        return f"{prefix}-{period}-{timestamp}"
    
    def _calculate_due_date(self, period_end_date: date, days_after: int) -> date:
        """Calculate due date based on period end"""
        return period_end_date + timedelta(days=days_after)
    
    def _create_submission_history(
        self,
        return_type: str,
        action: str,
        new_status: str,
        nbs7_return_id: Optional[UUID] = None,
        statutory_return_id: Optional[UUID] = None,
        xbrl_document_id: Optional[UUID] = None,
        previous_status: Optional[str] = None,
        comments: Optional[str] = None
    ):
        """Create submission history record"""
        
        history = ReturnSubmissionHistory(
            tenant_id=self.tenant_id,
            return_type=return_type,
            nbs7_return_id=nbs7_return_id,
            statutory_return_id=statutory_return_id,
            xbrl_document_id=xbrl_document_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            action_by=self.user_id,
            action_date=datetime.utcnow(),
            comments=comments
        )
        
        self.db.add(history)
        self.db.commit()

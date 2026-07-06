"""
Certificate Service

Handles certificate generation including:
- Interest certificates
- TDS certificates (Form 16A)
- Certificate issuance tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from decimal import Decimal
import io

from backend.shared.database.deposit_models import (
    DepositAccount, DepositTransaction, DepositInterestCalculation, DepositProduct
)
from backend.shared.database.models import Customer
from backend.shared.common.response import CustomException


class CertificateService:
    """Service for generating certificates"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def generate_interest_certificate(
        self,
        account_id: int,
        financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate interest certificate data"""
        account = self._get_account(account_id)
        
        # Determine financial year
        if not financial_year:
            today = date.today()
            if today.month >= 4:
                financial_year = f"{today.year}-{today.year + 1}"
            else:
                financial_year = f"{today.year - 1}-{today.year}"
        
        # Parse FY
        fy_start_year, fy_end_year = map(int, financial_year.split('-'))
        period_start = date(fy_start_year, 4, 1)
        period_end = date(fy_end_year, 3, 31)
        
        # Get interest calculations
        calculations = self.db.query(DepositInterestCalculation).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.calculation_period_end >= period_start,
                DepositInterestCalculation.calculation_period_start <= period_end,
                DepositInterestCalculation.posted == True
            )
        ).order_by(DepositInterestCalculation.calculation_period_start).all()
        
        # Calculate totals
        total_interest = sum(calc.interest_amount for calc in calculations)
        total_tds = sum(calc.tds_amount for calc in calculations)
        net_interest = sum(calc.net_interest for calc in calculations)
        
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == account.customer_id
        ).first()
        
        # Get product
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == account.deposit_product_id
        ).first()
        
        # Format calculations
        calc_list = []
        for calc in calculations:
            calc_list.append({
                "period_start": calc.calculation_period_start.isoformat(),
                "period_end": calc.calculation_period_end.isoformat(),
                "days": calc.days_in_period,
                "rate": float(calc.interest_rate),
                "interest_amount": float(calc.interest_amount),
                "tds_amount": float(calc.tds_amount),
                "net_interest": float(calc.net_interest),
                "posted_date": calc.posted_date.isoformat() if calc.posted_date else None
            })
        
        return {
            "account": {
                "account_number": account.account_number,
                "account_type": account.account_type,
                "product_name": product.product_name if product else "Unknown",
                "opening_date": account.opening_date.isoformat()
            },
            "customer": {
                "name": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
                "pan": customer.pan if customer else None,
                "address": customer.address if customer else None
            },
            "financial_year": financial_year,
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "summary": {
                "total_interest": float(total_interest),
                "total_tds": float(total_tds),
                "net_interest": float(net_interest),
                "calculation_count": len(calculations)
            },
            "calculations": calc_list,
            "certificate_date": date.today().isoformat()
        }
    
    def generate_interest_certificate_pdf(
        self,
        account_id: int,
        financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate interest certificate PDF"""
        certificate = self.generate_interest_certificate(account_id, financial_year)
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=20,
                alignment=1
            )
            elements.append(Paragraph("INTEREST CERTIFICATE", title_style))
            elements.append(Paragraph(f"Financial Year: {certificate['financial_year']}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Account & Customer Info
            info_data = [
                ["Account Number:", certificate['account']['account_number']],
                ["Account Type:", certificate['account']['account_type'].upper()],
                ["Product:", certificate['account']['product_name']],
                ["Customer Name:", certificate['customer']['name']],
                ["PAN:", certificate['customer']['pan'] or "Not Available"],
                ["Period:", f"{certificate['period']['start']} to {certificate['period']['end']}"],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Summary
            summary_data = [
                ["Total Gross Interest:", f"₹{certificate['summary']['total_interest']:,.2f}"],
                ["Total TDS Deducted:", f"₹{certificate['summary']['total_tds']:,.2f}"],
                ["Net Interest Paid:", f"₹{certificate['summary']['net_interest']:,.2f}"],
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Calculation details
            if certificate['calculations']:
                calc_data = [['Period', 'Days', 'Rate %', 'Interest', 'TDS', 'Net']]
                
                for calc in certificate['calculations']:
                    calc_data.append([
                        f"{calc['period_start']}\nto {calc['period_end']}",
                        str(calc['days']),
                        f"{calc['rate']:.2f}%",
                        f"₹{calc['interest_amount']:,.2f}",
                        f"₹{calc['tds_amount']:,.2f}",
                        f"₹{calc['net_interest']:,.2f}"
                    ])
                
                calc_table = Table(calc_data, colWidths=[1.5*inch, 0.6*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                calc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
                ]))
                
                elements.append(Paragraph("Interest Calculation Details", styles['Heading2']))
                elements.append(Spacer(1, 0.1*inch))
                elements.append(calc_table)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph(
                f"Certificate Date: {certificate['certificate_date']}",
                styles['Normal']
            ))
            elements.append(Paragraph(
                "This is a computer-generated certificate and does not require a signature.",
                styles['Italic']
            ))
            
            doc.build(elements)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            filename = f"interest_certificate_{certificate['account']['account_number']}_{certificate['financial_year']}.pdf"
            
            return {
                "pdf_content": pdf_content,
                "filename": filename
            }
            
        except ImportError:
            raise CustomException(
                status_code=500,
                message="PDF generation library not available"
            )
    
    def generate_tds_certificate(
        self,
        account_id: int,
        financial_year: str,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate TDS certificate (Form 16A) data"""
        account = self._get_account(account_id)
        
        # Parse FY
        fy_start_year, fy_end_year = map(int, financial_year.split('-'))
        
        # Determine period
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
        
        # Get TDS transactions
        tds_transactions = self.db.query(DepositTransaction).filter(
            and_(
                DepositTransaction.deposit_account_id == account_id,
                DepositTransaction.transaction_type == 'interest_tds',
                DepositTransaction.transaction_date >= period_start,
                DepositTransaction.transaction_date <= period_end
            )
        ).all()
        
        # Get interest calculations with TDS
        calculations = self.db.query(DepositInterestCalculation).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.tds_applicable == True,
                DepositInterestCalculation.calculation_period_end >= period_start,
                DepositInterestCalculation.calculation_period_start <= period_end,
                DepositInterestCalculation.posted == True
            )
        ).all()
        
        total_interest = sum(calc.interest_amount for calc in calculations)
        total_tds = sum(calc.tds_amount for calc in calculations)
        
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == account.customer_id
        ).first()
        
        return {
            "form_type": "Form 16A",
            "financial_year": financial_year,
            "quarter": quarter,
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "deductor": {
                "name": "NBFC Company Name",  # TODO: Get from tenant config
                "tan": "TANXXXXXXX",  # TODO: Get from tenant config
                "pan": "PANXXXXXXX"   # TODO: Get from tenant config
            },
            "deductee": {
                "name": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
                "pan": customer.pan if customer else None,
                "address": customer.address if customer else None
            },
            "account_number": account.account_number,
            "gross_interest": float(total_interest),
            "tds_deducted": float(total_tds),
            "tds_rate": float(account.product.tds_rate if account.product else 10.0),
            "tds_transactions": [
                {
                    "date": txn.transaction_date.isoformat(),
                    "amount": float(txn.amount),
                    "reference": txn.reference_number
                }
                for txn in tds_transactions
            ],
            "certificate_date": date.today().isoformat()
        }
    
    def generate_tds_certificate_pdf(
        self,
        account_id: int,
        financial_year: str,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate TDS certificate PDF"""
        certificate = self.generate_tds_certificate(account_id, financial_year, quarter)
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=20,
                alignment=1
            )
            elements.append(Paragraph("TDS CERTIFICATE (Form 16A)", title_style))
            elements.append(Paragraph(
                f"Financial Year: {certificate['financial_year']}" + 
                (f" - Quarter {certificate['quarter']}" if certificate['quarter'] else ""),
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.3*inch))
            
            # Deductor & Deductee
            info_data = [
                ["DEDUCTOR INFORMATION", ""],
                ["Name:", certificate['deductor']['name']],
                ["TAN:", certificate['deductor']['tan']],
                ["PAN:", certificate['deductor']['pan']],
                ["", ""],
                ["DEDUCTEE INFORMATION", ""],
                ["Name:", certificate['deductee']['name']],
                ["PAN:", certificate['deductee']['pan'] or "Not Available"],
                ["Account Number:", certificate['account_number']],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#e2e8f0')),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # TDS Summary
            summary_data = [
                ["Gross Interest Income:", f"₹{certificate['gross_interest']:,.2f}"],
                ["TDS Rate:", f"{certificate['tds_rate']}%"],
                ["TDS Deducted:", f"₹{certificate['tds_deducted']:,.2f}"],
                ["Net Amount Paid:", f"₹{certificate['gross_interest'] - certificate['tds_deducted']:,.2f}"],
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(summary_table)
            
            doc.build(elements)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            quarter_str = f"_Q{certificate['quarter']}" if certificate['quarter'] else ""
            filename = f"tds_certificate_{certificate['account_number']}_{certificate['financial_year']}{quarter_str}.pdf"
            
            return {
                "pdf_content": pdf_content,
                "filename": filename
            }
            
        except ImportError:
            raise CustomException(
                status_code=500,
                message="PDF generation library not available"
            )
    
    def mark_certificate_issued(self, account_id: int) -> Dict[str, Any]:
        """Mark certificate as issued"""
        account = self._get_account(account_id)
        
        account.certificate_issued = True
        account.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(account)
        
        return {
            "account_number": account.account_number,
            "certificate_issued": True,
            "issued_date": datetime.utcnow().isoformat()
        }
    
    def get_interest_summary(
        self,
        account_id: int,
        financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get interest summary"""
        account = self._get_account(account_id)
        
        # Determine financial year
        if not financial_year:
            today = date.today()
            if today.month >= 4:
                financial_year = f"{today.year}-{today.year + 1}"
            else:
                financial_year = f"{today.year - 1}-{today.year}"
        
        # Parse FY
        fy_start_year, fy_end_year = map(int, financial_year.split('-'))
        period_start = date(fy_start_year, 4, 1)
        period_end = date(fy_end_year, 3, 31)
        
        # Get summary from calculations
        calculations = self.db.query(
            func.sum(DepositInterestCalculation.interest_amount).label('total_interest'),
            func.sum(DepositInterestCalculation.tds_amount).label('total_tds'),
            func.sum(DepositInterestCalculation.net_interest).label('net_interest'),
            func.count(DepositInterestCalculation.id).label('count')
        ).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.calculation_period_end >= period_start,
                DepositInterestCalculation.calculation_period_start <= period_end,
                DepositInterestCalculation.posted == True
            )
        ).first()
        
        return {
            "account_number": account.account_number,
            "financial_year": financial_year,
            "total_interest": float(calculations.total_interest or 0),
            "total_tds": float(calculations.total_tds or 0),
            "net_interest": float(calculations.net_interest or 0),
            "calculation_count": calculations.count or 0,
            "certificate_issued": account.certificate_issued
        }
    
    def _get_account(self, account_id: int) -> DepositAccount:
        """Get and verify account"""
        account = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.id == account_id,
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).first()
        
        if not account:
            raise CustomException(status_code=404, message="Account not found")
        
        return account

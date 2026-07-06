"""
Passbook Service

Handles all business logic for passbook operations including:
- Viewing passbook entries
- Marking entries as printed
- PDF generation
- Passbook issuance
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import io

from backend.shared.database.deposit_models import (
    DepositAccount, DepositPassbookEntry, DepositProduct
)
from backend.shared.common.response import CustomException


class PassbookService:
    """Service for managing passbook operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def get_passbook_entries(
        self,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        unprinted_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get passbook entries with filtering"""
        # Verify account
        account = self._get_account(account_id)
        
        # Build query
        query = self.db.query(DepositPassbookEntry).filter(
            and_(
                DepositPassbookEntry.tenant_id == self.tenant_id,
                DepositPassbookEntry.deposit_account_id == account_id
            )
        )
        
        # Apply filters
        if from_date:
            query = query.filter(DepositPassbookEntry.entry_date >= from_date)
        
        if to_date:
            query = query.filter(DepositPassbookEntry.entry_date <= to_date)
        
        if unprinted_only:
            query = query.filter(DepositPassbookEntry.printed == False)
        
        # Get total count
        total_count = query.count()
        
        # Get entries
        entries = query.order_by(
            DepositPassbookEntry.entry_date.asc(),
            DepositPassbookEntry.id.asc()
        ).offset(skip).limit(limit).all()
        
        # Format entries
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "id": entry.id,
                "entry_date": entry.entry_date.isoformat(),
                "particulars": entry.particulars,
                "withdrawal_amount": float(entry.withdrawal_amount or 0),
                "deposit_amount": float(entry.deposit_amount or 0),
                "balance": float(entry.balance),
                "printed": entry.printed,
                "print_date": entry.print_date.isoformat() if entry.print_date else None
            })
        
        # Get customer info
        from backend.shared.database.models import Customer
        customer = self.db.query(Customer).filter(
            Customer.id == account.customer_id
        ).first()
        
        return {
            "account_number": account.account_number,
            "account_type": account.account_type,
            "customer_name": f"{customer.first_name} {customer.last_name}" if customer else "Unknown",
            "entries": formatted_entries,
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    def mark_entries_as_printed(
        self,
        account_id: int,
        entry_ids: List[int]
    ) -> Dict[str, Any]:
        """Mark entries as printed"""
        # Verify account
        account = self._get_account(account_id)
        
        # Update entries
        now = datetime.utcnow()
        marked_count = 0
        
        for entry_id in entry_ids:
            entry = self.db.query(DepositPassbookEntry).filter(
                and_(
                    DepositPassbookEntry.id == entry_id,
                    DepositPassbookEntry.tenant_id == self.tenant_id,
                    DepositPassbookEntry.deposit_account_id == account_id
                )
            ).first()
            
            if entry and not entry.printed:
                entry.printed = True
                entry.print_date = now
                marked_count += 1
        
        self.db.commit()
        
        return {
            "marked_count": marked_count,
            "print_date": now.isoformat()
        }
    
    def generate_passbook_pdf(
        self,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        unprinted_only: bool = False
    ) -> Dict[str, Any]:
        """Generate passbook PDF"""
        # Get entries
        entries_data = self.get_passbook_entries(
            account_id=account_id,
            from_date=from_date,
            to_date=to_date,
            unprinted_only=unprinted_only,
            skip=0,
            limit=10000  # Large limit for PDF generation
        )
        
        # Generate PDF using reportlab
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            elements.append(Paragraph("PASSBOOK", title_style))
            
            # Account details
            account_info = [
                ["Account Number:", entries_data['account_number']],
                ["Account Type:", entries_data['account_type'].upper()],
                ["Customer Name:", entries_data['customer_name']],
            ]
            
            if from_date:
                account_info.append(["From Date:", from_date.isoformat()])
            if to_date:
                account_info.append(["To Date:", to_date.isoformat()])
            
            info_table = Table(account_info, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Transactions table
            table_data = [['Date', 'Particulars', 'Withdrawal', 'Deposit', 'Balance']]
            
            for entry in entries_data['entries']:
                table_data.append([
                    entry['entry_date'],
                    entry['particulars'][:40],  # Truncate long text
                    f"₹{entry['withdrawal_amount']:,.2f}" if entry['withdrawal_amount'] > 0 else "-",
                    f"₹{entry['deposit_amount']:,.2f}" if entry['deposit_amount'] > 0 else "-",
                    f"₹{entry['balance']:,.2f}"
                ])
            
            transactions_table = Table(
                table_data,
                colWidths=[1*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1.3*inch]
            )
            
            transactions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
            ]))
            
            elements.append(transactions_table)
            
            # Build PDF
            doc.build(elements)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            filename = f"passbook_{entries_data['account_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return {
                "pdf_content": pdf_content,
                "filename": filename,
                "entry_count": len(entries_data['entries'])
            }
            
        except ImportError:
            raise CustomException(
                status_code=500,
                message="PDF generation library not available. Please install reportlab."
            )
    
    def get_passbook_summary(self, account_id: int) -> Dict[str, Any]:
        """Get passbook summary statistics"""
        account = self._get_account(account_id)
        
        # Get counts
        total_entries = self.db.query(func.count(DepositPassbookEntry.id)).filter(
            and_(
                DepositPassbookEntry.tenant_id == self.tenant_id,
                DepositPassbookEntry.deposit_account_id == account_id
            )
        ).scalar()
        
        printed_entries = self.db.query(func.count(DepositPassbookEntry.id)).filter(
            and_(
                DepositPassbookEntry.tenant_id == self.tenant_id,
                DepositPassbookEntry.deposit_account_id == account_id,
                DepositPassbookEntry.printed == True
            )
        ).scalar()
        
        # Get last print date
        last_printed = self.db.query(DepositPassbookEntry).filter(
            and_(
                DepositPassbookEntry.tenant_id == self.tenant_id,
                DepositPassbookEntry.deposit_account_id == account_id,
                DepositPassbookEntry.printed == True
            )
        ).order_by(DepositPassbookEntry.print_date.desc()).first()
        
        return {
            "account_number": account.account_number,
            "passbook_issued": account.passbook_issued,
            "total_entries": total_entries or 0,
            "printed_entries": printed_entries or 0,
            "unprinted_entries": (total_entries or 0) - (printed_entries or 0),
            "last_print_date": last_printed.print_date.isoformat() if last_printed else None
        }
    
    def issue_passbook(self, account_id: int) -> Dict[str, Any]:
        """Issue passbook to customer"""
        account = self._get_account(account_id)
        
        if account.passbook_issued:
            raise CustomException(
                status_code=400,
                message="Passbook already issued for this account"
            )
        
        account.passbook_issued = True
        account.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(account)
        
        return {
            "account_number": account.account_number,
            "passbook_issued": True,
            "issued_date": datetime.utcnow().isoformat()
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

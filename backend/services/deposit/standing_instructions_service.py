"""
Standing Instructions Service

Handles automated instructions including:
- Auto-debit for RD installments
- Sweep-in/Sweep-out for savings
- Automatic transfers
- Recurring instructions
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, ForeignKey
from backend.shared.database.deposit_models import DepositAccount
from backend.shared.database.models import Base
from backend.shared.common.response import CustomException
from .account_service import DepositAccountService


# Standing Instruction Model (to be added to deposit_models.py)
class StandingInstruction(Base):
    """Standing Instruction for automated operations"""
    __tablename__ = "deposit_standing_instructions"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False)
    
    instruction_type = Column(String(50), nullable=False)  # auto_debit, sweep_in, sweep_out, transfer
    status = Column(String(50), default='active')  # active, suspended, completed, cancelled
    
    # Auto-debit details
    debit_account_number = Column(String(50))  # External account to debit from
    debit_amount = Column(Numeric(15, 2))
    frequency = Column(String(50))  # daily, weekly, monthly, quarterly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_execution_date = Column(Date)
    
    # Sweep details
    threshold_amount = Column(Numeric(15, 2))  # For sweep-in/out
    sweep_to_account = Column(String(50))  # Target account for sweep
    
    # Execution tracking
    last_execution_date = Column(Date)
    execution_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))


class StandingInstructionService:
    """Service for standing instructions"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.account_service = DepositAccountService(db, tenant_id, user_id)
    
    def create_auto_debit_instruction(
        self,
        account_id: int,
        debit_account_number: str,
        amount: Decimal,
        frequency: str,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Create auto-debit instruction for RD installments"""
        account = self._get_account(account_id)
        
        if account.account_type != 'rd':
            raise CustomException(
                status_code=400,
                message="Auto-debit is only available for RD accounts"
            )
        
        # Calculate next execution date
        next_execution = self._calculate_next_execution(start_date, frequency)
        
        instruction = StandingInstruction(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            instruction_type='auto_debit',
            status='active',
            debit_account_number=debit_account_number,
            debit_amount=amount,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            next_execution_date=next_execution,
            created_by=str(self.user_id)
        )
        
        self.db.add(instruction)
        self.db.commit()
        self.db.refresh(instruction)
        
        return {
            "instruction_id": instruction.id,
            "account_number": account.account_number,
            "instruction_type": "auto_debit",
            "status": "active",
            "debit_amount": float(amount),
            "frequency": frequency,
            "next_execution": next_execution.isoformat()
        }
    
    def create_sweep_instruction(
        self,
        account_id: int,
        sweep_type: str,  # sweep_in or sweep_out
        threshold_amount: Decimal,
        sweep_to_account: str
    ) -> Dict[str, Any]:
        """Create sweep-in/sweep-out instruction"""
        account = self._get_account(account_id)
        
        if account.account_type != 'savings':
            raise CustomException(
                status_code=400,
                message="Sweep instructions are only available for savings accounts"
            )
        
        instruction = StandingInstruction(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            instruction_type=sweep_type,
            status='active',
            threshold_amount=threshold_amount,
            sweep_to_account=sweep_to_account,
            start_date=date.today(),
            created_by=str(self.user_id)
        )
        
        self.db.add(instruction)
        self.db.commit()
        self.db.refresh(instruction)
        
        return {
            "instruction_id": instruction.id,
            "account_number": account.account_number,
            "instruction_type": sweep_type,
            "threshold_amount": float(threshold_amount),
            "sweep_to_account": sweep_to_account,
            "status": "active"
        }
    
    def execute_auto_debit_instructions(
        self,
        execution_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Execute auto-debit instructions"""
        if not execution_date:
            execution_date = date.today()
        
        # Get due instructions
        instructions = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.tenant_id == self.tenant_id,
                StandingInstruction.instruction_type == 'auto_debit',
                StandingInstruction.status == 'active',
                StandingInstruction.next_execution_date <= execution_date,
                StandingInstruction.is_active == True
            )
        ).all()
        
        executed = 0
        failed = 0
        results = []
        
        for instruction in instructions:
            try:
                account = self._get_account(instruction.deposit_account_id)
                
                # Execute debit - pay RD installment
                result = self.account_service.pay_rd_installment(
                    account_id=account.id,
                    amount=instruction.debit_amount,
                    payment_mode='auto_debit',
                    reference_number=f"SI-{instruction.id}"
                )
                
                # Update instruction
                instruction.last_execution_date = execution_date
                instruction.execution_count += 1
                instruction.next_execution_date = self._calculate_next_execution(
                    execution_date,
                    instruction.frequency
                )
                
                # Check if completed
                if instruction.end_date and execution_date >= instruction.end_date:
                    instruction.status = 'completed'
                
                executed += 1
                results.append({
                    "instruction_id": instruction.id,
                    "account_number": account.account_number,
                    "status": "success",
                    "amount": float(instruction.debit_amount)
                })
                
            except Exception as e:
                instruction.failed_count += 1
                failed += 1
                results.append({
                    "instruction_id": instruction.id,
                    "status": "failed",
                    "error": str(e)
                })
        
        self.db.commit()
        
        return {
            "execution_date": execution_date.isoformat(),
            "instructions_processed": len(instructions),
            "executed": executed,
            "failed": failed,
            "results": results
        }
    
    def execute_sweep_instructions(self) -> Dict[str, Any]:
        """Execute sweep-in/sweep-out instructions"""
        # Get active sweep instructions
        instructions = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.tenant_id == self.tenant_id,
                StandingInstruction.instruction_type.in_(['sweep_in', 'sweep_out']),
                StandingInstruction.status == 'active',
                StandingInstruction.is_active == True
            )
        ).all()
        
        executed = 0
        results = []
        
        for instruction in instructions:
            try:
                account = self._get_account(instruction.deposit_account_id)
                
                # Check if sweep should be triggered
                if instruction.instruction_type == 'sweep_out':
                    # If balance exceeds threshold, sweep out excess
                    if account.current_balance > instruction.threshold_amount:
                        sweep_amount = account.current_balance - instruction.threshold_amount
                        
                        # Create withdrawal
                        self.account_service.make_withdrawal(
                            account_id=account.id,
                            amount=sweep_amount,
                            payment_mode='internal_transfer',
                            reference_number=f"SWEEP-{instruction.id}",
                            remarks=f"Sweep-out to {instruction.sweep_to_account}"
                        )
                        
                        executed += 1
                        results.append({
                            "instruction_id": instruction.id,
                            "account_number": account.account_number,
                            "type": "sweep_out",
                            "amount": float(sweep_amount),
                            "status": "success"
                        })
                
                elif instruction.instruction_type == 'sweep_in':
                    # If balance below threshold, sweep in from linked account
                    if account.current_balance < instruction.threshold_amount:
                        sweep_amount = instruction.threshold_amount - account.current_balance
                        
                        # Create deposit
                        self.account_service.make_deposit(
                            account_id=account.id,
                            amount=sweep_amount,
                            payment_mode='internal_transfer',
                            reference_number=f"SWEEP-{instruction.id}",
                            remarks=f"Sweep-in from {instruction.sweep_to_account}"
                        )
                        
                        executed += 1
                        results.append({
                            "instruction_id": instruction.id,
                            "account_number": account.account_number,
                            "type": "sweep_in",
                            "amount": float(sweep_amount),
                            "status": "success"
                        })
                
                # Update execution tracking
                instruction.last_execution_date = date.today()
                instruction.execution_count += 1
                
            except Exception as e:
                instruction.failed_count += 1
                results.append({
                    "instruction_id": instruction.id,
                    "status": "failed",
                    "error": str(e)
                })
        
        self.db.commit()
        
        return {
            "execution_date": date.today().isoformat(),
            "instructions_processed": len(instructions),
            "executed": executed,
            "results": results
        }
    
    def suspend_instruction(
        self,
        instruction_id: int
    ) -> Dict[str, Any]:
        """Suspend a standing instruction"""
        instruction = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.id == instruction_id,
                StandingInstruction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not instruction:
            raise CustomException(status_code=404, message="Instruction not found")
        
        instruction.status = 'suspended'
        self.db.commit()
        
        return {
            "instruction_id": instruction_id,
            "status": "suspended"
        }
    
    def resume_instruction(
        self,
        instruction_id: int
    ) -> Dict[str, Any]:
        """Resume a suspended instruction"""
        instruction = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.id == instruction_id,
                StandingInstruction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not instruction:
            raise CustomException(status_code=404, message="Instruction not found")
        
        if instruction.status != 'suspended':
            raise CustomException(
                status_code=400,
                message="Only suspended instructions can be resumed"
            )
        
        instruction.status = 'active'
        self.db.commit()
        
        return {
            "instruction_id": instruction_id,
            "status": "active"
        }
    
    def cancel_instruction(
        self,
        instruction_id: int
    ) -> Dict[str, Any]:
        """Cancel a standing instruction"""
        instruction = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.id == instruction_id,
                StandingInstruction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not instruction:
            raise CustomException(status_code=404, message="Instruction not found")
        
        instruction.status = 'cancelled'
        instruction.is_active = False
        self.db.commit()
        
        return {
            "instruction_id": instruction_id,
            "status": "cancelled"
        }
    
    def get_account_instructions(
        self,
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Get all instructions for an account"""
        instructions = self.db.query(StandingInstruction).filter(
            and_(
                StandingInstruction.deposit_account_id == account_id,
                StandingInstruction.tenant_id == self.tenant_id
            )
        ).all()
        
        return [
            {
                "instruction_id": inst.id,
                "instruction_type": inst.instruction_type,
                "status": inst.status,
                "debit_amount": float(inst.debit_amount) if inst.debit_amount else None,
                "frequency": inst.frequency,
                "threshold_amount": float(inst.threshold_amount) if inst.threshold_amount else None,
                "next_execution": inst.next_execution_date.isoformat() if inst.next_execution_date else None,
                "last_execution": inst.last_execution_date.isoformat() if inst.last_execution_date else None,
                "execution_count": inst.execution_count,
                "failed_count": inst.failed_count
            }
            for inst in instructions
        ]
    
    def _calculate_next_execution(
        self,
        current_date: date,
        frequency: str
    ) -> date:
        """Calculate next execution date based on frequency"""
        if frequency == 'daily':
            return current_date + timedelta(days=1)
        elif frequency == 'weekly':
            return current_date + timedelta(days=7)
        elif frequency == 'monthly':
            return current_date + timedelta(days=30)
        elif frequency == 'quarterly':
            return current_date + timedelta(days=90)
        else:
            return current_date + timedelta(days=30)  # Default monthly
    
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

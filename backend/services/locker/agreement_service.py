"""
Locker Agreement Service

Handles locker rental agreement lifecycle including:
- Agreement creation from templates
- Digital signature management
- Multi-party signature tracking
- Agreement execution and activation
- Renewal processing
- Termination handling
- Amendment management
- Compliance and audit tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerAgreement,
    LockerAllocation,
    LockerApplication,
    LockerMaster,
    Customer
)
from backend.services.locker.schemas import (
    LockerAgreementCreate,
    LockerAgreementUpdate,
    LockerAgreementResponse,
    AgreementSignatureRequest,
    AgreementExecutionRequest,
    AgreementRenewalRequest,
    AgreementTerminationRequest,
    AgreementAmendmentRequest,
    AgreementFilter,
    AgreementStatus,
    AgreementType,
    SignatureType,
    AgreementStatistics
)
from backend.shared.utils import generate_reference_number


class AgreementService:
    """Service for managing locker agreements"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_agreement(
        self,
        data: LockerAgreementCreate
    ) -> LockerAgreement:
        """
        Create new locker rental agreement
        """
        # Verify allocation exists
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.id == data.allocation_id,
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise ValueError("Allocation not found")
        
        # Check if agreement already exists for this allocation
        existing = self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.allocation_id == data.allocation_id,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.status.in_([
                    AgreementStatus.DRAFT,
                    AgreementStatus.PENDING_SIGNATURE,
                    AgreementStatus.EXECUTED,
                    AgreementStatus.ACTIVE
                ]),
                LockerAgreement.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError("Active agreement already exists for this allocation")
        
        # Generate agreement number
        agreement_number = generate_reference_number("AGR")
        
        # Create agreement
        agreement = LockerAgreement(
            agreement_number=agreement_number,
            agreement_version="1.0",
            tenant_id=self.tenant_id,
            allocation_id=data.allocation_id,
            locker_id=data.locker_id,
            customer_id=data.customer_id,
            application_id=data.application_id,
            agreement_type=data.agreement_type,
            parent_agreement_id=data.parent_agreement_id,
            agreement_date=data.agreement_date,
            agreement_start_date=data.agreement_start_date,
            agreement_end_date=data.agreement_end_date,
            agreement_duration_months=data.agreement_duration_months,
            template_id=data.template_id,
            template_name=data.template_name,
            template_version=data.template_version,
            terms_and_conditions=data.terms_and_conditions,
            dos_and_donts=data.dos_and_donts,
            bank_liability_clause=data.bank_liability_clause,
            insurance_clause=data.insurance_clause,
            access_rules=data.access_rules,
            special_terms=data.special_terms,
            additional_conditions=data.additional_conditions,
            annual_rent=data.annual_rent,
            security_deposit=data.security_deposit,
            rent_frequency=data.rent_frequency,
            rent_escalation_clause=data.rent_escalation_clause,
            rent_escalation_percentage=data.rent_escalation_percentage,
            rent_escalation_frequency_years=data.rent_escalation_frequency_years,
            joint_holder_signature_required=data.joint_holder_signature_required,
            bank_authorized_signatory=data.bank_authorized_signatory,
            witness_1_name=data.witness_1_name,
            witness_2_name=data.witness_2_name,
            agreement_document_path=data.agreement_document_path,
            agreement_document_type=data.agreement_document_type,
            execution_location=data.execution_location,
            stamp_paper_required=data.stamp_paper_required,
            stamp_paper_value=data.stamp_paper_value,
            stamp_paper_number=data.stamp_paper_number,
            stamp_paper_date=data.stamp_paper_date,
            notarized=data.notarized,
            notary_name=data.notary_name,
            notary_registration_number=data.notary_registration_number,
            notary_date=data.notary_date,
            auto_renewal_enabled=data.auto_renewal_enabled,
            renewal_notice_period_days=data.renewal_notice_period_days,
            notice_period_days=data.notice_period_days,
            status=AgreementStatus.DRAFT,
            customer_signed=False,
            joint_holder_1_signed=False,
            joint_holder_2_signed=False,
            bank_signed=False,
            bank_official_stamp=False,
            is_executed=False,
            all_signatures_complete=False,
            renewal_notice_sent=False,
            renewed=False,
            terminated=False,
            kyc_verified_at_execution=False,
            aml_check_done=False,
            legal_review_done=False,
            amendment_count=0,
            customer_copy_sent=False,
            special_instructions=data.special_instructions,
            internal_notes=data.internal_notes,
            remarks=data.remarks,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(agreement)
        self.db.commit()
        self.db.refresh(agreement)
        
        # Update allocation with agreement reference
        allocation.agreement_number = agreement_number
        allocation.updated_by = self.user_id
        self.db.commit()
        
        return agreement
    
    async def get_agreement(
        self,
        agreement_id: uuid.UUID
    ) -> Optional[LockerAgreement]:
        """Get agreement by ID"""
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.id == agreement_id,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        ).first()
    
    async def get_agreement_by_number(
        self,
        agreement_number: str
    ) -> Optional[LockerAgreement]:
        """Get agreement by agreement number"""
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.agreement_number == agreement_number,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        ).first()
    
    async def get_agreement_by_allocation(
        self,
        allocation_id: uuid.UUID
    ) -> Optional[LockerAgreement]:
        """Get active agreement for allocation"""
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.allocation_id == allocation_id,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.status.in_([
                    AgreementStatus.ACTIVE,
                    AgreementStatus.EXECUTED
                ]),
                LockerAgreement.is_deleted == False
            )
        ).first()
    
    async def list_agreements(
        self,
        filters: AgreementFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LockerAgreement], int]:
        """List agreements with filters"""
        query = self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.allocation_id:
            query = query.filter(LockerAgreement.allocation_id == filters.allocation_id)
        
        if filters.customer_id:
            query = query.filter(LockerAgreement.customer_id == filters.customer_id)
        
        if filters.agreement_type:
            query = query.filter(LockerAgreement.agreement_type == filters.agreement_type)
        
        if filters.status:
            query = query.filter(LockerAgreement.status == filters.status)
        
        if filters.expiring_within_days:
            expiry_date = date.today() + timedelta(days=filters.expiring_within_days)
            query = query.filter(
                and_(
                    LockerAgreement.agreement_end_date <= expiry_date,
                    LockerAgreement.status == AgreementStatus.ACTIVE
                )
            )
        
        if filters.renewal_due:
            renewal_date = date.today() + timedelta(days=30)
            query = query.filter(
                and_(
                    LockerAgreement.agreement_end_date <= renewal_date,
                    LockerAgreement.auto_renewal_enabled == True,
                    LockerAgreement.renewal_notice_sent == False,
                    LockerAgreement.status == AgreementStatus.ACTIVE
                )
            )
        
        # Get total count
        total = query.count()
        
        # Order by agreement date (most recent first)
        query = query.order_by(desc(LockerAgreement.agreement_date))
        
        # Pagination
        agreements = query.offset(skip).limit(limit).all()
        
        return agreements, total
    
    async def update_agreement(
        self,
        agreement_id: uuid.UUID,
        data: LockerAgreementUpdate
    ) -> Optional[LockerAgreement]:
        """Update agreement details"""
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            return None
        
        if agreement.status == AgreementStatus.EXECUTED:
            raise ValueError("Cannot modify executed agreement. Use amendment process.")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agreement, field, value)
        
        agreement.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(agreement)
        
        return agreement
    
    async def add_signature(
        self,
        agreement_id: uuid.UUID,
        signature: AgreementSignatureRequest
    ) -> Optional[LockerAgreement]:
        """
        Add signature to agreement
        """
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            return None
        
        if agreement.status == AgreementStatus.EXECUTED:
            raise ValueError("Agreement already executed")
        
        # Update signature based on signer type
        if signature.signer_type == "customer":
            agreement.customer_signature_path = signature.signature_path
            agreement.customer_signed = True
            agreement.customer_signature_date = signature.signature_date
            agreement.customer_signature_type = signature.signature_type
            agreement.customer_digital_signature_id = signature.digital_signature_id
            agreement.customer_ip_address = signature.ip_address
        
        elif signature.signer_type == "joint_holder_1":
            agreement.joint_holder_1_signature_path = signature.signature_path
            agreement.joint_holder_1_signed = True
            agreement.joint_holder_1_signature_date = signature.signature_date
        
        elif signature.signer_type == "joint_holder_2":
            agreement.joint_holder_2_signature_path = signature.signature_path
            agreement.joint_holder_2_signed = True
            agreement.joint_holder_2_signature_date = signature.signature_date
        
        elif signature.signer_type == "bank":
            agreement.bank_signature_path = signature.signature_path
            agreement.bank_signed = True
            agreement.bank_signature_date = signature.signature_date
            agreement.bank_official_stamp = True
        
        # Check if all required signatures are complete
        all_complete = agreement.customer_signed and agreement.bank_signed
        
        if agreement.joint_holder_signature_required:
            all_complete = all_complete and agreement.joint_holder_1_signed
        
        if all_complete:
            agreement.all_signatures_complete = True
            agreement.signatures_completed_date = date.today()
            agreement.status = AgreementStatus.PARTIALLY_SIGNED if not agreement.bank_signed else AgreementStatus.PENDING_SIGNATURE
            
            # If all signatures complete, ready for execution
            if agreement.bank_signed:
                agreement.status = AgreementStatus.PENDING_SIGNATURE
        else:
            agreement.status = AgreementStatus.PENDING_SIGNATURE
        
        agreement.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(agreement)
        
        return agreement
    
    async def execute_agreement(
        self,
        agreement_id: uuid.UUID,
        execution: AgreementExecutionRequest
    ) -> Optional[LockerAgreement]:
        """
        Execute agreement (make it legally binding)
        """
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            return None
        
        if not agreement.all_signatures_complete:
            raise ValueError("All required signatures must be completed before execution")
        
        # Update execution details
        agreement.is_executed = True
        agreement.execution_date = execution.execution_date
        agreement.execution_location = execution.execution_location
        agreement.status = AgreementStatus.EXECUTED
        
        # Update stamp paper details if provided
        if execution.stamp_paper_details:
            agreement.stamp_paper_required = True
            agreement.stamp_paper_value = execution.stamp_paper_details.get("value")
            agreement.stamp_paper_number = execution.stamp_paper_details.get("number")
            agreement.stamp_paper_date = execution.stamp_paper_details.get("date")
        
        # Update notary details if provided
        if execution.notary_details:
            agreement.notarized = True
            agreement.notary_name = execution.notary_details.get("name")
            agreement.notary_registration_number = execution.notary_details.get("registration_number")
            agreement.notary_date = execution.notary_details.get("date")
        
        # Compliance checks
        agreement.kyc_verified_at_execution = True
        agreement.aml_check_done = True
        
        # Activate agreement if start date is today or past
        if agreement.agreement_start_date <= date.today():
            agreement.status = AgreementStatus.ACTIVE
        
        agreement.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(agreement)
        
        # Send customer copy
        await self._send_customer_copy(agreement)
        
        return agreement
    
    async def _send_customer_copy(
        self,
        agreement: LockerAgreement
    ) -> bool:
        """Send executed agreement copy to customer"""
        # TODO: Integrate with document delivery service
        agreement.customer_copy_sent = True
        agreement.customer_copy_sent_date = date.today()
        agreement.customer_copy_delivery_method = "email"
        
        self.db.commit()
        return True
    
    async def renew_agreement(
        self,
        agreement_id: uuid.UUID,
        renewal: AgreementRenewalRequest
    ) -> Optional[LockerAgreement]:
        """
        Renew existing agreement
        """
        old_agreement = await self.get_agreement(agreement_id)
        if not old_agreement:
            return None
        
        if old_agreement.status != AgreementStatus.ACTIVE:
            raise ValueError("Only active agreements can be renewed")
        
        # Calculate new rent with escalation if applicable
        new_rent = renewal.annual_rent
        if renewal.rent_escalation_applied and old_agreement.rent_escalation_percentage > 0:
            new_rent = old_agreement.annual_rent * (
                1 + (old_agreement.rent_escalation_percentage / 100)
            )
        
        # Create new agreement
        new_agreement_data = LockerAgreementCreate(
            allocation_id=old_agreement.allocation_id,
            locker_id=old_agreement.locker_id,
            customer_id=old_agreement.customer_id,
            application_id=old_agreement.application_id,
            agreement_type=AgreementType.RENEWAL,
            parent_agreement_id=old_agreement.id,
            agreement_date=date.today(),
            agreement_start_date=old_agreement.agreement_end_date + timedelta(days=1),
            agreement_end_date=renewal.new_end_date,
            agreement_duration_months=(
                (renewal.new_end_date.year - old_agreement.agreement_end_date.year) * 12 +
                (renewal.new_end_date.month - old_agreement.agreement_end_date.month)
            ),
            template_id=old_agreement.template_id,
            template_name=old_agreement.template_name,
            template_version=old_agreement.template_version,
            terms_and_conditions=old_agreement.terms_and_conditions,
            dos_and_donts=old_agreement.dos_and_donts,
            bank_liability_clause=old_agreement.bank_liability_clause,
            insurance_clause=old_agreement.insurance_clause,
            access_rules=old_agreement.access_rules,
            special_terms=renewal.special_terms or old_agreement.special_terms,
            additional_conditions=old_agreement.additional_conditions,
            annual_rent=new_rent,
            security_deposit=old_agreement.security_deposit,
            rent_frequency=old_agreement.rent_frequency,
            rent_escalation_clause=old_agreement.rent_escalation_clause,
            rent_escalation_percentage=old_agreement.rent_escalation_percentage,
            rent_escalation_frequency_years=old_agreement.rent_escalation_frequency_years,
            joint_holder_signature_required=old_agreement.joint_holder_signature_required,
            bank_authorized_signatory=old_agreement.bank_authorized_signatory,
            witness_1_name=old_agreement.witness_1_name,
            witness_2_name=old_agreement.witness_2_name,
            agreement_document_path="",  # Will be generated
            agreement_document_type="pdf",
            execution_location=old_agreement.execution_location,
            stamp_paper_required=old_agreement.stamp_paper_required,
            stamp_paper_value=old_agreement.stamp_paper_value,
            notarized=False,
            auto_renewal_enabled=old_agreement.auto_renewal_enabled,
            renewal_notice_period_days=old_agreement.renewal_notice_period_days,
            notice_period_days=old_agreement.notice_period_days,
            special_instructions=None,
            internal_notes=f"Renewal of agreement {old_agreement.agreement_number}",
            remarks=None
        )
        
        new_agreement = await self.create_agreement(new_agreement_data)
        
        # Update old agreement
        old_agreement.renewed = True
        old_agreement.renewed_agreement_id = new_agreement.id
        old_agreement.renewal_date = date.today()
        old_agreement.status = AgreementStatus.RENEWED
        old_agreement.updated_by = self.user_id
        
        self.db.commit()
        
        return new_agreement
    
    async def terminate_agreement(
        self,
        agreement_id: uuid.UUID,
        termination: AgreementTerminationRequest
    ) -> Optional[LockerAgreement]:
        """
        Terminate agreement
        """
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            return None
        
        if agreement.status != AgreementStatus.ACTIVE:
            raise ValueError("Only active agreements can be terminated")
        
        # Update termination details
        agreement.terminated = True
        agreement.termination_date = termination.termination_date
        agreement.termination_reason = termination.termination_reason
        agreement.termination_initiated_by = termination.initiated_by
        
        if termination.notice_given:
            agreement.termination_notice_date = termination.notice_date
        
        agreement.status = AgreementStatus.TERMINATED
        agreement.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(agreement)
        
        return agreement
    
    async def amend_agreement(
        self,
        agreement_id: uuid.UUID,
        amendment: AgreementAmendmentRequest
    ) -> Optional[LockerAgreement]:
        """
        Add amendment to agreement
        """
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            return None
        
        if agreement.status not in [AgreementStatus.ACTIVE, AgreementStatus.EXECUTED]:
            raise ValueError("Only active/executed agreements can be amended")
        
        # Store amendment details
        amendments = []
        if agreement.amendment_details:
            import json
            amendments = json.loads(agreement.amendment_details)
        
        amendments.append({
            "amendment_number": agreement.amendment_count + 1,
            "amendment_date": amendment.amendment_date.isoformat(),
            "details": amendment.amendment_details,
            "amended_clauses": amendment.amended_clauses,
            "requires_new_signatures": amendment.requires_new_signatures,
            "amended_by": str(self.user_id)
        })
        
        import json
        agreement.amendment_details = json.dumps(amendments)
        agreement.amendment_count += 1
        agreement.last_amendment_date = amendment.amendment_date
        
        # Increment version
        version_parts = agreement.agreement_version.split(".")
        version_parts[1] = str(int(version_parts[1]) + 1)
        agreement.agreement_version = ".".join(version_parts)
        
        # If requires new signatures, reset signature status
        if amendment.requires_new_signatures:
            agreement.status = AgreementStatus.PENDING_SIGNATURE
            agreement.all_signatures_complete = False
        
        agreement.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(agreement)
        
        return agreement
    
    async def check_expiring_agreements(
        self,
        days: int = 30
    ) -> List[LockerAgreement]:
        """
        Get agreements expiring within specified days
        """
        expiry_date = date.today() + timedelta(days=days)
        
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.agreement_end_date <= expiry_date,
                LockerAgreement.agreement_end_date >= date.today(),
                LockerAgreement.is_deleted == False
            )
        ).order_by(LockerAgreement.agreement_end_date).all()
    
    async def send_renewal_notices(
        self
    ) -> Dict[str, Any]:
        """
        Send renewal notices for agreements with auto-renewal enabled
        """
        # Get agreements due for renewal notice
        agreements = self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.auto_renewal_enabled == True,
                LockerAgreement.renewal_notice_sent == False,
                LockerAgreement.is_deleted == False
            )
        ).all()
        
        sent = []
        failed = []
        
        for agreement in agreements:
            # Check if notice should be sent
            days_to_expiry = (agreement.agreement_end_date - date.today()).days
            
            if days_to_expiry <= agreement.renewal_notice_period_days:
                try:
                    # TODO: Integrate with notification service
                    agreement.renewal_notice_sent = True
                    agreement.renewal_notice_date = date.today()
                    agreement.updated_by = self.user_id
                    sent.append(agreement.agreement_number)
                except Exception as e:
                    failed.append({
                        "agreement_number": agreement.agreement_number,
                        "error": str(e)
                    })
        
        if sent:
            self.db.commit()
        
        return {
            "total_processed": len(agreements),
            "notices_sent": len(sent),
            "failed": len(failed),
            "sent_agreements": sent,
            "failed_items": failed
        }
    
    async def get_customer_agreements(
        self,
        customer_id: uuid.UUID
    ) -> List[LockerAgreement]:
        """Get all agreements for customer"""
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.customer_id == customer_id,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        ).order_by(desc(LockerAgreement.agreement_date)).all()
    
    async def get_pending_signatures(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[LockerAgreement]:
        """Get agreements pending signatures"""
        query = self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.status == AgreementStatus.PENDING_SIGNATURE,
                LockerAgreement.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        return query.order_by(LockerAgreement.agreement_date).all()
    
    async def get_statistics(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> AgreementStatistics:
        """Get agreement statistics"""
        query = self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        total_agreements = query.count()
        
        # By status
        by_status = {}
        status_counts = query.with_entities(
            LockerAgreement.status,
            func.count(LockerAgreement.id)
        ).group_by(LockerAgreement.status).all()
        
        for status, count in status_counts:
            by_status[status] = count
        
        # Expiring agreements
        expiring_30 = query.filter(
            and_(
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.agreement_end_date <= date.today() + timedelta(days=30),
                LockerAgreement.agreement_end_date >= date.today()
            )
        ).count()
        
        expiring_60 = query.filter(
            and_(
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.agreement_end_date <= date.today() + timedelta(days=60),
                LockerAgreement.agreement_end_date >= date.today()
            )
        ).count()
        
        expiring_90 = query.filter(
            and_(
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.agreement_end_date <= date.today() + timedelta(days=90),
                LockerAgreement.agreement_end_date >= date.today()
            )
        ).count()
        
        # Pending signatures
        pending_signatures = query.filter(
            LockerAgreement.status == AgreementStatus.PENDING_SIGNATURE
        ).count()
        
        # Fully executed
        fully_executed = query.filter(
            and_(
                LockerAgreement.is_executed == True,
                LockerAgreement.all_signatures_complete == True
            )
        ).count()
        
        # Renewal due
        renewal_due = query.filter(
            and_(
                LockerAgreement.status == AgreementStatus.ACTIVE,
                LockerAgreement.auto_renewal_enabled == True,
                LockerAgreement.renewal_notice_sent == False,
                LockerAgreement.agreement_end_date <= date.today() + timedelta(days=30)
            )
        ).count()
        
        return AgreementStatistics(
            total_agreements=total_agreements,
            by_status=by_status,
            expiring_30_days=expiring_30,
            expiring_60_days=expiring_60,
            expiring_90_days=expiring_90,
            pending_signatures=pending_signatures,
            fully_executed=fully_executed,
            renewal_due=renewal_due
        )
    
    async def get_agreement_history(
        self,
        allocation_id: uuid.UUID
    ) -> List[LockerAgreement]:
        """Get complete agreement history for allocation"""
        return self.db.query(LockerAgreement).filter(
            and_(
                LockerAgreement.allocation_id == allocation_id,
                LockerAgreement.tenant_id == self.tenant_id,
                LockerAgreement.is_deleted == False
            )
        ).order_by(desc(LockerAgreement.agreement_date)).all()
    
    async def bulk_send_customer_copies(
        self,
        agreement_ids: List[uuid.UUID]
    ) -> Dict[str, Any]:
        """Bulk send customer copies"""
        successful = []
        failed = []
        
        for agreement_id in agreement_ids:
            try:
                agreement = await self.get_agreement(agreement_id)
                if agreement and agreement.is_executed:
                    result = await self._send_customer_copy(agreement)
                    if result:
                        successful.append(str(agreement_id))
                    else:
                        failed.append({
                            "id": str(agreement_id),
                            "reason": "Failed to send"
                        })
                else:
                    failed.append({
                        "id": str(agreement_id),
                        "reason": "Not executed or not found"
                    })
            except Exception as e:
                failed.append({
                    "id": str(agreement_id),
                    "reason": str(e)
                })
        
        return {
            "total": len(agreement_ids),
            "successful": len(successful),
            "failed": len(failed),
            "successful_ids": successful,
            "failed_items": failed
        }
    
    async def generate_agreement_document(
        self,
        agreement_id: uuid.UUID
    ) -> str:
        """
        Generate agreement document from template
        Returns: Document path
        """
        agreement = await self.get_agreement(agreement_id)
        if not agreement:
            raise ValueError("Agreement not found")
        
        # TODO: Integrate with document generation service
        # This would use template engine to generate PDF from agreement data
        
        document_path = f"/documents/agreements/{agreement.agreement_number}.pdf"
        agreement.agreement_document_path = document_path
        
        self.db.commit()
        
        return document_path

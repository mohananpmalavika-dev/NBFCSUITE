"""
Locker Customer Management Service

Handles all customer-related operations including:
- Customer profile management
- Joint holder management
- KYC document management
- Nominee management
- Authorization management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerCustomer, LockerJointHolder, LockerKYC, LockerNominee,
    LockerAuthorization, LockerAllocation
)
from .schemas import (
    LockerCustomerCreate, LockerCustomerUpdate, LockerCustomerResponse,
    LockerJointHolderCreate, LockerJointHolderUpdate, LockerJointHolderResponse,
    LockerKYCCreate, LockerKYCUpdate, LockerKYCResponse,
    LockerNomineeCreate, LockerNomineeUpdate, LockerNomineeResponse,
    LockerAuthorizationCreate, LockerAuthorizationUpdate, LockerAuthorizationResponse,
    CustomerType, VerificationStatus, ApprovalStatus,
    CustomerAnalytics, JointHolderAnalytics, NomineeAnalytics
)


class LockerCustomerService:
    """Service for managing locker customer operations"""
    
    def __init__(self, db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CUSTOMER MANAGEMENT ====================
    
    async def create_customer(
        self,
        customer_data: LockerCustomerCreate
    ) -> LockerCustomer:
        """Create a new locker customer"""
        # Generate customer ID
        locker_customer_id = f"LC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate age from DOB
        age = None
        if customer_data.date_of_birth:
            today = date.today()
            age = today.year - customer_data.date_of_birth.year
            if today.month < customer_data.date_of_birth.month or \
               (today.month == customer_data.date_of_birth.month and today.day < customer_data.date_of_birth.day):
                age -= 1
        
        # Auto-detect senior citizen
        is_senior_citizen = age >= 60 if age else False
        
        customer = LockerCustomer(
            tenant_id=self.tenant_id,
            locker_customer_id=locker_customer_id,
            **customer_data.dict(exclude_unset=True),
            age=age,
            is_senior_citizen=is_senior_citizen or customer_data.is_senior_citizen,
            status='active',
            verification_status='pending',
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    async def get_customer(self, customer_id: uuid.UUID) -> Optional[LockerCustomer]:
        """Get customer by ID"""
        return self.db.query(LockerCustomer).filter(
            and_(
                LockerCustomer.id == customer_id,
                LockerCustomer.tenant_id == self.tenant_id,
                LockerCustomer.is_deleted == False
            )
        ).first()
    
    async def update_customer(
        self,
        customer_id: uuid.UUID,
        customer_data: LockerCustomerUpdate
    ) -> Optional[LockerCustomer]:
        """Update customer details"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        update_data = customer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_by = self.user_id
        customer.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    async def verify_customer(
        self,
        customer_id: uuid.UUID,
        verification_status: VerificationStatus,
        remarks: Optional[str] = None
    ) -> Optional[LockerCustomer]:
        """Verify customer KYC and details"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        customer.verification_status = verification_status.value
        customer.verification_date = date.today()
        customer.verified_by = self.user_id
        customer.updated_by = self.user_id
        customer.updated_at = datetime.utcnow()
        
        if remarks:
            customer.remarks = remarks
        
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    async def search_customers(
        self,
        search_query: Optional[str] = None,
        customer_category: Optional[str] = None,
        verification_status: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[LockerCustomer], int]:
        """Search customers with filters"""
        query = self.db.query(LockerCustomer).filter(
            and_(
                LockerCustomer.tenant_id == self.tenant_id,
                LockerCustomer.is_deleted == False
            )
        )
        
        # Apply filters
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                or_(
                    LockerCustomer.full_name.ilike(search),
                    LockerCustomer.mobile_number.ilike(search),
                    LockerCustomer.email.ilike(search),
                    LockerCustomer.pan_number.ilike(search),
                    LockerCustomer.aadhar_number.ilike(search)
                )
            )
        
        if customer_category:
            query = query.filter(LockerCustomer.customer_category == customer_category)
        
        if verification_status:
            query = query.filter(LockerCustomer.verification_status == verification_status)
        
        if status:
            query = query.filter(LockerCustomer.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        customers = query.offset(offset).limit(page_size).all()
        
        return customers, total

    
    # ==================== JOINT HOLDER MANAGEMENT ====================
    
    async def add_joint_holder(
        self,
        joint_holder_data: LockerJointHolderCreate
    ) -> LockerJointHolder:
        """Add a joint holder to an allocation"""
        # Generate joint holder ID
        joint_holder_id = f"JH{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        joint_holder = LockerJointHolder(
            tenant_id=self.tenant_id,
            joint_holder_id=joint_holder_id,
            **joint_holder_data.dict(exclude_unset=True),
            status='active',
            activation_date=date.today(),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(joint_holder)
        self.db.commit()
        self.db.refresh(joint_holder)
        
        return joint_holder
    
    async def get_joint_holder(self, joint_holder_id: uuid.UUID) -> Optional[LockerJointHolder]:
        """Get joint holder by ID"""
        return self.db.query(LockerJointHolder).filter(
            and_(
                LockerJointHolder.id == joint_holder_id,
                LockerJointHolder.tenant_id == self.tenant_id,
                LockerJointHolder.is_deleted == False
            )
        ).first()
    
    async def get_allocation_joint_holders(
        self,
        allocation_id: uuid.UUID
    ) -> List[LockerJointHolder]:
        """Get all joint holders for an allocation"""
        return self.db.query(LockerJointHolder).filter(
            and_(
                LockerJointHolder.allocation_id == allocation_id,
                LockerJointHolder.tenant_id == self.tenant_id,
                LockerJointHolder.is_deleted == False
            )
        ).order_by(LockerJointHolder.holder_sequence).all()
    
    async def update_joint_holder(
        self,
        joint_holder_id: uuid.UUID,
        joint_holder_data: LockerJointHolderUpdate
    ) -> Optional[LockerJointHolder]:
        """Update joint holder details"""
        joint_holder = await self.get_joint_holder(joint_holder_id)
        if not joint_holder:
            return None
        
        update_data = joint_holder_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(joint_holder, field, value)
        
        joint_holder.updated_by = self.user_id
        joint_holder.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(joint_holder)
        
        return joint_holder
    
    async def deactivate_joint_holder(
        self,
        joint_holder_id: uuid.UUID,
        reason: str
    ) -> Optional[LockerJointHolder]:
        """Deactivate a joint holder"""
        joint_holder = await self.get_joint_holder(joint_holder_id)
        if not joint_holder:
            return None
        
        joint_holder.status = 'inactive'
        joint_holder.deactivation_date = date.today()
        joint_holder.deactivation_reason = reason
        joint_holder.updated_by = self.user_id
        joint_holder.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(joint_holder)
        
        return joint_holder
    
    # ==================== KYC DOCUMENT MANAGEMENT ====================
    
    async def upload_kyc_document(
        self,
        kyc_data: LockerKYCCreate
    ) -> LockerKYC:
        """Upload a KYC document"""
        # Generate KYC ID
        kyc_id = f"KYC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check if document is expired
        is_expired = False
        if kyc_data.expiry_date:
            is_expired = kyc_data.expiry_date < date.today()
        
        kyc = LockerKYC(
            tenant_id=self.tenant_id,
            kyc_id=kyc_id,
            **kyc_data.dict(exclude_unset=True),
            is_expired=is_expired,
            verification_status='pending',
            kyc_compliance=False,
            aml_checked=False,
            version_number=1,
            is_latest_version=True,
            uploaded_by=self.user_id,
            upload_date=datetime.utcnow(),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(kyc)
        self.db.commit()
        self.db.refresh(kyc)
        
        return kyc
    
    async def get_kyc_document(self, kyc_id: uuid.UUID) -> Optional[LockerKYC]:
        """Get KYC document by ID"""
        return self.db.query(LockerKYC).filter(
            and_(
                LockerKYC.id == kyc_id,
                LockerKYC.tenant_id == self.tenant_id,
                LockerKYC.is_deleted == False
            )
        ).first()
    
    async def get_customer_kyc_documents(
        self,
        locker_customer_id: uuid.UUID
    ) -> List[LockerKYC]:
        """Get all KYC documents for a customer"""
        return self.db.query(LockerKYC).filter(
            and_(
                LockerKYC.locker_customer_id == locker_customer_id,
                LockerKYC.tenant_id == self.tenant_id,
                LockerKYC.is_deleted == False,
                LockerKYC.is_latest_version == True
            )
        ).order_by(LockerKYC.upload_date.desc()).all()
    
    async def verify_kyc_document(
        self,
        kyc_id: uuid.UUID,
        verification_status: VerificationStatus,
        verification_remarks: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[LockerKYC]:
        """Verify or reject a KYC document"""
        kyc = await self.get_kyc_document(kyc_id)
        if not kyc:
            return None
        
        kyc.verification_status = verification_status.value
        kyc.verified_by = self.user_id
        kyc.verification_date = date.today()
        kyc.verification_remarks = verification_remarks
        kyc.updated_by = self.user_id
        kyc.updated_at = datetime.utcnow()
        
        if verification_status == VerificationStatus.VERIFIED:
            kyc.kyc_compliance = True
        elif verification_status == VerificationStatus.REJECTED:
            kyc.rejection_reason = rejection_reason
        
        self.db.commit()
        self.db.refresh(kyc)
        
        return kyc
    
    async def check_kyc_compliance(
        self,
        locker_customer_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check if customer has all mandatory KYC documents"""
        kyc_documents = await self.get_customer_kyc_documents(locker_customer_id)
        
        mandatory_docs = ['identity_proof', 'address_proof', 'photo', 'signature']
        uploaded_categories = [doc.document_category for doc in kyc_documents]
        verified_categories = [
            doc.document_category for doc in kyc_documents 
            if doc.verification_status == 'verified'
        ]
        
        missing_docs = [cat for cat in mandatory_docs if cat not in uploaded_categories]
        pending_verification = [cat for cat in mandatory_docs if cat not in verified_categories]
        
        is_compliant = len(missing_docs) == 0 and len(pending_verification) == 0
        
        return {
            'is_compliant': is_compliant,
            'total_documents': len(kyc_documents),
            'verified_documents': len([d for d in kyc_documents if d.verification_status == 'verified']),
            'missing_documents': missing_docs,
            'pending_verification': pending_verification,
            'expired_documents': len([d for d in kyc_documents if d.is_expired])
        }

    
    # ==================== NOMINEE MANAGEMENT ====================
    
    async def add_nominee(
        self,
        nominee_data: LockerNomineeCreate
    ) -> LockerNominee:
        """Add a nominee to an allocation"""
        # Generate nominee ID
        nominee_id = f"NOM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate age
        today = date.today()
        age = today.year - nominee_data.date_of_birth.year
        if today.month < nominee_data.date_of_birth.month or \
           (today.month == nominee_data.date_of_birth.month and today.day < nominee_data.date_of_birth.day):
            age -= 1
        
        is_minor = age < 18
        
        nominee = LockerNominee(
            tenant_id=self.tenant_id,
            nominee_id=nominee_id,
            **nominee_data.dict(exclude_unset=True),
            is_minor=is_minor,
            age=age,
            status='active',
            verification_status='pending',
            nomination_accepted=False,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(nominee)
        self.db.commit()
        self.db.refresh(nominee)
        
        return nominee
    
    async def get_nominee(self, nominee_id: uuid.UUID) -> Optional[LockerNominee]:
        """Get nominee by ID"""
        return self.db.query(LockerNominee).filter(
            and_(
                LockerNominee.id == nominee_id,
                LockerNominee.tenant_id == self.tenant_id,
                LockerNominee.is_deleted == False
            )
        ).first()
    
    async def get_allocation_nominees(
        self,
        allocation_id: uuid.UUID
    ) -> List[LockerNominee]:
        """Get all nominees for an allocation"""
        return self.db.query(LockerNominee).filter(
            and_(
                LockerNominee.allocation_id == allocation_id,
                LockerNominee.tenant_id == self.tenant_id,
                LockerNominee.is_deleted == False
            )
        ).order_by(LockerNominee.nominee_sequence).all()
    
    async def update_nominee(
        self,
        nominee_id: uuid.UUID,
        nominee_data: LockerNomineeUpdate
    ) -> Optional[LockerNominee]:
        """Update nominee details"""
        nominee = await self.get_nominee(nominee_id)
        if not nominee:
            return None
        
        update_data = nominee_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nominee, field, value)
        
        nominee.updated_by = self.user_id
        nominee.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(nominee)
        
        return nominee
    
    async def verify_nominee(
        self,
        nominee_id: uuid.UUID,
        verification_status: VerificationStatus
    ) -> Optional[LockerNominee]:
        """Verify nominee details"""
        nominee = await self.get_nominee(nominee_id)
        if not nominee:
            return None
        
        nominee.verification_status = verification_status.value
        nominee.verified_by = self.user_id
        nominee.verification_date = date.today()
        nominee.updated_by = self.user_id
        nominee.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(nominee)
        
        return nominee
    
    async def validate_nominee_percentages(
        self,
        allocation_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Validate that nominee percentages total 100%"""
        nominees = await self.get_allocation_nominees(allocation_id)
        
        if not nominees:
            return {'valid': False, 'total': 0, 'message': 'No nominees added'}
        
        total_percentage = sum(n.nominee_percentage for n in nominees)
        
        return {
            'valid': total_percentage == 100,
            'total': float(total_percentage),
            'count': len(nominees),
            'message': f'Total percentage: {total_percentage}%'
        }
    
    # ==================== AUTHORIZATION MANAGEMENT ====================
    
    async def create_authorization(
        self,
        auth_data: LockerAuthorizationCreate
    ) -> LockerAuthorization:
        """Create an authorization for locker access"""
        # Generate authorization ID
        authorization_id = f"AUTH{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        authorization = LockerAuthorization(
            tenant_id=self.tenant_id,
            authorization_id=authorization_id,
            **auth_data.dict(exclude_unset=True),
            approval_status='pending',
            status='active',
            signature_verified=False,
            total_access_count=0,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(authorization)
        self.db.commit()
        self.db.refresh(authorization)
        
        return authorization
    
    async def get_authorization(self, auth_id: uuid.UUID) -> Optional[LockerAuthorization]:
        """Get authorization by ID"""
        return self.db.query(LockerAuthorization).filter(
            and_(
                LockerAuthorization.id == auth_id,
                LockerAuthorization.tenant_id == self.tenant_id,
                LockerAuthorization.is_deleted == False
            )
        ).first()
    
    async def get_allocation_authorizations(
        self,
        allocation_id: uuid.UUID
    ) -> List[LockerAuthorization]:
        """Get all authorizations for an allocation"""
        return self.db.query(LockerAuthorization).filter(
            and_(
                LockerAuthorization.allocation_id == allocation_id,
                LockerAuthorization.tenant_id == self.tenant_id,
                LockerAuthorization.is_deleted == False
            )
        ).order_by(LockerAuthorization.created_at.desc()).all()
    
    async def approve_authorization(
        self,
        auth_id: uuid.UUID,
        approval_status: ApprovalStatus,
        approval_remarks: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[LockerAuthorization]:
        """Approve or reject an authorization"""
        authorization = await self.get_authorization(auth_id)
        if not authorization:
            return None
        
        authorization.approval_status = approval_status.value
        authorization.approved_by = self.user_id
        authorization.approval_date = date.today()
        authorization.approval_remarks = approval_remarks
        authorization.updated_by = self.user_id
        authorization.updated_at = datetime.utcnow()
        
        if approval_status == ApprovalStatus.REJECTED:
            authorization.rejection_reason = rejection_reason
            authorization.status = 'inactive'
        elif approval_status == ApprovalStatus.APPROVED:
            authorization.status = 'active'
        
        self.db.commit()
        self.db.refresh(authorization)
        
        return authorization
    
    async def revoke_authorization(
        self,
        auth_id: uuid.UUID,
        revocation_reason: str,
        revocation_document_path: Optional[str] = None
    ) -> Optional[LockerAuthorization]:
        """Revoke an authorization"""
        authorization = await self.get_authorization(auth_id)
        if not authorization:
            return None
        
        authorization.approval_status = 'revoked'
        authorization.status = 'inactive'
        authorization.revoked_by_customer = True
        authorization.revocation_date = date.today()
        authorization.revocation_reason = revocation_reason
        authorization.revocation_document_path = revocation_document_path
        authorization.updated_by = self.user_id
        authorization.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(authorization)
        
        return authorization
    
    async def update_authorization(
        self,
        auth_id: uuid.UUID,
        auth_data: LockerAuthorizationUpdate
    ) -> Optional[LockerAuthorization]:
        """Update authorization details"""
        authorization = await self.get_authorization(auth_id)
        if not authorization:
            return None
        
        update_data = auth_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(authorization, field, value)
        
        authorization.updated_by = self.user_id
        authorization.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(authorization)
        
        return authorization
    
    async def check_authorization_validity(
        self,
        auth_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check if authorization is currently valid"""
        authorization = await self.get_authorization(auth_id)
        if not authorization:
            return {'valid': False, 'reason': 'Authorization not found'}
        
        today = date.today()
        
        # Check approval status
        if authorization.approval_status != 'approved':
            return {'valid': False, 'reason': f'Authorization is {authorization.approval_status}'}
        
        # Check active status
        if authorization.status != 'active':
            return {'valid': False, 'reason': f'Authorization status is {authorization.status}'}
        
        # Check validity period
        if authorization.authorization_valid_from > today:
            return {'valid': False, 'reason': 'Authorization not yet effective'}
        
        if authorization.authorization_valid_to and authorization.authorization_valid_to < today:
            return {'valid': False, 'reason': 'Authorization expired'}
        
        return {
            'valid': True,
            'authorization_id': authorization.authorization_id,
            'authorized_person': authorization.authorized_person_name,
            'permissions': {
                'can_deposit': authorization.can_deposit_items,
                'can_retrieve': authorization.can_retrieve_items,
                'can_view': authorization.can_view_contents,
                'can_pay': authorization.can_make_rent_payments
            }
        }

    
    # ==================== ANALYTICS & REPORTING ====================
    
    async def get_customer_analytics(self) -> CustomerAnalytics:
        """Get customer analytics summary"""
        customers = self.db.query(LockerCustomer).filter(
            and_(
                LockerCustomer.tenant_id == self.tenant_id,
                LockerCustomer.is_deleted == False
            )
        ).all()
        
        by_category = {}
        by_verification = {}
        senior_citizens = 0
        premium_customers = 0
        kyc_pending = 0
        kyc_completed = 0
        
        for customer in customers:
            # Count by category
            category = customer.customer_category
            by_category[category] = by_category.get(category, 0) + 1
            
            # Count by verification status
            status = customer.verification_status
            by_verification[status] = by_verification.get(status, 0) + 1
            
            # Special categories
            if customer.is_senior_citizen:
                senior_citizens += 1
            if customer.is_premium_customer:
                premium_customers += 1
            
            # KYC status
            if customer.verification_status == 'pending':
                kyc_pending += 1
            elif customer.verification_status == 'verified':
                kyc_completed += 1
        
        return CustomerAnalytics(
            total_customers=len(customers),
            by_category=by_category,
            by_verification_status=by_verification,
            senior_citizens=senior_citizens,
            premium_customers=premium_customers,
            kyc_pending=kyc_pending,
            kyc_completed=kyc_completed
        )
    
    async def get_joint_holder_analytics(self) -> JointHolderAnalytics:
        """Get joint holder analytics"""
        joint_holders = self.db.query(LockerJointHolder).filter(
            and_(
                LockerJointHolder.tenant_id == self.tenant_id,
                LockerJointHolder.is_deleted == False
            )
        ).all()
        
        by_operation_mode = {}
        active = 0
        inactive = 0
        
        # Get unique allocation IDs
        allocation_ids = set()
        
        for jh in joint_holders:
            allocation_ids.add(jh.allocation_id)
            
            # Count by operation mode
            mode = jh.operation_mode
            by_operation_mode[mode] = by_operation_mode.get(mode, 0) + 1
            
            # Count by status
            if jh.status == 'active':
                active += 1
            else:
                inactive += 1
        
        return JointHolderAnalytics(
            total_joint_accounts=len(allocation_ids),
            by_operation_mode=by_operation_mode,
            active_joint_holders=active,
            inactive_joint_holders=inactive
        )
    
    async def get_nominee_analytics(self) -> NomineeAnalytics:
        """Get nominee analytics"""
        nominees = self.db.query(LockerNominee).filter(
            and_(
                LockerNominee.tenant_id == self.tenant_id,
                LockerNominee.is_deleted == False
            )
        ).all()
        
        allocation_ids = set()
        minor_nominees = 0
        verified = 0
        pending = 0
        
        for nominee in nominees:
            allocation_ids.add(nominee.allocation_id)
            
            if nominee.is_minor:
                minor_nominees += 1
            
            if nominee.verification_status == 'verified':
                verified += 1
            elif nominee.verification_status == 'pending':
                pending += 1
        
        # Get total allocations
        total_allocations = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False,
                LockerAllocation.status == 'active'
            )
        ).count()
        
        return NomineeAnalytics(
            total_nominees=len(nominees),
            allocations_with_nominees=len(allocation_ids),
            allocations_without_nominees=total_allocations - len(allocation_ids),
            minor_nominees=minor_nominees,
            verified_nominees=verified,
            pending_verification=pending
        )
    
    # ==================== BULK OPERATIONS ====================
    
    async def bulk_upload_kyc(
        self,
        locker_customer_id: uuid.UUID,
        kyc_documents: List[LockerKYCCreate]
    ) -> Dict[str, Any]:
        """Bulk upload KYC documents"""
        uploaded = []
        errors = []
        
        for kyc_data in kyc_documents:
            try:
                kyc = await self.upload_kyc_document(kyc_data)
                uploaded.append(kyc)
            except Exception as e:
                errors.append({
                    'document_type': kyc_data.document_type,
                    'error': str(e)
                })
        
        return {
            'total_uploaded': len(kyc_documents),
            'successful': len(uploaded),
            'failed': len(errors),
            'kyc_documents': uploaded,
            'errors': errors
        }
    
    async def get_customer_complete_profile(
        self,
        locker_customer_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get complete customer profile with all related data"""
        customer = self.db.query(LockerCustomer).filter(
            and_(
                LockerCustomer.id == locker_customer_id,
                LockerCustomer.tenant_id == self.tenant_id,
                LockerCustomer.is_deleted == False
            )
        ).first()
        
        if not customer:
            return None
        
        # Get allocation if exists
        allocation = None
        if customer.allocation_id:
            allocation = self.db.query(LockerAllocation).filter(
                LockerAllocation.id == customer.allocation_id
            ).first()
        
        # Get KYC documents
        kyc_documents = await self.get_customer_kyc_documents(locker_customer_id)
        kyc_compliance = await self.check_kyc_compliance(locker_customer_id)
        
        # Get nominees
        nominees = []
        if allocation:
            nominees = await self.get_allocation_nominees(allocation.id)
        
        # Get joint holders
        joint_holders = []
        if allocation:
            joint_holders = await self.get_allocation_joint_holders(allocation.id)
        
        # Get authorizations
        authorizations = []
        if allocation:
            authorizations = await self.get_allocation_authorizations(allocation.id)
        
        return {
            'customer': customer,
            'allocation': allocation,
            'kyc_documents': kyc_documents,
            'kyc_compliance': kyc_compliance,
            'nominees': nominees,
            'joint_holders': joint_holders,
            'authorizations': authorizations
        }

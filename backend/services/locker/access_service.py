"""
Locker Access Service

Manages locker access requests, verification, and access logging.
Implements dual authentication, biometric verification, and access control.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from backend.shared.database.locker_models import (
    LockerAccessLog,
    LockerAllocation,
    LockerMaster,
    LockerCustomer,
    LockerJointHolder
)
from backend.services.locker.schemas import (
    LockerAccessLogCreate,
    LockerAccessLogUpdate,
    LockerAccessLogResponse
)


class LockerAccessService:
    """Service for managing locker access operations"""
    
    def __init__(self, db: Session, tenant_id: UUID, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== ACCESS REQUEST ====================
    
    async def request_access(self, data: LockerAccessLogCreate) -> LockerAccessLogResponse:
        """
        Create new locker access request with verification
        
        Validates:
        - Customer authorization
        - Operating hours
        - Allocation status
        - Dual authentication requirements
        """
        # Validate allocation
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == data.allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active'
        ).first()
        
        if not allocation:
            raise ValueError("Active allocation not found")
        
        # Validate locker availability
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.id == data.locker_id,
            LockerMaster.tenant_id == self.tenant_id,
            LockerMaster.is_deleted == False
        ).first()
        
        if not locker or locker.status != 'occupied':
            raise ValueError("Locker not available for access")
        
        # Validate operating hours
        if not await self._is_within_operating_hours(data.access_time_in):
            if not data.emergency_access:
                raise ValueError("Access outside operating hours requires emergency authorization")
        
        # Validate customer authorization
        is_authorized = await self._validate_customer_authorization(
            data.accessor_type,
            data.accessor_id_number,
            data.allocation_id
        )
        
        if not is_authorized:
            raise ValueError("Customer not authorized for locker access")
        
        # Generate access log number
        access_log_number = await self._generate_access_log_number()
        
        # Create access log
        access_log = LockerAccessLog(
            tenant_id=self.tenant_id,
            access_log_number=access_log_number,
            locker_id=data.locker_id,
            allocation_id=data.allocation_id,
            customer_id=data.customer_id,
            access_date=data.access_date or date.today(),
            access_time_in=data.access_time_in or datetime.now(),
            accessor_type=data.accessor_type,
            accessor_name=data.accessor_name,
            accessor_id_type=data.accessor_id_type,
            accessor_id_number=data.accessor_id_number,
            authorized_by=data.authorized_by,
            authorization_document=data.authorization_document,
            witness_1_name=data.witness_1_name,
            witness_1_employee_id=data.witness_1_employee_id,
            witness_2_name=data.witness_2_name,
            witness_2_employee_id=data.witness_2_employee_id,
            purpose=data.purpose,
            items_deposited=data.items_deposited,
            items_retrieved=data.items_retrieved,
            biometric_verified=data.biometric_verified,
            photo_captured=data.photo_captured,
            photo_path=data.photo_path,
            signature_captured=data.signature_captured,
            signature_path=data.signature_path,
            emergency_access=data.emergency_access,
            court_order=data.court_order,
            court_order_number=data.court_order_number,
            access_type=data.access_type or 'normal',
            remarks=data.remarks,
            special_notes=data.special_notes,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(access_log)
        self.db.commit()
        self.db.refresh(access_log)
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    async def complete_access(
        self,
        access_log_id: UUID,
        exit_time: datetime,
        remarks: Optional[str] = None
    ) -> LockerAccessLogResponse:
        """Complete locker access by recording exit time"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.id == access_log_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            raise ValueError("Access log not found")
        
        if access_log.access_time_out:
            raise ValueError("Access already completed")
        
        # Calculate duration
        duration = exit_time - access_log.access_time_in
        
        access_log.access_time_out = exit_time
        if remarks:
            access_log.remarks = f"{access_log.remarks}\nExit remarks: {remarks}" if access_log.remarks else remarks
        access_log.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(access_log)
        
        return LockerAccessLogResponse.from_orm(access_log)

    
    # ==================== VERIFICATION ====================
    
    async def verify_biometric(
        self,
        access_log_id: UUID,
        biometric_data: str,
        verified: bool
    ) -> LockerAccessLogResponse:
        """Record biometric verification for access log"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.id == access_log_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            raise ValueError("Access log not found")
        
        access_log.biometric_verified = verified
        access_log.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(access_log)
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    async def capture_photo(
        self,
        access_log_id: UUID,
        photo_path: str
    ) -> LockerAccessLogResponse:
        """Record photo capture for access log"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.id == access_log_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            raise ValueError("Access log not found")
        
        access_log.photo_captured = True
        access_log.photo_path = photo_path
        access_log.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(access_log)
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    async def capture_signature(
        self,
        access_log_id: UUID,
        signature_path: str
    ) -> LockerAccessLogResponse:
        """Record signature capture for access log"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.id == access_log_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            raise ValueError("Access log not found")
        
        access_log.signature_captured = True
        access_log.signature_path = signature_path
        access_log.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(access_log)
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    # ==================== QUERIES ====================
    
    async def get_access_log(self, access_log_id: UUID) -> Optional[LockerAccessLogResponse]:
        """Get access log by ID"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.id == access_log_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            return None
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    async def get_access_log_by_number(
        self,
        access_log_number: str
    ) -> Optional[LockerAccessLogResponse]:
        """Get access log by access log number"""
        access_log = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.access_log_number == access_log_number,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).first()
        
        if not access_log:
            return None
        
        return LockerAccessLogResponse.from_orm(access_log)
    
    async def list_access_logs(
        self,
        locker_id: Optional[UUID] = None,
        allocation_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        access_date_from: Optional[date] = None,
        access_date_to: Optional[date] = None,
        accessor_type: Optional[str] = None,
        purpose: Optional[str] = None,
        emergency_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List access logs with filters"""
        query = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        )
        
        if locker_id:
            query = query.filter(LockerAccessLog.locker_id == locker_id)
        
        if allocation_id:
            query = query.filter(LockerAccessLog.allocation_id == allocation_id)
        
        if customer_id:
            query = query.filter(LockerAccessLog.customer_id == customer_id)
        
        if access_date_from:
            query = query.filter(LockerAccessLog.access_date >= access_date_from)
        
        if access_date_to:
            query = query.filter(LockerAccessLog.access_date <= access_date_to)
        
        if accessor_type:
            query = query.filter(LockerAccessLog.accessor_type == accessor_type)
        
        if purpose:
            query = query.filter(LockerAccessLog.purpose == purpose)
        
        if emergency_only:
            query = query.filter(LockerAccessLog.emergency_access == True)
        
        total = query.count()
        
        access_logs = query.order_by(desc(LockerAccessLog.access_time_in))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return {
            "access_logs": [LockerAccessLogResponse.from_orm(log) for log in access_logs],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    async def get_active_access_sessions(
        self,
        locker_id: Optional[UUID] = None
    ) -> List[LockerAccessLogResponse]:
        """Get currently active access sessions (no exit time recorded)"""
        query = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_time_out.is_(None)
        )
        
        if locker_id:
            query = query.filter(LockerAccessLog.locker_id == locker_id)
        
        access_logs = query.order_by(desc(LockerAccessLog.access_time_in)).all()
        
        return [LockerAccessLogResponse.from_orm(log) for log in access_logs]
    
    async def get_customer_access_history(
        self,
        customer_id: UUID,
        limit: int = 50
    ) -> List[LockerAccessLogResponse]:
        """Get access history for a customer"""
        access_logs = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.customer_id == customer_id,
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False
        ).order_by(desc(LockerAccessLog.access_time_in))\
            .limit(limit)\
            .all()
        
        return [LockerAccessLogResponse.from_orm(log) for log in access_logs]

    
    # ==================== ANALYTICS & REPORTS ====================
    
    async def get_access_statistics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get access statistics"""
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()
        
        query = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to
        )
        
        total_accesses = query.count()
        
        emergency_accesses = query.filter(LockerAccessLog.emergency_access == True).count()
        
        active_sessions = query.filter(LockerAccessLog.access_time_out.is_(None)).count()
        
        # Access by accessor type
        accessor_type_stats = self.db.query(
            LockerAccessLog.accessor_type,
            func.count(LockerAccessLog.id).label('count')
        ).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to
        ).group_by(LockerAccessLog.accessor_type).all()
        
        # Access by purpose
        purpose_stats = self.db.query(
            LockerAccessLog.purpose,
            func.count(LockerAccessLog.id).label('count')
        ).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to
        ).group_by(LockerAccessLog.purpose).all()
        
        # Biometric verification rate
        biometric_verified_count = query.filter(
            LockerAccessLog.biometric_verified == True
        ).count()
        
        biometric_rate = (biometric_verified_count / total_accesses * 100) if total_accesses > 0 else 0
        
        # Average access duration (for completed sessions)
        completed_sessions = query.filter(
            LockerAccessLog.access_time_out.isnot(None)
        ).all()
        
        if completed_sessions:
            total_duration = sum([
                (log.access_time_out - log.access_time_in).total_seconds() / 60
                for log in completed_sessions
            ])
            avg_duration_minutes = total_duration / len(completed_sessions)
        else:
            avg_duration_minutes = 0
        
        return {
            "total_accesses": total_accesses,
            "emergency_accesses": emergency_accesses,
            "active_sessions": active_sessions,
            "accessor_type_breakdown": {stat[0]: stat[1] for stat in accessor_type_stats},
            "purpose_breakdown": {stat[0]: stat[1] for stat in purpose_stats},
            "biometric_verification_rate": round(biometric_rate, 2),
            "average_duration_minutes": round(avg_duration_minutes, 2),
            "date_from": date_from,
            "date_to": date_to
        }
    
    async def get_access_register_report(
        self,
        date_from: date,
        date_to: date,
        locker_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Generate access register report for audit"""
        query = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to
        )
        
        if locker_id:
            query = query.filter(LockerAccessLog.locker_id == locker_id)
        
        access_logs = query.order_by(
            LockerAccessLog.access_date,
            LockerAccessLog.access_time_in
        ).all()
        
        register = []
        for log in access_logs:
            # Calculate duration
            if log.access_time_out:
                duration = (log.access_time_out - log.access_time_in).total_seconds() / 60
            else:
                duration = None
            
            register.append({
                "access_log_number": log.access_log_number,
                "date": log.access_date,
                "locker_number": log.locker.locker_number if log.locker else None,
                "customer_name": log.accessor_name,
                "accessor_type": log.accessor_type,
                "entry_time": log.access_time_in.strftime("%H:%M") if log.access_time_in else None,
                "exit_time": log.access_time_out.strftime("%H:%M") if log.access_time_out else "In Progress",
                "duration_minutes": round(duration, 2) if duration else None,
                "purpose": log.purpose,
                "bank_official": log.witness_1_name or log.witness_2_name,
                "biometric_verified": log.biometric_verified,
                "emergency_access": log.emergency_access
            })
        
        return register
    
    # ==================== HELPER METHODS ====================
    
    async def _generate_access_log_number(self) -> str:
        """Generate unique access log number"""
        today = date.today()
        prefix = f"AL{today.strftime('%Y%m%d')}"
        
        # Get count of today's access logs
        count = self.db.query(func.count(LockerAccessLog.id)).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.access_date == today
        ).scalar()
        
        sequence = count + 1
        return f"{prefix}{sequence:04d}"
    
    async def _is_within_operating_hours(self, access_time: datetime) -> bool:
        """Check if access time is within standard operating hours"""
        # Standard hours: 10 AM - 4 PM on weekdays
        access_hour = access_time.hour
        weekday = access_time.weekday()
        
        # Weekend
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check hours (10 AM to 4 PM = 10 to 16)
        if access_hour < 10 or access_hour >= 16:
            return False
        
        return True
    
    async def _validate_customer_authorization(
        self,
        accessor_type: str,
        accessor_id: str,
        allocation_id: UUID
    ) -> bool:
        """Validate if the accessor is authorized to access the locker"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()
        
        if not allocation:
            return False
        
        # Primary customer
        if accessor_type == 'customer':
            customer = self.db.query(LockerCustomer).filter(
                LockerCustomer.customer_id == allocation.customer_id,
                LockerCustomer.tenant_id == self.tenant_id,
                LockerCustomer.is_deleted == False,
                LockerCustomer.status == 'active'
            ).first()
            return customer is not None
        
        # Joint holder
        elif accessor_type == 'joint_holder':
            joint_holder = self.db.query(LockerJointHolder).filter(
                LockerJointHolder.allocation_id == allocation_id,
                LockerJointHolder.tenant_id == self.tenant_id,
                LockerJointHolder.is_deleted == False,
                LockerJointHolder.status == 'active'
            ).first()
            return joint_holder is not None
        
        # Nominee (requires special authorization)
        elif accessor_type == 'nominee':
            # Nominee access typically requires court order or death certificate
            # This would need additional validation logic
            return True  # Placeholder - implement proper validation
        
        # Bank staff always authorized
        elif accessor_type == 'bank_staff':
            return True
        
        return False

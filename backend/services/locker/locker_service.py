"""
Locker Management Service

Handles all business logic for locker operations including:
- Locker inventory CRUD
- Availability checking
- Allocation lifecycle management
- Rent calculations
- Occupancy analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import LockerMaster, LockerAllocation
from backend.shared.common.response import CustomException


class LockerService:
    """Service for managing locker inventory and operations"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== LOCKER MASTER CRUD ====================
    
    def create_locker(self, locker_data: Dict[str, Any]) -> LockerMaster:
        """
        Create new locker in inventory
        
        Args:
            locker_data: Locker specifications and location
            
        Returns:
            Created locker
        """
        # Check if locker number already exists
        existing = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.locker_number == locker_data.get('locker_number'),
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Locker number {locker_data.get('locker_number')} already exists"
            )
        
        # Validate rent and deposit
        if locker_data.get('security_deposit', 0) < locker_data.get('annual_rent', 0):
            raise CustomException(
                status_code=400,
                message="Security deposit should be at least equal to annual rent"
            )
        
        # Create locker
        locker = LockerMaster(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            **locker_data
        )
        
        self.db.add(locker)
        self.db.commit()
        self.db.refresh(locker)
        
        return locker
    
    def get_locker(self, locker_id: uuid.UUID) -> Optional[LockerMaster]:
        """Get locker by ID"""
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id == locker_id,
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            raise CustomException(status_code=404, message="Locker not found")
        
        return locker
    
    def get_locker_by_number(self, locker_number: str) -> Optional[LockerMaster]:
        """Get locker by locker number"""
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.locker_number == locker_number,
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            raise CustomException(status_code=404, message="Locker not found")
        
        return locker
    
    def list_lockers(
        self,
        locker_size: Optional[str] = None,
        branch_id: Optional[uuid.UUID] = None,
        vault_room: Optional[str] = None,
        status: Optional[str] = None,
        is_available: Optional[bool] = None,
        min_rent: Optional[Decimal] = None,
        max_rent: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LockerMaster]:
        """List lockers with filters"""
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        )
        
        if locker_size:
            query = query.filter(LockerMaster.locker_size == locker_size)
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        if vault_room:
            query = query.filter(LockerMaster.vault_room == vault_room)
        
        if status:
            query = query.filter(LockerMaster.status == status)
        
        if is_available is not None:
            query = query.filter(LockerMaster.is_available == is_available)
        
        if min_rent:
            query = query.filter(LockerMaster.annual_rent >= min_rent)
        
        if max_rent:
            query = query.filter(LockerMaster.annual_rent <= max_rent)
        
        lockers = query.order_by(LockerMaster.locker_number).offset(skip).limit(limit).all()
        return lockers
    
    def update_locker(self, locker_id: uuid.UUID, update_data: Dict[str, Any]) -> LockerMaster:
        """Update locker details"""
        locker = self.get_locker(locker_id)
        
        # Don't allow changing locker number if allocated
        if 'locker_number' in update_data and update_data['locker_number'] != locker.locker_number:
            active_allocation = self.db.query(LockerAllocation).filter(
                and_(
                    LockerAllocation.locker_id == locker_id,
                    LockerAllocation.status == 'active',
                    LockerAllocation.is_deleted == False
                )
            ).first()
            
            if active_allocation:
                raise CustomException(
                    status_code=400,
                    message="Cannot change locker number while locker is allocated"
                )
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(locker, key) and value is not None:
                setattr(locker, key, value)
        
        locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(locker)
        
        return locker
    
    def delete_locker(self, locker_id: uuid.UUID) -> bool:
        """Soft delete locker"""
        locker = self.get_locker(locker_id)
        
        # Check if locker has active allocation
        active_allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.locker_id == locker_id,
                LockerAllocation.status == 'active',
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if active_allocation:
            raise CustomException(
                status_code=400,
                message="Cannot delete locker with active allocation"
            )
        
        locker.is_deleted = True
        locker.is_available = False
        locker.status = 'retired'
        locker.updated_by = self.user_id
        
        self.db.commit()
        return True
    
    # ==================== AVAILABILITY & SEARCH ====================
    
    def check_availability(
        self,
        branch_id: Optional[uuid.UUID] = None,
        locker_size: Optional[str] = None,
        vault_room: Optional[str] = None,
        max_rent: Optional[Decimal] = None
    ) -> List[LockerMaster]:
        """
        Check available lockers matching criteria
        
        Returns:
            List of available lockers
        """
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_available == True,
                LockerMaster.status == 'available',
                LockerMaster.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        if locker_size:
            query = query.filter(LockerMaster.locker_size == locker_size)
        
        if vault_room:
            query = query.filter(LockerMaster.vault_room == vault_room)
        
        if max_rent:
            query = query.filter(LockerMaster.annual_rent <= max_rent)
        
        available = query.order_by(LockerMaster.annual_rent).all()
        return available
    
    def get_floor_plan(
        self,
        branch_id: uuid.UUID,
        vault_room: str
    ) -> Dict[str, Any]:
        """
        Get floor plan layout for a vault room
        
        Returns:
            Dictionary with lockers grouped by floor/rack/position
        """
        lockers = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.branch_id == branch_id,
                LockerMaster.vault_room == vault_room,
                LockerMaster.is_deleted == False
            )
        ).order_by(LockerMaster.floor, LockerMaster.rack_number, LockerMaster.position).all()
        
        # Group by floor and rack
        layout = {}
        for locker in lockers:
            floor = locker.floor or 'Ground'
            rack = locker.rack_number or 'Main'
            
            if floor not in layout:
                layout[floor] = {}
            
            if rack not in layout[floor]:
                layout[floor][rack] = []
            
            layout[floor][rack].append({
                'id': str(locker.id),
                'locker_number': locker.locker_number,
                'size': locker.locker_size,
                'status': locker.status,
                'is_available': locker.is_available,
                'position': locker.position,
                'annual_rent': float(locker.annual_rent)
            })
        
        return layout
    
    def get_occupancy_stats(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get locker occupancy statistics
        
        Returns:
            Occupancy rates and breakdowns
        """
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        # Total counts
        total = query.count()
        available = query.filter(LockerMaster.status == 'available').count()
        allocated = query.filter(LockerMaster.status == 'allocated').count()
        maintenance = query.filter(LockerMaster.status == 'under_maintenance').count()
        blocked = query.filter(LockerMaster.status == 'blocked').count()
        
        # By size
        by_size = {}
        size_counts = query.with_entities(
            LockerMaster.locker_size,
            func.count(LockerMaster.id)
        ).group_by(LockerMaster.locker_size).all()
        
        for size, count in size_counts:
            by_size[size] = count
        
        # By branch
        by_branch = {}
        if not branch_id:
            branch_counts = query.with_entities(
                LockerMaster.branch_name,
                func.count(LockerMaster.id)
            ).group_by(LockerMaster.branch_name).all()
            
            for branch, count in branch_counts:
                by_branch[branch or 'Unknown'] = count
        
        occupancy_rate = (allocated / total * 100) if total > 0 else 0
        
        return {
            'total_lockers': total,
            'available_lockers': available,
            'allocated_lockers': allocated,
            'under_maintenance': maintenance,
            'blocked': blocked,
            'occupancy_rate': round(occupancy_rate, 2),
            'by_size': by_size,
            'by_branch': by_branch
        }
    
    # ==================== MAINTENANCE TRACKING ====================
    
    def get_maintenance_due(
        self,
        days_threshold: int = 30,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lockers due for maintenance
        
        Args:
            days_threshold: Consider lockers due within this many days
            branch_id: Filter by branch
            
        Returns:
            List of lockers needing maintenance
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False,
                or_(
                    LockerMaster.next_maintenance_date <= threshold_date,
                    LockerMaster.next_maintenance_date == None
                )
            )
        )
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        lockers = query.order_by(LockerMaster.next_maintenance_date).all()
        
        result = []
        for locker in lockers:
            days_overdue = 0
            if locker.next_maintenance_date:
                days_overdue = (today - locker.next_maintenance_date).days
            
            result.append({
                'locker_id': str(locker.id),
                'locker_number': locker.locker_number,
                'locker_size': locker.locker_size,
                'location': f"{locker.vault_room} - {locker.floor or ''} - {locker.rack_number or ''}",
                'last_maintenance_date': locker.last_maintenance_date,
                'next_maintenance_date': locker.next_maintenance_date,
                'days_overdue': days_overdue
            })
        
        return result
    
    def update_maintenance_schedule(
        self,
        locker_id: uuid.UUID,
        last_maintenance_date: date,
        frequency_days: Optional[int] = None
    ) -> LockerMaster:
        """
        Update locker maintenance schedule
        
        Args:
            locker_id: Locker to update
            last_maintenance_date: Date of last maintenance
            frequency_days: Maintenance frequency (uses existing if not provided)
            
        Returns:
            Updated locker
        """
        locker = self.get_locker(locker_id)
        
        locker.last_maintenance_date = last_maintenance_date
        
        if frequency_days:
            locker.maintenance_frequency_days = frequency_days
        
        # Calculate next maintenance date
        locker.next_maintenance_date = last_maintenance_date + timedelta(
            days=locker.maintenance_frequency_days
        )
        
        locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(locker)
        
        return locker
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_create_lockers(
        self,
        lockers_data: List[Dict[str, Any]]
    ) -> List[LockerMaster]:
        """
        Create multiple lockers at once
        
        Args:
            lockers_data: List of locker specifications
            
        Returns:
            List of created lockers
        """
        created_lockers = []
        
        for locker_data in lockers_data:
            try:
                locker = self.create_locker(locker_data)
                created_lockers.append(locker)
            except CustomException as e:
                # Skip duplicates and continue
                if "already exists" not in str(e):
                    raise
        
        return created_lockers
    
    def bulk_update_status(
        self,
        locker_ids: List[uuid.UUID],
        status: str,
        is_available: Optional[bool] = None
    ) -> int:
        """
        Update status for multiple lockers
        
        Args:
            locker_ids: List of locker IDs
            status: New status
            is_available: New availability flag
            
        Returns:
            Number of lockers updated
        """
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id.in_(locker_ids),
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        )
        
        update_data = {'status': status, 'updated_by': self.user_id}
        if is_available is not None:
            update_data['is_available'] = is_available
        
        count = query.update(update_data, synchronize_session=False)
        self.db.commit()
        
        return count
    
    # ==================== REPORTING ====================
    
    def get_inventory_report(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive inventory report
        
        Returns:
            Detailed breakdown of locker inventory
        """
        query = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        lockers = query.all()
        
        # Calculate totals
        total_count = len(lockers)
        total_annual_rent = sum(float(l.annual_rent) for l in lockers)
        total_security_deposit = sum(float(l.security_deposit) for l in lockers)
        
        # By size breakdown
        by_size = {}
        for locker in lockers:
            size = locker.locker_size
            if size not in by_size:
                by_size[size] = {
                    'count': 0,
                    'available': 0,
                    'allocated': 0,
                    'total_rent': 0
                }
            
            by_size[size]['count'] += 1
            by_size[size]['total_rent'] += float(locker.annual_rent)
            
            if locker.status == 'available':
                by_size[size]['available'] += 1
            elif locker.status == 'allocated':
                by_size[size]['allocated'] += 1
        
        # By status breakdown
        by_status = {}
        status_counts = query.with_entities(
            LockerMaster.status,
            func.count(LockerMaster.id)
        ).group_by(LockerMaster.status).all()
        
        for status, count in status_counts:
            by_status[status] = count
        
        return {
            'total_count': total_count,
            'total_annual_rent': total_annual_rent,
            'total_security_deposit': total_security_deposit,
            'average_rent': total_annual_rent / total_count if total_count > 0 else 0,
            'by_size': by_size,
            'by_status': by_status
        }

"""
Locker Maintenance Service

Handles both preventive and breakdown maintenance for locker facilities.
Includes lock servicing, key duplication, cleaning, repairs, and annual maintenance schedules.
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from backend.shared.database.models import (
    LockerMaintenance,
    LockerMaster,
    LockerAllocation,
    MaintenanceType,
    MaintenanceStatus,
    MaintenancePriority,
)


class LockerMaintenanceService:
    """Service for locker maintenance operations"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== PREVENTIVE MAINTENANCE ====================
    
    async def schedule_preventive_maintenance(self, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Schedule preventive maintenance for a locker
        
        Args:
            data: Maintenance details including locker_id, maintenance_type, scheduled_date
        
        Returns:
            LockerMaintenance: Created maintenance record
        """
        maintenance = LockerMaintenance(
            maintenance_id=str(uuid.uuid4()),
            maintenance_number=self._generate_maintenance_number(),
            tenant_id=self.tenant_id,
            locker_id=data['locker_id'],
            branch_id=data.get('branch_id'),
            
            # Type and category
            maintenance_type=data['maintenance_type'],  # lock_servicing, cleaning, etc.
            maintenance_category='preventive',
            
            # Scheduling
            scheduled_date=data['scheduled_date'],
            scheduled_time=data.get('scheduled_time'),
            frequency=data.get('frequency', 'annual'),  # monthly, quarterly, semi_annual, annual
            is_recurring=data.get('is_recurring', True),
            next_due_date=self._calculate_next_due_date(
                data['scheduled_date'], 
                data.get('frequency', 'annual')
            ),
            
            # Details
            description=data.get('description'),
            maintenance_checklist=data.get('maintenance_checklist', []),
            estimated_duration_minutes=data.get('estimated_duration_minutes', 60),
            estimated_cost=Decimal(data.get('estimated_cost', 0)),
            
            # Assignment
            assigned_to=data.get('assigned_to'),
            assigned_by=self.user_id,
            assignment_date=datetime.utcnow(),
            
            # Status
            status=MaintenanceStatus.SCHEDULED,
            priority=MaintenancePriority.MEDIUM,
            
            # Tracking
            created_by=self.user_id,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)
        
        # Update locker's next maintenance date
        self._update_locker_maintenance_date(
            data['locker_id'], 
            maintenance.next_due_date
        )
        
        return maintenance

    async def perform_lock_servicing(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Perform lock servicing maintenance
        
        Args:
            maintenance_id: Maintenance record ID
            data: Servicing details (lock_condition, lubrication_done, parts_replaced, etc.)
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.actual_start_time = data.get('actual_start_time')
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Lock servicing details
        maintenance.work_performed = {
            'lock_condition_before': data.get('lock_condition_before'),
            'lubrication_done': data.get('lubrication_done', True),
            'parts_replaced': data.get('parts_replaced', []),
            'lock_tested': data.get('lock_tested', True),
            'lock_condition_after': data.get('lock_condition_after'),
            'servicing_notes': data.get('servicing_notes'),
        }
        
        maintenance.parts_used = data.get('parts_used', [])
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def perform_key_duplication(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Perform spare key duplication
        
        Args:
            maintenance_id: Maintenance record ID
            data: Key duplication details (number_of_keys, key_type, etc.)
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Key duplication details
        maintenance.work_performed = {
            'number_of_keys_duplicated': data.get('number_of_keys_duplicated', 1),
            'key_type': data.get('key_type', 'spare'),  # spare, master, duplicate
            'key_numbers': data.get('key_numbers', []),
            'tested_successfully': data.get('tested_successfully', True),
            'storage_location': data.get('storage_location'),
            'duplication_notes': data.get('duplication_notes'),
        }
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def perform_locker_cleaning(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Perform locker cleaning maintenance
        
        Args:
            maintenance_id: Maintenance record ID
            data: Cleaning details (cleaning_type, areas_cleaned, etc.)
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Cleaning details
        maintenance.work_performed = {
            'cleaning_type': data.get('cleaning_type', 'regular'),  # regular, deep, sanitization
            'areas_cleaned': data.get('areas_cleaned', [
                'locker_interior',
                'locker_exterior',
                'lock_mechanism',
                'door_hinges'
            ]),
            'cleaning_materials_used': data.get('cleaning_materials_used', []),
            'condition_before': data.get('condition_before'),
            'condition_after': data.get('condition_after'),
            'sanitization_done': data.get('sanitization_done', False),
            'cleaning_notes': data.get('cleaning_notes'),
        }
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance

    async def perform_vault_maintenance(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Perform vault room maintenance
        
        Args:
            maintenance_id: Maintenance record ID
            data: Vault maintenance details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Vault maintenance details
        maintenance.work_performed = {
            'humidity_check': data.get('humidity_check', {}),
            'dehumidifier_servicing': data.get('dehumidifier_servicing', {}),
            'fire_protection_check': data.get('fire_protection_check', {}),
            'ventilation_check': data.get('ventilation_check', {}),
            'lighting_check': data.get('lighting_check', {}),
            'structural_inspection': data.get('structural_inspection', {}),
            'door_mechanism_check': data.get('door_mechanism_check', {}),
            'time_lock_check': data.get('time_lock_check', {}),
            'issues_found': data.get('issues_found', []),
            'corrective_actions': data.get('corrective_actions', []),
            'vault_notes': data.get('vault_notes'),
        }
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def check_fire_protection_system(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Check fire protection system
        
        Args:
            maintenance_id: Maintenance record ID
            data: Fire system check details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Fire protection system check
        maintenance.work_performed = {
            'fire_extinguisher_check': data.get('fire_extinguisher_check', {}),
            'smoke_detector_test': data.get('smoke_detector_test', {}),
            'sprinkler_system_check': data.get('sprinkler_system_check', {}),
            'fire_alarm_test': data.get('fire_alarm_test', {}),
            'emergency_exit_check': data.get('emergency_exit_check', {}),
            'fire_safety_signage': data.get('fire_safety_signage', {}),
            'compliance_status': data.get('compliance_status', 'compliant'),
            'deficiencies_found': data.get('deficiencies_found', []),
            'recommendations': data.get('recommendations', []),
            'fire_system_notes': data.get('fire_system_notes'),
        }
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    # ==================== BREAKDOWN MAINTENANCE ====================
    
    async def report_breakdown(self, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Report breakdown/emergency maintenance
        
        Args:
            data: Breakdown details including issue_type, description, priority
        
        Returns:
            Created maintenance record
        """
        maintenance = LockerMaintenance(
            maintenance_id=str(uuid.uuid4()),
            maintenance_number=self._generate_maintenance_number(),
            tenant_id=self.tenant_id,
            locker_id=data['locker_id'],
            branch_id=data.get('branch_id'),
            allocation_id=data.get('allocation_id'),
            
            # Type and category
            maintenance_type=data['issue_type'],  # lock_jamming, key_lost, lock_replacement, etc.
            maintenance_category='breakdown',
            
            # Issue details
            issue_reported_date=datetime.utcnow(),
            issue_reported_by=data.get('reported_by', self.user_id),
            issue_description=data['description'],
            issue_severity=data.get('severity', 'medium'),  # low, medium, high, critical
            
            # Priority based on severity
            priority=self._determine_priority(data.get('severity', 'medium')),
            
            # Customer impact
            customer_id=data.get('customer_id'),
            customer_notified=data.get('customer_notified', False),
            locker_accessible=data.get('locker_accessible', False),
            
            # Status
            status=MaintenanceStatus.REPORTED,
            
            # Charges
            is_customer_fault=data.get('is_customer_fault', False),
            estimated_cost=Decimal(data.get('estimated_cost', 0)),
            
            # Tracking
            created_by=self.user_id,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)
        
        # If critical, send immediate alerts
        if data.get('severity') == 'critical':
            await self._send_critical_alert(maintenance)
        
        return maintenance

    async def resolve_lock_jamming(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Resolve lock jamming issue
        
        Args:
            maintenance_id: Maintenance record ID
            data: Resolution details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Lock jamming resolution
        maintenance.work_performed = {
            'jamming_cause': data.get('jamming_cause'),  # debris, rust, misalignment, wear
            'resolution_method': data.get('resolution_method'),  # lubrication, adjustment, replacement
            'parts_replaced': data.get('parts_replaced', []),
            'lock_tested': data.get('lock_tested', True),
            'test_count': data.get('test_count', 5),
            'works_smoothly': data.get('works_smoothly', True),
            'customer_accessible': data.get('customer_accessible', True),
            'resolution_notes': data.get('resolution_notes'),
        }
        
        maintenance.locker_accessible = data.get('customer_accessible', True)
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def handle_lost_key(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Handle lost key situation
        
        Args:
            maintenance_id: Maintenance record ID
            data: Lost key handling details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Lost key handling
        maintenance.work_performed = {
            'key_type_lost': data.get('key_type_lost', 'customer'),  # customer, bank_master
            'fir_filed': data.get('fir_filed', False),
            'fir_number': data.get('fir_number'),
            'fir_date': data.get('fir_date'),
            'police_station': data.get('police_station'),
            'indemnity_bond_executed': data.get('indemnity_bond_executed', False),
            'indemnity_bond_path': data.get('indemnity_bond_path'),
            'action_taken': data.get('action_taken'),  # duplicate_key, lock_change, locker_breaking
            'new_key_issued': data.get('new_key_issued', False),
            'new_key_number': data.get('new_key_number'),
            'lock_changed': data.get('lock_changed', False),
            'customer_charges_applicable': data.get('customer_charges_applicable', True),
            'lost_key_notes': data.get('lost_key_notes'),
        }
        
        maintenance.is_customer_fault = True
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        maintenance.customer_charges = Decimal(data.get('customer_charges', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def replace_lock(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Replace locker lock
        
        Args:
            maintenance_id: Maintenance record ID
            data: Lock replacement details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Lock replacement details
        maintenance.work_performed = {
            'replacement_reason': data.get('replacement_reason'),
            'old_lock_type': data.get('old_lock_type'),
            'old_lock_serial_number': data.get('old_lock_serial_number'),
            'new_lock_type': data.get('new_lock_type'),
            'new_lock_serial_number': data.get('new_lock_serial_number'),
            'new_lock_manufacturer': data.get('new_lock_manufacturer'),
            'keys_issued': data.get('keys_issued', 2),
            'customer_key_numbers': data.get('customer_key_numbers', []),
            'master_key_number': data.get('master_key_number'),
            'lock_tested': data.get('lock_tested', True),
            'test_results': data.get('test_results'),
            'old_lock_disposed': data.get('old_lock_disposed', True),
            'disposal_date': data.get('disposal_date'),
            'replacement_notes': data.get('replacement_notes'),
        }
        
        maintenance.parts_used = [{
            'part_name': 'Lock Assembly',
            'part_number': data.get('new_lock_serial_number'),
            'quantity': 1,
            'cost': data.get('lock_cost', 0)
        }]
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance

    async def regenerate_master_key(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Regenerate master key for locker
        
        Args:
            maintenance_id: Maintenance record ID
            data: Master key regeneration details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Master key regeneration
        maintenance.work_performed = {
            'regeneration_reason': data.get('regeneration_reason'),
            'old_master_key_number': data.get('old_master_key_number'),
            'new_master_key_number': data.get('new_master_key_number'),
            'authorization_by': data.get('authorization_by'),  # Requires senior approval
            'authorization_date': data.get('authorization_date'),
            'keys_generated': data.get('keys_generated', 1),
            'storage_location': data.get('storage_location'),
            'custodian_assigned': data.get('custodian_assigned'),
            'old_key_destroyed': data.get('old_key_destroyed', True),
            'destruction_date': data.get('destruction_date'),
            'destruction_witnessed_by': data.get('destruction_witnessed_by', []),
            'regeneration_notes': data.get('regeneration_notes'),
        }
        
        maintenance.requires_approval = True
        maintenance.approved_by = data.get('authorization_by')
        maintenance.approval_date = data.get('authorization_date')
        
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    async def repair_locker(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Perform general locker repair
        
        Args:
            maintenance_id: Maintenance record ID
            data: Repair details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_start_date = data.get('actual_start_date', datetime.utcnow())
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        
        # Repair details
        maintenance.work_performed = {
            'repair_type': data.get('repair_type'),  # structural, cosmetic, functional
            'damage_description': data.get('damage_description'),
            'damage_cause': data.get('damage_cause'),
            'repair_method': data.get('repair_method'),
            'materials_used': data.get('materials_used', []),
            'parts_replaced': data.get('parts_replaced', []),
            'before_photos': data.get('before_photos', []),
            'after_photos': data.get('after_photos', []),
            'quality_check': data.get('quality_check', {}),
            'warranty_applicable': data.get('warranty_applicable', False),
            'warranty_period_days': data.get('warranty_period_days', 0),
            'repair_notes': data.get('repair_notes'),
        }
        
        maintenance.parts_used = data.get('parts_used', [])
        maintenance.actual_cost = Decimal(data.get('actual_cost', 0))
        
        # Determine if customer should be charged
        if data.get('damage_cause') == 'customer_fault':
            maintenance.is_customer_fault = True
            maintenance.customer_charges = Decimal(data.get('customer_charges', 0))
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        return maintenance
    
    # ==================== MAINTENANCE COMPLETION ====================
    
    async def complete_maintenance(self, maintenance_id: str, data: Dict[str, Any]) -> LockerMaintenance:
        """
        Complete maintenance work
        
        Args:
            maintenance_id: Maintenance record ID
            data: Completion details
        
        Returns:
            Updated maintenance record
        """
        maintenance = self._get_maintenance(maintenance_id)
        
        maintenance.actual_completion_date = data.get('actual_completion_date', datetime.utcnow())
        maintenance.actual_completion_time = data.get('actual_completion_time')
        
        # Calculate actual duration
        if maintenance.actual_start_date and maintenance.actual_completion_date:
            duration = (maintenance.actual_completion_date - maintenance.actual_start_date)
            maintenance.actual_duration_minutes = int(duration.total_seconds() / 60)
        
        # Completion details
        maintenance.completion_notes = data.get('completion_notes')
        maintenance.quality_check_done = data.get('quality_check_done', True)
        maintenance.quality_check_by = data.get('quality_check_by')
        maintenance.quality_check_remarks = data.get('quality_check_remarks')
        maintenance.customer_satisfaction_rating = data.get('customer_satisfaction_rating')
        
        # Final costs
        if 'actual_cost' in data:
            maintenance.actual_cost = Decimal(data['actual_cost'])
        
        if maintenance.is_customer_fault and 'customer_charges' in data:
            maintenance.customer_charges = Decimal(data['customer_charges'])
            maintenance.customer_charges_collected = data.get('customer_charges_collected', False)
            maintenance.payment_receipt_number = data.get('payment_receipt_number')
        
        # Status
        maintenance.status = MaintenanceStatus.COMPLETED
        maintenance.completed_by = self.user_id
        
        # If recurring, schedule next maintenance
        if maintenance.is_recurring and maintenance.next_due_date:
            await self._auto_schedule_next_maintenance(maintenance)
        
        self.db.commit()
        self.db.refresh(maintenance)
        
        # Update locker status if it was under maintenance
        await self._update_locker_status_after_maintenance(maintenance.locker_id)
        
        # Notify customer if applicable
        if maintenance.customer_id:
            await self._notify_customer_maintenance_completed(maintenance)
        
        return maintenance

    # ==================== MAINTENANCE QUERIES ====================
    
    async def get_maintenance_record(self, maintenance_id: str) -> Optional[LockerMaintenance]:
        """Get maintenance record by ID"""
        return self.db.query(LockerMaintenance).filter(
            LockerMaintenance.maintenance_id == maintenance_id,
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        ).first()
    
    async def get_maintenance_by_locker(self, locker_id: str) -> List[LockerMaintenance]:
        """Get all maintenance records for a locker"""
        return self.db.query(LockerMaintenance).filter(
            LockerMaintenance.locker_id == locker_id,
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        ).order_by(LockerMaintenance.created_at.desc()).all()
    
    async def list_maintenance_records(
        self,
        branch_id: Optional[str] = None,
        maintenance_type: Optional[str] = None,
        maintenance_category: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List maintenance records with filters"""
        query = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        )
        
        if branch_id:
            query = query.filter(LockerMaintenance.branch_id == branch_id)
        
        if maintenance_type:
            query = query.filter(LockerMaintenance.maintenance_type == maintenance_type)
        
        if maintenance_category:
            query = query.filter(LockerMaintenance.maintenance_category == maintenance_category)
        
        if status:
            query = query.filter(LockerMaintenance.status == status)
        
        if priority:
            query = query.filter(LockerMaintenance.priority == priority)
        
        if date_from:
            query = query.filter(LockerMaintenance.scheduled_date >= date_from)
        
        if date_to:
            query = query.filter(LockerMaintenance.scheduled_date <= date_to)
        
        total = query.count()
        records = query.order_by(
            LockerMaintenance.scheduled_date.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            'records': records,
            'total': total,
            'skip': skip,
            'limit': limit
        }
    
    async def get_upcoming_maintenance(
        self, 
        days_ahead: int = 30,
        branch_id: Optional[str] = None
    ) -> List[LockerMaintenance]:
        """Get upcoming scheduled maintenance"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        query = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False,
            LockerMaintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.PENDING]),
            LockerMaintenance.scheduled_date <= end_date,
            LockerMaintenance.scheduled_date >= date.today()
        )
        
        if branch_id:
            query = query.filter(LockerMaintenance.branch_id == branch_id)
        
        return query.order_by(LockerMaintenance.scheduled_date).all()
    
    async def get_overdue_maintenance(
        self, 
        branch_id: Optional[str] = None
    ) -> List[LockerMaintenance]:
        """Get overdue maintenance records"""
        query = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False,
            LockerMaintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.PENDING]),
            LockerMaintenance.scheduled_date < date.today()
        )
        
        if branch_id:
            query = query.filter(LockerMaintenance.branch_id == branch_id)
        
        return query.order_by(LockerMaintenance.scheduled_date).all()
    
    async def get_pending_breakdowns(
        self, 
        branch_id: Optional[str] = None
    ) -> List[LockerMaintenance]:
        """Get pending breakdown maintenance"""
        query = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False,
            LockerMaintenance.maintenance_category == 'breakdown',
            LockerMaintenance.status.in_([
                MaintenanceStatus.REPORTED,
                MaintenanceStatus.ASSIGNED,
                MaintenanceStatus.IN_PROGRESS
            ])
        )
        
        if branch_id:
            query = query.filter(LockerMaintenance.branch_id == branch_id)
        
        return query.order_by(
            LockerMaintenance.priority.desc(),
            LockerMaintenance.issue_reported_date
        ).all()
    
    # ==================== MAINTENANCE ANALYTICS ====================
    
    async def get_maintenance_statistics(
        self,
        branch_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get maintenance statistics"""
        query = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        )
        
        if branch_id:
            query = query.filter(LockerMaintenance.branch_id == branch_id)
        
        if date_from:
            query = query.filter(LockerMaintenance.created_at >= date_from)
        
        if date_to:
            query = query.filter(LockerMaintenance.created_at <= date_to)
        
        # Total counts
        total_maintenance = query.count()
        
        # By category
        preventive = query.filter(
            LockerMaintenance.maintenance_category == 'preventive'
        ).count()
        breakdown = query.filter(
            LockerMaintenance.maintenance_category == 'breakdown'
        ).count()
        
        # By status
        scheduled = query.filter(LockerMaintenance.status == MaintenanceStatus.SCHEDULED).count()
        in_progress = query.filter(LockerMaintenance.status == MaintenanceStatus.IN_PROGRESS).count()
        completed = query.filter(LockerMaintenance.status == MaintenanceStatus.COMPLETED).count()
        overdue = query.filter(
            LockerMaintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.PENDING]),
            LockerMaintenance.scheduled_date < date.today()
        ).count()
        
        # By type
        by_type = self.db.query(
            LockerMaintenance.maintenance_type,
            func.count(LockerMaintenance.id)
        ).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        ).group_by(LockerMaintenance.maintenance_type).all()
        
        # Cost analysis
        total_cost = query.filter(
            LockerMaintenance.status == MaintenanceStatus.COMPLETED
        ).with_entities(func.sum(LockerMaintenance.actual_cost)).scalar() or 0
        
        customer_charges = query.filter(
            LockerMaintenance.status == MaintenanceStatus.COMPLETED,
            LockerMaintenance.is_customer_fault == True
        ).with_entities(func.sum(LockerMaintenance.customer_charges)).scalar() or 0
        
        # Average response time for breakdowns
        avg_response = self.db.query(
            func.avg(
                func.extract('epoch', LockerMaintenance.actual_start_date - LockerMaintenance.issue_reported_date)
            )
        ).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.maintenance_category == 'breakdown',
            LockerMaintenance.actual_start_date.isnot(None)
        ).scalar()
        
        return {
            'total_maintenance': total_maintenance,
            'preventive_count': preventive,
            'breakdown_count': breakdown,
            'scheduled_count': scheduled,
            'in_progress_count': in_progress,
            'completed_count': completed,
            'overdue_count': overdue,
            'by_type': dict(by_type),
            'total_cost': float(total_cost),
            'customer_charges_collected': float(customer_charges),
            'avg_response_time_hours': float(avg_response / 3600) if avg_response else 0,
        }
    
    # ==================== HELPER METHODS ====================
    
    def _get_maintenance(self, maintenance_id: str) -> LockerMaintenance:
        """Get maintenance record or raise exception"""
        maintenance = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.maintenance_id == maintenance_id,
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.is_deleted == False
        ).first()
        
        if not maintenance:
            raise ValueError(f"Maintenance record {maintenance_id} not found")
        
        return maintenance
    
    def _generate_maintenance_number(self) -> str:
        """Generate unique maintenance number"""
        date_prefix = datetime.utcnow().strftime('%Y%m%d')
        count = self.db.query(LockerMaintenance).filter(
            LockerMaintenance.tenant_id == self.tenant_id,
            LockerMaintenance.maintenance_number.like(f'MAINT-{date_prefix}-%')
        ).count()
        return f"MAINT-{date_prefix}-{count + 1:04d}"
    
    def _calculate_next_due_date(self, scheduled_date: date, frequency: str) -> date:
        """Calculate next due date based on frequency"""
        frequency_days = {
            'weekly': 7,
            'bi_weekly': 14,
            'monthly': 30,
            'quarterly': 90,
            'semi_annual': 180,
            'annual': 365,
        }
        days = frequency_days.get(frequency, 365)
        return scheduled_date + timedelta(days=days)
    
    def _determine_priority(self, severity: str) -> str:
        """Determine priority based on severity"""
        priority_map = {
            'low': MaintenancePriority.LOW,
            'medium': MaintenancePriority.MEDIUM,
            'high': MaintenancePriority.HIGH,
            'critical': MaintenancePriority.CRITICAL
        }
        return priority_map.get(severity, MaintenancePriority.MEDIUM)
    
    def _update_locker_maintenance_date(self, locker_id: str, next_date: date):
        """Update locker's next maintenance date"""
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.locker_id == locker_id,
            LockerMaster.tenant_id == self.tenant_id
        ).first()
        
        if locker:
            locker.next_maintenance_date = next_date
            locker.updated_at = datetime.utcnow()
            locker.updated_by = self.user_id
            self.db.commit()
    
    async def _auto_schedule_next_maintenance(self, maintenance: LockerMaintenance):
        """Auto-schedule next recurring maintenance"""
        if not maintenance.is_recurring or not maintenance.next_due_date:
            return
        
        next_maintenance = LockerMaintenance(
            maintenance_id=str(uuid.uuid4()),
            maintenance_number=self._generate_maintenance_number(),
            tenant_id=self.tenant_id,
            locker_id=maintenance.locker_id,
            branch_id=maintenance.branch_id,
            maintenance_type=maintenance.maintenance_type,
            maintenance_category='preventive',
            scheduled_date=maintenance.next_due_date,
            frequency=maintenance.frequency,
            is_recurring=True,
            next_due_date=self._calculate_next_due_date(
                maintenance.next_due_date,
                maintenance.frequency
            ),
            description=f"Recurring {maintenance.maintenance_type}",
            maintenance_checklist=maintenance.maintenance_checklist,
            estimated_duration_minutes=maintenance.estimated_duration_minutes,
            estimated_cost=maintenance.estimated_cost,
            status=MaintenanceStatus.SCHEDULED,
            priority=MaintenancePriority.MEDIUM,
            created_by=self.user_id,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(next_maintenance)
        self.db.commit()
    
    async def _update_locker_status_after_maintenance(self, locker_id: str):
        """Update locker status after maintenance completion"""
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.locker_id == locker_id,
            LockerMaster.tenant_id == self.tenant_id
        ).first()
        
        if locker and locker.status == 'under_maintenance':
            locker.status = 'available' if not locker.allocation_id else 'allocated'
            locker.last_maintenance_date = date.today()
            locker.updated_at = datetime.utcnow()
            locker.updated_by = self.user_id
            self.db.commit()
    
    async def _send_critical_alert(self, maintenance: LockerMaintenance):
        """Send critical maintenance alert"""
        # Implementation for sending alerts (SMS, email, push notification)
        pass
    
    async def _notify_customer_maintenance_completed(self, maintenance: LockerMaintenance):
        """Notify customer that maintenance is completed"""
        # Implementation for customer notification
        pass

"""
Housekeeping Management Service
Handles housekeeping tasks, schedules, and supplies management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date, timedelta

from backend.shared.database.facility_models import (
    HousekeepingTask, HousekeepingSupply,
    HousekeepingTaskTypeEnum, TaskStatusEnum, TaskPriorityEnum
)
from backend.shared.exceptions import NotFoundError, ValidationError


class HousekeepingService:
    """Service for housekeeping operations"""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        tenant_id: str,
        task_data: Dict[str, Any],
        user_id: int
    ) -> HousekeepingTask:
        """Create a new housekeeping task"""
        
        # Generate task code
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(HousekeepingTask).where(
            HousekeepingTask.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        task_code = f"HK{date_str}{count:04d}"
        
        task = HousekeepingTask(
            tenant_id=tenant_id,
            task_code=task_code,
            created_by=user_id,
            **task_data
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return task
    
    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        building_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> tuple[List[HousekeepingTask], int]:
        """List housekeeping tasks with filters"""
        
        query = select(HousekeepingTask).where(
            and_(
                HousekeepingTask.tenant_id == tenant_id,
                HousekeepingTask.is_deleted == False
            )
        )
        
        if status:
            query = query.where(HousekeepingTask.status == status)
        
        if priority:
            query = query.where(HousekeepingTask.priority == priority)
        
        if assigned_to:
            query = query.where(HousekeepingTask.assigned_to_employee_id == assigned_to)
        
        if building_id:
            query = query.where(HousekeepingTask.building_id == building_id)
        
        if from_date:
            query = query.where(HousekeepingTask.scheduled_date >= from_date)
        
        if to_date:
            query = query.where(HousekeepingTask.scheduled_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(
            HousekeepingTask.scheduled_date.desc(),
            HousekeepingTask.priority
        )
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return tasks, total_count
    
    @staticmethod
    async def update_task_status(
        db: AsyncSession,
        tenant_id: str,
        task_id: int,
        status: TaskStatusEnum,
        user_id: int,
        remarks: Optional[str] = None
    ) -> HousekeepingTask:
        """Update task status"""
        
        stmt = select(HousekeepingTask).where(
            and_(
                HousekeepingTask.tenant_id == tenant_id,
                HousekeepingTask.id == task_id,
                HousekeepingTask.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise NotFoundError(f"Task with ID {task_id} not found")
        
        task.status = status
        task.updated_by = user_id
        task.updated_at = datetime.utcnow()
        
        if status == TaskStatusEnum.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        
        if status == TaskStatusEnum.COMPLETED:
            task.completed_at = datetime.utcnow()
            if task.started_at:
                duration = (task.completed_at - task.started_at).total_seconds() / 60
                task.actual_duration_minutes = int(duration)
        
        if remarks:
            task.remarks = remarks
        
        await db.commit()
        await db.refresh(task)
        
        return task
    
    @staticmethod
    async def assign_task(
        db: AsyncSession,
        tenant_id: str,
        task_id: int,
        employee_id: int,
        user_id: int
    ) -> HousekeepingTask:
        """Assign task to an employee"""
        
        stmt = select(HousekeepingTask).where(
            and_(
                HousekeepingTask.tenant_id == tenant_id,
                HousekeepingTask.id == task_id,
                HousekeepingTask.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise NotFoundError(f"Task with ID {task_id} not found")
        
        task.assigned_to_employee_id = employee_id
        task.assigned_at = datetime.utcnow()
        task.updated_by = user_id
        task.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        
        return task
    
    # ============================================================================
    # SUPPLY MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_supply(
        db: AsyncSession,
        tenant_id: str,
        supply_data: Dict[str, Any],
        user_id: int
    ) -> HousekeepingSupply:
        """Create a new supply item"""
        
        supply = HousekeepingSupply(
            tenant_id=tenant_id,
            created_by=user_id,
            **supply_data
        )
        
        db.add(supply)
        await db.commit()
        await db.refresh(supply)
        
        return supply
    
    @staticmethod
    async def update_stock(
        db: AsyncSession,
        tenant_id: str,
        supply_id: int,
        quantity_change: float,
        user_id: int
    ) -> HousekeepingSupply:
        """Update supply stock"""
        
        stmt = select(HousekeepingSupply).where(
            and_(
                HousekeepingSupply.tenant_id == tenant_id,
                HousekeepingSupply.id == supply_id,
                HousekeepingSupply.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        supply = result.scalar_one_or_none()
        
        if not supply:
            raise NotFoundError(f"Supply with ID {supply_id} not found")
        
        supply.current_stock += quantity_change
        supply.updated_by = user_id
        supply.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(supply)
        
        return supply
    
    @staticmethod
    async def get_low_stock_items(
        db: AsyncSession,
        tenant_id: str
    ) -> List[HousekeepingSupply]:
        """Get supplies below minimum stock level"""
        
        stmt = select(HousekeepingSupply).where(
            and_(
                HousekeepingSupply.tenant_id == tenant_id,
                HousekeepingSupply.current_stock <= HousekeepingSupply.minimum_stock,
                HousekeepingSupply.is_active == True,
                HousekeepingSupply.is_deleted == False
            )
        )
        
        result = await db.execute(stmt)
        return result.scalars().all()

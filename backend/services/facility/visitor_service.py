"""
Visitor Management Service
Handles visitor registration, check-in/out, and visitor passes
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date, time

from backend.shared.database.facility_models import (
    Visitor, VisitorGroup,
    VisitorTypeEnum, VisitPurposeEnum, VisitStatusEnum
)
from backend.shared.exceptions import NotFoundError, ValidationError


class VisitorService:
    """Service for visitor management operations"""
    
    @staticmethod
    async def create_visitor(
        db: AsyncSession,
        tenant_id: str,
        visitor_data: Dict[str, Any],
        user_id: int
    ) -> Visitor:
        """Create a new visitor entry"""
        
        # Generate visitor pass number
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(Visitor).where(
            Visitor.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        visitor_pass_number = f"VIS{date_str}{count:05d}"
        
        visitor = Visitor(
            tenant_id=tenant_id,
            visitor_pass_number=visitor_pass_number,
            created_by=user_id,
            **visitor_data
        )
        
        db.add(visitor)
        await db.commit()
        await db.refresh(visitor)
        
        return visitor
    
    @staticmethod
    async def list_visitors(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        visitor_type: Optional[str] = None,
        status: Optional[str] = None,
        host_employee_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None
    ) -> tuple[List[Visitor], int]:
        """List visitors with filters"""
        
        query = select(Visitor).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.is_deleted == False
            )
        )
        
        if visitor_type:
            query = query.where(Visitor.visitor_type == visitor_type)
        
        if status:
            query = query.where(Visitor.status == status)
        
        if host_employee_id:
            query = query.where(Visitor.host_employee_id == host_employee_id)
        
        if from_date:
            query = query.where(Visitor.visit_date >= from_date)
        
        if to_date:
            query = query.where(Visitor.visit_date <= to_date)
        
        if search:
            query = query.where(
                or_(
                    Visitor.visitor_name.ilike(f"%{search}%"),
                    Visitor.company_name.ilike(f"%{search}%"),
                    Visitor.mobile_number.ilike(f"%{search}%"),
                    Visitor.visitor_pass_number.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(
            Visitor.visit_date.desc(),
            Visitor.created_at.desc()
        )
        
        result = await db.execute(query)
        visitors = result.scalars().all()
        
        return visitors, total_count
    
    @staticmethod
    async def get_visitor(
        db: AsyncSession,
        tenant_id: str,
        visitor_id: int
    ) -> Visitor:
        """Get visitor by ID"""
        stmt = select(Visitor).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.id == visitor_id,
                Visitor.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        visitor = result.scalar_one_or_none()
        
        if not visitor:
            raise NotFoundError(f"Visitor with ID {visitor_id} not found")
        
        return visitor
    
    @staticmethod
    async def check_in_visitor(
        db: AsyncSession,
        tenant_id: str,
        visitor_id: int,
        badge_number: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Visitor:
        """Check in a visitor"""
        
        visitor = await VisitorService.get_visitor(db, tenant_id, visitor_id)
        
        if visitor.status == VisitStatusEnum.CHECKED_IN:
            raise ValidationError("Visitor is already checked in")
        
        visitor.status = VisitStatusEnum.CHECKED_IN
        visitor.check_in_time = datetime.utcnow()
        
        if badge_number:
            visitor.badge_number = badge_number
            visitor.badge_issued_by = user_id
        
        visitor.updated_by = user_id
        visitor.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(visitor)
        
        return visitor
    
    @staticmethod
    async def check_out_visitor(
        db: AsyncSession,
        tenant_id: str,
        visitor_id: int,
        user_id: Optional[int] = None
    ) -> Visitor:
        """Check out a visitor"""
        
        visitor = await VisitorService.get_visitor(db, tenant_id, visitor_id)
        
        if visitor.status != VisitStatusEnum.CHECKED_IN and visitor.status != VisitStatusEnum.IN_MEETING:
            raise ValidationError("Visitor is not checked in")
        
        visitor.status = VisitStatusEnum.CHECKED_OUT
        visitor.check_out_time = datetime.utcnow()
        visitor.badge_returned = True
        
        # Calculate duration
        if visitor.check_in_time:
            duration = (visitor.check_out_time - visitor.check_in_time).total_seconds() / 60
            visitor.duration_minutes = int(duration)
        
        visitor.updated_by = user_id
        visitor.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(visitor)
        
        return visitor
    
    @staticmethod
    async def get_active_visitors(
        db: AsyncSession,
        tenant_id: str
    ) -> List[Visitor]:
        """Get all currently checked-in visitors"""
        
        stmt = select(Visitor).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.status.in_([VisitStatusEnum.CHECKED_IN, VisitStatusEnum.IN_MEETING]),
                Visitor.is_deleted == False
            )
        ).order_by(Visitor.check_in_time.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_expected_visitors_today(
        db: AsyncSession,
        tenant_id: str
    ) -> List[Visitor]:
        """Get visitors expected today"""
        
        today = date.today()
        
        stmt = select(Visitor).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.visit_date == today,
                Visitor.status == VisitStatusEnum.SCHEDULED,
                Visitor.is_deleted == False
            )
        ).order_by(Visitor.expected_in_time)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def approve_visitor(
        db: AsyncSession,
        tenant_id: str,
        visitor_id: int,
        approved_by: int
    ) -> Visitor:
        """Approve a visitor entry"""
        
        visitor = await VisitorService.get_visitor(db, tenant_id, visitor_id)
        
        visitor.is_pre_approved = True
        visitor.approved_by = approved_by
        visitor.approved_at = datetime.utcnow()
        visitor.updated_by = approved_by
        visitor.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(visitor)
        
        return visitor
    
    # ============================================================================
    # VISITOR GROUP MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_visitor_group(
        db: AsyncSession,
        tenant_id: str,
        group_data: Dict[str, Any],
        user_id: int
    ) -> VisitorGroup:
        """Create a visitor group for bulk entries"""
        
        # Generate group code
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(VisitorGroup).where(
            VisitorGroup.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        group_code = f"VGRP{date_str}{count:04d}"
        
        group = VisitorGroup(
            tenant_id=tenant_id,
            group_code=group_code,
            created_by=user_id,
            **group_data
        )
        
        db.add(group)
        await db.commit()
        await db.refresh(group)
        
        return group
    
    @staticmethod
    async def get_visitor_statistics(
        db: AsyncSession,
        tenant_id: str,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Get visitor statistics for a date range"""
        
        # Total visitors
        total_stmt = select(func.count()).select_from(Visitor).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.visit_date >= from_date,
                Visitor.visit_date <= to_date,
                Visitor.is_deleted == False
            )
        )
        total_result = await db.execute(total_stmt)
        total_visitors = total_result.scalar()
        
        # By visitor type
        type_stmt = select(
            Visitor.visitor_type,
            func.count(Visitor.id)
        ).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.visit_date >= from_date,
                Visitor.visit_date <= to_date,
                Visitor.is_deleted == False
            )
        ).group_by(Visitor.visitor_type)
        
        type_result = await db.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_result.fetchall()}
        
        # By status
        status_stmt = select(
            Visitor.status,
            func.count(Visitor.id)
        ).where(
            and_(
                Visitor.tenant_id == tenant_id,
                Visitor.visit_date >= from_date,
                Visitor.visit_date <= to_date,
                Visitor.is_deleted == False
            )
        ).group_by(Visitor.status)
        
        status_result = await db.execute(status_stmt)
        by_status = {row[0]: row[1] for row in status_result.fetchall()}
        
        return {
            "total_visitors": total_visitors,
            "by_type": by_type,
            "by_status": by_status,
            "from_date": from_date,
            "to_date": to_date
        }

"""
Attendance Service Layer
Business logic for attendance, shift, and biometric operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, between
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, date, time, timedelta
import json

from backend.shared.database.attendance_models import (
    Shift, EmployeeShift, Attendance, BiometricLog, AttendanceRegularization,
    ShiftType, AttendanceStatus, CheckType, CheckMethod
)
from .schemas import (
    ShiftCreate, ShiftUpdate, CheckInRequest, CheckOutRequest,
    AttendanceCreate, AttendanceUpdate, BiometricLogCreate,
    AttendanceRegularizationRequest, MobileCheckInRequest, MobileCheckOutRequest
)


class ShiftService:
    """Service for shift management operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_shift(self, data: ShiftCreate) -> Shift:
        """Create new shift"""
        shift = Shift(
            tenant_id=self.tenant_id,
            shift_code=data.shift_code,
            shift_name=data.shift_name,
            shift_type=data.shift_type,
            start_time=data.start_time,
            end_time=data.end_time,
            grace_period_minutes=data.grace_period_minutes,
            half_day_hours=data.half_day_hours,
            full_day_hours=data.full_day_hours,
            break_duration_minutes=data.break_duration_minutes,
            break_start_time=data.break_start_time,
            break_end_time=data.break_end_time,
            week_off_1=data.week_off_1,
            week_off_2=data.week_off_2,
            allow_overtime=data.allow_overtime,
            overtime_start_after_minutes=data.overtime_start_after_minutes,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            description=data.description,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(shift)
        await self.db.commit()
        await self.db.refresh(shift)
        return shift
    
    async def get_shift(self, shift_id: str) -> Optional[Shift]:
        """Get shift by ID"""
        query = select(Shift).where(
            and_(
                Shift.id == shift_id,
                Shift.tenant_id == self.tenant_id,
                Shift.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_shifts(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        shift_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Shift], int]:
        """Get paginated shifts"""
        query = select(Shift).where(
            and_(
                Shift.tenant_id == self.tenant_id,
                Shift.is_deleted == False
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Shift.shift_name.ilike(search_term),
                    Shift.shift_code.ilike(search_term)
                )
            )
        
        if shift_type:
            query = query.where(Shift.shift_type == shift_type)
        
        if is_active is not None:
            query = query.where(Shift.is_active == is_active)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(Shift.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        shifts = result.scalars().all()
        
        return shifts, total
    
    async def update_shift(self, shift_id: str, data: ShiftUpdate) -> Shift:
        """Update shift"""
        shift = await self.get_shift(shift_id)
        if not shift:
            raise ValueError("Shift not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shift, field, value)
        
        shift.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(shift)
        return shift
    
    async def delete_shift(self, shift_id: str) -> bool:
        """Soft delete shift"""
        shift = await self.get_shift(shift_id)
        if not shift:
            raise ValueError("Shift not found")
        
        shift.is_deleted = True
        shift.deleted_at = datetime.utcnow()
        shift.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    async def assign_shift_to_employee(
        self, employee_id: str, shift_id: str, effective_from: date, effective_to: Optional[date] = None
    ) -> EmployeeShift:
        """Assign shift to employee"""
        # Verify shift exists
        shift = await self.get_shift(shift_id)
        if not shift:
            raise ValueError("Shift not found")
        
        # Check for overlapping assignments
        overlap_query = select(EmployeeShift).where(
            and_(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.tenant_id == self.tenant_id,
                EmployeeShift.is_deleted == False,
                EmployeeShift.is_active == True,
                or_(
                    EmployeeShift.effective_to.is_(None),
                    EmployeeShift.effective_to >= effective_from
                )
            )
        )
        overlap_result = await self.db.execute(overlap_query)
        overlap = overlap_result.scalar_one_or_none()
        
        if overlap:
            # Deactivate previous assignment
            overlap.is_active = False
            overlap.effective_to = effective_from - timedelta(days=1)
        
        # Create new assignment
        assignment = EmployeeShift(
            tenant_id=self.tenant_id,
            employee_id=employee_id,
            shift_id=shift_id,
            effective_from=effective_from,
            effective_to=effective_to,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment


class AttendanceService:
    """Service for attendance operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def check_in(self, request: CheckInRequest) -> Attendance:
        """Employee check-in"""
        check_in_time = request.check_in_time or datetime.now()
        attendance_date = check_in_time.date()
        
        # Check if attendance already exists for today
        existing = await self._get_attendance_for_date(request.employee_id, attendance_date)
        if existing and existing.actual_check_in:
            raise ValueError("Already checked in for today")
        
        # Get employee's shift for today
        shift = await self._get_employee_shift(request.employee_id, attendance_date)
        
        if existing:
            # Update existing record
            attendance = existing
            attendance.actual_check_in = check_in_time
            attendance.check_in_method = request.method
            attendance.check_in_device = request.device_info
            if request.location:
                attendance.check_in_location = json.dumps(request.location)
        else:
            # Create new attendance record
            attendance = Attendance(
                tenant_id=self.tenant_id,
                employee_id=request.employee_id,
                attendance_date=attendance_date,
                shift_id=shift.id if shift else None,
                scheduled_start_time=shift.start_time if shift else None,
                scheduled_end_time=shift.end_time if shift else None,
                actual_check_in=check_in_time,
                check_in_method=request.method,
                check_in_device=request.device_info,
                check_in_location=json.dumps(request.location) if request.location else None,
                status=AttendanceStatus.PRESENT,
                created_by=self.user_id,
                updated_by=self.user_id
            )
            self.db.add(attendance)
        
        # Calculate late arrival
        if shift and shift.start_time:
            scheduled_time = datetime.combine(attendance_date, shift.start_time)
            late_minutes = (check_in_time - scheduled_time).total_seconds() / 60
            
            if late_minutes > shift.grace_period_minutes:
                attendance.late_by_minutes = int(late_minutes - shift.grace_period_minutes)
        
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance
    
    async def check_out(self, request: CheckOutRequest) -> Attendance:
        """Employee check-out"""
        check_out_time = request.check_out_time or datetime.now()
        attendance_date = check_out_time.date()
        
        # Get today's attendance
        attendance = await self._get_attendance_for_date(request.employee_id, attendance_date)
        if not attendance:
            raise ValueError("No check-in record found for today")
        
        if attendance.actual_check_out:
            raise ValueError("Already checked out for today")
        
        attendance.actual_check_out = check_out_time
        attendance.check_out_method = request.method
        attendance.check_out_device = request.device_info
        if request.location:
            attendance.check_out_location = json.dumps(request.location)
        
        # Calculate work hours
        if attendance.actual_check_in:
            work_duration = check_out_time - attendance.actual_check_in
            total_minutes = work_duration.total_seconds() / 60
            
            # Subtract break time
            shift = await self._get_shift_by_id(attendance.shift_id)
            if shift:
                break_minutes = shift.break_duration_minutes
                work_minutes = total_minutes - break_minutes
                attendance.total_work_hours = round(work_minutes / 60, 2)
                attendance.break_hours = round(break_minutes / 60, 2)
                
                # Check for early departure
                if shift.end_time:
                    scheduled_end = datetime.combine(attendance_date, shift.end_time)
                    if check_out_time < scheduled_end:
                        early_minutes = (scheduled_end - check_out_time).total_seconds() / 60
                        attendance.early_out_minutes = int(early_minutes)
                
                # Calculate overtime
                if shift.allow_overtime:
                    expected_hours = shift.full_day_hours
                    if attendance.total_work_hours > expected_hours:
                        overtime = attendance.total_work_hours - expected_hours
                        if overtime * 60 >= shift.overtime_start_after_minutes:
                            attendance.overtime_hours = round(overtime, 2)
                
                # Determine status
                if attendance.total_work_hours >= shift.full_day_hours:
                    attendance.status = AttendanceStatus.PRESENT
                elif attendance.total_work_hours >= shift.half_day_hours:
                    attendance.status = AttendanceStatus.HALF_DAY
                else:
                    attendance.status = AttendanceStatus.HALF_DAY
        
        attendance.updated_by = self.user_id
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance
    
    async def mobile_check_in(self, request: MobileCheckInRequest) -> Dict[str, Any]:
        """Mobile app check-in with location"""
        check_in_req = CheckInRequest(
            employee_id=request.employee_id,
            location={
                "lat": request.latitude,
                "lng": request.longitude,
                "address": request.address
            },
            device_info=request.device_info,
            method=CheckMethod.MOBILE
        )
        
        attendance = await self.check_in(check_in_req)
        
        shift = await self._get_shift_by_id(attendance.shift_id)
        
        return {
            "success": True,
            "message": "Checked in successfully",
            "attendance_id": attendance.id,
            "check_in_time": attendance.actual_check_in,
            "shift_info": {
                "shift_name": shift.shift_name if shift else None,
                "start_time": str(shift.start_time) if shift else None,
                "end_time": str(shift.end_time) if shift else None
            } if shift else None
        }
    
    async def mobile_check_out(self, request: MobileCheckOutRequest) -> Dict[str, Any]:
        """Mobile app check-out with location"""
        check_out_req = CheckOutRequest(
            employee_id=request.employee_id,
            location={
                "lat": request.latitude,
                "lng": request.longitude,
                "address": request.address
            },
            device_info=request.device_info,
            method=CheckMethod.MOBILE
        )
        
        attendance = await self.check_out(check_out_req)
        
        return {
            "success": True,
            "message": "Checked out successfully",
            "attendance_id": attendance.id,
            "check_out_time": attendance.actual_check_out,
            "total_work_hours": attendance.total_work_hours,
            "overtime_hours": attendance.overtime_hours
        }
    
    async def get_attendance(self, attendance_id: str) -> Optional[Attendance]:
        """Get attendance by ID"""
        query = select(Attendance).where(
            and_(
                Attendance.id == attendance_id,
                Attendance.tenant_id == self.tenant_id,
                Attendance.is_deleted == False
            )
        ).options(
            selectinload(Attendance.employee),
            selectinload(Attendance.shift)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_attendances(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Attendance], int]:
        """Get paginated attendances"""
        query = select(Attendance).where(
            and_(
                Attendance.tenant_id == self.tenant_id,
                Attendance.is_deleted == False
            )
        ).options(
            selectinload(Attendance.employee),
            selectinload(Attendance.shift)
        )
        
        if employee_id:
            query = query.where(Attendance.employee_id == employee_id)
        
        if from_date and to_date:
            query = query.where(
                between(Attendance.attendance_date, from_date, to_date)
            )
        elif from_date:
            query = query.where(Attendance.attendance_date >= from_date)
        elif to_date:
            query = query.where(Attendance.attendance_date <= to_date)
        
        if status:
            query = query.where(Attendance.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(Attendance.attendance_date))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()
        
        return attendances, total
    
    async def create_manual_attendance(self, data: AttendanceCreate) -> Attendance:
        """Create manual attendance entry"""
        # Check if attendance already exists
        existing = await self._get_attendance_for_date(data.employee_id, data.attendance_date)
        if existing:
            raise ValueError("Attendance already exists for this date")
        
        attendance = Attendance(
            tenant_id=self.tenant_id,
            employee_id=data.employee_id,
            attendance_date=data.attendance_date,
            shift_id=data.shift_id,
            actual_check_in=data.actual_check_in,
            actual_check_out=data.actual_check_out,
            status=data.status,
            remarks=data.remarks,
            is_manual_entry=True,
            manual_entry_reason=data.manual_entry_reason,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance
    
    async def _get_attendance_for_date(self, employee_id: str, attendance_date: date) -> Optional[Attendance]:
        """Helper to get attendance for specific date"""
        query = select(Attendance).where(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.attendance_date == attendance_date,
                Attendance.tenant_id == self.tenant_id,
                Attendance.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_employee_shift(self, employee_id: str, effective_date: date) -> Optional[Shift]:
        """Get employee's active shift"""
        query = select(Shift).join(EmployeeShift).where(
            and_(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.tenant_id == self.tenant_id,
                EmployeeShift.is_active == True,
                EmployeeShift.is_deleted == False,
                EmployeeShift.effective_from <= effective_date,
                or_(
                    EmployeeShift.effective_to.is_(None),
                    EmployeeShift.effective_to >= effective_date
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_shift_by_id(self, shift_id: Optional[str]) -> Optional[Shift]:
        """Helper to get shift by ID"""
        if not shift_id:
            return None
        query = select(Shift).where(Shift.id == shift_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get attendance dashboard statistics"""
        today = date.today()
        
        # Total employees (from HRMS module)
        from backend.shared.database.hrms_models import Employee
        total_emp_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        total_emp_result = await self.db.execute(total_emp_query)
        total_employees = total_emp_result.scalar() or 0
        
        # Today's attendance stats
        today_query = select(
            Attendance.status,
            func.count(Attendance.id)
        ).where(
            and_(
                Attendance.attendance_date == today,
                Attendance.tenant_id == self.tenant_id,
                Attendance.is_deleted == False
            )
        ).group_by(Attendance.status)
        
        today_result = await self.db.execute(today_query)
        status_counts = dict(today_result.all())
        
        present = status_counts.get(AttendanceStatus.PRESENT, 0)
        half_day = status_counts.get(AttendanceStatus.HALF_DAY, 0)
        leave = status_counts.get(AttendanceStatus.LEAVE, 0)
        absent = total_employees - present - half_day - leave
        
        # Late arrivals today
        late_query = select(func.count(Attendance.id)).where(
            and_(
                Attendance.attendance_date == today,
                Attendance.tenant_id == self.tenant_id,
                Attendance.late_by_minutes > 0,
                Attendance.is_deleted == False
            )
        )
        late_result = await self.db.execute(late_query)
        late_arrivals = late_result.scalar() or 0
        
        # Average work hours today
        avg_query = select(func.avg(Attendance.total_work_hours)).where(
            and_(
                Attendance.attendance_date == today,
                Attendance.tenant_id == self.tenant_id,
                Attendance.total_work_hours > 0,
                Attendance.is_deleted == False
            )
        )
        avg_result = await self.db.execute(avg_query)
        avg_work_hours = avg_result.scalar() or 0.0
        
        attendance_percentage = (present + half_day) / total_employees * 100 if total_employees > 0 else 0
        
        return {
            "total_employees": total_employees,
            "present_today": present + half_day,
            "absent_today": absent,
            "on_leave_today": leave,
            "late_arrivals": late_arrivals,
            "early_departures": 0,  # TODO: Calculate
            "avg_work_hours": round(avg_work_hours, 2),
            "attendance_percentage": round(attendance_percentage, 2)
        }


class BiometricService:
    """Service for biometric log operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_biometric_log(self, data: BiometricLogCreate) -> BiometricLog:
        """Create biometric log from device"""
        log = BiometricLog(
            tenant_id=self.tenant_id,
            employee_id=data.employee_id,
            biometric_id=data.biometric_id,
            log_datetime=data.log_datetime,
            check_type=data.check_type,
            device_id=data.device_id,
            device_name=data.device_name,
            device_location=data.device_location,
            verification_method=data.verification_method,
            verification_score=data.verification_score
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        # Process the log asynchronously
        await self._process_biometric_log(log)
        
        return log
    
    async def _process_biometric_log(self, log: BiometricLog):
        """Process biometric log and create/update attendance"""
        attendance_date = log.log_datetime.date()
        
        # Get or create attendance record
        attendance_service = AttendanceService(self.db, self.tenant_id, self.user_id)
        
        if log.check_type == CheckType.CHECK_IN:
            request = CheckInRequest(
                employee_id=log.employee_id,
                check_in_time=log.log_datetime,
                method=CheckMethod.BIOMETRIC,
                device_info=f"{log.device_name} ({log.device_id})"
            )
            attendance = await attendance_service.check_in(request)
            log.attendance_id = attendance.id
        
        elif log.check_type == CheckType.CHECK_OUT:
            request = CheckOutRequest(
                employee_id=log.employee_id,
                check_out_time=log.log_datetime,
                method=CheckMethod.BIOMETRIC,
                device_info=f"{log.device_name} ({log.device_id})"
            )
            attendance = await attendance_service.check_out(request)
            log.attendance_id = attendance.id
        
        log.is_processed = True
        log.processed_at = datetime.utcnow()
        await self.db.commit()

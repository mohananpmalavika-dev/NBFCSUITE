"""
Locker Operating Hours Service

Manages locker facility operating hours, holiday schedules, and special access requests.
Handles standard hours, emergency access, and after-hours authorization.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from backend.shared.database.locker_models import LockerAccessLog


class LockerOperatingHoursService:
    """Service for managing locker operating hours and special access"""
    
    # Standard operating hours configuration
    STANDARD_HOURS = {
        "weekday_start": time(10, 0),  # 10:00 AM
        "weekday_end": time(16, 0),    # 4:00 PM
        "saturday_start": time(10, 0),  # 10:00 AM
        "saturday_end": time(13, 0),    # 1:00 PM
        "sunday_closed": True,
        "lunch_break_start": time(13, 0),  # 1:00 PM
        "lunch_break_end": time(14, 0),    # 2:00 PM
        "lunch_break_enabled": False
    }
    
    def __init__(self, db: Session, tenant_id: UUID, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self._holidays = []  # Would typically load from database
    
    # ==================== OPERATING HOURS VALIDATION ====================
    
    async def is_facility_open(
        self,
        check_datetime: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Check if locker facility is currently open
        
        Returns:
            Dict with open status, reason if closed, and next opening time
        """
        if check_datetime is None:
            check_datetime = datetime.now()
        
        check_date = check_datetime.date()
        check_time = check_datetime.time()
        weekday = check_datetime.weekday()
        
        # Check if it's a holiday
        if await self._is_holiday(check_date):
            next_opening = await self._get_next_opening_datetime(check_date)
            return {
                "is_open": False,
                "reason": "Holiday",
                "next_opening": next_opening,
                "current_time": check_datetime
            }
        
        # Check Sunday
        if weekday == 6 and self.STANDARD_HOURS["sunday_closed"]:
            next_opening = await self._get_next_opening_datetime(check_date)
            return {
                "is_open": False,
                "reason": "Sunday - Facility Closed",
                "next_opening": next_opening,
                "current_time": check_datetime
            }
        
        # Check operating hours
        if weekday == 5:  # Saturday
            start_time = self.STANDARD_HOURS["saturday_start"]
            end_time = self.STANDARD_HOURS["saturday_end"]
        else:  # Weekday
            start_time = self.STANDARD_HOURS["weekday_start"]
            end_time = self.STANDARD_HOURS["weekday_end"]
        
        # Check if within operating hours
        if check_time < start_time:
            opening_datetime = datetime.combine(check_date, start_time)
            return {
                "is_open": False,
                "reason": f"Before opening time ({start_time.strftime('%I:%M %p')})",
                "next_opening": opening_datetime,
                "current_time": check_datetime
            }
        
        if check_time >= end_time:
            next_opening = await self._get_next_opening_datetime(check_date)
            return {
                "is_open": False,
                "reason": f"After closing time ({end_time.strftime('%I:%M %p')})",
                "next_opening": next_opening,
                "current_time": check_datetime
            }
        
        # Check lunch break
        if self.STANDARD_HOURS["lunch_break_enabled"]:
            lunch_start = self.STANDARD_HOURS["lunch_break_start"]
            lunch_end = self.STANDARD_HOURS["lunch_break_end"]
            
            if lunch_start <= check_time < lunch_end:
                lunch_end_datetime = datetime.combine(check_date, lunch_end)
                return {
                    "is_open": False,
                    "reason": f"Lunch break ({lunch_start.strftime('%I:%M %p')} - {lunch_end.strftime('%I:%M %p')})",
                    "next_opening": lunch_end_datetime,
                    "current_time": check_datetime
                }
        
        return {
            "is_open": True,
            "reason": None,
            "closing_time": datetime.combine(check_date, end_time),
            "current_time": check_datetime
        }
    
    async def get_operating_hours(
        self,
        for_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get operating hours for a specific date"""
        if for_date is None:
            for_date = date.today()
        
        weekday = for_date.weekday()
        
        # Check if holiday
        is_holiday = await self._is_holiday(for_date)
        
        if is_holiday:
            return {
                "date": for_date,
                "is_holiday": True,
                "is_open": False,
                "hours": None,
                "holiday_name": "Bank Holiday"
            }
        
        # Sunday
        if weekday == 6 and self.STANDARD_HOURS["sunday_closed"]:
            return {
                "date": for_date,
                "is_holiday": False,
                "is_open": False,
                "hours": None,
                "reason": "Sunday"
            }
        
        # Saturday
        if weekday == 5:
            return {
                "date": for_date,
                "is_holiday": False,
                "is_open": True,
                "hours": {
                    "start": self.STANDARD_HOURS["saturday_start"].strftime("%H:%M"),
                    "end": self.STANDARD_HOURS["saturday_end"].strftime("%H:%M")
                },
                "day_type": "Saturday"
            }
        
        # Weekday
        hours_info = {
            "date": for_date,
            "is_holiday": False,
            "is_open": True,
            "hours": {
                "start": self.STANDARD_HOURS["weekday_start"].strftime("%H:%M"),
                "end": self.STANDARD_HOURS["weekday_end"].strftime("%H:%M")
            },
            "day_type": "Weekday"
        }
        
        if self.STANDARD_HOURS["lunch_break_enabled"]:
            hours_info["lunch_break"] = {
                "start": self.STANDARD_HOURS["lunch_break_start"].strftime("%H:%M"),
                "end": self.STANDARD_HOURS["lunch_break_end"].strftime("%H:%M")
            }
        
        return hours_info

    
    async def get_weekly_schedule(self) -> List[Dict[str, Any]]:
        """Get full weekly operating schedule"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        schedule = []
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_info = await self.get_operating_hours(day_date)
            day_info["day_name"] = day_date.strftime("%A")
            schedule.append(day_info)
        
        return schedule
    
    # ==================== SPECIAL ACCESS REQUESTS ====================
    
    async def request_holiday_access(
        self,
        requested_date: date,
        requested_time_start: time,
        requested_time_end: time,
        customer_id: UUID,
        allocation_id: UUID,
        reason: str,
        emergency: bool = False
    ) -> Dict[str, Any]:
        """
        Request special access on holiday
        
        Returns approval/rejection with reference number
        """
        # Validate it's actually a holiday
        is_holiday = await self._is_holiday(requested_date)
        
        if not is_holiday and requested_date.weekday() != 6:
            return {
                "approved": False,
                "reason": "Special access only required for holidays and Sundays",
                "request_id": None
            }
        
        # Generate request ID
        request_id = f"HAR{requested_date.strftime('%Y%m%d')}{str(customer_id)[:8].upper()}"
        
        # In real implementation, this would create a request record
        # For now, auto-approve emergency requests
        if emergency:
            approval_status = "approved"
            approval_reason = "Emergency access auto-approved"
        else:
            approval_status = "pending"
            approval_reason = "Awaiting management approval"
        
        return {
            "approved": emergency,
            "status": approval_status,
            "reason": approval_reason,
            "request_id": request_id,
            "requested_date": requested_date,
            "requested_time": f"{requested_time_start.strftime('%H:%M')} - {requested_time_end.strftime('%H:%M')}",
            "customer_id": customer_id,
            "allocation_id": allocation_id,
            "requires_approval": not emergency
        }
    
    async def request_after_hours_access(
        self,
        requested_datetime: datetime,
        customer_id: UUID,
        allocation_id: UUID,
        reason: str,
        emergency: bool = False,
        approver_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Request special access outside operating hours
        
        Returns approval/rejection with conditions
        """
        # Check if truly after hours
        facility_status = await self.is_facility_open(requested_datetime)
        
        if facility_status["is_open"]:
            return {
                "approved": False,
                "reason": "Facility is open at requested time - special access not required",
                "request_id": None
            }
        
        # Generate request ID
        request_id = f"AHR{requested_datetime.strftime('%Y%m%d%H%M')}{str(customer_id)[:8].upper()}"
        
        # Emergency access requires manager approval
        if emergency:
            if not approver_id:
                return {
                    "approved": False,
                    "status": "rejected",
                    "reason": "Emergency after-hours access requires manager approval",
                    "request_id": request_id
                }
            
            approval_status = "approved"
            conditions = [
                "Security personnel must be present",
                "Access limited to 30 minutes",
                "CCTV recording mandatory",
                "Dual authentication required"
            ]
        else:
            approval_status = "pending"
            conditions = [
                "Awaiting senior management approval",
                "Valid reason must be provided",
                "Advance notice of 24 hours required"
            ]
        
        return {
            "approved": emergency and approver_id is not None,
            "status": approval_status,
            "request_id": request_id,
            "requested_datetime": requested_datetime,
            "customer_id": customer_id,
            "allocation_id": allocation_id,
            "conditions": conditions,
            "approver_id": approver_id,
            "emergency": emergency
        }
    
    async def approve_special_access(
        self,
        request_id: str,
        approved: bool,
        approver_id: UUID,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve or reject special access request
        
        In real implementation, this would update the request in database
        """
        return {
            "request_id": request_id,
            "status": "approved" if approved else "rejected",
            "approved_by": approver_id,
            "approval_datetime": datetime.now(),
            "remarks": remarks,
            "valid_for": "Single use only",
            "expires_after": "24 hours"
        }
    
    # ==================== ACCESS PROTOCOLS ====================
    
    async def get_emergency_access_protocol(self) -> Dict[str, Any]:
        """Get emergency access protocol requirements"""
        return {
            "protocol_name": "Emergency Locker Access Protocol",
            "requirements": [
                "Senior manager approval required",
                "Two bank officials must be present",
                "Security personnel mandatory",
                "CCTV recording mandatory",
                "Customer identity verification (biometric + ID)",
                "Access log with detailed reason",
                "Time limit: Maximum 30 minutes"
            ],
            "approval_levels": [
                {
                    "level": 1,
                    "title": "Branch Manager",
                    "for": "Regular after-hours access"
                },
                {
                    "level": 2,
                    "title": "Regional Manager",
                    "for": "Holiday access"
                },
                {
                    "level": 3,
                    "title": "Head of Operations",
                    "for": "Emergency forced opening"
                }
            ],
            "documentation": [
                "Written request from customer",
                "Approval form signed by authorized manager",
                "Incident report (if emergency)",
                "Access log with entry/exit times",
                "Witness statements from bank officials"
            ]
        }
    
    async def get_escort_service_requirements(self) -> Dict[str, Any]:
        """Get requirements for bank official escort service"""
        return {
            "service_name": "Bank Official Escort Service",
            "mandatory_for": [
                "First-time locker access",
                "Access by nominee or legal heir",
                "After-hours access",
                "Emergency access",
                "Court order execution",
                "Locker breaking/forced opening"
            ],
            "optional_for": [
                "Regular customer access during operating hours"
            ],
            "escort_duties": [
                "Verify customer identity",
                "Witness locker opening and closing",
                "Ensure locker security",
                "Record access in register",
                "Sign access log as witness",
                "Escort customer to and from locker area"
            ],
            "minimum_officials": {
                "regular_access": 1,
                "after_hours_access": 2,
                "emergency_access": 2,
                "forced_opening": 3
            }
        }

    
    # ==================== ANALYTICS & REPORTS ====================
    
    async def get_after_hours_access_statistics(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get statistics on after-hours and special access"""
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()
        
        # Query after-hours access logs
        after_hours_logs = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to
        ).all()
        
        # Filter for after-hours accesses
        total_after_hours = 0
        emergency_accesses = 0
        holiday_accesses = 0
        
        for log in after_hours_logs:
            if log.access_time_in:
                is_after_hours = not await self._is_within_standard_hours(log.access_time_in)
                if is_after_hours:
                    total_after_hours += 1
                    
                    if log.emergency_access:
                        emergency_accesses += 1
                    
                    if await self._is_holiday(log.access_date):
                        holiday_accesses += 1
        
        return {
            "date_from": date_from,
            "date_to": date_to,
            "total_after_hours_access": total_after_hours,
            "emergency_access_count": emergency_accesses,
            "holiday_access_count": holiday_accesses,
            "regular_after_hours": total_after_hours - emergency_accesses - holiday_accesses
        }
    
    async def get_peak_hours_analysis(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Analyze peak access hours to optimize staffing"""
        if not date_from:
            date_from = date.today() - timedelta(days=30)
        if not date_to:
            date_to = date.today()
        
        access_logs = self.db.query(LockerAccessLog).filter(
            LockerAccessLog.tenant_id == self.tenant_id,
            LockerAccessLog.is_deleted == False,
            LockerAccessLog.access_date >= date_from,
            LockerAccessLog.access_date <= date_to,
            LockerAccessLog.access_time_in.isnot(None)
        ).all()
        
        # Group by hour
        hourly_distribution = {}
        for hour in range(24):
            hourly_distribution[f"{hour:02d}:00"] = 0
        
        for log in access_logs:
            hour = log.access_time_in.hour
            hourly_distribution[f"{hour:02d}:00"] += 1
        
        # Find peak hours
        sorted_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)
        peak_hours = sorted_hours[:3]
        
        # Day of week analysis
        day_distribution = {
            "Monday": 0, "Tuesday": 0, "Wednesday": 0,
            "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0
        }
        
        for log in access_logs:
            day_name = log.access_date.strftime("%A")
            day_distribution[day_name] += 1
        
        return {
            "date_from": date_from,
            "date_to": date_to,
            "total_accesses": len(access_logs),
            "hourly_distribution": hourly_distribution,
            "peak_hours": [{"hour": h[0], "count": h[1]} for h in peak_hours],
            "busiest_day": max(day_distribution.items(), key=lambda x: x[1])[0],
            "day_distribution": day_distribution,
            "recommendations": await self._generate_staffing_recommendations(hourly_distribution)
        }
    
    # ==================== HELPER METHODS ====================
    
    async def _is_holiday(self, check_date: date) -> bool:
        """Check if given date is a holiday"""
        # In real implementation, this would check against holiday calendar in database
        # For now, using a simple list
        
        # Common bank holidays (example for India)
        year = check_date.year
        holidays = [
            date(year, 1, 26),   # Republic Day
            date(year, 8, 15),   # Independence Day
            date(year, 10, 2),   # Gandhi Jayanti
            date(year, 12, 25),  # Christmas
        ]
        
        return check_date in holidays or check_date in self._holidays
    
    async def _get_next_opening_datetime(self, from_date: date) -> datetime:
        """Get next opening datetime after given date"""
        check_date = from_date + timedelta(days=1)
        max_checks = 14  # Check up to 2 weeks ahead
        
        for _ in range(max_checks):
            # Skip if holiday
            if await self._is_holiday(check_date):
                check_date += timedelta(days=1)
                continue
            
            weekday = check_date.weekday()
            
            # Skip Sunday
            if weekday == 6 and self.STANDARD_HOURS["sunday_closed"]:
                check_date += timedelta(days=1)
                continue
            
            # Determine opening time
            if weekday == 5:  # Saturday
                opening_time = self.STANDARD_HOURS["saturday_start"]
            else:  # Weekday
                opening_time = self.STANDARD_HOURS["weekday_start"]
            
            return datetime.combine(check_date, opening_time)
        
        # If no opening found in 2 weeks, return a default
        return datetime.combine(from_date + timedelta(days=1), time(10, 0))
    
    async def _is_within_standard_hours(self, check_datetime: datetime) -> bool:
        """Check if datetime falls within standard operating hours"""
        facility_status = await self.is_facility_open(check_datetime)
        return facility_status["is_open"]
    
    async def _generate_staffing_recommendations(
        self,
        hourly_distribution: Dict[str, int]
    ) -> List[str]:
        """Generate staffing recommendations based on peak hours"""
        recommendations = []
        
        # Find hours with high traffic
        sorted_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_hours[0][1] > 0:
            peak_hour = sorted_hours[0][0]
            recommendations.append(
                f"Peak hour is {peak_hour} - consider additional staff during this time"
            )
        
        # Check morning vs afternoon
        morning_count = sum([count for hour, count in hourly_distribution.items() 
                           if 10 <= int(hour.split(':')[0]) < 13])
        afternoon_count = sum([count for hour, count in hourly_distribution.items() 
                             if 13 <= int(hour.split(':')[0]) < 16])
        
        if morning_count > afternoon_count * 1.5:
            recommendations.append("Morning hours are significantly busier - prioritize morning staffing")
        elif afternoon_count > morning_count * 1.5:
            recommendations.append("Afternoon hours are significantly busier - prioritize afternoon staffing")
        else:
            recommendations.append("Traffic is evenly distributed - maintain consistent staffing")
        
        return recommendations
    
    # ==================== CONFIGURATION ====================
    
    async def update_operating_hours(
        self,
        weekday_start: Optional[time] = None,
        weekday_end: Optional[time] = None,
        saturday_start: Optional[time] = None,
        saturday_end: Optional[time] = None,
        enable_lunch_break: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update operating hours configuration
        (In real implementation, this would persist to database)
        """
        if weekday_start:
            self.STANDARD_HOURS["weekday_start"] = weekday_start
        if weekday_end:
            self.STANDARD_HOURS["weekday_end"] = weekday_end
        if saturday_start:
            self.STANDARD_HOURS["saturday_start"] = saturday_start
        if saturday_end:
            self.STANDARD_HOURS["saturday_end"] = saturday_end
        if enable_lunch_break is not None:
            self.STANDARD_HOURS["lunch_break_enabled"] = enable_lunch_break
        
        return {
            "status": "updated",
            "current_hours": self.STANDARD_HOURS,
            "updated_by": self.user_id,
            "updated_at": datetime.now()
        }
    
    async def add_holiday(
        self,
        holiday_date: date,
        holiday_name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a holiday to the calendar
        (In real implementation, this would persist to database)
        """
        self._holidays.append(holiday_date)
        
        return {
            "status": "added",
            "holiday_date": holiday_date,
            "holiday_name": holiday_name,
            "description": description,
            "added_by": self.user_id,
            "added_at": datetime.now()
        }
    
    async def get_holiday_calendar(
        self,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get list of holidays for given year"""
        if year is None:
            year = date.today().year
        
        # In real implementation, fetch from database
        holidays = [
            {"date": date(year, 1, 26), "name": "Republic Day"},
            {"date": date(year, 8, 15), "name": "Independence Day"},
            {"date": date(year, 10, 2), "name": "Gandhi Jayanti"},
            {"date": date(year, 12, 25), "name": "Christmas"},
        ]
        
        # Add custom holidays
        holidays.extend([
            {"date": d, "name": "Bank Holiday"}
            for d in self._holidays
            if d.year == year
        ])
        
        return sorted(holidays, key=lambda x: x["date"])

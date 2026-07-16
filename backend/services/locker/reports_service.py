"""
Locker Reports & Analytics Service
Handles comprehensive reporting and analytics for locker management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid


# ==================== ENUMS ====================

class ReportType(str, Enum):
    """Types of reports available"""
    ALLOCATION_REGISTER = "allocation_register"
    AVAILABLE_OCCUPIED = "available_occupied"
    WAITING_LIST = "waiting_list"
    RENT_COLLECTION = "rent_collection"
    OVERDUE_RENT = "overdue_rent"
    ACCESS_LOG = "access_log"
    LOCKER_BREAKING = "locker_breaking"
    BRANCH_WISE = "branch_wise"
    REVENUE = "revenue"
    OCCUPANCY_RATE = "occupancy_rate"
    CUSTOMER_DEMOGRAPHICS = "customer_demographics"


class ExportFormat(str, Enum):
    """Export formats supported"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ReportPeriod(str, Enum):
    """Report period options"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== SERVICE CLASS ====================

class LockerReportsService:
    """
    Service for generating locker reports and analytics
    """
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== DASHBOARD ====================
    
    async def get_dashboard(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard with all KPIs
        """
        dashboard = {
            # Total lockers by size
            "total_lockers": {
                "total": 250,
                "by_size": {
                    "small": 100,
                    "medium": 80,
                    "large": 50,
                    "extra_large": 20
                }
            },
            
            # Occupied vs Available
            "occupancy": {
                "total_lockers": 250,
                "occupied": 180,
                "available": 70,
                "occupancy_percentage": 72.0,
                "under_maintenance": 5,
                "blocked": 2
            },
            
            # Rent collection current month
            "rent_collection": {
                "current_month": {
                    "total_expected": 450000.00,
                    "collected": 380000.00,
                    "pending": 70000.00,
                    "collection_percentage": 84.4
                },
                "comparison": {
                    "last_month": 420000.00,
                    "growth_percentage": 7.1
                }
            },
            
            # Overdue lockers
            "overdue": {
                "total_overdue_lockers": 15,
                "total_overdue_amount": 75000.00,
                "by_period": {
                    "0-30_days": 8,
                    "31-60_days": 5,
                    "61-90_days": 2,
                    "over_90_days": 0
                }
            },
            
            # Waiting list
            "waiting_list": {
                "total_waiting": 25,
                "by_size": {
                    "small": 10,
                    "medium": 8,
                    "large": 5,
                    "extra_large": 2
                },
                "average_wait_days": 45
            },
            
            # Recent allocations
            "recent_allocations": {
                "today": 2,
                "this_week": 8,
                "this_month": 35,
                "last_allocation": datetime.utcnow() - timedelta(hours=5)
            },
            
            # Recent surrenders
            "recent_surrenders": {
                "today": 1,
                "this_week": 3,
                "this_month": 12,
                "last_surrender": datetime.utcnow() - timedelta(days=2)
            },
            
            # Additional metrics
            "revenue_trends": [
                {"month": "Jan", "revenue": 420000},
                {"month": "Feb", "revenue": 435000},
                {"month": "Mar", "revenue": 450000}
            ],
            
            "occupancy_trends": [
                {"month": "Jan", "percentage": 68.5},
                {"month": "Feb", "percentage": 70.2},
                {"month": "Mar", "percentage": 72.0}
            ]
        }
        
        return dashboard
    
    # ==================== REPORT GENERATION ====================
    
    async def generate_allocation_register(
        self,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate locker allocation register report
        """
        allocations = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.ALLOCATION_REGISTER,
            "generated_at": datetime.utcnow(),
            "filters": filters,
            "total_records": len(allocations),
            "data": allocations,
            "summary": {
                "total_allocations": len(allocations),
                "active_allocations": 0,
                "expired_allocations": 0,
                "total_rent_collected": 0.0,
                "total_security_deposit": 0.0
            }
        }
        
        return report
    
    async def generate_available_occupied_report(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate available/occupied lockers report
        """
        report = {
            "report_type": ReportType.AVAILABLE_OCCUPIED,
            "generated_at": datetime.utcnow(),
            "branch_id": branch_id,
            "summary": {
                "total_lockers": 250,
                "available": 70,
                "occupied": 180,
                "under_maintenance": 5,
                "blocked": 2,
                "occupancy_rate": 72.0
            },
            "by_size": [
                {
                    "size": "small",
                    "total": 100,
                    "available": 25,
                    "occupied": 75,
                    "occupancy_rate": 75.0
                },
                {
                    "size": "medium",
                    "total": 80,
                    "available": 20,
                    "occupied": 60,
                    "occupancy_rate": 75.0
                },
                {
                    "size": "large",
                    "total": 50,
                    "available": 15,
                    "occupied": 35,
                    "occupancy_rate": 70.0
                },
                {
                    "size": "extra_large",
                    "total": 20,
                    "available": 10,
                    "occupied": 10,
                    "occupancy_rate": 50.0
                }
            ],
            "by_branch": []
        }
        
        return report
    
    async def generate_waiting_list_report(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate waiting list report
        """
        waiting_list = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.WAITING_LIST,
            "generated_at": datetime.utcnow(),
            "branch_id": branch_id,
            "total_waiting": len(waiting_list),
            "data": waiting_list,
            "summary": {
                "by_size": {
                    "small": 10,
                    "medium": 8,
                    "large": 5,
                    "extra_large": 2
                },
                "by_priority": {
                    "high": 5,
                    "medium": 12,
                    "low": 8
                },
                "average_wait_days": 45,
                "longest_wait_days": 120
            }
        }
        
        return report

    
    async def generate_rent_collection_report(
        self,
        period: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """
        Generate rent collection report
        """
        collections = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.RENT_COLLECTION,
            "generated_at": datetime.utcnow(),
            "period": period,
            "total_records": len(collections),
            "data": collections,
            "summary": {
                "total_expected": 450000.00,
                "total_collected": 380000.00,
                "total_pending": 70000.00,
                "collection_percentage": 84.4,
                "by_payment_mode": {
                    "cash": 50000.00,
                    "cheque": 100000.00,
                    "online": 180000.00,
                    "card": 50000.00
                },
                "by_branch": []
            }
        }
        
        return report
    
    async def generate_overdue_rent_report(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate overdue rent report
        """
        overdue_records = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.OVERDUE_RENT,
            "generated_at": datetime.utcnow(),
            "branch_id": branch_id,
            "total_records": len(overdue_records),
            "data": overdue_records,
            "summary": {
                "total_overdue_lockers": 15,
                "total_overdue_amount": 75000.00,
                "by_aging": {
                    "0-30_days": {"count": 8, "amount": 20000.00},
                    "31-60_days": {"count": 5, "amount": 25000.00},
                    "61-90_days": {"count": 2, "amount": 15000.00},
                    "over_90_days": {"count": 0, "amount": 0.00}
                },
                "by_customer_category": {
                    "regular": 10,
                    "premium": 3,
                    "senior_citizen": 2
                }
            }
        }
        
        return report
    
    async def generate_access_log_report(
        self,
        period: Dict[str, datetime],
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate access log report
        """
        access_logs = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.ACCESS_LOG,
            "generated_at": datetime.utcnow(),
            "period": period,
            "branch_id": branch_id,
            "total_records": len(access_logs),
            "data": access_logs,
            "summary": {
                "total_accesses": len(access_logs),
                "unique_lockers_accessed": 0,
                "unique_customers": 0,
                "by_access_type": {
                    "deposit": 0,
                    "retrieval": 0,
                    "inspection": 0
                },
                "busiest_hours": [],
                "busiest_days": []
            }
        }
        
        return report
    
    async def generate_locker_breaking_register(
        self,
        period: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """
        Generate locker breaking register
        """
        breaking_records = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.LOCKER_BREAKING,
            "generated_at": datetime.utcnow(),
            "period": period,
            "total_records": len(breaking_records),
            "data": breaking_records,
            "summary": {
                "total_breakings": len(breaking_records),
                "by_reason": {
                    "key_lost": 0,
                    "non_payment": 0,
                    "customer_request": 0,
                    "expired_allocation": 0
                },
                "total_charges_collected": 0.0,
                "pending_charges": 0.0
            }
        }
        
        return report
    
    async def generate_branch_wise_report(
        self,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate branch-wise locker report
        """
        branches = []
        # Placeholder - would query database
        
        report = {
            "report_type": ReportType.BRANCH_WISE,
            "generated_at": datetime.utcnow(),
            "total_branches": len(branches),
            "data": branches,
            "summary": {
                "total_lockers_all_branches": 500,
                "total_occupied": 360,
                "total_available": 140,
                "overall_occupancy_rate": 72.0,
                "total_revenue_current_month": 850000.00,
                "top_performing_branches": [],
                "low_occupancy_branches": []
            }
        }
        
        return report
    
    async def generate_revenue_report(
        self,
        period: Dict[str, datetime],
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate revenue from lockers report
        """
        report = {
            "report_type": ReportType.REVENUE,
            "generated_at": datetime.utcnow(),
            "period": period,
            "branch_id": branch_id,
            "summary": {
                "total_revenue": 450000.00,
                "rent_revenue": 380000.00,
                "security_deposit": 50000.00,
                "penalty_revenue": 10000.00,
                "other_charges": 10000.00,
                "by_locker_size": {
                    "small": 150000.00,
                    "medium": 180000.00,
                    "large": 90000.00,
                    "extra_large": 30000.00
                },
                "by_payment_mode": {
                    "cash": 50000.00,
                    "cheque": 100000.00,
                    "online": 250000.00,
                    "card": 50000.00
                },
                "revenue_trends": []
            },
            "details": []
        }
        
        return report
    
    async def generate_occupancy_rate_report(
        self,
        period: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """
        Generate occupancy rate report
        """
        report = {
            "report_type": ReportType.OCCUPANCY_RATE,
            "generated_at": datetime.utcnow(),
            "period": period,
            "summary": {
                "current_occupancy_rate": 72.0,
                "average_occupancy_rate": 70.5,
                "highest_occupancy_rate": 75.0,
                "lowest_occupancy_rate": 68.0,
                "by_size": {
                    "small": 75.0,
                    "medium": 75.0,
                    "large": 70.0,
                    "extra_large": 50.0
                },
                "by_branch": [],
                "trends": [
                    {"date": "2026-01-01", "rate": 68.0},
                    {"date": "2026-02-01", "rate": 70.0},
                    {"date": "2026-03-01", "rate": 72.0}
                ]
            }
        }
        
        return report
    
    async def generate_customer_demographics_report(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate customer demographics report
        """
        report = {
            "report_type": ReportType.CUSTOMER_DEMOGRAPHICS,
            "generated_at": datetime.utcnow(),
            "branch_id": branch_id,
            "summary": {
                "total_customers": 180,
                "by_category": {
                    "regular": 120,
                    "premium": 30,
                    "senior_citizen": 20,
                    "staff": 10
                },
                "by_age_group": {
                    "18-30": 20,
                    "31-45": 60,
                    "46-60": 70,
                    "60+": 30
                },
                "by_gender": {
                    "male": 100,
                    "female": 70,
                    "other": 10
                },
                "by_occupation": {
                    "salaried": 90,
                    "business": 50,
                    "professional": 30,
                    "retired": 10
                },
                "by_locker_purpose": {
                    "jewelry": 100,
                    "documents": 50,
                    "cash": 20,
                    "other": 10
                }
            }
        }
        
        return report
    
    # ==================== HELPER METHODS ====================
    
    async def get_report_list(
        self,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of generated reports
        """
        reports = []
        # Placeholder - would query database
        
        return reports
    
    async def get_report_details(
        self,
        report_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed report by ID
        """
        # Placeholder - would query database
        report = {
            "id": report_id,
            "report_type": ReportType.ALLOCATION_REGISTER,
            "status": ReportStatus.COMPLETED,
            "generated_at": datetime.utcnow(),
            "generated_by": self.user_id,
            "file_path": "/reports/allocation_register_2026-07-15.pdf"
        }
        
        return report
    
    async def export_report(
        self,
        report_data: Dict[str, Any],
        format: ExportFormat
    ) -> Dict[str, Any]:
        """
        Export report to specified format
        """
        export_result = {
            "success": True,
            "format": format,
            "file_path": f"/exports/report_{uuid.uuid4().hex[:8]}.{format.value}",
            "file_size": 0,
            "exported_at": datetime.utcnow()
        }
        
        return export_result
    
    def _get_date_range(
        self,
        period: ReportPeriod,
        custom_start: Optional[datetime] = None,
        custom_end: Optional[datetime] = None
    ) -> Dict[str, datetime]:
        """
        Get date range based on period
        """
        now = datetime.utcnow()
        
        if period == ReportPeriod.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == ReportPeriod.YESTERDAY:
            yesterday = now - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = yesterday.replace(hour=23, minute=59, second=59)
        elif period == ReportPeriod.THIS_WEEK:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == ReportPeriod.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == ReportPeriod.LAST_MONTH:
            first_day_this_month = now.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            start = last_day_last_month.replace(day=1, hour=0, minute=0, second=0)
            end = last_day_last_month.replace(hour=23, minute=59, second=59)
        elif period == ReportPeriod.THIS_YEAR:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == ReportPeriod.CUSTOM:
            start = custom_start or now
            end = custom_end or now
        else:
            start = now
            end = now
        
        return {"start": start, "end": end}
    
    async def get_statistics(
        self,
        metric: str,
        period: ReportPeriod = ReportPeriod.THIS_MONTH
    ) -> Dict[str, Any]:
        """
        Get specific statistics
        """
        date_range = self._get_date_range(period)
        
        stats = {
            "metric": metric,
            "period": period,
            "date_range": date_range,
            "value": 0,
            "comparison": {
                "previous_period": 0,
                "change_percentage": 0.0
            }
        }
        
        return stats

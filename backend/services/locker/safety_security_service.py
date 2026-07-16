"""
Locker Safety & Security Service
Handles physical security, insurance, and incident management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid


# ==================== ENUMS ====================

class VaultAccessType(str, Enum):
    """Types of vault access"""
    REGULAR_OPERATION = "regular_operation"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    AUDIT = "audit"
    INCIDENT_RESPONSE = "incident_response"


class SecurityEventType(str, Enum):
    """Types of security events"""
    VAULT_OPENED = "vault_opened"
    VAULT_CLOSED = "vault_closed"
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    ALARM_TRIGGERED = "alarm_triggered"
    CCTV_OFFLINE = "cctv_offline"
    DUAL_CUSTODY_VIOLATION = "dual_custody_violation"
    TIME_LOCK_OVERRIDE = "time_lock_override"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class SecurityEventSeverity(str, Enum):
    """Severity levels for security events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class InsuranceType(str, Enum):
    """Types of insurance"""
    BANK_COVERAGE = "bank_coverage"
    CUSTOMER_OPTIONAL = "customer_optional"
    COMPREHENSIVE = "comprehensive"
    THIRD_PARTY = "third_party"


class InsuranceStatus(str, Enum):
    """Insurance policy status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING_RENEWAL = "pending_renewal"
    SUSPENDED = "suspended"


class IncidentType(str, Enum):
    """Types of security incidents"""
    THEFT = "theft"
    BURGLARY = "burglary"
    FIRE = "fire"
    WATER_DAMAGE = "water_damage"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    NATURAL_CALAMITY = "natural_calamity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    VANDALISM = "vandalism"
    TECHNICAL_FAILURE = "technical_failure"
    OTHER = "other"


class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class IncidentStatus(str, Enum):
    """Incident handling status"""
    REPORTED = "reported"
    UNDER_INVESTIGATION = "under_investigation"
    EVIDENCE_COLLECTED = "evidence_collected"
    REPORTED_TO_AUTHORITIES = "reported_to_authorities"
    CLAIM_FILED = "claim_filed"
    COMPENSATION_PROCESSED = "compensation_processed"
    CLOSED = "closed"


class CompensationStatus(str, Enum):
    """Customer compensation status"""
    PENDING_ASSESSMENT = "pending_assessment"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


# ==================== SERVICE CLASS ====================

class LockerSafetySecurityService:
    """
    Service for managing locker safety and security operations
    Handles physical security, insurance, and incident management
    """
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== VAULT OPERATIONS ====================
    
    async def open_vault(
        self,
        branch_id: str,
        access_type: VaultAccessType,
        official_1_id: str,
        official_2_id: str,
        purpose: str,
        time_lock_override: bool = False,
        override_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Open vault with dual custody requirement
        Records security event and validates time lock
        """
        # Validate dual custody (two different officials)
        if official_1_id == official_2_id:
            raise ValueError("Dual custody requires two different officials")
        
        # Check time lock (if not override)
        if not time_lock_override:
            if not await self._validate_time_lock(branch_id):
                raise ValueError("Vault time lock is active. Cannot open at this time.")
        
        # Create vault access record
        access_record = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "branch_id": branch_id,
            "access_type": access_type,
            "official_1_id": official_1_id,
            "official_2_id": official_2_id,
            "purpose": purpose,
            "opened_at": datetime.utcnow(),
            "time_lock_override": time_lock_override,
            "override_reason": override_reason,
            "created_by": self.user_id
        }
        
        # Log security event
        await self._log_security_event(
            branch_id=branch_id,
            event_type=SecurityEventType.VAULT_OPENED,
            severity=SecurityEventSeverity.HIGH if time_lock_override else SecurityEventSeverity.MEDIUM,
            description=f"Vault opened by {official_1_id} and {official_2_id} for {purpose}",
            officials=[official_1_id, official_2_id]
        )
        
        return {
            "success": True,
            "access_record": access_record,
            "message": "Vault opened successfully"
        }
    
    async def close_vault(
        self,
        access_record_id: str,
        official_1_id: str,
        official_2_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close vault with dual custody verification
        """
        # Get access record
        # access_record = self.db.query(VaultAccess).filter_by(id=access_record_id).first()
        
        # Update closed timestamp
        closed_at = datetime.utcnow()
        
        # Log security event
        await self._log_security_event(
            branch_id="branch_from_record",
            event_type=SecurityEventType.VAULT_CLOSED,
            severity=SecurityEventSeverity.LOW,
            description=f"Vault closed by {official_1_id} and {official_2_id}",
            officials=[official_1_id, official_2_id]
        )
        
        return {
            "success": True,
            "closed_at": closed_at,
            "message": "Vault closed successfully"
        }

    
    async def record_cctv_status(
        self,
        branch_id: str,
        camera_id: str,
        status: str,
        recording_status: bool,
        last_check: datetime
    ) -> Dict[str, Any]:
        """
        Record CCTV camera status for monitoring
        """
        cctv_record = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "branch_id": branch_id,
            "camera_id": camera_id,
            "status": status,
            "recording_status": recording_status,
            "last_check": last_check,
            "checked_by": self.user_id,
            "created_at": datetime.utcnow()
        }
        
        # If camera offline, log security event
        if status == "offline" or not recording_status:
            await self._log_security_event(
                branch_id=branch_id,
                event_type=SecurityEventType.CCTV_OFFLINE,
                severity=SecurityEventSeverity.HIGH,
                description=f"CCTV camera {camera_id} is offline or not recording",
                additional_data={"camera_id": camera_id}
            )
        
        return {
            "success": True,
            "cctv_record": cctv_record
        }
    
    async def trigger_alarm(
        self,
        branch_id: str,
        alarm_type: str,
        triggered_by: str,
        location: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Record alarm trigger event
        """
        alarm_event = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "branch_id": branch_id,
            "alarm_type": alarm_type,
            "triggered_by": triggered_by,
            "location": location,
            "reason": reason,
            "triggered_at": datetime.utcnow(),
            "acknowledged": False
        }
        
        # Log critical security event
        await self._log_security_event(
            branch_id=branch_id,
            event_type=SecurityEventType.ALARM_TRIGGERED,
            severity=SecurityEventSeverity.CRITICAL,
            description=f"{alarm_type} alarm triggered at {location}: {reason}",
            additional_data=alarm_event
        )
        
        return {"success": True, "alarm_event": alarm_event}
    
    # ==================== INSURANCE MANAGEMENT ====================
    
    async def create_insurance_policy(
        self,
        policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new insurance policy (bank or customer)
        """
        policy = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "policy_number": f"INS-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            "policy_type": policy_data.get("policy_type"),
            "locker_id": policy_data.get("locker_id"),
            "customer_id": policy_data.get("customer_id"),
            "insurer_name": policy_data.get("insurer_name"),
            "coverage_amount": policy_data.get("coverage_amount"),
            "premium_amount": policy_data.get("premium_amount"),
            "start_date": policy_data.get("start_date"),
            "end_date": policy_data.get("end_date"),
            "status": InsuranceStatus.ACTIVE,
            "terms_conditions": policy_data.get("terms_conditions"),
            "created_at": datetime.utcnow(),
            "created_by": self.user_id
        }
        
        return {"success": True, "policy": policy}
    
    async def renew_insurance_policy(
        self,
        policy_id: str,
        new_end_date: datetime,
        premium_amount: float
    ) -> Dict[str, Any]:
        """
        Renew existing insurance policy
        """
        renewal_record = {
            "id": str(uuid.uuid4()),
            "policy_id": policy_id,
            "renewed_at": datetime.utcnow(),
            "new_end_date": new_end_date,
            "premium_paid": premium_amount,
            "renewed_by": self.user_id
        }
        
        return {"success": True, "renewal": renewal_record}
    
    async def file_insurance_claim(
        self,
        claim_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        File insurance claim for incident
        """
        claim = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "claim_number": f"CLM-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            "policy_id": claim_data.get("policy_id"),
            "incident_id": claim_data.get("incident_id"),
            "claim_amount": claim_data.get("claim_amount"),
            "claim_description": claim_data.get("claim_description"),
            "supporting_documents": claim_data.get("supporting_documents", []),
            "filed_date": datetime.utcnow(),
            "status": "filed",
            "filed_by": self.user_id
        }
        
        return {"success": True, "claim": claim}

    
    # ==================== INCIDENT MANAGEMENT ====================
    
    async def report_incident(
        self,
        incident_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Report security incident
        """
        incident = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "incident_number": f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            "incident_type": incident_data.get("incident_type"),
            "severity": incident_data.get("severity"),
            "branch_id": incident_data.get("branch_id"),
            "affected_lockers": incident_data.get("affected_lockers", []),
            "incident_date": incident_data.get("incident_date"),
            "description": incident_data.get("description"),
            "reported_by": self.user_id,
            "reported_at": datetime.utcnow(),
            "status": IncidentStatus.REPORTED,
            "rbi_notified": False,
            "police_notified": False
        }
        
        # Log critical security event
        await self._log_security_event(
            branch_id=incident_data.get("branch_id"),
            event_type=SecurityEventType.ALARM_TRIGGERED,
            severity=SecurityEventSeverity.EMERGENCY,
            description=f"Incident reported: {incident_data.get('incident_type')}",
            additional_data=incident
        )
        
        return {"success": True, "incident": incident}
    
    async def investigate_incident(
        self,
        incident_id: str,
        investigation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update incident with investigation findings
        """
        investigation = {
            "incident_id": incident_id,
            "investigator_id": self.user_id,
            "investigation_date": datetime.utcnow(),
            "findings": investigation_data.get("findings"),
            "evidence_collected": investigation_data.get("evidence_collected", []),
            "root_cause": investigation_data.get("root_cause"),
            "recommendations": investigation_data.get("recommendations")
        }
        
        return {"success": True, "investigation": investigation}
    
    async def notify_authorities(
        self,
        incident_id: str,
        authority_type: str,  # "rbi" or "police"
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Record notification to RBI/Police
        """
        notification = {
            "id": str(uuid.uuid4()),
            "incident_id": incident_id,
            "authority_type": authority_type,
            "notified_at": datetime.utcnow(),
            "reference_number": notification_data.get("reference_number"),
            "contact_person": notification_data.get("contact_person"),
            "acknowledgment_received": notification_data.get("acknowledgment_received", False),
            "notified_by": self.user_id
        }
        
        return {"success": True, "notification": notification}
    
    async def process_compensation(
        self,
        incident_id: str,
        compensation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process customer compensation for incident
        """
        compensation = {
            "id": str(uuid.uuid4()),
            "incident_id": incident_id,
            "customer_id": compensation_data.get("customer_id"),
            "locker_id": compensation_data.get("locker_id"),
            "compensation_amount": compensation_data.get("compensation_amount"),
            "compensation_type": compensation_data.get("compensation_type"),  # cash, insurance, etc
            "assessment_date": datetime.utcnow(),
            "approved_by": compensation_data.get("approved_by"),
            "payment_date": compensation_data.get("payment_date"),
            "status": CompensationStatus.APPROVED,
            "notes": compensation_data.get("notes"),
            "processed_by": self.user_id
        }
        
        return {"success": True, "compensation": compensation}
    
    # ==================== QUERY METHODS ====================
    
    async def get_security_dashboard(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get security dashboard with real-time status
        """
        # In real implementation, query database
        dashboard = {
            "vault_status": "closed",
            "last_opened": datetime.utcnow() - timedelta(hours=2),
            "cctv_cameras_online": 12,
            "cctv_cameras_total": 12,
            "active_alarms": 0,
            "recent_security_events": [],
            "incidents_this_month": 0,
            "active_insurance_policies": 145,
            "expiring_policies_30_days": 8
        }
        
        return dashboard
    
    async def get_vault_access_log(
        self,
        branch_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get vault access history
        """
        # Query vault access records
        access_logs = []  # From database
        
        return {
            "access_logs": access_logs,
            "total": len(access_logs)
        }
    
    async def get_security_events(
        self,
        branch_id: Optional[str] = None,
        severity: Optional[SecurityEventSeverity] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get security events with filters
        """
        events = []  # From database
        
        return {
            "events": events,
            "total": len(events)
        }
    
    async def get_insurance_policies(
        self,
        customer_id: Optional[str] = None,
        status: Optional[InsuranceStatus] = None
    ) -> Dict[str, Any]:
        """
        Get insurance policies with filters
        """
        policies = []  # From database
        
        return {
            "policies": policies,
            "total": len(policies)
        }
    
    async def get_incidents(
        self,
        branch_id: Optional[str] = None,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None
    ) -> Dict[str, Any]:
        """
        Get incidents with filters
        """
        incidents = []  # From database
        
        return {
            "incidents": incidents,
            "total": len(incidents)
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get safety & security statistics
        """
        stats = {
            "total_incidents": 0,
            "incidents_by_type": {},
            "incidents_by_severity": {},
            "open_incidents": 0,
            "total_insurance_policies": 0,
            "active_policies": 0,
            "expired_policies": 0,
            "total_claims_filed": 0,
            "claims_approved": 0,
            "total_compensation_paid": 0,
            "security_events_today": 0,
            "critical_events_this_week": 0,
            "vault_opens_this_month": 0,
            "cctv_uptime_percentage": 99.8
        }
        
        return stats
    
    # ==================== HELPER METHODS ====================
    
    async def _validate_time_lock(self, branch_id: str) -> bool:
        """
        Check if current time is within vault operating hours
        """
        current_time = datetime.utcnow().time()
        # In real implementation, check branch operating hours
        # For now, assume 9 AM to 5 PM
        start_time = datetime.strptime("09:00", "%H:%M").time()
        end_time = datetime.strptime("17:00", "%H:%M").time()
        
        return start_time <= current_time <= end_time
    
    async def _log_security_event(
        self,
        branch_id: str,
        event_type: SecurityEventType,
        severity: SecurityEventSeverity,
        description: str,
        officials: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log security event for audit trail
        """
        event = {
            "id": str(uuid.uuid4()),
            "tenant_id": self.tenant_id,
            "branch_id": branch_id,
            "event_type": event_type,
            "severity": severity,
            "description": description,
            "officials_involved": officials or [],
            "additional_data": additional_data,
            "event_timestamp": datetime.utcnow(),
            "logged_by": self.user_id
        }
        
        # In real implementation, save to database
        # self.db.add(SecurityEvent(**event))
        # self.db.commit()
        
        return event

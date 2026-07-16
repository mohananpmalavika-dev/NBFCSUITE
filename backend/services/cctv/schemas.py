"""
CCTV Infrastructure Management Schemas

Comprehensive schemas for CCTV surveillance system including:
- Camera installation and management
- Recording and storage
- Live monitoring
- Video analytics and AI
- Incident management
- Compliance and audit
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
import uuid


# ==================== ENUMS ====================

class CameraType(str, Enum):
    """Camera types"""
    DOME = "dome"
    BULLET = "bullet"
    PTZ = "ptz"
    BOX = "box"
    FISHEYE = "fisheye"
    TURRET = "turret"
    THERMAL = "thermal"
    ANPR = "anpr"  # License Plate Recognition


class CameraLocation(str, Enum):
    """Standard camera locations"""
    ENTRANCE = "entrance"
    EXIT = "exit"
    CASH_COUNTER = "cash_counter"
    MANAGER_CABIN = "manager_cabin"
    STRONG_ROOM = "strong_room"
    VAULT = "vault"
    LOCKER_ROOM = "locker_room"
    ATM_CABIN = "atm_cabin"
    PARKING = "parking"
    PERIMETER = "perimeter"
    STAIRCASE = "staircase"
    CORRIDOR = "corridor"
    SERVER_ROOM = "server_room"
    BACK_OFFICE = "back_office"
    WAITING_AREA = "waiting_area"
    TERRACE = "terrace"


class CameraStatus(str, Enum):
    """Camera operational status"""
    ONLINE = "online"
    OFFLINE = "offline"
    RECORDING = "recording"
    MAINTENANCE = "maintenance"
    FAULTY = "faulty"
    DISABLED = "disabled"
    TESTING = "testing"


class RecordingStatus(str, Enum):
    """Recording status"""
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    DISK_FULL = "disk_full"


class RecordingQuality(str, Enum):
    """Recording quality presets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"
    CUSTOM = "custom"


class StorageType(str, Enum):
    """Storage type"""
    HOT = "hot"  # Fast access, recent recordings
    WARM = "warm"  # Medium access
    COLD = "cold"  # Archival, slower access
    CLOUD = "cloud"


class AlertType(str, Enum):
    """AI alert types"""
    MOTION_DETECTED = "motion_detected"
    PERSON_DETECTED = "person_detected"
    FACE_RECOGNIZED = "face_recognized"
    OBJECT_DETECTED = "object_detected"
    INTRUSION = "intrusion"
    LOITERING = "loitering"
    LINE_CROSSING = "line_crossing"
    CROWD_DETECTED = "crowd_detected"
    UNATTENDED_OBJECT = "unattended_object"
    MISSING_OBJECT = "missing_object"
    FIRE_SMOKE = "fire_smoke"
    LICENSE_PLATE = "license_plate"
    CAMERA_TAMPERED = "camera_tampered"
    CAMERA_BLOCKED = "camera_blocked"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert processing status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"
    ESCALATED = "escalated"


class IncidentType(str, Enum):
    """Incident types"""
    THEFT = "theft"
    ROBBERY = "robbery"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCIDENT = "accident"
    CUSTOMER_DISPUTE = "customer_dispute"
    VANDALISM = "vandalism"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FIRE = "fire"
    MEDICAL_EMERGENCY = "medical_emergency"
    ATM_TAMPERING = "atm_tampering"
    VEHICLE_ACCIDENT = "vehicle_accident"
    OTHER = "other"


class IncidentStatus(str, Enum):
    """Incident status"""
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    EVIDENCE_COLLECTED = "evidence_collected"
    POLICE_NOTIFIED = "police_notified"
    CLOSED = "closed"
    REOPENED = "reopened"


class MaintenanceType(str, Enum):
    """Maintenance type"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    UPGRADE = "upgrade"
    CALIBRATION = "calibration"


class MaintenanceStatus(str, Enum):
    """Maintenance status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING_PARTS = "pending_parts"


# ==================== CAMERA INFRASTRUCTURE SCHEMAS ====================

class CameraSpecifications(BaseModel):
    """Camera technical specifications"""
    resolution: str = Field(..., description="e.g., 1080p, 4MP, 8MP")
    frame_rate: int = Field(..., ge=15, le=60, description="FPS")
    field_of_view: Optional[str] = Field(None, description="e.g., 90°, 110°")
    ir_distance_meters: Optional[int] = Field(None, ge=0, description="Night vision range")
    weatherproof_rating: Optional[str] = Field(None, description="e.g., IP66, IP67")
    min_illumination_lux: Optional[float] = Field(None, ge=0)
    lens_type: Optional[str] = None
    focal_length_mm: Optional[str] = None
    zoom_optical: Optional[str] = None
    zoom_digital: Optional[str] = None
    pan_range: Optional[str] = None
    tilt_range: Optional[str] = None
    ptz_speed: Optional[str] = None
    audio_support: bool = False
    two_way_audio: bool = False
    sd_card_slot: bool = False
    poe_support: bool = True
    power_consumption_watts: Optional[int] = None


class CCTVCameraBase(BaseModel):
    """Base schema for CCTV camera"""
    camera_name: str = Field(..., min_length=1, max_length=200)
    camera_id: str = Field(..., min_length=1, max_length=100)
    
    # Location
    branch_id: uuid.UUID
    branch_name: Optional[str] = None
    location_type: CameraLocation
    location_description: str = Field(..., min_length=1)
    floor: Optional[str] = None
    zone: Optional[str] = None
    coordinates: Optional[str] = Field(None, description="Lat,Long or building coordinates")
    
    # Camera details
    camera_type: CameraType
    manufacturer: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    serial_number: str = Field(..., min_length=1)
    firmware_version: Optional[str] = None
    
    # Specifications
    specifications: CameraSpecifications
    
    # Network
    ip_address: str = Field(..., min_length=7)
    mac_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    onvif_support: bool = True
    port: int = Field(default=554, ge=1, le=65535)
    
    # Installation
    installation_date: date
    installation_height_meters: Optional[float] = None
    installation_angle: Optional[str] = None
    mounting_type: Optional[str] = None
    
    # Configuration
    recording_enabled: bool = True
    motion_detection_enabled: bool = True
    night_vision_enabled: bool = True
    audio_recording_enabled: bool = False
    
    # Status
    status: CameraStatus = CameraStatus.ONLINE
    is_critical: bool = False
    priority_level: int = Field(default=1, ge=1, le=5)
    
    # Coverage
    coverage_area: Optional[str] = None
    overlapping_cameras: Optional[List[str]] = None
    
    # Maintenance
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_interval_days: int = Field(default=180, ge=1)
    
    # Storage
    storage_days_required: int = Field(default=180, ge=1)
    
    remarks: Optional[str] = None


class CCTVCameraCreate(CCTVCameraBase):
    """Schema for creating CCTV camera"""
    pass


class CCTVCameraUpdate(BaseModel):
    """Schema for updating camera"""
    camera_name: Optional[str] = None
    location_description: Optional[str] = None
    ip_address: Optional[str] = None
    firmware_version: Optional[str] = None
    status: Optional[CameraStatus] = None
    recording_enabled: Optional[bool] = None
    motion_detection_enabled: Optional[bool] = None
    next_maintenance_date: Optional[date] = None
    remarks: Optional[str] = None


class CCTVCameraResponse(CCTVCameraBase):
    """Schema for camera response"""
    id: uuid.UUID
    tenant_id: str
    
    # Health metrics
    uptime_percentage: float = 0.0
    last_online_at: Optional[datetime] = None
    last_offline_at: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Recording stats
    total_recording_hours: float = 0.0
    storage_used_gb: float = 0.0
    
    # Alerts
    total_alerts_generated: int = 0
    critical_alerts_active: int = 0
    
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ==================== RECORDING & STORAGE SCHEMAS ====================

class DVRNVRConfigBase(BaseModel):
    """Base schema for DVR/NVR configuration"""
    device_name: str = Field(..., min_length=1)
    device_type: str = Field(..., description="DVR or NVR")
    
    branch_id: uuid.UUID
    location: str
    
    # Device details
    manufacturer: str
    model: str
    serial_number: str
    firmware_version: Optional[str] = None
    
    # Capacity
    total_channels: int = Field(..., ge=1)
    used_channels: int = Field(default=0, ge=0)
    available_channels: int = Field(default=0, ge=0)
    
    # Storage
    total_storage_tb: Decimal = Field(..., gt=0)
    used_storage_tb: Decimal = Field(default=Decimal("0"), ge=0)
    available_storage_tb: Decimal = Field(default=Decimal("0"), ge=0)
    
    # RAID configuration
    raid_type: Optional[str] = Field(None, description="RAID 0, 1, 5, 6, 10")
    raid_status: Optional[str] = None
    
    # Recording settings
    recording_quality: RecordingQuality = RecordingQuality.HIGH
    compression_format: str = Field(default="H.265", description="H.264, H.265, etc.")
    bitrate_kbps: int = Field(default=4096, ge=512)
    
    # Retention
    retention_days_hot: int = Field(default=30, ge=1)
    retention_days_cold: int = Field(default=150, ge=1)
    
    # Network
    ip_address: str
    port: int = Field(default=8000, ge=1, le=65535)
    remote_access_enabled: bool = True
    
    # Backup
    backup_enabled: bool = True
    backup_location: Optional[str] = None
    backup_frequency_hours: int = Field(default=24, ge=1)
    
    # Redundancy
    redundant_device_id: Optional[uuid.UUID] = None
    failover_enabled: bool = False
    
    status: str = "active"
    remarks: Optional[str] = None


class DVRNVRConfigCreate(DVRNVRConfigBase):
    """Schema for creating DVR/NVR config"""
    pass


class DVRNVRConfigUpdate(BaseModel):
    """Schema for updating DVR/NVR config"""
    firmware_version: Optional[str] = None
    recording_quality: Optional[RecordingQuality] = None
    bitrate_kbps: Optional[int] = None
    retention_days_hot: Optional[int] = None
    retention_days_cold: Optional[int] = None
    backup_enabled: Optional[bool] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class DVRNVRConfigResponse(DVRNVRConfigBase):
    """Schema for DVR/NVR response"""
    id: uuid.UUID
    tenant_id: str
    
    # Health
    uptime_percentage: float = 0.0
    disk_health_status: str = "healthy"
    temperature_celsius: Optional[float] = None
    
    # Connected cameras
    connected_cameras: int = 0
    recording_cameras: int = 0
    offline_cameras: int = 0
    
    # Storage alerts
    storage_alert_threshold_percentage: int = 80
    storage_alert_active: bool = False
    
    last_backup_date: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VIDEO ANALYTICS & AI SCHEMAS ====================

class AnalyticsConfigBase(BaseModel):
    """Base schema for analytics configuration"""
    camera_id: uuid.UUID
    analytics_name: str = Field(..., min_length=1)
    
    # Analytics types enabled
    motion_detection: bool = True
    person_detection: bool = True
    face_recognition: bool = False
    object_detection: bool = False
    crowd_detection: bool = False
    loitering_detection: bool = False
    line_crossing_detection: bool = False
    intrusion_detection: bool = True
    unattended_object_detection: bool = False
    missing_object_detection: bool = False
    fire_smoke_detection: bool = True
    license_plate_recognition: bool = False
    
    # Sensitivity
    detection_sensitivity: int = Field(default=70, ge=0, le=100)
    
    # ROI (Region of Interest)
    roi_enabled: bool = False
    roi_coordinates: Optional[str] = None
    
    # Scheduling
    schedule_enabled: bool = False
    active_hours: Optional[str] = None
    
    # Alert settings
    alert_enabled: bool = True
    alert_threshold: int = Field(default=1, ge=1)
    cooldown_seconds: int = Field(default=60, ge=0)
    
    # Actions
    record_on_detection: bool = True
    snapshot_on_detection: bool = True
    notification_on_detection: bool = True
    
    is_active: bool = True
    remarks: Optional[str] = None


class AnalyticsConfigCreate(AnalyticsConfigBase):
    """Schema for creating analytics config"""
    pass


class AnalyticsConfigUpdate(BaseModel):
    """Schema for updating analytics config"""
    motion_detection: Optional[bool] = None
    person_detection: Optional[bool] = None
    face_recognition: Optional[bool] = None
    detection_sensitivity: Optional[int] = None
    alert_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class AnalyticsConfigResponse(AnalyticsConfigBase):
    """Schema for analytics config response"""
    id: uuid.UUID
    tenant_id: str
    
    total_detections: int = 0
    total_alerts_generated: int = 0
    false_positives: int = 0
    accuracy_percentage: float = 0.0
    
    last_detection_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIAlertBase(BaseModel):
    """Base schema for AI alert"""
    camera_id: uuid.UUID
    analytics_config_id: Optional[uuid.UUID] = None
    
    alert_type: AlertType
    alert_severity: AlertSeverity
    alert_timestamp: datetime
    
    # Detection details
    detected_object: Optional[str] = None
    confidence_score: float = Field(..., ge=0, le=100)
    bounding_box: Optional[str] = None
    
    # Video evidence
    snapshot_path: Optional[str] = None
    video_clip_path: Optional[str] = None
    video_start_time: Optional[datetime] = None
    video_end_time: Optional[datetime] = None
    
    # Location
    location_description: Optional[str] = None
    
    # Response
    auto_acknowledged: bool = False
    notification_sent: bool = False
    notification_channels: Optional[str] = None
    
    description: Optional[str] = None
    remarks: Optional[str] = None


class AIAlertCreate(AIAlertBase):
    """Schema for creating AI alert"""
    pass


class AIAlertUpdate(BaseModel):
    """Schema for updating alert"""
    status: Optional[AlertStatus] = None
    acknowledged_by: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None
    false_alarm: Optional[bool] = None
    remarks: Optional[str] = None


class AIAlertResponse(AIAlertBase):
    """Schema for AI alert response"""
    id: uuid.UUID
    alert_id: str
    tenant_id: str
    status: AlertStatus
    
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[uuid.UUID] = None
    
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None
    
    escalated: bool = False
    escalated_to: Optional[uuid.UUID] = None
    escalated_at: Optional[datetime] = None
    
    false_alarm: bool = False
    false_alarm_reason: Optional[str] = None
    
    linked_incident_id: Optional[uuid.UUID] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== INCIDENT MANAGEMENT SCHEMAS ====================

class CCTVIncidentBase(BaseModel):
    """Base schema for CCTV incident"""
    incident_number: str = Field(..., min_length=1)
    
    branch_id: uuid.UUID
    incident_type: IncidentType
    incident_date: date
    incident_time: time
    incident_location: str
    
    # Details
    incident_description: str = Field(..., min_length=10)
    persons_involved: Optional[str] = None
    witnesses: Optional[str] = None
    
    # Video evidence
    camera_ids: List[uuid.UUID] = []
    video_start_time: datetime
    video_end_time: datetime
    
    # Investigation
    reported_by: uuid.UUID
    assigned_to: Optional[uuid.UUID] = None
    
    # Police involvement
    police_notified: bool = False
    fir_number: Optional[str] = None
    police_station: Optional[str] = None
    police_contact: Optional[str] = None
    
    # Insurance
    insurance_claim: bool = False
    insurance_claim_number: Optional[str] = None
    estimated_loss: Optional[Decimal] = None
    
    priority: int = Field(default=1, ge=1, le=5)
    remarks: Optional[str] = None


class CCTVIncidentCreate(CCTVIncidentBase):
    """Schema for creating incident"""
    pass


class CCTVIncidentUpdate(BaseModel):
    """Schema for updating incident"""
    status: Optional[IncidentStatus] = None
    incident_description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    police_notified: Optional[bool] = None
    fir_number: Optional[str] = None
    insurance_claim: Optional[bool] = None
    remarks: Optional[str] = None


class CCTVIncidentResponse(CCTVIncidentBase):
    """Schema for incident response"""
    id: uuid.UUID
    tenant_id: str
    status: IncidentStatus
    
    # Video clips collected
    video_clips_collected: int = 0
    video_clips_paths: Optional[List[str]] = []
    snapshots_collected: int = 0
    snapshots_paths: Optional[List[str]] = []
    
    # Evidence package
    evidence_package_created: bool = False
    evidence_package_path: Optional[str] = None
    evidence_package_password: Optional[str] = None
    
    # Timeline
    investigation_started_at: Optional[datetime] = None
    investigation_completed_at: Optional[datetime] = None
    police_notified_at: Optional[datetime] = None
    
    # Resolution
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    resolution_summary: Optional[str] = None
    
    # Actions taken
    actions_taken: Optional[str] = None
    preventive_measures: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VIDEO SEARCH & RETRIEVAL SCHEMAS ====================

class VideoSearchRequest(BaseModel):
    """Schema for video search"""
    camera_ids: Optional[List[uuid.UUID]] = None
    branch_id: Optional[uuid.UUID] = None
    location_type: Optional[CameraLocation] = None
    
    # Time range
    start_datetime: datetime
    end_datetime: datetime
    
    # Search criteria
    search_by_motion: bool = False
    search_by_person: bool = False
    search_by_vehicle: bool = False
    search_by_object: Optional[str] = None
    
    # Filters
    min_confidence: float = Field(default=70.0, ge=0, le=100)
    
    # Output
    include_snapshots: bool = True
    max_results: int = Field(default=100, ge=1, le=1000)


class VideoClipRequest(BaseModel):
    """Schema for video clip extraction"""
    camera_id: uuid.UUID
    start_datetime: datetime
    end_datetime: datetime
    
    clip_name: Optional[str] = None
    quality: RecordingQuality = RecordingQuality.HIGH
    include_audio: bool = True
    
    # Watermark
    add_watermark: bool = True
    watermark_text: Optional[str] = None
    
    # Authentication
    password_protect: bool = False
    password: Optional[str] = None
    
    purpose: str = Field(..., min_length=5)


class VideoClipResponse(BaseModel):
    """Schema for video clip response"""
    clip_id: str
    camera_id: uuid.UUID
    start_datetime: datetime
    end_datetime: datetime
    duration_seconds: int
    file_path: str
    file_size_mb: float
    format: str
    resolution: str
    created_at: datetime
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


# ==================== MAINTENANCE SCHEMAS ====================

class CCTVMaintenanceBase(BaseModel):
    """Base schema for CCTV maintenance"""
    maintenance_number: str = Field(..., min_length=1)
    
    camera_id: Optional[uuid.UUID] = None
    dvr_nvr_id: Optional[uuid.UUID] = None
    component_type: str = Field(..., description="camera, dvr, nvr, storage, network")
    
    maintenance_type: MaintenanceType
    scheduled_date: date
    
    # Issue
    issue_description: Optional[str] = None
    reported_by: Optional[uuid.UUID] = None
    reported_date: Optional[date] = None
    
    # Work
    work_description: str = Field(..., min_length=5)
    technician_name: Optional[str] = None
    technician_contact: Optional[str] = None
    vendor_name: Optional[str] = None
    
    # Parts
    parts_replaced: Optional[str] = None
    parts_cost: Decimal = Field(default=Decimal("0"), ge=0)
    labor_cost: Decimal = Field(default=Decimal("0"), ge=0)
    other_charges: Decimal = Field(default=Decimal("0"), ge=0)
    total_cost: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Downtime
    downtime_start: Optional[datetime] = None
    downtime_end: Optional[datetime] = None
    
    remarks: Optional[str] = None


class CCTVMaintenanceCreate(CCTVMaintenanceBase):
    """Schema for creating maintenance"""
    pass


class CCTVMaintenanceUpdate(BaseModel):
    """Schema for updating maintenance"""
    status: Optional[MaintenanceStatus] = None
    completion_date: Optional[date] = None
    work_description: Optional[str] = None
    total_cost: Optional[Decimal] = None
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    remarks: Optional[str] = None


class CCTVMaintenanceResponse(CCTVMaintenanceBase):
    """Schema for maintenance response"""
    id: uuid.UUID
    tenant_id: str
    status: MaintenanceStatus
    
    completion_date: Optional[date] = None
    downtime_hours: Optional[float] = None
    
    # Quality check
    quality_checked: bool = False
    quality_checked_by: Optional[uuid.UUID] = None
    quality_rating: Optional[int] = None
    
    # Invoice
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    payment_status: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== DASHBOARD & ANALYTICS ====================

class CCTVDashboardStats(BaseModel):
    """CCTV system dashboard statistics"""
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    recording_cameras: int
    maintenance_cameras: int
    
    total_storage_tb: float
    used_storage_tb: float
    storage_utilization_percentage: float
    
    active_alerts: int
    critical_alerts: int
    incidents_today: int
    incidents_this_month: int
    
    average_uptime_percentage: float
    cameras_needing_maintenance: int
    
    dvr_nvr_healthy: int
    dvr_nvr_issues: int


class CameraHealthReport(BaseModel):
    """Camera health report"""
    camera_id: uuid.UUID
    camera_name: str
    location: str
    status: CameraStatus
    uptime_percentage: float
    last_online: Optional[datetime]
    issues: List[str]
    maintenance_due: bool


class StorageAnalytics(BaseModel):
    """Storage analytics"""
    total_capacity_tb: float
    used_capacity_tb: float
    available_capacity_tb: float
    utilization_percentage: float
    
    estimated_days_remaining: int
    cleanup_recommended: bool
    
    by_camera: List[Dict[str, Any]]
    by_retention_period: Dict[str, float]


class AlertAnalytics(BaseModel):
    """Alert analytics"""
    total_alerts: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    
    average_response_time_minutes: float
    false_alarm_rate: float
    
    top_cameras: List[Dict[str, Any]]
    hourly_distribution: List[int]


# ==================== FILTERS ====================

class CameraFilter(BaseModel):
    """Camera filter"""
    branch_id: Optional[uuid.UUID] = None
    camera_type: Optional[CameraType] = None
    location_type: Optional[CameraLocation] = None
    status: Optional[CameraStatus] = None
    is_critical: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AlertFilter(BaseModel):
    """Alert filter"""
    camera_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None
    alert_type: Optional[AlertType] = None
    alert_severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class IncidentFilter(BaseModel):
    """Incident filter"""
    branch_id: Optional[uuid.UUID] = None
    incident_type: Optional[IncidentType] = None
    status: Optional[IncidentStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    police_notified: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

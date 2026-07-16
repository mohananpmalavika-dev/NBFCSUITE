"""
CCTV Infrastructure Management - Database Models

SQLAlchemy ORM models for CCTV surveillance system.
Includes camera management, recording, analytics, incidents, and maintenance.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, ForeignKey, JSON, Numeric, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.shared.database.base import Base


class CCTVCamera(Base):
    """CCTV Camera Master Table"""
    __tablename__ = "cctv_cameras"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Basic Information
    camera_name = Column(String(200), nullable=False)
    camera_id = Column(String(100), nullable=False, index=True)
    
    # Location
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    branch_name = Column(String(200))
    location_type = Column(String(50), nullable=False)
    location_description = Column(Text, nullable=False)
    floor = Column(String(50))
    zone = Column(String(100))
    coordinates = Column(String(200))
    
    # Camera Details
    camera_type = Column(String(50), nullable=False)
    manufacturer = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    serial_number = Column(String(200), nullable=False)
    firmware_version = Column(String(100))
    
    # Specifications (JSON)
    specifications = Column(JSON, nullable=False)
    
    # Network Configuration
    ip_address = Column(String(50), nullable=False)
    mac_address = Column(String(50))
    rtsp_url = Column(String(500))
    onvif_support = Column(Boolean, default=True)
    port = Column(Integer, default=554)
    
    # Installation
    installation_date = Column(DateTime, nullable=False)
    installation_height_meters = Column(Float)
    installation_angle = Column(String(50))
    mounting_type = Column(String(100))
    
    # Configuration
    recording_enabled = Column(Boolean, default=True)
    motion_detection_enabled = Column(Boolean, default=True)
    night_vision_enabled = Column(Boolean, default=True)
    audio_recording_enabled = Column(Boolean, default=False)
    
    # Status
    status = Column(String(50), default='online', index=True)
    is_critical = Column(Boolean, default=False)
    priority_level = Column(Integer, default=1)
    
    # Coverage
    coverage_area = Column(Text)
    overlapping_cameras = Column(JSON)
    
    # Maintenance
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime, index=True)
    maintenance_interval_days = Column(Integer, default=180)
    storage_days_required = Column(Integer, default=180)
    
    # Health Metrics
    uptime_percentage = Column(Float, default=100.0)
    last_online_at = Column(DateTime)
    last_offline_at = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)
    total_recording_hours = Column(Float, default=0.0)
    storage_used_gb = Column(Float, default=0.0)
    total_alerts_generated = Column(Integer, default=0)
    critical_alerts_active = Column(Integer, default=0)
    
    # Audit Fields
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(UUID(as_uuid=True))
    
    # Relationships
    analytics_configs = relationship("AnalyticsConfig", back_populates="camera")
    alerts = relationship("AIAlert", back_populates="camera")
    maintenance_records = relationship("CCTVMaintenance", back_populates="camera")
    
    # Indexes
    __table_args__ = (
        Index('idx_camera_tenant_status', 'tenant_id', 'status'),
        Index('idx_camera_branch_location', 'branch_id', 'location_type'),
        Index('idx_camera_serial', 'serial_number'),
    )



class DVRNVRConfig(Base):
    """DVR/NVR Configuration Table"""
    __tablename__ = "dvr_nvr_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    device_name = Column(String(200), nullable=False)
    device_type = Column(String(10), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    
    # Device Details
    manufacturer = Column(String(200), nullable=False)
    model = Column(String(200), nullable=False)
    serial_number = Column(String(200), nullable=False, unique=True)
    firmware_version = Column(String(100))
    
    # Capacity
    total_channels = Column(Integer, nullable=False)
    used_channels = Column(Integer, default=0)
    available_channels = Column(Integer, default=0)
    
    # Storage
    total_storage_tb = Column(Numeric(10, 2), nullable=False)
    used_storage_tb = Column(Numeric(10, 2), default=0)
    available_storage_tb = Column(Numeric(10, 2), default=0)
    
    # RAID
    raid_type = Column(String(20))
    raid_status = Column(String(50))
    
    # Recording Settings
    recording_quality = Column(String(20), default='high')
    compression_format = Column(String(20), default='H.265')
    bitrate_kbps = Column(Integer, default=4096)
    retention_days_hot = Column(Integer, default=30)
    retention_days_cold = Column(Integer, default=150)
    
    # Network
    ip_address = Column(String(50), nullable=False)
    port = Column(Integer, default=8000)
    remote_access_enabled = Column(Boolean, default=True)
    
    # Backup
    backup_enabled = Column(Boolean, default=True)
    backup_location = Column(String(500))
    backup_frequency_hours = Column(Integer, default=24)
    redundant_device_id = Column(UUID(as_uuid=True))
    failover_enabled = Column(Boolean, default=False)
    
    # Health Metrics
    uptime_percentage = Column(Float, default=100.0)
    disk_health_status = Column(String(50), default='healthy')
    temperature_celsius = Column(Float)
    connected_cameras = Column(Integer, default=0)
    recording_cameras = Column(Integer, default=0)
    offline_cameras = Column(Integer, default=0)
    storage_alert_threshold_percentage = Column(Integer, default=80)
    storage_alert_active = Column(Boolean, default=False)
    last_backup_date = Column(DateTime)
    last_health_check = Column(DateTime)
    
    status = Column(String(50), default='active')
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)


class AnalyticsConfig(Base):
    """AI Analytics Configuration"""
    __tablename__ = "analytics_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cctv_cameras.id'), nullable=False)
    analytics_name = Column(String(200), nullable=False)
    
    # Detection Types (14 types)
    motion_detection = Column(Boolean, default=True)
    person_detection = Column(Boolean, default=True)
    face_recognition = Column(Boolean, default=False)
    object_detection = Column(Boolean, default=False)
    crowd_detection = Column(Boolean, default=False)
    loitering_detection = Column(Boolean, default=False)
    line_crossing_detection = Column(Boolean, default=False)
    intrusion_detection = Column(Boolean, default=True)
    unattended_object_detection = Column(Boolean, default=False)
    missing_object_detection = Column(Boolean, default=False)
    fire_smoke_detection = Column(Boolean, default=True)
    license_plate_recognition = Column(Boolean, default=False)
    
    # Configuration
    detection_sensitivity = Column(Integer, default=70)
    roi_enabled = Column(Boolean, default=False)
    roi_coordinates = Column(Text)
    schedule_enabled = Column(Boolean, default=False)
    active_hours = Column(Text)
    
    # Alert Settings
    alert_enabled = Column(Boolean, default=True)
    alert_threshold = Column(Integer, default=1)
    cooldown_seconds = Column(Integer, default=60)
    
    # Actions
    record_on_detection = Column(Boolean, default=True)
    snapshot_on_detection = Column(Boolean, default=True)
    notification_on_detection = Column(Boolean, default=True)
    
    # Statistics
    total_detections = Column(Integer, default=0)
    total_alerts_generated = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    last_detection_at = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    camera = relationship("CCTVCamera", back_populates="analytics_configs")
    alerts = relationship("AIAlert", back_populates="analytics_config")


class AIAlert(Base):
    """AI Generated Alerts"""
    __tablename__ = "ai_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(String(50), unique=True, nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cctv_cameras.id'), nullable=False)
    analytics_config_id = Column(UUID(as_uuid=True), ForeignKey('analytics_configs.id'))
    
    # Alert Details
    alert_type = Column(String(50), nullable=False, index=True)
    alert_severity = Column(String(20), nullable=False, index=True)
    alert_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Detection
    detected_object = Column(String(200))
    confidence_score = Column(Float, nullable=False)
    bounding_box = Column(Text)
    
    # Evidence
    snapshot_path = Column(String(500))
    video_clip_path = Column(String(500))
    video_start_time = Column(DateTime)
    video_end_time = Column(DateTime)
    location_description = Column(Text)
    
    # Response
    status = Column(String(50), default='new', index=True)
    auto_acknowledged = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(Text)
    
    # Workflow
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(UUID(as_uuid=True))
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True))
    resolution_notes = Column(Text)
    
    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_to = Column(UUID(as_uuid=True))
    escalated_at = Column(DateTime)
    
    # Classification
    false_alarm = Column(Boolean, default=False)
    false_alarm_reason = Column(Text)
    linked_incident_id = Column(UUID(as_uuid=True))
    
    description = Column(Text)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    camera = relationship("CCTVCamera", back_populates="alerts")
    analytics_config = relationship("AnalyticsConfig", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alert_camera_time', 'camera_id', 'alert_timestamp'),
        Index('idx_alert_type_severity', 'alert_type', 'alert_severity'),
    )


class CCTVIncident(Base):
    """CCTV Incident Tracking"""
    __tablename__ = "cctv_incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_number = Column(String(50), unique=True, nullable=False, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Incident Details
    incident_type = Column(String(50), nullable=False, index=True)
    incident_date = Column(DateTime, nullable=False, index=True)
    incident_time = Column(String(20), nullable=False)
    incident_location = Column(String(500), nullable=False)
    incident_description = Column(Text, nullable=False)
    persons_involved = Column(Text)
    witnesses = Column(Text)
    
    # Video Evidence
    camera_ids = Column(JSON)
    video_start_time = Column(DateTime, nullable=False)
    video_end_time = Column(DateTime, nullable=False)
    
    # Investigation
    status = Column(String(50), default='reported', index=True)
    reported_by = Column(UUID(as_uuid=True), nullable=False)
    assigned_to = Column(UUID(as_uuid=True))
    
    # Police
    police_notified = Column(Boolean, default=False)
    fir_number = Column(String(100))
    police_station = Column(String(200))
    police_contact = Column(String(20))
    police_notified_at = Column(DateTime)
    
    # Insurance
    insurance_claim = Column(Boolean, default=False)
    insurance_claim_number = Column(String(100))
    estimated_loss = Column(Numeric(15, 2))
    
    # Evidence
    video_clips_collected = Column(Integer, default=0)
    video_clips_paths = Column(JSON)
    snapshots_collected = Column(Integer, default=0)
    snapshots_paths = Column(JSON)
    evidence_package_created = Column(Boolean, default=False)
    evidence_package_path = Column(String(500))
    evidence_package_password = Column(String(100))
    
    # Timeline
    investigation_started_at = Column(DateTime)
    investigation_completed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True))
    resolution_summary = Column(Text)
    
    # Actions
    actions_taken = Column(Text)
    preventive_measures = Column(Text)
    priority = Column(Integer, default=1)
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_incident_date_type', 'incident_date', 'incident_type'),
        Index('idx_incident_status', 'status'),
    )


class CCTVMaintenance(Base):
    """CCTV Maintenance Records"""
    __tablename__ = "cctv_maintenance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    maintenance_number = Column(String(50), unique=True, nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cctv_cameras.id'))
    dvr_nvr_id = Column(UUID(as_uuid=True))
    component_type = Column(String(50), nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    
    # Issue
    issue_description = Column(Text)
    reported_by = Column(UUID(as_uuid=True))
    reported_date = Column(DateTime)
    
    # Work
    work_description = Column(Text, nullable=False)
    technician_name = Column(String(200))
    technician_contact = Column(String(20))
    vendor_name = Column(String(200))
    
    # Costs
    parts_replaced = Column(Text)
    parts_cost = Column(Numeric(10, 2), default=0)
    labor_cost = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    total_cost = Column(Numeric(10, 2), default=0)
    
    # Downtime
    downtime_start = Column(DateTime)
    downtime_end = Column(DateTime)
    downtime_hours = Column(Float)
    
    # Status
    status = Column(String(50), default='scheduled', index=True)
    completion_date = Column(DateTime)
    
    # Quality
    quality_checked = Column(Boolean, default=False)
    quality_checked_by = Column(UUID(as_uuid=True))
    quality_rating = Column(Integer)
    
    # Invoice
    invoice_number = Column(String(100))
    invoice_date = Column(DateTime)
    payment_status = Column(String(50))
    
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    camera = relationship("CCTVCamera", back_populates="maintenance_records")


class VideoClip(Base):
    """Extracted Video Clips"""
    __tablename__ = "video_clips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clip_id = Column(String(50), unique=True, nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    camera_id = Column(UUID(as_uuid=True), nullable=False)
    clip_name = Column(String(200))
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    
    # File Details
    file_path = Column(String(500), nullable=False)
    file_size_mb = Column(Float, nullable=False)
    format = Column(String(20), nullable=False)
    resolution = Column(String(20))
    quality = Column(String(20))
    
    # Protection
    watermarked = Column(Boolean, default=False)
    watermark_text = Column(String(200))
    password_protected = Column(Boolean, default=False)
    
    # Purpose
    purpose = Column(Text, nullable=False)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    incident_id = Column(UUID(as_uuid=True))
    
    # Access
    download_count = Column(Integer, default=0)
    download_url = Column(String(500))
    expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)


class CameraHealthLog(Base):
    """Camera Health History"""
    __tablename__ = "camera_health_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    check_timestamp = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=False)
    is_online = Column(Boolean, nullable=False)
    is_recording = Column(Boolean, nullable=False)
    
    # Metrics
    response_time_ms = Column(Integer)
    packet_loss_percentage = Column(Float)
    bitrate_kbps = Column(Integer)
    frame_rate = Column(Integer)
    
    # Issues
    issues_detected = Column(JSON)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_health_camera_time', 'camera_id', 'check_timestamp'),
    )


class StorageUsageLog(Base):
    """Storage Usage Tracking"""
    __tablename__ = "storage_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    dvr_nvr_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    log_timestamp = Column(DateTime, nullable=False, index=True)
    total_capacity_gb = Column(Float, nullable=False)
    used_capacity_gb = Column(Float, nullable=False)
    available_capacity_gb = Column(Float, nullable=False)
    utilization_percentage = Column(Float, nullable=False)
    
    # Breakdown
    hot_storage_gb = Column(Float, default=0)
    warm_storage_gb = Column(Float, default=0)
    cold_storage_gb = Column(Float, default=0)
    
    # Alerts
    alert_generated = Column(Boolean, default=False)
    estimated_days_remaining = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertNotification(Base):
    """Alert Notification History"""
    __tablename__ = "alert_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    alert_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    notification_channel = Column(String(50), nullable=False)
    recipient = Column(String(200), nullable=False)
    sent_at = Column(DateTime, nullable=False)
    delivery_status = Column(String(50), nullable=False)
    
    message_content = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)



class PTZControlLog(Base):
    """PTZ Control Action Log"""
    __tablename__ = "ptz_control_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cctv_cameras.id'), nullable=False)
    
    action = Column(String(50), nullable=False)
    speed = Column(Integer)
    preset = Column(Integer)
    
    user_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class VideoBookmark(Base):
    """Video Event Bookmarks"""
    __tablename__ = "video_bookmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cctv_cameras.id'), nullable=False)
    
    bookmark_name = Column(String(200), nullable=False)
    description = Column(Text)
    bookmark_timestamp = Column(DateTime, nullable=False, index=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_bookmark_camera_time', 'camera_id', 'bookmark_timestamp'),
    )


class MonitoringShiftLog(Base):
    """Monitoring Shift Handover Logs"""
    __tablename__ = "monitoring_shift_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    shift_start = Column(DateTime, nullable=False, index=True)
    shift_end = Column(DateTime)
    shift_personnel = Column(Text, nullable=False)
    observations = Column(Text)
    
    incidents_reported = Column(Integer, default=0)
    alerts_handled = Column(Integer, default=0)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CameraSequence(Base):
    """Camera Auto-Switch Sequences"""
    __tablename__ = "camera_sequences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    
    sequence_name = Column(String(200), nullable=False)
    camera_ids = Column(JSON, nullable=False)
    interval_seconds = Column(Integer, default=10)
    
    is_active = Column(Boolean, default=True)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

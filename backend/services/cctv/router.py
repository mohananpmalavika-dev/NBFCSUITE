"""
CCTV Infrastructure Management Router

API endpoints for CCTV surveillance system including:
- Camera management
- Recording & storage
- Live monitoring
- Video analytics & AI
- Video search & retrieval
- Incident management
- Maintenance tracking
- Dashboard & analytics
"""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id

from .camera_service import CameraService
from .recording_service import RecordingService
from .monitoring_service import MonitoringService
from .analytics_service import AnalyticsService
from .incident_service import IncidentService
from .video_service import VideoService
from .maintenance_service import MaintenanceService
from .dashboard_service import DashboardService

from .schemas import (
    # Camera
    CCTVCameraCreate, CCTVCameraUpdate, CCTVCameraResponse,
    CameraFilter, CameraStatus, CameraType, CameraLocation,
    # DVR/NVR
    DVRNVRConfigCreate, DVRNVRConfigUpdate, DVRNVRConfigResponse,
    RecordingQuality, RecordingStatus,
    # Analytics
    AnalyticsConfigCreate, AnalyticsConfigUpdate, AnalyticsConfigResponse,
    AIAlertCreate, AIAlertUpdate, AIAlertResponse,
    AlertType, AlertSeverity, AlertStatus, AlertFilter,
    # Incidents
    CCTVIncidentCreate, CCTVIncidentUpdate, CCTVIncidentResponse,
    IncidentType, IncidentStatus, IncidentFilter,
)
    # Video
    VideoSearchRequest, VideoClipRequest, VideoClipResponse,
    # Maintenance
    CCTVMaintenanceCreate, CCTVMaintenanceUpdate, CCTVMaintenanceResponse,
    MaintenanceType, MaintenanceStatus,
    # Dashboard
    CCTVDashboardStats, CameraHealthReport, StorageAnalytics, AlertAnalytics
)

router = APIRouter(prefix="/cctv", tags=["CCTV Infrastructure"])

# ==================== CAMERA MANAGEMENT ENDPOINTS ====================

@router.post("/cameras", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CCTVCameraCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new CCTV camera"""
    service = CameraService(db, tenant_id, current_user["id"])
    camera = await service.create_camera(camera_data)
    
    return success_response(
        message="Camera created successfully",
        data=CCTVCameraResponse.from_orm(camera).dict()
    )


@router.get("/cameras", response_model=dict)
async def list_cameras(
    branch_id: Optional[uuid.UUID] = Query(None),
    camera_type: Optional[CameraType] = Query(None),
    location_type: Optional[CameraLocation] = Query(None),
    status: Optional[CameraStatus] = Query(None),
    is_critical: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all cameras with filters"""
    service = CameraService(db, tenant_id, current_user["id"])
    cameras, total = await service.list_cameras(
        branch_id=branch_id,
        camera_type=camera_type,
        location_type=location_type,
        status=status,
        is_critical=is_critical,
        page=page,
        page_size=page_size
    )

    
    return success_response(
        message="Cameras retrieved successfully",
        data={
            "cameras": [CCTVCameraResponse.from_orm(c).dict() for c in cameras],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


# ==================== RECORDING & STORAGE ENDPOINTS ====================

@router.post("/dvr-nvr", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_dvr_nvr(
    config_data: DVRNVRConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new DVR/NVR configuration"""
    service = RecordingService(db, tenant_id, current_user["id"])
    config = await service.create_dvr_nvr(config_data)
    
    return success_response(
        message="DVR/NVR created successfully",
        data=DVRNVRConfigResponse.from_orm(config).dict()
    )


@router.get("/dvr-nvr", response_model=dict)
async def list_dvr_nvr(
    branch_id: Optional[uuid.UUID] = Query(None),
    device_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all DVR/NVR configurations"""
    service = RecordingService(db, tenant_id, current_user["id"])
    configs, total = await service.list_dvr_nvr(
        branch_id=branch_id,
        device_type=device_type,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return success_response(
        message="DVR/NVR configurations retrieved successfully",
        data={
            "configs": [DVRNVRConfigResponse.from_orm(c).dict() for c in configs],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/dvr-nvr/{dvr_nvr_id}", response_model=dict)
async def get_dvr_nvr(
    dvr_nvr_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get DVR/NVR configuration by ID"""
    service = RecordingService(db, tenant_id, current_user["id"])
    config = await service.get_dvr_nvr(dvr_nvr_id)
    
    return success_response(
        message="DVR/NVR configuration retrieved successfully",
        data=DVRNVRConfigResponse.from_orm(config).dict()
    )


@router.put("/dvr-nvr/{dvr_nvr_id}", response_model=dict)
async def update_dvr_nvr(
    dvr_nvr_id: uuid.UUID,
    update_data: DVRNVRConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update DVR/NVR configuration"""
    service = RecordingService(db, tenant_id, current_user["id"])
    config = await service.update_dvr_nvr(dvr_nvr_id, update_data)
    
    return success_response(
        message="DVR/NVR updated successfully",
        data=DVRNVRConfigResponse.from_orm(config).dict()
    )


@router.post("/storage/calculate", response_model=dict)
async def calculate_storage_requirement(
    num_cameras: int = Query(..., ge=1, le=1000),
    bitrate_kbps: int = Query(..., ge=512, le=8192),
    retention_days: int = Query(..., ge=30, le=365),
    recording_hours: int = Query(24, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate storage requirement"""
    service = RecordingService(db, tenant_id, current_user["id"])
    calculation = await service.calculate_storage_requirement(
        num_cameras=num_cameras,
        bitrate_kbps=bitrate_kbps,
        retention_days=retention_days,
        recording_hours=recording_hours
    )
    
    return success_response(
        message="Storage calculation completed",
        data=calculation
    )


@router.get("/storage/analytics", response_model=dict)
async def get_storage_analytics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get storage analytics across all DVR/NVR devices"""
    service = RecordingService(db, tenant_id, current_user["id"])
    analytics = await service.get_storage_analytics(branch_id=branch_id)
    
    return success_response(
        message="Storage analytics retrieved successfully",
        data=analytics
    )


@router.get("/storage/health/{dvr_nvr_id}", response_model=dict)
async def check_storage_health(
    dvr_nvr_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check storage health for specific DVR/NVR"""
    service = RecordingService(db, tenant_id, current_user["id"])
    health = await service.check_storage_health(dvr_nvr_id)
    
    return success_response(
        message="Storage health checked successfully",
        data=health
    )


@router.post("/retention/enforce/{dvr_nvr_id}", response_model=dict)
async def enforce_retention_policy(
    dvr_nvr_id: uuid.UUID,
    dry_run: bool = Query(True, description="Simulate without deleting"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Enforce retention policy and cleanup old recordings"""
    service = RecordingService(db, tenant_id, current_user["id"])
    result = await service.enforce_retention_policy(dvr_nvr_id, dry_run=dry_run)
    
    return success_response(
        message="Retention policy enforcement completed",
        data=result
    )


@router.post("/backup/schedule/{dvr_nvr_id}", response_model=dict)
async def schedule_backup(
    dvr_nvr_id: uuid.UUID,
    backup_type: str = Query("incremental", regex="^(full|incremental)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Schedule backup for DVR/NVR"""
    service = RecordingService(db, tenant_id, current_user["id"])
    result = await service.schedule_backup(dvr_nvr_id, backup_type=backup_type)
    
    return success_response(
        message="Backup scheduled successfully",
        data=result
    )


@router.get("/recording/status/{camera_id}", response_model=dict)
async def get_recording_status(
    camera_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get recording status for a camera"""
    service = RecordingService(db, tenant_id, current_user["id"])
    result = await service.get_recording_status(camera_id)
    
    return success_response(
        message="Recording status retrieved successfully",
        data=result
    )


@router.post("/recording/{camera_id}/start", response_model=dict)
async def start_recording(
    camera_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Start recording for a camera"""
    service = RecordingService(db, tenant_id, current_user["id"])
    result = await service.update_recording_status(camera_id, recording_enabled=True)
    
    return success_response(
        message="Recording started successfully",
        data=result
    )


@router.post("/recording/{camera_id}/stop", response_model=dict)
async def stop_recording(
    camera_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Stop recording for a camera"""
    service = RecordingService(db, tenant_id, current_user["id"])
    result = await service.update_recording_status(camera_id, recording_enabled=False)
    
    return success_response(
        message="Recording stopped successfully",
        data=result
    )


# ==================== LIVE MONITORING ENDPOINTS ====================

@router.get("/monitoring/live-cameras", response_model=dict)
async def get_live_cameras(
    branch_id: Optional[uuid.UUID] = Query(None),
    location_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all cameras available for live monitoring"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    cameras, total = await service.get_live_cameras(
        branch_id=branch_id,
        location_type=location_type,
        page=page,
        page_size=page_size
    )
    
    return success_response(
        message="Live cameras retrieved successfully",
        data={
            "cameras": cameras,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/monitoring/stream/{camera_id}", response_model=dict)
async def get_stream_url(
    camera_id: uuid.UUID,
    quality: str = Query("high", regex="^(low|medium|high|ultra)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get streaming URL for a specific camera"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    stream_info = await service.get_stream_url(camera_id, quality=quality)
    
    return success_response(
        message="Stream URL retrieved successfully",
        data=stream_info
    )


@router.post("/monitoring/ptz/{camera_id}/control", response_model=dict)
async def control_ptz(
    camera_id: uuid.UUID,
    action: str = Query(..., regex="^(pan_left|pan_right|tilt_up|tilt_down|zoom_in|zoom_out|stop|go_to_preset|set_preset|home)$"),
    speed: Optional[int] = Query(None, ge=1, le=100),
    preset: Optional[int] = Query(None, ge=1, le=256),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Control PTZ camera (Pan, Tilt, Zoom)"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    result = await service.control_ptz(
        camera_id=camera_id,
        action=action,
        speed=speed,
        preset=preset
    )
    
    return success_response(
        message="PTZ command executed successfully",
        data=result
    )


@router.post("/monitoring/bookmarks", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    camera_id: uuid.UUID = Query(...),
    bookmark_name: str = Query(..., min_length=1, max_length=200),
    description: Optional[str] = Query(None, max_length=1000),
    timestamp: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a bookmark for an important event"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    bookmark = await service.create_bookmark(
        camera_id=camera_id,
        bookmark_name=bookmark_name,
        description=description,
        timestamp=timestamp
    )
    
    return success_response(
        message="Bookmark created successfully",
        data=bookmark
    )


@router.get("/monitoring/bookmarks", response_model=dict)
async def get_bookmarks(
    camera_id: Optional[uuid.UUID] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get bookmarked events"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    bookmarks, total = await service.get_bookmarks(
        camera_id=camera_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size
    )
    
    # Convert ORM objects to dicts
    bookmark_list = [
        {
            "id": str(b.id),
            "camera_id": str(b.camera_id),
            "bookmark_name": b.bookmark_name,
            "description": b.description,
            "bookmark_timestamp": b.bookmark_timestamp.isoformat(),
            "created_by": str(b.created_by),
            "created_at": b.created_at.isoformat()
        }
        for b in bookmarks
    ]
    
    return success_response(
        message="Bookmarks retrieved successfully",
        data={
            "bookmarks": bookmark_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/monitoring/alerts/active", response_model=dict)
async def get_active_alerts(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    alert_type: Optional[str] = Query(None),
    camera_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get active alerts for monitoring dashboard"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    alerts = await service.get_active_alerts(
        severity=severity,
        alert_type=alert_type,
        camera_id=camera_id,
        limit=limit
    )
    
    # Convert ORM objects to dicts
    alert_list = [
        {
            "id": str(a.id),
            "camera_id": str(a.camera_id),
            "alert_type": a.alert_type,
            "alert_severity": a.alert_severity,
            "status": a.status,
            "alert_timestamp": a.alert_timestamp.isoformat(),
            "alert_message": a.alert_message,
            "alert_metadata": a.alert_metadata
        }
        for a in alerts
    ]
    
    return success_response(
        message="Active alerts retrieved successfully",
        data={
            "alerts": alert_list,
            "count": len(alert_list)
        }
    )


@router.post("/monitoring/alerts/{alert_id}/acknowledge", response_model=dict)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Acknowledge an alert"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    result = await service.acknowledge_alert(alert_id)
    
    return success_response(
        message="Alert acknowledged successfully",
        data=result
    )


@router.post("/monitoring/shift-logs", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_shift_log(
    shift_start: datetime = Query(...),
    shift_end: Optional[datetime] = Query(None),
    shift_personnel: str = Query(..., min_length=1, max_length=500),
    observations: Optional[str] = Query(None, max_length=2000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create shift handover log"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    log = await service.create_shift_log(
        shift_start=shift_start,
        shift_end=shift_end,
        shift_personnel=shift_personnel,
        observations=observations
    )
    
    return success_response(
        message="Shift log created successfully",
        data=log
    )


@router.post("/monitoring/sequences", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_camera_sequence(
    sequence_name: str = Query(..., min_length=1, max_length=200),
    camera_ids: List[uuid.UUID] = Query(...),
    interval_seconds: int = Query(10, ge=5, le=60),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create camera auto-switch sequence"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    sequence = await service.create_camera_sequence(
        sequence_name=sequence_name,
        camera_ids=camera_ids,
        interval_seconds=interval_seconds
    )
    
    return success_response(
        message="Camera sequence created successfully",
        data=sequence
    )


@router.get("/monitoring/sequences/{sequence_name}", response_model=dict)
async def get_camera_sequence(
    sequence_name: str,
    interval_seconds: int = Query(10, ge=5, le=60),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get camera sequence configuration"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    sequence = await service.get_camera_sequence(
        sequence_name=sequence_name,
        interval_seconds=interval_seconds
    )
    
    return success_response(
        message="Camera sequence retrieved successfully",
        data=sequence
    )


@router.get("/monitoring/dashboard", response_model=dict)
async def get_monitoring_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get monitoring dashboard with real-time stats"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    dashboard = await service.get_monitoring_dashboard()
    
    return success_response(
        message="Monitoring dashboard data retrieved successfully",
        data=dashboard
    )


@router.post("/monitoring/{camera_id}/audio", response_model=dict)
async def toggle_audio_monitoring(
    camera_id: uuid.UUID,
    enabled: bool = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Enable or disable audio monitoring for a camera"""
    service = MonitoringService(db, tenant_id, current_user["id"])
    result = await service.enable_audio_monitoring(camera_id, enabled=enabled)
    
    return success_response(
        message=f"Audio monitoring {'enabled' if enabled else 'disabled'} successfully",
        data=result
    )

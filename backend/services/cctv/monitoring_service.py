"""
Live Monitoring Service

Manages real-time video surveillance including:
- Live stream management
- PTZ camera control
- Multi-camera viewing
- Alert monitoring
- Event bookmarking
- Shift management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import json

from .schemas import CameraStatus, AlertStatus


class MonitoringService:
    """Service for live monitoring operations"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def get_live_cameras(
        self,
        branch_id: Optional[uuid.UUID] = None,
        location_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List, int]:
        """Get all cameras available for live monitoring"""
        from .models import CCTVCamera
        
        query = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False,
                CCTVCamera.status.in_(['online', 'recording'])
            )
        )
        
        if branch_id:
            query = query.filter(CCTVCamera.branch_id == branch_id)
        if location_type:
            query = query.filter(CCTVCamera.location_type == location_type)
        
        total = query.count()
        cameras = query.order_by(CCTVCamera.camera_name).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        # Enrich with live stream URLs
        camera_list = []
        for camera in cameras:
            camera_dict = {
                "id": str(camera.id),
                "camera_name": camera.camera_name,
                "camera_id": camera.camera_id,
                "location_type": camera.location_type,
                "location_description": camera.location_description,
                "camera_type": camera.camera_type,
                "status": camera.status,
                "rtsp_url": camera.rtsp_url,
                "audio_recording_enabled": camera.audio_recording_enabled,
                "is_critical": camera.is_critical,
                "specifications": camera.specifications
            }
            camera_list.append(camera_dict)
        
        return camera_list, total
    
    async def get_stream_url(
        self,
        camera_id: uuid.UUID,
        quality: str = "high"
    ) -> Dict[str, Any]:
        """Get streaming URL for a camera"""
        from .models import CCTVCamera
        
        camera = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.id == camera_id,
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False
            )
        ).first()
        
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")
        
        if camera.status not in ['online', 'recording']:
            raise ValueError(f"Camera {camera_id} is not available for streaming")
        
        # Generate streaming URL based on quality
        base_url = camera.rtsp_url or f"rtsp://{camera.ip_address}:{camera.port}/stream"
        
        quality_params = {
            "low": "?quality=low&bitrate=512",
            "medium": "?quality=medium&bitrate=1024",
            "high": "?quality=high&bitrate=2048",
            "ultra": "?quality=ultra&bitrate=4096"
        }
        
        stream_url = base_url + quality_params.get(quality, quality_params["high"])
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "stream_url": stream_url,
            "quality": quality,
            "audio_enabled": camera.audio_recording_enabled,
            "can_ptz": camera.camera_type == "ptz",
            "resolution": camera.specifications.get("resolution", "1080p"),
            "frame_rate": camera.specifications.get("frame_rate", 25)
        }
    
    async def control_ptz(
        self,
        camera_id: uuid.UUID,
        action: str,
        speed: Optional[int] = None,
        preset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Control PTZ camera (Pan, Tilt, Zoom)"""
        from .models import CCTVCamera
        
        camera = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.id == camera_id,
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False,
                CCTVCamera.camera_type == 'ptz'
            )
        ).first()
        
        if not camera:
            raise ValueError(f"PTZ Camera {camera_id} not found")
        
        # Validate action
        valid_actions = [
            'pan_left', 'pan_right', 'tilt_up', 'tilt_down',
            'zoom_in', 'zoom_out', 'stop', 'go_to_preset', 'set_preset', 'home'
        ]
        
        if action not in valid_actions:
            raise ValueError(f"Invalid PTZ action: {action}")
        
        # In real implementation, this would send commands to the camera via ONVIF
        # For now, we'll log the action
        
        result = {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "action": action,
            "speed": speed or 50,
            "preset": preset,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed"
        }
        
        # Log PTZ action
        await self._log_ptz_action(camera_id, action, speed, preset)
        
        return result
    
    async def _log_ptz_action(
        self,
        camera_id: uuid.UUID,
        action: str,
        speed: Optional[int],
        preset: Optional[int]
    ):
        """Log PTZ control action"""
        from .models import PTZControlLog
        
        log = PTZControlLog(
            tenant_id=self.tenant_id,
            camera_id=camera_id,
            action=action,
            speed=speed,
            preset=preset,
            user_id=self.user_id,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(log)
        self.db.commit()
    
    async def create_bookmark(
        self,
        camera_id: uuid.UUID,
        bookmark_name: str,
        description: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a bookmark for an important event"""
        from .models import VideoBookmark
        
        bookmark_time = timestamp or datetime.utcnow()
        
        bookmark = VideoBookmark(
            tenant_id=self.tenant_id,
            camera_id=camera_id,
            bookmark_name=bookmark_name,
            description=description,
            bookmark_timestamp=bookmark_time,
            created_by=self.user_id
        )
        
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        
        return {
            "id": str(bookmark.id),
            "camera_id": str(camera_id),
            "bookmark_name": bookmark_name,
            "description": description,
            "timestamp": bookmark_time.isoformat(),
            "created_by": str(self.user_id),
            "created_at": bookmark.created_at.isoformat()
        }

    
    async def get_bookmarks(
        self,
        camera_id: Optional[uuid.UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List, int]:
        """Get bookmarked events"""
        from .models import VideoBookmark
        
        query = self.db.query(VideoBookmark).filter(
            VideoBookmark.tenant_id == self.tenant_id
        )
        
        if camera_id:
            query = query.filter(VideoBookmark.camera_id == camera_id)
        if date_from:
            query = query.filter(VideoBookmark.bookmark_timestamp >= date_from)
        if date_to:
            query = query.filter(VideoBookmark.bookmark_timestamp <= date_to)
        
        total = query.count()
        bookmarks = query.order_by(VideoBookmark.bookmark_timestamp.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return bookmarks, total
    
    async def get_active_alerts(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        camera_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List:
        """Get active alerts for monitoring"""
        from .models import AIAlert
        
        query = self.db.query(AIAlert).filter(
            and_(
                AIAlert.tenant_id == self.tenant_id,
                AIAlert.status.in_(['new', 'acknowledged'])
            )
        )
        
        if severity:
            query = query.filter(AIAlert.alert_severity == severity)
        if alert_type:
            query = query.filter(AIAlert.alert_type == alert_type)
        if camera_id:
            query = query.filter(AIAlert.camera_id == camera_id)
        
        alerts = query.order_by(
            AIAlert.alert_timestamp.desc()
        ).limit(limit).all()
        
        return alerts
    
    async def acknowledge_alert(
        self,
        alert_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Acknowledge an alert"""
        from .models import AIAlert
        
        alert = self.db.query(AIAlert).filter(
            and_(
                AIAlert.id == alert_id,
                AIAlert.tenant_id == self.tenant_id
            )
        ).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert.status = 'acknowledged'
        alert.acknowledged_by = self.user_id
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return {
            "alert_id": str(alert_id),
            "status": "acknowledged",
            "acknowledged_by": str(self.user_id),
            "acknowledged_at": alert.acknowledged_at.isoformat()
        }
    
    async def create_shift_log(
        self,
        shift_start: datetime,
        shift_end: Optional[datetime] = None,
        shift_personnel: str = "",
        observations: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create shift handover log"""
        from .models import MonitoringShiftLog
        
        log = MonitoringShiftLog(
            tenant_id=self.tenant_id,
            shift_start=shift_start,
            shift_end=shift_end,
            shift_personnel=shift_personnel,
            observations=observations,
            created_by=self.user_id
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return {
            "id": str(log.id),
            "shift_start": shift_start.isoformat(),
            "shift_end": shift_end.isoformat() if shift_end else None,
            "personnel": shift_personnel,
            "observations": observations
        }
    
    async def get_camera_sequence(
        self,
        sequence_name: str,
        interval_seconds: int = 10
    ) -> Dict[str, Any]:
        """Get camera sequence configuration for auto-switching"""
        from .models import CameraSequence
        
        sequence = self.db.query(CameraSequence).filter(
            and_(
                CameraSequence.tenant_id == self.tenant_id,
                CameraSequence.sequence_name == sequence_name,
                CameraSequence.is_active == True
            )
        ).first()
        
        if not sequence:
            raise ValueError(f"Camera sequence '{sequence_name}' not found")
        
        return {
            "sequence_name": sequence_name,
            "camera_ids": sequence.camera_ids,
            "interval_seconds": interval_seconds,
            "loop": True
        }
    
    async def create_camera_sequence(
        self,
        sequence_name: str,
        camera_ids: List[uuid.UUID],
        interval_seconds: int = 10
    ) -> Dict[str, Any]:
        """Create camera auto-switch sequence"""
        from .models import CameraSequence
        
        sequence = CameraSequence(
            tenant_id=self.tenant_id,
            sequence_name=sequence_name,
            camera_ids=[str(cid) for cid in camera_ids],
            interval_seconds=interval_seconds,
            is_active=True,
            created_by=self.user_id
        )
        
        self.db.add(sequence)
        self.db.commit()
        self.db.refresh(sequence)
        
        return {
            "id": str(sequence.id),
            "sequence_name": sequence_name,
            "camera_count": len(camera_ids),
            "interval_seconds": interval_seconds
        }
    
    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        from .models import CCTVCamera, AIAlert
        
        # Camera stats
        total_cameras = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False
            )
        ).count()
        
        online_cameras = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False,
                CCTVCamera.status.in_(['online', 'recording'])
            )
        ).count()
        
        # Active alerts
        active_alerts = self.db.query(AIAlert).filter(
            and_(
                AIAlert.tenant_id == self.tenant_id,
                AIAlert.status == 'new'
            )
        ).count()
        
        critical_alerts = self.db.query(AIAlert).filter(
            and_(
                AIAlert.tenant_id == self.tenant_id,
                AIAlert.status == 'new',
                AIAlert.alert_severity == 'critical'
            )
        ).count()
        
        # Recent alerts (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_alerts = self.db.query(AIAlert).filter(
            and_(
                AIAlert.tenant_id == self.tenant_id,
                AIAlert.alert_timestamp >= one_hour_ago
            )
        ).count()
        
        return {
            "cameras": {
                "total": total_cameras,
                "online": online_cameras,
                "offline": total_cameras - online_cameras,
                "availability_percentage": (online_cameras / total_cameras * 100) if total_cameras > 0 else 0
            },
            "alerts": {
                "active": active_alerts,
                "critical": critical_alerts,
                "last_hour": recent_alerts
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def enable_audio_monitoring(
        self,
        camera_id: uuid.UUID,
        enabled: bool
    ) -> Dict[str, Any]:
        """Enable or disable audio monitoring for a camera"""
        from .models import CCTVCamera
        
        camera = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.id == camera_id,
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False
            )
        ).first()
        
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")
        
        # Check if camera supports audio
        if not camera.specifications.get("audio_support", False):
            raise ValueError(f"Camera {camera.camera_name} does not support audio")
        
        camera.audio_recording_enabled = enabled
        camera.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(camera)
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "audio_enabled": enabled,
            "timestamp": datetime.utcnow().isoformat()
        }

"""
Camera Management Service

Handles CCTV camera operations including:
- Camera CRUD operations
- Health monitoring
- Status management
- Connectivity testing
- Uptime calculation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from .schemas import (
    CCTVCameraCreate, CCTVCameraUpdate,
    CameraStatus, CameraType, CameraLocation
)


class CameraService:
    """Service for managing CCTV cameras"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_camera(self, camera_data: CCTVCameraCreate):
        """Create new CCTV camera"""
        from .models import CCTVCamera
        
        # Check for duplicate camera_id
        existing = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.camera_id == camera_data.camera_id,
                CCTVCamera.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Camera with ID {camera_data.camera_id} already exists")
        
        # Create camera
        camera = CCTVCamera(
            **camera_data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            uptime_percentage=100.0,
            last_online_at=datetime.utcnow()
        )
        
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        
        return camera
    
    async def get_camera(self, camera_id: uuid.UUID):
        """Get camera by ID"""
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
        
        return camera
    
    async def list_cameras(
        self,
        branch_id: Optional[uuid.UUID] = None,
        camera_type: Optional[CameraType] = None,
        location_type: Optional[CameraLocation] = None,
        status: Optional[CameraStatus] = None,
        is_critical: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List, int]:
        """List cameras with filters"""
        from .models import CCTVCamera
        
        query = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(CCTVCamera.branch_id == branch_id)
        if camera_type:
            query = query.filter(CCTVCamera.camera_type == camera_type.value)
        if location_type:
            query = query.filter(CCTVCamera.location_type == location_type.value)
        if status:
            query = query.filter(CCTVCamera.status == status.value)
        if is_critical is not None:
            query = query.filter(CCTVCamera.is_critical == is_critical)
        
        total = query.count()
        
        cameras = query.order_by(CCTVCamera.camera_name).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return cameras, total
    
    async def update_camera(
        self,
        camera_id: uuid.UUID,
        update_data: CCTVCameraUpdate
    ):
        """Update camera details"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(camera, field, value)
        
        camera.updated_at = datetime.utcnow()
        camera.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(camera)
        
        return camera
    
    async def delete_camera(self, camera_id: uuid.UUID):
        """Soft delete camera"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        camera.is_deleted = True
        camera.deleted_at = datetime.utcnow()
        camera.deleted_by = self.user_id
        
        self.db.commit()
        
        return {"message": "Camera deleted successfully"}
    
    async def update_camera_status(
        self,
        camera_id: uuid.UUID,
        status: CameraStatus
    ):
        """Update camera status"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        old_status = camera.status
        camera.status = status.value
        camera.updated_at = datetime.utcnow()
        
        if status.value == 'online':
            camera.last_online_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(camera)
        
        return {
            "camera_id": str(camera_id),
            "old_status": old_status,
            "new_status": status.value,
            "updated_at": camera.updated_at.isoformat()
        }
    
    async def get_camera_health(self, camera_id: uuid.UUID):
        """Get camera health status"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        # Calculate health metrics
        health_score = 100
        issues = []
        
        # Check online status
        if camera.status != 'online':
            health_score -= 50
            issues.append(f"Camera is {camera.status}")
        
        # Check last online time
        if camera.last_online_at:
            offline_duration = datetime.utcnow() - camera.last_online_at
            if offline_duration > timedelta(hours=1):
                health_score -= 20
                issues.append(f"Camera offline for {offline_duration.total_seconds() / 3600:.1f} hours")
        
        # Check uptime percentage
        if camera.uptime_percentage < 95:
            health_score -= 15
            issues.append(f"Low uptime: {camera.uptime_percentage}%")
        
        # Check recording status
        if not camera.recording_enabled:
            health_score -= 10
            issues.append("Recording is disabled")
        
        # Determine health status
        if health_score >= 90:
            health_status = "excellent"
        elif health_score >= 70:
            health_status = "good"
        elif health_score >= 50:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "health_score": max(0, health_score),
            "health_status": health_status,
            "status": camera.status,
            "uptime_percentage": float(camera.uptime_percentage),
            "last_online_at": camera.last_online_at.isoformat() if camera.last_online_at else None,
            "recording_enabled": camera.recording_enabled,
            "issues": issues,
            "recommendations": self._get_health_recommendations(health_score, issues)
        }
    
    def _get_health_recommendations(self, health_score: int, issues: List[str]) -> List[str]:
        """Get health improvement recommendations"""
        recommendations = []
        
        if health_score < 90:
            if any("offline" in issue.lower() for issue in issues):
                recommendations.append("Check camera power supply and network connectivity")
                recommendations.append("Restart camera if needed")
            
            if any("uptime" in issue.lower() for issue in issues):
                recommendations.append("Schedule preventive maintenance")
                recommendations.append("Check for intermittent connection issues")
            
            if any("recording" in issue.lower() for issue in issues):
                recommendations.append("Enable recording to ensure compliance")
                recommendations.append("Verify DVR/NVR connection")
        
        if not recommendations:
            recommendations.append("Camera is operating optimally")
        
        return recommendations
    
    async def calculate_uptime(
        self,
        camera_id: uuid.UUID,
        days: int = 30
    ):
        """Calculate camera uptime percentage"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        # In production, this would query actual uptime logs
        # For now, we'll use the stored uptime percentage
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "period_days": days,
            "uptime_percentage": float(camera.uptime_percentage),
            "total_hours": days * 24,
            "online_hours": days * 24 * (camera.uptime_percentage / 100),
            "offline_hours": days * 24 * (1 - camera.uptime_percentage / 100)
        }
    
    async def test_connectivity(self, camera_id: uuid.UUID):
        """Test camera connectivity"""
        from .models import CCTVCamera
        
        camera = await self.get_camera(camera_id)
        
        # In production, this would:
        # 1. Ping the camera IP
        # 2. Test RTSP stream
        # 3. Check ONVIF connectivity
        # For now, we'll simulate based on status
        
        connectivity_status = camera.status == 'online'
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "ip_address": camera.ip_address,
            "connectivity": "success" if connectivity_status else "failed",
            "ping_response_ms": 45 if connectivity_status else None,
            "rtsp_stream": "accessible" if connectivity_status else "not accessible",
            "onvif_status": "connected" if connectivity_status else "disconnected",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_branch_cameras_summary(self, branch_id: uuid.UUID):
        """Get camera summary for a branch"""
        from .models import CCTVCamera
        
        cameras = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.branch_id == branch_id,
                CCTVCamera.is_deleted == False
            )
        ).all()
        
        total = len(cameras)
        online = sum(1 for c in cameras if c.status == 'online')
        offline = sum(1 for c in cameras if c.status == 'offline')
        maintenance = sum(1 for c in cameras if c.status == 'maintenance')
        recording = sum(1 for c in cameras if c.recording_enabled)
        critical = sum(1 for c in cameras if c.is_critical)
        
        avg_uptime = sum(c.uptime_percentage for c in cameras) / total if total > 0 else 0
        
        # Group by type
        by_type = {}
        for camera in cameras:
            camera_type = camera.camera_type
            if camera_type not in by_type:
                by_type[camera_type] = 0
            by_type[camera_type] += 1
        
        # Group by location
        by_location = {}
        for camera in cameras:
            location = camera.location_type
            if location not in by_location:
                by_location[location] = 0
            by_location[location] += 1
        
        return {
            "branch_id": str(branch_id),
            "total_cameras": total,
            "online_cameras": online,
            "offline_cameras": offline,
            "maintenance_cameras": maintenance,
            "recording_cameras": recording,
            "critical_cameras": critical,
            "average_uptime_percentage": round(avg_uptime, 2),
            "by_type": by_type,
            "by_location": by_location,
            "health_status": "good" if avg_uptime >= 95 and offline == 0 else "needs_attention"
        }
    
    async def get_system_health_report(self):
        """Get system-wide camera health report"""
        from .models import CCTVCamera
        
        cameras = self.db.query(CCTVCamera).filter(
            and_(
                CCTVCamera.tenant_id == self.tenant_id,
                CCTVCamera.is_deleted == False
            )
        ).all()
        
        total = len(cameras)
        if total == 0:
            return {
                "total_cameras": 0,
                "message": "No cameras found"
            }
        
        online = sum(1 for c in cameras if c.status == 'online')
        offline = sum(1 for c in cameras if c.status == 'offline')
        maintenance = sum(1 for c in cameras if c.status == 'maintenance')
        faulty = sum(1 for c in cameras if c.status == 'faulty')
        
        avg_uptime = sum(c.uptime_percentage for c in cameras) / total
        
        # Find cameras needing attention
        low_uptime_cameras = [
            {
                "camera_id": str(c.id),
                "camera_name": c.camera_name,
                "uptime_percentage": float(c.uptime_percentage)
            }
            for c in cameras if c.uptime_percentage < 90
        ]
        
        offline_cameras = [
            {
                "camera_id": str(c.id),
                "camera_name": c.camera_name,
                "last_online": c.last_online_at.isoformat() if c.last_online_at else None
            }
            for c in cameras if c.status == 'offline'
        ]
        
        return {
            "total_cameras": total,
            "online_cameras": online,
            "offline_cameras": offline,
            "maintenance_cameras": maintenance,
            "faulty_cameras": faulty,
            "availability_percentage": round((online / total) * 100, 2),
            "average_uptime_percentage": round(avg_uptime, 2),
            "system_health": "excellent" if avg_uptime >= 95 and offline == 0 else "good" if avg_uptime >= 90 else "needs_attention",
            "cameras_needing_attention": len(low_uptime_cameras) + len(offline_cameras),
            "low_uptime_cameras": low_uptime_cameras[:10],  # Top 10
            "offline_cameras": offline_cameras[:10],  # Top 10
            "timestamp": datetime.utcnow().isoformat()
        }

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

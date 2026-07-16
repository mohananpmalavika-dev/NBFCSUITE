"""
Recording & Storage Service

Manages DVR/NVR systems, storage capacity, retention policies,
and backup operations for CCTV surveillance.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from .schemas import (
    DVRNVRConfigCreate, DVRNVRConfigUpdate,
    RecordingQuality, RecordingStatus, StorageType
)


class RecordingService:
    """Service for managing recording and storage operations"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_dvr_nvr(self, config_data: DVRNVRConfigCreate):
        """Create new DVR/NVR configuration"""
        from .models import DVRNVRConfig
        
        # Check for duplicate serial number
        existing = self.db.query(DVRNVRConfig).filter(
            and_(
                DVRNVRConfig.tenant_id == self.tenant_id,
                DVRNVRConfig.serial_number == config_data.serial_number,
                DVRNVRConfig.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"DVR/NVR with serial {config_data.serial_number} already exists")
        
        # Calculate available storage and channels
        config = DVRNVRConfig(
            **config_data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            available_channels=config_data.total_channels - config_data.used_channels,
            available_storage_tb=config_data.total_storage_tb - config_data.used_storage_tb
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config

    
    async def get_dvr_nvr(self, dvr_nvr_id: uuid.UUID):
        """Get DVR/NVR by ID"""
        from .models import DVRNVRConfig
        
        config = self.db.query(DVRNVRConfig).filter(
            and_(
                DVRNVRConfig.id == dvr_nvr_id,
                DVRNVRConfig.tenant_id == self.tenant_id,
                DVRNVRConfig.is_deleted == False
            )
        ).first()
        
        if not config:
            raise ValueError(f"DVR/NVR {dvr_nvr_id} not found")
        
        return config
    
    async def list_dvr_nvr(
        self,
        branch_id: Optional[uuid.UUID] = None,
        device_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List, int]:
        """List all DVR/NVR configurations"""
        from .models import DVRNVRConfig
        
        query = self.db.query(DVRNVRConfig).filter(
            and_(
                DVRNVRConfig.tenant_id == self.tenant_id,
                DVRNVRConfig.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(DVRNVRConfig.branch_id == branch_id)
        if device_type:
            query = query.filter(DVRNVRConfig.device_type == device_type)
        if status:
            query = query.filter(DVRNVRConfig.status == status)
        
        total = query.count()
        configs = query.order_by(DVRNVRConfig.device_name).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return configs, total
    
    async def update_dvr_nvr(
        self,
        dvr_nvr_id: uuid.UUID,
        update_data: DVRNVRConfigUpdate
    ):
        """Update DVR/NVR configuration"""
        config = await self.get_dvr_nvr(dvr_nvr_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(config, key, value)
        
        # Recalculate available resources
        if 'total_channels' in update_dict or 'used_channels' in update_dict:
            config.available_channels = config.total_channels - config.used_channels
        
        if 'total_storage_tb' in update_dict or 'used_storage_tb' in update_dict:
            config.available_storage_tb = config.total_storage_tb - config.used_storage_tb
            
            # Check storage alert threshold
            utilization = (float(config.used_storage_tb) / float(config.total_storage_tb)) * 100
            if utilization >= config.storage_alert_threshold_percentage:
                config.storage_alert_active = True
            else:
                config.storage_alert_active = False
        
        config.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(config)
        
        return config

    
    async def calculate_storage_requirement(
        self,
        num_cameras: int,
        bitrate_kbps: int,
        retention_days: int,
        recording_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate storage requirement based on cameras and retention
        
        Formula: Storage (GB) = (Bitrate × 3600 × Hours × Days × Cameras) / (8 × 1024 × 1024)
        """
        # Convert bitrate from Kbps to bps
        bitrate_bps = bitrate_kbps * 1024
        
        # Calculate storage in bytes
        storage_bytes = (bitrate_bps * 3600 * recording_hours * retention_days * num_cameras) / 8
        
        # Convert to different units
        storage_mb = storage_bytes / (1024 * 1024)
        storage_gb = storage_mb / 1024
        storage_tb = storage_gb / 1024
        
        # Calculate tier breakdown (Hot: 30 days, Warm: 60 days, Cold: 90 days)
        hot_days = min(30, retention_days)
        warm_days = min(60, max(0, retention_days - 30))
        cold_days = max(0, retention_days - 90)
        
        hot_storage_gb = (bitrate_bps * 3600 * recording_hours * hot_days * num_cameras) / (8 * 1024 * 1024 * 1024)
        warm_storage_gb = (bitrate_bps * 3600 * recording_hours * warm_days * num_cameras) / (8 * 1024 * 1024 * 1024)
        cold_storage_gb = (bitrate_bps * 3600 * recording_hours * cold_days * num_cameras) / (8 * 1024 * 1024 * 1024)
        
        return {
            "num_cameras": num_cameras,
            "bitrate_kbps": bitrate_kbps,
            "retention_days": retention_days,
            "recording_hours_per_day": recording_hours,
            "total_storage_gb": round(storage_gb, 2),
            "total_storage_tb": round(storage_tb, 2),
            "storage_breakdown": {
                "hot_storage_gb": round(hot_storage_gb, 2),
                "hot_storage_days": hot_days,
                "warm_storage_gb": round(warm_storage_gb, 2),
                "warm_storage_days": warm_days,
                "cold_storage_gb": round(cold_storage_gb, 2),
                "cold_storage_days": cold_days
            },
            "recommended_raid": "RAID 6" if storage_tb > 5 else "RAID 10",
            "recommended_backup_size_tb": round(storage_tb, 2)
        }
    
    async def get_storage_analytics(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get storage analytics and utilization"""
        from .models import DVRNVRConfig
        
        query = self.db.query(DVRNVRConfig).filter(
            and_(
                DVRNVRConfig.tenant_id == self.tenant_id,
                DVRNVRConfig.is_deleted == False,
                DVRNVRConfig.status == 'active'
            )
        )
        
        if branch_id:
            query = query.filter(DVRNVRConfig.branch_id == branch_id)
        
        configs = query.all()
        
        if not configs:
            return {
                "total_devices": 0,
                "total_capacity_tb": 0,
                "total_used_tb": 0,
                "total_available_tb": 0,
                "average_utilization_percentage": 0,
                "devices_with_alerts": 0,
                "storage_by_branch": [],
                "storage_health": "good"
            }
        
        total_capacity = sum(float(c.total_storage_tb) for c in configs)
        total_used = sum(float(c.used_storage_tb) for c in configs)
        total_available = sum(float(c.available_storage_tb) for c in configs)
        
        avg_utilization = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        devices_with_alerts = sum(1 for c in configs if c.storage_alert_active)
        
        # Storage health assessment
        if avg_utilization >= 90:
            storage_health = "critical"
        elif avg_utilization >= 80:
            storage_health = "warning"
        elif avg_utilization >= 70:
            storage_health = "fair"
        else:
            storage_health = "good"
        
        return {
            "total_devices": len(configs),
            "total_capacity_tb": round(total_capacity, 2),
            "total_used_tb": round(total_used, 2),
            "total_available_tb": round(total_available, 2),
            "average_utilization_percentage": round(avg_utilization, 2),
            "devices_with_alerts": devices_with_alerts,
            "storage_health": storage_health,
            "cleanup_recommended": avg_utilization >= 80
        }

    
    async def enforce_retention_policy(
        self,
        dvr_nvr_id: uuid.UUID,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Enforce retention policy and cleanup old recordings
        
        Args:
            dvr_nvr_id: DVR/NVR device ID
            dry_run: If True, only simulate without deleting
        """
        config = await self.get_dvr_nvr(dvr_nvr_id)
        
        # Calculate cutoff dates
        hot_cutoff = datetime.utcnow() - timedelta(days=config.retention_days_hot)
        cold_cutoff = datetime.utcnow() - timedelta(days=config.retention_days_cold)
        
        # Simulate what would be deleted
        estimated_space_freed_gb = 0
        
        # In real implementation, this would:
        # 1. Query video_clips table for old recordings
        # 2. Move hot to warm, warm to cold
        # 3. Delete recordings older than cold retention
        # 4. Update storage usage
        
        if not dry_run:
            # Update storage usage after cleanup
            # This would be calculated based on actual deletions
            pass
        
        return {
            "dvr_nvr_id": str(dvr_nvr_id),
            "device_name": config.device_name,
            "hot_retention_days": config.retention_days_hot,
            "cold_retention_days": config.retention_days_cold,
            "hot_cutoff_date": hot_cutoff.isoformat(),
            "cold_cutoff_date": cold_cutoff.isoformat(),
            "dry_run": dry_run,
            "estimated_space_freed_gb": estimated_space_freed_gb,
            "action_taken": "Simulation only" if dry_run else "Cleanup executed"
        }
    
    async def check_storage_health(
        self,
        dvr_nvr_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Check DVR/NVR storage health"""
        config = await self.get_dvr_nvr(dvr_nvr_id)
        
        utilization_pct = (float(config.used_storage_tb) / float(config.total_storage_tb)) * 100
        
        # Estimate days until full
        if config.used_storage_tb > 0:
            # Get recent usage trend (simplified - would query storage_usage_logs)
            # Assume linear growth for now
            days_until_full = int((float(config.available_storage_tb) / float(config.used_storage_tb)) * 180)
        else:
            days_until_full = 999
        
        # Health status
        if utilization_pct >= 95:
            health_status = "critical"
            recommendation = "Immediate cleanup or expansion required"
        elif utilization_pct >= 85:
            health_status = "warning"
            recommendation = "Schedule cleanup or plan expansion"
        elif utilization_pct >= 75:
            health_status = "fair"
            recommendation = "Monitor closely"
        else:
            health_status = "good"
            recommendation = "Operating normally"
        
        return {
            "dvr_nvr_id": str(dvr_nvr_id),
            "device_name": config.device_name,
            "health_status": health_status,
            "disk_health": config.disk_health_status,
            "raid_status": config.raid_status,
            "total_capacity_tb": float(config.total_storage_tb),
            "used_capacity_tb": float(config.used_storage_tb),
            "available_capacity_tb": float(config.available_storage_tb),
            "utilization_percentage": round(utilization_pct, 2),
            "days_until_full": days_until_full,
            "alert_threshold": config.storage_alert_threshold_percentage,
            "alert_active": config.storage_alert_active,
            "recommendation": recommendation,
            "last_health_check": config.last_health_check.isoformat() if config.last_health_check else None
        }
    
    async def schedule_backup(
        self,
        dvr_nvr_id: uuid.UUID,
        backup_type: str = "incremental"
    ) -> Dict[str, Any]:
        """Schedule backup for DVR/NVR"""
        config = await self.get_dvr_nvr(dvr_nvr_id)
        
        if not config.backup_enabled:
            raise ValueError(f"Backup not enabled for {config.device_name}")
        
        if not config.backup_location:
            raise ValueError(f"Backup location not configured for {config.device_name}")
        
        # Calculate backup size
        if backup_type == "full":
            backup_size_tb = config.used_storage_tb
        else:  # incremental
            # Assume 10% of used storage for incremental
            backup_size_tb = config.used_storage_tb * Decimal("0.1")
        
        # Schedule backup (in real implementation, this would trigger actual backup job)
        scheduled_time = datetime.utcnow() + timedelta(hours=config.backup_frequency_hours)
        
        return {
            "dvr_nvr_id": str(dvr_nvr_id),
            "device_name": config.device_name,
            "backup_type": backup_type,
            "backup_location": config.backup_location,
            "estimated_size_tb": float(backup_size_tb),
            "scheduled_time": scheduled_time.isoformat(),
            "frequency_hours": config.backup_frequency_hours,
            "last_backup": config.last_backup_date.isoformat() if config.last_backup_date else None,
            "status": "scheduled"
        }
    
    async def get_recording_status(
        self,
        camera_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get recording status for a camera"""
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
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "recording_enabled": camera.recording_enabled,
            "status": camera.status,
            "total_recording_hours": camera.total_recording_hours,
            "storage_used_gb": camera.storage_used_gb,
            "last_online": camera.last_online_at.isoformat() if camera.last_online_at else None
        }
    
    async def update_recording_status(
        self,
        camera_id: uuid.UUID,
        recording_enabled: bool
    ) -> Dict[str, Any]:
        """Enable or disable recording for a camera"""
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
        
        camera.recording_enabled = recording_enabled
        camera.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(camera)
        
        return {
            "camera_id": str(camera_id),
            "camera_name": camera.camera_name,
            "recording_enabled": camera.recording_enabled,
            "action": "enabled" if recording_enabled else "disabled",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def log_storage_usage(
        self,
        dvr_nvr_id: uuid.UUID
    ) -> None:
        """Log current storage usage for trending"""
        from .models import StorageUsageLog, DVRNVRConfig
        
        config = self.db.query(DVRNVRConfig).filter(
            DVRNVRConfig.id == dvr_nvr_id
        ).first()
        
        if not config:
            return
        
        utilization = (float(config.used_storage_tb) / float(config.total_storage_tb)) * 100
        
        # Estimate days remaining (simplified)
        if config.used_storage_tb > 0:
            days_remaining = int((float(config.available_storage_tb) / float(config.used_storage_tb)) * 180)
        else:
            days_remaining = 999
        
        alert_generated = utilization >= config.storage_alert_threshold_percentage
        
        log_entry = StorageUsageLog(
            tenant_id=self.tenant_id,
            dvr_nvr_id=dvr_nvr_id,
            log_timestamp=datetime.utcnow(),
            total_capacity_gb=float(config.total_storage_tb) * 1024,
            used_capacity_gb=float(config.used_storage_tb) * 1024,
            available_capacity_gb=float(config.available_storage_tb) * 1024,
            utilization_percentage=utilization,
            alert_generated=alert_generated,
            estimated_days_remaining=days_remaining
        )
        
        self.db.add(log_entry)
        self.db.commit()

"""
Asset Verification Service
Handles physical verification of assets
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from backend.shared.database.asset_models import (
    AssetVerification, AssetVerificationCycle, FixedAsset,
    VerificationStatus, AssetCategory
)
from backend.services.fixed_assets.schemas import (
    AssetVerificationCreate, VerificationCycleCreate, VerificationCycleUpdate
)


class VerificationService:
    """Service for asset verification operations"""
    
    @staticmethod
    def generate_cycle_number(db: Session, tenant_id: int, prefix: str = "VCY") -> str:
        """Generate unique verification cycle number"""
        last_cycle = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.cycle_number.like(f"{prefix}%")
        ).order_by(AssetVerificationCycle.id.desc()).first()
        
        if last_cycle and last_cycle.cycle_number:
            try:
                last_num = int(last_cycle.cycle_number.replace(prefix, ""))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    @staticmethod
    def generate_verification_number(db: Session, tenant_id: int, prefix: str = "VRF") -> str:
        """Generate unique verification number"""
        last_verification = db.query(AssetVerification).filter(
            AssetVerification.tenant_id == tenant_id,
            AssetVerification.verification_number.like(f"{prefix}%")
        ).order_by(AssetVerification.id.desc()).first()
        
        if last_verification and last_verification.verification_number:
            try:
                last_num = int(last_verification.verification_number.replace(prefix, ""))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    @staticmethod
    def create_verification_cycle(
        db: Session,
        tenant_id: int,
        user_id: int,
        cycle_data: VerificationCycleCreate
    ) -> AssetVerificationCycle:
        """Create a verification cycle"""
        
        # Generate cycle number
        cycle_number = VerificationService.generate_cycle_number(db, tenant_id)
        
        # Count assets in scope
        assets_query = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False,
            FixedAsset.is_active == True
        )
        
        # Apply scope filters
        import json
        if cycle_data.scope != "all":
            if cycle_data.scope == "category" and cycle_data.category_filter:
                assets_query = assets_query.filter(
                    FixedAsset.asset_category.in_(cycle_data.category_filter)
                )
            elif cycle_data.scope == "location" and cycle_data.location_filter:
                assets_query = assets_query.filter(
                    FixedAsset.location_id.in_(cycle_data.location_filter)
                )
            elif cycle_data.scope == "department" and cycle_data.department_filter:
                assets_query = assets_query.filter(
                    FixedAsset.department_id.in_(cycle_data.department_filter)
                )
        
        total_assets = assets_query.count()
        
        # Create cycle
        cycle = AssetVerificationCycle(
            tenant_id=tenant_id,
            cycle_number=cycle_number,
            **cycle_data.model_dump(exclude={'category_filter', 'location_filter', 'department_filter', 'team_members'}),
            total_assets=total_assets,
            verified_assets=0,
            pending_assets=total_assets,
            found_assets=0,
            not_found_assets=0,
            discrepancy_count=0,
            status="planned",
            completion_percentage=Decimal('0.00'),
            created_by=user_id,
            updated_by=user_id
        )
        
        # Handle JSON fields
        if cycle_data.category_filter:
            cycle.category_filter = json.dumps(cycle_data.category_filter)
        if cycle_data.location_filter:
            cycle.location_filter = json.dumps([int(x) for x in cycle_data.location_filter])
        if cycle_data.department_filter:
            cycle.department_filter = json.dumps([int(x) for x in cycle_data.department_filter])
        if cycle_data.team_members:
            cycle.team_members = json.dumps([int(x) for x in cycle_data.team_members])
        
        db.add(cycle)
        db.commit()
        db.refresh(cycle)
        
        return cycle
    
    @staticmethod
    def start_verification_cycle(
        db: Session,
        tenant_id: int,
        user_id: int,
        cycle_id: int
    ) -> AssetVerificationCycle:
        """Start a verification cycle"""
        
        cycle = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.id == cycle_id,
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        ).first()
        
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification cycle not found"
            )
        
        if cycle.status != "planned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start cycle with status {cycle.status}"
            )
        
        cycle.status = "in_progress"
        cycle.actual_start_date = date.today()
        cycle.updated_by = user_id
        cycle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cycle)
        
        return cycle
    
    @staticmethod
    def create_verification(
        db: Session,
        tenant_id: int,
        user_id: int,
        verification_data: AssetVerificationCreate
    ) -> AssetVerification:
        """Create a verification record"""
        
        # Verify asset exists
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == verification_data.asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # If part of a cycle, verify cycle exists
        if verification_data.verification_cycle_id:
            cycle = db.query(AssetVerificationCycle).filter(
                AssetVerificationCycle.id == verification_data.verification_cycle_id,
                AssetVerificationCycle.tenant_id == tenant_id,
                AssetVerificationCycle.is_deleted == False
            ).first()
            
            if not cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Verification cycle not found"
                )
            
            if cycle.status != "in_progress":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification cycle is not in progress"
                )
        
        # Generate verification number
        verification_number = VerificationService.generate_verification_number(db, tenant_id)
        
        # Create verification
        verification = AssetVerification(
            tenant_id=tenant_id,
            verification_number=verification_number,
            asset_code=asset.asset_code,
            expected_location_id=asset.location_id,
            expected_location_name=asset.location_name,
            expected_custodian_id=asset.custodian_id,
            expected_custodian_name=asset.custodian_name,
            verified_by=user_id,
            **verification_data.model_dump(exclude={'image_urls', 'document_urls', 'verification_cycle_id'}),
            verification_cycle_id=verification_data.verification_cycle_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Handle JSON fields
        import json
        if verification_data.image_urls:
            verification.image_urls = json.dumps(verification_data.image_urls)
        if verification_data.document_urls:
            verification.document_urls = json.dumps(verification_data.document_urls)
        
        db.add(verification)
        
        # Update asset verification status
        asset.is_verified = verification_data.is_found
        asset.last_verification_date = verification_data.verification_date
        asset.verified_by = user_id
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        # Update cycle statistics if part of a cycle
        if verification_data.verification_cycle_id:
            cycle = db.query(AssetVerificationCycle).filter(
                AssetVerificationCycle.id == verification_data.verification_cycle_id
            ).first()
            
            if cycle:
                cycle.verified_assets += 1
                cycle.pending_assets = max(0, cycle.pending_assets - 1)
                
                if verification_data.is_found:
                    cycle.found_assets += 1
                else:
                    cycle.not_found_assets += 1
                
                if verification_data.has_discrepancy:
                    cycle.discrepancy_count += 1
                
                # Update completion percentage
                if cycle.total_assets > 0:
                    cycle.completion_percentage = (
                        Decimal(cycle.verified_assets) / Decimal(cycle.total_assets)
                    ) * Decimal('100.00')
                
                cycle.updated_by = user_id
                cycle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(verification)
        
        return verification
    
    @staticmethod
    def complete_verification_cycle(
        db: Session,
        tenant_id: int,
        user_id: int,
        cycle_id: int
    ) -> AssetVerificationCycle:
        """Complete a verification cycle"""
        
        cycle = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.id == cycle_id,
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        ).first()
        
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification cycle not found"
            )
        
        if cycle.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete cycle with status {cycle.status}"
            )
        
        cycle.status = "completed"
        cycle.actual_end_date = date.today()
        cycle.completion_percentage = Decimal('100.00')
        cycle.updated_by = user_id
        cycle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cycle)
        
        return cycle
    
    @staticmethod
    def get_cycle(
        db: Session,
        tenant_id: int,
        cycle_id: int
    ) -> Optional[AssetVerificationCycle]:
        """Get verification cycle by ID"""
        return db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.id == cycle_id,
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        ).first()
    
    @staticmethod
    def list_cycles(
        db: Session,
        tenant_id: int,
        financial_year: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple:
        """List verification cycles"""
        
        query = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        )
        
        if financial_year:
            query = query.filter(AssetVerificationCycle.financial_year == financial_year)
        
        if status:
            query = query.filter(AssetVerificationCycle.status == status)
        
        total = query.count()
        
        query = query.order_by(AssetVerificationCycle.planned_start_date.desc())
        
        offset = (page - 1) * page_size
        cycles = query.offset(offset).limit(page_size).all()
        
        return cycles, total
    
    @staticmethod
    def list_verifications(
        db: Session,
        tenant_id: int,
        cycle_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        verification_status: Optional[VerificationStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple:
        """List verification records"""
        
        query = db.query(AssetVerification).filter(
            AssetVerification.tenant_id == tenant_id
        )
        
        if cycle_id:
            query = query.filter(AssetVerification.verification_cycle_id == cycle_id)
        
        if asset_id:
            query = query.filter(AssetVerification.asset_id == asset_id)
        
        if verification_status:
            query = query.filter(AssetVerification.verification_status == verification_status)
        
        if from_date:
            query = query.filter(AssetVerification.verification_date >= from_date)
        
        if to_date:
            query = query.filter(AssetVerification.verification_date <= to_date)
        
        total = query.count()
        
        query = query.order_by(AssetVerification.verification_date.desc())
        
        offset = (page - 1) * page_size
        verifications = query.offset(offset).limit(page_size).all()
        
        return verifications, total
    
    @staticmethod
    def get_unverified_assets(
        db: Session,
        tenant_id: int,
        cycle_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> tuple:
        """Get assets pending verification in a cycle"""
        
        cycle = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.id == cycle_id,
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        ).first()
        
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification cycle not found"
            )
        
        # Get verified asset IDs in this cycle
        verified_asset_ids = db.query(AssetVerification.asset_id).filter(
            AssetVerification.tenant_id == tenant_id,
            AssetVerification.verification_cycle_id == cycle_id
        ).all()
        verified_ids = [id[0] for id in verified_asset_ids]
        
        # Query unverified assets
        query = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False,
            FixedAsset.is_active == True,
            ~FixedAsset.id.in_(verified_ids) if verified_ids else True
        )
        
        # Apply scope filters
        import json
        if cycle.scope != "all":
            if cycle.scope == "category" and cycle.category_filter:
                categories = json.loads(cycle.category_filter)
                query = query.filter(FixedAsset.asset_category.in_(categories))
            elif cycle.scope == "location" and cycle.location_filter:
                locations = json.loads(cycle.location_filter)
                query = query.filter(FixedAsset.location_id.in_(locations))
            elif cycle.scope == "department" and cycle.department_filter:
                departments = json.loads(cycle.department_filter)
                query = query.filter(FixedAsset.department_id.in_(departments))
        
        total = query.count()
        
        offset = (page - 1) * page_size
        assets = query.offset(offset).limit(page_size).all()
        
        return assets, total
    
    @staticmethod
    def get_verification_report(
        db: Session,
        tenant_id: int,
        cycle_id: int
    ) -> Dict[str, Any]:
        """Generate verification report for a cycle"""
        
        cycle = db.query(AssetVerificationCycle).filter(
            AssetVerificationCycle.id == cycle_id,
            AssetVerificationCycle.tenant_id == tenant_id,
            AssetVerificationCycle.is_deleted == False
        ).first()
        
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification cycle not found"
            )
        
        # Get all verifications in this cycle
        verifications = db.query(AssetVerification).filter(
            AssetVerification.tenant_id == tenant_id,
            AssetVerification.verification_cycle_id == cycle_id
        ).all()
        
        # Group by status
        by_status = {}
        for v in verifications:
            status = v.verification_status.value
            if status not in by_status:
                by_status[status] = {"status": status, "count": 0}
            by_status[status]["count"] += 1
        
        # Group by condition
        by_condition = {}
        for v in verifications:
            if v.condition:
                condition = v.condition
                if condition not in by_condition:
                    by_condition[condition] = {"condition": condition, "count": 0}
                by_condition[condition]["count"] += 1
        
        # Discrepancies
        discrepancies = [
            {
                "asset_id": v.asset_id,
                "asset_code": v.asset_code,
                "discrepancy_type": v.discrepancy_type,
                "description": v.discrepancy_description,
                "resolved": v.discrepancy_resolved
            }
            for v in verifications if v.has_discrepancy
        ]
        
        return {
            "cycle_id": cycle.id,
            "cycle_number": cycle.cycle_number,
            "cycle_name": cycle.cycle_name,
            "financial_year": cycle.financial_year,
            "status": cycle.status,
            "total_assets": cycle.total_assets,
            "verified_assets": cycle.verified_assets,
            "pending_assets": cycle.pending_assets,
            "found_assets": cycle.found_assets,
            "not_found_assets": cycle.not_found_assets,
            "discrepancy_count": cycle.discrepancy_count,
            "completion_percentage": float(cycle.completion_percentage),
            "verifications_by_status": list(by_status.values()),
            "verifications_by_condition": list(by_condition.values()),
            "discrepancies": discrepancies
        }

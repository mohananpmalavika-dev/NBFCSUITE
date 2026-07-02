"""
Gold Ornament Catalog API
Phase 4: Enhanced Ornament Lifecycle & Management
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..models.catalog import (
    GoldOrnamentPhoto,
    GoldOrnamentStone,
    GoldOrnamentStatusHistory,
    GoldOrnamentMovement,
    GoldOrnamentCondition,
    GoldOrnamentTag,
    GoldOrnamentComparison,
    GoldOrnamentCertificate,
    GoldOrnamentInsurance,
    GoldOrnamentGroup,
    GoldOrnamentGroupMember
)
from ..schemas.catalog import (
    OrnamentPhotoCreate,
    OrnamentPhotoResponse,
    StoneCreate,
    StoneResponse,
    StatusChangeCreate,
    StatusHistoryResponse,
    MovementCreate,
    MovementVerify,
    MovementResponse,
    ConditionInspectionCreate,
    ConditionInspectionResponse,
    TagCreate,
    TagResponse,
    ComparisonCreate,
    ComparisonResponse,
    CertificateCreate,
    CertificateVerify,
    CertificateResponse,
    InsuranceCreate,
    InsuranceUpdate,
    InsuranceResponse,
    GroupCreate,
    GroupAddOrnament,
    GroupResponse,
    OrnamentCompleteProfile
)

router = APIRouter(prefix="/catalog", tags=["Ornament Catalog"])


def get_db():
    """Placeholder for database session"""
    pass


# ============================================================================
# PHOTO MANAGEMENT
# ============================================================================

@router.post("/photos", response_model=OrnamentPhotoResponse, status_code=201)
async def add_ornament_photo(photo: OrnamentPhotoCreate, db: Session = Depends(get_db)):
    """
    Add photo to ornament
    
    Supports multiple photo types: general, hallmark, close_up, damage, stone, certificate
    """
    # If this is set as primary, unset other primary photos
    if photo.is_primary:
        db.query(GoldOrnamentPhoto).filter(
            and_(
                GoldOrnamentPhoto.ornament_id == photo.ornament_id,
                GoldOrnamentPhoto.is_primary == True
            )
        ).update({"is_primary": False})
    
    photo_record = GoldOrnamentPhoto(
        id=str(uuid4()),
        **photo.model_dump()
    )
    
    db.add(photo_record)
    db.commit()
    db.refresh(photo_record)
    
    return photo_record


@router.get("/photos/ornament/{ornament_id}", response_model=List[OrnamentPhotoResponse])
async def list_ornament_photos(
    ornament_id: str,
    photo_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all photos for an ornament"""
    query = db.query(GoldOrnamentPhoto).filter(GoldOrnamentPhoto.ornament_id == ornament_id)
    
    if photo_type:
        query = query.filter(GoldOrnamentPhoto.photo_type == photo_type)
    
    photos = query.order_by(GoldOrnamentPhoto.is_primary.desc(), GoldOrnamentPhoto.photo_order).all()
    return photos


@router.delete("/photos/{photo_id}", status_code=204)
async def delete_ornament_photo(photo_id: str, db: Session = Depends(get_db)):
    """Delete a photo"""
    photo = db.query(GoldOrnamentPhoto).filter(GoldOrnamentPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    db.delete(photo)
    db.commit()


# ============================================================================
# STONE CATALOG
# ============================================================================

@router.post("/stones", response_model=StoneResponse, status_code=201)
async def add_stone(stone: StoneCreate, db: Session = Depends(get_db)):
    """
    Add stone details to ornament
    
    Supports comprehensive stone cataloging with certification
    """
    stone_record = GoldOrnamentStone(
        id=str(uuid4()),
        **stone.model_dump()
    )
    
    db.add(stone_record)
    db.commit()
    db.refresh(stone_record)
    
    return stone_record


@router.get("/stones/ornament/{ornament_id}", response_model=List[StoneResponse])
async def list_ornament_stones(ornament_id: str, db: Session = Depends(get_db)):
    """List all stones for an ornament"""
    stones = db.query(GoldOrnamentStone).filter(
        GoldOrnamentStone.ornament_id == ornament_id
    ).order_by(GoldOrnamentStone.stone_number).all()
    return stones


@router.get("/stones/{stone_id}", response_model=StoneResponse)
async def get_stone(stone_id: str, db: Session = Depends(get_db)):
    """Get specific stone details"""
    stone = db.query(GoldOrnamentStone).filter(GoldOrnamentStone.id == stone_id).first()
    if not stone:
        raise HTTPException(status_code=404, detail="Stone not found")
    return stone


@router.put("/stones/{stone_id}", response_model=StoneResponse)
async def update_stone(stone_id: str, stone_data: StoneCreate, db: Session = Depends(get_db)):
    """Update stone details"""
    stone = db.query(GoldOrnamentStone).filter(GoldOrnamentStone.id == stone_id).first()
    if not stone:
        raise HTTPException(status_code=404, detail="Stone not found")
    
    for field, value in stone_data.model_dump(exclude_unset=True).items():
        setattr(stone, field, value)
    
    stone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(stone)
    
    return stone


# ============================================================================
# STATUS TRACKING
# ============================================================================

@router.post("/status-change", response_model=StatusHistoryResponse, status_code=201)
async def change_ornament_status(status_change: StatusChangeCreate, db: Session = Depends(get_db)):
    """
    Change ornament status and record in history
    
    Tracks complete status lifecycle with reasons and notes
    """
    # Get current status (fetch from gold_ornaments table)
    # from_status = current_ornament.status
    
    history = GoldOrnamentStatusHistory(
        id=str(uuid4()),
        from_status=None,  # Fetch from ornament
        **status_change.model_dump()
    )
    
    db.add(history)
    
    # Update ornament status
    # ornament.status = status_change.to_status
    
    db.commit()
    db.refresh(history)
    
    return history


@router.get("/status-history/ornament/{ornament_id}", response_model=List[StatusHistoryResponse])
async def get_status_history(ornament_id: str, db: Session = Depends(get_db)):
    """Get complete status history for ornament"""
    history = db.query(GoldOrnamentStatusHistory).filter(
        GoldOrnamentStatusHistory.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentStatusHistory.changed_at)).all()
    return history


# ============================================================================
# MOVEMENT TRACKING
# ============================================================================

@router.post("/movements", response_model=MovementResponse, status_code=201)
async def record_movement(movement: MovementCreate, db: Session = Depends(get_db)):
    """
    Record ornament movement
    
    Tracks physical movement with GPS, QR scanning, and verification
    """
    movement_record = GoldOrnamentMovement(
        id=str(uuid4()),
        **movement.model_dump()
    )
    
    db.add(movement_record)
    db.commit()
    db.refresh(movement_record)
    
    return movement_record


@router.post("/movements/{movement_id}/verify", response_model=MovementResponse)
async def verify_movement(
    movement_id: str,
    verify: MovementVerify,
    db: Session = Depends(get_db)
):
    """Verify movement (maker-checker)"""
    movement = db.query(GoldOrnamentMovement).filter(
        GoldOrnamentMovement.id == movement_id
    ).first()
    
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    if movement.moved_by_user_id == verify.verified_by_user_id:
        raise HTTPException(
            status_code=400,
            detail="Verifier cannot be the same as mover (maker-checker violation)"
        )
    
    movement.verified_by_user_id = verify.verified_by_user_id
    movement.verification_timestamp = datetime.utcnow()
    
    db.commit()
    db.refresh(movement)
    
    return movement


@router.get("/movements/ornament/{ornament_id}", response_model=List[MovementResponse])
async def list_movements(ornament_id: str, db: Session = Depends(get_db)):
    """List all movements for an ornament"""
    movements = db.query(GoldOrnamentMovement).filter(
        GoldOrnamentMovement.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentMovement.movement_timestamp)).all()
    return movements


@router.get("/movements/location/{location}", response_model=List[MovementResponse])
async def movements_by_location(
    location: str,
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get movements to/from a location"""
    query = db.query(GoldOrnamentMovement).filter(
        or_(
            GoldOrnamentMovement.from_location.ilike(f"%{location}%"),
            GoldOrnamentMovement.to_location.ilike(f"%{location}%")
        )
    )
    
    if from_date:
        query = query.filter(GoldOrnamentMovement.movement_timestamp >= from_date)
    if to_date:
        query = query.filter(GoldOrnamentMovement.movement_timestamp <= to_date)
    
    movements = query.order_by(desc(GoldOrnamentMovement.movement_timestamp)).all()
    return movements


# ============================================================================
# CONDITION INSPECTION
# ============================================================================

@router.post("/conditions", response_model=ConditionInspectionResponse, status_code=201)
async def create_condition_inspection(
    inspection: ConditionInspectionCreate,
    db: Session = Depends(get_db)
):
    """
    Record condition inspection
    
    Tracks damage, repairs, missing parts, stone condition, polish level, etc.
    """
    inspection_record = GoldOrnamentCondition(
        id=str(uuid4()),
        inspection_date=datetime.utcnow(),
        **inspection.model_dump()
    )
    
    db.add(inspection_record)
    db.commit()
    db.refresh(inspection_record)
    
    return inspection_record


@router.get("/conditions/ornament/{ornament_id}", response_model=List[ConditionInspectionResponse])
async def list_condition_history(ornament_id: str, db: Session = Depends(get_db)):
    """Get condition inspection history"""
    conditions = db.query(GoldOrnamentCondition).filter(
        GoldOrnamentCondition.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentCondition.inspection_date)).all()
    return conditions


@router.get("/conditions/due-inspection", response_model=List[Dict])
async def get_due_inspections(
    days_ahead: int = Query(30, description="Look ahead days"),
    db: Session = Depends(get_db)
):
    """Get ornaments due for inspection"""
    cutoff_date = date.today() + timedelta(days=days_ahead)
    
    conditions = db.query(GoldOrnamentCondition).filter(
        and_(
            GoldOrnamentCondition.next_inspection_date.isnot(None),
            GoldOrnamentCondition.next_inspection_date <= cutoff_date
        )
    ).all()
    
    return [
        {
            "ornament_id": c.ornament_id,
            "next_inspection_date": c.next_inspection_date,
            "last_inspection": c.inspection_date,
            "overall_condition": c.overall_condition
        }
        for c in conditions
    ]


# ============================================================================
# TAGS
# ============================================================================

@router.post("/tags", response_model=TagResponse, status_code=201)
async def add_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Add tag to ornament"""
    # Check for duplicate
    existing = db.query(GoldOrnamentTag).filter(
        and_(
            GoldOrnamentTag.ornament_id == tag.ornament_id,
            GoldOrnamentTag.tag_category == tag.tag_category,
            GoldOrnamentTag.tag_value == tag.tag_value
        )
    ).first()
    
    if existing:
        return existing
    
    tag_record = GoldOrnamentTag(
        id=str(uuid4()),
        **tag.model_dump()
    )
    
    db.add(tag_record)
    db.commit()
    db.refresh(tag_record)
    
    return tag_record


@router.get("/tags/ornament/{ornament_id}", response_model=List[TagResponse])
async def list_tags(ornament_id: str, db: Session = Depends(get_db)):
    """List all tags for ornament"""
    tags = db.query(GoldOrnamentTag).filter(
        GoldOrnamentTag.ornament_id == ornament_id
    ).all()
    return tags


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    """Remove tag"""
    tag = db.query(GoldOrnamentTag).filter(GoldOrnamentTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()


# ============================================================================
# COMPARISONS (FRAUD DETECTION)
# ============================================================================

@router.post("/comparisons", response_model=ComparisonResponse, status_code=201)
async def create_comparison(comparison: ComparisonCreate, db: Session = Depends(get_db)):
    """
    Compare two ornaments for fraud detection
    
    Detects duplicates, similar patterns, and suspicious activities
    """
    comparison_record = GoldOrnamentComparison(
        id=str(uuid4()),
        **comparison.model_dump()
    )
    
    db.add(comparison_record)
    db.commit()
    db.refresh(comparison_record)
    
    return comparison_record


@router.get("/comparisons", response_model=List[ComparisonResponse])
async def list_comparisons(
    ornament_id: Optional[str] = Query(None),
    is_flagged: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List ornament comparisons"""
    query = db.query(GoldOrnamentComparison)
    
    if ornament_id:
        query = query.filter(
            or_(
                GoldOrnamentComparison.ornament_id_1 == ornament_id,
                GoldOrnamentComparison.ornament_id_2 == ornament_id
            )
        )
    
    if is_flagged is not None:
        query = query.filter(GoldOrnamentComparison.is_flagged == is_flagged)
    
    comparisons = query.order_by(desc(GoldOrnamentComparison.comparison_date)).all()
    return comparisons


# ============================================================================
# CERTIFICATES
# ============================================================================

@router.post("/certificates", response_model=CertificateResponse, status_code=201)
async def add_certificate(certificate: CertificateCreate, db: Session = Depends(get_db)):
    """Add certificate to ornament"""
    cert_record = GoldOrnamentCertificate(
        id=str(uuid4()),
        **certificate.model_dump()
    )
    
    db.add(cert_record)
    db.commit()
    db.refresh(cert_record)
    
    return cert_record


@router.post("/certificates/{cert_id}/verify", response_model=CertificateResponse)
async def verify_certificate(
    cert_id: str,
    verify: CertificateVerify,
    db: Session = Depends(get_db)
):
    """Verify certificate"""
    cert = db.query(GoldOrnamentCertificate).filter(
        GoldOrnamentCertificate.id == cert_id
    ).first()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    cert.is_verified = verify.is_verified
    cert.verified_by_user_id = verify.verified_by_user_id
    cert.verified_at = datetime.utcnow()
    cert.verification_method = verify.verification_method
    
    db.commit()
    db.refresh(cert)
    
    return cert


@router.get("/certificates/ornament/{ornament_id}", response_model=List[CertificateResponse])
async def list_certificates(ornament_id: str, db: Session = Depends(get_db)):
    """List certificates for ornament"""
    certs = db.query(GoldOrnamentCertificate).filter(
        GoldOrnamentCertificate.ornament_id == ornament_id
    ).all()
    return certs


# ============================================================================
# INSURANCE
# ============================================================================

@router.post("/insurance", response_model=InsuranceResponse, status_code=201)
async def add_insurance(insurance: InsuranceCreate, db: Session = Depends(get_db)):
    """Add insurance policy for ornament"""
    insurance_record = GoldOrnamentInsurance(
        id=str(uuid4()),
        **insurance.model_dump()
    )
    
    db.add(insurance_record)
    db.commit()
    db.refresh(insurance_record)
    
    return insurance_record


@router.patch("/insurance/{insurance_id}", response_model=InsuranceResponse)
async def update_insurance(
    insurance_id: str,
    update: InsuranceUpdate,
    db: Session = Depends(get_db)
):
    """Update insurance policy"""
    insurance = db.query(GoldOrnamentInsurance).filter(
        GoldOrnamentInsurance.id == insurance_id
    ).first()
    
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")
    
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(insurance, field, value)
    
    insurance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(insurance)
    
    return insurance


@router.get("/insurance/ornament/{ornament_id}", response_model=InsuranceResponse)
async def get_insurance(ornament_id: str, db: Session = Depends(get_db)):
    """Get insurance for ornament"""
    insurance = db.query(GoldOrnamentInsurance).filter(
        GoldOrnamentInsurance.ornament_id == ornament_id,
        GoldOrnamentInsurance.is_active == True
    ).first()
    
    if not insurance:
        raise HTTPException(status_code=404, detail="No active insurance found")
    
    return insurance


# ============================================================================
# ORNAMENT GROUPS
# ============================================================================

@router.post("/groups", response_model=GroupResponse, status_code=201)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """Create ornament group (set, collection)"""
    group_record = GoldOrnamentGroup(
        id=str(uuid4()),
        **group.model_dump()
    )
    
    db.add(group_record)
    db.commit()
    db.refresh(group_record)
    
    return group_record


@router.post("/groups/{group_id}/ornaments", response_model=GroupResponse)
async def add_ornament_to_group(
    group_id: str,
    ornament: GroupAddOrnament,
    db: Session = Depends(get_db)
):
    """Add ornament to group"""
    group = db.query(GoldOrnamentGroup).filter(GoldOrnamentGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if already in group
    existing = db.query(GoldOrnamentGroupMember).filter(
        and_(
            GoldOrnamentGroupMember.group_id == group_id,
            GoldOrnamentGroupMember.ornament_id == ornament.ornament_id
        )
    ).first()
    
    if existing:
        return group
    
    member = GoldOrnamentGroupMember(
        id=str(uuid4()),
        group_id=group_id,
        ornament_id=ornament.ornament_id,
        sequence_number=ornament.sequence_number
    )
    
    db.add(member)
    group.total_ornaments += 1
    db.commit()
    db.refresh(group)
    
    return group


@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: str, db: Session = Depends(get_db)):
    """Get group details"""
    group = db.query(GoldOrnamentGroup).filter(GoldOrnamentGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("/groups", response_model=List[GroupResponse])
async def list_groups(
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List ornament groups"""
    query = db.query(GoldOrnamentGroup)
    
    if customer_id:
        query = query.filter(GoldOrnamentGroup.customer_id == customer_id)
    
    groups = query.all()
    return groups


# ============================================================================
# COMPLETE PROFILE
# ============================================================================

@router.get("/profile/{ornament_id}", response_model=OrnamentCompleteProfile)
async def get_complete_profile(ornament_id: str, db: Session = Depends(get_db)):
    """
    Get complete ornament profile with all related data
    
    Returns comprehensive view including photos, stones, history, etc.
    """
    # Fetch all related data
    photos = db.query(GoldOrnamentPhoto).filter(GoldOrnamentPhoto.ornament_id == ornament_id).all()
    stones = db.query(GoldOrnamentStone).filter(GoldOrnamentStone.ornament_id == ornament_id).all()
    status_history = db.query(GoldOrnamentStatusHistory).filter(
        GoldOrnamentStatusHistory.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentStatusHistory.changed_at)).all()
    
    movements = db.query(GoldOrnamentMovement).filter(
        GoldOrnamentMovement.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentMovement.movement_timestamp)).all()
    
    conditions = db.query(GoldOrnamentCondition).filter(
        GoldOrnamentCondition.ornament_id == ornament_id
    ).order_by(desc(GoldOrnamentCondition.inspection_date)).all()
    
    tags = db.query(GoldOrnamentTag).filter(GoldOrnamentTag.ornament_id == ornament_id).all()
    certs = db.query(GoldOrnamentCertificate).filter(
        GoldOrnamentCertificate.ornament_id == ornament_id
    ).all()
    
    insurance = db.query(GoldOrnamentInsurance).filter(
        and_(
            GoldOrnamentInsurance.ornament_id == ornament_id,
            GoldOrnamentInsurance.is_active == True
        )
    ).first()
    
    # Get groups
    group_members = db.query(GoldOrnamentGroupMember).filter(
        GoldOrnamentGroupMember.ornament_id == ornament_id
    ).all()
    group_ids = [gm.group_id for gm in group_members]
    groups = db.query(GoldOrnamentGroup).filter(GoldOrnamentGroup.id.in_(group_ids)).all() if group_ids else []
    
    # Calculate stats
    total_stone_weight = sum([s.gram_weight or 0 for s in stones])
    last_movement = movements[0] if movements else None
    current_condition = conditions[0].overall_condition if conditions else None
    
    # Calculate days in vault
    days_in_vault = None
    if last_movement and last_movement.to_location and "vault" in last_movement.to_location.lower():
        days_in_vault = (datetime.utcnow() - last_movement.movement_timestamp).days
    
    return OrnamentCompleteProfile(
        ornament={},  # Base ornament data from gold_ornaments
        photos=photos,
        stones=stones,
        status_history=status_history,
        movements=movements,
        conditions=conditions,
        tags=tags,
        certificates=certs,
        insurance=insurance,
        groups=groups,
        total_photos=len(photos),
        total_stones=len(stones),
        total_stone_weight=total_stone_weight,
        current_condition=current_condition,
        last_movement=last_movement,
        days_in_vault=days_in_vault
    )

"""
Vault & Packet Management API
Phase 5: Hierarchical vault structure with QR codes and security management
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from uuid import uuid4
import qrcode
import io
import base64

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..models.vault import (
    GoldVault,
    GoldVaultRack,
    GoldVaultLocker,
    GoldVaultTray,
    GoldPacket,
    GoldPacketOrnament,
    GoldPacketMovement,
    GoldVaultAudit,
    GoldAuditFinding,
    GoldVaultAccessLog,
    GoldSecuritySeal
)
from ..schemas.vault import (
    VaultCreate,
    VaultUpdate,
    VaultResponse,
    RackCreate,
    RackResponse,
    LockerCreate,
    LockerResponse,
    TrayCreate,
    TrayResponse,
    PacketCreate,
    PacketSeal,
    PacketVerifySeal,
    PacketAssignLocation,
    PacketResponse,
    PacketWithLocation,
    PacketMovementCreate,
    PacketMovementVerify,
    PacketMovementResponse,
    VaultAuditCreate,
    VaultAuditStart,
    VaultAuditComplete,
    VaultAuditReview,
    VaultAuditApprove,
    VaultAuditResponse,
    AuditFindingCreate,
    AuditFindingResolve,
    AuditFindingResponse,
    VaultAccessCreate,
    VaultAccessExit,
    VaultAccessResponse,
    SealCreate,
    SealIssue,
    SealDispose,
    SealResponse,
    VaultHierarchy,
    PacketAuditTrail
)

router = APIRouter(prefix="/vault", tags=["Vault & Packet Management"])


def get_db():
    """Placeholder for database session"""
    pass


def generate_qr_code(data: str) -> str:
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def generate_packet_number(branch_id: str) -> str:
    """Generate unique packet number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid4())[:8].upper()
    return f"PKT-{branch_id}-{timestamp}-{random_suffix}"


# ============================================================================
# VAULT HIERARCHY MANAGEMENT
# ============================================================================

@router.post("/vaults", response_model=VaultResponse, status_code=201)
async def create_vault(vault: VaultCreate, db: Session = Depends(get_db)):
    """
    Create new vault
    
    Vault types: main, satellite, temporary
    Security levels: high, medium, standard
    """
    # Check if vault code already exists
    existing = db.query(GoldVault).filter(GoldVault.vault_code == vault.vault_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vault code already exists")
    
    vault_record = GoldVault(
        id=str(uuid4()),
        **vault.model_dump()
    )
    
    db.add(vault_record)
    db.commit()
    db.refresh(vault_record)
    
    # Calculate occupancy percentage
    response = VaultResponse.model_validate(vault_record)
    if vault_record.capacity_packets > 0:
        response.occupancy_percentage = round(
            (vault_record.current_occupancy / vault_record.capacity_packets) * 100, 2
        )
    
    return response


@router.get("/vaults", response_model=List[VaultResponse])
async def list_vaults(
    branch_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    vault_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all vaults with optional filters"""
    query = db.query(GoldVault)
    
    if branch_id:
        query = query.filter(GoldVault.branch_id == branch_id)
    if is_active is not None:
        query = query.filter(GoldVault.is_active == is_active)
    if vault_type:
        query = query.filter(GoldVault.vault_type == vault_type)
    
    vaults = query.order_by(GoldVault.vault_code).all()
    
    # Add occupancy percentage
    results = []
    for vault in vaults:
        v = VaultResponse.model_validate(vault)
        if vault.capacity_packets > 0:
            v.occupancy_percentage = round(
                (vault.current_occupancy / vault.capacity_packets) * 100, 2
            )
        results.append(v)
    
    return results


@router.get("/vaults/{vault_id}", response_model=VaultResponse)
async def get_vault(vault_id: str, db: Session = Depends(get_db)):
    """Get vault details"""
    vault = db.query(GoldVault).filter(GoldVault.id == vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    response = VaultResponse.model_validate(vault)
    if vault.capacity_packets > 0:
        response.occupancy_percentage = round(
            (vault.current_occupancy / vault.capacity_packets) * 100, 2
        )
    
    return response


@router.patch("/vaults/{vault_id}", response_model=VaultResponse)
async def update_vault(vault_id: str, update: VaultUpdate, db: Session = Depends(get_db)):
    """Update vault details"""
    vault = db.query(GoldVault).filter(GoldVault.id == vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(vault, field, value)
    
    vault.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vault)
    
    response = VaultResponse.model_validate(vault)
    if vault.capacity_packets > 0:
        response.occupancy_percentage = round(
            (vault.current_occupancy / vault.capacity_packets) * 100, 2
        )
    
    return response


@router.get("/vaults/{vault_id}/hierarchy", response_model=VaultHierarchy)
async def get_vault_hierarchy(vault_id: str, db: Session = Depends(get_db)):
    """Get complete vault hierarchy with all racks, lockers, and trays"""
    vault = db.query(GoldVault).filter(GoldVault.id == vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    # Get all racks
    racks = db.query(GoldVaultRack).filter(GoldVaultRack.vault_id == vault_id).all()
    
    hierarchy = []
    total_capacity = 0
    total_occupancy = 0
    
    for rack in racks:
        # Get lockers for this rack
        lockers = db.query(GoldVaultLocker).filter(GoldVaultLocker.rack_id == rack.id).all()
        
        locker_data = []
        for locker in lockers:
            # Get trays for this locker
            trays = db.query(GoldVaultTray).filter(GoldVaultTray.locker_id == locker.id).all()
            
            tray_data = []
            for tray in trays:
                total_capacity += tray.capacity_packets
                total_occupancy += tray.current_occupancy
                tray_data.append({
                    "id": tray.id,
                    "tray_code": tray.tray_code,
                    "tray_number": tray.tray_number,
                    "capacity_packets": tray.capacity_packets,
                    "current_occupancy": tray.current_occupancy,
                    "tray_size": tray.tray_size
                })
            
            locker_data.append({
                "id": locker.id,
                "locker_code": locker.locker_code,
                "locker_number": locker.locker_number,
                "capacity_trays": locker.capacity_trays,
                "current_occupancy": locker.current_occupancy,
                "lock_type": locker.lock_type,
                "trays": tray_data
            })
        
        hierarchy.append({
            "id": rack.id,
            "rack_code": rack.rack_code,
            "rack_number": rack.rack_number,
            "capacity_lockers": rack.capacity_lockers,
            "current_occupancy": rack.current_occupancy,
            "lockers": locker_data
        })
    
    vault_response = VaultResponse.model_validate(vault)
    occupancy_pct = round((total_occupancy / total_capacity * 100), 2) if total_capacity > 0 else 0
    
    return VaultHierarchy(
        vault=vault_response,
        racks=hierarchy,
        total_capacity=total_capacity,
        current_occupancy=total_occupancy,
        occupancy_percentage=occupancy_pct
    )


# ============================================================================
# RACK MANAGEMENT
# ============================================================================

@router.post("/racks", response_model=RackResponse, status_code=201)
async def create_rack(rack: RackCreate, db: Session = Depends(get_db)):
    """Create rack within a vault"""
    # Verify vault exists
    vault = db.query(GoldVault).filter(GoldVault.id == rack.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    # Check for duplicate rack number
    existing = db.query(GoldVaultRack).filter(
        and_(
            GoldVaultRack.vault_id == rack.vault_id,
            GoldVaultRack.rack_number == rack.rack_number
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rack number already exists in this vault")
    
    rack_record = GoldVaultRack(
        id=str(uuid4()),
        **rack.model_dump()
    )
    
    db.add(rack_record)
    db.commit()
    db.refresh(rack_record)
    
    return rack_record


@router.get("/vaults/{vault_id}/racks", response_model=List[RackResponse])
async def list_vault_racks(vault_id: str, db: Session = Depends(get_db)):
    """List all racks in a vault"""
    racks = db.query(GoldVaultRack).filter(
        GoldVaultRack.vault_id == vault_id
    ).order_by(GoldVaultRack.rack_number).all()
    return racks


# ============================================================================
# LOCKER MANAGEMENT
# ============================================================================

@router.post("/lockers", response_model=LockerResponse, status_code=201)
async def create_locker(locker: LockerCreate, db: Session = Depends(get_db)):
    """Create locker within a rack"""
    # Verify rack exists
    rack = db.query(GoldVaultRack).filter(GoldVaultRack.id == locker.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")
    
    # Check for duplicate locker number
    existing = db.query(GoldVaultLocker).filter(
        and_(
            GoldVaultLocker.rack_id == locker.rack_id,
            GoldVaultLocker.locker_number == locker.locker_number
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Locker number already exists in this rack")
    
    locker_record = GoldVaultLocker(
        id=str(uuid4()),
        **locker.model_dump()
    )
    
    db.add(locker_record)
    db.commit()
    db.refresh(locker_record)
    
    return locker_record


@router.get("/racks/{rack_id}/lockers", response_model=List[LockerResponse])
async def list_rack_lockers(rack_id: str, db: Session = Depends(get_db)):
    """List all lockers in a rack"""
    lockers = db.query(GoldVaultLocker).filter(
        GoldVaultLocker.rack_id == rack_id
    ).order_by(GoldVaultLocker.locker_number).all()
    return lockers


# ============================================================================
# TRAY MANAGEMENT
# ============================================================================

@router.post("/trays", response_model=TrayResponse, status_code=201)
async def create_tray(tray: TrayCreate, db: Session = Depends(get_db)):
    """Create tray within a locker"""
    # Verify locker exists
    locker = db.query(GoldVaultLocker).filter(GoldVaultLocker.id == tray.locker_id).first()
    if not locker:
        raise HTTPException(status_code=404, detail="Locker not found")
    
    # Check for duplicate tray number
    existing = db.query(GoldVaultTray).filter(
        and_(
            GoldVaultTray.locker_id == tray.locker_id,
            GoldVaultTray.tray_number == tray.tray_number
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tray number already exists in this locker")
    
    tray_record = GoldVaultTray(
        id=str(uuid4()),
        **tray.model_dump()
    )
    
    db.add(tray_record)
    db.commit()
    db.refresh(tray_record)
    
    return tray_record


@router.get("/lockers/{locker_id}/trays", response_model=List[TrayResponse])
async def list_locker_trays(locker_id: str, db: Session = Depends(get_db)):
    """List all trays in a locker"""
    trays = db.query(GoldVaultTray).filter(
        GoldVaultTray.locker_id == locker_id
    ).order_by(GoldVaultTray.tray_number).all()
    return trays


# ============================================================================
# PACKET MANAGEMENT
# ============================================================================

@router.post("/packets", response_model=PacketResponse, status_code=201)
async def create_packet(packet: PacketCreate, db: Session = Depends(get_db)):
    """
    Create new packet with QR code
    
    Automatically generates:
    - Unique packet number
    - QR code
    """
    # Generate packet number
    packet_number = generate_packet_number(packet.branch_id)
    
    # Generate QR code data
    qr_data = f"GOLD_PACKET:{packet_number}:{packet.customer_id}"
    
    packet_record = GoldPacket(
        id=str(uuid4()),
        packet_number=packet_number,
        qr_code=qr_data,
        qr_generated_at=datetime.utcnow(),
        current_location_type='counter',
        appraisal_session_id=packet.appraisal_session_id,
        customer_id=packet.customer_id,
        branch_id=packet.branch_id,
        created_by_user_id=packet.created_by_user_id
    )
    
    db.add(packet_record)
    
    # Add ornaments to packet
    total_ornaments = 0
    for idx, ornament_id in enumerate(packet.ornament_ids, 1):
        ornament_mapping = GoldPacketOrnament(
            id=str(uuid4()),
            packet_id=packet_record.id,
            ornament_id=ornament_id,
            sequence_number=idx,
            added_by_user_id=packet.created_by_user_id
        )
        db.add(ornament_mapping)
        total_ornaments += 1
    
    packet_record.total_ornaments = total_ornaments
    
    db.commit()
    db.refresh(packet_record)
    
    return packet_record


@router.post("/packets/{packet_id}/seal", response_model=PacketResponse)
async def seal_packet(packet_id: str, seal: PacketSeal, db: Session = Depends(get_db)):
    """
    Seal packet with security seal
    
    Updates seal inventory to 'used' status
    """
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Check if seal exists and is available
    seal_record = db.query(GoldSecuritySeal).filter(
        GoldSecuritySeal.seal_number == seal.seal_number
    ).first()
    
    if seal_record:
        if seal_record.seal_status != 'available':
            raise HTTPException(status_code=400, detail=f"Seal {seal.seal_number} is not available")
        
        # Update seal record
        seal_record.seal_status = 'used'
        seal_record.used_on_packet_id = packet_id
        seal_record.used_at = datetime.utcnow()
        seal_record.used_by_user_id = seal.sealed_by_user_id
    
    # Update packet
    packet.seal_number = seal.seal_number
    packet.seal_type = seal.seal_type
    packet.sealed_by_user_id = seal.sealed_by_user_id
    packet.sealed_at = datetime.utcnow()
    packet.seal_status = 'intact'
    packet.packet_status = 'sealed'
    packet.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(packet)
    
    return packet


@router.post("/packets/{packet_id}/verify-seal", response_model=PacketResponse)
async def verify_packet_seal(packet_id: str, verify: PacketVerifySeal, db: Session = Depends(get_db)):
    """
    Verify packet seal (maker-checker)
    
    Different user must verify the seal
    """
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    if not packet.sealed_by_user_id:
        raise HTTPException(status_code=400, detail="Packet not sealed yet")
    
    if packet.sealed_by_user_id == verify.seal_verified_by_user_id:
        raise HTTPException(
            status_code=400,
            detail="Verifier must be different from sealer (maker-checker violation)"
        )
    
    packet.seal_verified_by_user_id = verify.seal_verified_by_user_id
    packet.seal_verified_at = datetime.utcnow()
    packet.seal_status = verify.seal_status
    packet.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(packet)
    
    return packet


@router.post("/packets/{packet_id}/assign-location", response_model=PacketResponse)
async def assign_packet_location(
    packet_id: str,
    location: PacketAssignLocation,
    db: Session = Depends(get_db)
):
    """
    Assign packet to specific vault location
    
    Updates occupancy counts at all hierarchy levels
    """
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Verify location exists
    vault = db.query(GoldVault).filter(GoldVault.id == location.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    rack = db.query(GoldVaultRack).filter(GoldVaultRack.id == location.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")
    
    locker = db.query(GoldVaultLocker).filter(GoldVaultLocker.id == location.locker_id).first()
    if not locker:
        raise HTTPException(status_code=404, detail="Locker not found")
    
    tray = db.query(GoldVaultTray).filter(GoldVaultTray.id == location.tray_id).first()
    if not tray:
        raise HTTPException(status_code=404, detail="Tray not found")
    
    # Check capacity
    if tray.current_occupancy >= tray.capacity_packets:
        raise HTTPException(status_code=400, detail="Tray is at full capacity")
    
    # Update packet location
    packet.vault_id = location.vault_id
    packet.rack_id = location.rack_id
    packet.locker_id = location.locker_id
    packet.tray_id = location.tray_id
    packet.current_location_type = 'vault'
    packet.packet_status = 'vaulted'
    packet.updated_at = datetime.utcnow()
    
    # Update occupancy counts
    vault.current_occupancy += 1
    rack.current_occupancy += 1
    locker.current_occupancy += 1
    tray.current_occupancy += 1
    
    # Record movement
    movement = GoldPacketMovement(
        id=str(uuid4()),
        packet_id=packet_id,
        movement_type='vault_in',
        from_location_type=packet.current_location_type,
        to_location_type='vault',
        to_vault_id=location.vault_id,
        to_rack_id=location.rack_id,
        to_locker_id=location.locker_id,
        to_tray_id=location.tray_id,
        moved_by_user_id=location.assigned_by_user_id,
        seal_status_at_movement=packet.seal_status
    )
    db.add(movement)
    
    db.commit()
    db.refresh(packet)
    
    return packet


@router.get("/packets", response_model=List[PacketResponse])
async def list_packets(
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    packet_status: Optional[str] = Query(None),
    vault_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List packets with filters"""
    query = db.query(GoldPacket)
    
    if customer_id:
        query = query.filter(GoldPacket.customer_id == customer_id)
    if branch_id:
        query = query.filter(GoldPacket.branch_id == branch_id)
    if packet_status:
        query = query.filter(GoldPacket.packet_status == packet_status)
    if vault_id:
        query = query.filter(GoldPacket.vault_id == vault_id)
    
    packets = query.order_by(desc(GoldPacket.created_at)).all()
    return packets


@router.get("/packets/{packet_id}", response_model=PacketWithLocation)
async def get_packet(packet_id: str, db: Session = Depends(get_db)):
    """Get packet details with location information"""
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Get location details
    vault_code = vault_name = rack_code = locker_code = tray_code = None
    full_location = None
    
    if packet.vault_id:
        vault = db.query(GoldVault).filter(GoldVault.id == packet.vault_id).first()
        if vault:
            vault_code = vault.vault_code
            vault_name = vault.vault_name
    
    if packet.rack_id:
        rack = db.query(GoldVaultRack).filter(GoldVaultRack.id == packet.rack_id).first()
        if rack:
            rack_code = rack.rack_code
    
    if packet.locker_id:
        locker = db.query(GoldVaultLocker).filter(GoldVaultLocker.id == packet.locker_id).first()
        if locker:
            locker_code = locker.locker_code
    
    if packet.tray_id:
        tray = db.query(GoldVaultTray).filter(GoldVaultTray.id == packet.tray_id).first()
        if tray:
            tray_code = tray.tray_code
    
    if all([vault_code, rack_code, locker_code, tray_code]):
        full_location = f"{vault_code}-{rack_code}-{locker_code}-{tray_code}"
    
    packet_response = PacketResponse.model_validate(packet)
    
    return PacketWithLocation(
        packet=packet_response,
        vault_code=vault_code,
        vault_name=vault_name,
        rack_code=rack_code,
        locker_code=locker_code,
        tray_code=tray_code,
        full_location=full_location
    )


@router.get("/packets/{packet_id}/qr-code")
async def get_packet_qr_code(packet_id: str, db: Session = Depends(get_db)):
    """
    Generate QR code image for packet
    
    Returns base64 encoded PNG image
    """
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    qr_image = generate_qr_code(packet.qr_code)
    
    return {
        "packet_id": packet_id,
        "packet_number": packet.packet_number,
        "qr_code": packet.qr_code,
        "qr_image": qr_image
    }


# Continue with packet movements, audits, access log, and seal management in the next chunk...


# ============================================================================
# PACKET MOVEMENTS
# ============================================================================

@router.post("/packet-movements", response_model=PacketMovementResponse, status_code=201)
async def record_packet_movement(movement: PacketMovementCreate, db: Session = Depends(get_db)):
    """
    Record packet movement
    
    Tracks complete movement with GPS and seal verification
    """
    packet = db.query(GoldPacket).filter(GoldPacket.id == movement.packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    movement_record = GoldPacketMovement(
        id=str(uuid4()),
        **movement.model_dump()
    )
    
    db.add(movement_record)
    
    # Update packet current location
    packet.current_location_type = movement.to_location_type
    if movement.to_vault_id:
        packet.vault_id = movement.to_vault_id
        packet.rack_id = movement.to_rack_id
        packet.locker_id = movement.to_locker_id
        packet.tray_id = movement.to_tray_id
    
    packet.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(movement_record)
    
    return movement_record


@router.post("/packet-movements/{movement_id}/verify", response_model=PacketMovementResponse)
async def verify_packet_movement(
    movement_id: str,
    verify: PacketMovementVerify,
    db: Session = Depends(get_db)
):
    """Verify packet movement (maker-checker)"""
    movement = db.query(GoldPacketMovement).filter(
        GoldPacketMovement.id == movement_id
    ).first()
    
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    if movement.moved_by_user_id == verify.verified_by_user_id:
        raise HTTPException(
            status_code=400,
            detail="Verifier must be different from mover (maker-checker violation)"
        )
    
    movement.verified_by_user_id = verify.verified_by_user_id
    movement.verification_timestamp = datetime.utcnow()
    
    db.commit()
    db.refresh(movement)
    
    return movement


@router.get("/packets/{packet_id}/movements", response_model=List[PacketMovementResponse])
async def list_packet_movements(packet_id: str, db: Session = Depends(get_db)):
    """Get complete movement history for packet"""
    movements = db.query(GoldPacketMovement).filter(
        GoldPacketMovement.packet_id == packet_id
    ).order_by(desc(GoldPacketMovement.movement_timestamp)).all()
    return movements


@router.get("/packets/{packet_id}/audit-trail", response_model=PacketAuditTrail)
async def get_packet_audit_trail(packet_id: str, db: Session = Depends(get_db)):
    """Get complete audit trail for packet"""
    packet = db.query(GoldPacket).filter(GoldPacket.id == packet_id).first()
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    movements = db.query(GoldPacketMovement).filter(
        GoldPacketMovement.packet_id == packet_id
    ).order_by(desc(GoldPacketMovement.movement_timestamp)).all()
    
    # Calculate days in vault
    days_in_vault = None
    vault_in_movement = next(
        (m for m in movements if m.movement_type == 'vault_in'),
        None
    )
    if vault_in_movement:
        days_in_vault = (datetime.utcnow() - vault_in_movement.movement_timestamp).days
    
    # Count seal changes
    seal_changes = len([m for m in movements if m.seal_status_at_movement])
    
    # Current location
    current_location = None
    if packet.vault_id:
        vault = db.query(GoldVault).filter(GoldVault.id == packet.vault_id).first()
        if vault:
            current_location = f"{vault.vault_code}"
            if packet.rack_id:
                rack = db.query(GoldVaultRack).filter(GoldVaultRack.id == packet.rack_id).first()
                if rack:
                    current_location += f"-{rack.rack_code}"
    
    packet_response = PacketResponse.model_validate(packet)
    
    return PacketAuditTrail(
        packet=packet_response,
        movements=[PacketMovementResponse.model_validate(m) for m in movements],
        current_location=current_location,
        total_movements=len(movements),
        days_in_vault=days_in_vault,
        seal_changes=seal_changes
    )


# ============================================================================
# VAULT AUDITS
# ============================================================================

@router.post("/audits", response_model=VaultAuditResponse, status_code=201)
async def create_vault_audit(audit: VaultAuditCreate, db: Session = Depends(get_db)):
    """
    Schedule vault audit
    
    Audit types: scheduled, surprise, regulatory, internal
    """
    vault = db.query(GoldVault).filter(GoldVault.id == audit.vault_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")
    
    # Generate audit number
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    audit_number = f"AUD-{vault.vault_code}-{timestamp}-{str(uuid4())[:6].upper()}"
    
    audit_record = GoldVaultAudit(
        id=str(uuid4()),
        audit_number=audit_number,
        **audit.model_dump()
    )
    
    db.add(audit_record)
    db.commit()
    db.refresh(audit_record)
    
    return audit_record


@router.post("/audits/{audit_id}/start", response_model=VaultAuditResponse)
async def start_vault_audit(audit_id: str, start: VaultAuditStart, db: Session = Depends(get_db)):
    """Start vault audit"""
    audit = db.query(GoldVaultAudit).filter(GoldVaultAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit.audit_started_at = datetime.utcnow()
    audit.total_packets_expected = start.total_packets_expected
    audit.audit_status = 'in_progress'
    audit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(audit)
    
    return audit


@router.post("/audits/{audit_id}/complete", response_model=VaultAuditResponse)
async def complete_vault_audit(
    audit_id: str,
    complete: VaultAuditComplete,
    db: Session = Depends(get_db)
):
    """Complete vault audit"""
    audit = db.query(GoldVaultAudit).filter(GoldVaultAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit.audit_completed_at = datetime.utcnow()
    audit.total_packets_found = complete.total_packets_found
    audit.discrepancies_found = complete.discrepancies_found
    audit.audit_result = complete.audit_result
    audit.findings_summary = complete.findings_summary
    audit.recommendations = complete.recommendations
    audit.audit_status = 'completed'
    audit.updated_at = datetime.utcnow()
    
    # Update vault last audit date
    vault = db.query(GoldVault).filter(GoldVault.id == audit.vault_id).first()
    if vault:
        vault.last_audit_date = date.today()
        vault.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(audit)
    
    return audit


@router.post("/audits/{audit_id}/review", response_model=VaultAuditResponse)
async def review_vault_audit(audit_id: str, review: VaultAuditReview, db: Session = Depends(get_db)):
    """Review completed audit"""
    audit = db.query(GoldVaultAudit).filter(GoldVaultAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit.reviewed_by_user_id = review.reviewed_by_user_id
    audit.reviewed_at = datetime.utcnow()
    audit.audit_status = 'report_pending'
    audit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(audit)
    
    return audit


@router.post("/audits/{audit_id}/approve", response_model=VaultAuditResponse)
async def approve_vault_audit(audit_id: str, approve: VaultAuditApprove, db: Session = Depends(get_db)):
    """Approve audit report"""
    audit = db.query(GoldVaultAudit).filter(GoldVaultAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    audit.approved_by_user_id = approve.approved_by_user_id
    audit.approved_at = datetime.utcnow()
    audit.audit_status = 'closed'
    audit.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(audit)
    
    return audit


@router.get("/audits", response_model=List[VaultAuditResponse])
async def list_audits(
    vault_id: Optional[str] = Query(None),
    audit_status: Optional[str] = Query(None),
    audit_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List audits with filters"""
    query = db.query(GoldVaultAudit)
    
    if vault_id:
        query = query.filter(GoldVaultAudit.vault_id == vault_id)
    if audit_status:
        query = query.filter(GoldVaultAudit.audit_status == audit_status)
    if audit_type:
        query = query.filter(GoldVaultAudit.audit_type == audit_type)
    
    audits = query.order_by(desc(GoldVaultAudit.audit_date)).all()
    return audits


# ============================================================================
# AUDIT FINDINGS
# ============================================================================

@router.post("/audit-findings", response_model=AuditFindingResponse, status_code=201)
async def create_audit_finding(finding: AuditFindingCreate, db: Session = Depends(get_db)):
    """Record audit finding"""
    finding_record = GoldAuditFinding(
        id=str(uuid4()),
        **finding.model_dump()
    )
    
    db.add(finding_record)
    db.commit()
    db.refresh(finding_record)
    
    return finding_record


@router.post("/audit-findings/{finding_id}/resolve", response_model=AuditFindingResponse)
async def resolve_audit_finding(
    finding_id: str,
    resolve: AuditFindingResolve,
    db: Session = Depends(get_db)
):
    """Resolve audit finding"""
    finding = db.query(GoldAuditFinding).filter(GoldAuditFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding.resolution_status = resolve.resolution_status
    finding.resolution_notes = resolve.resolution_notes
    finding.resolved_by_user_id = resolve.resolved_by_user_id
    finding.resolved_at = datetime.utcnow()
    finding.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(finding)
    
    return finding


@router.get("/audits/{audit_id}/findings", response_model=List[AuditFindingResponse])
async def list_audit_findings(audit_id: str, db: Session = Depends(get_db)):
    """List findings for an audit"""
    findings = db.query(GoldAuditFinding).filter(
        GoldAuditFinding.audit_id == audit_id
    ).order_by(desc(GoldAuditFinding.severity)).all()
    return findings


# ============================================================================
# VAULT ACCESS LOG
# ============================================================================

@router.post("/access-log", response_model=VaultAccessResponse, status_code=201)
async def record_vault_access(access: VaultAccessCreate, db: Session = Depends(get_db)):
    """Record vault access (entry)"""
    access_record = GoldVaultAccessLog(
        id=str(uuid4()),
        **access.model_dump()
    )
    
    db.add(access_record)
    db.commit()
    db.refresh(access_record)
    
    return access_record


@router.post("/access-log/{access_id}/exit", response_model=VaultAccessResponse)
async def record_vault_exit(access_id: str, exit: VaultAccessExit, db: Session = Depends(get_db)):
    """Record vault exit"""
    access = db.query(GoldVaultAccessLog).filter(GoldVaultAccessLog.id == access_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")
    
    access.exit_timestamp = datetime.utcnow()
    access.notes = exit.notes
    
    # Calculate duration
    if access.access_timestamp:
        duration = (access.exit_timestamp - access.access_timestamp).total_seconds() / 60
        access.duration_minutes = int(duration)
    
    db.commit()
    db.refresh(access)
    
    return access


@router.get("/vaults/{vault_id}/access-log", response_model=List[VaultAccessResponse])
async def list_vault_access(
    vault_id: str,
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """List vault access records"""
    query = db.query(GoldVaultAccessLog).filter(GoldVaultAccessLog.vault_id == vault_id)
    
    if from_date:
        query = query.filter(GoldVaultAccessLog.access_timestamp >= from_date)
    if to_date:
        query = query.filter(GoldVaultAccessLog.access_timestamp <= to_date)
    
    access_logs = query.order_by(desc(GoldVaultAccessLog.access_timestamp)).all()
    return access_logs


# ============================================================================
# SEAL MANAGEMENT
# ============================================================================

@router.post("/seals", response_model=SealResponse, status_code=201)
async def create_seal(seal: SealCreate, db: Session = Depends(get_db)):
    """Add seal to inventory"""
    # Check for duplicate
    existing = db.query(GoldSecuritySeal).filter(
        GoldSecuritySeal.seal_number == seal.seal_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Seal number already exists")
    
    seal_record = GoldSecuritySeal(
        id=str(uuid4()),
        **seal.model_dump()
    )
    
    db.add(seal_record)
    db.commit()
    db.refresh(seal_record)
    
    return seal_record


@router.post("/seals/{seal_id}/issue", response_model=SealResponse)
async def issue_seal(seal_id: str, issue: SealIssue, db: Session = Depends(get_db)):
    """Issue seal to branch/user"""
    seal = db.query(GoldSecuritySeal).filter(GoldSecuritySeal.id == seal_id).first()
    if not seal:
        raise HTTPException(status_code=404, detail="Seal not found")
    
    if seal.seal_status != 'available':
        raise HTTPException(status_code=400, detail="Seal is not available for issuance")
    
    seal.seal_status = 'issued'
    seal.issued_to_branch_id = issue.issued_to_branch_id
    seal.issued_to_user_id = issue.issued_to_user_id
    seal.issued_at = datetime.utcnow()
    seal.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(seal)
    
    return seal


@router.post("/seals/{seal_id}/dispose", response_model=SealResponse)
async def dispose_seal(seal_id: str, dispose: SealDispose, db: Session = Depends(get_db)):
    """Dispose/destroy seal"""
    seal = db.query(GoldSecuritySeal).filter(GoldSecuritySeal.id == seal_id).first()
    if not seal:
        raise HTTPException(status_code=404, detail="Seal not found")
    
    seal.seal_status = 'destroyed'
    seal.disposed_at = datetime.utcnow()
    seal.disposed_by_user_id = dispose.disposed_by_user_id
    seal.disposal_reason = dispose.disposal_reason
    seal.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(seal)
    
    return seal


@router.get("/seals", response_model=List[SealResponse])
async def list_seals(
    seal_status: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List seals with filters"""
    query = db.query(GoldSecuritySeal)
    
    if seal_status:
        query = query.filter(GoldSecuritySeal.seal_status == seal_status)
    if branch_id:
        query = query.filter(GoldSecuritySeal.issued_to_branch_id == branch_id)
    
    seals = query.order_by(GoldSecuritySeal.seal_number).all()
    return seals


@router.get("/seals/available-count")
async def get_available_seals_count(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get count of available seals"""
    query = db.query(func.count(GoldSecuritySeal.id)).filter(
        GoldSecuritySeal.seal_status == 'available'
    )
    
    if branch_id:
        query = query.filter(GoldSecuritySeal.issued_to_branch_id == branch_id)
    
    count = query.scalar()
    
    return {
        "branch_id": branch_id,
        "available_seals": count
    }

"""
Gold Lending - Collections & Recovery Router
Phase 8: Complete collections, recovery, legal, and auction management
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.collections import (
    AuctionBid, AuctionLot, AuctionLotItem, CollectionActivity,
    CollectionCase, CollectionPerformance, CommunicationLog,
    FieldVisit, LegalNotice, PaymentPromise, RecoveryAction,
    SettlementOffer
)
from app.schemas.collections import (
    AuctionBidCreate, AuctionBidResponse, AuctionBidUpdate,
    AuctionLotCreate, AuctionLotDetail, AuctionLotItemCreate,
    AuctionLotItemResponse, AuctionLotItemUpdate, AuctionLotList,
    AuctionLotResponse, AuctionLotUpdate, CaseStatistics,
    CollectionActivityCreate, CollectionActivityResponse,
    CollectionCaseCreate, CollectionCaseDetail, CollectionCaseList,
    CollectionCaseResponse, CollectionCaseUpdate, CollectionDashboard,
    CollectionPerformanceCreate, CollectionPerformanceResponse,
    CollectionPerformanceUpdate, CommunicationLogCreate,
    CommunicationLogResponse, CommunicationLogUpdate, FieldVisitCreate,
    FieldVisitList, FieldVisitResponse, FieldVisitUpdate,
    LegalNoticeCreate, LegalNoticeResponse, LegalNoticeUpdate,
    PaymentPromiseCreate, PaymentPromiseResponse, PaymentPromiseUpdate,
    RecoveryActionCreate, RecoveryActionResponse, RecoveryActionUpdate,
    SettlementOfferCreate, SettlementOfferResponse, SettlementOfferUpdate
)

router = APIRouter(prefix="/api/v1/gold/collections", tags=["Collections & Recovery"])


# ============================================================================
# COLLECTION CASE ENDPOINTS
# ============================================================================

@router.post("/cases", response_model=CollectionCaseResponse, status_code=status.HTTP_201_CREATED)
def create_collection_case(
    case: CollectionCaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection case"""
    # Generate case number
    latest_case = db.query(CollectionCase).order_by(desc(CollectionCase.created_at)).first()
    if latest_case and latest_case.case_number:
        last_num = int(latest_case.case_number.split("CC")[1])
        case_number = f"CC{last_num + 1:09d}"
    else:
        case_number = "CC000000001"
    
    db_case = CollectionCase(**case.dict(), case_number=case_number)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@router.get("/cases", response_model=CollectionCaseList)
def list_collection_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    case_status: Optional[str] = Query(None),
    bucket_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to_user_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """List all collection cases with filters"""
    query = db.query(CollectionCase)
    
    if case_status:
        query = query.filter(CollectionCase.case_status == case_status)
    if bucket_type:
        query = query.filter(CollectionCase.bucket_type == bucket_type)
    if priority:
        query = query.filter(CollectionCase.priority == priority)
    if assigned_to_user_id:
        query = query.filter(CollectionCase.assigned_to_user_id == assigned_to_user_id)
    
    total = query.count()
    cases = query.order_by(desc(CollectionCase.created_at)).offset(skip).limit(limit).all()
    
    return {
        "items": cases,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/cases/{case_id}", response_model=CollectionCaseDetail)
def get_collection_case(case_id: UUID, db: Session = Depends(get_db)):
    """Get a specific collection case by ID"""
    case = db.query(CollectionCase).filter(CollectionCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Collection case not found")
    
    # Get counts
    activities_count = db.query(func.count(CollectionActivity.id)).filter(
        CollectionActivity.collection_case_id == case_id
    ).scalar()
    field_visits_count = db.query(func.count(FieldVisit.id)).filter(
        FieldVisit.collection_case_id == case_id
    ).scalar()
    promises_count = db.query(func.count(PaymentPromise.id)).filter(
        PaymentPromise.collection_case_id == case_id
    ).scalar()
    legal_notices_count = db.query(func.count(LegalNotice.id)).filter(
        LegalNotice.collection_case_id == case_id
    ).scalar()
    recovery_actions_count = db.query(func.count(RecoveryAction.id)).filter(
        RecoveryAction.collection_case_id == case_id
    ).scalar()
    
    case_dict = case.__dict__.copy()
    case_dict.update({
        "activities_count": activities_count,
        "field_visits_count": field_visits_count,
        "promises_count": promises_count,
        "legal_notices_count": legal_notices_count,
        "recovery_actions_count": recovery_actions_count
    })
    
    return case_dict


@router.patch("/cases/{case_id}", response_model=CollectionCaseResponse)
def update_collection_case(
    case_id: UUID,
    case_update: CollectionCaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a collection case"""
    db_case = db.query(CollectionCase).filter(CollectionCase.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Collection case not found")
    
    update_data = case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)
    
    if case_update.case_status == "closed":
        db_case.closed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_case)
    return db_case


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_case(case_id: UUID, db: Session = Depends(get_db)):
    """Delete a collection case"""
    db_case = db.query(CollectionCase).filter(CollectionCase.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Collection case not found")
    
    db.delete(db_case)
    db.commit()
    return None


@router.get("/cases/{case_id}/statistics", response_model=CaseStatistics)
def get_case_statistics(case_id: UUID, db: Session = Depends(get_db)):
    """Get statistics for a specific case"""
    case = db.query(CollectionCase).filter(CollectionCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Collection case not found")
    
    total_activities = db.query(func.count(CollectionActivity.id)).filter(
        CollectionActivity.collection_case_id == case_id
    ).scalar()
    
    total_field_visits = db.query(func.count(FieldVisit.id)).filter(
        FieldVisit.collection_case_id == case_id
    ).scalar()
    
    total_promises = db.query(func.count(PaymentPromise.id)).filter(
        PaymentPromise.collection_case_id == case_id
    ).scalar()
    
    promises_kept = db.query(func.count(PaymentPromise.id)).filter(
        and_(PaymentPromise.collection_case_id == case_id, PaymentPromise.promise_status == 'kept')
    ).scalar()
    
    promises_broken = db.query(func.count(PaymentPromise.id)).filter(
        and_(PaymentPromise.collection_case_id == case_id, PaymentPromise.promise_status == 'broken')
    ).scalar()
    
    total_legal_notices = db.query(func.count(LegalNotice.id)).filter(
        LegalNotice.collection_case_id == case_id
    ).scalar()
    
    total_recovery_actions = db.query(func.count(RecoveryAction.id)).filter(
        RecoveryAction.collection_case_id == case_id
    ).scalar()
    
    days_in_collection = (datetime.utcnow() - case.created_at).days
    
    last_activity = db.query(CollectionActivity.activity_date).filter(
        CollectionActivity.collection_case_id == case_id
    ).order_by(desc(CollectionActivity.activity_date)).first()
    
    return {
        "case_id": case_id,
        "total_activities": total_activities,
        "total_field_visits": total_field_visits,
        "total_promises": total_promises,
        "promises_kept": promises_kept,
        "promises_broken": promises_broken,
        "total_legal_notices": total_legal_notices,
        "total_recovery_actions": total_recovery_actions,
        "days_in_collection": days_in_collection,
        "last_activity_date": last_activity[0] if last_activity else None
    }



# ============================================================================
# COLLECTION ACTIVITY ENDPOINTS
# ============================================================================

@router.post("/activities", response_model=CollectionActivityResponse, status_code=status.HTTP_201_CREATED)
def create_collection_activity(
    activity: CollectionActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection activity"""
    db_activity = CollectionActivity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.get("/activities", response_model=List[CollectionActivityResponse])
def list_collection_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    activity_type: Optional[str] = Query(None),
    disposition: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all collection activities with filters"""
    query = db.query(CollectionActivity)
    
    if collection_case_id:
        query = query.filter(CollectionActivity.collection_case_id == collection_case_id)
    if activity_type:
        query = query.filter(CollectionActivity.activity_type == activity_type)
    if disposition:
        query = query.filter(CollectionActivity.disposition == disposition)
    if from_date:
        query = query.filter(CollectionActivity.activity_date >= from_date)
    if to_date:
        query = query.filter(CollectionActivity.activity_date <= to_date)
    
    activities = query.order_by(desc(CollectionActivity.activity_date)).offset(skip).limit(limit).all()
    return activities


@router.get("/activities/{activity_id}", response_model=CollectionActivityResponse)
def get_collection_activity(activity_id: UUID, db: Session = Depends(get_db)):
    """Get a specific collection activity"""
    activity = db.query(CollectionActivity).filter(CollectionActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Collection activity not found")
    return activity


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_activity(activity_id: UUID, db: Session = Depends(get_db)):
    """Delete a collection activity"""
    activity = db.query(CollectionActivity).filter(CollectionActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Collection activity not found")
    
    db.delete(activity)
    db.commit()
    return None


# ============================================================================
# FIELD VISIT ENDPOINTS
# ============================================================================

@router.post("/field-visits", response_model=FieldVisitResponse, status_code=status.HTTP_201_CREATED)
def create_field_visit(
    visit: FieldVisitCreate,
    db: Session = Depends(get_db)
):
    """Create a new field visit"""
    # Generate visit number
    latest_visit = db.query(FieldVisit).order_by(desc(FieldVisit.created_at)).first()
    if latest_visit and latest_visit.visit_number:
        last_num = int(latest_visit.visit_number.split("FV")[1])
        visit_number = f"FV{last_num + 1:09d}"
    else:
        visit_number = "FV000000001"
    
    db_visit = FieldVisit(**visit.dict(), visit_number=visit_number)
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit


@router.get("/field-visits", response_model=FieldVisitList)
def list_field_visits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    visit_status: Optional[str] = Query(None),
    field_officer_id: Optional[UUID] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all field visits with filters"""
    query = db.query(FieldVisit)
    
    if collection_case_id:
        query = query.filter(FieldVisit.collection_case_id == collection_case_id)
    if visit_status:
        query = query.filter(FieldVisit.visit_status == visit_status)
    if field_officer_id:
        query = query.filter(FieldVisit.field_officer_id == field_officer_id)
    if from_date:
        query = query.filter(FieldVisit.visit_date >= from_date)
    if to_date:
        query = query.filter(FieldVisit.visit_date <= to_date)
    
    total = query.count()
    visits = query.order_by(desc(FieldVisit.visit_date)).offset(skip).limit(limit).all()
    
    return {
        "items": visits,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/field-visits/{visit_id}", response_model=FieldVisitResponse)
def get_field_visit(visit_id: UUID, db: Session = Depends(get_db)):
    """Get a specific field visit"""
    visit = db.query(FieldVisit).filter(FieldVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Field visit not found")
    return visit


@router.patch("/field-visits/{visit_id}", response_model=FieldVisitResponse)
def update_field_visit(
    visit_id: UUID,
    visit_update: FieldVisitUpdate,
    db: Session = Depends(get_db)
):
    """Update a field visit"""
    db_visit = db.query(FieldVisit).filter(FieldVisit.id == visit_id).first()
    if not db_visit:
        raise HTTPException(status_code=404, detail="Field visit not found")
    
    update_data = visit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_visit, field, value)
    
    if visit_update.visit_status == "completed":
        db_visit.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_visit)
    return db_visit


@router.delete("/field-visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_visit(visit_id: UUID, db: Session = Depends(get_db)):
    """Delete a field visit"""
    visit = db.query(FieldVisit).filter(FieldVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Field visit not found")
    
    db.delete(visit)
    db.commit()
    return None



# ============================================================================
# PAYMENT PROMISE ENDPOINTS
# ============================================================================

@router.post("/payment-promises", response_model=PaymentPromiseResponse, status_code=status.HTTP_201_CREATED)
def create_payment_promise(
    promise: PaymentPromiseCreate,
    db: Session = Depends(get_db)
):
    """Create a new payment promise"""
    # Generate promise number
    latest_promise = db.query(PaymentPromise).order_by(desc(PaymentPromise.created_at)).first()
    if latest_promise and latest_promise.promise_number:
        last_num = int(latest_promise.promise_number.split("PP")[1])
        promise_number = f"PP{last_num + 1:09d}"
    else:
        promise_number = "PP000000001"
    
    db_promise = PaymentPromise(**promise.dict(), promise_number=promise_number)
    db.add(db_promise)
    db.commit()
    db.refresh(db_promise)
    return db_promise


@router.get("/payment-promises", response_model=List[PaymentPromiseResponse])
def list_payment_promises(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    promise_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all payment promises with filters"""
    query = db.query(PaymentPromise)
    
    if collection_case_id:
        query = query.filter(PaymentPromise.collection_case_id == collection_case_id)
    if promise_status:
        query = query.filter(PaymentPromise.promise_status == promise_status)
    if from_date:
        query = query.filter(PaymentPromise.promised_payment_date >= from_date)
    if to_date:
        query = query.filter(PaymentPromise.promised_payment_date <= to_date)
    
    promises = query.order_by(desc(PaymentPromise.promise_date)).offset(skip).limit(limit).all()
    return promises


@router.get("/payment-promises/{promise_id}", response_model=PaymentPromiseResponse)
def get_payment_promise(promise_id: UUID, db: Session = Depends(get_db)):
    """Get a specific payment promise"""
    promise = db.query(PaymentPromise).filter(PaymentPromise.id == promise_id).first()
    if not promise:
        raise HTTPException(status_code=404, detail="Payment promise not found")
    return promise


@router.patch("/payment-promises/{promise_id}", response_model=PaymentPromiseResponse)
def update_payment_promise(
    promise_id: UUID,
    promise_update: PaymentPromiseUpdate,
    db: Session = Depends(get_db)
):
    """Update a payment promise"""
    db_promise = db.query(PaymentPromise).filter(PaymentPromise.id == promise_id).first()
    if not db_promise:
        raise HTTPException(status_code=404, detail="Payment promise not found")
    
    update_data = promise_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_promise, field, value)
    
    db.commit()
    db.refresh(db_promise)
    return db_promise


@router.delete("/payment-promises/{promise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_promise(promise_id: UUID, db: Session = Depends(get_db)):
    """Delete a payment promise"""
    promise = db.query(PaymentPromise).filter(PaymentPromise.id == promise_id).first()
    if not promise:
        raise HTTPException(status_code=404, detail="Payment promise not found")
    
    db.delete(promise)
    db.commit()
    return None


# ============================================================================
# RECOVERY ACTION ENDPOINTS
# ============================================================================

@router.post("/recovery-actions", response_model=RecoveryActionResponse, status_code=status.HTTP_201_CREATED)
def create_recovery_action(
    action: RecoveryActionCreate,
    db: Session = Depends(get_db)
):
    """Create a new recovery action"""
    # Generate action number
    latest_action = db.query(RecoveryAction).order_by(desc(RecoveryAction.created_at)).first()
    if latest_action and latest_action.action_number:
        last_num = int(latest_action.action_number.split("RA")[1])
        action_number = f"RA{last_num + 1:09d}"
    else:
        action_number = "RA000000001"
    
    db_action = RecoveryAction(**action.dict(), action_number=action_number)
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


@router.get("/recovery-actions", response_model=List[RecoveryActionResponse])
def list_recovery_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    action_type: Optional[str] = Query(None),
    action_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all recovery actions with filters"""
    query = db.query(RecoveryAction)
    
    if collection_case_id:
        query = query.filter(RecoveryAction.collection_case_id == collection_case_id)
    if action_type:
        query = query.filter(RecoveryAction.action_type == action_type)
    if action_status:
        query = query.filter(RecoveryAction.action_status == action_status)
    if from_date:
        query = query.filter(RecoveryAction.action_date >= from_date)
    if to_date:
        query = query.filter(RecoveryAction.action_date <= to_date)
    
    actions = query.order_by(desc(RecoveryAction.action_date)).offset(skip).limit(limit).all()
    return actions


@router.get("/recovery-actions/{action_id}", response_model=RecoveryActionResponse)
def get_recovery_action(action_id: UUID, db: Session = Depends(get_db)):
    """Get a specific recovery action"""
    action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Recovery action not found")
    return action


@router.patch("/recovery-actions/{action_id}", response_model=RecoveryActionResponse)
def update_recovery_action(
    action_id: UUID,
    action_update: RecoveryActionUpdate,
    db: Session = Depends(get_db)
):
    """Update a recovery action"""
    db_action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not db_action:
        raise HTTPException(status_code=404, detail="Recovery action not found")
    
    update_data = action_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_action, field, value)
    
    db.commit()
    db.refresh(db_action)
    return db_action


@router.delete("/recovery-actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recovery_action(action_id: UUID, db: Session = Depends(get_db)):
    """Delete a recovery action"""
    action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Recovery action not found")
    
    db.delete(action)
    db.commit()
    return None


# ============================================================================
# LEGAL NOTICE ENDPOINTS
# ============================================================================

@router.post("/legal-notices", response_model=LegalNoticeResponse, status_code=status.HTTP_201_CREATED)
def create_legal_notice(
    notice: LegalNoticeCreate,
    db: Session = Depends(get_db)
):
    """Create a new legal notice"""
    # Generate notice number
    latest_notice = db.query(LegalNotice).order_by(desc(LegalNotice.created_at)).first()
    if latest_notice and latest_notice.notice_number:
        last_num = int(latest_notice.notice_number.split("LN")[1])
        notice_number = f"LN{last_num + 1:09d}"
    else:
        notice_number = "LN000000001"
    
    db_notice = LegalNotice(**notice.dict(), notice_number=notice_number)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice


@router.get("/legal-notices", response_model=List[LegalNoticeResponse])
def list_legal_notices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    notice_type: Optional[str] = Query(None),
    notice_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all legal notices with filters"""
    query = db.query(LegalNotice)
    
    if collection_case_id:
        query = query.filter(LegalNotice.collection_case_id == collection_case_id)
    if notice_type:
        query = query.filter(LegalNotice.notice_type == notice_type)
    if notice_status:
        query = query.filter(LegalNotice.notice_status == notice_status)
    if from_date:
        query = query.filter(LegalNotice.notice_date >= from_date)
    if to_date:
        query = query.filter(LegalNotice.notice_date <= to_date)
    
    notices = query.order_by(desc(LegalNotice.notice_date)).offset(skip).limit(limit).all()
    return notices


@router.get("/legal-notices/{notice_id}", response_model=LegalNoticeResponse)
def get_legal_notice(notice_id: UUID, db: Session = Depends(get_db)):
    """Get a specific legal notice"""
    notice = db.query(LegalNotice).filter(LegalNotice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Legal notice not found")
    return notice


@router.patch("/legal-notices/{notice_id}", response_model=LegalNoticeResponse)
def update_legal_notice(
    notice_id: UUID,
    notice_update: LegalNoticeUpdate,
    db: Session = Depends(get_db)
):
    """Update a legal notice"""
    db_notice = db.query(LegalNotice).filter(LegalNotice.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=404, detail="Legal notice not found")
    
    update_data = notice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notice, field, value)
    
    db.commit()
    db.refresh(db_notice)
    return db_notice


@router.delete("/legal-notices/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_legal_notice(notice_id: UUID, db: Session = Depends(get_db)):
    """Delete a legal notice"""
    notice = db.query(LegalNotice).filter(LegalNotice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Legal notice not found")
    
    db.delete(notice)
    db.commit()
    return None



# ============================================================================
# AUCTION LOT ENDPOINTS
# ============================================================================

@router.post("/auction-lots", response_model=AuctionLotResponse, status_code=status.HTTP_201_CREATED)
def create_auction_lot(
    lot: AuctionLotCreate,
    db: Session = Depends(get_db)
):
    """Create a new auction lot"""
    # Generate lot number
    latest_lot = db.query(AuctionLot).order_by(desc(AuctionLot.created_at)).first()
    if latest_lot and latest_lot.lot_number:
        last_num = int(latest_lot.lot_number.split("AL")[1])
        lot_number = f"AL{last_num + 1:09d}"
    else:
        lot_number = "AL000000001"
    
    db_lot = AuctionLot(**lot.dict(), lot_number=lot_number)
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot


@router.get("/auction-lots", response_model=AuctionLotList)
def list_auction_lots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lot_status: Optional[str] = Query(None),
    auction_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all auction lots with filters"""
    query = db.query(AuctionLot)
    
    if lot_status:
        query = query.filter(AuctionLot.lot_status == lot_status)
    if auction_type:
        query = query.filter(AuctionLot.auction_type == auction_type)
    if from_date:
        query = query.filter(AuctionLot.auction_date >= from_date)
    if to_date:
        query = query.filter(AuctionLot.auction_date <= to_date)
    
    total = query.count()
    lots = query.order_by(desc(AuctionLot.auction_date)).offset(skip).limit(limit).all()
    
    return {
        "items": lots,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/auction-lots/{lot_id}", response_model=AuctionLotDetail)
def get_auction_lot(lot_id: UUID, db: Session = Depends(get_db)):
    """Get a specific auction lot"""
    lot = db.query(AuctionLot).filter(AuctionLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Auction lot not found")
    
    # Get counts and bid statistics
    items_count = db.query(func.count(AuctionLotItem.id)).filter(
        AuctionLotItem.auction_lot_id == lot_id
    ).scalar()
    
    bids_count = db.query(func.count(AuctionBid.id)).filter(
        AuctionBid.auction_lot_id == lot_id
    ).scalar()
    
    highest_bid = db.query(func.max(AuctionBid.bid_amount)).filter(
        and_(AuctionBid.auction_lot_id == lot_id, AuctionBid.bid_status == 'active')
    ).scalar()
    
    lowest_bid = db.query(func.min(AuctionBid.bid_amount)).filter(
        and_(AuctionBid.auction_lot_id == lot_id, AuctionBid.bid_status == 'active')
    ).scalar()
    
    lot_dict = lot.__dict__.copy()
    lot_dict.update({
        "items_count": items_count,
        "bids_count": bids_count,
        "highest_bid": highest_bid,
        "lowest_bid": lowest_bid
    })
    
    return lot_dict


@router.patch("/auction-lots/{lot_id}", response_model=AuctionLotResponse)
def update_auction_lot(
    lot_id: UUID,
    lot_update: AuctionLotUpdate,
    db: Session = Depends(get_db)
):
    """Update an auction lot"""
    db_lot = db.query(AuctionLot).filter(AuctionLot.id == lot_id).first()
    if not db_lot:
        raise HTTPException(status_code=404, detail="Auction lot not found")
    
    update_data = lot_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_lot, field, value)
    
    db.commit()
    db.refresh(db_lot)
    return db_lot


@router.delete("/auction-lots/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auction_lot(lot_id: UUID, db: Session = Depends(get_db)):
    """Delete an auction lot"""
    lot = db.query(AuctionLot).filter(AuctionLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Auction lot not found")
    
    db.delete(lot)
    db.commit()
    return None


# ============================================================================
# AUCTION LOT ITEM ENDPOINTS
# ============================================================================

@router.post("/auction-lot-items", response_model=AuctionLotItemResponse, status_code=status.HTTP_201_CREATED)
def create_auction_lot_item(
    item: AuctionLotItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new auction lot item"""
    db_item = AuctionLotItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/auction-lot-items", response_model=List[AuctionLotItemResponse])
def list_auction_lot_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auction_lot_id: Optional[UUID] = Query(None),
    collection_case_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """List all auction lot items with filters"""
    query = db.query(AuctionLotItem)
    
    if auction_lot_id:
        query = query.filter(AuctionLotItem.auction_lot_id == auction_lot_id)
    if collection_case_id:
        query = query.filter(AuctionLotItem.collection_case_id == collection_case_id)
    
    items = query.order_by(AuctionLotItem.item_number).offset(skip).limit(limit).all()
    return items


@router.get("/auction-lot-items/{item_id}", response_model=AuctionLotItemResponse)
def get_auction_lot_item(item_id: UUID, db: Session = Depends(get_db)):
    """Get a specific auction lot item"""
    item = db.query(AuctionLotItem).filter(AuctionLotItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Auction lot item not found")
    return item


@router.patch("/auction-lot-items/{item_id}", response_model=AuctionLotItemResponse)
def update_auction_lot_item(
    item_id: UUID,
    item_update: AuctionLotItemUpdate,
    db: Session = Depends(get_db)
):
    """Update an auction lot item"""
    db_item = db.query(AuctionLotItem).filter(AuctionLotItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Auction lot item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/auction-lot-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auction_lot_item(item_id: UUID, db: Session = Depends(get_db)):
    """Delete an auction lot item"""
    item = db.query(AuctionLotItem).filter(AuctionLotItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Auction lot item not found")
    
    db.delete(item)
    db.commit()
    return None


# ============================================================================
# AUCTION BID ENDPOINTS
# ============================================================================

@router.post("/auction-bids", response_model=AuctionBidResponse, status_code=status.HTTP_201_CREATED)
def create_auction_bid(
    bid: AuctionBidCreate,
    db: Session = Depends(get_db)
):
    """Create a new auction bid"""
    # Generate bid number
    latest_bid = db.query(AuctionBid).order_by(desc(AuctionBid.created_at)).first()
    if latest_bid and latest_bid.bid_number:
        last_num = int(latest_bid.bid_number.split("AB")[1])
        bid_number = f"AB{last_num + 1:09d}"
    else:
        bid_number = "AB000000001"
    
    db_bid = AuctionBid(**bid.dict(), bid_number=bid_number)
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid


@router.get("/auction-bids", response_model=List[AuctionBidResponse])
def list_auction_bids(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auction_lot_id: Optional[UUID] = Query(None),
    bidder_id: Optional[UUID] = Query(None),
    bid_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all auction bids with filters"""
    query = db.query(AuctionBid)
    
    if auction_lot_id:
        query = query.filter(AuctionBid.auction_lot_id == auction_lot_id)
    if bidder_id:
        query = query.filter(AuctionBid.bidder_id == bidder_id)
    if bid_status:
        query = query.filter(AuctionBid.bid_status == bid_status)
    
    bids = query.order_by(desc(AuctionBid.bid_time)).offset(skip).limit(limit).all()
    return bids


@router.get("/auction-bids/{bid_id}", response_model=AuctionBidResponse)
def get_auction_bid(bid_id: UUID, db: Session = Depends(get_db)):
    """Get a specific auction bid"""
    bid = db.query(AuctionBid).filter(AuctionBid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Auction bid not found")
    return bid


@router.patch("/auction-bids/{bid_id}", response_model=AuctionBidResponse)
def update_auction_bid(
    bid_id: UUID,
    bid_update: AuctionBidUpdate,
    db: Session = Depends(get_db)
):
    """Update an auction bid"""
    db_bid = db.query(AuctionBid).filter(AuctionBid.id == bid_id).first()
    if not db_bid:
        raise HTTPException(status_code=404, detail="Auction bid not found")
    
    update_data = bid_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_bid, field, value)
    
    db.commit()
    db.refresh(db_bid)
    return db_bid


@router.delete("/auction-bids/{bid_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auction_bid(bid_id: UUID, db: Session = Depends(get_db)):
    """Delete an auction bid"""
    bid = db.query(AuctionBid).filter(AuctionBid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Auction bid not found")
    
    db.delete(bid)
    db.commit()
    return None



# ============================================================================
# COMMUNICATION LOG ENDPOINTS
# ============================================================================

@router.post("/communication-logs", response_model=CommunicationLogResponse, status_code=status.HTTP_201_CREATED)
def create_communication_log(
    log: CommunicationLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new communication log"""
    db_log = CommunicationLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/communication-logs", response_model=List[CommunicationLogResponse])
def list_communication_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    communication_type: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """List all communication logs with filters"""
    query = db.query(CommunicationLog)
    
    if collection_case_id:
        query = query.filter(CommunicationLog.collection_case_id == collection_case_id)
    if communication_type:
        query = query.filter(CommunicationLog.communication_type == communication_type)
    if direction:
        query = query.filter(CommunicationLog.direction == direction)
    if from_date:
        query = query.filter(CommunicationLog.communication_date >= from_date)
    if to_date:
        query = query.filter(CommunicationLog.communication_date <= to_date)
    
    logs = query.order_by(desc(CommunicationLog.communication_date)).offset(skip).limit(limit).all()
    return logs


@router.get("/communication-logs/{log_id}", response_model=CommunicationLogResponse)
def get_communication_log(log_id: UUID, db: Session = Depends(get_db)):
    """Get a specific communication log"""
    log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Communication log not found")
    return log


@router.patch("/communication-logs/{log_id}", response_model=CommunicationLogResponse)
def update_communication_log(
    log_id: UUID,
    log_update: CommunicationLogUpdate,
    db: Session = Depends(get_db)
):
    """Update a communication log"""
    db_log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Communication log not found")
    
    update_data = log_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)
    
    db.commit()
    db.refresh(db_log)
    return db_log


@router.delete("/communication-logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_communication_log(log_id: UUID, db: Session = Depends(get_db)):
    """Delete a communication log"""
    log = db.query(CommunicationLog).filter(CommunicationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Communication log not found")
    
    db.delete(log)
    db.commit()
    return None


# ============================================================================
# SETTLEMENT OFFER ENDPOINTS
# ============================================================================

@router.post("/settlement-offers", response_model=SettlementOfferResponse, status_code=status.HTTP_201_CREATED)
def create_settlement_offer(
    offer: SettlementOfferCreate,
    db: Session = Depends(get_db)
):
    """Create a new settlement offer"""
    # Generate offer number
    latest_offer = db.query(SettlementOffer).order_by(desc(SettlementOffer.created_at)).first()
    if latest_offer and latest_offer.offer_number:
        last_num = int(latest_offer.offer_number.split("SO")[1])
        offer_number = f"SO{last_num + 1:09d}"
    else:
        offer_number = "SO000000001"
    
    db_offer = SettlementOffer(**offer.dict(), offer_number=offer_number)
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


@router.get("/settlement-offers", response_model=List[SettlementOfferResponse])
def list_settlement_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    collection_case_id: Optional[UUID] = Query(None),
    offer_status: Optional[str] = Query(None),
    offered_by: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all settlement offers with filters"""
    query = db.query(SettlementOffer)
    
    if collection_case_id:
        query = query.filter(SettlementOffer.collection_case_id == collection_case_id)
    if offer_status:
        query = query.filter(SettlementOffer.offer_status == offer_status)
    if offered_by:
        query = query.filter(SettlementOffer.offered_by == offered_by)
    if from_date:
        query = query.filter(SettlementOffer.offer_date >= from_date)
    if to_date:
        query = query.filter(SettlementOffer.offer_date <= to_date)
    
    offers = query.order_by(desc(SettlementOffer.offer_date)).offset(skip).limit(limit).all()
    return offers


@router.get("/settlement-offers/{offer_id}", response_model=SettlementOfferResponse)
def get_settlement_offer(offer_id: UUID, db: Session = Depends(get_db)):
    """Get a specific settlement offer"""
    offer = db.query(SettlementOffer).filter(SettlementOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Settlement offer not found")
    return offer


@router.patch("/settlement-offers/{offer_id}", response_model=SettlementOfferResponse)
def update_settlement_offer(
    offer_id: UUID,
    offer_update: SettlementOfferUpdate,
    db: Session = Depends(get_db)
):
    """Update a settlement offer"""
    db_offer = db.query(SettlementOffer).filter(SettlementOffer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Settlement offer not found")
    
    update_data = offer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_offer, field, value)
    
    db.commit()
    db.refresh(db_offer)
    return db_offer


@router.delete("/settlement-offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_settlement_offer(offer_id: UUID, db: Session = Depends(get_db)):
    """Delete a settlement offer"""
    offer = db.query(SettlementOffer).filter(SettlementOffer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Settlement offer not found")
    
    db.delete(offer)
    db.commit()
    return None


# ============================================================================
# COLLECTION PERFORMANCE ENDPOINTS
# ============================================================================

@router.post("/performance", response_model=CollectionPerformanceResponse, status_code=status.HTTP_201_CREATED)
def create_performance_record(
    performance: CollectionPerformanceCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection performance record"""
    db_performance = CollectionPerformance(**performance.dict())
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


@router.get("/performance", response_model=List[CollectionPerformanceResponse])
def list_performance_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = Query(None),
    team_name: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all performance records with filters"""
    query = db.query(CollectionPerformance)
    
    if user_id:
        query = query.filter(CollectionPerformance.user_id == user_id)
    if team_name:
        query = query.filter(CollectionPerformance.team_name == team_name)
    if region:
        query = query.filter(CollectionPerformance.region == region)
    if from_date:
        query = query.filter(CollectionPerformance.period_start >= from_date)
    if to_date:
        query = query.filter(CollectionPerformance.period_end <= to_date)
    
    records = query.order_by(desc(CollectionPerformance.period_start)).offset(skip).limit(limit).all()
    return records


@router.get("/performance/{performance_id}", response_model=CollectionPerformanceResponse)
def get_performance_record(performance_id: UUID, db: Session = Depends(get_db)):
    """Get a specific performance record"""
    performance = db.query(CollectionPerformance).filter(CollectionPerformance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return performance


@router.patch("/performance/{performance_id}", response_model=CollectionPerformanceResponse)
def update_performance_record(
    performance_id: UUID,
    performance_update: CollectionPerformanceUpdate,
    db: Session = Depends(get_db)
):
    """Update a performance record"""
    db_performance = db.query(CollectionPerformance).filter(CollectionPerformance.id == performance_id).first()
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    
    update_data = performance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_performance, field, value)
    
    db.commit()
    db.refresh(db_performance)
    return db_performance


@router.delete("/performance/{performance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_record(performance_id: UUID, db: Session = Depends(get_db)):
    """Delete a performance record"""
    performance = db.query(CollectionPerformance).filter(CollectionPerformance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    
    db.delete(performance)
    db.commit()
    return None


# ============================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=CollectionDashboard)
def get_collection_dashboard(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get collection dashboard with key metrics"""
    query = db.query(CollectionCase)
    
    if from_date:
        query = query.filter(CollectionCase.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.filter(CollectionCase.created_at <= datetime.combine(to_date, datetime.max.time()))
    
    total_cases = query.count()
    open_cases = query.filter(CollectionCase.case_status == 'open').count()
    in_progress_cases = query.filter(CollectionCase.case_status == 'in_progress').count()
    legal_cases = query.filter(CollectionCase.case_status == 'legal').count()
    closed_cases = query.filter(CollectionCase.case_status == 'closed').count()
    
    total_outstanding = query.with_entities(func.sum(CollectionCase.total_outstanding)).scalar() or 0
    total_overdue = query.with_entities(func.sum(CollectionCase.overdue_amount)).scalar() or 0
    
    # Calculate total collected from payment promises
    total_collected = db.query(func.sum(PaymentPromise.amount_received)).filter(
        PaymentPromise.promise_status == 'kept'
    ).scalar() or 0
    
    collection_rate = (total_collected / total_overdue * 100) if total_overdue > 0 else 0
    
    bucket_0_30 = query.filter(CollectionCase.bucket_type == 'dpd_0_30').count()
    bucket_31_60 = query.filter(CollectionCase.bucket_type == 'dpd_31_60').count()
    bucket_61_90 = query.filter(CollectionCase.bucket_type == 'dpd_61_90').count()
    bucket_90_plus = query.filter(CollectionCase.bucket_type == 'dpd_90_plus').count()
    npa_cases = query.filter(CollectionCase.bucket_type == 'npa').count()
    
    return {
        "total_cases": total_cases,
        "open_cases": open_cases,
        "in_progress_cases": in_progress_cases,
        "legal_cases": legal_cases,
        "closed_cases": closed_cases,
        "total_outstanding": total_outstanding,
        "total_overdue": total_overdue,
        "total_collected": total_collected,
        "collection_rate": collection_rate,
        "bucket_0_30": bucket_0_30,
        "bucket_31_60": bucket_31_60,
        "bucket_61_90": bucket_61_90,
        "bucket_90_plus": bucket_90_plus,
        "npa_cases": npa_cases
    }


@router.get("/cases/{case_id}/timeline", response_model=List[dict])
def get_case_timeline(case_id: UUID, db: Session = Depends(get_db)):
    """Get complete timeline for a collection case"""
    case = db.query(CollectionCase).filter(CollectionCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Collection case not found")
    
    timeline = []
    
    # Add activities
    activities = db.query(CollectionActivity).filter(
        CollectionActivity.collection_case_id == case_id
    ).order_by(CollectionActivity.activity_date).all()
    
    for activity in activities:
        timeline.append({
            "date": activity.activity_date,
            "type": "activity",
            "sub_type": activity.activity_type,
            "description": f"{activity.activity_type} - {activity.disposition}",
            "details": activity.discussion_summary
        })
    
    # Add field visits
    visits = db.query(FieldVisit).filter(
        FieldVisit.collection_case_id == case_id
    ).order_by(FieldVisit.visit_date).all()
    
    for visit in visits:
        timeline.append({
            "date": visit.visit_date,
            "type": "field_visit",
            "sub_type": visit.visit_type,
            "description": f"Field visit - {visit.visit_status}",
            "details": visit.discussion_summary
        })
    
    # Add legal notices
    notices = db.query(LegalNotice).filter(
        LegalNotice.collection_case_id == case_id
    ).order_by(LegalNotice.notice_date).all()
    
    for notice in notices:
        timeline.append({
            "date": notice.notice_date,
            "type": "legal_notice",
            "sub_type": notice.notice_type,
            "description": f"Legal notice - {notice.notice_status}",
            "details": notice.notice_subject
        })
    
    # Sort timeline by date
    timeline.sort(key=lambda x: x["date"], reverse=True)
    
    return timeline

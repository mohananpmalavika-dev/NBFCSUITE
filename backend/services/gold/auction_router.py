"""
Auction Router
API endpoints for gold auction management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.gold.auction_service import AuctionService
from backend.services.gold.schemas import (
    GoldAuctionCreateRequest,
    GoldAuctionResponse,
    AuctionBidCreateRequest,
    AuctionBidResponse,
    AuctionNoticeCreateRequest,
    AuctionNoticeResponse
)

router = APIRouter(prefix="/auctions", tags=["Gold Auctions"])


# ==================== Auction Management Endpoints ====================

@router.post("/", response_model=GoldAuctionResponse)
async def create_auction(
    auction_data: GoldAuctionCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create auction for defaulted gold loan"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.create_auction(auction_data)
    return GoldAuctionResponse.from_orm(auction)


@router.put("/{auction_id}/schedule", response_model=GoldAuctionResponse)
async def schedule_auction(
    auction_id: str,
    auction_date: datetime = Query(...),
    auction_venue: str = Query(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Schedule or reschedule auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.schedule_auction(auction_id, auction_date, auction_venue)
    return GoldAuctionResponse.from_orm(auction)


@router.post("/{auction_id}/start", response_model=GoldAuctionResponse)
async def start_auction(
    auction_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Start auction process"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.start_auction(auction_id)
    return GoldAuctionResponse.from_orm(auction)


@router.post("/{auction_id}/complete", response_model=GoldAuctionResponse)
async def complete_auction(
    auction_id: str,
    winning_bid_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Complete auction with winning bid"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.complete_auction(auction_id, winning_bid_id)
    return GoldAuctionResponse.from_orm(auction)


@router.post("/{auction_id}/cancel", response_model=GoldAuctionResponse)
async def cancel_auction(
    auction_id: str,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Cancel scheduled auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.cancel_auction(auction_id, reason)
    return GoldAuctionResponse.from_orm(auction)


@router.post("/{auction_id}/mark-failed", response_model=GoldAuctionResponse)
async def mark_auction_failed(
    auction_id: str,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Mark auction as failed"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.mark_auction_failed(auction_id, reason)
    return GoldAuctionResponse.from_orm(auction)


@router.get("/{auction_id}", response_model=GoldAuctionResponse)
async def get_auction(
    auction_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get auction by ID"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auction = service.get_auction(auction_id)
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    return GoldAuctionResponse.from_orm(auction)


@router.get("/", response_model=List[GoldAuctionResponse])
async def list_auctions(
    loan_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List auctions with filters"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auctions = service.list_auctions(loan_id, customer_id, status, start_date, end_date)
    return [GoldAuctionResponse.from_orm(auction) for auction in auctions]


@router.get("/upcoming/scheduled", response_model=List[GoldAuctionResponse])
async def get_upcoming_auctions(
    days_ahead: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get auctions scheduled in next N days"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    auctions = service.get_upcoming_auctions(days_ahead)
    return [GoldAuctionResponse.from_orm(auction) for auction in auctions]


# ==================== Bidding Endpoints ====================

@router.post("/{auction_id}/register-bidder")
async def register_bidder(
    auction_id: str,
    bidder_name: str = Query(...),
    bidder_contact: str = Query(...),
    bidder_email: Optional[str] = Query(None),
    bidder_pan: Optional[str] = Query(None),
    bidder_address: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Register bidder for auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bidder_data = {
        "bidder_name": bidder_name,
        "bidder_contact": bidder_contact,
        "bidder_email": bidder_email,
        "bidder_pan": bidder_pan,
        "bidder_address": bidder_address
    }
    return service.register_bidder(auction_id, bidder_data)


@router.post("/bids", response_model=AuctionBidResponse)
async def submit_bid(
    bid_data: AuctionBidCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Submit bid for auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bid = service.submit_bid(bid_data)
    return AuctionBidResponse.from_orm(bid)


@router.put("/bids/{bid_id}", response_model=AuctionBidResponse)
async def update_bid(
    bid_id: str,
    new_amount: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update bid amount"""
    from decimal import Decimal
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bid = service.update_bid(bid_id, Decimal(str(new_amount)))
    return AuctionBidResponse.from_orm(bid)


@router.post("/bids/{bid_id}/withdraw", response_model=AuctionBidResponse)
async def withdraw_bid(
    bid_id: str,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Withdraw bid"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bid = service.withdraw_bid(bid_id, reason)
    return AuctionBidResponse.from_orm(bid)


@router.get("/{auction_id}/bids", response_model=List[AuctionBidResponse])
async def list_bids(
    auction_id: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List bids for an auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bids = service.list_bids(auction_id, status)
    return [AuctionBidResponse.from_orm(bid) for bid in bids]


@router.get("/{auction_id}/winning-bid", response_model=AuctionBidResponse)
async def get_winning_bid(
    auction_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get winning bid for auction"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    bid = service.get_winning_bid(auction_id)
    
    if not bid:
        raise HTTPException(status_code=404, detail="No winning bid found")
    
    return AuctionBidResponse.from_orm(bid)


# ==================== Notice Management Endpoints ====================

@router.post("/notices", response_model=AuctionNoticeResponse)
async def create_auction_notice(
    notice_data: AuctionNoticeCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create auction notice"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    notice = service.create_notice(notice_data)
    return AuctionNoticeResponse.from_orm(notice)


@router.post("/notices/{notice_id}/send", response_model=AuctionNoticeResponse)
async def send_auction_notice(
    notice_id: str,
    tracking_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Mark notice as sent"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    notice = service.send_notice(notice_id, tracking_number)
    return AuctionNoticeResponse.from_orm(notice)


@router.post("/notices/{notice_id}/delivered", response_model=AuctionNoticeResponse)
async def mark_notice_delivered(
    notice_id: str,
    proof_url: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Mark notice as delivered"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    notice = service.mark_notice_delivered(notice_id, proof_url)
    return AuctionNoticeResponse.from_orm(notice)


@router.post("/notices/{notice_id}/response", response_model=AuctionNoticeResponse)
async def record_notice_response(
    notice_id: str,
    response_type: str = Query(..., description="Payment Made, Extension Request, Dispute, No Response"),
    remarks: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Record customer response to notice"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    notice = service.record_notice_response(notice_id, response_type, remarks)
    return AuctionNoticeResponse.from_orm(notice)


@router.get("/notices", response_model=List[AuctionNoticeResponse])
async def list_auction_notices(
    auction_id: Optional[str] = Query(None),
    loan_id: Optional[str] = Query(None),
    notice_type: Optional[str] = Query(None),
    delivery_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List auction notices"""
    service = AuctionService(db, tenant_id, current_user.get("user_id"))
    notices = service.list_notices(auction_id, loan_id, notice_type, delivery_status)
    return [AuctionNoticeResponse.from_orm(notice) for notice in notices]

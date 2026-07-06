"""
Auction Service
Manages complete gold auction workflow for defaulted loans
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
import json
from fastapi import HTTPException

from backend.shared.database.gold_loan_models import (
    GoldAuction,
    AuctionBid,
    AuctionNotice,
    GoldLoanAccount,
    GoldOrnament,
    VaultInventory
)
from backend.services.gold.schemas import (
    GoldAuctionCreateRequest,
    AuctionBidCreateRequest,
    AuctionNoticeCreateRequest,
    GoldAuctionResponse,
    AuctionBidResponse
)


class AuctionService:
    """Service for auction management"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== Auction Management ====================
    
    def create_auction(
        self,
        auction_data: GoldAuctionCreateRequest
    ) -> GoldAuction:
        """
        Create auction for defaulted gold loan
        """
        # Validate loan
        loan = self.db.query(GoldLoanAccount).filter(
            and_(
                GoldLoanAccount.id == auction_data.gold_loan_id,
                GoldLoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan:
            raise HTTPException(status_code=404, detail="Gold loan not found")
        
        # Check if loan is eligible for auction (overdue/NPA)
        if loan.status not in ["Overdue", "NPA"]:
            raise HTTPException(
                status_code=400,
                detail=f"Loan is not eligible for auction (current status: {loan.status})"
            )
        
        # Check if auction already exists
        existing = self.db.query(GoldAuction).filter(
            and_(
                GoldAuction.gold_loan_id == auction_data.gold_loan_id,
                GoldAuction.tenant_id == self.tenant_id,
                GoldAuction.auction_status.in_(["Scheduled", "In Progress"])
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Active auction already exists: {existing.auction_number}"
            )
        
        # Calculate reserve price (90% of total gold value by default)
        reserve_price = loan.total_gold_value * Decimal("0.90")
        if auction_data.reserve_price:
            reserve_price = auction_data.reserve_price
        
        # Generate auction number
        auction_number = self._generate_auction_number()
        
        # Create auction
        auction = GoldAuction(
            tenant_id=self.tenant_id,
            auction_number=auction_number,
            gold_loan_id=auction_data.gold_loan_id,
            customer_id=loan.customer_id,
            total_gold_weight_grams=loan.total_gold_weight_grams,
            total_gold_value=loan.total_gold_value,
            outstanding_principal=loan.principal_outstanding,
            outstanding_interest=loan.interest_outstanding,
            outstanding_charges=loan.penal_interest_outstanding,
            total_outstanding=loan.total_outstanding,
            reserve_price=reserve_price,
            auction_date=auction_data.auction_date,
            auction_venue=auction_data.auction_venue,
            notice_period_days=auction_data.notice_period_days or 30,
            auction_status="Scheduled",
            remarks=auction_data.remarks
        )
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        # Auto-generate default notice
        self._create_default_notice(auction)
        
        return auction
    
    def schedule_auction(
        self,
        auction_id: str,
        auction_date: datetime,
        auction_venue: str
    ) -> GoldAuction:
        """
        Schedule or reschedule auction
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status not in ["Scheduled", "Cancelled"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reschedule auction (current status: {auction.auction_status})"
            )
        
        auction.auction_date = auction_date
        auction.auction_venue = auction_venue
        auction.auction_status = "Scheduled"
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        return auction
    
    def cancel_auction(
        self,
        auction_id: str,
        reason: str
    ) -> GoldAuction:
        """
        Cancel scheduled auction
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status not in ["Scheduled"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel auction (current status: {auction.auction_status})"
            )
        
        auction.auction_status = "Cancelled"
        auction.remarks = f"{auction.remarks or ''}\nCancelled: {reason}"
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        return auction
    
    def start_auction(self, auction_id: str) -> GoldAuction:
        """
        Start auction process
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status != "Scheduled":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start auction (current status: {auction.auction_status})"
            )
        
        # Verify notice period completed
        if auction.notice_sent_date:
            notice_completion = auction.notice_sent_date + timedelta(days=auction.notice_period_days)
            if datetime.utcnow() < notice_completion:
                raise HTTPException(
                    status_code=400,
                    detail=f"Notice period not completed. Auction can start after {notice_completion}"
                )
        
        auction.auction_status = "In Progress"
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        return auction
    
    def complete_auction(
        self,
        auction_id: str,
        winning_bid_id: Optional[str] = None
    ) -> GoldAuction:
        """
        Complete auction with winning bid
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status != "In Progress":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete auction (current status: {auction.auction_status})"
            )
        
        if winning_bid_id:
            # Get winning bid
            winning_bid = self.db.query(AuctionBid).filter(
                and_(
                    AuctionBid.id == winning_bid_id,
                    AuctionBid.auction_id == auction_id,
                    AuctionBid.tenant_id == self.tenant_id
                )
            ).first()
            
            if not winning_bid:
                raise HTTPException(status_code=404, detail="Winning bid not found")
            
            # Update auction with winner details
            auction.highest_bid_amount = winning_bid.bid_amount
            auction.winning_bidder_name = winning_bid.bidder_name
            auction.winning_bidder_contact = winning_bid.bidder_contact
            auction.sale_amount = winning_bid.bid_amount
            auction.sale_date = datetime.utcnow()
            
            # Calculate refund if sale > outstanding
            if auction.sale_amount > auction.total_outstanding:
                auction.refund_amount = auction.sale_amount - auction.total_outstanding
                auction.refund_status = "Pending"
            
            # Mark bid as winner
            winning_bid.is_winning_bid = True
            winning_bid.won_date = datetime.utcnow()
            winning_bid.bid_status = "Winner"
            self.db.add(winning_bid)
            
            # Mark other bids as outbid
            self._mark_other_bids_as_outbid(auction_id, winning_bid_id)
        
        auction.auction_status = "Completed"
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        # Update loan status
        self._update_loan_after_auction(auction)
        
        return auction
    
    def mark_auction_failed(
        self,
        auction_id: str,
        reason: str
    ) -> GoldAuction:
        """
        Mark auction as failed (no bids or below reserve)
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status not in ["In Progress", "Scheduled"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot mark as failed (current status: {auction.auction_status})"
            )
        
        auction.auction_status = "Failed"
        auction.remarks = f"{auction.remarks or ''}\nFailed: {reason}"
        
        self.db.add(auction)
        self.db.commit()
        self.db.refresh(auction)
        
        return auction
    
    def get_auction(self, auction_id: str) -> Optional[GoldAuction]:
        """Get auction by ID"""
        return self._get_auction(auction_id)
    
    def list_auctions(
        self,
        loan_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[GoldAuction]:
        """List auctions with filters"""
        query = self.db.query(GoldAuction).filter(
            GoldAuction.tenant_id == self.tenant_id
        )
        
        if loan_id:
            query = query.filter(GoldAuction.gold_loan_id == loan_id)
        if customer_id:
            query = query.filter(GoldAuction.customer_id == customer_id)
        if status:
            query = query.filter(GoldAuction.auction_status == status)
        if start_date:
            query = query.filter(GoldAuction.auction_date >= start_date)
        if end_date:
            query = query.filter(GoldAuction.auction_date <= end_date)
        
        return query.order_by(desc(GoldAuction.auction_date)).all()
    
    def get_upcoming_auctions(self, days_ahead: int = 30) -> List[GoldAuction]:
        """Get auctions scheduled in next N days"""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return self.db.query(GoldAuction).filter(
            and_(
                GoldAuction.tenant_id == self.tenant_id,
                GoldAuction.auction_status == "Scheduled",
                GoldAuction.auction_date <= future_date,
                GoldAuction.auction_date >= datetime.utcnow()
            )
        ).order_by(GoldAuction.auction_date).all()
    
    # ==================== Bidding Management ====================
    
    def register_bidder(
        self,
        auction_id: str,
        bidder_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register bidder for auction
        """
        auction = self._get_auction(auction_id)
        
        if auction.auction_status not in ["Scheduled", "In Progress"]:
            raise HTTPException(
                status_code=400,
                detail="Auction is not open for registration"
            )
        
        # Generate registration number
        registration_number = self._generate_bidder_registration_number(auction_id)
        
        return {
            "auction_id": auction_id,
            "auction_number": auction.auction_number,
            "registration_number": registration_number,
            "bidder_name": bidder_data["bidder_name"],
            "registration_date": datetime.utcnow(),
            "deposit_required": float(auction.reserve_price * Decimal("0.10")),  # 10% EMD
            "auction_date": auction.auction_date
        }
    
    def submit_bid(
        self,
        bid_data: AuctionBidCreateRequest
    ) -> AuctionBid:
        """
        Submit bid for auction
        """
        auction = self._get_auction(bid_data.auction_id)
        
        if auction.auction_status != "In Progress":
            raise HTTPException(
                status_code=400,
                detail=f"Auction is not accepting bids (current status: {auction.auction_status})"
            )
        
        # Validate bid amount
        if bid_data.bid_amount < auction.reserve_price:
            raise HTTPException(
                status_code=400,
                detail=f"Bid amount must be at least reserve price: ₹{auction.reserve_price}"
            )
        
        # Generate bid number
        bid_number = self._generate_bid_number(auction.auction_number)
        
        # Create bid
        bid = AuctionBid(
            tenant_id=self.tenant_id,
            bid_number=bid_number,
            auction_id=bid_data.auction_id,
            bid_date=datetime.utcnow(),
            bidder_name=bid_data.bidder_name,
            bidder_contact=bid_data.bidder_contact,
            bidder_email=bid_data.bidder_email,
            bidder_pan=bid_data.bidder_pan,
            bidder_address=bid_data.bidder_address,
            bidder_registration_number=bid_data.bidder_registration_number,
            deposit_amount=bid_data.deposit_amount,
            bid_amount=bid_data.bid_amount,
            bid_type=bid_data.bid_type or "Regular",
            bid_status="Submitted",
            remarks=bid_data.remarks
        )
        
        self.db.add(bid)
        
        # Update auction highest bid if this is higher
        if not auction.highest_bid_amount or bid_data.bid_amount > auction.highest_bid_amount:
            auction.highest_bid_amount = bid_data.bid_amount
            auction.winning_bidder_name = bid_data.bidder_name
            auction.winning_bidder_contact = bid_data.bidder_contact
            self.db.add(auction)
        
        self.db.commit()
        self.db.refresh(bid)
        
        # Rank bids
        self._update_bid_rankings(bid_data.auction_id)
        
        return bid
    
    def update_bid(
        self,
        bid_id: str,
        new_amount: Decimal
    ) -> AuctionBid:
        """
        Update bid amount (if allowed)
        """
        bid = self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.id == bid_id,
                AuctionBid.tenant_id == self.tenant_id
            )
        ).first()
        
        if not bid:
            raise HTTPException(status_code=404, detail="Bid not found")
        
        if bid.bid_status != "Submitted":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update bid (current status: {bid.bid_status})"
            )
        
        auction = self._get_auction(bid.auction_id)
        
        if new_amount < auction.reserve_price:
            raise HTTPException(
                status_code=400,
                detail=f"Bid amount must be at least reserve price: ₹{auction.reserve_price}"
            )
        
        bid.bid_amount = new_amount
        bid.remarks = f"{bid.remarks or ''}\nUpdated bid amount to ₹{new_amount}"
        
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        
        # Update rankings
        self._update_bid_rankings(bid.auction_id)
        
        return bid
    
    def withdraw_bid(
        self,
        bid_id: str,
        reason: str
    ) -> AuctionBid:
        """
        Withdraw bid
        """
        bid = self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.id == bid_id,
                AuctionBid.tenant_id == self.tenant_id
            )
        ).first()
        
        if not bid:
            raise HTTPException(status_code=404, detail="Bid not found")
        
        if bid.bid_status != "Submitted":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot withdraw bid (current status: {bid.bid_status})"
            )
        
        bid.bid_status = "Withdrawn"
        bid.remarks = f"{bid.remarks or ''}\nWithdrawn: {reason}"
        
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        
        return bid
    
    def list_bids(
        self,
        auction_id: str,
        status: Optional[str] = None
    ) -> List[AuctionBid]:
        """List bids for an auction"""
        query = self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.auction_id == auction_id,
                AuctionBid.tenant_id == self.tenant_id
            )
        )
        
        if status:
            query = query.filter(AuctionBid.bid_status == status)
        
        return query.order_by(desc(AuctionBid.bid_amount)).all()
    
    def get_winning_bid(self, auction_id: str) -> Optional[AuctionBid]:
        """Get winning bid for auction"""
        return self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.auction_id == auction_id,
                AuctionBid.tenant_id == self.tenant_id,
                AuctionBid.is_winning_bid == True
            )
        ).first()
    
    # ==================== Notice Management ====================
    
    def create_notice(
        self,
        notice_data: AuctionNoticeCreateRequest
    ) -> AuctionNotice:
        """
        Create auction notice
        """
        auction = self._get_auction(notice_data.auction_id)
        
        # Generate notice number
        notice_number = self._generate_notice_number(auction.auction_number)
        
        # Calculate response due date
        response_due = notice_data.notice_date + timedelta(days=notice_data.notice_period_days)
        
        notice = AuctionNotice(
            tenant_id=self.tenant_id,
            notice_number=notice_number,
            auction_id=notice_data.auction_id,
            gold_loan_id=auction.gold_loan_id,
            customer_id=auction.customer_id,
            notice_type=notice_data.notice_type,
            notice_date=notice_data.notice_date,
            notice_period_days=notice_data.notice_period_days,
            response_due_date=response_due,
            delivery_method=notice_data.delivery_method,
            delivery_address=notice_data.delivery_address,
            delivery_email=notice_data.delivery_email,
            delivery_phone=notice_data.delivery_phone,
            delivery_status="Pending",
            remarks=notice_data.remarks
        )
        
        self.db.add(notice)
        self.db.commit()
        self.db.refresh(notice)
        
        return notice
    
    def send_notice(
        self,
        notice_id: str,
        tracking_number: Optional[str] = None
    ) -> AuctionNotice:
        """
        Mark notice as sent
        """
        notice = self.db.query(AuctionNotice).filter(
            and_(
                AuctionNotice.id == notice_id,
                AuctionNotice.tenant_id == self.tenant_id
            )
        ).first()
        
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")
        
        notice.sent_date = datetime.utcnow()
        notice.tracking_number = tracking_number
        notice.delivery_status = "Sent"
        
        self.db.add(notice)
        
        # Update auction notice sent date
        auction = self._get_auction(notice.auction_id)
        if not auction.notice_sent_date:
            auction.notice_sent_date = datetime.utcnow()
            self.db.add(auction)
        
        self.db.commit()
        self.db.refresh(notice)
        
        return notice
    
    def mark_notice_delivered(
        self,
        notice_id: str,
        proof_url: Optional[str] = None
    ) -> AuctionNotice:
        """
        Mark notice as delivered
        """
        notice = self.db.query(AuctionNotice).filter(
            and_(
                AuctionNotice.id == notice_id,
                AuctionNotice.tenant_id == self.tenant_id
            )
        ).first()
        
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")
        
        notice.delivered_date = datetime.utcnow()
        notice.delivery_status = "Delivered"
        notice.proof_of_delivery_url = proof_url
        notice.legal_requirement_met = True
        notice.verified_by = self.user_id
        notice.verification_date = datetime.utcnow()
        
        self.db.add(notice)
        self.db.commit()
        self.db.refresh(notice)
        
        return notice
    
    def record_notice_response(
        self,
        notice_id: str,
        response_type: str,
        remarks: Optional[str] = None
    ) -> AuctionNotice:
        """
        Record customer response to notice
        """
        notice = self.db.query(AuctionNotice).filter(
            and_(
                AuctionNotice.id == notice_id,
                AuctionNotice.tenant_id == self.tenant_id
            )
        ).first()
        
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")
        
        notice.response_received = True
        notice.response_date = datetime.utcnow()
        notice.response_type = response_type
        
        if remarks:
            notice.remarks = f"{notice.remarks or ''}\nResponse: {remarks}"
        
        self.db.add(notice)
        self.db.commit()
        self.db.refresh(notice)
        
        return notice
    
    def list_notices(
        self,
        auction_id: Optional[str] = None,
        loan_id: Optional[str] = None,
        notice_type: Optional[str] = None,
        delivery_status: Optional[str] = None
    ) -> List[AuctionNotice]:
        """List auction notices"""
        query = self.db.query(AuctionNotice).filter(
            AuctionNotice.tenant_id == self.tenant_id
        )
        
        if auction_id:
            query = query.filter(AuctionNotice.auction_id == auction_id)
        if loan_id:
            query = query.filter(AuctionNotice.gold_loan_id == loan_id)
        if notice_type:
            query = query.filter(AuctionNotice.notice_type == notice_type)
        if delivery_status:
            query = query.filter(AuctionNotice.delivery_status == delivery_status)
        
        return query.order_by(desc(AuctionNotice.notice_date)).all()
    
    # ==================== Helper Methods ====================
    
    def _get_auction(self, auction_id: str) -> GoldAuction:
        """Get auction with error handling"""
        auction = self.db.query(GoldAuction).filter(
            and_(
                GoldAuction.id == auction_id,
                GoldAuction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")
        
        return auction
    
    def _create_default_notice(self, auction: GoldAuction) -> None:
        """Create default auction notice"""
        notice_number = self._generate_notice_number(auction.auction_number)
        notice_date = datetime.utcnow()
        response_due = notice_date + timedelta(days=auction.notice_period_days)
        
        notice = AuctionNotice(
            tenant_id=self.tenant_id,
            notice_number=notice_number,
            auction_id=auction.id,
            gold_loan_id=auction.gold_loan_id,
            customer_id=auction.customer_id,
            notice_type="Default Notice",
            notice_date=notice_date,
            notice_period_days=auction.notice_period_days,
            response_due_date=response_due,
            delivery_method="Registered Post",
            delivery_status="Pending",
            remarks="Auto-generated default notice"
        )
        
        self.db.add(notice)
    
    def _update_bid_rankings(self, auction_id: str) -> None:
        """Update bid rankings for auction"""
        bids = self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.auction_id == auction_id,
                AuctionBid.tenant_id == self.tenant_id,
                AuctionBid.bid_status == "Submitted"
            )
        ).order_by(desc(AuctionBid.bid_amount)).all()
        
        for rank, bid in enumerate(bids, 1):
            bid.bid_rank = rank
            self.db.add(bid)
    
    def _mark_other_bids_as_outbid(self, auction_id: str, winning_bid_id: str) -> None:
        """Mark all other bids as outbid"""
        bids = self.db.query(AuctionBid).filter(
            and_(
                AuctionBid.auction_id == auction_id,
                AuctionBid.tenant_id == self.tenant_id,
                AuctionBid.id != winning_bid_id,
                AuctionBid.bid_status == "Submitted"
            )
        ).all()
        
        for bid in bids:
            bid.bid_status = "Outbid"
            self.db.add(bid)
    
    def _update_loan_after_auction(self, auction: GoldAuction) -> None:
        """Update loan status after auction completion"""
        loan = self.db.query(GoldLoanAccount).filter(
            and_(
                GoldLoanAccount.id == auction.gold_loan_id,
                GoldLoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if loan:
            loan.status = "Auctioned"
            loan.closure_date = datetime.utcnow()
            loan.is_active = False
            self.db.add(loan)
    
    def _generate_auction_number(self) -> str:
        """Generate unique auction number"""
        count = self.db.query(func.count(GoldAuction.id)).filter(
            GoldAuction.tenant_id == self.tenant_id
        ).scalar()
        
        return f"AUC-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
    
    def _generate_bid_number(self, auction_number: str) -> str:
        """Generate unique bid number"""
        count = self.db.query(func.count(AuctionBid.id)).filter(
            and_(
                AuctionBid.tenant_id == self.tenant_id,
                AuctionBid.bid_number.like(f"BID-{auction_number}%")
            )
        ).scalar()
        
        return f"BID-{auction_number}-{count + 1:03d}"
    
    def _generate_notice_number(self, auction_number: str) -> str:
        """Generate unique notice number"""
        count = self.db.query(func.count(AuctionNotice.id)).filter(
            and_(
                AuctionNotice.tenant_id == self.tenant_id,
                AuctionNotice.notice_number.like(f"NOT-{auction_number}%")
            )
        ).scalar()
        
        return f"NOT-{auction_number}-{count + 1:03d}"
    
    def _generate_bidder_registration_number(self, auction_id: str) -> str:
        """Generate bidder registration number"""
        auction = self._get_auction(auction_id)
        count = self.db.query(func.count(AuctionBid.bidder_registration_number)).filter(
            and_(
                AuctionBid.auction_id == auction_id,
                AuctionBid.tenant_id == self.tenant_id
            )
        ).scalar()
        
        return f"REG-{auction.auction_number}-{count + 1:04d}"

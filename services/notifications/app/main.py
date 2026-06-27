from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import os
import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, JSON, String, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    sms = "sms"
    whatsapp = "whatsapp"
    email = "email"
    push = "push"
    voice_call = "voice_call"
    in_app = "in_app"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_notifications_tenant_idempotency"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    channel = Column(String, index=True, nullable=False)
    recipient = Column(String, nullable=True)
    recipient_type = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    template_code = Column(String, nullable=True)
    template_data = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    status = Column(String, default="pending", index=True)
    error_message = Column(String, nullable=True)
    source_event = Column(String, nullable=True, index=True)
    event_id = Column(String, nullable=True, index=True)
    idempotency_key = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationRequest(BaseModel):
    tenant_id: str
    channel: NotificationChannel
    recipient: Optional[str] = None
    recipient_type: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    template_code: Optional[str] = None
    template_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    event_id: Optional[str] = None
    source_event: Optional[str] = None
    idempotency_key: Optional[str] = None
    user_id: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    tenant_id: str
    channel: NotificationChannel
    recipient: Optional[str] = None
    recipient_type: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    template_code: Optional[str] = None
    template_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str
    error_message: Optional[str] = None
    source_event: Optional[str] = None
    event_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DomainEventPublish(BaseModel):
    tenant_id: str
    event_type: str
    source_service: str
    aggregate_type: str
    aggregate_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class NotificationDispatcher:
    def send(self, notification: Notification) -> Dict[str, Any]:
        channel = notification.channel
        handler = {
            NotificationChannel.sms.value: self.send_sms,
            NotificationChannel.whatsapp.value: self.send_whatsapp,
            NotificationChannel.email.value: self.send_email,
            NotificationChannel.push.value: self.send_push,
            NotificationChannel.voice_call.value: self.send_voice_call,
            NotificationChannel.in_app.value: self.send_in_app,
        }.get(channel)

        if not handler:
            raise ValueError(f"Unsupported notification channel: {channel}")

        return handler(notification)

    def send_sms(self, notification: Notification) -> Dict[str, Any]:
        if not notification.recipient:
            raise ValueError("SMS notifications require a recipient phone number")
        logger.info("Sending SMS to %s: %s", notification.recipient, notification.body or notification.template_code)
        return {"provider": "sms", "status": "queued"}

    def send_whatsapp(self, notification: Notification) -> Dict[str, Any]:
        if not notification.recipient:
            raise ValueError("WhatsApp notifications require a recipient phone number")
        logger.info("Sending WhatsApp message to %s: %s", notification.recipient, notification.body or notification.template_code)
        return {"provider": "whatsapp", "status": "queued"}

    def send_email(self, notification: Notification) -> Dict[str, Any]:
        if not notification.recipient:
            raise ValueError("Email notifications require a recipient email address")
        if not notification.subject and not notification.template_code:
            raise ValueError("Email notifications require a subject or template_code")
        logger.info("Sending email to %s: subject=%s", notification.recipient, notification.subject)
        return {"provider": "email", "status": "queued"}

    def send_push(self, notification: Notification) -> Dict[str, Any]:
        if not notification.recipient and not notification.user_id:
            raise ValueError("Push notifications require a recipient token or user_id")
        recipient = notification.recipient or notification.user_id
        logger.info("Sending push notification to %s: %s", recipient, notification.body or notification.subject)
        return {"provider": "push", "status": "queued"}

    def send_voice_call(self, notification: Notification) -> Dict[str, Any]:
        if not notification.recipient:
            raise ValueError("Voice call notifications require a phone number recipient")
        logger.info("Placing voice call to %s: %s", notification.recipient, notification.body or notification.template_code)
        return {"provider": "voice_call", "status": "queued"}

    def send_in_app(self, notification: Notification) -> Dict[str, Any]:
        recipient = notification.user_id or notification.recipient
        if not recipient:
            raise ValueError("In-app notifications require a user_id or recipient")
        logger.info("Creating in-app notification for %s: %s", recipient, notification.body or notification.subject)
        return {"provider": "in_app", "status": "created"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_notification_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        tenant_id=notification.tenant_id,
        channel=notification.channel,
        recipient=notification.recipient,
        recipient_type=notification.recipient_type,
        subject=notification.subject,
        body=notification.body,
        template_code=notification.template_code,
        template_data=notification.template_data or {},
        metadata=notification.metadata or {},
        status=notification.status,
        error_message=notification.error_message,
        source_event=notification.source_event,
        event_id=notification.event_id,
        idempotency_key=notification.idempotency_key,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
    )


def dispatch_notification(notification: Notification, db: Session) -> Notification:
    dispatcher = NotificationDispatcher()
    try:
        result = dispatcher.send(notification)
        notification.status = "sent"
        notification.metadata = {**(notification.metadata or {}), "dispatch_result": result}
    except Exception as exc:
        notification.status = "failed"
        notification.error_message = str(exc)
        notification.metadata = {**(notification.metadata or {}), "dispatch_error": str(exc)}

    notification.updated_at = datetime.utcnow()
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_notification(request: NotificationRequest, db: Session) -> Notification:
    if request.idempotency_key:
        existing = (
            db.query(Notification)
            .filter(Notification.tenant_id == request.tenant_id, Notification.idempotency_key == request.idempotency_key)
            .first()
        )
        if existing:
            return existing

    notification = Notification(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        channel=request.channel.value,
        recipient=request.recipient,
        recipient_type=request.recipient_type,
        subject=request.subject,
        body=request.body,
        template_code=request.template_code,
        template_data=request.template_data,
        metadata=request.metadata,
        source_event=request.source_event,
        event_id=request.event_id,
        idempotency_key=request.idempotency_key,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_and_dispatch(request: NotificationRequest, db: Session) -> NotificationResponse:
    notification = create_notification(request, db)
    if notification.status == "pending":
        notification = dispatch_notification(notification, db)
    return build_notification_response(notification)


def build_notifications_from_event(payload: DomainEventPublish) -> List[NotificationRequest]:
    requests: List[NotificationRequest] = []
    data = payload.payload or {}
    phone = data.get("customer_phone") or data.get("phone") or data.get("mobile")
    email = data.get("customer_email") or data.get("email")
    user_id = data.get("user_id") or data.get("customer_id")
    subject = f"Notification for {payload.event_type}"
    body = data.get("message") or f"Your {payload.event_type} event has been received for {payload.aggregate_id}."

    if payload.event_type == "application.submitted":
        if phone:
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.sms,
                    recipient=phone,
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-sms",
                )
            )
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.whatsapp,
                    recipient=phone,
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-whatsapp",
                )
            )
        if email:
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.email,
                    recipient=email,
                    subject=subject,
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-email",
                )
            )
        if user_id:
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.in_app,
                    recipient=user_id,
                    user_id=user_id,
                    subject=subject,
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-inapp",
                )
            )
    elif payload.event_type == "customer.onboarding.approved":
        if email:
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.email,
                    recipient=email,
                    subject="Your onboarding is approved",
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-email",
                )
            )
        if user_id:
            requests.append(
                NotificationRequest(
                    tenant_id=payload.tenant_id,
                    channel=NotificationChannel.in_app,
                    recipient=user_id,
                    user_id=user_id,
                    subject="Onboarding approved",
                    body=body,
                    source_event=payload.event_type,
                    event_id=payload.aggregate_id,
                    idempotency_key=f"{payload.idempotency_key or payload.aggregate_id}-inapp",
                )
            )

    return requests


app = FastAPI(title="notifications-service", version="0.1.0")


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"service": "notifications", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "notifications"}


@app.post("/notifications/send", response_model=NotificationResponse)
def send_notification(payload: NotificationRequest, db: Session = Depends(get_db)):
    notification = create_and_dispatch(payload, db)
    return notification


@app.post("/events", response_model=List[NotificationResponse])
def ingest_event(payload: DomainEventPublish, db: Session = Depends(get_db)):
    requests = build_notifications_from_event(payload)
    if not requests:
        return []

    responses: List[NotificationResponse] = []
    for request in requests:
        responses.append(create_and_dispatch(request, db))
    return responses


@app.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(
    tenant_id: str = Query(...),
    channel: Optional[NotificationChannel] = Query(None),
    status: Optional[str] = Query(None),
    recipient: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(Notification.tenant_id == tenant_id)
    if channel:
        query = query.filter(Notification.channel == channel.value)
    if status:
        query = query.filter(Notification.status == status)
    if recipient:
        query = query.filter(Notification.recipient == recipient)
    notifications = query.order_by(Notification.created_at.desc()).all()
    return [build_notification_response(item) for item in notifications]


@app.get("/notifications/in_app/{user_id}", response_model=List[NotificationResponse])
def list_in_app_notifications(user_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification)
        .filter(Notification.tenant_id == tenant_id)
        .filter(Notification.channel == NotificationChannel.in_app.value)
        .filter((Notification.recipient == user_id) | (Notification.event_id == user_id))
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [build_notification_response(item) for item in notifications]

"""
Notification & Communication Engine

Complete multi-channel notification system with TRAI DLT compliance,
event-driven triggers, and provider integration.

Features:
- Multi-channel support (SMS, Email, WhatsApp, Push)
- Template management with Jinja2 rendering
- TRAI DLT compliance for India SMS
- Event-driven notification triggers
- Provider management with failover
- Delivery tracking and analytics
- Scheduled and recurring notifications
"""

from backend.services.notification.router import router
from backend.services.notification.notification_service import NotificationService
from backend.services.notification.dlt_compliance_service import DLTComplianceService
from backend.services.notification.trigger_engine import TriggerEngine, EventTypes

__all__ = [
    "router",
    "NotificationService",
    "DLTComplianceService",
    "TriggerEngine",
    "EventTypes",
]

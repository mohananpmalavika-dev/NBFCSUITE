"""
Notifications Service

Automated Email/SMS notifications for property management:
- Rent due reminders
- Lease expiry alerts
- Payment confirmations
- Maintenance updates
"""

from .notification_service import get_notification_service, NotificationService
from .scheduler import start_notification_scheduler, stop_notification_scheduler
from .notification_router import router as notification_router

__all__ = [
    'get_notification_service',
    'NotificationService',
    'start_notification_scheduler',
    'stop_notification_scheduler',
    'notification_router'
]

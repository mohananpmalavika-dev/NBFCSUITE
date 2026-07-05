"""
Notification Service Module

Multi-channel notification system with template management and delivery tracking.

Services:
- Notification Service: Send and manage notifications
- Template Service: Template management with variables

Router:
- Notification Router: REST API endpoints for notifications and templates

Features:
- Multi-channel support (SMS, Email, WhatsApp)
- Template management with variable substitution
- Delivery tracking and retry mechanism
- Priority-based queuing
- Bulk notification support
- Complete audit trail
"""

from .notification_service import NotificationService
from .template_service import TemplateService
from .router import router

__all__ = [
    "NotificationService",
    "TemplateService",
    "router",
]


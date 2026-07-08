"""
Grievance & Complaint Management Module

This module handles:
- Multi-channel complaint intake (Email, Phone, Web, Branch, Social Media)
- SLA tracking and breach detection
- Escalation workflow with auto-escalation
- Ombudsman case management
- Resolution tracking and reporting
"""

from .models import (
    Complaint,
    ComplaintChannel,
    ComplaintEscalation,
    ComplaintSLA,
    OmbudsmanCase,
)

__all__ = [
    "Complaint",
    "ComplaintChannel",
    "ComplaintEscalation",
    "ComplaintSLA",
    "OmbudsmanCase",
]

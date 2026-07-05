"""Database module"""

from shared.database.connection import engine, Base, get_db, AsyncSessionLocal
from shared.database.models import BaseModel, Tenant, TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin
from shared.database.accounting_models import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger,
    TrialBalance, AccountingPeriod
)

__all__ = [
    "engine",
    "Base",
    "get_db",
    "AsyncSessionLocal",
    "BaseModel",
    "Tenant",
    "TenantMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    # Accounting models
    "ChartOfAccounts",
    "JournalEntry",
    "JournalEntryLine",
    "GeneralLedger",
    "TrialBalance",
    "AccountingPeriod"
]

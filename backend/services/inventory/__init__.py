"""
Inventory & Store Management Module
NOTE: This module is conditionally loaded based on ENABLE_INVENTORY flag.
Imports are lazy to prevent loading disabled modules.
"""

__all__ = []

# Lazy imports - only load when explicitly requested
def get_item_service():
    from backend.services.inventory.item_service import ItemMasterService
    return ItemMasterService

def get_transaction_service():
    from backend.services.inventory.transaction_service import StockTransactionService
    return StockTransactionService

def get_verification_service():
    from backend.services.inventory.verification_service import StockVerificationService
    return StockVerificationService

def get_valuation_service():
    from backend.services.inventory.valuation_service import InventoryValuationService
    return InventoryValuationService

"""
Integration Services Package
Handles all third-party integrations for the NBFC Suite

Available Services:
- Bureau Integration (CIBIL, Equifax, Experian, CRIF)
- Bank Statement Analyzer (Perfios/FinBox)
- OCR & Document Verification (AWS Textract)
- eKYC Integration (Aadhaar)
- DigiLocker Integration

Author: NBFC Suite Development Team
Date: January 7, 2026
"""

from .bureau_manager import BureauManager
from .bank_statement_service import BankStatementService
from .ocr_service import OCRService
from .ekyc_service import EKYCService
from .digilocker_service import DigiLockerService

__all__ = [
    'BureauManager',
    'BankStatementService',
    'OCRService',
    'EKYCService',
    'DigiLockerService',
]

__version__ = '1.0.0'

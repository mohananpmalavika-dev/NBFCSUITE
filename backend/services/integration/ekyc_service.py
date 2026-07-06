"""
eKYC Integration Service
Aadhaar-based eKYC integration

Supports:
- Aadhaar OTP-based eKYC
- Biometric authentication (future)
- Auto-fill customer data
- Photo extraction
"""

import requests
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging
import hashlib
import base64

from backend.shared.database.integration_models import EKYCRecord

logger = logging.getLogger(__name__)


class EKYCServiceError(Exception):
    """eKYC service errors"""
    pass


class EKYCService:
    """
    eKYC Integration Service
    
    Handles Aadhaar-based eKYC verification
    """
    
    def __init__(self, db: Session, tenant_id: int, config: Dict[str, Any]):
        """
        Initialize eKYC service
        
        Args:
            db: Database session
            tenant_id: Tenant identifier
            config: Configuration (UIDAI credentials)
        """
        self.db = db
        self.tenant_id = tenant_id
        self.config = config
        self.api_url = config.get('uidai_api_url')
        self.client_id = config.get('uidai_client_id')
        self.client_secret = config.get('uidai_client_secret')
    
    def initiate_ekyc(
        self,
        customer_id: int,
        aadhaar_number: str,
        mobile_number: str
    ) -> Dict[str, Any]:
        """
        Initiate eKYC by sending OTP
        
        Args:
            customer_id: Customer ID
            aadhaar_number: 12-digit Aadhaar number
            mobile_number: Registered mobile number
            
        Returns:
            Transaction ID for OTP verification
        """
        try:
            # Validate Aadhaar number
            if not self._validate_aadhaar(aadhaar_number):
                raise EKYCServiceError("Invalid Aadhaar number format")
            
            logger.info(f"eKYC: Initiating for Aadhaar {aadhaar_number[-4:]}")
            
            # Call UIDAI API to send OTP
            response = requests.post(
                f"{self.api_url}/send-otp",
                json={
                    'aadhaar_number': aadhaar_number,
                    'mobile_number': mobile_number,
                    'client_id': self.client_id
                },
                headers={
                    'Authorization': f'Bearer {self._get_auth_token()}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Create eKYC record
            ekyc_record = EKYCRecord(
                tenant_id=self.tenant_id,
                customer_id=customer_id,
                kyc_type='aadhaar_otp',
                aadhaar_number=aadhaar_number,
                transaction_id=data.get('transaction_id'),
                otp_sent=True,
                otp_verified=False,
                verification_status='pending',
                created_at=datetime.utcnow()
            )
            
            self.db.add(ekyc_record)
            self.db.commit()
            
            logger.info(f"eKYC: OTP sent successfully for Aadhaar {aadhaar_number[-4:]}")
            
            return {
                'success': True,
                'transaction_id': data.get('transaction_id'),
                'message': 'OTP sent to registered mobile number',
                'expires_in': 600  # 10 minutes
            }
            
        except Exception as e:
            error_msg = f"Failed to initiate eKYC: {str(e)}"
            logger.error(f"eKYC: {error_msg}")
            raise EKYCServiceError(error_msg)
    
    def verify_otp_and_fetch(
        self,
        customer_id: int,
        transaction_id: str,
        otp: str
    ) -> Dict[str, Any]:
        """
        Verify OTP and fetch eKYC data
        
        Args:
            customer_id: Customer ID
            transaction_id: Transaction ID from initiate
            otp: 6-digit OTP
            
        Returns:
            eKYC data with customer information
        """
        try:
            logger.info(f"eKYC: Verifying OTP for transaction {transaction_id}")
            
            # Find eKYC record
            ekyc_record = self.db.query(EKYCRecord).filter(
                EKYCRecord.customer_id == customer_id,
                EKYCRecord.transaction_id == transaction_id,
                EKYCRecord.tenant_id == self.tenant_id
            ).first()
            
            if not ekyc_record:
                raise EKYCServiceError("eKYC transaction not found")
            
            # Verify OTP with UIDAI
            response = requests.post(
                f"{self.api_url}/verify-otp",
                json={
                    'transaction_id': transaction_id,
                    'otp': otp,
                    'client_id': self.client_id
                },
                headers={
                    'Authorization': f'Bearer {self._get_auth_token()}',
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                # Parse eKYC data
                kyc_data = data.get('kyc_data', {})
                
                # Update eKYC record
                ekyc_record.otp_verified = True
                ekyc_record.verification_status = 'success'
                ekyc_record.verification_timestamp = datetime.utcnow()
                ekyc_record.kyc_data = kyc_data
                ekyc_record.full_name = kyc_data.get('name')
                ekyc_record.date_of_birth = self._parse_date(kyc_data.get('dob'))
                ekyc_record.gender = kyc_data.get('gender')
                ekyc_record.address = kyc_data.get('address')
                ekyc_record.photo_base64 = kyc_data.get('photo')
                ekyc_record.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(ekyc_record)
                
                logger.info(f"eKYC: Successfully verified for customer {customer_id}")
                
                # Return standardized data
                return {
                    'success': True,
                    'ekyc_id': ekyc_record.id,
                    'data': {
                        'full_name': kyc_data.get('name'),
                        'date_of_birth': kyc_data.get('dob'),
                        'gender': kyc_data.get('gender'),
                        'address': kyc_data.get('address'),
                        'photo_base64': kyc_data.get('photo'),
                        'aadhaar_number': ekyc_record.aadhaar_number
                    },
                    'verified': True,
                    'verification_timestamp': ekyc_record.verification_timestamp.isoformat()
                }
            else:
                ekyc_record.verification_status = 'failed'
                ekyc_record.error_message = data.get('error', 'OTP verification failed')
                self.db.commit()
                
                raise EKYCServiceError("OTP verification failed")
                
        except Exception as e:
            error_msg = f"Failed to verify OTP: {str(e)}"
            logger.error(f"eKYC: {error_msg}")
            raise EKYCServiceError(error_msg)
    
    def get_ekyc_data(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get latest eKYC data for customer"""
        ekyc_record = self.db.query(EKYCRecord).filter(
            EKYCRecord.customer_id == customer_id,
            EKYCRecord.tenant_id == self.tenant_id,
            EKYCRecord.verification_status == 'success'
        ).order_by(EKYCRecord.verification_timestamp.desc()).first()
        
        if ekyc_record:
            return {
                'full_name': ekyc_record.full_name,
                'date_of_birth': ekyc_record.date_of_birth.isoformat() if ekyc_record.date_of_birth else None,
                'gender': ekyc_record.gender,
                'address': ekyc_record.address,
                'aadhaar_number': ekyc_record.aadhaar_number,
                'verified_at': ekyc_record.verification_timestamp.isoformat() if ekyc_record.verification_timestamp else None
            }
        
        return None
    
    def _validate_aadhaar(self, aadhaar: str) -> bool:
        """Validate Aadhaar number format"""
        # Remove spaces
        aadhaar = aadhaar.replace(' ', '')
        
        # Check length and digits
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return False
        
        # Simple checksum validation (Verhoeff algorithm can be added)
        return True
    
    def _get_auth_token(self) -> str:
        """Get authentication token for UIDAI API"""
        # In production, implement proper OAuth flow
        return self.config.get('uidai_access_token', '')
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string"""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, '%d-%m-%Y').date()
        except:
            try:
                return datetime.strptime(date_str, '%d/%m/%Y').date()
            except:
                return None


class DigiLockerService:
    """
    DigiLocker Integration Service
    
    Fetch government-verified documents from DigiLocker
    """
    
    def __init__(self, db: Session, tenant_id: int, config: Dict[str, Any]):
        """
        Initialize DigiLocker service
        
        Args:
            db: Database session
            tenant_id: Tenant identifier
            config: Configuration (DigiLocker app credentials)
        """
        self.db = db
        self.tenant_id = tenant_id
        self.config = config
        self.api_url = config.get('digilocker_api_url')
        self.client_id = config.get('digilocker_client_id')
        self.client_secret = config.get('digilocker_client_secret')
        self.redirect_uri = config.get('digilocker_redirect_uri')
    
    def get_authorization_url(self, customer_id: int) -> str:
        """
        Get DigiLocker authorization URL
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Authorization URL to redirect user
        """
        state = hashlib.sha256(f"{customer_id}{datetime.utcnow()}".encode()).hexdigest()
        
        auth_url = (
            f"{self.api_url}/oauth2/1/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"state={state}"
        )
        
        return auth_url
    
    def fetch_documents(
        self,
        customer_id: int,
        authorization_code: str
    ) -> Dict[str, Any]:
        """
        Fetch documents from DigiLocker after OAuth
        
        Args:
            customer_id: Customer ID
            authorization_code: OAuth authorization code
            
        Returns:
            List of fetched documents
        """
        try:
            # Exchange code for access token
            token_response = requests.post(
                f"{self.api_url}/oauth2/1/token",
                data={
                    'code': authorization_code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'grant_type': 'authorization_code'
                },
                timeout=30
            )
            
            token_response.raise_for_status()
            access_token = token_response.json().get('access_token')
            
            # Get document list
            docs_response = requests.get(
                f"{self.api_url}/api/1/documents",
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=30
            )
            
            docs_response.raise_for_status()
            documents = docs_response.json().get('documents', [])
            
            # Download each document
            fetched_docs = []
            for doc in documents:
                # Download document
                # Save to storage
                # Create DigiLockerDocument record
                pass
            
            return {
                'success': True,
                'documents_count': len(documents),
                'documents': fetched_docs
            }
            
        except Exception as e:
            logger.error(f"DigiLocker: Failed to fetch documents - {str(e)}")
            raise Exception(f"DigiLocker fetch failed: {str(e)}")

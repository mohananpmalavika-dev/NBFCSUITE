"""
Aadhaar eKYC Integration Service
Integrates with UIDAI API for OTP-based and biometric eKYC
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import json
import os
import hashlib
import random
from abc import ABC, abstractmethod

from backend.shared.database.customer_models import (
    Customer, CustomerKYC, CustomerTimeline, ActivityType, KYCStatus
)


# ============================================================================
# BASE eKYC PROVIDER (Abstract)
# ============================================================================

class BaseEKYCProvider(ABC):
    """Abstract base class for eKYC providers"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = 30.0
    
    @abstractmethod
    async def generate_otp(self, aadhaar_number: str) -> Dict[str, Any]:
        """Generate OTP for Aadhaar verification"""
        pass
    
    @abstractmethod
    async def verify_otp(
        self,
        aadhaar_number: str,
        otp: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Verify OTP and fetch eKYC data"""
        pass
    
    @abstractmethod
    async def biometric_auth(
        self,
        aadhaar_number: str,
        biometric_data: str
    ) -> Dict[str, Any]:
        """Authenticate using biometric data"""
        pass



# ============================================================================
# UIDAI eKYC PROVIDER
# ============================================================================

class UIDAIEKYCProvider(BaseEKYCProvider):
    """UIDAI (Aadhaar) eKYC provider"""
    
    async def generate_otp(self, aadhaar_number: str) -> Dict[str, Any]:
        """
        Generate OTP for Aadhaar verification
        
        Args:
            aadhaar_number: 12-digit Aadhaar number
        
        Returns:
            Dictionary with request_id and status
        """
        
        # Validate Aadhaar number
        if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
            raise ValueError("Invalid Aadhaar number format")
        
        # Prepare request
        request_id = f"OTP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        payload = {
            "uid": aadhaar_number,
            "txn": request_id,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Make API call
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/otp/generate",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            result = response.json()
        
        return {
            "request_id": request_id,
            "status": result.get("status"),
            "message": result.get("message"),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat(),
        }
    
    async def verify_otp(
        self,
        aadhaar_number: str,
        otp: str,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Verify OTP and fetch eKYC data
        
        Args:
            aadhaar_number: 12-digit Aadhaar number
            otp: 6-digit OTP
            request_id: Request ID from generate_otp
        
        Returns:
            Dictionary with eKYC data
        """
        
        payload = {
            "uid": aadhaar_number,
            "otp": otp,
            "txn": request_id,
            "timestamp": datetime.now().isoformat(),
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/otp/verify",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            result = response.json()
        
        # Parse eKYC data
        kyc_data = result.get("eKYCData", {})
        
        return {
            "verified": result.get("status") == "success",
            "name": kyc_data.get("name", ""),
            "date_of_birth": kyc_data.get("dob", ""),
            "gender": kyc_data.get("gender", ""),
            "address": {
                "line1": kyc_data.get("address", {}).get("house", ""),
                "line2": kyc_data.get("address", {}).get("street", ""),
                "city": kyc_data.get("address", {}).get("vtc", ""),
                "district": kyc_data.get("address", {}).get("dist", ""),
                "state": kyc_data.get("address", {}).get("state", ""),
                "pincode": kyc_data.get("address", {}).get("pc", ""),
            },
            "photo": kyc_data.get("photo", ""),
            "mobile": kyc_data.get("mobile", ""),
            "email": kyc_data.get("email", ""),
            "raw_data": result,
        }
    
    async def biometric_auth(
        self,
        aadhaar_number: str,
        biometric_data: str
    ) -> Dict[str, Any]:
        """
        Authenticate using biometric data (fingerprint/iris)
        
        Args:
            aadhaar_number: 12-digit Aadhaar number
            biometric_data: Base64 encoded biometric data
        
        Returns:
            Dictionary with authentication result and eKYC data
        """
        
        request_id = f"BIO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        
        payload = {
            "uid": aadhaar_number,
            "biometricData": biometric_data,
            "txn": request_id,
            "timestamp": datetime.now().isoformat(),
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/biometric/auth",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            result = response.json()
        
        # Similar parsing as OTP verification
        kyc_data = result.get("eKYCData", {})
        
        return {
            "verified": result.get("status") == "success",
            "name": kyc_data.get("name", ""),
            "date_of_birth": kyc_data.get("dob", ""),
            "gender": kyc_data.get("gender", ""),
            "address": kyc_data.get("address", {}),
            "photo": kyc_data.get("photo", ""),
            "raw_data": result,
        }



# ============================================================================
# MOCK eKYC PROVIDER (for testing)
# ============================================================================

class MockEKYCProvider(BaseEKYCProvider):
    """Mock eKYC provider for testing"""
    
    # In-memory OTP storage for testing
    _otp_store: Dict[str, Dict[str, Any]] = {}
    
    async def generate_otp(self, aadhaar_number: str) -> Dict[str, Any]:
        """Generate mock OTP"""
        
        import asyncio
        await asyncio.sleep(0.5)
        
        request_id = f"MOCK-OTP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        otp = "123456"  # Fixed OTP for testing
        
        # Store OTP
        self._otp_store[request_id] = {
            "aadhaar": aadhaar_number,
            "otp": otp,
            "expires_at": datetime.now() + timedelta(minutes=10),
        }
        
        return {
            "request_id": request_id,
            "status": "success",
            "message": f"OTP sent successfully (Test OTP: {otp})",
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat(),
        }
    
    async def verify_otp(
        self,
        aadhaar_number: str,
        otp: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Verify mock OTP"""
        
        import asyncio
        await asyncio.sleep(0.5)
        
        # Check if request exists
        stored = self._otp_store.get(request_id)
        if not stored:
            raise ValueError("Invalid or expired OTP request")
        
        # Verify OTP
        if stored["otp"] != otp or stored["aadhaar"] != aadhaar_number:
            return {"verified": False, "error": "Invalid OTP"}
        
        # Check expiry
        if datetime.now() > stored["expires_at"]:
            return {"verified": False, "error": "OTP expired"}
        
        # Return mock eKYC data
        return {
            "verified": True,
            "name": "John Doe",
            "date_of_birth": "1990-01-15",
            "gender": "Male",
            "address": {
                "line1": "House No 123",
                "line2": "MG Road",
                "city": "Bangalore",
                "district": "Bangalore Urban",
                "state": "Karnataka",
                "pincode": "560001",
            },
            "photo": "base64_encoded_photo_data",
            "mobile": "9876543210",
            "email": "john@example.com",
            "raw_data": {"mock": True},
        }
    
    async def biometric_auth(
        self,
        aadhaar_number: str,
        biometric_data: str
    ) -> Dict[str, Any]:
        """Mock biometric authentication"""
        
        import asyncio
        await asyncio.sleep(1.0)
        
        return {
            "verified": True,
            "name": "John Doe",
            "date_of_birth": "1990-01-15",
            "gender": "Male",
            "address": {
                "line1": "House No 123",
                "line2": "MG Road",
                "city": "Bangalore",
                "district": "Bangalore Urban",
                "state": "Karnataka",
                "pincode": "560001",
            },
            "photo": "base64_encoded_photo_data",
            "raw_data": {"mock": True, "biometric": True},
        }



# ============================================================================
# eKYC SERVICE
# ============================================================================

class EKYCService:
    """Main service for eKYC operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        
        # Initialize provider
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> BaseEKYCProvider:
        """Initialize eKYC provider from environment"""
        
        use_mock = os.getenv("EKYC_USE_MOCK", "true").lower() == "true"
        
        if use_mock:
            return MockEKYCProvider("mock_key", "mock_secret", "http://localhost")
        else:
            return UIDAIEKYCProvider(
                api_key=os.getenv("UIDAI_API_KEY"),
                api_secret=os.getenv("UIDAI_API_SECRET"),
                base_url=os.getenv("UIDAI_API_URL", "https://ekyc.uidai.gov.in/api")
            )
    
    async def initiate_aadhaar_otp(
        self,
        customer_id: int,
        aadhaar_number: str
    ) -> Dict[str, Any]:
        """
        Initiate Aadhaar OTP verification
        
        Args:
            customer_id: Customer database ID
            aadhaar_number: 12-digit Aadhaar number
        
        Returns:
            Dictionary with request_id and expiry
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Generate OTP
        result = await self.provider.generate_otp(aadhaar_number)
        
        # Log timeline event
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.KYC_INITIATED,
            title="Aadhaar OTP initiated",
            description=f"OTP sent to Aadhaar-linked mobile",
            metadata={"request_id": result["request_id"]}
        )
        
        return result
    
    async def complete_aadhaar_otp_verification(
        self,
        customer_id: int,
        aadhaar_number: str,
        otp: str,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Complete Aadhaar OTP verification and update customer
        
        Args:
            customer_id: Customer database ID
            aadhaar_number: 12-digit Aadhaar number
            otp: 6-digit OTP
            request_id: Request ID from initiate_aadhaar_otp
        
        Returns:
            Dictionary with verification result and eKYC data
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Verify OTP
        result = await self.provider.verify_otp(aadhaar_number, otp, request_id)
        
        if not result.get("verified"):
            # Log failed attempt
            await self._log_timeline_event(
                customer_id=customer.id,
                activity_type=ActivityType.KYC_REJECTED,
                title="Aadhaar OTP verification failed",
                description=result.get("error", "Invalid OTP"),
            )
            return result
        
        # Update customer with eKYC data
        await self._update_customer_from_ekyc(customer, result)
        
        # Update KYC record
        await self._update_kyc_record(customer.id, "aadhaar", result)
        
        # Log success
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.AADHAAR_VERIFIED,
            title="Aadhaar verified successfully",
            description=f"Name: {result.get('name')}",
            metadata={
                "name": result.get("name"),
                "dob": result.get("date_of_birth"),
                "address": result.get("address"),
            }
        )
        
        return result
    
    async def verify_with_biometric(
        self,
        customer_id: int,
        aadhaar_number: str,
        biometric_data: str
    ) -> Dict[str, Any]:
        """
        Verify Aadhaar using biometric authentication
        
        Args:
            customer_id: Customer database ID
            aadhaar_number: 12-digit Aadhaar number
            biometric_data: Base64 encoded biometric data
        
        Returns:
            Dictionary with verification result
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Authenticate with biometric
        result = await self.provider.biometric_auth(aadhaar_number, biometric_data)
        
        if not result.get("verified"):
            await self._log_timeline_event(
                customer_id=customer.id,
                activity_type=ActivityType.KYC_REJECTED,
                title="Biometric verification failed",
                description="Biometric authentication failed",
            )
            return result
        
        # Update customer with eKYC data
        await self._update_customer_from_ekyc(customer, result)
        
        # Update KYC record
        await self._update_kyc_record(customer.id, "biometric", result)
        
        # Log success
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.BIOMETRIC_CAPTURED,
            title="Biometric verification completed",
            description=f"Name: {result.get('name')}",
            metadata={"name": result.get("name")}
        )
        
        return result
    
    async def _update_customer_from_ekyc(
        self,
        customer: Customer,
        ekyc_data: Dict[str, Any]
    ):
        """Update customer record with eKYC data"""
        
        # Parse name
        name_parts = ekyc_data.get("name", "").split()
        if len(name_parts) >= 2:
            customer.first_name = name_parts[0]
            customer.last_name = " ".join(name_parts[1:])
        else:
            customer.first_name = ekyc_data.get("name", "")
        
        customer.full_name = ekyc_data.get("name", "")
        
        # Date of birth
        if ekyc_data.get("date_of_birth"):
            try:
                from datetime import datetime
                dob = datetime.strptime(ekyc_data["date_of_birth"], "%Y-%m-%d").date()
                customer.date_of_birth = dob
                customer.age = self._calculate_age(dob)
            except:
                pass
        
        # Gender
        gender_map = {"Male": "male", "Female": "female", "Other": "other"}
        if ekyc_data.get("gender") in gender_map:
            from backend.shared.database.customer_models import Gender
            customer.gender = Gender[gender_map[ekyc_data["gender"]].upper()]
        
        # Address
        address = ekyc_data.get("address", {})
        if address:
            customer.current_address_line1 = f"{address.get('line1', '')} {address.get('line2', '')}".strip()
            customer.current_pincode = address.get("pincode", "")
        
        # Mobile and email
        if ekyc_data.get("mobile"):
            customer.mobile = ekyc_data["mobile"]
        if ekyc_data.get("email"):
            customer.email = ekyc_data["email"]
        
        customer.updated_by = self.user_id
        customer.updated_at = datetime.now()
        
        await self.db.commit()
    
    async def _update_kyc_record(
        self,
        customer_id: int,
        verification_method: str,
        ekyc_data: Dict[str, Any]
    ):
        """Update KYC record with verification details"""
        
        # Get or create KYC record
        query = select(CustomerKYC).where(
            and_(
                CustomerKYC.customer_id == customer_id,
                CustomerKYC.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        kyc = result.scalar_one_or_none()
        
        if not kyc:
            kyc = CustomerKYC(
                tenant_id=self.tenant_id,
                customer_id=customer_id,
                created_by=self.user_id
            )
            self.db.add(kyc)
        
        # Update based on method
        if verification_method == "aadhaar":
            kyc.aadhaar_verified = True
            kyc.aadhaar_verified_date = datetime.now()
            kyc.aadhaar_verification_method = "eKYC-OTP"
            kyc.aadhaar_name = ekyc_data.get("name", "")
            kyc.aadhaar_address = json.dumps(ekyc_data.get("address", {}))
        elif verification_method == "biometric":
            kyc.aadhaar_verified = True
            kyc.aadhaar_verified_date = datetime.now()
            kyc.aadhaar_verification_method = "Biometric"
            kyc.biometric_captured = True
            kyc.biometric_capture_date = datetime.now()
        
        # Update overall status
        kyc.kyc_completion_percentage = self._calculate_kyc_completion(kyc)
        if kyc.kyc_completion_percentage >= 80:
            kyc.overall_kyc_status = KYCStatus.COMPLETED
        else:
            kyc.overall_kyc_status = KYCStatus.IN_PROGRESS
        
        kyc.updated_by = self.user_id
        kyc.updated_at = datetime.now()
        
        await self.db.commit()
    
    def _calculate_kyc_completion(self, kyc: CustomerKYC) -> int:
        """Calculate KYC completion percentage"""
        total_checks = 5
        completed = 0
        
        if kyc.aadhaar_verified:
            completed += 1
        if kyc.pan_verified:
            completed += 1
        if kyc.bank_account_verified:
            completed += 1
        if kyc.video_kyc_done or kyc.in_person_verification_done:
            completed += 1
        if kyc.cibil_consent_given:
            completed += 1
        
        return int((completed / total_checks) * 100)
    
    def _calculate_age(self, dob) -> int:
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age
    
    async def _get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        query = select(Customer).where(
            and_(
                Customer.id == customer_id,
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _log_timeline_event(
        self,
        customer_id: int,
        activity_type: ActivityType,
        title: str,
        description: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Log event to customer timeline"""
        timeline = CustomerTimeline(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            activity_type=activity_type,
            title=title,
            description=description,
            event_category="kyc",
            performed_by=self.user_id,
            metadata=metadata,
            is_system_generated=True,
            created_by=self.user_id
        )
        self.db.add(timeline)
        await self.db.commit()

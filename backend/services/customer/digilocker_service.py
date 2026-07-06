"""
DigiLocker Integration Service
Integrates with DigiLocker API for document fetching
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
import json
import os
import base64
from abc import ABC, abstractmethod

from backend.shared.database.customer_models import (
    Customer, CustomerDocument, CustomerTimeline, ActivityType, DocumentStatus
)


# ============================================================================
# BASE DIGILOCKER PROVIDER (Abstract)
# ============================================================================

class BaseDigiLockerProvider(ABC):
    """Abstract base class for DigiLocker providers"""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.timeout = 30.0
    
    @abstractmethod
    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Get OAuth authorization URL"""
        pass
    
    @abstractmethod
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        pass
    
    @abstractmethod
    async def get_issued_documents(self, access_token: str) -> List[Dict[str, Any]]:
        """Get list of issued documents"""
        pass
    
    @abstractmethod
    async def fetch_document(
        self,
        access_token: str,
        document_uri: str
    ) -> Dict[str, Any]:
        """Fetch specific document"""
        pass



# ============================================================================
# DIGILOCKER PROVIDER
# ============================================================================

class DigiLockerProvider(BaseDigiLockerProvider):
    """Official DigiLocker API provider"""
    
    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate OAuth authorization URL for DigiLocker
        
        Args:
            redirect_uri: Callback URL after authorization
            state: Random state for CSRF protection
        
        Returns:
            Authorization URL
        """
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        
        # Build URL
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{self.base_url}/public/oauth2/1/authorize?{query_string}"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization
        
        Returns:
            Dictionary with access_token, refresh_token, expires_in
        """
        
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/public/oauth2/1/token",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_issued_documents(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get list of issued documents in user's DigiLocker
        
        Args:
            access_token: OAuth access token
        
        Returns:
            List of document metadata
        """
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/public/oauth2/1/file/issued",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            result = response.json()
        
        return result.get("items", [])
    
    async def fetch_document(
        self,
        access_token: str,
        document_uri: str
    ) -> Dict[str, Any]:
        """
        Fetch specific document content
        
        Args:
            access_token: OAuth access token
            document_uri: Document URI from issued documents list
        
        Returns:
            Dictionary with document content and metadata
        """
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/public/oauth2/1/file/{document_uri}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            result = response.json()
        
        return {
            "uri": document_uri,
            "name": result.get("name", ""),
            "type": result.get("type", ""),
            "size": result.get("size", 0),
            "content": result.get("content", ""),  # Base64 encoded
            "mime_type": result.get("mime", ""),
            "date_of_issue": result.get("date", ""),
            "issuer": result.get("issuer", ""),
        }



# ============================================================================
# MOCK DIGILOCKER PROVIDER (for testing)
# ============================================================================

class MockDigiLockerProvider(BaseDigiLockerProvider):
    """Mock DigiLocker provider for testing"""
    
    # In-memory token storage
    _tokens: Dict[str, str] = {}
    
    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Generate mock authorization URL"""
        return f"http://localhost:8000/digilocker/mock/authorize?redirect_uri={redirect_uri}&state={state}"
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Return mock access token"""
        
        import asyncio
        await asyncio.sleep(0.5)
        
        access_token = f"mock_token_{code}"
        self._tokens[access_token] = code
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": f"mock_refresh_{code}",
        }
    
    async def get_issued_documents(self, access_token: str) -> List[Dict[str, Any]]:
        """Return mock document list"""
        
        import asyncio
        await asyncio.sleep(0.5)
        
        return [
            {
                "uri": "AADHAAR-123456",
                "name": "Aadhaar Card",
                "type": "ADHAR",
                "size": 524288,
                "date": "2020-01-15",
                "issuer": "UIDAI",
            },
            {
                "uri": "PAN-ABCDE1234F",
                "name": "PAN Card",
                "type": "PANCR",
                "size": 245760,
                "date": "2019-06-20",
                "issuer": "Income Tax Department",
            },
            {
                "uri": "DL-KA12345678",
                "name": "Driving License",
                "type": "DRVLC",
                "size": 327680,
                "date": "2021-03-10",
                "issuer": "Transport Department Karnataka",
            },
        ]
    
    async def fetch_document(
        self,
        access_token: str,
        document_uri: str
    ) -> Dict[str, Any]:
        """Return mock document content"""
        
        import asyncio
        await asyncio.sleep(1.0)
        
        # Mock document content
        mock_content = base64.b64encode(b"Mock PDF content for " + document_uri.encode()).decode()
        
        doc_types = {
            "AADHAAR": {"name": "Aadhaar Card", "type": "ADHAR", "issuer": "UIDAI"},
            "PAN": {"name": "PAN Card", "type": "PANCR", "issuer": "Income Tax Department"},
            "DL": {"name": "Driving License", "type": "DRVLC", "issuer": "Transport Department"},
        }
        
        doc_prefix = document_uri.split("-")[0]
        doc_info = doc_types.get(doc_prefix, {"name": "Document", "type": "OTHER", "issuer": "Unknown"})
        
        return {
            "uri": document_uri,
            "name": doc_info["name"],
            "type": doc_info["type"],
            "size": len(mock_content),
            "content": mock_content,
            "mime_type": "application/pdf",
            "date_of_issue": "2020-01-15",
            "issuer": doc_info["issuer"],
        }


# ============================================================================
# DIGILOCKER SERVICE
# ============================================================================

class DigiLockerService:
    """Main service for DigiLocker operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        
        # Initialize provider
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> BaseDigiLockerProvider:
        """Initialize DigiLocker provider from environment"""
        
        use_mock = os.getenv("DIGILOCKER_USE_MOCK", "true").lower() == "true"
        
        if use_mock:
            return MockDigiLockerProvider("mock_client", "mock_secret", "http://localhost")
        else:
            return DigiLockerProvider(
                client_id=os.getenv("DIGILOCKER_CLIENT_ID"),
                client_secret=os.getenv("DIGILOCKER_CLIENT_SECRET"),
                base_url=os.getenv("DIGILOCKER_API_URL", "https://api.digitallocker.gov.in")
            )
    
    async def initiate_authorization(
        self,
        customer_id: int,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Initiate DigiLocker authorization flow
        
        Args:
            customer_id: Customer database ID
            redirect_uri: Callback URL after authorization
        
        Returns:
            Dictionary with authorization URL and state
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Generate state for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Get authorization URL
        auth_url = await self.provider.get_authorization_url(redirect_uri, state)
        
        # Log timeline event
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.KYC_INITIATED,
            title="DigiLocker authorization initiated",
            description="Customer redirected to DigiLocker for document access",
            metadata={"state": state}
        )
        
        return {
            "authorization_url": auth_url,
            "state": state,
        }
    
    async def complete_authorization(
        self,
        customer_id: int,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Complete DigiLocker authorization and get access token
        
        Args:
            customer_id: Customer database ID
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization
        
        Returns:
            Dictionary with access token and available documents
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Exchange code for token
        token_data = await self.provider.exchange_code_for_token(code, redirect_uri)
        
        # Get issued documents
        documents = await self.provider.get_issued_documents(token_data["access_token"])
        
        # Log timeline event
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.DOCUMENT_UPLOADED,
            title="DigiLocker connected",
            description=f"Found {len(documents)} documents in DigiLocker",
            metadata={"document_count": len(documents)}
        )
        
        return {
            "access_token": token_data["access_token"],
            "expires_in": token_data.get("expires_in", 3600),
            "documents": documents,
        }
    
    async def fetch_and_store_document(
        self,
        customer_id: int,
        access_token: str,
        document_uri: str,
        document_type_id: str
    ) -> CustomerDocument:
        """
        Fetch document from DigiLocker and store in system
        
        Args:
            customer_id: Customer database ID
            access_token: DigiLocker access token
            document_uri: Document URI to fetch
            document_type_id: Document type UUID
        
        Returns:
            CustomerDocument record
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Fetch document from DigiLocker
        doc_data = await self.provider.fetch_document(access_token, document_uri)
        
        # TODO: Upload to file storage (S3/MinIO) and get URL
        # For now, we'll use a placeholder
        document_url = f"/documents/{customer_id}/{document_uri}.pdf"
        
        # Create document record
        document = CustomerDocument(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            document_type_id=document_type_id,
            document_name=doc_data.get("name", ""),
            document_url=document_url,
            document_size_kb=int(doc_data.get("size", 0) / 1024),
            document_format="PDF",
            status=DocumentStatus.SUBMITTED,
            issue_date=datetime.strptime(doc_data.get("date_of_issue", ""), "%Y-%m-%d").date() if doc_data.get("date_of_issue") else None,
            ocr_data={"source": "digilocker", "issuer": doc_data.get("issuer", "")},
            uploaded_by=self.user_id,
            uploaded_date=datetime.now(),
            created_by=self.user_id
        )
        
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        
        # Log timeline event
        await self._log_timeline_event(
            customer_id=customer.id,
            activity_type=ActivityType.DOCUMENT_UPLOADED,
            title=f"Document fetched from DigiLocker",
            description=f"{doc_data.get('name', '')} uploaded",
            metadata={"document_id": str(document.id), "source": "digilocker"}
        )
        
        return document
    
    async def get_available_documents(
        self,
        customer_id: int,
        access_token: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of available documents in customer's DigiLocker
        
        Args:
            customer_id: Customer database ID
            access_token: DigiLocker access token
        
        Returns:
            List of document metadata
        """
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get issued documents
        documents = await self.provider.get_issued_documents(access_token)
        
        return documents
    
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

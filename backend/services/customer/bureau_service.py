"""
Credit Bureau Integration Service
Integrates with CIBIL, Equifax, Experian, and CRIF for credit report pulling
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import httpx
import json
import os
from abc import ABC, abstractmethod

from backend.shared.database.customer_models import (
    Customer, CustomerBureauHistory, BureauProvider, BureauPullStatus,
    CustomerTimeline, ActivityType
)


# ============================================================================
# BASE BUREAU PROVIDER (Abstract)
# ============================================================================

class BaseBureauProvider(ABC):
    """Abstract base class for bureau providers"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = 30.0
    
    @abstractmethod
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """Pull credit report from bureau"""
        pass
    
    @abstractmethod
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse bureau response into standardized format"""
        pass


# ============================================================================
# CIBIL PROVIDER
# ============================================================================

class CIBILProvider(BaseBureauProvider):
    """CIBIL TransUnion bureau provider"""
    
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Pull CIBIL credit report
        
        Args:
            customer_id: Internal customer ID
            pan: PAN number
            name: Full name
            dob: Date of birth (YYYY-MM-DD)
            mobile: Mobile number
            address: Address dict with keys: line1, city, state, pincode
        """
        
        # Prepare request payload
        payload = {
            "RequestHeader": {
                "CustomerId": customer_id,
                "RequestId": f"CIBIL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "RequestDate": datetime.now().isoformat(),
            },
            "RequestBody": {
                "InquiryPurpose": "LOAN",
                "FirstName": name.split()[0] if name else "",
                "LastName": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
                "DOB": dob,
                "PANId": pan,
                "MobilePhone": mobile,
                "Address": {
                    "AddressLine1": address.get("line1", ""),
                    "City": address.get("city", ""),
                    "State": address.get("state", ""),
                    "Pincode": address.get("pincode", ""),
                },
                "IDDetails": [
                    {"IDType": "PAN", "IDValue": pan},
                ],
            }
        }
        
        # Make API call
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/credit-report",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse CIBIL response"""
        try:
            report_data = response.get("ResponseBody", {})
            score_segment = report_data.get("ScoreSegment", {})
            
            return {
                "credit_score": int(score_segment.get("Score", 0)),
                "score_date": score_segment.get("ScoreDate", ""),
                "total_accounts": len(report_data.get("Accounts", [])),
                "active_accounts": len([a for a in report_data.get("Accounts", []) if a.get("Status") == "Active"]),
                "total_outstanding": sum([float(a.get("CurrentBalance", 0)) for a in report_data.get("Accounts", [])]),
                "enquiries_1m": len([e for e in report_data.get("Enquiries", []) if self._is_within_months(e.get("Date"), 1)]),
                "enquiries_3m": len([e for e in report_data.get("Enquiries", []) if self._is_within_months(e.get("Date"), 3)]),
                "enquiries_6m": len([e for e in report_data.get("Enquiries", []) if self._is_within_months(e.get("Date"), 6)]),
                "enquiries_12m": len([e for e in report_data.get("Enquiries", []) if self._is_within_months(e.get("Date"), 12)]),
                "raw_data": response,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse CIBIL response: {str(e)}")
    
    def _is_within_months(self, date_str: str, months: int) -> bool:
        """Check if date is within specified months"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date >= datetime.now() - timedelta(days=months * 30)
        except:
            return False



# ============================================================================
# EQUIFAX PROVIDER
# ============================================================================

class EquifaxProvider(BaseBureauProvider):
    """Equifax bureau provider"""
    
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """Pull Equifax credit report"""
        
        payload = {
            "requestId": f"EQX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customerId": customer_id,
            "applicantDetails": {
                "name": name,
                "dateOfBirth": dob,
                "pan": pan,
                "mobile": mobile,
                "address": address,
            },
            "inquiryPurpose": "LOAN_APPLICATION",
            "includeScore": True,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v2/credit-report",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "X-API-Secret": self.api_secret,
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Equifax response"""
        try:
            data = response.get("data", {})
            score_info = data.get("scoreInfo", {})
            accounts = data.get("accounts", [])
            
            return {
                "credit_score": int(score_info.get("score", 0)),
                "score_date": score_info.get("scoreDate", ""),
                "total_accounts": len(accounts),
                "active_accounts": len([a for a in accounts if a.get("accountStatus") == "ACTIVE"]),
                "total_outstanding": sum([float(a.get("currentBalance", 0)) for a in accounts]),
                "enquiries_1m": data.get("enquiries1Month", 0),
                "enquiries_3m": data.get("enquiries3Months", 0),
                "enquiries_6m": data.get("enquiries6Months", 0),
                "enquiries_12m": data.get("enquiries12Months", 0),
                "raw_data": response,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse Equifax response: {str(e)}")


# ============================================================================
# EXPERIAN PROVIDER
# ============================================================================

class ExperianProvider(BaseBureauProvider):
    """Experian bureau provider"""
    
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """Pull Experian credit report"""
        
        payload = {
            "header": {
                "transactionId": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "customerId": customer_id,
                "timestamp": datetime.now().isoformat(),
            },
            "request": {
                "personalInfo": {
                    "fullName": name,
                    "dateOfBirth": dob,
                    "panNumber": pan,
                    "mobileNumber": mobile,
                },
                "addressInfo": address,
                "consentInfo": {
                    "consentGiven": True,
                    "purpose": "CREDIT_ASSESSMENT",
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/credit-information",
                json=payload,
                headers={
                    "Authorization": f"Basic {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Experian response"""
        try:
            report = response.get("response", {}).get("creditReport", {})
            score = report.get("creditScore", {})
            summary = report.get("accountSummary", {})
            
            return {
                "credit_score": int(score.get("value", 0)),
                "score_date": score.get("scoreDate", ""),
                "total_accounts": summary.get("totalAccounts", 0),
                "active_accounts": summary.get("activeAccounts", 0),
                "total_outstanding": float(summary.get("totalOutstanding", 0)),
                "enquiries_1m": summary.get("enquiries1Month", 0),
                "enquiries_3m": summary.get("enquiries3Months", 0),
                "enquiries_6m": summary.get("enquiries6Months", 0),
                "enquiries_12m": summary.get("enquiries12Months", 0),
                "raw_data": response,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse Experian response: {str(e)}")


# ============================================================================
# CRIF PROVIDER
# ============================================================================

class CRIFProvider(BaseBureauProvider):
    """CRIF High Mark bureau provider"""
    
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """Pull CRIF credit report"""
        
        payload = {
            "requestInfo": {
                "requestId": f"CRIF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "memberId": self.api_key,
                "requestDateTime": datetime.now().isoformat(),
            },
            "applicantInfo": {
                "personalInfo": {
                    "name": {"fullName": name},
                    "dateOfBirth": dob,
                    "identifiers": [
                        {"type": "PAN", "value": pan},
                        {"type": "MOBILE", "value": mobile},
                    ],
                },
                "addressInfo": [address],
            },
            "inquiryPurpose": "LOAN_ORIGINATION",
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/inquiry",
                json=payload,
                headers={
                    "X-Member-Id": self.api_key,
                    "X-Member-Password": self.api_secret,
                    "Content-Type": "application/json",
                }
            )
            response.raise_for_status()
            return response.json()
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse CRIF response"""
        try:
            report = response.get("creditReport", {})
            score_segment = report.get("scoreSegment", {})
            account_summary = report.get("accountSummary", {})
            
            return {
                "credit_score": int(score_segment.get("score", 0)),
                "score_date": score_segment.get("scoreDate", ""),
                "total_accounts": account_summary.get("totalAccounts", 0),
                "active_accounts": account_summary.get("activeAccounts", 0),
                "total_outstanding": float(account_summary.get("totalOutstanding", 0)),
                "enquiries_1m": report.get("enquiryCount1Month", 0),
                "enquiries_3m": report.get("enquiryCount3Months", 0),
                "enquiries_6m": report.get("enquiryCount6Months", 0),
                "enquiries_12m": report.get("enquiryCount12Months", 0),
                "raw_data": response,
            }
        except Exception as e:
            raise ValueError(f"Failed to parse CRIF response: {str(e)}")


# ============================================================================
# MOCK BUREAU PROVIDER (for testing)
# ============================================================================

class MockBureauProvider(BaseBureauProvider):
    """Mock bureau provider for testing"""
    
    async def pull_report(
        self,
        customer_id: str,
        pan: str,
        name: str,
        dob: str,
        mobile: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """Return mock credit report"""
        
        # Simulate API delay
        import asyncio
        await asyncio.sleep(0.5)
        
        # Generate mock score based on PAN hash
        score = 650 + (hash(pan) % 250)
        
        return {
            "status": "success",
            "request_id": f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "score": score,
            "score_date": datetime.now().strftime("%Y-%m-%d"),
            "accounts": 5,
            "active_accounts": 3,
            "outstanding": 150000,
            "enquiries": {"1m": 1, "3m": 2, "6m": 4, "12m": 8},
        }
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse mock response"""
        return {
            "credit_score": response.get("score", 0),
            "score_date": response.get("score_date", ""),
            "total_accounts": response.get("accounts", 0),
            "active_accounts": response.get("active_accounts", 0),
            "total_outstanding": float(response.get("outstanding", 0)),
            "enquiries_1m": response.get("enquiries", {}).get("1m", 0),
            "enquiries_3m": response.get("enquiries", {}).get("3m", 0),
            "enquiries_6m": response.get("enquiries", {}).get("6m", 0),
            "enquiries_12m": response.get("enquiries", {}).get("12m", 0),
            "raw_data": response,
        }


# ============================================================================
# CREDIT BUREAU SERVICE
# ============================================================================

class CreditBureauService:
    """Main service for credit bureau operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        
        # Initialize providers based on environment
        self.providers = self._initialize_providers()
    
    def _initialize_providers(self) -> Dict[BureauProvider, BaseBureauProvider]:
        """Initialize bureau providers from environment variables"""
        providers = {}
        
        # Check if using mock mode
        use_mock = os.getenv("BUREAU_USE_MOCK", "true").lower() == "true"
        
        if use_mock:
            # Use mock provider for all bureaus in development
            mock_provider = MockBureauProvider("mock_key", "mock_secret", "http://localhost")
            providers[BureauProvider.CIBIL] = mock_provider
            providers[BureauProvider.EQUIFAX] = mock_provider
            providers[BureauProvider.EXPERIAN] = mock_provider
            providers[BureauProvider.CRIF] = mock_provider
        else:
            # Initialize real providers
            if os.getenv("CIBIL_API_KEY"):
                providers[BureauProvider.CIBIL] = CIBILProvider(
                    api_key=os.getenv("CIBIL_API_KEY"),
                    api_secret=os.getenv("CIBIL_API_SECRET"),
                    base_url=os.getenv("CIBIL_API_URL", "https://api.cibil.com")
                )
            
            if os.getenv("EQUIFAX_API_KEY"):
                providers[BureauProvider.EQUIFAX] = EquifaxProvider(
                    api_key=os.getenv("EQUIFAX_API_KEY"),
                    api_secret=os.getenv("EQUIFAX_API_SECRET"),
                    base_url=os.getenv("EQUIFAX_API_URL", "https://api.equifax.co.in")
                )
            
            if os.getenv("EXPERIAN_API_KEY"):
                providers[BureauProvider.EXPERIAN] = ExperianProvider(
                    api_key=os.getenv("EXPERIAN_API_KEY"),
                    api_secret=os.getenv("EXPERIAN_API_SECRET"),
                    base_url=os.getenv("EXPERIAN_API_URL", "https://api.experian.in")
                )
            
            if os.getenv("CRIF_API_KEY"):
                providers[BureauProvider.CRIF] = CRIFProvider(
                    api_key=os.getenv("CRIF_API_KEY"),
                    api_secret=os.getenv("CRIF_API_SECRET"),
                    base_url=os.getenv("CRIF_API_URL", "https://api.crifhighmark.com")
                )
        
        return providers
    
    async def pull_credit_report(
        self,
        customer_id: int,
        bureau_provider: BureauProvider,
        request_purpose: str = "loan_application"
    ) -> CustomerBureauHistory:
        """
        Pull credit report from specified bureau
        
        Args:
            customer_id: Customer database ID
            bureau_provider: Which bureau to use (CIBIL, EQUIFAX, etc.)
            request_purpose: Purpose of request (loan_application, periodic_review)
        
        Returns:
            CustomerBureauHistory record
        """
        
        # Get customer details
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Validate customer has required fields
        if not customer.pan_number:
            raise ValueError("Customer PAN number is required for bureau pull")
        
        # Get provider
        provider = self.providers.get(bureau_provider)
        if not provider:
            raise ValueError(f"Bureau provider {bureau_provider.value} is not configured")
        
        # Create bureau history record
        bureau_request_id = f"{bureau_provider.value.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        history = CustomerBureauHistory(
            tenant_id=self.tenant_id,
            customer_id=customer.id,
            bureau_provider=bureau_provider,
            bureau_request_id=bureau_request_id,
            request_purpose=request_purpose,
            requested_by=self.user_id,
            status=BureauPullStatus.INITIATED,
            created_by=self.user_id
        )
        self.db.add(history)
        await self.db.commit()
        
        try:
            # Prepare address
            address = {
                "line1": customer.current_address_line1 or "",
                "city": customer.current_city.name if customer.current_city else "",
                "state": customer.current_state.name if customer.current_state else "",
                "pincode": customer.current_pincode or "",
            }
            
            # Start timer
            start_time = datetime.now()
            
            # Pull report
            response = await provider.pull_report(
                customer_id=str(customer.id),
                pan=customer.pan_number,
                name=customer.full_name,
                dob=customer.date_of_birth.strftime("%Y-%m-%d") if customer.date_of_birth else "",
                mobile=customer.mobile,
                address=address
            )
            
            # Calculate response time
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Parse response
            parsed_data = provider.parse_response(response)
            
            # Update history record
            history.response_date = datetime.now()
            history.response_time_ms = response_time_ms
            history.status = BureauPullStatus.SUCCESS
            history.credit_score = parsed_data.get("credit_score")
            history.score_date = datetime.strptime(parsed_data.get("score_date"), "%Y-%m-%d").date() if parsed_data.get("score_date") else None
            history.total_accounts = parsed_data.get("total_accounts", 0)
            history.active_accounts = parsed_data.get("active_accounts", 0)
            history.total_outstanding = Decimal(str(parsed_data.get("total_outstanding", 0)))
            history.recent_enquiries_1m = parsed_data.get("enquiries_1m", 0)
            history.recent_enquiries_3m = parsed_data.get("enquiries_3m", 0)
            history.recent_enquiries_6m = parsed_data.get("enquiries_6m", 0)
            history.recent_enquiries_12m = parsed_data.get("enquiries_12m", 0)
            history.raw_response = parsed_data.get("raw_data")
            
            # Update customer record
            customer.cibil_score = parsed_data.get("credit_score")
            customer.cibil_last_checked = datetime.now()
            
            # Update risk rating based on score
            customer.risk_rating = self._calculate_risk_rating(parsed_data.get("credit_score", 0))
            
            await self.db.commit()
            await self.db.refresh(history)
            
            # Log timeline event
            await self._log_timeline_event(
                customer_id=customer.id,
                activity_type=ActivityType.BUREAU_REPORT_FETCHED,
                title=f"{bureau_provider.value.upper()} report fetched",
                description=f"Credit score: {parsed_data.get('credit_score')}",
                metadata={
                    "bureau": bureau_provider.value,
                    "score": parsed_data.get("credit_score"),
                    "total_accounts": parsed_data.get("total_accounts"),
                }
            )
            
            return history
            
        except httpx.HTTPError as e:
            # HTTP/Network error
            history.status = BureauPullStatus.FAILED
            history.error_message = f"API Error: {str(e)}"
            await self.db.commit()
            raise
            
        except Exception as e:
            # Other errors
            history.status = BureauPullStatus.FAILED
            history.error_message = str(e)
            await self.db.commit()
            raise
    
    async def get_bureau_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[CustomerBureauHistory]:
        """Get bureau pull history for customer"""
        query = select(CustomerBureauHistory).where(
            and_(
                CustomerBureauHistory.customer_id == customer_id,
                CustomerBureauHistory.tenant_id == self.tenant_id
            )
        ).order_by(CustomerBureauHistory.request_date.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_latest_score(self, customer_id: int) -> Optional[int]:
        """Get latest credit score for customer"""
        query = select(CustomerBureauHistory).where(
            and_(
                CustomerBureauHistory.customer_id == customer_id,
                CustomerBureauHistory.tenant_id == self.tenant_id,
                CustomerBureauHistory.status == BureauPullStatus.SUCCESS,
                CustomerBureauHistory.credit_score.isnot(None)
            )
        ).order_by(CustomerBureauHistory.request_date.desc()).limit(1)
        
        result = await self.db.execute(query)
        history = result.scalar_one_or_none()
        return history.credit_score if history else None
    
    def _calculate_risk_rating(self, credit_score: int) -> str:
        """Calculate risk rating from credit score"""
        from backend.shared.database.customer_models import RiskRating
        
        if credit_score >= 750:
            return RiskRating.LOW
        elif credit_score >= 650:
            return RiskRating.MEDIUM
        elif credit_score >= 550:
            return RiskRating.HIGH
        else:
            return RiskRating.VERY_HIGH
    
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
            event_category="bureau",
            performed_by=self.user_id,
            metadata=metadata,
            is_system_generated=True,
            created_by=self.user_id
        )
        self.db.add(timeline)
        await self.db.commit()

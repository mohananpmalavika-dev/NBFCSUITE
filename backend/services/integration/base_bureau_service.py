"""
Base Bureau Service
Abstract base class for all credit bureau integrations

Provides common functionality:
- Authentication handling
- Request/response logging
- Error handling and retry logic
- Rate limiting
- Cache management
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
import time
import hashlib
import json

logger = logging.getLogger(__name__)


class BureauServiceError(Exception):
    """Base exception for bureau service errors"""
    pass


class BureauAuthenticationError(BureauServiceError):
    """Raised when authentication fails"""
    pass


class BureauRateLimitError(BureauServiceError):
    """Raised when rate limit is exceeded"""
    pass


class BaseBureauService(ABC):
    """
    Abstract base class for credit bureau integrations
    
    All bureau-specific services should inherit from this class
    and implement the required abstract methods.
    """
    
    # Bureau-specific configuration (override in subclasses)
    BUREAU_NAME = "Generic"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    RATE_LIMIT_PER_MINUTE = 60
    CACHE_DURATION_HOURS = 24
    
    def __init__(self, db: Session, tenant_id: int, config: Dict[str, Any]):
        """
        Initialize bureau service
        
        Args:
            db: Database session
            tenant_id: Tenant identifier
            config: Bureau-specific configuration (API keys, URLs, etc.)
        """
        self.db = db
        self.tenant_id = tenant_id
        self.config = config
        self._request_timestamps = []
        self._cache = {}
        
        # Validate configuration
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate bureau-specific configuration
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> str:
        """
        Authenticate with bureau API
        
        Returns:
            Authentication token or session ID
            
        Raises:
            BureauAuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def pull_consumer_report(
        self,
        customer_data: Dict[str, Any],
        consent_id: int
    ) -> Dict[str, Any]:
        """
        Pull consumer credit report
        
        Args:
            customer_data: Customer information (name, PAN, etc.)
            consent_id: Consent record ID
            
        Returns:
            Parsed credit report data
            
        Raises:
            BureauServiceError: If report pull fails
        """
        pass
    
    @abstractmethod
    def parse_report(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse bureau-specific response format
        
        Args:
            raw_response: Raw API response
            
        Returns:
            Standardized report format
        """
        pass
    
    def check_rate_limit(self) -> None:
        """
        Check if rate limit is exceeded
        
        Raises:
            BureauRateLimitError: If rate limit exceeded
        """
        now = time.time()
        # Remove timestamps older than 1 minute
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if now - ts < 60
        ]
        
        if len(self._request_timestamps) >= self.RATE_LIMIT_PER_MINUTE:
            raise BureauRateLimitError(
                f"{self.BUREAU_NAME}: Rate limit of {self.RATE_LIMIT_PER_MINUTE}/min exceeded"
            )
        
        self._request_timestamps.append(now)
    
    def get_cache_key(self, customer_data: Dict[str, Any]) -> str:
        """
        Generate cache key for customer
        
        Args:
            customer_data: Customer information
            
        Returns:
            Cache key string
        """
        # Create hash from PAN/Aadhaar + DOB
        key_data = f"{customer_data.get('pan', '')}{customer_data.get('aadhaar', '')}{customer_data.get('dob', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_report(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached report if available and not expired
        
        Args:
            customer_data: Customer information
            
        Returns:
            Cached report or None
        """
        cache_key = self.get_cache_key(customer_data)
        
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            cached_time = cached_data['timestamp']
            
            # Check if cache is still valid
            if datetime.utcnow() - cached_time < timedelta(hours=self.CACHE_DURATION_HOURS):
                logger.info(f"{self.BUREAU_NAME}: Using cached report for customer")
                return cached_data['report']
            else:
                # Cache expired, remove it
                del self._cache[cache_key]
        
        return None
    
    def cache_report(self, customer_data: Dict[str, Any], report: Dict[str, Any]) -> None:
        """
        Cache report for future use
        
        Args:
            customer_data: Customer information
            report: Report data to cache
        """
        cache_key = self.get_cache_key(customer_data)
        self._cache[cache_key] = {
            'timestamp': datetime.utcnow(),
            'report': report
        }
        logger.info(f"{self.BUREAU_NAME}: Cached report for customer")
    
    def execute_with_retry(self, func, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            BureauServiceError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"{self.BUREAU_NAME}: Attempt {attempt + 1}/{self.MAX_RETRIES} failed: {str(e)}"
                )
                
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"{self.BUREAU_NAME}: All retry attempts failed")
        
        raise BureauServiceError(f"{self.BUREAU_NAME}: Failed after {self.MAX_RETRIES} attempts: {str(last_error)}")
    
    def log_request(
        self,
        customer_id: int,
        request_type: str,
        request_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log bureau API request for audit trail
        
        Args:
            customer_id: Customer ID
            request_type: Type of request (consumer_report, commercial_report, etc.)
            request_data: Request payload (sanitized)
            response_data: Response data (sanitized)
            error: Error message if request failed
        """
        # TODO: Implement logging to database
        log_entry = {
            'bureau_name': self.BUREAU_NAME,
            'tenant_id': self.tenant_id,
            'customer_id': customer_id,
            'request_type': request_type,
            'request_timestamp': datetime.utcnow().isoformat(),
            'success': error is None,
            'error': error
        }
        
        logger.info(f"{self.BUREAU_NAME}: Request logged - {json.dumps(log_entry)}")
    
    def extract_score(self, report: Dict[str, Any]) -> Optional[int]:
        """
        Extract credit score from parsed report
        
        Args:
            report: Parsed report data
            
        Returns:
            Credit score (300-900) or None
        """
        # Override in subclass for bureau-specific extraction
        return report.get('score')
    
    def extract_accounts(self, report: Dict[str, Any]) -> list:
        """
        Extract account details from parsed report
        
        Args:
            report: Parsed report data
            
        Returns:
            List of account dictionaries
        """
        # Override in subclass for bureau-specific extraction
        return report.get('accounts', [])
    
    def extract_enquiries(self, report: Dict[str, Any]) -> list:
        """
        Extract enquiry history from parsed report
        
        Args:
            report: Parsed report data
            
        Returns:
            List of enquiry dictionaries
        """
        # Override in subclass for bureau-specific extraction
        return report.get('enquiries', [])
    
    def calculate_utilization(self, accounts: list) -> float:
        """
        Calculate credit utilization ratio
        
        Args:
            accounts: List of credit accounts
            
        Returns:
            Utilization percentage (0-100)
        """
        total_limit = 0
        total_balance = 0
        
        for account in accounts:
            if account.get('account_type') in ['Credit Card', 'Overdraft']:
                total_limit += account.get('credit_limit', 0)
                total_balance += account.get('current_balance', 0)
        
        if total_limit > 0:
            return round((total_balance / total_limit) * 100, 2)
        
        return 0.0

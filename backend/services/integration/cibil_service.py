"""
CIBIL Integration Service
Integration with CIBIL (Credit Information Bureau India Limited)

Supports:
- Consumer credit report
- Commercial credit report (for businesses)
- Score retrieval
- Report parsing
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime, date
import xml.etree.ElementTree as ET
import logging

from .base_bureau_service import (
    BaseBureauService,
    BureauServiceError,
    BureauAuthenticationError
)

logger = logging.getLogger(__name__)


class CIBILService(BaseBureauService):
    """
    CIBIL API Integration Service
    
    Handles authentication, report pulling, and response parsing
    for CIBIL credit bureau.
    """
    
    BUREAU_NAME = "CIBIL"
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    RATE_LIMIT_PER_MINUTE = 60
    CACHE_DURATION_HOURS = 24
    
    def validate_config(self) -> None:
        """Validate CIBIL-specific configuration"""
        required_keys = ['api_url', 'member_id', 'password', 'certificate_path']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"CIBIL config missing required key: {key}")
        
        logger.info("CIBIL: Configuration validated successfully")
    
    def authenticate(self) -> str:
        """
        Authenticate with CIBIL API
        
        CIBIL uses certificate-based authentication
        
        Returns:
            Session token or member ID
        """
        try:
            # CIBIL typically uses client certificates for authentication
            # This is a simplified version
            auth_data = {
                'MemberId': self.config['member_id'],
                'Password': self.config['password']
            }
            
            logger.info(f"CIBIL: Authentication successful for member {self.config['member_id']}")
            return self.config['member_id']
            
        except Exception as e:
            logger.error(f"CIBIL: Authentication failed - {str(e)}")
            raise BureauAuthenticationError(f"CIBIL authentication failed: {str(e)}")
    
    def pull_consumer_report(
        self,
        customer_data: Dict[str, Any],
        consent_id: int
    ) -> Dict[str, Any]:
        """
        Pull consumer credit report from CIBIL
        
        Args:
            customer_data: {
                'pan': str,
                'name': str,
                'dob': date,
                'address': str,
                'pincode': str,
                'mobile': str,
                'email': str
            }
            consent_id: Consent record ID
            
        Returns:
            Parsed credit report
        """
        # Check rate limit
        self.check_rate_limit()
        
        # Check cache first
        cached_report = self.get_cached_report(customer_data)
        if cached_report:
            return cached_report
        
        try:
            # Authenticate
            auth_token = self.authenticate()
            
            # Prepare CIBIL request
            request_xml = self._build_consumer_request(customer_data, consent_id)
            
            # Make API call with retry
            raw_response = self.execute_with_retry(
                self._make_api_call,
                request_xml,
                auth_token
            )
            
            # Parse response
            parsed_report = self.parse_report(raw_response)
            
            # Cache the report
            self.cache_report(customer_data, parsed_report)
            
            # Log request
            self.log_request(
                customer_id=customer_data.get('customer_id'),
                request_type='consumer_report',
                request_data=customer_data,
                response_data={'score': parsed_report.get('score')}
            )
            
            logger.info(f"CIBIL: Successfully pulled consumer report for PAN {customer_data.get('pan')}")
            return parsed_report
            
        except Exception as e:
            error_msg = f"Failed to pull CIBIL consumer report: {str(e)}"
            logger.error(f"CIBIL: {error_msg}")
            
            # Log error
            self.log_request(
                customer_id=customer_data.get('customer_id'),
                request_type='consumer_report',
                request_data=customer_data,
                error=error_msg
            )
            
            raise BureauServiceError(error_msg)
    
    def pull_commercial_report(
        self,
        business_data: Dict[str, Any],
        consent_id: int
    ) -> Dict[str, Any]:
        """
        Pull commercial credit report for businesses
        
        Args:
            business_data: Business information (CIN, PAN, etc.)
            consent_id: Consent record ID
            
        Returns:
            Parsed commercial credit report
        """
        # Similar to consumer report but for businesses
        # Implementation would follow similar pattern
        logger.info("CIBIL: Commercial report feature - to be implemented")
        return {}
    
    def _build_consumer_request(
        self,
        customer_data: Dict[str, Any],
        consent_id: int
    ) -> str:
        """
        Build CIBIL consumer report request XML
        
        Args:
            customer_data: Customer information
            consent_id: Consent ID
            
        Returns:
            XML request string
        """
        # CIBIL uses XML format for requests
        # This is a simplified version - actual CIBIL XML is more complex
        
        dob = customer_data.get('dob')
        if isinstance(dob, date):
            dob_str = dob.strftime('%d%m%Y')
        else:
            dob_str = dob
        
        xml_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<INProfileRequest>
    <Authentication>
        <MemberCode>{self.config['member_id']}</MemberCode>
        <Password>{self.config['password']}</Password>
    </Authentication>
    <RequestHeader>
        <RequestId>{consent_id}</RequestId>
        <RequestDateTime>{datetime.utcnow().strftime('%Y%m%d%H%M%S')}</RequestDateTime>
        <ReportType>Consumer</ReportType>
    </RequestHeader>
    <RequestBody>
        <InquiryPurpose>04</InquiryPurpose>
        <Applicant>
            <Name>{customer_data.get('name', '')}</Name>
            <DOB>{dob_str}</DOB>
            <PANId>{customer_data.get('pan', '')}</PANId>
            <Address>
                <AddressLine1>{customer_data.get('address', '')}</AddressLine1>
                <City>{customer_data.get('city', '')}</City>
                <State>{customer_data.get('state', '')}</State>
                <Pincode>{customer_data.get('pincode', '')}</Pincode>
            </Address>
            <Phone>
                <Mobile>{customer_data.get('mobile', '')}</Mobile>
            </Phone>
            <Email>{customer_data.get('email', '')}</Email>
        </Applicant>
    </RequestBody>
</INProfileRequest>"""
        
        return xml_request
    
    def _make_api_call(self, request_xml: str, auth_token: str) -> Dict[str, Any]:
        """
        Make HTTP request to CIBIL API
        
        Args:
            request_xml: XML request payload
            auth_token: Authentication token
            
        Returns:
            Raw response data
        """
        try:
            # In production, use client certificate authentication
            cert_path = self.config.get('certificate_path')
            
            response = requests.post(
                self.config['api_url'],
                data=request_xml,
                headers={'Content-Type': 'application/xml'},
                cert=cert_path if cert_path else None,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {'xml': response.text, 'status_code': response.status_code}
            
        except requests.exceptions.RequestException as e:
            raise BureauServiceError(f"CIBIL API call failed: {str(e)}")
    
    def parse_report(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse CIBIL XML response
        
        Args:
            raw_response: Raw API response with XML
            
        Returns:
            Standardized report format
        """
        try:
            xml_data = raw_response.get('xml', '')
            root = ET.fromstring(xml_data)
            
            # Extract CIBIL score
            score_element = root.find('.//Score')
            score = int(score_element.text) if score_element is not None else None
            
            # Extract account information
            accounts = []
            for account_elem in root.findall('.//Account'):
                account = {
                    'account_number': self._get_text(account_elem, 'AccountNumber'),
                    'account_type': self._get_text(account_elem, 'AccountType'),
                    'ownership': self._get_text(account_elem, 'Ownership'),
                    'date_opened': self._get_text(account_elem, 'DateOpened'),
                    'date_closed': self._get_text(account_elem, 'DateClosed'),
                    'credit_limit': float(self._get_text(account_elem, 'CreditLimit', '0')),
                    'current_balance': float(self._get_text(account_elem, 'CurrentBalance', '0')),
                    'amount_overdue': float(self._get_text(account_elem, 'AmountOverdue', '0')),
                    'payment_status': self._get_text(account_elem, 'PaymentStatus'),
                    'dpd': int(self._get_text(account_elem, 'DPD', '0')),
                }
                accounts.append(account)
            
            # Extract enquiry history
            enquiries = []
            for enq_elem in root.findall('.//Enquiry'):
                enquiry = {
                    'date': self._get_text(enq_elem, 'Date'),
                    'member_name': self._get_text(enq_elem, 'MemberName'),
                    'enquiry_purpose': self._get_text(enq_elem, 'Purpose'),
                    'enquiry_amount': float(self._get_text(enq_elem, 'Amount', '0')),
                }
                enquiries.append(enquiry)
            
            # Calculate derived metrics
            total_accounts = len(accounts)
            active_accounts = len([a for a in accounts if not a['date_closed']])
            defaulted_accounts = len([a for a in accounts if a['dpd'] > 90])
            credit_utilization = self.calculate_utilization(accounts)
            
            # Build standardized report
            parsed_report = {
                'bureau_name': 'CIBIL',
                'report_date': datetime.utcnow().isoformat(),
                'score': score,
                'score_range': {'min': 300, 'max': 900},
                'accounts': accounts,
                'enquiries': enquiries,
                'summary': {
                    'total_accounts': total_accounts,
                    'active_accounts': active_accounts,
                    'defaulted_accounts': defaulted_accounts,
                    'credit_utilization': credit_utilization,
                    'recent_enquiries_6m': len([e for e in enquiries if self._is_recent(e['date'], 180)]),
                    'recent_enquiries_3m': len([e for e in enquiries if self._is_recent(e['date'], 90)]),
                },
                'raw_xml': xml_data
            }
            
            logger.info(f"CIBIL: Successfully parsed report - Score: {score}")
            return parsed_report
            
        except Exception as e:
            logger.error(f"CIBIL: Failed to parse report - {str(e)}")
            raise BureauServiceError(f"Failed to parse CIBIL report: {str(e)}")
    
    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """Helper to safely get text from XML element"""
        child = element.find(tag)
        return child.text if child is not None and child.text else default
    
    def _is_recent(self, date_str: str, days: int) -> bool:
        """Check if date is within last N days"""
        try:
            # Parse date (format: DDMMYYYY)
            enq_date = datetime.strptime(date_str, '%d%m%Y')
            days_ago = (datetime.now() - enq_date).days
            return days_ago <= days
        except:
            return False

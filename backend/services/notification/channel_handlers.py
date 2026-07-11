"""
Channel Handlers for Multi-Channel Notification Delivery

Implements channel-specific logic for SMS, Email, WhatsApp, and Push notifications.
Each handler is responsible for formatting and sending via the appropriate provider.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import httpx
import json

logger = logging.getLogger(__name__)


class BaseChannelHandler(ABC):
    """Base class for all channel handlers"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        """
        Initialize channel handler with provider configuration
        
        Args:
            provider_config: Provider-specific configuration
        """
        self.provider_config = provider_config
        self.provider_type = provider_config.get("provider_type")
        self.api_key = provider_config.get("api_key")
        self.api_secret = provider_config.get("api_secret")
        self.api_endpoint = provider_config.get("api_endpoint")
        self.additional_config = provider_config.get("additional_config", {})
    
    @abstractmethod
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification via this channel
        
        Args:
            recipient: Recipient contact (phone/email)
            content: Notification content/body
            subject: Subject line (for email)
            metadata: Additional metadata
            
        Returns:
            Dict with provider_message_id, status, and response
        """
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format for this channel"""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common HTTP headers"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to provider API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or self._get_headers(),
                    json=data,
                    params=params
                )
                
                return {
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code,
                    "response": response.json() if response.text else {},
                    "raw_response": response.text
                }
        except httpx.TimeoutException:
            logger.error(f"Timeout calling provider API: {url}")
            return {
                "success": False,
                "error": "Request timeout",
                "status_code": 504
            }
        except Exception as e:
            logger.error(f"Error calling provider API: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 500
            }


# ============================================================================
# SMS CHANNEL HANDLERS
# ============================================================================

class TwilioSMSHandler(BaseChannelHandler):
    """Twilio SMS handler"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.account_sid = self.additional_config.get("account_sid")
        self.from_number = self.additional_config.get("from_number")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        # Basic validation - should start with + and have 10-15 digits
        import re
        return bool(re.match(r'^\+\d{10,15}$', recipient))
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        
        if not self.validate_recipient(recipient):
            return {
                "success": False,
                "error": "Invalid phone number format"
            }
        
        url = f"{self.api_endpoint}/Accounts/{self.account_sid}/Messages.json"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "To": recipient,
            "From": self.from_number,
            "Body": content
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    auth=(self.account_sid, self.api_key),
                    data=data
                )
                
                result = response.json()
                
                if response.status_code in [200, 201]:
                    return {
                        "success": True,
                        "provider_message_id": result.get("sid"),
                        "status": "sent",
                        "response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("message", "Unknown error"),
                        "response": result
                    }
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class MSG91SMSHandler(BaseChannelHandler):
    """MSG91 SMS handler (Popular in India)"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.sender_id = self.additional_config.get("sender_id", "NBFCFN")
        self.route = self.additional_config.get("route", "4")  # 4 = Transactional
        self.dlt_entity_id = self.additional_config.get("dlt_entity_id")
        self.dlt_template_id = self.additional_config.get("dlt_template_id")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate Indian mobile number"""
        import re
        # Indian mobile: +91XXXXXXXXXX or 91XXXXXXXXXX or XXXXXXXXXX (10 digits)
        return bool(re.match(r'^(\+?91)?[6-9]\d{9}$', recipient))
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send SMS via MSG91 with DLT compliance"""
        
        if not self.validate_recipient(recipient):
            return {
                "success": False,
                "error": "Invalid Indian mobile number"
            }
        
        # Clean phone number (remove +91 prefix if present)
        phone = recipient.replace("+91", "").replace("91", "")
        if len(phone) == 10:
            phone = phone  # Keep as is
        
        url = f"{self.api_endpoint}/api/v5/flow/"
        
        headers = {
            "authkey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # MSG91 Flow API payload (DLT compliant)
        data = {
            "flow_id": self.additional_config.get("flow_id"),
            "sender": self.sender_id,
            "mobiles": f"91{phone}",
            "message": content,
            "route": self.route
        }
        
        # Add DLT parameters if configured
        if self.dlt_entity_id:
            data["DLT_TE_ID"] = self.dlt_entity_id
        
        if metadata and metadata.get("dlt_template_id"):
            data["DLT_TE_ID"] = metadata.get("dlt_template_id")
        
        try:
            result = await self._make_request("POST", url, headers=headers, data=data)
            
            if result.get("success"):
                response_data = result.get("response", {})
                return {
                    "success": True,
                    "provider_message_id": response_data.get("request_id") or response_data.get("message_id"),
                    "status": "sent",
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("message", "Unknown error"),
                    "response": result.get("response")
                }
        except Exception as e:
            logger.error(f"MSG91 SMS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# EMAIL CHANNEL HANDLERS
# ============================================================================

class SendGridEmailHandler(BaseChannelHandler):
    """SendGrid email handler"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.from_email = self.additional_config.get("from_email")
        self.from_name = self.additional_config.get("from_name", "NBFC Financial Suite")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send email via SendGrid"""
        
        if not self.validate_recipient(recipient):
            return {
                "success": False,
                "error": "Invalid email address"
            }
        
        url = f"{self.api_endpoint}/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Determine if content is HTML
        content_type = "text/html" if "<html" in content.lower() or "<div" in content.lower() else "text/plain"
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": recipient}],
                    "subject": subject or "Notification"
                }
            ],
            "from": {
                "email": self.from_email,
                "name": self.from_name
            },
            "content": [
                {
                    "type": content_type,
                    "value": content
                }
            ]
        }
        
        # Add reply-to if configured
        if self.additional_config.get("reply_to"):
            data["reply_to"] = {"email": self.additional_config.get("reply_to")}
        
        try:
            result = await self._make_request("POST", url, headers=headers, data=data)
            
            if result.get("success"):
                # SendGrid returns message ID in X-Message-Id header
                return {
                    "success": True,
                    "provider_message_id": result.get("response", {}).get("message_id", "sent"),
                    "status": "sent",
                    "response": result.get("response")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("errors", [{}])[0].get("message", "Unknown error"),
                    "response": result.get("response")
                }
        except Exception as e:
            logger.error(f"SendGrid email error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class AWSSESEmailHandler(BaseChannelHandler):
    """AWS SES email handler"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.from_email = self.additional_config.get("from_email")
        self.aws_region = self.additional_config.get("aws_region", "us-east-1")
        self.aws_access_key = self.api_key
        self.aws_secret_key = self.api_secret
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send email via AWS SES"""
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid email address"
                }
            
            # Create SES client
            ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            
            # Determine content type
            if "<html" in content.lower() or "<div" in content.lower():
                body_key = "Html"
            else:
                body_key = "Text"
            
            response = ses_client.send_email(
                Source=self.from_email,
                Destination={
                    'ToAddresses': [recipient]
                },
                Message={
                    'Subject': {
                        'Data': subject or "Notification",
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        body_key: {
                            'Data': content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            return {
                "success": True,
                "provider_message_id": response.get("MessageId"),
                "status": "sent",
                "response": response
            }
            
        except ClientError as e:
            logger.error(f"AWS SES error: {e}")
            return {
                "success": False,
                "error": e.response['Error']['Message']
            }
        except ImportError:
            logger.error("boto3 not installed")
            return {
                "success": False,
                "error": "AWS SDK (boto3) not installed"
            }
        except Exception as e:
            logger.error(f"AWS SES error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# WHATSAPP CHANNEL HANDLER
# ============================================================================

class WhatsAppBusinessHandler(BaseChannelHandler):
    """WhatsApp Business API handler"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.phone_number_id = self.additional_config.get("phone_number_id")
        self.business_account_id = self.additional_config.get("business_account_id")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate WhatsApp phone number"""
        import re
        # Should be in E.164 format: +[country code][number]
        return bool(re.match(r'^\+\d{10,15}$', recipient))
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp message via Business API"""
        
        if not self.validate_recipient(recipient):
            return {
                "success": False,
                "error": "Invalid WhatsApp number (use E.164 format: +919876543210)"
            }
        
        url = f"{self.api_endpoint}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Check if using template or text message
        template_name = metadata.get("template_name") if metadata else None
        
        if template_name:
            # Template message (pre-approved)
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.replace("+", ""),
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": metadata.get("language_code", "en")
                    }
                }
            }
            
            # Add template parameters if provided
            if metadata.get("template_params"):
                data["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": param}
                            for param in metadata.get("template_params", [])
                        ]
                    }
                ]
        else:
            # Text message (requires business initiated conversation)
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.replace("+", ""),
                "type": "text",
                "text": {
                    "body": content
                }
            }
        
        try:
            result = await self._make_request("POST", url, headers=headers, data=data)
            
            if result.get("success"):
                response_data = result.get("response", {})
                messages = response_data.get("messages", [{}])
                return {
                    "success": True,
                    "provider_message_id": messages[0].get("id") if messages else None,
                    "status": "sent",
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", {}).get("message", "Unknown error"),
                    "response": result.get("response")
                }
        except Exception as e:
            logger.error(f"WhatsApp Business API error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# PUSH NOTIFICATION HANDLER
# ============================================================================

class FirebasePushHandler(BaseChannelHandler):
    """Firebase Cloud Messaging (FCM) push notification handler"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.server_key = self.api_key
        self.project_id = self.additional_config.get("project_id")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate FCM device token"""
        # Basic validation - FCM tokens are typically long alphanumeric strings
        return len(recipient) > 50 and recipient.replace(":", "").replace("-", "").isalnum()
    
    async def send(
        self,
        recipient: str,
        content: str,
        subject: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification via Firebase FCM"""
        
        if not self.validate_recipient(recipient):
            return {
                "success": False,
                "error": "Invalid FCM device token"
            }
        
        url = f"{self.api_endpoint}/fcm/send"
        
        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }
        
        # Build notification payload
        notification_data = {
            "title": subject or "Notification",
            "body": content
        }
        
        # Add optional fields
        if metadata:
            if metadata.get("image_url"):
                notification_data["image"] = metadata.get("image_url")
            if metadata.get("icon_url"):
                notification_data["icon"] = metadata.get("icon_url")
            if metadata.get("click_action"):
                notification_data["click_action"] = metadata.get("click_action")
        
        data = {
            "to": recipient,
            "notification": notification_data,
            "priority": "high"
        }
        
        # Add custom data payload if provided
        if metadata and metadata.get("custom_data"):
            data["data"] = metadata.get("custom_data")
        
        try:
            result = await self._make_request("POST", url, headers=headers, data=data)
            
            if result.get("success"):
                response_data = result.get("response", {})
                return {
                    "success": response_data.get("success", 0) > 0,
                    "provider_message_id": response_data.get("results", [{}])[0].get("message_id"),
                    "status": "sent" if response_data.get("success", 0) > 0 else "failed",
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Unknown error"),
                    "response": result.get("response")
                }
        except Exception as e:
            logger.error(f"Firebase FCM error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# CHANNEL HANDLER FACTORY
# ============================================================================

class ChannelHandlerFactory:
    """Factory to create appropriate channel handler"""
    
    @staticmethod
    def create_handler(
        channel: str,
        provider_type: str,
        provider_config: Dict[str, Any]
    ) -> BaseChannelHandler:
        """
        Create channel handler based on channel and provider type
        
        Args:
            channel: Channel type (sms, email, whatsapp, push)
            provider_type: Provider type (twilio, msg91, sendgrid, etc.)
            provider_config: Provider configuration
            
        Returns:
            Appropriate channel handler instance
        """
        handlers = {
            "sms": {
                "twilio": TwilioSMSHandler,
                "msg91": MSG91SMSHandler,
            },
            "email": {
                "sendgrid": SendGridEmailHandler,
                "aws_ses": AWSSESEmailHandler,
            },
            "whatsapp": {
                "whatsapp_business": WhatsAppBusinessHandler,
            },
            "push": {
                "firebase": FirebasePushHandler,
            }
        }
        
        channel_handlers = handlers.get(channel, {})
        handler_class = channel_handlers.get(provider_type)
        
        if not handler_class:
            raise ValueError(f"No handler found for channel={channel}, provider={provider_type}")
        
        return handler_class(provider_config)

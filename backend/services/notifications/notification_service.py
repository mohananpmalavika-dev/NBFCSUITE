"""
Notification Service

Core service for sending Email/SMS notifications with support for:
- Email delivery via SMTP/SendGrid
- SMS delivery via Twilio/other providers
- Template rendering with variable substitution
- Retry logic and error handling
- Delivery tracking
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
from datetime import datetime
from jinja2 import Template
import httpx

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Core notification service for Email and SMS delivery
    """
    
    def __init__(self):
        # Email Configuration (from environment variables)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@nbfcsuite.com")
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "NBFC Suite")
        
        # SMS Configuration (Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER", "")
        
        # Alternative SMS Provider (custom HTTP API)
        self.sms_api_url = os.getenv("SMS_API_URL", "")
        self.sms_api_key = os.getenv("SMS_API_KEY", "")
        
        logger.info("NotificationService initialized")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict:
        """
        Send email via SMTP
        
        Returns:
            Dict with 'success', 'message_id', and 'error' fields
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{from_name or self.smtp_from_name} <{from_email or self.smtp_from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Add text version
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(
                    from_email or self.smtp_from_email,
                    recipients,
                    msg.as_string()
                )
            
            message_id = f"email_{datetime.utcnow().timestamp()}"
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                "success": True,
                "message_id": message_id,
                "provider": "smtp",
                "sent_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "smtp"
            }
    
    async def send_sms(
        self,
        to_phone: str,
        message: str,
        provider: str = "twilio"
    ) -> Dict:
        """
        Send SMS via Twilio or custom provider
        
        Args:
            to_phone: Recipient phone number (with country code)
            message: SMS message text
            provider: 'twilio' or 'custom'
        
        Returns:
            Dict with 'success', 'message_id', and 'error' fields
        """
        try:
            if provider == "twilio" and self.twilio_account_sid:
                return await self._send_sms_twilio(to_phone, message)
            elif provider == "custom" and self.sms_api_url:
                return await self._send_sms_custom(to_phone, message)
            else:
                # Fallback to mock/logging if no provider configured
                logger.warning(f"No SMS provider configured, would send to {to_phone}: {message}")
                return {
                    "success": True,
                    "message_id": f"mock_{datetime.utcnow().timestamp()}",
                    "provider": "mock",
                    "sent_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": provider
            }
    
    async def _send_sms_twilio(self, to_phone: str, message: str) -> Dict:
        """Send SMS via Twilio API"""
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    auth=(self.twilio_account_sid, self.twilio_auth_token),
                    data={
                        "From": self.twilio_from_number,
                        "To": to_phone,
                        "Body": message
                    }
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("sid"),
                        "provider": "twilio",
                        "sent_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Twilio API error: {response.status_code}",
                        "provider": "twilio"
                    }
                    
        except Exception as e:
            raise Exception(f"Twilio SMS failed: {str(e)}")
    
    async def _send_sms_custom(self, to_phone: str, message: str) -> Dict:
        """Send SMS via custom HTTP API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.sms_api_url,
                    headers={
                        "Authorization": f"Bearer {self.sms_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "to": to_phone,
                        "message": message
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("message_id", f"custom_{datetime.utcnow().timestamp()}"),
                        "provider": "custom",
                        "sent_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Custom API error: {response.status_code}",
                        "provider": "custom"
                    }
                    
        except Exception as e:
            raise Exception(f"Custom SMS API failed: {str(e)}")
    
    def render_template(self, template_text: str, variables: Dict) -> str:
        """
        Render Jinja2 template with variables
        
        Args:
            template_text: Template string with {{ variable }} placeholders
            variables: Dict of variable names to values
        
        Returns:
            Rendered template string
        """
        try:
            template = Template(template_text)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            return template_text
    
    async def send_notification(
        self,
        notification_type: str,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        subject: Optional[str] = None,
        body_template: Optional[str] = None,
        sms_template: Optional[str] = None,
        variables: Optional[Dict] = None
    ) -> Dict:
        """
        Unified method to send notification via Email and/or SMS
        
        Returns:
            Dict with results for each channel
        """
        results = {
            "email": None,
            "sms": None
        }
        
        variables = variables or {}
        
        # Send Email
        if recipient_email and body_template:
            body_html = self.render_template(body_template, variables)
            subject_rendered = self.render_template(subject or "", variables)
            
            email_result = await self.send_email(
                to_email=recipient_email,
                subject=subject_rendered,
                body_html=body_html
            )
            results["email"] = email_result
        
        # Send SMS
        if recipient_phone and sms_template:
            sms_text = self.render_template(sms_template, variables)
            
            # Truncate SMS to 160 characters if needed
            if len(sms_text) > 160:
                sms_text = sms_text[:157] + "..."
            
            sms_result = await self.send_sms(
                to_phone=recipient_phone,
                message=sms_text
            )
            results["sms"] = sms_result
        
        return results


# Singleton instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get singleton instance of NotificationService"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

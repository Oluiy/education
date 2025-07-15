"""
EduNerve Notification Service - Notification Providers
Handles different communication channels: SMS, WhatsApp, Email, Push, Voice
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
import aiosmtplib
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
import phonenumbers
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class NotificationProvider(ABC):
    """Abstract base class for notification providers"""
    
    @abstractmethod
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send notification to recipient"""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient format"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass

class SMSProvider(NotificationProvider):
    """SMS notification provider with multiple backend support"""
    
    def __init__(self):
        self.provider = os.getenv("SMS_PROVIDER", "twilio")
        self.setup_provider()
    
    def setup_provider(self):
        """Setup SMS provider based on configuration"""
        if self.provider == "twilio":
            self.client = TwilioClient(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        elif self.provider == "africastalking":
            self.setup_africastalking()
        elif self.provider == "infobip":
            self.setup_infobip()
    
    def setup_africastalking(self):
        """Setup Africa's Talking SMS"""
        try:
            import africastalking
            self.username = os.getenv("AFRICASTALKING_USERNAME")
            self.api_key = os.getenv("AFRICASTALKING_API_KEY")
            self.sender_id = os.getenv("AFRICASTALKING_SENDER_ID", "EduNerve")
            
            africastalking.initialize(self.username, self.api_key)
            self.sms_client = africastalking.SMS
        except ImportError:
            logger.error("africastalking library not installed")
            raise
    
    def setup_infobip(self):
        """Setup Infobip SMS"""
        self.base_url = os.getenv("INFOBIP_BASE_URL", "https://api.infobip.com")
        self.api_key = os.getenv("INFOBIP_API_KEY")
        self.sender = os.getenv("INFOBIP_SENDER", "EduNerve")
    
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS to recipient"""
        try:
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid phone number format",
                    "provider": self.provider
                }
            
            if self.provider == "twilio":
                return await self.send_twilio_sms(recipient, message, **kwargs)
            elif self.provider == "africastalking":
                return await self.send_africastalking_sms(recipient, message, **kwargs)
            elif self.provider == "infobip":
                return await self.send_infobip_sms(recipient, message, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported SMS provider: {self.provider}",
                    "provider": self.provider
                }
        
        except Exception as e:
            logger.error(f"SMS send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider
            }
    
    async def send_twilio_sms(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )
            
            return {
                "success": True,
                "provider_id": message_obj.sid,
                "status": message_obj.status,
                "provider": "twilio",
                "cost": message_obj.price,
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except TwilioException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code,
                "provider": "twilio"
            }
    
    async def send_africastalking_sms(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via Africa's Talking"""
        try:
            response = self.sms_client.send(
                message=message,
                recipients=[recipient],
                sender_id=self.sender_id
            )
            
            if response['SMSMessageData']['Recipients']:
                recipient_data = response['SMSMessageData']['Recipients'][0]
                return {
                    "success": True,
                    "provider_id": recipient_data.get('messageId'),
                    "status": recipient_data.get('status'),
                    "provider": "africastalking",
                    "cost": recipient_data.get('cost'),
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "No recipients in response",
                    "provider": "africastalking"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "africastalking"
            }
    
    async def send_infobip_sms(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via Infobip"""
        try:
            url = f"{self.base_url}/sms/2/text/advanced"
            headers = {
                "Authorization": f"App {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "from": self.sender,
                        "destinations": [{"to": recipient}],
                        "text": message
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('messages'):
                            msg_data = result['messages'][0]
                            return {
                                "success": True,
                                "provider_id": msg_data.get('messageId'),
                                "status": msg_data.get('status', {}).get('name'),
                                "provider": "infobip",
                                "sent_at": datetime.utcnow().isoformat()
                            }
                    
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "provider": "infobip"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "infobip"
            }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(recipient, None)
            return phonenumbers.is_valid_number(parsed)
        except phonenumbers.NumberParseException:
            return False
    
    def get_provider_name(self) -> str:
        return f"sms_{self.provider}"

class WhatsAppProvider(NotificationProvider):
    """WhatsApp notification provider"""
    
    def __init__(self):
        self.provider = os.getenv("WHATSAPP_PROVIDER", "twilio")
        self.setup_provider()
    
    def setup_provider(self):
        """Setup WhatsApp provider"""
        if self.provider == "twilio":
            self.client = TwilioClient(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.from_number = f"whatsapp:{os.getenv('WHATSAPP_PHONE_NUMBER')}"
        elif self.provider == "meta":
            self.setup_meta_whatsapp()
        elif self.provider == "infobip":
            self.setup_infobip_whatsapp()
    
    def setup_meta_whatsapp(self):
        """Setup Meta WhatsApp Business API"""
        self.access_token = os.getenv("META_WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("META_WHATSAPP_PHONE_NUMBER_ID")
        self.base_url = "https://graph.facebook.com/v17.0"
    
    def setup_infobip_whatsapp(self):
        """Setup Infobip WhatsApp"""
        self.base_url = os.getenv("INFOBIP_BASE_URL", "https://api.infobip.com")
        self.api_key = os.getenv("INFOBIP_API_KEY")
        self.sender = os.getenv("INFOBIP_SENDER", "EduNerve")
    
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send WhatsApp message"""
        try:
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid phone number format",
                    "provider": self.provider
                }
            
            if self.provider == "twilio":
                return await self.send_twilio_whatsapp(recipient, message, **kwargs)
            elif self.provider == "meta":
                return await self.send_meta_whatsapp(recipient, message, **kwargs)
            elif self.provider == "infobip":
                return await self.send_infobip_whatsapp(recipient, message, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported WhatsApp provider: {self.provider}",
                    "provider": self.provider
                }
        
        except Exception as e:
            logger.error(f"WhatsApp send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider
            }
    
    async def send_twilio_whatsapp(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send WhatsApp via Twilio"""
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=f"whatsapp:{recipient}"
            )
            
            return {
                "success": True,
                "provider_id": message_obj.sid,
                "status": message_obj.status,
                "provider": "twilio_whatsapp",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except TwilioException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code,
                "provider": "twilio_whatsapp"
            }
    
    async def send_meta_whatsapp(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send WhatsApp via Meta Business API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": message}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "provider_id": result.get('messages', [{}])[0].get('id'),
                            "status": "sent",
                            "provider": "meta_whatsapp",
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "provider": "meta_whatsapp"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "meta_whatsapp"
            }
    
    async def send_infobip_whatsapp(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send WhatsApp via Infobip"""
        try:
            url = f"{self.base_url}/whatsapp/1/message/text"
            headers = {
                "Authorization": f"App {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "from": self.sender,
                "to": recipient,
                "content": {
                    "text": message
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "provider_id": result.get('messageId'),
                            "status": result.get('status', {}).get('name'),
                            "provider": "infobip_whatsapp",
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "provider": "infobip_whatsapp"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "infobip_whatsapp"
            }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(recipient, None)
            return phonenumbers.is_valid_number(parsed)
        except phonenumbers.NumberParseException:
            return False
    
    def get_provider_name(self) -> str:
        return f"whatsapp_{self.provider}"

class EmailProvider(NotificationProvider):
    """Email notification provider"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
        self.smtp_use_ssl = os.getenv("SMTP_USE_SSL", "False").lower() == "true"
        self.email_from = os.getenv("EMAIL_FROM", "noreply@edunerve.com")
        self.email_from_name = os.getenv("EMAIL_FROM_NAME", "EduNerve")
    
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send email to recipient"""
        try:
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid email address",
                    "provider": "email"
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = kwargs.get('subject', 'EduNerve Notification')
            msg['From'] = f"{self.email_from_name} <{self.email_from}>"
            msg['To'] = recipient
            
            # Add text part
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML part if provided
            html_message = kwargs.get('html_message')
            if html_message:
                html_part = MIMEText(html_message, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments if provided
            attachments = kwargs.get('attachments', [])
            for attachment in attachments:
                self.add_attachment(msg, attachment)
            
            # Send email
            if self.smtp_use_ssl:
                await self.send_ssl_email(msg, recipient)
            else:
                await self.send_tls_email(msg, recipient)
            
            return {
                "success": True,
                "provider_id": f"email_{int(datetime.utcnow().timestamp())}",
                "status": "sent",
                "provider": "email",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "email"
            }
    
    async def send_tls_email(self, msg: MIMEMultipart, recipient: str):
        """Send email with TLS"""
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            start_tls=self.smtp_use_tls,
            username=self.smtp_username,
            password=self.smtp_password
        )
    
    async def send_ssl_email(self, msg: MIMEMultipart, recipient: str):
        """Send email with SSL"""
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            use_tls=True,
            username=self.smtp_username,
            password=self.smtp_password
        )
    
    def add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            msg.attach(part)
        except Exception as e:
            logger.error(f"Error adding attachment: {str(e)}")
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, recipient) is not None
    
    def get_provider_name(self) -> str:
        return "email"

class PushNotificationProvider(NotificationProvider):
    """Push notification provider using Firebase Cloud Messaging"""
    
    def __init__(self):
        self.setup_firebase()
    
    def setup_firebase(self):
        """Setup Firebase"""
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials
                firebase_admin.initialize_app()
            
            self.messaging = messaging
            self.firebase_available = True
        
        except Exception as e:
            logger.error(f"Firebase setup error: {str(e)}")
            self.firebase_available = False
    
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send push notification"""
        try:
            if not self.firebase_available:
                return {
                    "success": False,
                    "error": "Firebase not available",
                    "provider": "push"
                }
            
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid push token",
                    "provider": "push"
                }
            
            # Create message
            notification = self.messaging.Notification(
                title=kwargs.get('subject', 'EduNerve'),
                body=message
            )
            
            # Add data payload
            data = kwargs.get('data', {})
            
            # Create FCM message
            fcm_message = self.messaging.Message(
                notification=notification,
                data=data,
                token=recipient
            )
            
            # Send message
            response = self.messaging.send(fcm_message)
            
            return {
                "success": True,
                "provider_id": response,
                "status": "sent",
                "provider": "push",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Push notification error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "push"
            }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate push token format"""
        # Basic validation - FCM tokens are typically long strings
        return len(recipient) > 100
    
    def get_provider_name(self) -> str:
        return "push"

# Alias for consistency
PushProvider = PushNotificationProvider

class VoiceProvider(NotificationProvider):
    """Voice notification provider using TTS"""
    
    def __init__(self):
        self.provider = os.getenv("VOICE_PROVIDER", "twilio")
        self.setup_provider()
    
    def setup_provider(self):
        """Setup voice provider"""
        if self.provider == "twilio":
            self.client = TwilioClient(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send voice call with TTS"""
        try:
            if not self.validate_recipient(recipient):
                return {
                    "success": False,
                    "error": "Invalid phone number",
                    "provider": "voice"
                }
            
            if self.provider == "twilio":
                return await self.send_twilio_voice(recipient, message, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported voice provider: {self.provider}",
                    "provider": "voice"
                }
        
        except Exception as e:
            logger.error(f"Voice call error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "voice"
            }
    
    async def send_twilio_voice(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send voice call via Twilio"""
        try:
            # Create TwiML for voice message
            twiml = f'<Response><Say voice="alice" language="en">{message}</Say></Response>'
            
            call = self.client.calls.create(
                twiml=twiml,
                to=recipient,
                from_=self.from_number
            )
            
            return {
                "success": True,
                "provider_id": call.sid,
                "status": call.status,
                "provider": "voice_twilio",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        except TwilioException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code,
                "provider": "voice_twilio"
            }
    
    def validate_recipient(self, recipient: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(recipient, None)
            return phonenumbers.is_valid_number(parsed)
        except phonenumbers.NumberParseException:
            return False
    
    def get_provider_name(self) -> str:
        return f"voice_{self.provider}"

class NotificationProviderManager:
    """Manager for all notification providers"""
    
    def __init__(self):
        self.providers = {
            "sms": SMSProvider(),
            "whatsapp": WhatsAppProvider(),
            "email": EmailProvider(),
            "push": PushNotificationProvider(),
            "voice": VoiceProvider()
        }
    
    def get_provider(self, notification_type: str) -> Optional[NotificationProvider]:
        """Get provider for notification type"""
        return self.providers.get(notification_type)
    
    async def send_notification(
        self,
        notification_type: str,
        recipient: str,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Send notification using appropriate provider"""
        provider = self.get_provider(notification_type)
        if not provider:
            return {
                "success": False,
                "error": f"No provider for type: {notification_type}",
                "provider": notification_type
            }
        
        return await provider.send(recipient, message, **kwargs)
    
    def validate_recipient(self, notification_type: str, recipient: str) -> bool:
        """Validate recipient for notification type"""
        provider = self.get_provider(notification_type)
        if not provider:
            return False
        
        return provider.validate_recipient(recipient)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())

# Initialize global provider manager
provider_manager = NotificationProviderManager()

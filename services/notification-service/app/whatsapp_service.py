import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from .models import NotificationLog, NotificationStatus, NotificationChannel

logger = logging.getLogger(__name__)

class WhatsAppService:
    """WhatsApp integration service using Termii API"""
    
    def __init__(self, api_key: str, sender_id: str = "EduNerve"):
        self.api_key = api_key
        self.sender_id = sender_id
        self.base_url = "https://api.ng.termii.com/api"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def send_whatsapp_message(
        self, 
        phone_number: str, 
        message: str, 
        message_type: str = "text",
        template_id: Optional[str] = None,
        template_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp message via Termii API"""
        
        try:
            # Clean phone number (remove spaces, hyphens, etc.)
            clean_phone = self._clean_phone_number(phone_number)
            
            if message_type == "template" and template_id:
                return self._send_template_message(clean_phone, template_id, template_data or {})
            else:
                return self._send_text_message(clean_phone, message)
                
        except Exception as e:
            logger.error(f"WhatsApp send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    def _send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send text message via WhatsApp"""
        
        payload = {
            "to": phone_number,
            "from": self.sender_id,
            "sms": message,
            "type": "plain",
            "channel": "whatsapp",
            "api_key": self.api_key
        }
        
        response = requests.post(
            f"{self.base_url}/sms/send",
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("message_id"),
                "balance": result.get("balance"),
                "response": result
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code} - {response.text}",
                "message_id": None
            }
    
    def _send_template_message(self, phone_number: str, template_id: str, template_data: Dict) -> Dict[str, Any]:
        """Send template-based WhatsApp message"""
        
        payload = {
            "to": phone_number,
            "from": self.sender_id,
            "template_id": template_id,
            "channel": "whatsapp",
            "api_key": self.api_key,
            "data": template_data
        }
        
        response = requests.post(
            f"{self.base_url}/sms/send/template",
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("message_id"),
                "response": result
            }
        else:
            return {
                "success": False,
                "error": f"Template API Error: {response.status_code} - {response.text}",
                "message_id": None
            }
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """Clean and format phone number"""
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Ensure it starts with country code
        if not cleaned.startswith('+'):
            # Assume Nigeria if no country code
            if cleaned.startswith('0'):
                cleaned = '+234' + cleaned[1:]
            else:
                cleaned = '+234' + cleaned
        
        return cleaned
    
    def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of a message"""
        
        try:
            response = requests.get(
                f"{self.base_url}/sms/status/{message_id}",
                params={"api_key": self.api_key}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"Status API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ParentNotificationService:
    """Service for sending educational notifications to parents via WhatsApp"""
    
    def __init__(self, db: Session, whatsapp_api_key: str):
        self.db = db
        self.whatsapp = WhatsAppService(whatsapp_api_key)
    
    def send_attendance_alert(
        self, 
        parent_phone: str, 
        student_name: str, 
        date: str, 
        status: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send attendance notification to parent"""
        
        message = self._format_attendance_message(student_name, date, status, school_name)
        
        result = self.whatsapp.send_whatsapp_message(
            phone_number=parent_phone,
            message=message
        )
        
        # Log notification
        self._log_notification(
            phone_number=parent_phone,
            message_type="attendance_alert",
            content=message,
            result=result
        )
        
        return result
    
    def send_academic_update(
        self, 
        parent_phone: str, 
        student_name: str, 
        subject: str, 
        score: str,
        teacher_comment: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send academic performance update to parent"""
        
        message = self._format_academic_message(
            student_name, subject, score, teacher_comment, school_name
        )
        
        result = self.whatsapp.send_whatsapp_message(
            phone_number=parent_phone,
            message=message
        )
        
        self._log_notification(
            phone_number=parent_phone,
            message_type="academic_update",
            content=message,
            result=result
        )
        
        return result
    
    def send_fee_reminder(
        self, 
        parent_phone: str, 
        student_name: str, 
        amount: str, 
        due_date: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send fee payment reminder to parent"""
        
        message = self._format_fee_message(student_name, amount, due_date, school_name)
        
        result = self.whatsapp.send_whatsapp_message(
            phone_number=parent_phone,
            message=message
        )
        
        self._log_notification(
            phone_number=parent_phone,
            message_type="fee_reminder",
            content=message,
            result=result
        )
        
        return result
    
    def send_announcement(
        self, 
        parent_phone: str, 
        student_name: str, 
        announcement: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send school announcement to parent"""
        
        message = self._format_announcement_message(student_name, announcement, school_name)
        
        result = self.whatsapp.send_whatsapp_message(
            phone_number=parent_phone,
            message=message
        )
        
        self._log_notification(
            phone_number=parent_phone,
            message_type="announcement",
            content=message,
            result=result
        )
        
        return result
    
    def send_emergency_alert(
        self, 
        parent_phone: str, 
        student_name: str, 
        alert_message: str,
        contact_number: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send emergency alert to parent"""
        
        message = self._format_emergency_message(
            student_name, alert_message, contact_number, school_name
        )
        
        result = self.whatsapp.send_whatsapp_message(
            phone_number=parent_phone,
            message=message
        )
        
        self._log_notification(
            phone_number=parent_phone,
            message_type="emergency_alert",
            content=message,
            result=result
        )
        
        return result
    
    def bulk_send_to_parents(
        self, 
        recipients: List[Dict[str, str]], 
        message_template: str,
        message_type: str,
        school_name: str
    ) -> Dict[str, Any]:
        """Send bulk messages to multiple parents"""
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "results": []
        }
        
        for recipient in recipients:
            try:
                # Format message with recipient data
                formatted_message = message_template.format(**recipient, school_name=school_name)
                
                result = self.whatsapp.send_whatsapp_message(
                    phone_number=recipient["parent_phone"],
                    message=formatted_message
                )
                
                self._log_notification(
                    phone_number=recipient["parent_phone"],
                    message_type=message_type,
                    content=formatted_message,
                    result=result
                )
                
                if result["success"]:
                    results["success_count"] += 1
                else:
                    results["failed_count"] += 1
                
                results["results"].append({
                    "phone": recipient["parent_phone"],
                    "success": result["success"],
                    "error": result.get("error")
                })
                
            except Exception as e:
                results["failed_count"] += 1
                results["results"].append({
                    "phone": recipient.get("parent_phone", "unknown"),
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def _format_attendance_message(self, student_name: str, date: str, status: str, school_name: str) -> str:
        """Format attendance notification message"""
        if status.lower() == "absent":
            return (f"🏫 {school_name}\n\n"
                   f"Dear Parent,\n\n"
                   f"Your child {student_name} was marked ABSENT on {date}.\n\n"
                   f"If this is unexpected, please contact the school immediately.\n\n"
                   f"Thank you.")
        else:
            return (f"🏫 {school_name}\n\n"
                   f"Dear Parent,\n\n"
                   f"Your child {student_name} was present at school on {date}.\n\n"
                   f"Thank you.")
    
    def _format_academic_message(self, student_name: str, subject: str, score: str, comment: str, school_name: str) -> str:
        """Format academic update message"""
        return (f"📚 {school_name}\n\n"
               f"Dear Parent,\n\n"
               f"Academic Update for {student_name}:\n"
               f"Subject: {subject}\n"
               f"Score: {score}\n"
               f"Teacher's Comment: {comment}\n\n"
               f"Keep encouraging your child!\n\n"
               f"Thank you.")
    
    def _format_fee_message(self, student_name: str, amount: str, due_date: str, school_name: str) -> str:
        """Format fee reminder message"""
        return (f"💰 {school_name}\n\n"
               f"Dear Parent,\n\n"
               f"Fee Reminder for {student_name}:\n"
               f"Amount Due: {amount}\n"
               f"Due Date: {due_date}\n\n"
               f"Please make payment before the due date to avoid late fees.\n\n"
               f"Thank you.")
    
    def _format_announcement_message(self, student_name: str, announcement: str, school_name: str) -> str:
        """Format school announcement message"""
        return (f"📢 {school_name}\n\n"
               f"Dear Parent of {student_name},\n\n"
               f"{announcement}\n\n"
               f"Thank you.")
    
    def _format_emergency_message(self, student_name: str, alert_message: str, contact_number: str, school_name: str) -> str:
        """Format emergency alert message"""
        return (f"🚨 {school_name} - URGENT\n\n"
               f"Dear Parent,\n\n"
               f"Emergency Alert regarding {student_name}:\n\n"
               f"{alert_message}\n\n"
               f"Please contact us immediately at {contact_number}\n\n"
               f"Thank you.")
    
    def _log_notification(self, phone_number: str, message_type: str, content: str, result: Dict) -> None:
        """Log notification attempt to database"""
        
        status = NotificationStatus.SENT if result["success"] else NotificationStatus.FAILED
        
        log_entry = NotificationLog(
            phone_number=phone_number,
            message_type=message_type,
            content=content,
            channel=NotificationChannel.WHATSAPP,
            status=status,
            external_message_id=result.get("message_id"),
            error_message=result.get("error"),
            sent_at=datetime.utcnow() if result["success"] else None
        )
        
        self.db.add(log_entry)
        self.db.commit()
    
    def get_notification_history(
        self, 
        phone_number: Optional[str] = None,
        message_type: Optional[str] = None,
        days: int = 30
    ) -> List[NotificationLog]:
        """Get notification history"""
        
        query = self.db.query(NotificationLog)
        
        if phone_number:
            query = query.filter(NotificationLog.phone_number == phone_number)
        
        if message_type:
            query = query.filter(NotificationLog.message_type == message_type)
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(NotificationLog.created_at >= cutoff_date)
        
        return query.order_by(NotificationLog.created_at.desc()).all()

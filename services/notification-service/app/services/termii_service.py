"""
Termii Integration Service
SMS and WhatsApp messaging via Termii API
"""

import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TermiiConfig:
    """Termii configuration"""
    api_key: str
    sender_id: str
    api_url: str = "https://api.ng.termii.com/api"
    whatsapp_sender_id: Optional[str] = None


@dataclass
class MessageResult:
    """Message delivery result"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    cost: Optional[float] = None
    status: str = "unknown"


class TermiiService:
    """Service for Termii SMS and WhatsApp integration"""
    
    def __init__(self):
        self.config = TermiiConfig(
            api_key=os.getenv("TERMII_API_KEY", ""),
            sender_id=os.getenv("TERMII_SENDER_ID", "EduNerve"),
            whatsapp_sender_id=os.getenv("TERMII_WHATSAPP_SENDER_ID", "")
        )
        
        if not self.config.api_key:
            logger.warning("Termii API key not configured")
    
    async def send_sms(
        self,
        to: str,
        message: str,
        sender_id: Optional[str] = None,
        message_type: str = "plain"
    ) -> MessageResult:
        """
        Send SMS via Termii
        """
        try:
            if not self.config.api_key:
                return MessageResult(
                    success=False,
                    error="Termii API key not configured"
                )
            
            # Clean phone number
            phone = self._clean_phone_number(to)
            if not phone:
                return MessageResult(
                    success=False,
                    error="Invalid phone number format"
                )
            
            # Prepare request
            url = f"{self.config.api_url}/sms/send"
            
            payload = {
                "to": phone,
                "from": sender_id or self.config.sender_id,
                "sms": message,
                "type": message_type,
                "channel": "generic",
                "api_key": self.config.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("code") == "ok":
                        return MessageResult(
                            success=True,
                            message_id=result.get("message_id"),
                            status="sent",
                            cost=result.get("balance", 0)
                        )
                    else:
                        return MessageResult(
                            success=False,
                            error=result.get("message", "Unknown error"),
                            status="failed"
                        )
                else:
                    return MessageResult(
                        success=False,
                        error=f"HTTP {response.status_code}: {response.text}",
                        status="failed"
                    )
        
        except httpx.TimeoutException:
            logger.error("Termii SMS timeout")
            return MessageResult(
                success=False,
                error="Request timeout",
                status="timeout"
            )
        except Exception as e:
            logger.error(f"Termii SMS error: {e}")
            return MessageResult(
                success=False,
                error=str(e),
                status="error"
            )
    
    async def send_whatsapp(
        self,
        to: str,
        message: str,
        template_name: Optional[str] = None,
        template_params: Optional[Dict[str, str]] = None
    ) -> MessageResult:
        """
        Send WhatsApp message via Termii
        """
        try:
            if not self.config.api_key:
                return MessageResult(
                    success=False,
                    error="Termii API key not configured"
                )
            
            if not self.config.whatsapp_sender_id:
                return MessageResult(
                    success=False,
                    error="WhatsApp sender ID not configured"
                )
            
            # Clean phone number
            phone = self._clean_phone_number(to)
            if not phone:
                return MessageResult(
                    success=False,
                    error="Invalid phone number format"
                )
            
            # Prepare request
            url = f"{self.config.api_url}/whatsapp/send"
            
            payload = {
                "to": phone,
                "from": self.config.whatsapp_sender_id,
                "type": "template" if template_name else "text",
                "api_key": self.config.api_key
            }
            
            if template_name:
                payload.update({
                    "template_name": template_name,
                    "template_params": template_params or {}
                })
            else:
                payload["body"] = message
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("code") == "ok":
                        return MessageResult(
                            success=True,
                            message_id=result.get("message_id"),
                            status="sent"
                        )
                    else:
                        return MessageResult(
                            success=False,
                            error=result.get("message", "Unknown error"),
                            status="failed"
                        )
                else:
                    return MessageResult(
                        success=False,
                        error=f"HTTP {response.status_code}: {response.text}",
                        status="failed"
                    )
        
        except httpx.TimeoutException:
            logger.error("Termii WhatsApp timeout")
            return MessageResult(
                success=False,
                error="Request timeout",
                status="timeout"
            )
        except Exception as e:
            logger.error(f"Termii WhatsApp error: {e}")
            return MessageResult(
                success=False,
                error=str(e),
                status="error"
            )
    
    async def send_bulk_sms(
        self,
        recipients: List[str],
        message: str,
        sender_id: Optional[str] = None
    ) -> List[MessageResult]:
        """
        Send bulk SMS messages
        """
        results = []
        
        # Send messages in batches to avoid rate limits
        batch_size = 50
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Send each message in the batch
            for phone in batch:
                result = await self.send_sms(
                    to=phone,
                    message=message,
                    sender_id=sender_id
                )
                results.append(result)
            
            # Small delay between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(1)
        
        return results
    
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get message delivery status
        """
        try:
            url = f"{self.config.api_url}/sms/status"
            
            params = {
                "message_id": message_id,
                "api_key": self.config.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"error": str(e)}
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """
        Get Termii account balance
        """
        try:
            url = f"{self.config.api_url}/balance"
            
            params = {
                "api_key": self.config.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except Exception as e:
            logger.error(f"Balance check error: {e}")
            return {"error": str(e)}
    
    async def create_whatsapp_template(
        self,
        name: str,
        language: str,
        category: str,
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create WhatsApp message template
        """
        try:
            url = f"{self.config.api_url}/whatsapp/template"
            
            payload = {
                "name": name,
                "language": language,
                "category": category,
                "components": components,
                "api_key": self.config.api_key
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
        
        except Exception as e:
            logger.error(f"Template creation error: {e}")
            return {"error": str(e)}
    
    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """
        Clean and validate phone number
        """
        if not phone:
            return None
        
        # Remove all non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Handle Nigerian numbers
        if phone.startswith('0'):
            phone = '234' + phone[1:]  # Replace leading 0 with 234
        elif phone.startswith('234'):
            pass  # Already has country code
        elif len(phone) == 10:
            phone = '234' + phone  # Add Nigerian country code
        else:
            # Try to detect other formats
            if len(phone) < 10:
                return None
        
        # Validate length (Nigerian numbers should be 13 digits with country code)
        if len(phone) >= 10:
            return phone
        
        return None
    
    def validate_config(self) -> Dict[str, bool]:
        """
        Validate Termii configuration
        """
        return {
            "api_key_configured": bool(self.config.api_key),
            "sender_id_configured": bool(self.config.sender_id),
            "whatsapp_sender_configured": bool(self.config.whatsapp_sender_id)
        }


class ParentSummaryService:
    """Service for generating and sending weekly parent summaries"""
    
    def __init__(self, termii_service: TermiiService):
        self.termii = termii_service
    
    async def generate_summary(
        self,
        student_id: int,
        week_start: datetime,
        week_end: datetime,
        db_session: Any  # Database session
    ) -> Dict[str, Any]:
        """
        Generate weekly summary for a student
        """
        try:
            # This would integrate with other services to get data
            # For now, returning a template structure
            
            summary = {
                "student_id": student_id,
                "week_period": f"{week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}",
                "attendance": {
                    "days_present": 4,
                    "days_absent": 1,
                    "attendance_rate": "80%"
                },
                "academic_performance": {
                    "quizzes_taken": 3,
                    "average_score": 78.5,
                    "subjects_improved": ["Mathematics", "English"],
                    "subjects_needing_attention": ["Physics"]
                },
                "behavioral_notes": [
                    "Good participation in class discussions",
                    "Submitted all assignments on time"
                ],
                "upcoming_events": [
                    "Mathematics test on Monday",
                    "Parent-teacher meeting on Friday"
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {}
    
    def format_summary_message(self, summary: Dict[str, Any], student_name: str) -> str:
        """
        Format summary as SMS/WhatsApp message
        """
        try:
            message = f"📚 WEEKLY REPORT - {student_name.upper()}\n"
            message += f"Period: {summary.get('week_period', 'N/A')}\n\n"
            
            # Attendance
            attendance = summary.get('attendance', {})
            message += f"📅 ATTENDANCE\n"
            message += f"Present: {attendance.get('days_present', 0)} days\n"
            message += f"Rate: {attendance.get('attendance_rate', '0%')}\n\n"
            
            # Academic performance
            performance = summary.get('academic_performance', {})
            message += f"📊 ACADEMICS\n"
            message += f"Quizzes: {performance.get('quizzes_taken', 0)}\n"
            message += f"Average: {performance.get('average_score', 0)}%\n"
            
            improved = performance.get('subjects_improved', [])
            if improved:
                message += f"✅ Improved: {', '.join(improved)}\n"
            
            attention = performance.get('subjects_needing_attention', [])
            if attention:
                message += f"⚠️ Needs help: {', '.join(attention)}\n"
            
            message += f"\n📱 Full report: [Link to detailed report]\n"
            message += f"📞 Contact school for questions"
            
            return message[:1000]  # Limit message length
            
        except Exception as e:
            logger.error(f"Message formatting error: {e}")
            return f"Weekly report for {student_name} is ready. Contact school for details."
    
    async def send_parent_summary(
        self,
        student_id: int,
        parent_phone: str,
        summary: Dict[str, Any],
        student_name: str,
        method: str = "sms"  # "sms" or "whatsapp"
    ) -> MessageResult:
        """
        Send summary to parent via SMS or WhatsApp
        """
        try:
            message = self.format_summary_message(summary, student_name)
            
            if method == "whatsapp":
                return await self.termii.send_whatsapp(
                    to=parent_phone,
                    message=message
                )
            else:
                return await self.termii.send_sms(
                    to=parent_phone,
                    message=message,
                    sender_id="EduNerve"
                )
        
        except Exception as e:
            logger.error(f"Parent summary send error: {e}")
            return MessageResult(
                success=False,
                error=str(e),
                status="error"
            )
    
    async def send_bulk_parent_summaries(
        self,
        student_parent_list: List[Dict[str, Any]],
        week_start: datetime,
        week_end: datetime,
        method: str = "sms"
    ) -> List[MessageResult]:
        """
        Send summaries to multiple parents
        """
        results = []
        
        for item in student_parent_list:
            try:
                student_id = item["student_id"]
                student_name = item["student_name"]
                parent_phone = item["parent_phone"]
                
                # Generate summary (would use actual data)
                summary = await self.generate_summary(
                    student_id=student_id,
                    week_start=week_start,
                    week_end=week_end,
                    db_session=None
                )
                
                # Send summary
                result = await self.send_parent_summary(
                    student_id=student_id,
                    parent_phone=parent_phone,
                    summary=summary,
                    student_name=student_name,
                    method=method
                )
                
                results.append(result)
                
                # Small delay between sends
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Bulk summary error for student {item.get('student_id')}: {e}")
                results.append(MessageResult(
                    success=False,
                    error=str(e),
                    status="error"
                ))
        
        return results


# Global service instances
termii_service = TermiiService()
parent_summary_service = ParentSummaryService(termii_service)

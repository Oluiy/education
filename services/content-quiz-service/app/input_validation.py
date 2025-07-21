"""
EduNerve Content Service - Input Validation System
Comprehensive input validation and sanitization to prevent injection attacks
"""

import re
import bleach
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
from fastapi import HTTPException, status
import html
import urllib.parse
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class SecurityConfig:
    """Security configuration for input validation"""
    
    # SQL injection prevention patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|\*|\/\*|\*\/)",
        r"(\bOR\b.*\b=\b|\bAND\b.*\b=\b)",
        r"(SLEEP\(|BENCHMARK\(|WAITFOR\s+DELAY)",
        r"(xp_cmdshell|sp_executesql)",
        r"(\bSCRIPT\b|\bEVAL\b)"
    ]
    
    # XSS prevention patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"vbscript:",
        r"data:text/html"
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e%5c",
        r"~",
        r"/etc/passwd",
        r"\\windows\\system32"
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$()]",
        r"\\x[0-9a-fA-F]{2}",
        r"%[0-9a-fA-F]{2}",
        r"(cat|ls|dir|type|ping|nslookup|wget|curl)\s",
        r"(rm|del|rmdir|mkdir)\s"
    ]

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    @staticmethod
    def validate_sql_injection(value: str, field_name: str = "input") -> str:
        """Check for SQL injection patterns"""
        if not isinstance(value, str):
            return value
            
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid {field_name}: Contains potentially malicious content"
                )
        return value
    
    @staticmethod
    def validate_xss(value: str, field_name: str = "input") -> str:
        """Check for XSS patterns and sanitize"""
        if not isinstance(value, str):
            return value
            
        # Check for XSS patterns
        for pattern in SecurityConfig.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid {field_name}: Contains potentially malicious content"
                )
        
        # Sanitize HTML content
        cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)
        return html.escape(cleaned)
    
    @staticmethod
    def validate_text_field(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
        """Comprehensive text field validation"""
        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be a string"
            )
        
        # Length validation
        if len(value.strip()) < min_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must be at least {min_length} characters"
            )
        
        if len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} must not exceed {max_length} characters"
            )
        
        # Security validations
        value = InputValidator.validate_xss(value, field_name)
        value = InputValidator.validate_sql_injection(value, field_name)
        
        return value.strip()

def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize all string values in request data"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Apply basic sanitization
            value = html.escape(value)
            value = urllib.parse.unquote(value)
            
            # Security validation
            try:
                InputValidator.validate_xss(value, key)
                InputValidator.validate_sql_injection(value, key)
            except HTTPException:
                # If validation fails, reject the request
                raise
            
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            value = sanitize_request_data(value)
        elif isinstance(value, list):
            # Sanitize list items
            value = [
                sanitize_request_data(item) if isinstance(item, dict)
                else html.escape(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        
        sanitized[key] = value
    
    return sanitized

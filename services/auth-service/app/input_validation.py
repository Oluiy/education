"""
EduNerve Authentication Service - Input Validation System
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
    def validate_path_traversal(value: str, field_name: str = "input") -> str:
        """Check for path traversal attacks"""
        if not isinstance(value, str):
            return value
            
        for pattern in SecurityConfig.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid {field_name}: Contains invalid path characters"
                )
        return value
    
    @staticmethod
    def validate_command_injection(value: str, field_name: str = "input") -> str:
        """Check for command injection patterns"""
        if not isinstance(value, str):
            return value
            
        for pattern in SecurityConfig.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid {field_name}: Contains potentially dangerous characters"
                )
        return value
    
    @staticmethod
    def validate_email_secure(email: str) -> str:
        """Enhanced email validation with security checks"""
        try:
            # Basic format validation
            validated_email = validate_email(email)
            email = validated_email.email
            
            # Additional security checks
            InputValidator.validate_xss(email, "email")
            InputValidator.validate_sql_injection(email, "email")
            
            # Length validation
            if len(email) > 254:  # RFC 5321 limit
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address too long"
                )
            
            # Domain validation
            if email.count('@') != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            local, domain = email.split('@')
            
            # Local part validation
            if len(local) > 64:  # RFC 5321 limit
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email local part too long"
                )
            
            # Domain validation
            if len(domain) > 253:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email domain too long"
                )
            
            return email.lower()
            
        except EmailNotValidError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
    
    @staticmethod
    def validate_phone_secure(phone: str) -> str:
        """Enhanced phone validation with security checks"""
        if not phone:
            return phone
            
        # Security validation
        InputValidator.validate_xss(phone, "phone")
        InputValidator.validate_sql_injection(phone, "phone")
        InputValidator.validate_command_injection(phone, "phone")
        
        try:
            # Parse phone number
            if not phone.startswith('+'):
                # Nigerian number handling
                if len(phone) == 11 and phone.startswith('0'):
                    phone = '+234' + phone[1:]
                elif len(phone) == 10:
                    phone = '+234' + phone
                else:
                    phone = '+234' + phone
            
            # Validate with phonenumbers library
            parsed = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format"
                )
            
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
        except phonenumbers.NumberParseException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
    
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
        value = InputValidator.validate_command_injection(value, field_name)
        
        return value.strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> str:
        """Enhanced password strength validation"""
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        
        # Length validation
        if len(password) < 12:  # Increased minimum length
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 12 characters long"
            )
        
        if len(password) > 128:  # Maximum length for security
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must not exceed 128 characters"
            )
        
        # Complexity requirements
        requirements = []
        if not re.search(r'[a-z]', password):
            requirements.append("lowercase letter")
        if not re.search(r'[A-Z]', password):
            requirements.append("uppercase letter")
        if not re.search(r'\d', password):
            requirements.append("number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            requirements.append("special character")
        
        if requirements:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must contain at least one: {', '.join(requirements)}"
            )
        
        # Check for common passwords (basic check)
        common_passwords = [
            "password", "123456789", "qwertyuiop", "admin123", 
            "password123", "admin", "user", "guest"
        ]
        if password.lower() in common_passwords:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too common. Please choose a stronger password"
            )
        
        return password
    
    @staticmethod
    def validate_school_code(code: str) -> str:
        """Validate school code format"""
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="School code is required"
            )
        
        # Security validation
        code = InputValidator.validate_text_field(code, "school_code", 2, 20)
        
        # Format validation - only alphanumeric and hyphens
        if not re.match(r'^[A-Za-z0-9\-]+$', code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="School code can only contain letters, numbers, and hyphens"
            )
        
        return code.upper()

class SecureValidationMixin:
    """Mixin class to add security validation to Pydantic models"""
    
    @validator('*', pre=True)
    def validate_all_strings(cls, value, field):
        """Apply security validation to all string fields"""
        if isinstance(value, str) and field.name not in ['password', 'hashed_password']:
            # Basic security validation for all string fields
            InputValidator.validate_xss(value, field.name)
            InputValidator.validate_sql_injection(value, field.name)
            InputValidator.validate_path_traversal(value, field.name)
            InputValidator.validate_command_injection(value, field.name)
        
        return value

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
                InputValidator.validate_path_traversal(value, key)
                InputValidator.validate_command_injection(value, key)
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

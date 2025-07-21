"""
EduNerve Content Service - Secure Error Handling
Standardized error responses that don't leak sensitive information
"""

import logging
import traceback
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SecurityError(HTTPException):
    """Custom exception for security-related errors"""
    
    def __init__(
        self,
        detail: str = "Security validation failed",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class ErrorResponseHandler:
    """Handles standardized error responses"""
    
    # Standard error messages that don't leak information
    GENERIC_MESSAGES = {
        400: "Invalid request data",
        401: "Authentication required",
        403: "Access denied",
        404: "Resource not found",
        409: "Resource conflict",
        422: "Invalid input data",
        429: "Too many requests",
        500: "Internal server error"
    }
    
    @staticmethod
    def create_error_response(
        status_code: int,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        
        # Generate unique request ID for tracking
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Use generic message if none provided
        if not message:
            message = ErrorResponseHandler.GENERIC_MESSAGES.get(
                status_code, "An error occurred"
            )
        
        response = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add error code if provided
        if error_code:
            response["error_code"] = error_code
        
        # Add details only in development mode and if safe
        if details and logger.getEffectiveLevel() == logging.DEBUG:
            response["details"] = details
        
        return response
    
    @staticmethod
    def log_error(
        error: Exception,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> str:
        """Log error with context information"""
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Prepare log context
        context = {
            "request_id": request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add request information if available
        if request:
            context.update({
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            })
        
        # Add user context if available
        if user_id:
            context["user_id"] = user_id
        
        # Log error with full traceback
        logger.error(
            f"Request error: {error}",
            extra=context,
            exc_info=True
        )
        
        return request_id

class SecureErrorHandler:
    """Secure error handling middleware"""
    
    @staticmethod
    async def authentication_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle authentication errors securely"""
        request_id = ErrorResponseHandler.log_error(exc, request)
        
        # Always return generic authentication error
        response = ErrorResponseHandler.create_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Authentication required",
            error_code="AUTH_REQUIRED",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=response,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    async def authorization_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle authorization errors securely"""
        request_id = ErrorResponseHandler.log_error(exc, request)
        
        # Generic access denied message
        response = ErrorResponseHandler.create_error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Access denied",
            error_code="ACCESS_DENIED",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=response
        )
    
    @staticmethod
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle internal server errors securely"""
        request_id = ErrorResponseHandler.log_error(exc, request)
        
        # Never expose internal error details
        response = ErrorResponseHandler.create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response
        )

"""
EduNerve API Key Management System
Secure API key generation, validation, and management for service-to-service communication
"""

import os
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

Base = declarative_base()

class APIKeyScope(Enum):
    """API key scope levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SERVICE = "service"
    FULL_ACCESS = "full_access"

class APIKeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"

@dataclass
class APIKeyPermissions:
    """API key permissions structure"""
    scopes: List[APIKeyScope] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    ip_whitelist: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    
    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if API key has specific scope"""
        return scope in self.scopes or APIKeyScope.FULL_ACCESS in self.scopes
    
    def can_access_endpoint(self, endpoint: str) -> bool:
        """Check if API key can access endpoint"""
        if not self.endpoints:
            return True  # No restrictions
        
        return any(
            endpoint.startswith(allowed_endpoint) 
            for allowed_endpoint in self.endpoints
        )
    
    def can_access_service(self, service: str) -> bool:
        """Check if API key can access service"""
        if not self.services:
            return True  # No restrictions
            
        return service in self.services

class APIKey(Base):
    """API Key database model"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Key identification
    key_id = Column(String(32), unique=True, index=True)  # Public identifier
    key_hash = Column(String(64), unique=True)  # Hashed secret
    key_prefix = Column(String(8))  # First 8 chars for identification
    
    # Metadata
    name = Column(String(255))
    description = Column(Text, nullable=True)
    
    # Ownership
    user_id = Column(Integer, nullable=True)  # User who created the key
    service_name = Column(String(100), nullable=True)  # Service key
    
    # Permissions and access
    permissions = Column(JSON)  # Serialized APIKeyPermissions
    status = Column(String(20), default=APIKeyStatus.ACTIVE.value)
    
    # Rate limiting
    rate_limit_requests = Column(Integer, default=1000)  # Requests per hour
    rate_limit_window = Column(Integer, default=3600)  # Window in seconds
    
    # IP restrictions
    ip_whitelist = Column(JSON, nullable=True)  # List of allowed IPs
    
    # Usage tracking
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Security
    is_active = Column(Boolean, default=True)

class APIKeyManager:
    """API Key management system"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.key_length = 32
        self.secret_length = 64
    
    def generate_api_key(
        self,
        name: str,
        permissions: APIKeyPermissions,
        user_id: Optional[int] = None,
        service_name: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        description: Optional[str] = None
    ) -> Tuple[str, APIKey]:
        """
        Generate new API key
        Returns: (api_key_string, api_key_model)
        """
        
        # Generate cryptographically secure key components
        key_id = secrets.token_urlsafe(24)[:32]  # Public identifier
        key_secret = secrets.token_urlsafe(48)[:64]  # Secret part
        
        # Create full API key
        api_key_string = f"enk_{key_id}_{key_secret}"  # edunerve key format
        
        # Hash the secret for storage
        key_hash = hashlib.sha256(api_key_string.encode()).hexdigest()
        key_prefix = api_key_string[:8]
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create database record
        api_key_model = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            description=description,
            user_id=user_id,
            service_name=service_name,
            permissions=self._serialize_permissions(permissions),
            rate_limit_requests=permissions.rate_limits.get("requests", 1000),
            rate_limit_window=permissions.rate_limits.get("window", 3600),
            ip_whitelist=permissions.ip_whitelist if permissions.ip_whitelist else None,
            expires_at=expires_at
        )
        
        try:
            self.db.add(api_key_model)
            self.db.commit()
            self.db.refresh(api_key_model)
            
            logger.info(f"API key created: {name} (ID: {key_id})")
            return api_key_string, api_key_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create API key: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create API key"
            )
    
    def validate_api_key(
        self, 
        api_key: str,
        endpoint: Optional[str] = None,
        service: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[bool, Optional[APIKey], str]:
        """
        Validate API key and check permissions
        Returns: (valid, api_key_model, error_message)
        """
        
        try:
            # Parse API key format
            if not api_key.startswith("enk_"):
                return False, None, "Invalid API key format"
            
            # Hash the provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Find in database
            api_key_model = self.db.query(APIKey).filter(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            ).first()
            
            if not api_key_model:
                return False, None, "Invalid API key"
            
            # Check status
            if api_key_model.status != APIKeyStatus.ACTIVE.value:
                return False, api_key_model, f"API key is {api_key_model.status}"
            
            # Check expiration
            if api_key_model.expires_at and api_key_model.expires_at < datetime.utcnow():
                # Update status
                api_key_model.status = APIKeyStatus.EXPIRED.value
                self.db.commit()
                return False, api_key_model, "API key expired"
            
            # Check IP whitelist
            if api_key_model.ip_whitelist and client_ip:
                if client_ip not in api_key_model.ip_whitelist:
                    logger.warning(f"IP {client_ip} not in whitelist for key {api_key_model.key_id}")
                    return False, api_key_model, "IP not allowed"
            
            # Check permissions
            permissions = self._deserialize_permissions(api_key_model.permissions)
            
            if endpoint and not permissions.can_access_endpoint(endpoint):
                return False, api_key_model, "Endpoint access denied"
            
            if service and not permissions.can_access_service(service):
                return False, api_key_model, "Service access denied"
            
            # Update usage tracking
            api_key_model.last_used = datetime.utcnow()
            api_key_model.usage_count += 1
            self.db.commit()
            
            return True, api_key_model, "Valid"
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False, None, "Validation failed"
    
    def revoke_api_key(self, key_id: str, user_id: Optional[int] = None) -> bool:
        """Revoke API key"""
        try:
            query = self.db.query(APIKey).filter(APIKey.key_id == key_id)
            
            # If user_id provided, ensure user owns the key
            if user_id:
                query = query.filter(APIKey.user_id == user_id)
            
            api_key = query.first()
            
            if not api_key:
                return False
            
            api_key.status = APIKeyStatus.REVOKED.value
            api_key.revoked_at = datetime.utcnow()
            api_key.is_active = False
            
            self.db.commit()
            logger.info(f"API key revoked: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            self.db.rollback()
            return False
    
    def list_api_keys(self, user_id: Optional[int] = None, service_name: Optional[str] = None) -> List[Dict]:
        """List API keys with safe information"""
        try:
            query = self.db.query(APIKey)
            
            if user_id:
                query = query.filter(APIKey.user_id == user_id)
            
            if service_name:
                query = query.filter(APIKey.service_name == service_name)
            
            api_keys = query.all()
            
            return [
                {
                    "key_id": key.key_id,
                    "name": key.name,
                    "description": key.description,
                    "key_prefix": key.key_prefix + "...",
                    "status": key.status,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                    "usage_count": key.usage_count,
                    "rate_limit": f"{key.rate_limit_requests}/{key.rate_limit_window}s"
                }
                for key in api_keys
            ]
            
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []
    
    def _serialize_permissions(self, permissions: APIKeyPermissions) -> Dict:
        """Serialize permissions for database storage"""
        return {
            "scopes": [scope.value for scope in permissions.scopes],
            "endpoints": permissions.endpoints,
            "rate_limits": permissions.rate_limits,
            "ip_whitelist": permissions.ip_whitelist,
            "services": permissions.services
        }
    
    def _deserialize_permissions(self, permissions_data: Dict) -> APIKeyPermissions:
        """Deserialize permissions from database"""
        return APIKeyPermissions(
            scopes=[APIKeyScope(scope) for scope in permissions_data.get("scopes", [])],
            endpoints=permissions_data.get("endpoints", []),
            rate_limits=permissions_data.get("rate_limits", {}),
            ip_whitelist=permissions_data.get("ip_whitelist", []),
            services=permissions_data.get("services", [])
        )

class APIKeyAuth:
    """API Key authentication dependency"""
    
    def __init__(self, required_scope: Optional[APIKeyScope] = None):
        self.required_scope = required_scope
    
    async def __call__(
        self,
        x_api_key: Optional[str] = Header(None),
        authorization: Optional[str] = Header(None),
        request: Request = None,
        db: Session = Depends(get_db)  # Assume get_db dependency exists
    ) -> APIKey:
        """API key authentication dependency"""
        
        # Extract API key from headers
        api_key = None
        
        if x_api_key:
            api_key = x_api_key
        elif authorization and authorization.startswith("Bearer "):
            api_key = authorization[7:]  # Remove "Bearer " prefix
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate API key
        api_key_manager = APIKeyManager(db)
        client_ip = request.client.host if request and request.client else None
        endpoint = str(request.url.path) if request else None
        
        valid, api_key_model, error_message = api_key_manager.validate_api_key(
            api_key, endpoint=endpoint, client_ip=client_ip
        )
        
        if not valid:
            logger.warning(f"Invalid API key usage: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid API key: {error_message}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check required scope
        if self.required_scope:
            permissions = api_key_manager._deserialize_permissions(api_key_model.permissions)
            if not permissions.has_scope(self.required_scope):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient scope: {self.required_scope.value} required"
                )
        
        return api_key_model

# Convenience functions for common scopes
def require_api_key(scope: Optional[APIKeyScope] = None):
    """Require API key with optional scope"""
    return APIKeyAuth(scope)

def require_read_access():
    """Require read access API key"""
    return APIKeyAuth(APIKeyScope.READ_ONLY)

def require_write_access():
    """Require write access API key"""
    return APIKeyAuth(APIKeyScope.READ_WRITE)

def require_admin_access():
    """Require admin access API key"""
    return APIKeyAuth(APIKeyScope.ADMIN)

def require_service_access():
    """Require service access API key"""
    return APIKeyAuth(APIKeyScope.SERVICE)

# Pre-configured API key permissions
class DefaultPermissions:
    """Default API key permission configurations"""
    
    @staticmethod
    def read_only() -> APIKeyPermissions:
        """Read-only access permissions"""
        return APIKeyPermissions(
            scopes=[APIKeyScope.READ_ONLY],
            endpoints=["/api/v1/", "/health", "/docs"],
            rate_limits={"requests": 100, "window": 3600}
        )
    
    @staticmethod
    def read_write() -> APIKeyPermissions:
        """Read-write access permissions"""
        return APIKeyPermissions(
            scopes=[APIKeyScope.READ_ONLY, APIKeyScope.READ_WRITE],
            endpoints=["/api/v1/"],
            rate_limits={"requests": 500, "window": 3600}
        )
    
    @staticmethod
    def admin() -> APIKeyPermissions:
        """Admin access permissions"""
        return APIKeyPermissions(
            scopes=[APIKeyScope.READ_ONLY, APIKeyScope.READ_WRITE, APIKeyScope.ADMIN],
            rate_limits={"requests": 2000, "window": 3600}
        )
    
    @staticmethod
    def service_to_service(service_name: str) -> APIKeyPermissions:
        """Service-to-service communication permissions"""
        return APIKeyPermissions(
            scopes=[APIKeyScope.SERVICE],
            services=[service_name],
            rate_limits={"requests": 10000, "window": 3600}
        )
    
    @staticmethod
    def full_access() -> APIKeyPermissions:
        """Full access permissions (use with caution)"""
        return APIKeyPermissions(
            scopes=[APIKeyScope.FULL_ACCESS],
            rate_limits={"requests": 5000, "window": 3600}
        )

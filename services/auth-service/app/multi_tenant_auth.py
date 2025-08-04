from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import secrets
from typing import Optional, Dict, Any
import re

from .models import User, School, AuthSession, PasswordReset, UserRole
from .database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # Should be in environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthenticationError(Exception):
    pass

class MultiTenantAuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": "strong" if len(errors) == 0 else "weak"
        }
    
    def get_school_by_domain(self, domain: str) -> Optional[School]:
        """Get school by domain"""
        return self.db.query(School).filter(
            and_(School.domain == domain, School.is_active == True)
        ).first()
    
    def get_user_by_credentials(self, identifier: str, school_id: Optional[int] = None) -> Optional[User]:
        """Get user by email or username within school context"""
        query = self.db.query(User).filter(User.is_active == True)
        
        if school_id is not None:
            # School-scoped user lookup
            query = query.filter(User.school_id == school_id)
            query = query.filter(
                or_(User.email == identifier, User.username == identifier)
            )
        else:
            # Super admin lookup (no school constraint)
            query = query.filter(
                and_(
                    User.school_id.is_(None),
                    or_(User.email == identifier, User.username == identifier),
                    User.role == UserRole.SUPER_ADMIN.value
                )
            )
        
        return query.first()
    
    def authenticate_user(self, identifier: str, password: str, school_domain: Optional[str] = None) -> Optional[User]:
        """Authenticate user with multi-tenant support"""
        
        # Get school if domain provided
        school = None
        school_id = None
        if school_domain:
            school = self.get_school_by_domain(school_domain)
            if not school:
                raise AuthenticationError("Invalid school domain")
            school_id = school.id
        
        # Get user
        user = self.get_user_by_credentials(identifier, school_id)
        if not user:
            return None
        
        # Verify password
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def create_access_token(self, user: User, device_info: Dict = None) -> str:
        """Create JWT access token and session"""
        
        # Create session record
        token_data = {
            "user_id": user.id,
            "school_id": user.school_id,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow()
        }
        
        # Generate JWT
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Store session
        session = AuthSession(
            user_id=user.id,
            school_id=user.school_id,
            token=token,
            expires_at=token_data["exp"],
            device_info=device_info or {}
        )
        self.db.add(session)
        self.db.commit()
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if session exists and is active
            session = self.db.query(AuthSession).filter(
                and_(
                    AuthSession.token == token,
                    AuthSession.is_active == True,
                    AuthSession.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not session:
                return None
            
            return payload
            
        except jwt.PyJWTError:
            return None
    
    def logout_user(self, token: str) -> bool:
        """Logout user by deactivating session"""
        session = self.db.query(AuthSession).filter(AuthSession.token == token).first()
        if session:
            session.is_active = False
            self.db.commit()
            return True
        return False
    
    def register_user(self, user_data: Dict, school_domain: Optional[str] = None) -> User:
        """Register new user with multi-tenant support"""
        
        # Validate password
        password_validation = self.validate_password_strength(user_data["password"])
        if not password_validation["is_valid"]:
            raise ValueError(f"Password validation failed: {', '.join(password_validation['errors'])}")
        
        # Get school
        school = None
        school_id = None
        if school_domain:
            school = self.get_school_by_domain(school_domain)
            if not school:
                raise ValueError("Invalid school domain")
            school_id = school.id
        
        # Check if user already exists
        existing_user = self.get_user_by_credentials(user_data["email"], school_id)
        if existing_user:
            raise ValueError("User already exists")
        
        # Check username uniqueness within school
        if school_id:
            existing_username = self.db.query(User).filter(
                and_(
                    User.school_id == school_id,
                    User.username == user_data["username"]
                )
            ).first()
            if existing_username:
                raise ValueError("Username already taken in this school")
        
        # Create user
        hashed_password = self.get_password_hash(user_data["password"])
        
        user = User(
            school_id=school_id,
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            phone_number=user_data.get("phone_number"),
            role=user_data.get("role", UserRole.STUDENT.value),
            profile_data=user_data.get("profile_data", {})
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user = self.db.query(User).filter(User.id == payload["user_id"]).first()
        return user
    
    def reset_password_request(self, email: str, school_domain: Optional[str] = None) -> str:
        """Create password reset request"""
        
        # Get school
        school_id = None
        if school_domain:
            school = self.get_school_by_domain(school_domain)
            if not school:
                raise ValueError("Invalid school domain")
            school_id = school.id
        
        # Get user
        user = self.get_user_by_credentials(email, school_id)
        if not user:
            raise ValueError("User not found")
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset request
        reset_request = PasswordReset(
            user_id=user.id,
            reset_token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        self.db.add(reset_request)
        self.db.commit()
        
        return reset_token
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password using token"""
        
        # Validate password
        password_validation = self.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            raise ValueError(f"Password validation failed: {', '.join(password_validation['errors'])}")
        
        # Get reset request
        reset_request = self.db.query(PasswordReset).filter(
            and_(
                PasswordReset.reset_token == reset_token,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not reset_request:
            return False
        
        # Get user and update password
        user = self.db.query(User).filter(User.id == reset_request.user_id).first()
        if not user:
            return False
        
        user.hashed_password = self.get_password_hash(new_password)
        reset_request.is_used = True
        
        self.db.commit()
        return True

"""
User model and authentication for Nova Prompt Optimizer
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

from .database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANNOTATOR = "annotator"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic user information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Nullable for SSO users
    
    # Authorization
    role = Column(String(20), default=UserRole.VIEWER.value, nullable=False)
    permissions = Column(JSON, default=list)  # Additional permissions
    
    # Status and metadata
    status = Column(String(20), default=UserStatus.ACTIVE.value, nullable=False)
    is_verified = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON, default=dict)  # User preferences and settings
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Session management
    session_token = Column(String(255), nullable=True, index=True)
    session_expires = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
    
    def set_password(self, password: str):
        """Hash and set user password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Admin has all permissions
        if self.role == UserRole.ADMIN.value:
            return True
        
        # Check role-based permissions
        role_permissions = get_role_permissions(self.role)
        if permission in role_permissions:
            return True
        
        # Check additional permissions
        return permission in (self.permissions or [])
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a specific feature"""
        feature_permissions = {
            "prompt_management": ["prompt.create", "prompt.edit", "prompt.view"],
            "annotation": ["annotation.create", "annotation.view"],
            "optimization": ["optimization.run", "optimization.view"],
            "admin": ["admin.users", "admin.settings"]
        }
        
        required_permissions = feature_permissions.get(feature, [])
        return any(self.has_permission(perm) for perm in required_permissions)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def create_session(self, expires_in_hours: int = 24) -> str:
        """Create a new session token"""
        self.session_token = str(uuid.uuid4())
        self.session_expires = datetime.utcnow() + timedelta(hours=expires_in_hours)
        self.last_login = datetime.utcnow()
        return self.session_token
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not self.session_token or not self.session_expires:
            return False
        return datetime.utcnow() < self.session_expires
    
    def invalidate_session(self):
        """Invalidate current session"""
        self.session_token = None
        self.session_expires = None
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "is_verified": self.is_verified,
            "preferences": self.preferences or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
        
        if include_sensitive:
            data.update({
                "permissions": self.permissions or [],
                "session_expires": self.session_expires.isoformat() if self.session_expires else None
            })
        
        return data


class UserSession(Base):
    """User session tracking for analytics and security"""
    
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    session_token = Column(String(255), nullable=False, index=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    logout_reason = Column(String(50), nullable=True)  # manual, timeout, forced
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours: int = 24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_accessed = datetime.utcnow()


def get_role_permissions(role: str) -> List[str]:
    """Get permissions for a specific role"""
    role_permissions = {
        UserRole.ADMIN.value: [
            "admin.users", "admin.settings", "admin.system",
            "prompt.create", "prompt.edit", "prompt.delete", "prompt.view",
            "annotation.create", "annotation.edit", "annotation.delete", "annotation.view",
            "optimization.run", "optimization.view", "optimization.manage",
            "dataset.upload", "dataset.edit", "dataset.delete", "dataset.view",
            "results.view", "results.export", "results.delete"
        ],
        UserRole.MANAGER.value: [
            "prompt.create", "prompt.edit", "prompt.view",
            "annotation.create", "annotation.view", "annotation.manage",
            "optimization.run", "optimization.view",
            "dataset.upload", "dataset.edit", "dataset.view",
            "results.view", "results.export"
        ],
        UserRole.ANNOTATOR.value: [
            "prompt.view",
            "annotation.create", "annotation.view",
            "dataset.view",
            "results.view"
        ],
        UserRole.VIEWER.value: [
            "prompt.view",
            "annotation.view",
            "dataset.view",
            "results.view"
        ]
    }
    
    return role_permissions.get(role, [])


# Authentication helper functions
async def create_user_session(request, username: str, password: str = None) -> Optional[User]:
    """Create user session after authentication"""
    from .database import get_async_db
    from sqlalchemy import select
    
    async with get_async_db() as db:
        # Find user
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user for demo purposes (remove in production)
            user = User(
                username=username,
                full_name=username.title(),
                role=UserRole.MANAGER.value,
                status=UserStatus.ACTIVE.value,
                is_verified=True
            )
            if password:
                user.set_password(password)
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Create session
        session_token = user.create_session()
        user.update_activity()
        
        # Store in request session
        request.session["user_id"] = user.id
        request.session["session_token"] = session_token
        request.session["username"] = user.username
        request.session["role"] = user.role
        
        await db.commit()
        return user


async def get_user_from_session(request) -> Optional[User]:
    """Get user from session"""
    from .database import get_async_db
    from sqlalchemy import select
    
    user_id = request.session.get("user_id")
    session_token = request.session.get("session_token")
    
    if not user_id or not session_token:
        return None
    
    async with get_async_db() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or user.session_token != session_token or not user.is_session_valid():
            return None
        
        # Update activity
        user.update_activity()
        await db.commit()
        
        return user


def create_default_admin():
    """Create default admin user (for initial setup)"""
    from .database import SessionLocal
    
    with SessionLocal() as db:
        # Check if admin exists
        admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if admin:
            return admin
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            role=UserRole.ADMIN.value,
            status=UserStatus.ACTIVE.value,
            is_verified=True
        )
        admin.set_password("admin123")  # Change in production!
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        return admin

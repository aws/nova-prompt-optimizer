"""
Prompt management models for Nova Prompt Optimizer
"""

import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class PromptStatus(str, Enum):
    """Prompt status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    OPTIMIZING = "optimizing"
    OPTIMIZED = "optimized"


class PromptType(str, Enum):
    """Prompt type enumeration"""
    SYSTEM = "system"
    USER = "user"
    COMBINED = "combined"
    TEMPLATE = "template"


class OptimizationStatus(str, Enum):
    """Optimization status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Prompt(Base):
    """Main prompt model"""
    
    __tablename__ = "prompts"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Prompt content
    system_prompt = Column(Text, nullable=True)
    user_prompt = Column(Text, nullable=True)
    variables = Column(JSON, default=list)  # List of variable names
    
    # Metadata
    prompt_type = Column(String(20), default=PromptType.COMBINED.value)
    status = Column(String(20), default=PromptStatus.DRAFT.value)
    tags = Column(JSON, default=list)  # List of tags for categorization
    
    # Ownership and collaboration
    created_by = Column(String, nullable=False)  # User ID
    updated_by = Column(String, nullable=True)   # User ID
    collaborators = Column(JSON, default=list)   # List of user IDs with access
    
    # Version control
    version = Column(Integer, default=1)
    parent_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    is_latest = Column(Boolean, default=True)
    
    # Performance metrics (from optimization)
    performance_score = Column(Float, nullable=True)
    optimization_metrics = Column(JSON, nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    versions = relationship("Prompt", backref="parent", remote_side=[id])
    optimizations = relationship("OptimizationRun", back_populates="prompt", foreign_keys="OptimizationRun.prompt_id")
    
    def __repr__(self):
        return f"<Prompt(id={self.id}, name={self.name}, version={self.version})>"
    
    def get_full_prompt(self, variables: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get full prompt with variable substitution"""
        result = {}
        
        if self.system_prompt:
            system = self.system_prompt
            if variables:
                for var, value in variables.items():
                    system = system.replace(f"{{{{{var}}}}}", str(value))
            result["system"] = system
        
        if self.user_prompt:
            user = self.user_prompt
            if variables:
                for var, value in variables.items():
                    user = user.replace(f"{{{{{var}}}}}", str(value))
            result["user"] = user
        
        return result
    
    def extract_variables(self) -> List[str]:
        """Extract variable names from prompt content"""
        import re
        variables = set()
        
        # Extract from system prompt
        if self.system_prompt:
            variables.update(re.findall(r'\{\{(\w+)\}\}', self.system_prompt))
        
        # Extract from user prompt
        if self.user_prompt:
            variables.update(re.findall(r'\{\{(\w+)\}\}', self.user_prompt))
        
        return list(variables)
    
    def create_version(self, updated_by: str) -> "Prompt":
        """Create a new version of this prompt"""
        new_version = Prompt(
            name=self.name,
            description=self.description,
            system_prompt=self.system_prompt,
            user_prompt=self.user_prompt,
            variables=self.variables,
            prompt_type=self.prompt_type,
            status=PromptStatus.DRAFT.value,
            tags=self.tags,
            created_by=self.created_by,
            updated_by=updated_by,
            collaborators=self.collaborators,
            version=self.version + 1,
            parent_id=self.id,
            is_latest=True
        )
        
        # Mark current version as not latest
        self.is_latest = False
        
        return new_version
    
    def add_collaborator(self, user_id: str):
        """Add a collaborator to the prompt"""
        if not self.collaborators:
            self.collaborators = []
        if user_id not in self.collaborators:
            self.collaborators.append(user_id)
    
    def remove_collaborator(self, user_id: str):
        """Remove a collaborator from the prompt"""
        if self.collaborators and user_id in self.collaborators:
            self.collaborators.remove(user_id)
    
    def can_edit(self, user_id: str, user_role: str = None) -> bool:
        """Check if user can edit this prompt"""
        # Creator can always edit
        if self.created_by == user_id:
            return True
        
        # Admin can always edit
        if user_role == "admin":
            return True
        
        # Collaborators can edit
        if self.collaborators and user_id in self.collaborators:
            return True
        
        return False
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def to_dict(self, include_content: bool = True) -> Dict[str, Any]:
        """Convert prompt to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "prompt_type": self.prompt_type,
            "status": self.status,
            "tags": self.tags or [],
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "collaborators": self.collaborators or [],
            "version": self.version,
            "parent_id": self.parent_id,
            "is_latest": self.is_latest,
            "performance_score": self.performance_score,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
        
        if include_content:
            data.update({
                "system_prompt": self.system_prompt,
                "user_prompt": self.user_prompt,
                "variables": self.variables or [],
                "optimization_metrics": self.optimization_metrics
            })
        
        return data


class PromptTemplate(Base):
    """Prompt template for reusable prompt patterns"""
    
    __tablename__ = "prompt_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Template information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Template content
    system_template = Column(Text, nullable=True)
    user_template = Column(Text, nullable=True)
    default_variables = Column(JSON, default=dict)  # Default variable values
    required_variables = Column(JSON, default=list)  # Required variable names
    
    # Metadata
    is_public = Column(Boolean, default=False)
    created_by = Column(String, nullable=False)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, name={self.name}, category={self.category})>"
    
    def create_prompt(self, name: str, created_by: str, variables: Optional[Dict[str, str]] = None) -> Prompt:
        """Create a prompt from this template"""
        # Merge default variables with provided variables
        merged_variables = self.default_variables.copy() if self.default_variables else {}
        if variables:
            merged_variables.update(variables)
        
        # Substitute variables in templates
        system_prompt = self.system_template
        user_prompt = self.user_template
        
        if system_prompt and merged_variables:
            for var, value in merged_variables.items():
                system_prompt = system_prompt.replace(f"{{{{{var}}}}}", str(value))
        
        if user_prompt and merged_variables:
            for var, value in merged_variables.items():
                user_prompt = user_prompt.replace(f"{{{{{var}}}}}", str(value))
        
        # Create prompt
        prompt = Prompt(
            name=name,
            description=f"Created from template: {self.name}",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            variables=list(merged_variables.keys()),
            prompt_type=PromptType.COMBINED.value,
            status=PromptStatus.DRAFT.value,
            created_by=created_by
        )
        
        # Increment template usage
        self.usage_count += 1
        
        return prompt


class OptimizationRun(Base):
    """Optimization run tracking"""
    
    __tablename__ = "optimization_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    prompt_id = Column(String, ForeignKey("prompts.id"), nullable=False)
    dataset_id = Column(String, nullable=True)  # Reference to dataset
    
    # Configuration
    optimization_mode = Column(String(20), nullable=False)  # lite, pro, premier
    model_id = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=True)  # Optimization parameters
    
    # Status and progress
    status = Column(String(20), default=OptimizationStatus.PENDING.value)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    current_step = Column(String(100), nullable=True)
    
    # Results
    original_score = Column(Float, nullable=True)
    optimized_score = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    optimized_prompt_id = Column(String, ForeignKey("prompts.id"), nullable=True)
    
    # Execution details
    started_by = Column(String, nullable=False)  # User ID
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metrics and logs
    execution_logs = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prompt = relationship("Prompt", foreign_keys=[prompt_id], back_populates="optimizations")
    optimized_prompt = relationship("Prompt", foreign_keys=[optimized_prompt_id])
    
    def __repr__(self):
        return f"<OptimizationRun(id={self.id}, status={self.status}, progress={self.progress})>"
    
    def update_progress(self, progress: float, step: str = None):
        """Update optimization progress"""
        self.progress = max(0.0, min(1.0, progress))
        if step:
            self.current_step = step
        self.updated_at = datetime.utcnow()
    
    def mark_started(self):
        """Mark optimization as started"""
        self.status = OptimizationStatus.RUNNING.value
        self.started_at = datetime.utcnow()
        self.progress = 0.0
    
    def mark_completed(self, optimized_prompt_id: str = None):
        """Mark optimization as completed"""
        self.status = OptimizationStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        if optimized_prompt_id:
            self.optimized_prompt_id = optimized_prompt_id
    
    def mark_failed(self, error_message: str):
        """Mark optimization as failed"""
        self.status = OptimizationStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def calculate_improvement(self):
        """Calculate improvement percentage"""
        if self.original_score and self.optimized_score:
            self.improvement = ((self.optimized_score - self.original_score) / self.original_score) * 100
    
    def get_duration(self) -> Optional[float]:
        """Get optimization duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert optimization run to dictionary"""
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "dataset_id": self.dataset_id,
            "optimization_mode": self.optimization_mode,
            "model_id": self.model_id,
            "parameters": self.parameters,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "original_score": self.original_score,
            "optimized_score": self.optimized_score,
            "improvement": self.improvement,
            "optimized_prompt_id": self.optimized_prompt_id,
            "started_by": self.started_by,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.get_duration(),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

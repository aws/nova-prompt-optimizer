"""
Configuration settings for Nova Prompt Optimizer Frontend
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    """Application configuration settings"""
    
    # Application settings
    APP_NAME: str = "Nova Prompt Optimizer"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Server settings
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Database settings
    DATABASE_URL: str = Field(default="sqlite:///nova_optimizer.db", env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Session settings
    SESSION_MAX_AGE: int = Field(default=86400, env="SESSION_MAX_AGE")  # 24 hours
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # AWS settings for Nova SDK integration
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Nova model settings
    DEFAULT_NOVA_MODEL: str = Field(default="us.amazon.nova-pro-v1:0", env="DEFAULT_NOVA_MODEL")
    NOVA_RATE_LIMIT: int = Field(default=2, env="NOVA_RATE_LIMIT")  # TPS
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 50MB
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["csv", "json", "jsonl", "txt"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # Optimization settings
    MAX_OPTIMIZATION_TIME: int = Field(default=3600, env="MAX_OPTIMIZATION_TIME")  # 1 hour
    DEFAULT_OPTIMIZATION_MODE: str = Field(default="pro", env="DEFAULT_OPTIMIZATION_MODE")
    
    # Annotation settings
    MAX_ANNOTATORS_PER_ITEM: int = Field(default=3, env="MAX_ANNOTATORS_PER_ITEM")
    ANNOTATION_TIMEOUT: int = Field(default=1800, env="ANNOTATION_TIMEOUT")  # 30 minutes
    
    # Real-time features
    WEBSOCKET_TIMEOUT: int = Field(default=300, env="WEBSOCKET_TIMEOUT")  # 5 minutes
    SSE_HEARTBEAT_INTERVAL: int = Field(default=30, env="SSE_HEARTBEAT_INTERVAL")  # 30 seconds
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Cache settings
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    
    # Feature flags
    ENABLE_COLLABORATION: bool = Field(default=True, env="ENABLE_COLLABORATION")
    ENABLE_ANNOTATIONS: bool = Field(default=True, env="ENABLE_ANNOTATIONS")
    ENABLE_ADVANCED_CHARTS: bool = Field(default=True, env="ENABLE_ADVANCED_CHARTS")
    ENABLE_PROMPT_VERSIONING: bool = Field(default=True, env="ENABLE_PROMPT_VERSIONING")
    
    # Security settings
    ENABLE_CSRF_PROTECTION: bool = Field(default=True, env="ENABLE_CSRF_PROTECTION")
    SECURE_COOKIES: bool = Field(default=False, env="SECURE_COOKIES")  # Set to True in production with HTTPS
    
    # Performance settings
    ENABLE_COMPRESSION: bool = Field(default=True, env="ENABLE_COMPRESSION")
    STATIC_FILE_MAX_AGE: int = Field(default=86400, env="STATIC_FILE_MAX_AGE")  # 24 hours
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Nova model configurations
NOVA_MODELS = {
    "nova-micro": {
        "id": "us.amazon.nova-micro-v1:0",
        "name": "Nova Micro",
        "description": "Fastest and most cost-effective model",
        "max_tokens": 8192,
        "rate_limit": 10
    },
    "nova-lite": {
        "id": "us.amazon.nova-lite-v1:0", 
        "name": "Nova Lite",
        "description": "Balanced performance and cost",
        "max_tokens": 32768,
        "rate_limit": 5
    },
    "nova-pro": {
        "id": "us.amazon.nova-pro-v1:0",
        "name": "Nova Pro", 
        "description": "High performance for complex tasks",
        "max_tokens": 32768,
        "rate_limit": 2
    },
    "nova-premier": {
        "id": "us.amazon.nova-premier-v1:0",
        "name": "Nova Premier",
        "description": "Highest capability model",
        "max_tokens": 32768,
        "rate_limit": 1
    }
}

# Optimization mode configurations
OPTIMIZATION_MODES = {
    "micro": {
        "task_model": "us.amazon.nova-micro-v1:0",
        "num_candidates": 5,
        "num_trials": 10,
        "max_bootstrapped_demos": 3,
        "max_labeled_demos": 0,
        "timeout": 600  # 10 minutes
    },
    "lite": {
        "task_model": "us.amazon.nova-lite-v1:0",
        "num_candidates": 10,
        "num_trials": 20,
        "max_bootstrapped_demos": 5,
        "max_labeled_demos": 0,
        "timeout": 1200  # 20 minutes
    },
    "pro": {
        "task_model": "us.amazon.nova-pro-v1:0",
        "num_candidates": 20,
        "num_trials": 50,
        "max_bootstrapped_demos": 5,
        "max_labeled_demos": 0,
        "timeout": 3600  # 1 hour
    },
    "premier": {
        "task_model": "us.amazon.nova-premier-v1:0",
        "num_candidates": 30,
        "num_trials": 100,
        "max_bootstrapped_demos": 8,
        "max_labeled_demos": 2,
        "timeout": 7200  # 2 hours
    }
}

# UI Theme configurations
THEMES = {
    "light": {
        "name": "Light Theme",
        "primary_color": "#0066cc",
        "secondary_color": "#6c757d",
        "success_color": "#28a745",
        "warning_color": "#ffc107",
        "error_color": "#dc3545",
        "background_color": "#ffffff",
        "text_color": "#212529"
    },
    "dark": {
        "name": "Dark Theme", 
        "primary_color": "#0d6efd",
        "secondary_color": "#6c757d",
        "success_color": "#198754",
        "warning_color": "#fd7e14",
        "error_color": "#dc3545",
        "background_color": "#1a1a1a",
        "text_color": "#ffffff"
    }
}


@lru_cache()
def get_settings() -> Config:
    """Get cached application settings"""
    return Config()


def get_nova_model_config(model_name: str) -> dict:
    """Get configuration for a specific Nova model"""
    return NOVA_MODELS.get(model_name, NOVA_MODELS["nova-pro"])


def get_optimization_config(mode: str) -> dict:
    """Get configuration for optimization mode"""
    return OPTIMIZATION_MODES.get(mode, OPTIMIZATION_MODES["pro"])


def get_theme_config(theme_name: str) -> dict:
    """Get theme configuration"""
    return THEMES.get(theme_name, THEMES["light"])

#!/usr/bin/env python3
"""
Nova Prompt Optimizer - Simple Deployment Script

A lightweight deployment script for the simplified web interface.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, cwd=Path(__file__).parent)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Set default environment variables if not already set
    env_vars = {
        "NOVA_OPTIMIZER_ENV": "development",
        "NOVA_OPTIMIZER_HOST": "0.0.0.0",
        "NOVA_OPTIMIZER_PORT": "8000",
        "NOVA_OPTIMIZER_LOG_LEVEL": "info"
    }
    
    for key, default_value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = default_value
            print(f"  Set {key}={default_value}")
    
    # Check for AWS credentials
    aws_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]
    missing_aws = [var for var in aws_vars if var not in os.environ]
    
    if missing_aws:
        print("⚠️  AWS credentials not found in environment:")
        for var in missing_aws:
            print(f"    Missing: {var}")
        print("  The application will run in demo mode without SDK functionality")
    else:
        print("✅ AWS credentials found")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "uploads",
        "uploads/datasets",
        "uploads/prompts",
        "uploads/results"
    ]
    
    base_path = Path(__file__).parent
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    return True

def run_application(host="0.0.0.0", port=8000, reload=False):
    """Run the FastAPI application"""
    print(f"🚀 Starting Nova Prompt Optimizer on http://{host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=os.environ.get("NOVA_OPTIMIZER_LOG_LEVEL", "info")
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except ImportError:
        print("❌ uvicorn not found. Please install requirements first.")
        return False
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Deploy Nova Prompt Optimizer (Lightweight)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--check-only", action="store_true", help="Only check requirements, don't start server")
    
    args = parser.parse_args()
    
    print("🚀 Nova Prompt Optimizer - Lightweight Deployment")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not args.skip_install:
        if not install_dependencies():
            return 1
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Create directories
    if not create_directories():
        return 1
    
    if args.check_only:
        print("✅ All checks passed! Ready to deploy.")
        return 0
    
    # Run application
    if not run_application(args.host, args.port, args.reload):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

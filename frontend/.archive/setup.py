#!/usr/bin/env python3
"""
Setup script for Nova Prompt Optimizer Frontend
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Try minimal requirements first
    if run_command("pip install -r requirements-minimal.txt", "Installing minimal dependencies"):
        print("✅ Minimal dependencies installed successfully")
        
        # Wait and verify critical dependencies are available
        print("🔍 Verifying dependencies...")
        import time
        time.sleep(2)  # Give pip a moment to finish
        
        # Verify critical imports
        try:
            import sqlalchemy
            import aiosqlite
            import fasthtml
            print("✅ Core dependencies verified")
        except ImportError as e:
            print(f"⚠️  Dependency verification failed: {e}")
            print("   Retrying installation...")
            time.sleep(1)
            run_command("pip install sqlalchemy aiosqlite python-fasthtml", "Installing core dependencies individually")
        
        # Ask if user wants full dependencies
        response = input("\n🤔 Install optional dependencies (testing, development tools)? [y/N]: ")
        if response.lower() in ['y', 'yes']:
            run_command("pip install -r requirements.txt", "Installing full dependencies")
        return True
    else:
        print("❌ Failed to install minimal dependencies")
        return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_template.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(env_template, 'r') as template:
                content = template.read()
            
            with open(env_file, 'w') as env:
                env.write(content)
            
            print("✅ .env file created successfully")
            print("⚠️  Please edit .env file with your configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("📝 Creating basic .env file...")
        env_content = """# Nova Prompt Optimizer Frontend Configuration

# Application Settings
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
HOST=127.0.0.1
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///nova_optimizer.db

# AWS Configuration (optional for demo mode)
AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key

# Nova Model Settings
DEFAULT_NOVA_MODEL=us.amazon.nova-pro-v1:0
NOVA_RATE_LIMIT=2

# Feature Flags
ENABLE_COLLABORATION=true
ENABLE_ANNOTATIONS=true
ENABLE_ADVANCED_CHARTS=true
"""
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Basic .env file created")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

async def init_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    
    # Wait for dependencies to be fully available
    import time
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Check if required modules are available
            import sqlalchemy
            import aiosqlite
            print("✅ Database dependencies verified")
            
            # Small delay to ensure modules are fully loaded
            time.sleep(1)
            
            # Now try to import and initialize
            from models.database import init_database
            await init_database()
            print("✅ Database initialized successfully")
            return True
            
        except ImportError as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for dependencies to be available... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                print(f"⚠️  Database initialization skipped: Missing dependency ({e})")
                print("   Run this command after setup completes:")
                print("   python init_db.py")
                return False
                
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("   You can initialize it later by running:")
            print("   python init_db.py")
            return False
    
    return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "logs",
        "static/assets",
        "templates/email"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")
    return True

def main():
    """Main setup function"""
    print("🚀 Nova Prompt Optimizer Frontend Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Setup failed during .env file creation")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed during directory creation")
        sys.exit(1)
    
    # Initialize database
    try:
        db_success = asyncio.run(init_database())
        if not db_success:
            print("   💡 Complete database setup by running: python init_db.py")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}")
        print("   You can initialize it later by running:")
        print("   python -c \"import asyncio; from models.database import init_database; asyncio.run(init_database())\"")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Edit .env file with your AWS credentials (optional)")
    print("   2. Run the application: python app.py --reload")
    print("   3. Open http://localhost:8000 in your browser")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()

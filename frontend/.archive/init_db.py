#!/usr/bin/env python3
"""
Database initialization script for Nova Prompt Optimizer Frontend
"""

import asyncio
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import sqlalchemy
        import aiosqlite
        print("✅ Database dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Please install dependencies first:")
        print("   pip install -r requirements-minimal.txt")
        return False

async def initialize_database():
    """Initialize the database with tables"""
    try:
        from models.database import init_database
        await init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_default_admin():
    """Create default admin user"""
    try:
        from models.user import create_default_admin
        admin = create_default_admin()
        print(f"✅ Default admin user created: {admin.username}")
        print("   Default password: admin123 (change this in production!)")
        return True
    except Exception as e:
        print(f"⚠️  Admin user creation failed: {e}")
        return False

async def main():
    """Main initialization function"""
    print("🗄️  Nova Prompt Optimizer - Database Initialization")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Creating basic .env file...")
        
        env_content = """# Basic configuration for database initialization
DEBUG=true
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///nova_optimizer.db
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Basic .env file created")
    
    # Initialize database
    success = await initialize_database()
    if not success:
        sys.exit(1)
    
    # Create default admin user
    create_default_admin()
    
    print("\n🎉 Database initialization completed!")
    print("\n📋 Next steps:")
    print("   1. Start the application: python app.py --reload")
    print("   2. Login with username: admin, password: admin123")
    print("   3. Change the default password in the user settings")

if __name__ == "__main__":
    asyncio.run(main())

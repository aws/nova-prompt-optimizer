#!/usr/bin/env python3
"""
Nova Prompt Optimizer Frontend Setup Script
Ensures clean installation and proper initialization
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create required directories"""
    dirs = ['data', 'uploads', 'optimized_prompts']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Directory created: {dir_name}/")
    
    # Verify directories were created
    for dir_name in dirs:
        if not Path(dir_name).exists():
            print(f"❌ Failed to create directory: {dir_name}")
            return False
    return True

def install_dependencies():
    """Install required Python packages"""
    requirements = [
        'python-fasthtml',
        'starlette', 
        'python-multipart',
        'boto3',
        'pydantic_settings',
        'nova-prompt-optimizer'
    ]
    
    print("📦 Installing dependencies...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ Installed: {req}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install: {req}")
            return False
    return True

def initialize_database():
    """Initialize database with proper schema and sample data"""
    print("🗄️ Initializing database...")
    
    # Remove existing database to ensure clean state
    db_path = Path("nova_optimizer.db")
    if db_path.exists():
        db_path.unlink()
        print("🧹 Removed existing database")
    
    # Import and initialize database
    try:
        from database import Database
        db = Database()
        print("✅ Database initialized with schema")
        
        # Verify critical data exists
        metrics = db.get_metrics()
        datasets = db.get_datasets()
        prompts = db.get_prompts()
        
        print(f"✅ Sample data loaded: {len(datasets)} datasets, {len(prompts)} prompts, {len(metrics)} metrics")
        
        # Ensure at least one working metric exists
        if not metrics:
            print("⚠️ No metrics found, creating default metric...")
            create_default_metric(db)
            
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_default_metric(db):
    """Create a default working metric"""
    default_metric = {
        'id': 'accuracy_metric_default',
        'name': 'Accuracy Score',
        'description': 'Basic accuracy evaluation metric',
        'code': '''
class AccuracyMetric(MetricAdapter):
    def apply(self, y_pred, y_true):
        try:
            import json
            import re
            
            # Parse JSON from prediction if needed
            if isinstance(y_pred, str):
                json_match = re.search(r'\\{.*\\}', y_pred)
                if json_match:
                    try:
                        pred_data = json.loads(json_match.group())
                        y_pred = pred_data.get('answer', y_pred)
                    except:
                        pass
            
            # Simple string comparison
            pred_str = str(y_pred).strip().lower()
            true_str = str(y_true).strip().lower()
            
            # Exact match
            if pred_str == true_str:
                return 1.0
            
            # Partial match
            if pred_str in true_str or true_str in pred_str:
                return 0.7
            
            # No match
            return 0.0
            
        except Exception as e:
            print(f"Metric evaluation error: {e}")
            return 0.0
''',
        'created': '2024-01-01'
    }
    
    db.add_metric(
        default_metric['id'],
        default_metric['name'], 
        default_metric['description'],
        default_metric['code'],
        default_metric['created']
    )
    print("✅ Default metric created")

def validate_installation():
    """Validate that everything is working"""
    print("🔍 Validating installation...")
    
    # Check imports
    try:
        import fasthtml
        import starlette
        import boto3
        print("✅ Core dependencies importable")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check Nova SDK
    try:
        from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
        print("✅ Nova SDK available")
    except ImportError:
        print("⚠️ Nova SDK not available (demo mode will be used)")
    
    # Check database
    try:
        from database import Database
        db = Database()
        datasets = db.get_datasets()
        metrics = db.get_metrics()
        if not datasets or not metrics:
            print("❌ Database missing required data")
            return False
        print("✅ Database validation passed")
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False
    
    # Check file structure
    required_files = ['app.py', 'database.py', 'sdk_worker.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing required file: {file}")
            return False
    print("✅ File structure validation passed")
    
    return True

def main():
    """Main setup process"""
    print("🚀 Nova Prompt Optimizer Frontend Setup")
    print("=" * 50)
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Create directories
    if not create_directories():
        print("❌ Setup failed during directory creation")
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Step 4: Initialize database
    if not initialize_database():
        print("❌ Setup failed during database initialization")
        sys.exit(1)
    
    # Step 5: Validate installation
    if not validate_installation():
        print("❌ Setup failed validation")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure AWS credentials (aws configure)")
    print("2. Request Nova model access in AWS Bedrock console")
    print("3. Run: python3 app.py")
    print("4. Open: http://localhost:8000")

if __name__ == "__main__":
    main()

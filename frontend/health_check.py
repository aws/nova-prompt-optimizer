#!/usr/bin/env python3
"""
Health Check Script for Nova Prompt Optimizer Frontend
Validates installation and identifies issues
"""

import sys
import os
from pathlib import Path
import sqlite3

def check_file_structure():
    """Check that all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        'app.py',
        'database.py', 
        'sdk_worker.py',
        'metric_service.py',
        'prompt_templates.py',
        'simple_rate_limiter.py',
        'requirements.txt'
    ]
    
    required_dirs = [
        'components',
        'data',
        'uploads', 
        'optimized_prompts'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    print("✅ File structure complete")
    return True

def check_dependencies():
    """Check that all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fasthtml',
        'starlette',
        'boto3'
    ]
    
    optional_packages = [
        'nova-prompt-optimizer'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            if package == 'nova-prompt-optimizer':
                from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️ Missing optional packages: {', '.join(missing_optional)} (demo mode will be used)")
    
    print("✅ Dependencies satisfied")
    return True

def check_database():
    """Check database structure and data"""
    print("🔍 Checking database...")
    
    db_path = Path(__file__).parent / "nova_optimizer.db"
    if not db_path.exists():
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Check tables exist
        required_tables = ['datasets', 'prompts', 'optimizations', 'metrics']
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            print(f"❌ Missing database tables: {', '.join(missing_tables)}")
            conn.close()
            return False
        
        # Check data exists
        datasets_count = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        prompts_count = conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
        metrics_count = conn.execute("SELECT COUNT(*) FROM metrics").fetchone()[0]
        
        if datasets_count == 0:
            print("❌ No sample datasets found")
            conn.close()
            return False
            
        if prompts_count == 0:
            print("❌ No sample prompts found")
            conn.close()
            return False
            
        if metrics_count == 0:
            print("❌ No metrics found - this will cause optimization failures")
            conn.close()
            return False
        
        print(f"✅ Database valid: {datasets_count} datasets, {prompts_count} prompts, {metrics_count} metrics")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_aws_config():
    """Check AWS configuration"""
    print("🔍 Checking AWS configuration...")
    
    # Check for AWS credentials
    aws_configured = False
    
    # Method 1: Environment variables
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        aws_configured = True
        print("✅ AWS credentials found in environment variables")
    
    # Method 2: AWS credentials file
    aws_creds_path = Path.home() / '.aws' / 'credentials'
    if aws_creds_path.exists():
        aws_configured = True
        print("✅ AWS credentials file found")
    
    if not aws_configured:
        print("⚠️ No AWS credentials found - optimization will fail without proper AWS setup")
        print("   Configure with: aws configure")
        print("   Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        return False
    
    return True

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from database import Database
        print("✅ Database module imports successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from services.metric_service import MetricService
        print("✅ MetricService imports successfully")
    except Exception as e:
        print(f"❌ MetricService import failed: {e}")
        return False
    
    try:
        import app
        print("✅ Main app module imports successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    return True

def run_health_check():
    """Run complete health check"""
    print("🏥 Nova Prompt Optimizer Health Check")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies), 
        ("Database", check_database),
        ("AWS Configuration", check_aws_config),
        ("Import Tests", test_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 50)
    print("📋 Health Check Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 All checks passed! The application should run successfully.")
        print("Run: python3 app.py")
    else:
        print(f"\n⚠️ {len(results) - passed} issues found. Please fix before running the application.")
        print("Run: python3 setup.py to fix common issues")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)

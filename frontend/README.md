# Nova Prompt Optimizer - Frontend Installation Guide

A modern web interface for the Nova Prompt Optimizer SDK, built with FastHTML and SQLite for simplicity and performance.

## 📋 **Table of Contents**
- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Installation Methods](#-installation-methods)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Verification](#-verification)
- [Troubleshooting](#-troubleshooting)
- [Development Setup](#-development-setup)

## 🚀 **Quick Start**

```bash
# Clone and navigate to frontend
cd nova-prompt-optimizer/frontend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install fasthtml starlette python-multipart

# Optional: Install Nova SDK for real optimizations
pip install nova-prompt-optimizer

# Run the application
python3 app.py

# Open browser
open http://localhost:8000
```

## 📋 **Prerequisites**

### **System Requirements**
- **Python 3.8+** (Python 3.11+ recommended)
- **pip** (Python package manager)
- **4GB+ RAM** (for running optimizations)
- **1GB+ disk space** (for dependencies and data)

### **Operating System Support**
- ✅ **macOS** (10.14+)
- ✅ **Linux** (Ubuntu 18.04+, CentOS 7+)
- ✅ **Windows** (10+, WSL recommended)

### **Browser Support**
- ✅ **Chrome** (90+)
- ✅ **Firefox** (88+)
- ✅ **Safari** (14+)
- ✅ **Edge** (90+)

## 🛠️ **Installation Methods**

### **Method 1: Standard Installation (Recommended)**

#### **Step 1: Environment Setup**
```bash
# Navigate to frontend directory
cd /path/to/nova-prompt-optimizer/frontend

# Create isolated Python environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

#### **Step 2: Install Core Dependencies**
```bash
# Install required packages
pip install fasthtml starlette python-multipart

# Verify installation
python3 -c "import fasthtml; print('✅ FastHTML installed successfully')"
```

#### **Step 3: Install Nova SDK (Optional but Recommended)**
```bash
# For real prompt optimization (requires AWS credentials)
pip install nova-prompt-optimizer

# Verify SDK installation
python3 -c "from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer; print('✅ Nova SDK installed')"
```

### **Method 2: Development Installation**

#### **For Contributors and Advanced Users**
```bash
# Install with development tools
pip install fasthtml starlette python-multipart
pip install nova-prompt-optimizer

# Install optional development tools
pip install pytest black flake8 isort

# Verify development setup
python3 -c "import fasthtml, pytest, black; print('✅ Development environment ready')"
```

### **Method 3: Minimal Installation**

#### **For Demo/Testing Only**
```bash
# Minimal dependencies (no Nova SDK)
pip install fasthtml starlette python-multipart

# Note: Optimizations will run in demo mode
echo "⚠️ Demo mode: Install nova-prompt-optimizer for real optimizations"
```

## ⚙️ **Configuration**

### **Default Configuration**
The application works out-of-the-box with these defaults:
- **Database**: SQLite (`nova_optimizer.db`)
- **Port**: 8000
- **Host**: localhost
- **Mode**: Demo (if SDK not installed)

### **AWS Configuration (For Real Optimizations)**

#### **Option 1: AWS CLI Configuration**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

#### **Option 2: Environment Variables**
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"  # or your preferred region
```

#### **Option 3: IAM Roles (EC2/Lambda)**
If running on AWS infrastructure, use IAM roles instead of credentials.

### **Nova Model Access**
To use real Nova models:
1. Go to **Amazon Bedrock Model Access** page
2. Click **"Manage model access"**
3. Choose **Amazon** as provider and **Nova models**
4. Click **"Request access"**
5. Wait for approval (usually instant)

## 🏃 **Running the Application**

### **Standard Run**
```bash
# Activate environment
source .venv/bin/activate

# Start the application
python3 app.py

# Expected output:
# ✅ Nova Prompt Optimizer SDK loaded successfully
# ✅ Database initialized: nova_optimizer.db
# ✅ Initial sample data inserted
# INFO: Started server process
# INFO: Uvicorn running on http://127.0.0.1:8000
```

### **Custom Port/Host**
```bash
# Run on different port
python3 -c "
import uvicorn
from app import app
uvicorn.run(app, host='0.0.0.0', port=8080)
"
```

### **Background/Production Run**
```bash
# Install uvicorn for production
pip install uvicorn

# Run in background
nohup uvicorn app:app --host 0.0.0.0 --port 8000 &

# Or with gunicorn for production
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## ✅ **Verification**

### **Step 1: Check Application Status**
```bash
# Test if app is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000
# Expected: 200
```

### **Step 2: Verify Database**
```bash
# Check if database was created
ls -la nova_optimizer.db
# Expected: Database file exists

# Check database contents
python3 -c "
from database import db
print(f'📊 Datasets: {len(db.get_datasets())}')
print(f'📝 Prompts: {len(db.get_prompts())}')  
print(f'⚡ Optimizations: {len(db.get_optimizations())}')
"
# Expected: 2 datasets, 2 prompts, 2 optimizations
```

### **Step 3: Test Core Features**
```bash
# Test dashboard
curl -s http://localhost:8000/ | grep -c "Dashboard"
# Expected: 1 or more

# Test optimization page
curl -s http://localhost:8000/optimization | grep -c "Start Optimization"
# Expected: 1
```

### **Step 4: Verify SDK Integration**
```bash
# Check SDK status in logs
python3 -c "
try:
    from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
    print('✅ Real optimization mode enabled')
except ImportError:
    print('⚠️ Demo mode - install nova-prompt-optimizer for real optimizations')
"
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Issue: "ModuleNotFoundError: No module named 'fasthtml'"**
```bash
# Solution: Install FastHTML
pip install fasthtml

# Verify virtual environment is activated
which python3  # Should show .venv path
```

#### **Issue: "Permission denied" on port 8000**
```bash
# Solution: Use different port
python3 -c "
import uvicorn
from app import app
uvicorn.run(app, host='127.0.0.1', port=8080)
"
```

#### **Issue: Database errors**
```bash
# Solution: Reset database
python3 -c "
from database import db
db.reset_database()
print('✅ Database reset successfully')
"
```

#### **Issue: AWS credentials not found**
```bash
# Solution: Configure AWS credentials
aws configure
# OR set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

#### **Issue: Nova SDK import errors**
```bash
# Solution: Install SDK
pip install nova-prompt-optimizer

# If still failing, check Python version
python3 --version  # Should be 3.8+
```

### **Debug Mode**
```bash
# Run with debug output
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')
"
```

### **Clean Installation**
```bash
# If all else fails, clean install
rm -rf .venv nova_optimizer.db __pycache__
python3 -m venv .venv
source .venv/bin/activate
pip install fasthtml starlette python-multipart nova-prompt-optimizer
python3 app.py
```

## 🔬 **Development Setup**

### **For Contributors**

#### **Setup Development Environment**
```bash
# Clone repository
git clone <repository-url>
cd nova-prompt-optimizer/frontend

# Create development environment
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install fasthtml starlette python-multipart nova-prompt-optimizer
pip install pytest black flake8 isort mypy

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### **Development Commands**
```bash
# Format code
black app.py database.py components/

# Lint code
flake8 app.py database.py components/

# Sort imports
isort app.py database.py components/

# Type checking
mypy app.py database.py

# Run tests (when available)
pytest tests/
```

#### **Development Database**
```bash
# Reset database for testing
curl -X POST http://localhost:8000/admin/reset-database

# Or programmatically
python3 -c "from database import db; db.reset_database()"
```

## 📁 **Project Structure**

```
frontend/
├── app.py                    # Main application
├── database.py              # SQLite database layer
├── config.py                # Configuration settings
├── nova_optimizer.db        # SQLite database file
├── components/              # UI components
│   ├── layout.py           # Page layouts
│   ├── navbar.py           # Navigation bar
│   └── ui.py               # UI elements
├── .venv/                  # Virtual environment
├── __pycache__/            # Python cache
├── .archive/               # Archived unused files
├── README.md               # This file
├── PROJECT_DESIGN.md       # Design documentation
├── FEATURES.md             # Feature documentation
└── UNUSED_FILES_REPORT.md  # Cleanup report
```

## 🔗 **Related Documentation**

- **[Project Design](PROJECT_DESIGN.md)** - Architecture and design decisions
- **[Features](FEATURES.md)** - Feature documentation and roadmap
- **[Unused Files Report](UNUSED_FILES_REPORT.md)** - Cleanup analysis
- **[Nova SDK Documentation](https://github.com/aws-samples/nova-prompt-optimizer)** - Official SDK docs

## 🆘 **Getting Help**

### **Check These First**
1. **Logs**: Check console output for error messages
2. **Database**: Verify `nova_optimizer.db` exists and has data
3. **Network**: Ensure port 8000 is available
4. **Dependencies**: Verify all packages are installed

### **Common Solutions**
- **Restart the app**: `Ctrl+C` then `python3 app.py`
- **Reset database**: Use admin reset route
- **Reinstall dependencies**: Delete `.venv` and reinstall
- **Check AWS credentials**: Verify AWS configuration

### **Still Need Help?**
- Check the **[Troubleshooting](#-troubleshooting)** section above
- Review error messages carefully
- Ensure all prerequisites are met
- Try the clean installation process

---

**🎉 You're ready to start optimizing prompts with Nova!**

Open http://localhost:8000 in your browser and begin creating datasets, prompts, and running optimizations.

# Nova Prompt Optimizer - Frontend

A modern web interface for the Nova Prompt Optimizer SDK, built with FastHTML and SQLite for simplicity and performance.

## **Quick Start**

### **Automated Installation (Recommended)**
```bash
# Clone and navigate to frontend
cd nova-prompt-optimizer/frontend

# Run automated installation
./install.sh

# Start the application
./start.sh

# Open browser
open http://localhost:8000
```

### **Manual Installation**
```bash
# Clone and navigate to frontend
cd nova-prompt-optimizer/frontend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies and setup
pip install -r requirements.txt
python3 setup.py

# Validate installation
python3 health_check.py

# Run the application
python3 app.py

# Open browser
open http://localhost:8000
```

## **Prerequisites**

### **System Requirements**
- **Python 3.8+** (Python 3.11+ recommended)
- **pip** (Python package manager)
- **4GB+ RAM** (for running optimizations)
- **1GB+ disk space** (for dependencies and data)

### **Operating System Support**
- **macOS** (10.14+)
- **Linux** (Ubuntu 18.04+, CentOS 7+)
- **Windows** (10+, WSL recommended)

### **Browser Support**
- **Chrome** (90+)
- **Firefox** (88+)
- **Safari** (14+)
- **Edge** (90+)

## **Configuration**

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

## **Running the Application**

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

## **Features**

### **Core Features**
- **Dataset Management**: Upload and manage CSV datasets
- **Prompt Creation**: Create and edit system/user prompts
- **Metric Generation**: AI-powered metric creation and selection
- **Optimization**: Real-time prompt optimization using Nova SDK
- **Results Analysis**: Detailed comparison of baseline vs optimized prompts
- **Few-shot Examples**: Automatic generation and display of training examples

### **User Interface**
- **Modern Design**: Clean, responsive interface using Shad4FastHTML
- **Dark/Light Mode**: Toggle between themes with persistent preference
- **Real-time Updates**: Live progress monitoring during optimizations
- **Interactive Components**: Switches, accordions, and collapsible sections
- **Mobile Friendly**: Responsive design works on all devices

### **Technical Features**
- **Rate Limiting**: Intelligent rate limiting for AWS Bedrock API calls
- **Error Handling**: Comprehensive error handling and user feedback
- **Database**: SQLite for simplicity and portability
- **Logging**: Detailed optimization logs and progress tracking
- **File Management**: Automatic cleanup and organization

## **Project Structure**

```
frontend/
├── app.py                    # Main FastHTML application
├── sdk_worker.py            # Nova SDK optimization worker
├── database.py              # SQLite database layer
├── config.py                # Configuration settings
├── metric_service.py        # AI metric generation service
├── prompt_templates.py      # AI prompt templates
├── simple_rate_limiter.py   # Rate limiting utility
├── requirements.txt         # Python dependencies
├── setup.py                 # Database initialization
├── health_check.py          # System health validation
├── install.sh               # Automated installation script
├── start.sh                 # Application startup script
├── nova_optimizer.db        # SQLite database file
├── components/              # UI components
│   ├── layout.py           # Page layouts and styling
│   ├── navbar.py           # Navigation bar
│   ├── ui.py               # UI elements
│   └── metrics_page.py     # Metrics interface
├── uploads/                # User uploaded datasets
├── optimized_prompts/      # Optimization results
├── data/                   # Temporary optimization data
├── .venv/                  # Virtual environment
├── README.md               # This file
└── FEATURES.md             # Feature documentation
```

## **Troubleshooting**

### **Common Issues**

#### **Issue: "ModuleNotFoundError"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt

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
python3 setup.py
```

#### **Issue: AWS credentials not found**
```bash
# Solution: Configure AWS credentials
aws configure
# OR set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
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
rm -rf .venv nova_optimizer.db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 setup.py
python3 app.py
```

## **Getting Help**

### **Check These First**
1. **Logs**: Check console output for error messages
2. **Database**: Verify `nova_optimizer.db` exists and has data
3. **Network**: Ensure port 8000 is available
4. **Dependencies**: Verify all packages are installed

### **Common Solutions**
- **Restart the app**: `Ctrl+C` then `python3 app.py`
- **Reset database**: Run `python3 setup.py`
- **Reinstall dependencies**: Delete `.venv` and reinstall
- **Check AWS credentials**: Verify AWS configuration

---

**Ready to optimize prompts with Nova!**

Open http://localhost:8000 in your browser and begin creating datasets, prompts, and running optimizations.

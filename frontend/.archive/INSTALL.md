# Installation Guide - Nova Prompt Optimizer Frontend

## 🚀 Quick Installation

### Option 1: Quick Setup (Recommended)

```bash
cd frontend
python quick_setup.py
```

This will:
- ✅ Install minimal dependencies with proper timing
- 📝 Create basic configuration file (.env)
- 🗄️ Initialize database with retry logic
- 📁 Create necessary directories

### Option 2: Step-by-Step Manual Installation

```bash
cd frontend

# 1. Install dependencies
pip install -r requirements-minimal.txt

# 2. Wait for dependencies to be ready
sleep 3

# 3. Create configuration file
cp .env.template .env
# Edit .env with your settings

# 4. Initialize database
python init_db.py

# 5. Start the application
python app.py --reload
```

### Option 3: Original Automated Setup

```bash
cd frontend
python setup.py
```

If database initialization fails, run separately:
```bash
python init_db.py
```

## 📋 Prerequisites

- **Python 3.11+** (required)
- **AWS Credentials** (optional, for Nova model access)

### Check Python Version
```bash
python --version
# Should show Python 3.11.0 or higher
```

### Install Python 3.11+ (if needed)

**macOS (using Homebrew):**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

## 🔧 Configuration

### Environment Variables

Edit the `.env` file created during setup:

```bash
# Required for basic functionality
DEBUG=true
SECRET_KEY=your-secret-key-here

# Optional: AWS credentials for Nova models
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Database (SQLite by default)
DATABASE_URL=sqlite:///nova_optimizer.db
```

### AWS Setup (Optional)

If you want to use Nova models:

1. **Configure AWS credentials:**
   ```bash
   aws configure
   # OR set environment variables in .env
   ```

2. **Enable Nova model access:**
   - Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
   - Navigate to "Model access"
   - Request access to Nova models

3. **Test AWS connection:**
   ```bash
   python -c "
   import boto3
   client = boto3.client('bedrock-runtime', region_name='us-east-1')
   print('✅ AWS connection successful')
   "
   ```

## 🚀 Running the Application

### Development Mode
```bash
python app.py --reload
```

### Production Mode
```bash
python app.py --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🌐 Access the Application

Once running, access the application at:
- **Web Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 🐛 Troubleshooting

### Common Issues

**1. Python Version Error**
```
ERROR: Python 3.11+ is required
```
**Solution:** Install Python 3.11 or higher

**2. Package Installation Fails**
```
ERROR: Could not find a version that satisfies the requirement...
```
**Solution:** 
```bash
# Update pip
pip install --upgrade pip

# Try installing minimal requirements
pip install -r requirements-minimal.txt
```

**3. Database Initialization Fails**
```
ERROR: Database initialization failed
```
**Solution:**
```bash
# Check if database directory is writable
ls -la nova_optimizer.db

# Try manual initialization
python -c "
import asyncio
from models.database import init_database
asyncio.run(init_database())
"
```

**4. AWS Connection Issues**
```
ERROR: Unable to locate credentials
```
**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Or set in .env file
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

**5. Port Already in Use**
```
ERROR: [Errno 48] Address already in use
```
**Solution:**
```bash
# Use different port
python app.py --port 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Getting Help

1. **Check logs:**
   ```bash
   # Application logs
   tail -f logs/app.log
   
   # Database logs (if enabled)
   tail -f logs/database.log
   ```

2. **Test database connection:**
   ```bash
   python -c "
   import asyncio
   from models.database import db_manager
   print('Database health:', asyncio.run(db_manager.health_check()))
   "
   ```

3. **Verify installation:**
   ```bash
   python -c "
   import fasthtml
   import sqlalchemy
   import boto3
   print('✅ All core dependencies installed')
   "
   ```

## 🔄 Updating

To update the application:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
python -c "
import asyncio
from models.database import init_database
asyncio.run(init_database())
"

# Restart application
python app.py --reload
```

## 🧪 Development Setup

For development with testing and code quality tools:

```bash
# Install full dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests
pytest

# Run code quality checks
black .
flake8 .
```

## 📦 Docker Installation (Alternative)

If you prefer Docker:

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-minimal.txt .
RUN pip install -r requirements-minimal.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py", "--host", "0.0.0.0"]
```

```bash
# Build and run
docker build -t nova-frontend .
docker run -p 8000:8000 nova-frontend
```

## 🎉 Success!

If everything is working correctly, you should see:

```
🚀 Starting Nova Prompt Optimizer Frontend...
✅ Database initialized
✅ Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Visit http://localhost:8000 to start using the application!

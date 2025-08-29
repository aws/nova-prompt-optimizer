# Nova Prompt Optimizer - Frontend

A modern web interface for the Nova Prompt Optimizer SDK, built with FastHTML and SQLite. Features AI-powered dataset generation, prompt optimization, and advanced "Optimize Further" capabilities.

## **🚀 Quick Start**

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

## **📋 Prerequisites**

### **System Requirements**
- **Python 3.8+** (Python 3.11+ recommended)
- **pip** (Python package manager)
- **4GB+ RAM** (for running optimizations)
- **1GB+ disk space** (for dependencies and data)

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

### **Nova Model Access**
To use real Nova models:
1. Go to **Amazon Bedrock Model Access** page
2. Click **"Manage model access"**
3. Choose **Amazon** as provider and **Nova models**
4. Click **"Request access"**
5. Wait for approval (usually instant)

## **🏗️ Project Structure & File Explanations**

### **Core Application Files**

#### **`app.py`** - Main FastHTML Application
- **Purpose**: Primary web server and route handler
- **Key Features**:
  - FastHTML web framework setup
  - All HTTP routes (GET/POST endpoints)
  - UI rendering and page layouts
  - File upload handling
  - Database integration
- **Main Routes**:
  - `/` - Dashboard homepage
  - `/datasets` - Dataset management
  - `/prompts` - Prompt creation/editing
  - `/metrics` - AI metric generation
  - `/optimization` - Optimization interface
  - `/optimization/results/{id}` - Results viewing

#### **`sdk_worker.py`** - Nova SDK Optimization Engine
- **Purpose**: Handles all Nova SDK optimization operations
- **Key Functions**:
  - `run_optimization_worker()` - Main optimization orchestrator
  - Dataset adaptation and splitting
  - Prompt adapter creation and configuration
  - Metric adapter setup and validation
  - Baseline and optimized evaluation
  - Results extraction and storage
- **Process Flow**:
  1. Load and validate configuration
  2. Create dataset, prompt, and metric adapters
  3. Run baseline evaluation
  4. Execute Nova optimization
  5. Evaluate optimized results
  6. Extract and store prompt candidates

#### **`database.py`** - SQLite Database Layer
- **Purpose**: All database operations and schema management
- **Key Tables**:
  - `datasets` - Uploaded CSV datasets
  - `prompts` - System/user prompt templates
  - `metrics` - AI-generated evaluation metrics
  - `optimizations` - Optimization job records
  - `optimization_logs` - Detailed progress logs
  - `prompt_candidates` - Optimization results
- **Key Functions**:
  - CRUD operations for all entities
  - Optimization progress tracking
  - Results storage and retrieval

#### **`metric_service.py`** - AI Metric Generation Service
- **Purpose**: Generates custom evaluation metrics using AI
- **Key Features**:
  - Dataset analysis and column detection
  - AI-powered metric code generation
  - Metric validation and testing
  - Support for classification, regression, and custom metrics
- **Process**:
  1. Analyze dataset structure
  2. Generate metric code using Nova
  3. Validate generated code
  4. Test metric with sample data

### **Configuration & Utilities**

#### **`config.py`** - Application Configuration
- **Purpose**: Centralized configuration management
- **Settings**:
  - Database paths and connection settings
  - Nova model configurations
  - Rate limiting parameters
  - File upload limits

#### **`simple_rate_limiter.py`** - Rate Limiting Utility
- **Purpose**: Manages AWS Bedrock API rate limits
- **Features**:
  - Token bucket algorithm
  - Configurable rates per minute
  - Thread-safe implementation
  - Automatic rate adjustment

#### **`prompt_templates.py`** - AI Prompt Templates
- **Purpose**: Templates for AI-powered features
- **Templates**:
  - Dataset analysis prompts
  - Metric generation prompts
  - Sample data generation prompts
  - Validation and testing prompts

### **Setup & Deployment Scripts**

#### **`setup.py`** - Database Initialization
- **Purpose**: Creates and initializes SQLite database
- **Actions**:
  1. Creates database schema
  2. Inserts sample data
  3. Sets up initial configurations
  4. Validates database integrity

#### **`health_check.py`** - System Health Validation
- **Purpose**: Validates system readiness
- **Checks**:
  - Python version compatibility
  - Required dependencies
  - AWS credentials (if configured)
  - Database connectivity
  - File system permissions

#### **`install.sh`** - Automated Installation Script
```bash
#!/bin/bash
# Automated installation and setup
set -e

echo "🚀 Installing Nova Prompt Optimizer Frontend..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 setup.py

# Run health check
python3 health_check.py

echo "✅ Installation complete! Run ./start.sh to begin."
```

#### **`start.sh`** - Application Startup Script
```bash
#!/bin/bash
# Application startup script
set -e

# Activate virtual environment
source .venv/bin/activate

# Run health check
python3 health_check.py

# Start application
echo "🚀 Starting Nova Prompt Optimizer..."
python3 app.py
```

## **🎯 Key Features**

### **1. AI Dataset Generation** ⭐ NEW FEATURE
- **Purpose**: Generate synthetic datasets using conversational AI
- **Process**:
  1. **Describe Dataset**: User describes desired dataset in natural language
  2. **AI Analysis**: System analyzes requirements and suggests structure
  3. **Sample Generation**: AI generates realistic sample data
  4. **Review & Edit**: User reviews and modifies generated samples
  5. **Finalize**: Dataset saved and ready for optimization
- **Benefits**:
  - No need to manually create datasets
  - Consistent, realistic sample data
  - Customizable to specific use cases
  - Integrated with optimization workflow

### **2. Optimize Further** ⭐ ADVANCED FEATURE
- **Purpose**: Iteratively improve already optimized prompts
- **How It Works**:
  1. Start with a completed optimization
  2. Click "Optimize Further" on results page
  3. System uses optimized prompt as new baseline
  4. Includes few-shot examples from previous optimization
  5. Runs new optimization cycle for additional improvements
- **Key Benefits**:
  - **Iterative Improvement**: Build upon previous optimizations
  - **Few-shot Integration**: Automatically includes learned examples
  - **Baseline Accuracy**: Maintains score consistency across iterations
  - **Rate Limit Inheritance**: Uses same performance settings
- **Technical Details**:
  - Inherits rate limits from original optimization
  - Preserves few-shot examples in baseline evaluation
  - Prevents infinite loops with safety mechanisms
  - Runs in separate process to avoid threading issues

### **3. Core Optimization Features**
- **Dataset Management**: Upload and manage CSV datasets
- **Prompt Creation**: Create and edit system/user prompts with variables
- **Metric Generation**: AI-powered custom metric creation
- **Real-time Monitoring**: Live progress tracking during optimizations
- **Results Analysis**: Detailed comparison of baseline vs optimized prompts

## **📊 Step-by-Step Usage Guide**

### **Step 1: Create or Generate Dataset**

#### **Option A: Upload Existing Dataset**
1. Navigate to **Datasets** page
2. Click **"Upload Dataset"**
3. Select CSV file with input/output columns
4. Review column mapping
5. Save dataset

#### **Option B: Generate Dataset with AI** ⭐
1. Navigate to **Datasets** page
2. Click **"Generate Dataset with AI"**
3. **Describe Your Dataset**:
   ```
   Example: "Create a customer support email classification dataset 
   with categories for billing, technical, and general inquiries"
   ```
4. **Review AI Suggestions**: System analyzes and suggests structure
5. **Generate Samples**: AI creates realistic sample data
6. **Review & Edit**: Modify samples as needed
7. **Finalize**: Save generated dataset

### **Step 2: Create Prompts**
1. Navigate to **Prompts** page
2. Click **"Create Prompt"**
3. Enter **System Prompt**: Instructions for the AI
4. Enter **User Prompt**: Template with variables like `{input}`
5. Test prompt with sample data
6. Save prompt

### **Step 3: Generate Metrics**
1. Navigate to **Metrics** page
2. Click **"Generate Metric with AI"**
3. Select your dataset
4. Describe evaluation criteria
5. AI generates custom metric code
6. Test and validate metric
7. Save metric

### **Step 4: Run Optimization**
1. Navigate to **Optimization** page
2. Select prompt, dataset, and metric
3. Configure settings (model, rate limit)
4. Click **"Start Optimization"**
5. Monitor progress in real-time
6. View results when complete

### **Step 5: Optimize Further** ⭐
1. From optimization results page
2. Click **"Optimize Further"**
3. System automatically:
   - Uses optimized prompt as baseline
   - Includes few-shot examples
   - Inherits rate limits and settings
4. Monitor new optimization progress
5. Compare iterative improvements

## **🔧 Advanced Configuration**

### **Custom Rate Limits**
```python
# In config.py
RATE_LIMITS = {
    "nova-lite": 1000,    # RPM for Nova Lite
    "nova-pro": 500,      # RPM for Nova Pro
    "nova-premier": 100   # RPM for Nova Premier
}
```

### **Database Customization**
```python
# Custom database path
DATABASE_PATH = "/custom/path/nova_optimizer.db"

# Connection pool settings
CONNECTION_POOL_SIZE = 10
CONNECTION_TIMEOUT = 30
```

### **File Upload Limits**
```python
# Maximum file sizes
MAX_DATASET_SIZE = 50 * 1024 * 1024  # 50MB
MAX_SAMPLES = 10000                   # Maximum dataset rows
```

## **🐛 Troubleshooting**

### **Common Issues**

#### **Issue: "Optimize Further" Infinite Loop**
```bash
# Check logs for safety limit messages
tail -f optimization_logs.txt

# Solution: Already fixed in latest version
# Uses original_metric to prevent wrapper conflicts
```

#### **Issue: Rate Limit Inheritance Not Working**
```bash
# Check optimization logs for rate limit extraction
# Should see: "Inherited rate limit from original optimization: 1000 RPM"

# Manual fix: Edit config in optimize_further function
```

#### **Issue: Few-shot Examples Not Included in Baseline**
```bash
# Verify baseline_few_shot_examples in config
# Should see: "Added X few-shot examples to baseline evaluation"
```

#### **Issue: DSPy Thread Configuration Error**
```bash
# Error: "dspy.settings can only be changed by the thread that initially configured it"
# Solution: Already fixed - uses subprocess instead of threading
```

### **Debug Mode**
```bash
# Run with detailed debugging
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8000, log_level='debug')
"
```

## **🚀 Deployment**

### **Development**
```bash
# Standard development server
python3 app.py
```

### **Production**
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python3 setup.py

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## **📈 Performance Tips**

### **Optimization Performance**
- **Use higher rate limits** for faster optimization (1000+ RPM)
- **Smaller datasets** optimize faster (< 1000 samples)
- **Simpler metrics** reduce evaluation time
- **Pro/Premier models** provide better optimization quality

### **System Performance**
- **SSD storage** improves database performance
- **8GB+ RAM** recommended for large datasets
- **Multiple CPU cores** help with parallel processing

## **🔄 Workflow Examples**

### **Basic Optimization Workflow**
1. Upload customer support emails dataset
2. Create classification prompt
3. Generate accuracy metric
4. Run optimization
5. Review 15-20% improvement
6. Deploy optimized prompt

### **Iterative Optimization Workflow** ⭐
1. Complete basic optimization (baseline: 65%, optimized: 78%)
2. Click "Optimize Further"
3. System uses 78% prompt as new baseline
4. Run second optimization (baseline: 78%, optimized: 85%)
5. Continue iterating for maximum performance

### **AI Dataset Generation Workflow** ⭐
1. Describe: "Email sentiment analysis dataset"
2. AI suggests: input (email text), output (positive/negative/neutral)
3. Generate 500 realistic email samples
4. Review and edit samples
5. Use for prompt optimization

## **🧹 Directory Management**

**Important**: Keep the root directory clean! All application files belong in `frontend/`.

### **Cleanup Script**
```bash
# From project root, run cleanup script
../cleanup.sh
```

### **Rules**:
- ✅ Database: `frontend/nova_optimizer.db`
- ✅ Uploads: `frontend/uploads/`
- ✅ Data: `frontend/data/`
- ✅ Logs: `frontend/logs/`
- ❌ No application files in project root

---

**🎉 Ready to optimize prompts with Nova!**

Open http://localhost:8000 in your browser and begin creating datasets, prompts, and running optimizations with advanced AI-powered features.

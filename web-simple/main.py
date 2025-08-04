#!/usr/bin/env python3
"""
Nova Prompt Optimizer - Lightweight Web Interface

A simplified FastAPI application that serves both the API and static files
for the Nova Prompt Optimizer web interface.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter, CSVDatasetAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
    from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
    from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
    from amzn_nova_prompt_optimizer.core.evaluation import Evaluator
except ImportError as e:
    print(f"Warning: Could not import Nova Prompt Optimizer SDK: {e}")
    print("Running in demo mode without SDK functionality")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nova Prompt Optimizer",
    description="Lightweight web interface for Nova Prompt Optimizer",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
uploads_dir = Path(__file__).parent / "uploads"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)
uploads_dir.mkdir(exist_ok=True)

# Create data directory for persistent storage
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Persistent storage files
DATASETS_FILE = data_dir / "datasets.json"
PROMPTS_FILE = data_dir / "prompts.json"
OPTIMIZATIONS_FILE = data_dir / "optimizations.json"

# Persistent storage functions
def load_datasets() -> Dict:
    """Load datasets from persistent storage"""
    if DATASETS_FILE.exists():
        try:
            with open(DATASETS_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} datasets from persistent storage")
                return data
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
    return {}

def save_datasets(datasets_data: Dict):
    """Save datasets to persistent storage"""
    try:
        with open(DATASETS_FILE, 'w') as f:
            json.dump(datasets_data, f, indent=2, default=str)
        logger.info(f"Saved {len(datasets_data)} datasets to persistent storage")
    except Exception as e:
        logger.error(f"Error saving datasets: {e}")

def load_prompts() -> Dict:
    """Load prompts from persistent storage"""
    if PROMPTS_FILE.exists():
        try:
            with open(PROMPTS_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} prompts from persistent storage")
                return data
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
    return {}

def save_prompts(prompts_data: Dict):
    """Save prompts to persistent storage"""
    try:
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts_data, f, indent=2, default=str)
        logger.info(f"Saved {len(prompts_data)} prompts to persistent storage")
    except Exception as e:
        logger.error(f"Error saving prompts: {e}")

def load_optimizations() -> Dict:
    """Load optimizations from persistent storage"""
    if OPTIMIZATIONS_FILE.exists():
        try:
            with open(OPTIMIZATIONS_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} optimizations from persistent storage")
                return data
        except Exception as e:
            logger.error(f"Error loading optimizations: {e}")
    return {}

def save_optimizations(optimizations_data: Dict):
    """Save optimizations to persistent storage"""
    try:
        with open(OPTIMIZATIONS_FILE, 'w') as f:
            json.dump(optimizations_data, f, indent=2, default=str)
        logger.info(f"Saved {len(optimizations_data)} optimizations to persistent storage")
    except Exception as e:
        logger.error(f"Error saving optimizations: {e}")

# Load data from persistent storage
datasets = load_datasets()
prompts = load_prompts()
optimizations = load_optimizations()
active_websockets = {}

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

# Routes

@app.get("/test-simple")
async def test_simple():
    """Simple test page for debugging data loading"""
    with open("test_simple.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Dataset Management API

@app.post("/api/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload and process a dataset file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.jsonl', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSONL files are supported")
        
        # Save uploaded file
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process dataset based on file type
        if file.filename.endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
            row_count = len(df)
        else:  # JSON/JSONL
            with open(file_path, 'r') as f:
                if file.filename.endswith('.jsonl'):
                    lines = f.readlines()
                    data = [json.loads(line) for line in lines if line.strip()]
                else:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
            
            columns = list(data[0].keys()) if data else []
            row_count = len(data)
        
        # Create dataset record
        dataset_id = f"dataset_{len(datasets) + 1}"
        dataset_record = {
            "id": dataset_id,
            "name": name or file.filename,
            "description": description or "",
            "filename": file.filename,
            "file_path": str(file_path),
            "columns": columns,
            "row_count": row_count,
            "created_at": datetime.now().isoformat()
        }
        
        datasets[dataset_id] = dataset_record
        
        # Save to persistent storage
        save_datasets(datasets)
        
        logger.info(f"Dataset uploaded: {dataset_id} ({file.filename})")
        return dataset_record
        
    except Exception as e:
        logger.error(f"Dataset upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets")
async def list_datasets():
    """List all uploaded datasets"""
    return {"datasets": list(datasets.values())}

@app.get("/api/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get dataset details"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return datasets[dataset_id]

@app.get("/api/datasets/{dataset_id}/preview")
async def get_dataset_preview(dataset_id: str, limit: int = 50, offset: int = 0):
    """Get dataset preview with pagination support"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets[dataset_id]
    file_path = Path(dataset["file_path"])
    
    try:
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        preview_data = []
        columns = []
        
        if dataset["filename"].endswith('.csv'):
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # Get column names
            columns = df.columns.tolist()
            
            # Apply pagination
            end_idx = offset + limit
            paginated_df = df.iloc[offset:end_idx]
            preview_data = paginated_df.to_dict('records')
            
        elif dataset["filename"].endswith('.json') or dataset["filename"].endswith('.jsonl'):
            import json
            
            # Read JSON data
            if dataset["filename"].endswith('.jsonl'):
                # JSONL format - one JSON object per line
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    
                # Apply pagination to lines
                paginated_lines = lines[offset:offset + limit]
                preview_data = [json.loads(line.strip()) for line in paginated_lines if line.strip()]
            else:
                # Regular JSON format
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    # Apply pagination
                    preview_data = data[offset:offset + limit]
                else:
                    preview_data = [data] if offset == 0 else []
            
            # Extract column names from first record
            if preview_data:
                columns = list(preview_data[0].keys())
        
        return {
            "data": preview_data,
            "columns": columns,
            "offset": offset,
            "limit": limit,
            "total_rows": dataset.get("row_count", len(preview_data))
        }
        
    except Exception as e:
        logger.error(f"Failed to load dataset preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}/export")
async def export_dataset(dataset_id: str, format: str = "csv"):
    """Export dataset in specified format"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets[dataset_id]
    file_path = Path(dataset["file_path"])
    
    try:
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        if format.lower() == "csv":
            if dataset["filename"].endswith('.csv'):
                # Return original CSV file
                from fastapi.responses import FileResponse
                return FileResponse(
                    file_path,
                    media_type="text/csv",
                    filename=f"{dataset['name']}.csv"
                )
            else:
                # Convert JSONL to CSV
                import pandas as pd
                with open(file_path, 'r') as f:
                    if dataset["filename"].endswith('.jsonl'):
                        lines = f.readlines()
                        data = [json.loads(line) for line in lines if line.strip()]
                    else:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]
                
                df = pd.DataFrame(data)
                
                # Create temporary CSV file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                    df.to_csv(tmp_file.name, index=False)
                    
                from fastapi.responses import FileResponse
                return FileResponse(
                    tmp_file.name,
                    media_type="text/csv",
                    filename=f"{dataset['name']}.csv"
                )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error(f"Failed to export dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets[dataset_id]
    
    try:
        # Delete the physical file
        file_path = Path(dataset["file_path"])
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted dataset file: {file_path}")
        
        # Remove from datasets dictionary
        deleted_dataset = datasets.pop(dataset_id)
        
        # Save to persistent storage
        save_datasets(datasets)
        
        logger.info(f"Dataset deleted: {dataset_id}")
        return {"message": "Dataset deleted successfully", "deleted_dataset": deleted_dataset}
        
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets/{dataset_id}/download")
async def download_dataset(dataset_id: str):
    """Download dataset file"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = datasets[dataset_id]
    file_path = Path(dataset["file_path"])
    
    try:
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset file not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=dataset["filename"]
        )
        
    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Prompt Management API

@app.post("/api/prompts")
async def create_prompt(prompt_data: dict):
    """Create a new prompt"""
    prompt_id = f"prompt_{len(prompts) + 1}"
    prompt_record = {
        "id": prompt_id,
        "name": prompt_data.get("name", "Untitled Prompt"),
        "description": prompt_data.get("description", ""),
        "system_prompt": prompt_data.get("system_prompt", ""),
        "user_prompt": prompt_data.get("user_prompt", ""),
        "variables": prompt_data.get("variables", []),
        "created_at": datetime.now().isoformat()
    }
    
    prompts[prompt_id] = prompt_record
    
    # Save to persistent storage
    save_prompts(prompts)
    
    logger.info(f"Prompt created: {prompt_id}")
    return prompt_record

@app.get("/api/prompts")
async def list_prompts():
    """List all prompts"""
    return {"prompts": list(prompts.values())}

@app.get("/api/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get prompt details"""
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts[prompt_id]

@app.put("/api/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, prompt_data: dict):
    """Update an existing prompt"""
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    prompts[prompt_id].update(prompt_data)
    prompts[prompt_id]["updated_at"] = datetime.now().isoformat()
    
    # Save to persistent storage
    save_prompts(prompts)
    
    logger.info(f"Prompt updated: {prompt_id}")
    return prompts[prompt_id]

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Delete a prompt"""
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    deleted_prompt = prompts.pop(prompt_id)
    
    # Save to persistent storage
    save_prompts(prompts)
    
    logger.info(f"Prompt deleted: {prompt_id}")
    return {"message": "Prompt deleted successfully", "deleted_prompt": deleted_prompt}

# Optimization API

@app.post("/api/optimization/start")
async def start_optimization(optimization_request: dict):
    """Start a prompt optimization process"""
    try:
        optimization_id = f"opt_{len(optimizations) + 1}"
        
        # Create optimization record
        optimization_record = {
            "id": optimization_id,
            "dataset_id": optimization_request.get("dataset_id"),
            "prompt_id": optimization_request.get("prompt_id"),
            "mode": optimization_request.get("mode", "pro"),
            "status": "queued",
            "progress": 0.0,
            "current_step": "Initializing",
            "created_at": datetime.now().isoformat(),
            "results": None
        }
        
        optimizations[optimization_id] = optimization_record
        
        # Save to persistent storage
        save_optimizations(optimizations)
        
        # Start optimization in background
        asyncio.create_task(run_optimization(optimization_id, optimization_request))
        
        logger.info(f"Optimization started: {optimization_id}")
        return optimization_record
        
    except Exception as e:
        logger.error(f"Failed to start optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/runs")
async def list_optimization_runs():
    """List all optimization runs"""
    return {"runs": list(optimizations.values())}

@app.get("/api/optimization/{optimization_id}")
async def get_optimization_status(optimization_id: str):
    """Get optimization status"""
    if optimization_id not in optimizations:
        raise HTTPException(status_code=404, detail="Optimization not found")
    return optimizations[optimization_id]

# WebSocket for real-time updates

@app.websocket("/ws/optimization/{optimization_id}")
async def websocket_endpoint(websocket: WebSocket, optimization_id: str):
    """WebSocket endpoint for real-time optimization updates"""
    await manager.connect(websocket, optimization_id)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(optimization_id)

# Background optimization task

async def run_optimization(optimization_id: str, request: dict):
    """Run the optimization process in the background"""
    try:
        optimization = optimizations[optimization_id]
        
        # Update status
        optimization["status"] = "running"
        optimization["current_step"] = "Loading dataset"
        await manager.send_message(optimization_id, {
            "type": "progress",
            "optimization_id": optimization_id,
            "progress": 0.1,
            "current_step": "Loading dataset"
        })
        
        # Simulate optimization process (replace with actual SDK calls)
        steps = [
            ("Loading dataset", 0.1),
            ("Preparing prompt", 0.2),
            ("Initializing optimizer", 0.3),
            ("Running meta prompting", 0.5),
            ("Running MIPROv2", 0.8),
            ("Finalizing results", 1.0)
        ]
        
        for step_name, progress in steps:
            optimization["current_step"] = step_name
            optimization["progress"] = progress
            
            await manager.send_message(optimization_id, {
                "type": "progress",
                "optimization_id": optimization_id,
                "progress": progress,
                "current_step": step_name
            })
            
            # Simulate work
            await asyncio.sleep(2)
        
        # Complete optimization
        optimization["status"] = "completed"
        optimization["completed_at"] = datetime.now().isoformat()
        optimization["results"] = {
            "original_score": 0.65,
            "optimized_score": 0.82,
            "improvement": 0.17,
            "optimized_prompt": {
                "system_prompt": "You are an expert classifier...",
                "user_prompt": "Classify the following text: {{input}}"
            }
        }
        
        # Save to persistent storage
        save_optimizations(optimizations)
        
        await manager.send_message(optimization_id, {
            "type": "completed",
            "optimization_id": optimization_id,
            "results": optimization["results"]
        })
        
        logger.info(f"Optimization completed: {optimization_id}")
        
    except Exception as e:
        logger.error(f"Optimization failed: {optimization_id} - {e}")
        optimization["status"] = "failed"
        optimization["error"] = str(e)
        
        # Save to persistent storage
        save_optimizations(optimizations)
        
        await manager.send_message(optimization_id, {
            "type": "error",
            "optimization_id": optimization_id,
            "error": str(e)
        })

# Development server
if __name__ == "__main__":
    print("🚀 Starting Nova Prompt Optimizer (Lightweight)")
    print("📊 Web Interface: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

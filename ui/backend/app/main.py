"""
FastAPI main application with comprehensive API documentation.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager

from app.core.monitoring import setup_monitoring
from app.core.error_tracking import setup_error_tracking
from app.routers import (
    datasets,
    prompts,
    optimization,
    metrics,
    annotations,
    websocket,
    monitoring
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_monitoring()
    setup_error_tracking()
    yield
    # Shutdown
    pass


# Create FastAPI app with comprehensive metadata
app = FastAPI(
    title="Nova Prompt Optimizer API",
    description="""
    The Nova Prompt Optimizer API provides programmatic access to prompt optimization functionality.
    
    ## Features
    
    * **Dataset Management**: Upload, process, and manage datasets for optimization
    * **Prompt Engineering**: Create, edit, and manage prompts with template variables
    * **Custom Metrics**: Define domain-specific evaluation metrics
    * **Optimization Workflows**: Run automated prompt optimization with various algorithms
    * **Human Annotation**: AI-generated rubrics with human quality assurance
    * **Real-time Updates**: WebSocket support for live progress tracking
    
    ## Authentication
    
    Currently uses session-based authentication. API key support coming soon.
    
    ## Rate Limits
    
    * General endpoints: 100 requests/minute
    * Upload endpoints: 10 requests/minute  
    * Optimization endpoints: 5 concurrent per user
    
    ## Support
    
    * Documentation: [User Guide](/docs)
    * Interactive API: [Swagger UI](/docs)
    * Alternative docs: [ReDoc](/redoc)
    """,
    version="1.0.0",
    contact={
        "name": "Nova Prompt Optimizer Team",
        "email": "support@example.com",
        "url": "https://github.com/example/nova-prompt-optimizer"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.nova-optimizer.example.com",
            "description": "Production server"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers with tags for organization
app.include_router(
    datasets.router,
    prefix="/api/v1/datasets",
    tags=["Datasets"],
    responses={
        404: {"description": "Dataset not found"},
        422: {"description": "Dataset processing error"}
    }
)

app.include_router(
    prompts.router,
    prefix="/api/v1/prompts",
    tags=["Prompts"],
    responses={
        404: {"description": "Prompt not found"},
        422: {"description": "Template validation error"}
    }
)

app.include_router(
    optimization.router,
    prefix="/api/v1/optimize",
    tags=["Optimization"],
    responses={
        404: {"description": "Optimization task not found"},
        429: {"description": "Rate limit exceeded"}
    }
)

app.include_router(
    metrics.router,
    prefix="/api/v1/metrics",
    tags=["Custom Metrics"],
    responses={
        404: {"description": "Metric not found"},
        422: {"description": "Metric code validation error"}
    }
)

app.include_router(
    annotations.router,
    prefix="/api/v1",
    tags=["Annotations & Rubrics"],
    responses={
        404: {"description": "Annotation resource not found"},
        422: {"description": "Annotation validation error"}
    }
)

app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)

app.include_router(
    monitoring.router,
    prefix="/api/v1",
    tags=["Monitoring & Health"]
)

# Serve static files for documentation
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve user documentation
if os.path.exists("../docs"):
    app.mount("/docs-static", StaticFiles(directory="../docs"), name="docs")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nova Prompt Optimizer API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2563eb; }
            .link { color: #1d4ed8; text-decoration: none; }
            .link:hover { text-decoration: underline; }
            .section { margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1 class="header">Nova Prompt Optimizer API</h1>
        <p>Welcome to the Nova Prompt Optimizer API. This service provides programmatic access to prompt optimization functionality.</p>
        
        <div class="section">
            <h2>Documentation</h2>
            <ul>
                <li><a href="/docs" class="link">Interactive API Documentation (Swagger UI)</a></li>
                <li><a href="/redoc" class="link">Alternative API Documentation (ReDoc)</a></li>
                <li><a href="/openapi.json" class="link">OpenAPI Specification (JSON)</a></li>
                <li><a href="/docs-static/user-guide/" class="link">User Guide</a></li>
                <li><a href="/docs-static/api/" class="link">API Guide</a></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Quick Start</h2>
            <p>Get started with the API:</p>
            <ol>
                <li>Upload a dataset: <code>POST /api/v1/datasets/upload</code></li>
                <li>Create a prompt: <code>POST /api/v1/prompts</code></li>
                <li>Start optimization: <code>POST /api/v1/optimize/start</code></li>
                <li>Monitor progress: <code>GET /api/v1/optimize/{task_id}/status</code></li>
            </ol>
        </div>
        
        <div class="section">
            <h2>Health Check</h2>
            <p><a href="/health" class="link">API Health Status</a></p>
        </div>
    </body>
    </html>
    """)


@app.get("/health", tags=["Monitoring & Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "nova-prompt-optimizer-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
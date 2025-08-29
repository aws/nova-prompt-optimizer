# Let me create a clean working version
# First, let me copy the working parts and create a minimal dashboard

import os
import json
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fasthtml.common import *
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

# Import Shad4FastHTML components
from shad4fast import ShadHead, Button, Input, Textarea, Alert, Switch, Accordion, AccordionItem, AccordionTrigger, AccordionContent, Tabs, TabsList, TabsTrigger, TabsContent, Card

# Import existing components
from components.layout import create_main_layout
from components.metrics_page import create_metrics_page, create_metric_tabs

# Import database
from database import db
from services.metric_service import MetricService
from components.navbar import create_navbar, create_navbar_styles, create_navbar_script
from components.ui import Card, CardContainer, FormField, Badge, CardSection, CardNested, MainContainer

# Nova Prompt Optimizer SDK imports
try:
    from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
    from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
    from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
    from amzn_nova_prompt_optimizer.core.evaluation import Evaluator
    SDK_AVAILABLE = True
    print("✅ Nova Prompt Optimizer SDK loaded successfully")
except ImportError as e:
    SDK_AVAILABLE = False
    print(f"⚠️ Nova Prompt Optimizer SDK not available: {e}")
    print("   Optimization will run in demo mode")

# Import simple generator routes
from simple_routes import create_simple_generator_routes

# Maintain backward compatibility for existing imports
try:
    from services.simple_dataset_generator import SimpleDatasetGenerator
except ImportError:
    from simple_dataset_generator import SimpleDatasetGenerator

try:
    from services.dataset_conversation import DatasetConversationService
except ImportError:
    from dataset_conversation import DatasetConversationService

# Data storage
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Mock user class
class MockUser:
    def __init__(self, username="demo"):
        self.username = username
        self.email = f"{username}@example.com"
    
    def to_dict(self):
        return {"username": self.username, "email": self.email}

async def get_current_user(request):
    return MockUser()

# Create FastHTML app
app = FastHTML(
    hdrs=[
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        Script("""
            // Delete confirmation dialog
            function confirmDelete(type, id, name) {
                const typeNames = {
                    'dataset': 'dataset',
                    'prompt': 'prompt', 
                    'optimization': 'optimization job'
                };
                
                const typeName = typeNames[type] || type;
                const message = `Are you sure you want to delete the ${typeName} "${name}"?\\n\\nThis action cannot be undone.`;
                
                if (confirm(message)) {
                    // Create a form and submit it for deletion
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/${type}s/delete/${id}`;
                    
                    // Add CSRF token if needed (placeholder)
                    const csrfToken = document.querySelector('meta[name="csrf-token"]');
                    if (csrfToken) {
                        const csrfInput = document.createElement('input');
                        csrfInput.type = 'hidden';
                        csrfInput.name = 'csrf_token';
                        csrfInput.value = csrfToken.content;
                        form.appendChild(csrfInput);
                    }
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            }
        """)
    ]
)

# Initialize generator sessions storage
app.generator_sessions = {}

# Setup routes
from routes.prompt_builder import setup_prompt_builder_routes
from routes.simple_optimizer import setup_simple_optimizer_routes
from routes.dataset_generator import setup_dataset_generator_routes
from routes.datasets import setup_dataset_routes
from routes.prompts import setup_prompt_routes
from routes.prompt_generator import setup_prompt_generator_routes
from routes.metrics_infer_assets import setup_infer_assets_routes
from routes.metrics import setup_metric_routes
from routes.optimization import setup_optimization_routes

# Initialize all routes
setup_prompt_builder_routes(app)
setup_simple_optimizer_routes(app)
setup_dataset_generator_routes(app)
setup_dataset_routes(app)
setup_prompt_routes(app)
setup_prompt_generator_routes(app)
setup_infer_assets_routes(app)
setup_metric_routes(app)
setup_optimization_routes(app)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add flexible generator routes
create_simple_generator_routes(app)  # Works with any format

# Root route - Dashboard
@app.get("/")
async def index(request):
    """Main dashboard page"""
    user = await get_current_user(request)
    
    # Get data from SQLite database
    uploaded_datasets = db.get_datasets()
    created_prompts = db.get_prompts()
    optimization_runs = db.get_optimizations()
    metrics = db.get_metrics()
    
    # Enhanced dashboard with nested card structure
    return create_main_layout(
        "Dashboard",
        MainContainer(
            CardSection(
                H2("System Overview", cls="text-2xl font-semibold"),
                
                # Stats nested cards
                Div(
                    CardNested(
                        H3("Prompts", cls="text-lg font-medium"),
                        Div(
                            H3(str(len(created_prompts)), cls="text-3xl font-bold text-primary mb-2"),
                            P("Active prompt templates", cls="text-sm text-muted-foreground"),
                            A("Manage →", href="/prompts", cls="inline-flex items-center text-sm text-primary hover:underline mt-2")
                        )
                    ),
                    
                    CardNested(
                        H3("Datasets", cls="text-lg font-medium"),
                        Div(
                            H3(str(len(uploaded_datasets)), cls="text-3xl font-bold text-primary mb-2"),
                            P("Total uploaded datasets", cls="text-sm text-muted-foreground"),
                            A("View All →", href="/datasets", cls="inline-flex items-center text-sm text-primary hover:underline mt-2")
                        )
                    ),
                    
                    CardNested(
                        H3("Metrics", cls="text-lg font-medium"),
                        Div(
                            H3(str(len(metrics)), cls="text-3xl font-bold text-primary mb-2"),
                            P("Available evaluation metrics", cls="text-sm text-muted-foreground"),
                            A("Configure →", href="/metrics", cls="inline-flex items-center text-sm text-primary hover:underline mt-2")
                        )
                    ),
                    
                    CardNested(
                        H3("Optimizations", cls="text-lg font-medium"),
                        Div(
                            H3(str(len(optimization_runs)), cls="text-3xl font-bold text-primary mb-2"),
                            P("Completed optimizations", cls="text-sm text-muted-foreground"),
                            A("View Results →", href="/optimization", cls="inline-flex items-center text-sm text-primary hover:underline mt-2")
                        )
                    ),
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
                )
            ),
            
            CardSection(
                H2("Quick Actions", cls="text-2xl font-semibold"),
                
                Div(
                    CardNested(
                        H3("Start New Optimization", cls="text-lg font-medium"),
                        Div(
                            P("Create and optimize prompts with Nova AI", cls="text-sm text-muted-foreground mb-4"),
                            Button("Start Optimization", 
                                   hx_get="/optimization", 
                                   hx_target="body", 
                                   cls="bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2")
                        )
                    ),
                    
                    CardNested(
                        H3("Upload Dataset", cls="text-lg font-medium"),
                        Div(
                            P("Add new training data for optimization", cls="text-sm text-muted-foreground mb-4"),
                            Button("Upload Data", 
                                   hx_get="/datasets", 
                                   hx_target="body",
                                   variant="secondary",
                                   cls="border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2")
                        )
                    ),
                    
                    CardNested(
                        H3("View Metrics", cls="text-lg font-medium"),
                        Div(
                            P("Analyze optimization performance", cls="text-sm text-muted-foreground mb-4"),
                            Button("View Metrics", 
                                   hx_get="/metrics", 
                                   hx_target="body",
                                   variant="secondary",
                                   cls="border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2")
                        )
                    ),
                    cls="grid grid-cols-1 md:grid-cols-3 gap-4"
                )
            )
        )
    )

@app.get("/test")
async def test_page(request):
    return H1("Test page works!")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Nova Prompt Optimizer...")
    uvicorn.run(app, host="127.0.0.1", port=8000)


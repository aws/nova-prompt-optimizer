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
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

# Import existing components
from components.layout import create_main_layout, create_navigation, create_page_layout

# Import database
from database import db
from components.navbar import create_navbar, create_navbar_styles, create_navbar_script
from components.ui import Button, Card, CardContainer, Textarea, Input, FormField, Badge, Alert, create_ui_styles

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
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
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
            
            // Show success/error messages
            function showMessage(message, type = 'success') {
                const messageDiv = document.createElement('div');
                messageDiv.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 20px;
                    border-radius: 6px;
                    color: white;
                    font-weight: 500;
                    z-index: 1000;
                    background: ${type === 'success' ? '#10b981' : '#ef4444'};
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                `;
                messageDiv.textContent = message;
                
                document.body.appendChild(messageDiv);
                
                // Remove after 3 seconds
                setTimeout(() => {
                    messageDiv.remove();
                }, 3000);
            }
        """)
    ]
)

# Root route - Dashboard
@app.get("/")
async def index(request):
    """Main dashboard page"""
    user = await get_current_user(request)
    
    # Get data from SQLite database
    uploaded_datasets = db.get_datasets()
    created_prompts = db.get_prompts()
    optimization_runs = db.get_optimizations()
    
    # Enhanced dashboard with nested card structure
    return create_page_layout(
        "Dashboard",
        content=[
            Card(
                header=H3("Overview"),
                content=Div(
                    Div(
                        A(
                            Div(
                                H3(str(len(uploaded_datasets)), style="font-size: 2rem; margin: 0; color: #667eea;"),
                                P("Datasets", style="margin: 0; color: #6b7280; font-weight: 500;"),
                                style="text-align: center;"
                            ),
                            href="/datasets",
                            style="text-decoration: none; display: block; padding: 1rem; border-radius: 0.5rem; transition: background-color 0.2s ease;",
                            onmouseover="this.style.backgroundColor='#f8f9fa'",
                            onmouseout="this.style.backgroundColor='transparent'"
                        ),
                        A(
                            Div(
                                H3(str(len(created_prompts)), style="font-size: 2rem; margin: 0; color: #667eea;"),
                                P("Prompts", style="margin: 0; color: #6b7280; font-weight: 500;"),
                                style="text-align: center;"
                            ),
                            href="/prompts",
                            style="text-decoration: none; display: block; padding: 1rem; border-radius: 0.5rem; transition: background-color 0.2s ease;",
                            onmouseover="this.style.backgroundColor='#f8f9fa'",
                            onmouseout="this.style.backgroundColor='transparent'"
                        ),
                        A(
                            Div(
                                H3(str(len(optimization_runs)), style="font-size: 2rem; margin: 0; color: #667eea;"),
                                P("Optimizations", style="margin: 0; color: #6b7280; font-weight: 500;"),
                                style="text-align: center;"
                            ),
                            href="/optimization",
                            style="text-decoration: none; display: block; padding: 1rem; border-radius: 0.5rem; transition: background-color 0.2s ease;",
                            onmouseover="this.style.backgroundColor='#f8f9fa'",
                            onmouseout="this.style.backgroundColor='transparent'"
                        ),
                        style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;"
                    )
                ),
                nested=True
            ),
            
            Card(
                header=H3("Recent Activity"),
                content=Div(
                    P("Welcome to Nova Prompt Optimizer! Get started by exploring your data and creating optimized prompts.", 
                      style="color: #6b7280; margin-bottom: 1rem;"),
                    Div(
                        A("View All Datasets", href="/datasets", 
                          style="color: #667eea; text-decoration: none; margin-right: 1rem; font-weight: 500;"),
                        A("Browse Prompts", href="/prompts", 
                          style="color: #667eea; text-decoration: none; margin-right: 1rem; font-weight: 500;"),
                        A("View Results", href="/results", 
                          style="color: #667eea; text-decoration: none; font-weight: 500;")
                    )
                ),
                nested=True
            )
        ],
        current_page="dashboard",
        user=user.to_dict() if user else None
    )

# Test route
@app.get("/test")
async def test_page(request):
    return H1("Test page works!")

# Essential routes for clickable dashboard links
@app.get("/datasets")
async def datasets_page(request):
    """Datasets page"""
    user = await get_current_user(request)
    
    # Check for success/error messages
    deleted = request.query_params.get("deleted")
    uploaded = request.query_params.get("uploaded")
    error = request.query_params.get("error")
    
    success_message = None
    error_message = None
    
    if deleted == "dataset":
        success_message = "Dataset deleted successfully!"
    elif uploaded == "true":
        success_message = "Dataset uploaded successfully!"
    elif error == "no_file":
        error_message = "Please select a file to upload."
    elif error == "unsupported_format":
        error_message = "Unsupported file format. Please upload CSV or JSON files."
    elif error == "upload_failed":
        error_message = "Failed to upload dataset. Please try again."
    
    # Get datasets from SQLite database
    sample_datasets = db.get_datasets()
    
    content = [
        Card(
            header=H3("Upload Dataset"),
            content=Div(
                P("Upload your training data in CSV or JSON format.", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                # Dataset upload form
                Form(
                    Div(
                        Label("Dataset Name:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(
                            type="text", 
                            name="dataset_name", 
                            placeholder="Enter dataset name (optional - will use filename)",
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Label("Select File:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(
                            type="file", 
                            name="dataset_file", 
                            accept=".csv,.json,.jsonl",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        P("Supported formats: CSV, JSON, JSONL", 
                          style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                        style="margin-bottom: 1rem;"
                    ),
                    Button(
                        "📁 Upload Dataset", 
                        type="submit",
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"
                    ),
                    method="POST",
                    action="/datasets/upload",
                    enctype="multipart/form-data"
                )
            ),
            nested=True
        ),
        Card(
            header=H3("Your Datasets"),
            content=Div(
                *[Div(
                    Div(
                        H4(dataset["name"], style="margin: 0 0 0.5rem 0; color: #1f2937;"),
                        P(f"{dataset['type']} • {dataset['size']} • {dataset['rows']:,} rows", 
                          style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;"),
                        P(f"Created: {dataset['created']} • Status: {dataset['status']}", 
                          style="margin: 0; color: #6b7280; font-size: 0.875rem;")
                    ),
                    Div(
                        Button("View", variant="outline", style="margin-right: 0.5rem; font-size: 0.875rem;"),
                        Button("Edit", variant="ghost", style="margin-right: 0.5rem; font-size: 0.875rem;"),
                        Button("Delete", 
                               variant="danger", 
                               style="font-size: 0.875rem; background: #ef4444; color: white; border: 1px solid #ef4444;",
                               onclick=f"confirmDelete('dataset', '{dataset['id']}', '{dataset['name']}')",
                               **{"data-dataset-id": dataset["id"]}),
                        style="display: flex; gap: 0.25rem;"
                    ),
                    style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.75rem;"
                ) for dataset in sample_datasets] if sample_datasets else [
                    P("No datasets uploaded yet. Upload your first dataset to get started!", 
                      style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            ),
            nested=True
        )
    ]
    
    # Add success/error message scripts if needed
    if success_message:
        content.append(Script(f"showMessage('{success_message}', 'success');"))
    elif error_message:
        content.append(Script(f"showMessage('{error_message}', 'error');"))
    
    return create_page_layout(
        "Datasets",
        content=content,
        current_page="datasets",
        user=user.to_dict() if user else None
    )

@app.get("/prompts")
async def prompts_page(request):
    """Prompts page"""
    user = await get_current_user(request)
    
    # Check for success/error messages
    deleted = request.query_params.get("deleted")
    created = request.query_params.get("created")
    error = request.query_params.get("error")
    
    success_message = None
    error_message = None
    
    if deleted == "prompt":
        success_message = "Prompt deleted successfully!"
    elif created == "true":
        success_message = "Prompt created successfully!"
    elif error == "no_name":
        error_message = "Please enter a prompt name."
    elif error == "no_content":
        error_message = "Please enter at least one prompt (system or user)."
    elif error == "create_failed":
        error_message = "Failed to create prompt. Please try again."
    
    # Get prompts from SQLite database
    sample_prompts = db.get_prompts()
    
    content = [
        Card(
            header=H3("Create Prompt"),
            content=Div(
                P("Create system and user prompts for optimization.", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                # Prompt creation form
                Form(
                    Div(
                        Label("Prompt Name:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(
                            type="text", 
                            name="prompt_name", 
                            placeholder="Enter prompt name",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Label("System Prompt:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Textarea(
                            name="system_prompt", 
                            placeholder="Enter system prompt (optional)\n\nExample: You are a helpful assistant that classifies emails...",
                            rows=4,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem; font-family: monospace; resize: vertical;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Label("User Prompt:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Textarea(
                            name="user_prompt", 
                            placeholder="Enter user prompt (optional)\n\nExample: Classify this email: {email_content}\n\nCategories: {categories}",
                            rows=4,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem; font-family: monospace; resize: vertical;"
                        ),
                        P("Note: At least one prompt (system or user) is required.", 
                          style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                        style="margin-bottom: 1rem;"
                    ),
                    Button(
                        "✨ Create Prompt", 
                        type="submit",
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"
                    ),
                    method="POST",
                    action="/prompts/create"
                )
            ),
            nested=True
        ),
        Card(
            header=H3("Your Prompts"),
            content=Div(
                *[Div(
                    Div(
                        H4(prompt["name"], style="margin: 0 0 0.5rem 0; color: #1f2937;"),
                        P(f"{prompt['type']} • Variables: {', '.join(prompt['variables'])}", 
                          style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;"),
                        P(f"Created: {prompt['created']} • Performance: {prompt['performance']}", 
                          style="margin: 0; color: #6b7280; font-size: 0.875rem;")
                    ),
                    Div(
                        Button("Edit", variant="outline", style="margin-right: 0.5rem; font-size: 0.875rem;"),
                        Button("Test", variant="ghost", style="margin-right: 0.5rem; font-size: 0.875rem;"),
                        Button("Delete", 
                               variant="danger", 
                               style="font-size: 0.875rem; background: #ef4444; color: white; border: 1px solid #ef4444;",
                               onclick=f"confirmDelete('prompt', '{prompt['id']}', '{prompt['name']}')",
                               **{"data-prompt-id": prompt["id"]}),
                        style="display: flex; gap: 0.25rem;"
                    ),
                    style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.75rem;"
                ) for prompt in sample_prompts] if sample_prompts else [
                    P("No prompts created yet. Create your first prompt template to get started!", 
                      style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            ),
            nested=True
        )
    ]
    
    # Add success/error message scripts if needed
    if success_message:
        content.append(Script(f"showMessage('{success_message}', 'success');"))
    elif error_message:
        content.append(Script(f"showMessage('{error_message}', 'error');"))
    
    return create_page_layout(
        "Prompts",
        content=content,
        current_page="prompts",
        user=user.to_dict() if user else None
    )

@app.get("/optimization")
async def optimization_page(request):
    """Optimization page"""
    user = await get_current_user(request)
    
    # Check for success/error messages
    deleted = request.query_params.get("deleted")
    started = request.query_params.get("started")
    error = request.query_params.get("error")
    
    success_message = None
    error_message = None
    
    if deleted == "optimization":
        success_message = "Optimization job deleted successfully!"
    elif started == "true":
        success_message = "Optimization started successfully!"
    elif error == "missing_data":
        error_message = "Please select both a prompt and dataset to start optimization."
    elif error == "start_failed":
        error_message = "Failed to start optimization. Please try again."
    
    # Get optimizations from SQLite database
    sample_optimizations = db.get_optimizations()
    
    # Get available prompts and datasets for the form
    available_prompts = db.get_prompts()
    available_datasets = db.get_datasets()
    
    content = [
        Card(
            header=H3("Start New Optimization"),
            content=Div(
                P("Configure and start prompt optimization runs here.", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                # Optimization start form
                Form(
                    Div(
                        Label("Optimization Name:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(
                            type="text", 
                            name="name", 
                            placeholder="Enter optimization name (optional)",
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Label("Select Prompt:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Select(
                            Option("Choose a prompt...", value="", disabled=True, selected=True),
                            *[Option(f"{prompt['name']} ({prompt['type']})", value=prompt["id"]) 
                              for prompt in available_prompts],
                            name="prompt_id",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    Div(
                        Label("Select Dataset:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Select(
                            Option("Choose a dataset...", value="", disabled=True, selected=True),
                            *[Option(f"{dataset['name']} ({dataset['type']}, {dataset['rows']} rows)", value=dataset["id"]) 
                              for dataset in available_datasets],
                            name="dataset_id",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    # Advanced Configuration Section
                    Div(
                        Div(
                            "⚙️ Advanced Configuration", 
                            style="font-weight: 500; cursor: pointer; margin-bottom: 1rem; padding: 0.5rem; background: #f3f4f6; border-radius: 0.375rem;",
                            onclick="document.getElementById('advanced-config').style.display = document.getElementById('advanced-config').style.display === 'none' ? 'block' : 'none'"
                        ),
                        Div(
                            # Model Selection
                            Div(
                                Label("Nova Model:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                                Select(
                                    Option("Lite (Fast, Cost-effective)", value="lite", selected=True),
                                    Option("Pro (Balanced Performance)", value="pro"),
                                    Option("Premier (Highest Quality)", value="premier"),
                                    name="model_mode",
                                    style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                                ),
                                P("Lite: Fast optimization, Pro: Balanced quality/speed, Premier: Best results", 
                                  style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                                style="margin-bottom: 1rem;"
                            ),
                            # Dataset Record Limit
                            Div(
                                Label("Dataset Records to Process:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                                Input(
                                    type="number", 
                                    name="record_limit", 
                                    placeholder="Leave empty to use all records",
                                    min="1",
                                    max="10000",
                                    style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                                ),
                                P("Limit the number of records to process for faster testing (1-10,000)", 
                                  style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                                style="margin-bottom: 1rem;"
                            ),
                            # Rate Limit
                            Div(
                                Label("Rate Limit (RPM):", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                                Input(
                                    type="number", 
                                    name="rate_limit", 
                                    placeholder="60",
                                    value="60",
                                    min="1",
                                    max="1000",
                                    style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                                ),
                                P("Requests per minute to avoid throttling (1-1000, default: 60)", 
                                  style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                                style="margin-bottom: 1rem;"
                            ),
                            style="padding: 1rem; background: #f8fafc; border-radius: 0.375rem; margin-bottom: 1rem; display: none;",
                            id="advanced-config"
                        )
                    ),
                    Button(
                        "🚀 Start Optimization", 
                        type="submit",
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"
                    ),
                    method="POST",
                    action="/optimization/start"
                ) if available_prompts and available_datasets else P(
                    "⚠️ You need at least one prompt and one dataset to start optimization.",
                    style="color: #f59e0b; font-weight: 500; padding: 1rem; background: #fef3c7; border-radius: 0.375rem;"
                )
            ),
            nested=True
        ),
        Card(
            header=H3("Optimization Runs"),
            content=Div(
                *[Div(
                    Div(
                        H4(opt["name"], style="margin: 0 0 0.5rem 0; color: #1f2937;"),
                        P(f"Prompt: {opt['prompt']} • Dataset: {opt['dataset']}", 
                          style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;"),
                        P(f"Started: {opt['started']} • Status: {opt['status']}", 
                          style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;"),
                        Div(
                            Div(
                                style=f"width: {opt['progress']}%; height: 4px; background: #10b981; border-radius: 2px;"
                            ),
                            style="width: 100%; height: 4px; background: #e5e7eb; border-radius: 2px; margin-top: 0.5rem;"
                        ) if opt["status"] in ["Starting", "Running"] else None
                    ),
                    Div(
                        Div(
                            P(opt["improvement"], 
                              style="margin: 0; font-weight: 600; color: #10b981;" if opt["improvement"].startswith("+") else "margin: 0; font-weight: 600; color: #6b7280;"),
                            P("improvement", style="margin: 0; font-size: 0.75rem; color: #6b7280;"),
                            style="text-align: center; margin-bottom: 0.5rem;"
                        ),
                        Div(
                            Button("View Results" if opt["status"] == "Completed" else "Monitor", 
                                   variant="outline", 
                                   style="font-size: 0.875rem; margin-right: 0.5rem;",
                                   onclick=f"window.location.href='/optimization/{opt['id']}/monitor'" if opt["status"] != "Completed" else ""),
                            Button("Stop" if opt["status"] in ["Starting", "Running"] else "Delete", 
                                   variant="danger", 
                                   style="font-size: 0.875rem; background: #ef4444; color: white; border: 1px solid #ef4444;",
                                   onclick=f"confirmDelete('optimization', '{opt['id']}', '{opt['name']}')",
                                   **{"data-optimization-id": opt["id"]}),
                            style="display: flex; gap: 0.25rem;"
                        ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    style="display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.75rem;"
                ) for opt in sample_optimizations] if sample_optimizations else [
                    P("No optimization runs yet. Start your first optimization to improve your prompts!", 
                      style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            ),
            nested=True
        )
    ]
    
    # Add success/error message scripts if needed
    if success_message:
        content.append(Script(f"showMessage('{success_message}', 'success');"))
    elif error_message:
        content.append(Script(f"showMessage('{error_message}', 'error');"))
    
    return create_page_layout(
        "Optimization",
        content=content,
        current_page="optimization",
        user=user.to_dict() if user else None
    )

@app.get("/results")
async def results_page(request):
    """Results page"""
    user = await get_current_user(request)
    return create_page_layout(
        "Results",
        content=[
            Card(
                header=H3("Optimization Results"),
                content=P("View and analyze your optimization results here."),
                nested=True
            )
        ],
        current_page="results",
        user=user.to_dict() if user else None
    )

# Delete routes
@app.post("/datasets/delete/{dataset_id}")
async def delete_dataset(request):
    """Delete a dataset"""
    dataset_id = request.path_params["dataset_id"]
    
    # Delete from SQLite database
    deleted = db.delete_dataset(dataset_id)
    
    if deleted:
        print(f"✅ Deleted dataset: {dataset_id}")
        print(f"📊 Remaining datasets: {len(db.get_datasets())}")
    else:
        print(f"❌ Dataset not found: {dataset_id}")
    
    # Redirect back to datasets page with success message
    return RedirectResponse(url="/datasets?deleted=dataset", status_code=302)

@app.post("/prompts/delete/{prompt_id}")
async def delete_prompt(request):
    """Delete a prompt"""
    prompt_id = request.path_params["prompt_id"]
    
    # Delete from SQLite database
    deleted = db.delete_prompt(prompt_id)
    
    if deleted:
        print(f"✅ Deleted prompt: {prompt_id}")
        print(f"📝 Remaining prompts: {len(db.get_prompts())}")
    else:
        print(f"❌ Prompt not found: {prompt_id}")
    
    # Redirect back to prompts page with success message
    return RedirectResponse(url="/prompts?deleted=prompt", status_code=302)

@app.post("/optimizations/delete/{optimization_id}")
async def delete_optimization(request):
    """Delete an optimization job"""
    optimization_id = request.path_params["optimization_id"]
    
    # Create fresh database instance to avoid connection issues
    import database as db_module
    fresh_db = db_module.Database()
    
    # Delete from SQLite database
    deleted = fresh_db.delete_optimization(optimization_id)
    
    if deleted:
        print(f"✅ Deleted optimization: {optimization_id}")
        print(f"⚡ Remaining optimizations: {len(fresh_db.get_optimizations())}")
    else:
        print(f"❌ Optimization not found: {optimization_id}")
    
    # Redirect back to optimization page with success message
    return RedirectResponse(url="/optimization?deleted=optimization", status_code=302)

# Real optimization routes
@app.post("/optimization/start")
async def start_optimization(request):
    """Start a real optimization run"""
    try:
        # Get form data
        form_data = await request.form()
        prompt_id = form_data.get("prompt_id")
        dataset_id = form_data.get("dataset_id")
        optimization_name = form_data.get("name", f"Optimization {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Get advanced configuration
        model_mode = form_data.get("model_mode", "lite")  # lite, pro, premier
        record_limit = form_data.get("record_limit", "")
        rate_limit = form_data.get("rate_limit", "60")
        
        # Validate required fields
        if not prompt_id or not dataset_id:
            return RedirectResponse(url="/optimization?error=missing_data", status_code=302)
        
        # Debug: Log what we received
        print(f"🔍 Received prompt_id: {prompt_id}")
        print(f"🔍 Received dataset_id: {dataset_id}")
        
        # Verify the prompt exists
        try:
            import sys
            import os
            # Add current directory to path to ensure we get our database module
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # Import our specific database module
            import database as db_module
            db = db_module.Database()
            print(f"🔍 Database initialized successfully")
            
            prompt_data = db.get_prompt(prompt_id)
            print(f"🔍 Prompt lookup completed")
            
            if not prompt_data:
                print(f"❌ Prompt not found for ID: {prompt_id}")
                return RedirectResponse(url="/optimization?error=prompt_not_found", status_code=302)
                
            print(f"🔍 Prompt found: {prompt_data['name']}")
            
            # Also verify dataset exists
            dataset_data = db.get_dataset(dataset_id)
            print(f"🔍 Dataset lookup completed")
            
            if not dataset_data:
                print(f"❌ Dataset not found for ID: {dataset_id}")
                return RedirectResponse(url="/optimization?error=dataset_not_found", status_code=302)
                
            print(f"🔍 Dataset found: {dataset_data['name']}")
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            import traceback
            traceback.print_exc()
            return RedirectResponse(url="/optimization?error=database_error", status_code=302)
        
        # Validate and convert numeric fields
        try:
            rate_limit_int = int(rate_limit) if rate_limit else 60
            rate_limit_int = max(1, min(1000, rate_limit_int))  # Clamp between 1-1000
        except ValueError:
            rate_limit_int = 60
        
        record_limit_int = None
        if record_limit:
            try:
                record_limit_int = int(record_limit)
                record_limit_int = max(1, min(10000, record_limit_int))  # Clamp between 1-10000
            except ValueError:
                record_limit_int = None
        
        # Create optimization record with configuration
        try:
            optimization_id = db.create_optimization(optimization_name, prompt_id, dataset_id)
            print(f"✅ Created optimization record: {optimization_id}")
        except Exception as e:
            print(f"❌ Error creating optimization: {e}")
            return RedirectResponse(url="/optimization?error=start_failed", status_code=302)
        
        # Verify the record was created
        created_opt = db.get_optimization_by_id(optimization_id)
        if created_opt:
            print(f"✅ Verified optimization in database: {created_opt['name']} - {created_opt['status']}")
        else:
            print(f"❌ Failed to verify optimization in database")
        
        # Store configuration in optimization record (we'll need to update the database schema for this)
        optimization_config = {
            "model_mode": model_mode,
            "record_limit": record_limit_int,
            "rate_limit": rate_limit_int
        }
        
        if SDK_AVAILABLE:
            # Start optimization in separate worker process
            import subprocess
            import json
            
            config_json = json.dumps(optimization_config)
            worker_cmd = [
                "/Users/tsanti/Development/Publish/nova-prompt-optimizer/.venv/bin/python3", 
                "frontend/sdk_worker.py", 
                optimization_id, 
                config_json
            ]
            
            # Start worker process in background (run from main project directory)
            main_project_dir = Path(__file__).parent.parent
            subprocess.Popen(worker_cmd, cwd=main_project_dir)
            print(f"✅ Started optimization worker process: {optimization_id} (Mode: {model_mode}, Rate: {rate_limit_int} RPM, Records: {record_limit_int or 'All'})")
        else:
            # Demo mode - simulate optimization in worker
            import subprocess
            
            worker_cmd = [
                "/Users/tsanti/Development/Publish/nova-prompt-optimizer/.venv/bin/python3", 
                "sdk_worker.py", 
                optimization_id
            ]
            
            subprocess.Popen(worker_cmd, cwd=Path(__file__).parent)
            print(f"🎭 Started demo optimization worker: {optimization_id}")
        
        return RedirectResponse(url="/optimization?started=true", status_code=302)
        
    except Exception as e:
        print(f"❌ Error starting optimization: {e}")
        return RedirectResponse(url="/optimization?error=start_failed", status_code=302)

@app.get("/optimization/{optimization_id}/logs")
async def get_optimization_logs(request):
    """Get optimization logs and status (for AJAX polling)"""
    optimization_id = request.path_params["optimization_id"]
    
    optimization = db.get_optimization_by_id(optimization_id)
    if not optimization:
        return JSONResponse({"error": "Optimization not found"}, status_code=404)
    
    logs = db.get_optimization_logs(optimization_id)
    
    return JSONResponse({
        "id": optimization["id"],
        "status": optimization["status"],
        "progress": optimization["progress"],
        "improvement": optimization["improvement"],
        "logs": logs,
        "metrics": None  # Will be populated when metrics are available
    })

@app.get("/optimization/{optimization_id}/candidates")
def get_optimization_candidates(optimization_id: str):
    """Get prompt candidates for an optimization"""
    db = Database()
    candidates = db.get_prompt_candidates(optimization_id)
    return {"candidates": candidates}

@app.get("/optimization/{optimization_id}/prompts")
async def view_prompts(request):
    """View baseline vs optimized prompts"""
    optimization_id = request.path_params['optimization_id']
    db = Database()
    
    # Get prompt candidates
    candidates = db.get_prompt_candidates(optimization_id)
    
    baseline_system = None
    baseline_user = None
    final_system = None
    final_user = None
    few_shot_count = 0
    few_shot_sample = None
    
    for candidate in candidates:
        if candidate['iteration'] == 'BASELINE_SYSTEM':
            baseline_system = candidate['user_prompt']
        elif candidate['iteration'] == 'BASELINE_USER':
            baseline_user = candidate['user_prompt']
        elif candidate['iteration'] == 'FINAL_SYSTEM':
            final_system = candidate['user_prompt']
        elif candidate['iteration'] == 'FINAL_USER':
            final_user = candidate['user_prompt']
        elif candidate['iteration'] == 'FEW_SHOT_COUNT':
            few_shot_count = int(candidate['user_prompt']) if candidate['user_prompt'].isdigit() else 0
        elif candidate['iteration'] == 'FEW_SHOT_SAMPLE':
            few_shot_sample = candidate['user_prompt']
    
    return create_main_layout(
        "Prompt Comparison",
        Div(
            H1("Prompt Comparison", cls="text-2xl font-bold mb-6"),
            
            # Baseline vs Optimized comparison
            Div(
                Div(
                    H2("Baseline System Prompt", cls="text-lg font-semibold mb-2"),
                    Pre(baseline_system or "No baseline system prompt", 
                        cls="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap border max-h-64 overflow-y-auto"),
                    cls="mb-6"
                ),
                
                Div(
                    H2("Optimized System Prompt", cls="text-lg font-semibold mb-2"),
                    Pre(final_system or "No optimized system prompt", 
                        cls="bg-blue-50 p-4 rounded text-sm whitespace-pre-wrap border max-h-64 overflow-y-auto"),
                    cls="mb-6"
                ),
                
                Div(
                    H2("Baseline User Prompt", cls="text-lg font-semibold mb-2"),
                    Pre(baseline_user or "No baseline user prompt", 
                        cls="bg-gray-100 p-4 rounded text-sm whitespace-pre-wrap border"),
                    cls="mb-6"
                ),
                
                Div(
                    H2("Optimized User Prompt", cls="text-lg font-semibold mb-2"),
                    Pre(final_user or "No optimized user prompt", 
                        cls="bg-blue-50 p-4 rounded text-sm whitespace-pre-wrap border"),
                    cls="mb-6"
                ),
                
                # Comparison summary
                Div(
                    H3("Comparison Summary", cls="text-lg font-semibold mb-2"),
                    P(f"System prompts identical: {'Yes' if baseline_system == final_system else 'No'}", 
                      cls="mb-1"),
                    P(f"User prompts identical: {'Yes' if baseline_user == final_user else 'No'}", 
                      cls="mb-1"),
                    P(f"Few-shot examples added: {few_shot_count}", cls="mb-1"),
                    cls="bg-yellow-50 p-4 rounded border"
                ),
                
                # Few-shot examples section
                Div(
                    H3("Few-shot Examples", cls="text-lg font-semibold mb-2"),
                    P(f"Number of examples: {few_shot_count}", cls="mb-2"),
                    Div(
                        H4("Sample Example:", cls="font-medium mb-1"),
                        Pre(few_shot_sample or "No sample available", 
                            cls="bg-green-50 p-3 rounded text-xs whitespace-pre-wrap border max-h-32 overflow-y-auto"),
                        cls="mb-4"
                    ) if few_shot_sample else P("No few-shot examples", cls="text-gray-500"),
                    cls="bg-green-50 p-4 rounded border"
                ) if few_shot_count > 0 else None,
                
                A("← Back to Monitor", href=f"/optimization/{optimization_id}/monitor", 
                  cls="inline-block mt-4 text-blue-600 hover:underline")
            )
        ),
        current_page="optimization"
    )

@app.get("/optimization/{optimization_id}/monitor")
async def monitor_optimization(request):
    """Monitor optimization progress page with detailed logs"""
    optimization_id = request.path_params["optimization_id"]
    user = await get_current_user(request)
    
    optimization = db.get_optimization_by_id(optimization_id)
    if not optimization:
        return RedirectResponse(url="/optimization?error=not_found", status_code=302)
    
    # Get optimization logs and candidates
    logs = db.get_optimization_logs(optimization_id)
    try:
        candidates = db.get_prompt_candidates(optimization_id)
        print(f"DEBUG: Found {len(candidates)} candidates for {optimization_id}")
        for c in candidates:
            print(f"  - {c['iteration']}: {c['user_prompt'][:50]}... (score: {c['score']})")
    except Exception as e:
        print(f"Error getting candidates: {e}")
        candidates = []
    
    content = [
        Card(
            header=H3(f"🔍 Monitoring: {optimization['name']}"),
            content=Div(
                # Optimization Overview
                Div(
                    H4("Optimization Overview", style="margin-bottom: 0.5rem; color: #1f2937;"),
                    Div(
                        Div(
                            P(f"📝 Prompt: {optimization['prompt']}", style="margin: 0.25rem 0;"),
                            P(f"📊 Dataset: {optimization['dataset']}", style="margin: 0.25rem 0;"),
                            P(f"🕐 Started: {optimization['started']}", style="margin: 0.25rem 0;"),
                            style="flex: 1;"
                        ),
                        Div(
                            P(f"Status: {optimization['status']}", 
                              style="font-weight: 600; margin: 0.25rem 0; color: #10b981;" if optimization['status'] == 'Completed' else "font-weight: 600; margin: 0.25rem 0;",
                              id="status-text"),
                            P(f"Progress: {optimization['progress']}%", 
                              style="margin: 0.25rem 0;",
                              id="progress-text"),
                            P(f"Improvement: {optimization['improvement']}", 
                              style="font-weight: 600; color: #10b981;" if optimization['improvement'].startswith('+') else "font-weight: 600;",
                              id="improvement-text"),
                            style="flex: 1;"
                        ),
                        style="display: flex; gap: 2rem; margin-bottom: 1rem;"
                    ),
                    # Progress Bar
                    Div(
                        Div(
                            style=f"width: {optimization['progress']}%; height: 8px; background: #10b981; border-radius: 4px; transition: width 0.3s ease;",
                            id="progress-bar"
                        ),
                        style="width: 100%; height: 8px; background: #e5e7eb; border-radius: 4px; margin-bottom: 1rem;"
                    ),
                    style="margin-bottom: 2rem; padding: 1rem; background: #f8fafc; border-radius: 0.5rem;"
                ),
                
                # Prompt Candidates Table - Always show if candidates exist
                Div(
                    H4("🧪 Prompt Candidates", style="margin: 2rem 0 1rem 0; color: #1f2937;"),
                    P(f"Found {len(candidates)} candidates", style="margin-bottom: 1rem; color: #6b7280;"),
                    *([
                        Table(
                            Thead(
                                Tr(
                                    Th("Iteration"),
                                    Th("User Prompt"), 
                                    Th("Score")
                                )
                            ),
                            Tbody(
                                *[Tr(
                                    Td(candidate["iteration"]),
                                    Td(candidate["user_prompt"][:60] + "..."),
                                    Td(f"{candidate['score']:.3f}" if candidate["score"] else "N/A")
                                ) for candidate in candidates]
                            )
                        )
                    ] if candidates else [P("No candidates found yet.")]),
                    style="margin-bottom: 2rem;"
                ),
                
                # Real-time Logs Section
                Div(
                    H4("📋 Real-time SDK Logs", style="margin-bottom: 1rem; color: #1f2937;"),
                    Div(
                        # Log entries will be populated here
                        *[Div(
                            Div(
                                Span(log["timestamp"], style="font-size: 0.75rem; color: #6b7280; font-family: monospace;"),
                                Span(log["log_type"].upper(), 
                                     style=f"font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem; padding: 0.125rem 0.375rem; border-radius: 0.25rem; "
                                           f"{'background: #dcfce7; color: #166534;' if log['log_type'] == 'success' else ''}"
                                           f"{'background: #fef3c7; color: #92400e;' if log['log_type'] == 'warning' else ''}"
                                           f"{'background: #fee2e2; color: #dc2626;' if log['log_type'] == 'error' else ''}"
                                           f"{'background: #dbeafe; color: #1d4ed8;' if log['log_type'] == 'info' else ''}"
                                           f"{'background: #f3f4f6; color: #374151;' if log['log_type'] not in ['success', 'warning', 'error', 'info'] else ''}"),
                                style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;"
                            ),
                            P(log["message"], 
                              style="margin: 0; font-family: monospace; font-size: 0.875rem; color: #1f2937; white-space: pre-wrap; line-height: 1.4;"),
                            # Show structured data if available
                            *([Div(
                                Details(
                                    Summary("📊 View Data", style="cursor: pointer; font-size: 0.75rem; color: #6b7280; margin: 0.5rem 0 0.25rem 0;"),
                                    Pre(json.dumps(log["data"], indent=2), 
                                        style="background: #f9fafb; padding: 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; margin: 0; overflow-x: auto; border: 1px solid #e5e7eb;"),
                                ),
                                style="margin-top: 0.5rem;"
                            )] if log.get("data") else []),
                            style=f"padding: 0.75rem; border-left: 3px solid "
                                  f"{'#10b981' if log['log_type'] == 'success' else ''}"
                                  f"{'#f59e0b' if log['log_type'] == 'warning' else ''}"
                                  f"{'#ef4444' if log['log_type'] == 'error' else ''}"
                                  f"{'#3b82f6' if log['log_type'] == 'info' else ''}"
                                  f"{'#6b7280' if log['log_type'] not in ['success', 'warning', 'error', 'info'] else ''}"
                                  f"; margin-bottom: 0.5rem; background: #fafafa; border-radius: 0 0.375rem 0.375rem 0;"
                        ) for log in logs] if logs else [
                            P("No logs available yet. Logs will appear here as the optimization runs.", 
                              style="color: #6b7280; text-align: center; padding: 2rem; font-style: italic;")
                        ],
                        id="logs-container",
                        style="max-height: 600px; overflow-y: auto; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 1rem; background: white;"
                    ),
                    style="margin-bottom: 2rem;"
                ),
                
                # Evaluator Metrics Section (will be populated when available)
                Div(
                    H4("📈 Evaluator Metrics Breakdown", style="margin-bottom: 1rem; color: #1f2937;"),
                    Div(
                        P("Detailed metrics will appear here when evaluation is complete.", 
                          style="color: #6b7280; text-align: center; padding: 2rem; font-style: italic;"),
                        id="metrics-container"
                    ),
                    style="margin-bottom: 2rem; padding: 1rem; background: #f8fafc; border-radius: 0.5rem;"
                ),
                
                # Action Buttons
                Div(
                    Button("🔄 Refresh Logs", 
                           onclick="refreshLogs()",
                           style="margin-right: 0.5rem; background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                    Button("📊 Auto-refresh: ON", 
                           id="auto-refresh-btn",
                           onclick="toggleAutoRefresh()",
                           style="margin-right: 0.5rem; background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                    Button("📝 View Prompts", 
                           onclick=f"window.location.href='/optimization/{optimization_id}/prompts'",
                           style="margin-right: 0.5rem; background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                    Button("⬅️ Back to Optimization", 
                           onclick="window.location.href='/optimization'",
                           style="background: #6b7280; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                    style="display: flex; gap: 0.5rem;"
                ),
                
                # JavaScript for real-time updates
                Script(f"""
                    const optimizationId = '{optimization_id}';
                    let autoRefreshEnabled = true;
                    let refreshInterval;
                    
                    function refreshLogs() {{
                        fetch(`/optimization/${{optimizationId}}/logs`)
                            .then(response => response.json())
                            .then(data => {{
                                // Update status
                                document.getElementById('status-text').textContent = `Status: ${{data.status}}`;
                                document.getElementById('progress-text').textContent = `Progress: ${{data.progress}}%`;
                                document.getElementById('progress-bar').style.width = `${{data.progress}}%`;
                                document.getElementById('improvement-text').textContent = `Improvement: ${{data.improvement}}`;
                                
                                // Update logs
                                const logsContainer = document.getElementById('logs-container');
                                if (data.logs && data.logs.length > 0) {{
                                    logsContainer.innerHTML = data.logs.map(log => `
                                        <div style="padding: 0.75rem; border-left: 3px solid #e5e7eb; margin-bottom: 0.5rem; background: #fafafa;">
                                            <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                                                <span style="font-size: 0.75rem; color: #6b7280; font-family: monospace;">${{log.timestamp}}</span>
                                                <span style="font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem; padding: 0.125rem 0.375rem; border-radius: 0.25rem; background: #f3f4f6; color: #374151;">${{log.log_type.toUpperCase()}}</span>
                                            </div>
                                            <p style="margin: 0; font-family: monospace; font-size: 0.875rem; color: #1f2937; white-space: pre-wrap;">${{log.message}}</p>
                                            ${{log.data ? `<div style="margin-top: 0.5rem;"><h5 style="margin: 0.5rem 0 0.25rem 0; font-size: 0.75rem; color: #6b7280;">📊 Data:</h5><pre style="background: #f9fafb; padding: 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; margin: 0; overflow-x: auto;">${{JSON.stringify(log.data, null, 2)}}</pre></div>` : ''}}
                                        </div>
                                    `).join('');
                                    
                                    // Auto-scroll to bottom
                                    logsContainer.scrollTop = logsContainer.scrollHeight;
                                }}
                                
                                // Update metrics if available
                                if (data.metrics) {{
                                    const metricsContainer = document.getElementById('metrics-container');
                                    metricsContainer.innerHTML = data.metrics;
                                }}
                            }})
                            .catch(error => console.error('Error refreshing logs:', error));
                    }}
                    
                    function toggleAutoRefresh() {{
                        autoRefreshEnabled = !autoRefreshEnabled;
                        const btn = document.getElementById('auto-refresh-btn');
                        
                        if (autoRefreshEnabled) {{
                            btn.textContent = '📊 Auto-refresh: ON';
                            btn.style.background = '#10b981';
                            startAutoRefresh();
                        }} else {{
                            btn.textContent = '📊 Auto-refresh: OFF';
                            btn.style.background = '#6b7280';
                            stopAutoRefresh();
                        }}
                    }}
                    
                    function startAutoRefresh() {{
                        if (refreshInterval) clearInterval(refreshInterval);
                        refreshInterval = setInterval(() => {{
                            if (autoRefreshEnabled) {{
                                refreshLogs();
                            }}
                        }}, 2000); // Refresh every 2 seconds
                    }}
                    
                    function stopAutoRefresh() {{
                        if (refreshInterval) {{
                            clearInterval(refreshInterval);
                            refreshInterval = null;
                        }}
                    }}
                    
                    // Start auto-refresh if optimization is running
                    if ('{optimization['status']}' === 'Running' || '{optimization['status']}' === 'Starting') {{
                        startAutoRefresh();
                    }}
                    
                    // Initial log refresh
                    setTimeout(refreshLogs, 1000);
                """)
            ),
            nested=True
        )
    ]
    
    return create_page_layout(
        f"Monitor: {optimization['name']}",
        content=content,
        current_page="optimization",
        user=user.to_dict() if user else None
    )

# Helper function for creating sample dataset
def create_sample_dataset():
    """Create a sample dataset for fallback"""
    sample_data = [
        {"input": "Hello, I need help with my order", "output": "support"},
        {"input": "Thank you for your service", "output": "feedback"},
        {"input": "I want to cancel my subscription", "output": "support"},
        {"input": "Great product, very satisfied", "output": "feedback"},
        {"input": "How do I return an item?", "output": "support"},
        {"input": "Amazing customer service!", "output": "feedback"}
    ]
    
    # Create temporary dataset file
    import tempfile
    import json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_data:
            json.dump(item, f)
            f.write('\n')
        temp_dataset_path = f.name
    
    input_columns = {"input"}
    output_columns = {"output"}
    dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
    dataset_adapter.adapt(data_source=temp_dataset_path)
    train_dataset, test_dataset = dataset_adapter.split(0.7)
    
    # Clean up temporary file
    import os
    os.unlink(temp_dataset_path)
    
    return train_dataset, test_dataset

# Background optimization functions are now handled by optimization_worker.py

# Development route to reset database
@app.post("/admin/reset-database")
async def reset_database(request):
    """Reset database to initial state (development only)"""
    db.reset_database()
    print("🔄 Database reset to initial state")
    return RedirectResponse(url="/?reset=true", status_code=302)

if __name__ == "__main__":
    print("📁 Starting clean Nova Prompt Optimizer...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

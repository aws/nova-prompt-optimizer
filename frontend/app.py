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
from shad4fast import ShadHead, Button, Input, Textarea, Alert, Switch, Accordion, AccordionItem, AccordionTrigger, AccordionContent

# Import existing components
from components.layout import create_main_layout
from components.metrics_page import create_metrics_page, create_metric_tabs

# Import database
from database import db
from metric_service import MetricService
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

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

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
                            A("View Results →", href="/results", cls="inline-flex items-center text-sm text-primary hover:underline mt-2")
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

# Essential routes for clickable dashboard links
@app.get("/metrics")
async def metrics_page(request):
    """Metrics management page"""
    user = await get_current_user(request)
    
    # Check for success/error messages
    created = request.query_params.get("created")
    deleted = request.query_params.get("deleted")
    error = request.query_params.get("error")
    
    success_message = None
    error_message = None
    
    if created == "metric":
        success_message = "Metric created successfully!"
    elif deleted == "metric":
        success_message = "Metric deleted successfully!"
    elif error == "no_dataset_selected":
        error_message = "Please select a dataset to analyze."
    elif error == "no_metric_name":
        error_message = "Please enter a metric name."
    elif error == "inference_failed":
        error_message = "Failed to infer metrics. Please try again."
    
    from database import Database
    db = Database()
    metrics = db.get_metrics()
    datasets = db.get_datasets()
    
    # Create content similar to prompts page
    content = [
        # Create form card (hidden by default)
        Card(
            header=H3("Create Metric"),
            content=Div(
                P("Create custom evaluation metrics for your prompts.", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                Button("Create New Metric", 
                       onclick="showCreateForm()",
                       id="create-metric-btn",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                
                # Tabbed create form (hidden by default)
                Div(
                    Button("Cancel", 
                           onclick="hideCreateForm()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mb-4"),
                    
                    # Import the tabbed interface
                    create_metric_tabs(datasets),
                    
                    style="display: none; margin-top: 1rem;",
                    id="create-metric-section"
                )
            ),
            nested=True
        ),
        
        # Metrics list card
        Card(
            header=H3("Your Metrics"),
            content=Div(
                *[Div(
                    Div(
                        H4(metric["name"], style="margin: 0 0 0.5rem 0; color: #1f2937;"),
                        P(metric.get("description", "No description"), 
                          style="margin: 0 0 0.5rem 0; color: #6b7280; font-size: 0.875rem;"),
                        P(f"Format: {metric.get('dataset_format', 'Unknown')} • Created: {metric.get('created_at', 'Unknown')[:10]}", 
                          style="margin: 0; color: #6b7280; font-size: 0.875rem;")
                    ),
                    Div(
                        Button("Edit", 
                               variant="secondary",
                               size="sm",
                               onclick=f"window.location.href='/metrics/edit/{metric['id']}'"),
                        Button("Delete", 
                               variant="destructive",
                               size="sm",
                               onclick=f"confirmDelete('metric', '{metric['id']}', '{metric['name']}')")
                    ),
                    style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.75rem;"
                ) for metric in metrics] if metrics else [
                    P("No metrics created yet. Create your first metric to get started!", 
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
    
    # Add show/hide form JavaScript (global functions)
    content.append(Script("""
        function showCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'block';
            if (btn) btn.style.display = 'none';
        }
        
        function hideCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'none';
            if (btn) btn.style.display = 'block';
        }
        
        function confirmDelete(type, id, name) {
            const message = `Are you sure you want to delete the ${type} "${name}"?\\n\\nThis action cannot be undone.`;
            
            if (confirm(message)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/${type}s/delete/${id}`;
                document.body.appendChild(form);
                form.submit();
            }
        }
    """))
    
    return create_main_layout(
        "Metrics",
        Div(*content),
        current_page="metrics",
        user=user.to_dict() if user else None
    )

def create_metric_card(metric):
    """Create a metric card similar to other pages"""
    return Div(
        Div(
            Div(
                H3(metric["name"], style="margin: 0; font-size: 1.125rem; font-weight: 600;"),
                P(metric.get("description", "No description"), 
                  style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.875rem;"),
                style="flex: 1;"
            ),
            Div(
                Button("Edit", variant="secondary", size="sm"),
                Button("Delete", variant="destructive",
                       onclick=f"confirmDelete('metric', '{metric['id']}', '{metric['name']}')")
            ),
            style="display: flex; justify-content: space-between; align-items: flex-start;"
        ),
        Div(
            P(f"Format: {metric.get('dataset_format', 'Unknown')} • Created: {metric.get('created_at', 'Unknown')[:10]}", 
              style="margin: 0; color: #6b7280; font-size: 0.875rem;"),
            style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;"
        ),
        style="background: white; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #e5e7eb;"
    )

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
                Div(
                    Button("Upload New Dataset", 
                           onclick="showCreateForm('dataset')",
                           id="create-dataset-btn",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2",
                           style="margin-right: 0.5rem;"),
                    Button("Generate with AI", 
                           onclick="startDatasetGenerator()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem; margin-bottom: 1rem;"
                ),
                
                # Upload form (hidden by default)
                Div(
                    Button("Cancel", 
                           onclick="hideCreateForm('dataset')",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mb-4"),
                    
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
                        "Upload Dataset", 
                        type="submit"
                    ),
                    method="POST",
                    action="/datasets/upload",
                    enctype="multipart/form-data"
                ),
                
                style="display: none; margin-top: 1rem;",
                id="create-dataset-section"
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
                        Button("View", 
                               variant="outline",
                               size="sm",
                               onclick=f"window.location.href='/datasets/view/{dataset['id']}'"),
                        Button("Edit", 
                               variant="secondary",
                               size="sm",
                               onclick=f"window.location.href='/datasets/edit/{dataset['id']}'"),
                        Button("Delete", 
                               variant="destructive",
                               size="sm",
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
    
    # Add confirmDelete function for delete buttons
    content.append(Script("""
        function showCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'block';
            if (btn) btn.style.display = 'none';
        }
        
        function hideCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'none';
            if (btn) btn.style.display = 'block';
        }
        
        function confirmDelete(type, id, name) {
            const message = `Are you sure you want to delete the ${type} "${name}"?\\n\\nThis action cannot be undone.`;
            
            if (confirm(message)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/${type}s/delete/${id}`;
                document.body.appendChild(form);
                form.submit();
            }
        }
        
        function startDatasetGenerator() {
            // Navigate to the AI Dataset Generator page
            window.location.href = '/datasets/generator';
        }
    """))
    
    return create_main_layout(
        "Datasets",
        Div(*content),
        current_page="datasets",
        user=user.to_dict() if user else None
    )

@app.post("/metrics/infer-from-dataset")
async def infer_metrics_from_dataset(request):
    """Infer metrics from dataset using AI"""
    print("=" * 50)
    print("🚀 ENDPOINT HIT: /metrics/infer-from-dataset")
    print("=" * 50)
    
    print("🔍 Starting metric inference from dataset...")
    
    form_data = await request.form()
    metric_name = form_data.get("metric_name")
    dataset_id = form_data.get("dataset_id")
    analysis_depth = form_data.get("analysis_depth", "standard")
    focus_areas = form_data.getlist("focus")
    
    # Handle rate_limit with proper default for empty strings
    rate_limit_str = form_data.get("rate_limit", "60")
    rate_limit = int(rate_limit_str) if rate_limit_str and rate_limit_str.strip() else 60
    
    model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0")
    
    print(f"📋 Parameters: name={metric_name}, dataset={dataset_id}, depth={analysis_depth}")
    print(f"⚡ Rate limit: {rate_limit} RPM, Model: {model_id}")
    print(f"🎯 Focus areas: {focus_areas}")
    
    if not dataset_id:
        print("❌ No dataset selected")
        return RedirectResponse(url="/metrics?error=no_dataset_selected", status_code=302)
    
    if not metric_name:
        print("❌ No metric name provided")
        return RedirectResponse(url="/metrics?error=no_metric_name", status_code=302)
    
    try:
        print("📊 Reading dataset content...")
        # Read dataset content
        sample_counts = {"quick": 5, "standard": 20, "deep": 50}
        max_samples = sample_counts.get(analysis_depth, 20)
        
        dataset_content = read_dataset_content(dataset_id, max_samples)
        print(f"✅ Dataset content loaded: {len(dataset_content)} characters")
        
        # No prompt processing - analyze dataset only
        print("🤖 Creating AI prompt for metric inference...")
        # Create AI prompt for metric inference
        from prompt_templates import get_dataset_analysis_prompt
        prompt = get_dataset_analysis_prompt(dataset_content, focus_areas, analysis_depth, prompt_content=None)
        print(f"✅ Prompt created: {len(prompt)} characters")
        
        print("🔄 Calling AI for metric inference...")
        # Call AI to infer metrics with rate limiting
        inferred_metrics = await call_ai_for_metric_inference(prompt, rate_limit, model_id)
        print(f"✅ AI inference completed: {type(inferred_metrics)}")
        print(f"📝 Inference result keys: {list(inferred_metrics.keys()) if isinstance(inferred_metrics, dict) else 'Not a dict'}")
        print(f"🎯 Intent analysis present: {'intent_analysis' in inferred_metrics if isinstance(inferred_metrics, dict) else 'N/A'}")
        if isinstance(inferred_metrics, dict) and 'intent_analysis' in inferred_metrics:
            print(f"📋 Intent content: {inferred_metrics['intent_analysis'][:100]}...")
        else:
            print("⚠️ No intent_analysis field found in response")
        
        print("📦 Preparing metric selection data...")
        # Instead of generating code immediately, redirect to metric selection page
        import urllib.parse
        import json
        selection_data = {
            "metric_name": metric_name,
            "dataset_id": dataset_id,
            "analysis_depth": analysis_depth,
            "focus_areas": focus_areas,
            "model_id": model_id,
            "rate_limit": rate_limit,
            "inferred_metrics": inferred_metrics
        }
        
        encoded_data = urllib.parse.quote(json.dumps(selection_data))
        print(f"✅ Selection data encoded: {len(encoded_data)} characters")
        print("🔄 Redirecting to metric selection page...")
        return RedirectResponse(url=f"/metrics/select?data={encoded_data}", status_code=302)
        
    except Exception as e:
        print(f"❌ Error inferring metrics: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return RedirectResponse(url="/metrics?error=inference_failed", status_code=302)

async def call_ai_for_metric_inference(prompt: str, rate_limit: int = 60, model_id: str = "us.amazon.nova-premier-v1:0") -> dict:
    """Call AI service to infer metrics from actual dataset analysis"""
    import boto3
    import json
    
    print(f"🤖 AI Inference - Model: {model_id}, Rate limit: {rate_limit} RPM")
    print("⏱️ Note: Rate limiting removed for faster response")
    
    try:
        print("🔗 Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime')
        
        print("📤 Sending request to Bedrock...")
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.3
                }
            })
        )
        
        print("📥 Received response from Bedrock")
        result = json.loads(response['body'].read())
        ai_response = result['output']['message']['content'][0]['text']
        print(f"✅ AI response length: {len(ai_response)} characters")
        
        # Parse the JSON response from AI
        try:
            print("🔄 Parsing AI response as JSON...")
            print(f"📝 Raw AI response (first 1000 chars): {ai_response[:1000]}")
            parsed_response = json.loads(ai_response)
            print(f"✅ JSON parsing successful: {list(parsed_response.keys())}")
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📝 Full raw AI response: {ai_response}")
            
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                try:
                    print("🔄 Found JSON in markdown, attempting to parse...")
                    extracted_json = json_match.group(1)
                    parsed_response = json.loads(extracted_json)
                    print(f"✅ Markdown JSON parsing successful: {list(parsed_response.keys())}")
                    return parsed_response
                except json.JSONDecodeError:
                    print("❌ Markdown JSON also failed to parse")
            
            # Fallback if AI doesn't return valid JSON
            return {
                "metrics": [{"name": "AI Analysis Failed", "description": "Could not parse AI response", "criteria": "No criteria", "example": "No example"}],
                "reasoning": f"AI response was not valid JSON. Raw response: {ai_response[:500]}..."
            }
            
    except Exception as e:
        print(f"❌ Bedrock API error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        # Fallback to hardcoded response
        return {
            "metrics": [
                {
                    "name": "Response Accuracy",
                    "description": "Measures how accurately the output matches the expected result",
                    "criteria": "5=Perfect match, 4=Minor errors, 3=Some errors, 2=Major errors, 1=Completely wrong",
                    "example": "For classification tasks, checks if predicted category matches actual category"
                }
            ],
            "reasoning": "Fallback metrics due to API error"
        }

@app.get("/metrics/edit/{metric_id}")
def edit_metric_page(request):
    """Edit metric page"""
    metric_id = request.path_params["metric_id"]
    
    from database import Database
    db = Database()
    metric = db.get_metric_by_id(metric_id)
    
    if not metric:
        return RedirectResponse(url="/metrics?error=not_found", status_code=302)
    
    page_content = Div(
        H2("Edit Metric", style="margin-bottom: 2rem; color: #1f2937;"),
        
        Form(
            Card(
                header=H3("Metric Details"),
                content=Div(
                    FormField(
                        Label("Name:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(name="name", value=metric["name"], required=True)
                    ),
                    FormField(
                        Label("Description:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Textarea(metric["description"], name="description", rows=3)
                    ),
                    FormField(
                        Label("Natural Language Input:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Textarea(metric.get("natural_language_input", ""), name="natural_language_input", rows=2)
                    )
                )
            ),
            
            Card(
                header=H3("Generated Code"),
                content=Div(
                    FormField(
                        Label("Python Code:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Textarea(metric["generated_code"], 
                                name="generated_code", 
                                rows=15,
                                style="font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem;")
                    )
                )
            ),
            
            Div(
                Button("Update Metric", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mr-4"),
                Button("Cancel", type="button", onclick="window.location.href='/metrics'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                style="margin-top: 2rem; display: flex; gap: 1rem;"
            ),
            
            method="POST",
            action=f"/metrics/edit/{metric_id}"
        )
    )
    
    return create_main_layout("Edit Metric", page_content, current_page="metrics")

@app.post("/metrics/edit/{metric_id}")
async def update_metric(request):
    """Update metric"""
    metric_id = request.path_params["metric_id"]
    form_data = await request.form()
    
    from database import Database
    db = Database()
    
    # Update metric in database
    success = db.update_metric(
        metric_id=metric_id,
        name=form_data.get("name"),
        description=form_data.get("description"),
        generated_code=form_data.get("generated_code"),
        natural_language_input=form_data.get("natural_language_input")
    )
    
    if success:
        return RedirectResponse(url="/metrics?updated=metric", status_code=302)
    else:
        return RedirectResponse(url="/metrics?error=update_failed", status_code=302)

@app.get("/metrics/select")
def metric_selection_page(request):
    """Select which inferred metrics to convert to code"""
    import urllib.parse
    import json
    
    # Get selection data from URL params
    data_param = request.query_params.get("data", "{}")
    try:
        selection_data = json.loads(urllib.parse.unquote(data_param))
    except:
        return RedirectResponse(url="/metrics?error=invalid_selection", status_code=302)
    
    inferred_metrics = selection_data.get("inferred_metrics", {})
    metrics = inferred_metrics.get("metrics", [])
    reasoning = inferred_metrics.get("reasoning", "No reasoning provided")
    intent_analysis = inferred_metrics.get("intent_analysis", "")
    
    # Debug intent analysis
    print(f"🔍 DEBUG - Intent analysis value: '{intent_analysis}'")
    
    # Infer output format from dataset
    format_fields = []
    if metrics and len(metrics) > 0:
        # Extract field names from the first metric's data_fields
        first_metric = metrics[0]
        format_fields = first_metric.get('data_fields', [])
    
    format_description = f"JSON with fields: {', '.join(format_fields)}" if format_fields else "JSON format detected"
    print(f"🔍 DEBUG - Intent analysis length: {len(intent_analysis)}")
    print(f"🔍 DEBUG - Inferred metrics keys: {list(inferred_metrics.keys())}")
    
    page_content = Div(
        # Editable Intent Field
        Card(
            header="Intent Analysis",
            content=Div(
                P("Review and edit the AI's understanding of your dataset task:", 
                  cls="text-sm text-gray-600 mb-3"),
                Form(
                    Textarea(
                        intent_analysis,
                        name="intent_analysis",
                        id="intent_field",
                        rows=4,
                        cls="w-full p-3 border border-gray-300 rounded-md resize-none mb-3"
                    ),
                Button("Update Intent & Regenerate Metrics",
                           type="button",
                           onclick="regenerateWithIntent()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mt-3"),
                    id="intent_form"
                )
            ),
            cls="mb-6"
        ),
        
        # Dataset Information
        Card(
            header="Dataset Information",
            content=Div(
                P(f"Dataset: {selection_data.get('dataset_id', 'Unknown')}", cls="mb-2 font-medium"),
                P(f"Analysis Depth: {selection_data.get('analysis_depth', 'standard').title()}", cls="mb-3"),
                H4("AI Reasoning:", cls="font-medium mb-2 text-gray-900"),
                P(reasoning, cls="bg-gray-50 p-3 rounded-md italic text-gray-700")
            ),
            cls="mb-6"
        ),
        
        # Metric Selection Form
        Form(
            # Output Format Validation Section
            Card(
                header="Output Format Validation",
                content=Div(
                    P("Automatically validate that AI outputs match the expected JSON structure from your dataset.", 
                      cls="text-sm text-gray-600 mb-3"),
                    Div(
                        Switch(name="include_format_validation", value="true", id="format-validation", checked=True),
                        Label("Include JSON format validation", **{"for": "format-validation"}, cls="ml-2 text-sm font-medium"),
                        cls="flex items-center mb-2"
                    ),
                    Div(
                        P(f"Detected format: {format_description}", 
                          cls="text-xs text-gray-500 ml-6"),
                        cls="ml-6"
                    )
                ),
                cls="mb-6"
            ),
            
            Card(
                header="Available Metrics",
                content=Div(
                    *[Div(
                        Div(
                            Div(
                                Label(f"{metric.get('name', f'Metric {i+1}')}", **{"for": f"metric-{i}"}, cls="font-semibold text-base"),
                                cls="flex-1"
                            ),
                            Switch(name="selected_metrics", value=str(i), id=f"metric-{i}", checked=True),
                            cls="flex items-center justify-between mb-3"
                        ),
                        Div(
                            P(f"Intent: {metric.get('intent_understanding', 'No description')}", cls="mb-2 text-sm text-gray-600"),
                            P(f"Fields: {', '.join(metric.get('data_fields', []))}", cls="mb-2 text-sm text-gray-600"),
                            P(f"Logic: {metric.get('evaluation_logic', 'No logic')}", cls="mb-2 text-sm text-gray-600"),
                            P(f"Example: {metric.get('example', 'No example')}", cls="text-xs text-gray-500"),
                            cls="ml-6 p-3 bg-gray-50 rounded-md border"
                        ),
                        cls="mb-4 p-4 border border-gray-200 rounded-lg"
                    ) for i, metric in enumerate(metrics)] if metrics else [
                        P("No metrics were suggested by the AI", cls="text-red-500 text-center py-8")
                    ]
                ),
                cls="mb-6"
            ),
            
            # Action Buttons
            Card(
                header="Actions",
                content=Div(
                    Button("Generate Selected Metrics", 
                           type="submit", 
                           id="generate-btn",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 flex-1 mr-2"),
                    Button("Cancel", 
                           type="button", 
                           onclick="window.location.href='/metrics'", 
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-1/4"),
                    cls="flex"
                ),
                cls="mb-6"
            ),
            
            # Hidden fields to preserve data
            *[Input(type="hidden", name=key, value=str(value)) for key, value in selection_data.items() if key != "inferred_metrics"],
            Input(type="hidden", name="metrics_json", value=json.dumps(metrics)),
            Input(type="hidden", name="reasoning", value=reasoning),
            
            method="POST",
            action="/metrics/generate-selected"
        ),
        
        # JavaScript for intent regeneration and button loading
        Script(f"""
            const selectionData = {json.dumps(selection_data)};
            
            // Show loading state on form submit
            document.querySelector('form[action="/metrics/generate-selected"]').addEventListener('submit', function() {{
                const button = document.getElementById('generate-btn');
                button.disabled = true;
                button.textContent = 'Generating Metrics...';
                button.style.cursor = 'wait';
                document.body.style.cursor = 'wait';
            }});
            
            function regenerateWithIntent() {{
                const newIntent = document.getElementById('intent_field').value;
                const formData = new FormData();
                
                // Include all original data
                formData.append('metric_name', selectionData.metric_name || '');
                formData.append('dataset_id', selectionData.dataset_id || '');
                formData.append('analysis_depth', selectionData.analysis_depth || 'standard');
                formData.append('model_id', selectionData.model_id || 'us.amazon.nova-premier-v1:0');
                formData.append('rate_limit', selectionData.rate_limit || '25');
                formData.append('updated_intent', newIntent);
                
                // Show loading
                document.body.style.cursor = 'wait';
                const button = event.target;
                button.disabled = true;
                button.textContent = 'Regenerating...';
                
                fetch('/metrics/regenerate-with-intent', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        // Reload page with new data
                        const newData = encodeURIComponent(JSON.stringify(data.selection_data));
                        window.location.href = `/metrics/select?data=${{newData}}`;
                    }} else {{
                        alert('Error: ' + data.error);
                        document.body.style.cursor = 'default';
                        button.disabled = false;
                        button.textContent = 'Update Intent & Regenerate Metrics';
                    }}
                }})
                .catch(error => {{
                    alert('Error: ' + error);
                    document.body.style.cursor = 'default';
                    button.disabled = false;
                    button.textContent = 'Update Intent & Regenerate Metrics';
                }});
            }}
        """)
    )
    
    return create_main_layout("Metric Selection", page_content, current_page="metrics")

@app.post("/metrics/regenerate-with-intent")
async def regenerate_with_intent(request):
    """Regenerate metrics with updated intent"""
    try:
        form_data = await request.form()
        
        # Get form data
        metric_name = form_data.get("metric_name", "")
        dataset_id = form_data.get("dataset_id", "")
        analysis_depth = form_data.get("analysis_depth", "standard")
        model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0")
        rate_limit = int(form_data.get("rate_limit", "25"))
        updated_intent = form_data.get("updated_intent", "")
        
        print(f"🔄 Regenerating metrics with updated intent...")
        print(f"📝 Updated intent: {updated_intent[:100]}...")
        
        # Read dataset content
        sample_counts = {"quick": 5, "standard": 20, "deep": 50}
        max_samples = sample_counts.get(analysis_depth, 20)
        dataset_content = read_dataset_content(dataset_id, max_samples)
        
        # Get prompt content if available (try to get from original request)
        prompt_content = None
        # TODO: Store and retrieve prompt content if needed
        
        # Create enhanced prompt with updated intent
        enhanced_prompt = f"""You are an expert in AI evaluation metrics. Analyze the dataset and create simple evaluation metrics based on the updated intent.

Dataset Content ({analysis_depth} analysis):
```
{dataset_content}
```

UPDATED INTENT FROM USER:
{updated_intent}

ANALYSIS REQUIREMENTS:
1. Use the UPDATED INTENT above as the primary guide for metric creation
2. Examine the ACTUAL data structure and field names in the dataset
3. Create metrics that measure success for the updated intent

Based on the updated intent and dataset analysis, suggest 2-3 simple evaluation metrics. For each metric, provide:

1. **Metric Name**: Clear, descriptive name
2. **Intent Understanding**: How this metric measures success for the updated intent
3. **Data Fields Used**: Exactly which fields from the dataset this metric will access
4. **Evaluation Logic**: Simple logic for comparing predicted vs expected values
5. **Example**: How it would evaluate a sample from this dataset

Focus on metrics that are:
- Aligned with the updated intent
- Use the exact field names from the dataset
- Simple and focused on the core task
- Avoid overfitting or complex scoring

Format your response as JSON:
{{
  "intent_analysis": "Confirmation of the updated intent and how it guides metric creation",
  "metrics": [
    {{
      "name": "Metric Name",
      "intent_understanding": "How this metric measures success for the updated intent",
      "data_fields": ["field1", "field2"],
      "evaluation_logic": "Simple comparison logic using actual field names",
      "example": "Example using actual data structure"
    }}
  ],
  "reasoning": "Why these metrics effectively measure the updated intent"
}}"""
        
        # Call AI for metric inference with updated intent
        inferred_metrics = await call_ai_for_metric_inference(enhanced_prompt, rate_limit, model_id)
        
        # Prepare new selection data
        selection_data = {
            "metric_name": metric_name,
            "dataset_id": dataset_id,
            "analysis_depth": analysis_depth,
            "model_id": model_id,
            "rate_limit": rate_limit,
            "inferred_metrics": inferred_metrics
        }
        
        return {
            "success": True,
            "selection_data": selection_data,
            "message": "Metrics regenerated with updated intent"
        }
        
    except Exception as e:
        print(f"❌ Error regenerating with intent: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/metrics/generate-selected")
async def generate_selected_metrics(request):
    """Generate code for selected metrics"""
    form_data = await request.form()
    selected_indices = form_data.getlist("selected_metrics")
    include_format_validation = form_data.get("include_format_validation") == "true"
    
    if not selected_indices:
        return RedirectResponse(url="/metrics?error=no_metrics_selected", status_code=302)
    
    # Get the original data
    metric_name = form_data.get("metric_name")
    model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0")
    
    # Handle rate_limit with proper default for empty strings
    rate_limit_str = form_data.get("rate_limit", "60")
    rate_limit = int(rate_limit_str) if rate_limit_str and rate_limit_str.strip() else 60
    
    metrics_json = form_data.get("metrics_json", "[]")
    reasoning = form_data.get("reasoning", "")
    
    try:
        import json
        all_metrics = json.loads(metrics_json)
        selected_metrics = [all_metrics[int(i)] for i in selected_indices]
        
        # Generate code for selected metrics
        metric_service = MetricService()
        criteria = {
            "natural_language": reasoning,
            "dataset_format": "json",
            "metrics_description": str(selected_metrics),
            "include_format_validation": include_format_validation
        }
        
        generated_code = metric_service.generate_metric_code(metric_name, criteria, model_id=model_id, rate_limit=rate_limit)
        
        # VALIDATE THE GENERATED METRIC
        from metric_validator import MetricValidator
        validator = MetricValidator()
        
        # Get sample data for validation
        from database import Database
        db = Database()
        dataset = db.get_dataset(form_data.get("dataset_id"))
        if dataset and dataset.get('content'):
            import json
            sample_data = []
            for line in dataset['content'].strip().split('\n')[:10]:  # Use first 10 samples
                try:
                    sample_data.append(json.loads(line))
                except:
                    continue
            
            validation_result = validator.validate_metric(generated_code, sample_data)
            validation_report = validator.format_validation_report(validation_result)
        else:
            validation_result = {"is_valid": True, "warnings": ["No sample data available for validation"]}
            validation_report = "⚠️ No sample data available for validation"
        
        # Prepare preview data
        preview_data = {
            "name": metric_name,
            "description": f"Selected metrics from AI analysis",
            "dataset_format": "JSON",
            "scoring_criteria": reasoning,
            "generated_code": generated_code,
            "natural_language_input": f"Selected {len(selected_metrics)} metrics: {', '.join([m.get('name', 'Unnamed') for m in selected_metrics])}",
            "validation_result": validation_result,
            "validation_report": validation_report
        }
        
        import urllib.parse
        encoded_data = urllib.parse.quote(json.dumps(preview_data))
        return RedirectResponse(url=f"/metrics/preview?data={encoded_data}", status_code=302)
        
    except Exception as e:
        print(f"❌ Error generating selected metrics: {e}")
        return RedirectResponse(url="/metrics?error=generation_failed", status_code=302)

@app.get("/metrics/preview")
def metric_preview_page(request):
    """Preview generated metric before saving"""
    import urllib.parse
    import json
    
    # Get preview data from URL params
    data_param = request.query_params.get("data", "{}")
    try:
        preview_data = json.loads(urllib.parse.unquote(data_param))
    except:
        return RedirectResponse(url="/metrics?error=invalid_preview", status_code=302)
    
    # Build the page content
    page_content = Div(
        Card(
            header="Metric Details",
            content=Div(
                P(f"Name: {preview_data.get('name', 'Unknown')}", cls="mb-2 font-medium"),
                P(f"Description: {preview_data.get('description', 'No description')}", cls="mb-2"),
                P(f"Criteria: {preview_data.get('scoring_criteria', 'No criteria')}", cls="mb-2"),
            ),
            cls="mb-6"
        ),
        
        # VALIDATION RESULTS CARD
        Card(
            header="🔍 Metric Validation Results",
            content=Div(
                Pre(
                    preview_data.get('validation_report', 'No validation performed'),
                    cls="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded border max-h-128 overflow-y-auto"
                ),
                P("This validation tests your metric with sample data to ensure it works correctly.", 
                  cls="text-xs text-gray-500 mt-2")
            ),
            cls="mb-6"
        ),
        
        Card(
            header="Generated Code",
            content=Div(
                Pre(
                    Code(preview_data.get('generated_code', 'No code generated')),
                    cls="bg-gray-50 p-4 rounded overflow-x-auto font-mono text-sm"
                )
            ),
            cls="mb-6"
        ),
        
        Card(
            header="Actions",
            content=Div(
                Button("Save Metric", 
                       onclick="saveMetric()",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 flex-1 mr-2"),
                Button("Cancel", 
                       onclick="window.location.href='/metrics'",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-1/4"),
                cls="flex"
            ),
            cls="mb-6"
        ),
        
        # Hidden form with metric data
        Form(
            *[Input(type="hidden", name=key, value=str(value)) for key, value in preview_data.items()],
            id="metric-form",
            method="POST",
            action="/metrics/save"
        ),
        
        Script("""
            function saveMetric() {
                document.getElementById('metric-form').submit();
            }
        """)
    )
    
    return create_main_layout("Metric Preview", page_content, current_page="metrics")

@app.post("/metrics/save")
async def save_metric(request):
    """Save the previewed metric"""
    form_data = await request.form()
    
    from database import Database
    db = Database()
    
    metric_id = db.create_metric(
        name=form_data.get("name"),
        description=form_data.get("description"),
        dataset_format=form_data.get("dataset_format", "JSON"),
        scoring_criteria=form_data.get("scoring_criteria"),
        generated_code=form_data.get("generated_code"),
        natural_language_input=form_data.get("natural_language_input")
    )
    
    return RedirectResponse(url=f"/metrics?created=metric&id={metric_id}", status_code=302)

@app.post("/metrics/create")
async def create_metric(request):
    """Create a new metric from natural language description"""
    from database import Database
    from metric_service import MetricService
    
    db = Database()
    metric_service = MetricService()
    
    # Get form data
    form_data = await request.form()
    name = form_data.get("name", "").strip()
    description = form_data.get("description", "").strip()
    natural_language = form_data.get("natural_language", "").strip()
    model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0").strip()
    
    if not name or not natural_language:
        return {"error": "Name and natural language description are required"}
    
    try:
        # Parse natural language to criteria
        criteria = metric_service.parse_natural_language(natural_language)
        criteria['model_id'] = model_id
        
        # Generate metric code using selected model
        generated_code = metric_service.generate_metric_code(name, criteria, model_id)
        
        # Validate the code (temporarily disabled for debugging)
        # if not metric_service.validate_metric_code(generated_code):
        #     return {"error": "Generated metric code is invalid"}
        
        print("Generated code:", generated_code)  # Debug output
        
        # Store in database
        metric_id = db.create_metric(
            name=name,
            description=description,
            dataset_format=criteria['dataset_format'],
            scoring_criteria=json.dumps(criteria),
            generated_code=generated_code,
            natural_language_input=natural_language
        )
        
        return {"success": True, "metric_id": metric_id, "message": "Metric created successfully"}
        
    except Exception as e:
        return {"error": f"Failed to create metric: {str(e)}"}

@app.get("/metrics/{metric_id}")
async def get_metric(request):
    """Get a single metric for editing"""
    metric_id = request.path_params["metric_id"]
    
    try:
        metric = db.get_metric_by_id(metric_id)
        if metric:
            return metric
        else:
            return {"error": "Metric not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/metrics/update/{metric_id}")
async def update_metric(request):
    """Update an existing metric"""
    metric_id = request.path_params["metric_id"]
    
    try:
        form_data = await request.form()
        name = form_data.get("name", "").strip()
        description = form_data.get("description", "").strip()
        natural_language = form_data.get("natural_language", "").strip()
        model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0").strip()
        
        if not name or not natural_language:
            return {"error": "Name and natural language description are required"}
        
        # Generate updated code
        metric_service = MetricService()
        criteria = {"description": natural_language}
        generated_code = metric_service.generate_metric_code(name, criteria, model_id)
        
        # Update in database
        updated = db.update_metric(metric_id, name, description, generated_code, natural_language)
        
        if updated:
            return {"success": True, "message": "Metric updated successfully"}
        else:
            return {"error": "Metric not found"}
            
    except Exception as e:
        return {"error": f"Failed to update metric: {str(e)}"}

@app.post("/metrics/preview")
async def preview_metric(request):
    """Preview generated metric code"""
    try:
        form_data = await request.form()
        name = form_data.get("name", "Untitled Metric").strip()
        natural_language = form_data.get("natural_language", "").strip()
        model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0").strip()
        
        if not natural_language:
            return {"error": "Natural language description is required"}
        
        # Generate metric code using selected model
        metric_service = MetricService()
        criteria = {"description": natural_language}
        generated_code = metric_service.generate_metric_code(name, criteria, model_id)
        
        return {"success": True, "code": generated_code}
        
    except Exception as e:
        return {"error": f"Failed to generate preview: {str(e)}"}

@app.post("/metrics/delete/{metric_id}")
async def delete_metric(request):
    """Delete a metric"""
    metric_id = request.path_params["metric_id"]
    
    try:
        deleted = db.delete_metric(metric_id)
        if deleted:
            return {"success": True}
        else:
            return {"error": "Metric not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500
async def preview_metric(request):
    """Preview generated metric code from natural language"""
    from metric_service import MetricService
    
    metric_service = MetricService()
    
    # Get form data
    form_data = await request.form()
    name = form_data.get("name", "Untitled Metric").strip()
    natural_language = form_data.get("natural_language", "").strip()
    model_id = form_data.get("model_id", "us.amazon.nova-premier-v1:0").strip()
    
    if not natural_language:
        return {"error": "Natural language description is required"}
    
    try:
        # Parse and generate code
        criteria = metric_service.parse_natural_language(natural_language)
        generated_code = metric_service.generate_metric_code(name, criteria, model_id)
        
        return {"code": generated_code}
        criteria = metric_service.parse_natural_language(natural_language)
        generated_code = metric_service.generate_metric_code(name, criteria)
        
        return {
            "success": True,
            "code": generated_code,
            "criteria": criteria
        }
        
    except Exception as e:
        return {"error": f"Failed to generate preview: {str(e)}"}

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
                Button("Create New Prompt", 
                       onclick="showCreateForm('prompt')",
                       id="create-prompt-btn",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                
                # Create form (hidden by default)
                Div(
                    Button("Cancel", 
                           onclick="hideCreateForm('prompt')",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mb-4"),
                    
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
                        "Create Prompt", 
                        type="submit"
                    ),
                    method="POST",
                    action="/prompts/create"
                ),
                
                style="display: none; margin-top: 1rem;",
                id="create-prompt-section"
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
                        Button("Edit", 
                               variant="secondary",
                               size="sm",
                               onclick=f"window.location.href='/prompts/edit/{prompt['id']}'"),
                        Button("Delete", 
                               variant="destructive",
                               size="sm",
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
    
    # Add confirmDelete function for delete buttons
    content.append(Script("""
        function showCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'block';
            if (btn) btn.style.display = 'none';
        }
        
        function hideCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'none';
            if (btn) btn.style.display = 'block';
        }
        
        function confirmDelete(type, id, name) {
            const message = `Are you sure you want to delete the ${type} "${name}"?\\n\\nThis action cannot be undone.`;
            
            if (confirm(message)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/${type}s/delete/${id}`;
                document.body.appendChild(form);
                form.submit();
            }
        }
    """))
    
    return create_main_layout(
        "Prompts",
        Div(*content),
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
    
    # Debug: Print optimization statuses
    for opt in sample_optimizations:
        print(f"🔍 DEBUG - Optimization {opt['id']}: status='{opt['status']}'")
    
    # Get available prompts and datasets for the form
    available_prompts = db.get_prompts()
    available_datasets = db.get_datasets()
    available_metrics = db.get_metrics()  # Add metrics
    
    print(f"DEBUG: Found {len(available_metrics)} metrics for optimization form:")
    for metric in available_metrics:
        print(f"  - {metric['id']}: {metric['name']} - {metric['description']}")
    
    content = [
        Card(
            header=H3("Start New Optimization"),
            content=Div(
                P("Optimize your prompts using AI-powered techniques.", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                Button("Start New Optimization", 
                       onclick="showCreateForm('optimization')",
                       id="create-optimization-btn",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                
                # Optimization form (hidden by default)
                Div(
                    Button("Cancel", 
                           onclick="hideCreateForm('optimization')",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mb-4"),
                    
                    # Optimization form
                    P("Configure and start prompt optimization runs here.", 
                      style="color: #6b7280; margin-bottom: 1rem;"),
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
                    
                    # Metric Selection
                    Div(
                        Label("Evaluation Metric:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Select(
                            Option("Select a metric...", value="", disabled=True, selected=True),
                            *[Option(f"{metric['name']} - {metric['description'] or 'Custom metric'}", 
                                   value=metric['id']) for metric in available_metrics],
                            name="metric_id",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        P("Select the evaluation metric to measure prompt performance", 
                          style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                        style="margin-bottom: 1rem;"
                    ) if available_metrics else Alert(
                        "⚠️ No metrics available. Create a metric first.",
                        variant="destructive",
                        cls="mb-4"
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
                            # Train/Test Split
                            Div(
                                Label("Train/Test Split:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                                Select(
                                    Option("50/50 (Balanced)", value="0.5", selected=True),
                                    Option("60/40 (More Test Data)", value="0.6"),
                                    Option("70/30 (Standard)", value="0.7"),
                                    Option("80/20 (More Training Data)", value="0.8"),
                                    name="train_split",
                                    style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                                ),
                                P("Higher train split = more data for optimization, lower = more data for evaluation", 
                                  style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                                style="margin-bottom: 1rem;"
                            ),
                            # Dataset Record Limit
                            Div(
                                Label("Dataset Records to Process:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                                Input(
                                    type="number", 
                                    name="record_limit", 
                                    placeholder="Minimum 5 records",
                                    min="5",
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
                        "Start Optimization", 
                        type="submit"
                    ),
                    method="POST",
                    action="/optimization/start"
                ) if available_prompts and available_datasets else Alert(
                    "You need at least one prompt and one dataset to start optimization.",
                    variant="destructive"
                ),
                
                style="display: none; margin-top: 1rem;",
                id="create-optimization-section"
            )
            ),  # Close the main content Div
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
                        P(f"Started: {opt['started']} • Status: '{opt['status']}' (DEBUG: {repr(opt['status'])})", 
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
                            P(str(opt["improvement"]), 
                              style="margin: 0; font-weight: 600; color: #10b981;" if str(opt["improvement"]).startswith("+") else "margin: 0; font-weight: 600; color: #6b7280;"),
                            P("improvement", style="margin: 0; font-size: 0.75rem; color: #6b7280;"),
                            style="text-align: center; margin-bottom: 0.5rem;"
                        ),
                        Div(
                            Button("Retry", 
                                   onclick=f"retryOptimization('{opt['id']}')",
                                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"
                                   ) if opt["status"] == "Failed" else None,
                            Button("View Results", 
                                   variant="outline",
                                   size="sm",
                                   onclick=f"window.location.href='/optimization/results/{opt['id']}'",
                                   ) if opt.get("status") in ["Completed", "Failed", "Complete", "completed", "complete"] or opt.get("status") == 100 else Button("Monitor Progress", 
                                   variant="default",
                                   size="sm",
                                   onclick=f"window.location.href='/optimization/monitor/{opt['id']}'",
                                   ),
                            Button("Stop" if opt["status"] in ["Starting", "Running"] else "Delete", 
                                   variant="destructive",
                                   size="sm",
                                   onclick=f"confirmDelete('optimization', '{opt['id']}', {json.dumps(opt['name'])})",
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
    
    # Add modal functions
    content.append(Script("""
        function retryOptimization(optimizationId) {
            if (confirm('Retry this failed optimization? It will restart from the beginning.')) {
                fetch(`/optimization/${optimizationId}/retry`, {method: 'POST'})
                .then(() => location.reload());
            }
        }
        
        function showCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'block';
            if (btn) btn.style.display = 'none';
        }
        
        function hideCreateForm(type) {
            const section = document.getElementById('create-' + (type || 'metric') + '-section');
            const btn = document.getElementById('create-' + (type || 'metric') + '-btn');
            if (section) section.style.display = 'none';
            if (btn) btn.style.display = 'block';
        }
        
        function confirmDelete(type, id, name) {
            const message = `Are you sure you want to delete the ${type} "${name}"?\\n\\nThis action cannot be undone.`;
            
            if (confirm(message)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/${type}s/delete/${id}`;
                document.body.appendChild(form);
                form.submit();
            }
        }
    """))
    
    return create_main_layout(
        "Optimization",
        Div(*content),
        current_page="optimization",
        user=user.to_dict() if user else None
    )

@app.get("/results")
async def results_page(request):
    """Results page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Results",
        Div(
            Card(
                header=H3("Optimization Results"),
                content=P("View and analyze your optimization results here."),
                nested=True
            )
        ),
        current_page="results",
        user=user.to_dict() if user else None
    )

@app.get("/test-edit")
async def test_edit():
    """Test route to verify server updates"""
    return H1("Server updated successfully - Edit should work now")

@app.get("/prompts/edit/{prompt_id}")
async def edit_prompt(request):
    """Edit a prompt"""
    prompt_id = request.path_params["prompt_id"]
    
    # Use the same import pattern as other working functions
    from database import Database
    db = Database()
    
    # Find the prompt using get_prompts method (which we know works)
    prompts = db.get_prompts()
    prompt = next((p for p in prompts if p["id"] == prompt_id), None)
    
    if not prompt:
        return RedirectResponse(url="/prompts?error=prompt_not_found", status_code=302)
    
    # Variables are already parsed as dict, not JSON string
    variables = prompt.get("variables", {})
    if isinstance(variables, str):
        import json
        variables = json.loads(variables)
    
    system_prompt = variables.get("system_prompt", "")
    user_prompt = variables.get("user_prompt", "")
    
    return create_main_layout(
        "Edit Prompt",
        Div(
            H1("Edit Prompt", style="margin-bottom: 2rem;"),
            Form(
                Div(
                    Label("Prompt Name", **{"for": "name"}),
                    Input(type="text", name="name", value=prompt["name"], required=True),
                    style="margin-bottom: 1rem;"
                ),
                Div(
                    Label("System Prompt", **{"for": "system_prompt"}),
                    Textarea(system_prompt, name="system_prompt", rows="8"),
                    style="margin-bottom: 1rem;"
                ),
                Div(
                    Label("User Prompt", **{"for": "user_prompt"}),
                    Textarea(user_prompt, name="user_prompt", rows="8"),
                    style="margin-bottom: 1rem;"
                ),
                Div(
                    Button("Update Prompt", type="submit", style="margin-right: 1rem;"),
                    Button("Cancel", type="button", onclick="window.location.href='/prompts'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem;"
                ),
                method="post",
                action=f"/prompts/edit/{prompt_id}"
            )
        ),
        current_page="prompts"
    )

@app.post("/prompts/create")
async def create_prompt(request):
    """Create a new prompt"""
    form_data = await request.form()
    from database import Database
    db = Database()
    
    name = form_data.get("prompt_name", "").strip()
    system_prompt = form_data.get("system_prompt", "").strip()
    user_prompt = form_data.get("user_prompt", "").strip()
    
    print(f"🔍 Creating prompt: name='{name}', system_len={len(system_prompt)}, user_len={len(user_prompt)}")
    
    if not name:
        print("❌ No name provided")
        return RedirectResponse(url="/prompts?error=name_required", status_code=302)
    
    if not system_prompt and not user_prompt:
        print("❌ No prompts provided")
        return RedirectResponse(url="/prompts?error=prompt_required", status_code=302)
    
    try:
        prompt_id = db.create_prompt(name, system_prompt or None, user_prompt or None)
        print(f"✅ Prompt created: {prompt_id}")
        return RedirectResponse(url=f"/prompts?created=prompt&id={prompt_id}", status_code=302)
    except Exception as e:
        print(f"❌ Error creating prompt: {e}")
        return RedirectResponse(url="/prompts?error=create_failed", status_code=302)

@app.post("/prompts/edit/{prompt_id}")
async def update_prompt(request):
    """Update a prompt"""
    prompt_id = request.path_params["prompt_id"]
    form_data = await request.form()
    from database import Database
    db = Database()
    
    updated = db.update_prompt(
        prompt_id,
        form_data.get("name"),
        form_data.get("system_prompt"),
        form_data.get("user_prompt")
    )
    
    if updated:
        return RedirectResponse(url="/prompts?updated=prompt", status_code=302)
    else:
        return RedirectResponse(url="/prompts?error=update_failed", status_code=302)

def read_dataset_content(dataset_id: str, max_lines: int = 10) -> str:
    """Read dataset content from file"""
    import os
    import json
    
    # Look for dataset file in uploads directory
    uploads_dir = Path(__file__).parent / "uploads"
    
    # Try different file extensions
    for ext in ['.jsonl', '.csv', '.json']:
        # Look for files containing the dataset_id
        for file_path in uploads_dir.glob(f"*{dataset_id}*{ext}"):
            try:
                with open(file_path, 'r') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append(f"... (showing first {max_lines} lines)")
                            break
                        lines.append(line.strip())
                    return '\n'.join(lines)
            except Exception as e:
                return f"Error reading file: {str(e)}"
    
    return "Dataset file not found"

@app.get("/datasets/view/{dataset_id}")
async def view_dataset(request):
    """View dataset contents"""
    dataset_id = request.path_params["dataset_id"]
    from database import Database
    db = Database()
    
    datasets = db.get_datasets()
    dataset = next((d for d in datasets if d["id"] == dataset_id), None)
    
    if not dataset:
        return RedirectResponse(url="/datasets?error=dataset_not_found", status_code=302)
    
    # Read actual dataset content
    content = read_dataset_content(dataset_id)
    
    return create_main_layout(
        "View Dataset",
        Div(
            H1(f"Dataset: {dataset['name']}", style="margin-bottom: 2rem;"),
            P(f"Type: {dataset['type']} • Rows: {dataset['rows']} • Size: {dataset['size']} • Created: {dataset['created']}", 
              style="margin-bottom: 2rem; color: #6b7280;"),
            Div(
                H3("Dataset Contents:", style="margin-bottom: 1rem;"),
                Pre(content, 
                    style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; max-height: 400px; font-size: 0.875rem;"),
                style="margin-bottom: 2rem;"
            ),
            Button("Back to Datasets", onclick="window.location.href='/datasets'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2")
        ),
        current_page="datasets"
    )

@app.get("/datasets/edit/{dataset_id}")
async def edit_dataset(request):
    """Edit a dataset"""
    dataset_id = request.path_params["dataset_id"]
    from database import Database
    db = Database()
    
    datasets = db.get_datasets()
    dataset = next((d for d in datasets if d["id"] == dataset_id), None)
    
    if not dataset:
        return RedirectResponse(url="/datasets?error=dataset_not_found", status_code=302)
    
    return create_main_layout(
        "Edit Dataset",
        Div(
            H1("Edit Dataset", style="margin-bottom: 2rem;"),
            Form(
                Div(
                    Label("Dataset Name", **{"for": "name"}),
                    Input(type="text", name="name", value=dataset["name"], required=True),
                    style="margin-bottom: 1rem;"
                ),
                Div(
                    Button("Update Dataset", type="submit", style="margin-right: 1rem;"),
                    Button("Cancel", type="button", onclick="window.location.href='/datasets'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem;"
                ),
                method="post",
                action=f"/datasets/edit/{dataset_id}"
            )
        ),
        current_page="datasets"
    )

@app.post("/datasets/upload")
async def upload_dataset(request):
    """Upload a new dataset"""
    form_data = await request.form()
    from database import Database
    import os
    from pathlib import Path
    
    db = Database()
    
    # Get form fields
    dataset_name = form_data.get("dataset_name", "").strip()
    file = form_data.get("dataset_file")
    
    if not dataset_name:
        return RedirectResponse(url="/datasets?error=name_required", status_code=302)
    
    if not file or not file.filename:
        return RedirectResponse(url="/datasets?error=file_required", status_code=302)
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Determine file type and count rows
        file_extension = Path(file.filename).suffix.lower()
        if file_extension == '.csv':
            file_type = "CSV"
            row_count = file_content.decode('utf-8').count('\n')
        elif file_extension in ['.json', '.jsonl']:
            file_type = "JSON"
            row_count = file_content.decode('utf-8').count('\n')
        else:
            return RedirectResponse(url="/datasets?error=unsupported_format", status_code=302)
        
        # Create dataset in database
        dataset_id = db.create_dataset(
            name=dataset_name,
            file_type=file_type,
            file_size=f"{file_size / 1024:.1f} KB",
            row_count=row_count
        )
        
        # Save file with dataset ID
        safe_name = dataset_name.replace(" ", "_").lower()
        file_path = uploads_dir / f"{safe_name}_{dataset_id}{file_extension}"
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return RedirectResponse(url=f"/datasets?created=dataset&id={dataset_id}", status_code=302)
        
    except Exception as e:
        print(f"❌ Error uploading dataset: {e}")
        return RedirectResponse(url="/datasets?error=upload_failed", status_code=302)

@app.post("/datasets/edit/{dataset_id}")
async def update_dataset(request):
    """Update a dataset"""
    dataset_id = request.path_params["dataset_id"]
    form_data = await request.form()
    from database import Database
    db = Database()
    
    # Simple name update - you can extend this for more fields
    updated = db.update_dataset_name(dataset_id, form_data.get("name"))
    
    if updated:
        return RedirectResponse(url="/datasets?updated=dataset", status_code=302)
    else:
        return RedirectResponse(url="/datasets?error=update_failed", status_code=302)

@app.post("/metrics/delete/{metric_id}")
async def delete_metric(request):
    """Delete a metric"""
    metric_id = request.path_params["metric_id"]
    from database import Database
    db = Database()
    
    success = db.delete_metric(metric_id)
    
    if success:
        return RedirectResponse(url="/metrics?deleted=metric", status_code=302)
    else:
        return RedirectResponse(url="/metrics?error=delete_failed", status_code=302)

# Delete routes
@app.post("/datasets/delete/{dataset_id}")
async def delete_dataset(request):
    """Delete a dataset"""
    dataset_id = request.path_params["dataset_id"]
    
    from database import Database
    db = Database()
    
    # Delete from SQLite database
    deleted = db.delete_dataset(dataset_id)
    
    if deleted:
        print(f"✅ Deleted dataset: {dataset_id}")
        print(f"📊 Remaining datasets: {len(db.get_datasets())}")
    else:
        print(f"❌ Dataset not found: {dataset_id}")
    
    # Redirect back to datasets page with success message
    return RedirectResponse(url="/datasets?deleted=dataset", status_code=302)

@app.post("/optimizations/delete/{optimization_id}")
async def delete_optimization(request):
    """Delete an optimization and clean up all related files"""
    optimization_id = request.path_params["optimization_id"]
    
    from database import Database
    db = Database()
    
    # Delete optimization and clean up files
    deleted = db.delete_optimization(optimization_id)
    
    if deleted:
        print(f"✅ Deleted optimization: {optimization_id}")
        return RedirectResponse(url="/?deleted=optimization", status_code=302)
    else:
        print(f"❌ Optimization not found: {optimization_id}")
        return RedirectResponse(url="/?error=optimization_not_found", status_code=302)

@app.post("/prompts/delete/{prompt_id}")
async def delete_prompt(request):
    """Delete a prompt"""
    prompt_id = request.path_params["prompt_id"]
    
    from database import Database
    db = Database()
    
    # Delete from SQLite database
    deleted = db.delete_prompt(prompt_id)
    
    if deleted:
        print(f"✅ Deleted prompt: {prompt_id}")
        print(f"📝 Remaining prompts: {len(db.get_prompts())}")
    else:
        print(f"❌ Prompt not found: {prompt_id}")
    
    # Redirect back to prompts page with success message
    return RedirectResponse(url="/prompts?deleted=prompt", status_code=302)

@app.post("/optimization/{optimization_id}/retry")
async def retry_optimization(request):
    """Retry a failed optimization"""
    optimization_id = request.path_params["optimization_id"]
    
    from database import Database
    db = Database()
    
    # Get the original optimization
    optimization = db.get_optimization(optimization_id)
    if not optimization:
        return RedirectResponse(url="/optimization?error=not_found", status_code=302)
    
    # Reset status and clear old logs/candidates
    db.conn.execute("UPDATE optimizations SET status = 'Starting', progress = 0 WHERE id = ?", (optimization_id,))
    db.conn.execute("DELETE FROM optimization_logs WHERE optimization_id = ?", (optimization_id,))
    db.conn.execute("DELETE FROM prompt_candidates WHERE optimization_id = ?", (optimization_id,))
    db.conn.commit()
    
    # Restart the optimization worker
    import subprocess
    from pathlib import Path
    
    worker_cmd = ["python3", "sdk_worker.py", optimization_id]
    frontend_dir = Path(__file__).parent  # Use frontend directory, not parent
    subprocess.Popen(worker_cmd, cwd=frontend_dir)
    
    return RedirectResponse(url="/optimization?started=true", status_code=302)

@app.get("/optimization/monitor/{optimization_id}")
def optimization_monitor_page(request):
    """Monitor running optimization progress"""
    optimization_id = request.path_params["optimization_id"]
    
    from database import Database
    db = Database()
    
    # Get optimization details
    optimization = db.get_optimization_by_id(optimization_id)
    if not optimization:
        return RedirectResponse(url="/optimization?error=not_found", status_code=302)
    
    # Get recent logs
    logs = db.get_optimization_logs(optimization_id)
    recent_logs = logs[-20:] if logs else []  # Last 20 logs
    
    page_content = Div(
        H2(f"Monitoring: {optimization['name']}", style="margin-bottom: 2rem; color: #1f2937;"),
        
        # Status Card
        Card(
            header=H3("Current Status"),
            content=Div(
                P(f"Status: {optimization['status']}", 
                  style=f"margin-bottom: 0.5rem; font-weight: 500; color: {'#10b981' if optimization['status'] == 'Completed' else '#3b82f6' if optimization['status'] == 'Running' else '#f59e0b'};"),
                P(f"Progress: {optimization.get('progress', 0)}%", style="margin-bottom: 0.5rem;"),
                P(f"Current Improvement: {optimization.get('improvement', 'N/A')}", style="margin-bottom: 0.5rem;"),
                P(f"Started: {optimization.get('started', 'N/A')}", style="margin-bottom: 0.5rem;"),
                Div(
                    Div(style=f"width: {optimization.get('progress', 0)}%; height: 20px; background: #10b981; border-radius: 10px; transition: width 0.3s ease;"),
                    style="width: 100%; height: 20px; background: #e5e7eb; border-radius: 10px; margin-top: 1rem;"
                )
            )
        ),
        
        # Recent Logs Card
        Card(
            header=H3("Recent Activity"),
            content=Div(
                *[Div(
                    Span(log.get('timestamp', ''), style="color: #6b7280; font-size: 0.875rem; margin-right: 1rem;"),
                    Span(log.get('level', '').upper(), style=f"color: {'#ef4444' if log.get('level') == 'error' else '#10b981' if log.get('level') == 'success' else '#6b7280'}; font-weight: 500; margin-right: 1rem;"),
                    Span(log.get('message', ''), style="color: #1f2937;"),
                    style="display: block; padding: 0.5rem; border-bottom: 1px solid #e5e7eb;"
                ) for log in recent_logs] if recent_logs else [
                    P("No recent activity", style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            )
        ),
        
        # Actions
        Div(
            Button("Refresh", 
                   onclick="window.location.reload()",
                   style="background: #3b82f6; color: white; margin-right: 1rem;"),
            Button("Back to Optimizations", 
                   onclick="window.location.href='/optimization'",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
            style="margin-top: 2rem; display: flex; gap: 1rem;"
        ),
        
        # Auto-refresh script
        Script("""
            // Auto-refresh every 5 seconds if optimization is still running
            const status = document.querySelector('p').textContent;
            if (status.includes('Running') || status.includes('Starting')) {
                setTimeout(() => {
                    window.location.reload();
                }, 5000);
            }
        """)
    )
    
    return create_main_layout("Monitor Optimization", page_content, current_page="optimization")

@app.get("/optimization/results/{optimization_id}")
def optimization_results_page(request):
    """View detailed optimization results"""
    optimization_id = request.path_params["optimization_id"]
    
    from database import Database
    db = Database()
    
    # Get optimization details
    optimization = db.get_optimization_by_id(optimization_id)
    if not optimization:
        return RedirectResponse(url="/optimization?error=not_found", status_code=302)
    
    # Get optimization logs
    logs = db.get_optimization_logs(optimization_id)
    
    # Get prompt candidates if available
    candidates = db.get_prompt_candidates(optimization_id)
    
    page_content = Div(
        H2(f"Optimization Results: {optimization['name']}", style="margin-bottom: 2rem; color: #1f2937;"),
        
        # Overview Card
        Card(
            header=H3("Overview"),
            content=Div(
                P(f"Status: {optimization['status']}", style="margin-bottom: 0.5rem; font-weight: 500;"),
                P(f"Progress: {optimization.get('progress', 0)}%", style="margin-bottom: 0.5rem;"),
                P(f"Improvement: {optimization.get('improvement', 'N/A')}", style="margin-bottom: 0.5rem;"),
                P(f"Started: {optimization.get('started', 'N/A')}", style="margin-bottom: 0.5rem;"),
                P(f"Completed: {optimization.get('completed', 'N/A')}", style="margin-bottom: 0.5rem;"),
            )
        ),
        
        # Prompt Results - Reordered: Baseline → Few-shot → Optimized
        Card(
            header=H3("Optimization Results"),
            content=Div(
                # 1. Baseline Prompt (first)
                *[
                    Div(
                        H4("Baseline Prompt", 
                           style="margin-bottom: 1rem; color: #1f2937; font-size: 1.25rem;"),
                        
                        P(f"Score: {candidate.get('score', 'N/A')}", 
                          style="margin-bottom: 1rem; font-weight: 600; color: #dc2626;"),
                        
                        # Parse structured data if available
                        (lambda data: 
                            Div(
                                # System Prompt
                                Div(
                                    H5("System Prompt:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                    Div(
                                        eval(data.split('|', 1)[1])['system'] if '|' in data and data.split('|', 1)[1] else data,
                                        style="background: #f9fafb; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-left: 4px solid #10b981; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                    ),
                                ),
                                
                                # User Prompt  
                                Div(
                                    H5("User Prompt:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                    Div(
                                        eval(data.split('|', 1)[1])['user'] if '|' in data and data.split('|', 1)[1] else "No user prompt",
                                        style="background: #f0f9ff; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-left: 4px solid #3b82f6; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                    ),
                                ),
                                
                                style="background: #ffffff; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem;"
                            ) if '|' in data else 
                            # Fallback for non-structured data
                            Div(
                                H5("Content:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                Div(
                                    data,
                                    style="background: #f9fafb; padding: 1rem; border-radius: 0.375rem; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                )
                            )
                        )(candidate.get('prompt_text', 'No content')),
                        
                        style="margin-bottom: 2rem; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; background: #fafafa;"
                    ) for candidate in candidates if candidate and candidate.get('prompt_text', '').startswith('BASELINE|')
                ],
                
                # 2. Optimized Prompt (last)
                *[
                    Div(
                        Div(
                            H4("Optimized Prompt", 
                               style="margin-bottom: 1rem; color: #1f2937; font-size: 1.25rem; flex: 1;"),
                            Button("Optimize Further", 
                                   onclick=f"optimizeFurther('{optimization_id}')",
                                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1"),
                            style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;"
                        ),
                        
                        P(f"Score: {candidate.get('score', 'N/A')}", 
                          style="margin-bottom: 1rem; font-weight: 600; color: #059669;"),
                        
                        # Parse structured data if available
                        (lambda data: 
                            Div(
                                # System Prompt
                                Div(
                                    H5("System Prompt:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                    Div(
                                        eval(data.split('|', 1)[1])['system'] if '|' in data and data.split('|', 1)[1] else data,
                                        style="background: #f9fafb; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-left: 4px solid #10b981; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                    ),
                                ),
                                
                                # User Prompt  
                                Div(
                                    H5("User Prompt:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                    Div(
                                        eval(data.split('|', 1)[1])['user'] if '|' in data and data.split('|', 1)[1] else "No user prompt",
                                        style="background: #f0f9ff; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem; border-left: 4px solid #3b82f6; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                    ),
                                ),
                                
                                # Few-shot info for optimized
                                (Div(
                                    P(f"Few-shot Examples: {eval(data.split('|', 1)[1])['few_shot_count']}", 
                                      style="margin: 0.5rem 0; color: #6b7280; font-size: 0.875rem;")
                                ) if '|' in data and 'few_shot_count' in eval(data.split('|', 1)[1]) else None),
                                
                                style="background: #ffffff; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem;"
                            ) if '|' in data else 
                            # Fallback for non-structured data
                            Div(
                                H5("Content:", style="margin: 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                Div(
                                    data,
                                    style="background: #f9fafb; padding: 1rem; border-radius: 0.375rem; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.875rem; white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;"
                                )
                            )
                        )(candidate.get('prompt_text', 'No content')),
                        
                        style="margin-bottom: 2rem; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; background: #fafafa;"
                    ) for candidate in candidates if candidate and candidate.get('prompt_text', '').startswith('OPTIMIZED|')
                ] if candidates else [
                    P("No optimization results available", style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            )
        ),
        
        # Few-shot Examples Card (separate display)
        Card(
            header=Div(
                H3("Few-shot Examples"),
                Button("More Info", 
                       variant="ghost", 
                       size="sm",
                       onclick="toggleInfo('few-shot-info')",
                       style="margin-left: auto;"),
                style="display: flex; justify-content: space-between; align-items: center;"
            ),
            content=Div(
                # Collapsible info section
                Div(
                    H4("Implementation:", style="font-weight: 600; margin-bottom: 0.5rem;"),
                    Ul(
                        Li("Few-shot examples are part of the Nova SDK's optimization workflow"),
                        Li("They're generated automatically during the MIPROv2 + Nova Model Tips optimization process"),
                        Li("The examples are designed to be task-specific and help improve the model's performance on the target dataset"),
                        style="margin-bottom: 1rem; padding-left: 1rem;"
                    ),
                    P("The few-shot examples essentially act as \"training wheels\" that help the language model understand the specific patterns and requirements of your task without requiring actual fine-tuning.",
                      style="font-style: italic; color: #6b7280;"),
                    id="few-shot-info",
                    style="display: none; padding: 1rem; background: #f9fafb; border-radius: 0.5rem; margin-bottom: 1rem;"
                ),
                
                # Original few-shot examples content
                *[
                    Div(
                        H4(f"Generated {eval(candidate.get('prompt_text', '').split('|', 1)[1])['count']} Few-shot Examples", 
                           style="margin-bottom: 1rem; color: #1f2937; font-size: 1.1rem;"),
                        
                        *[
                            Div(
                                H5(f"Example {example['number']}:", 
                                   style="margin: 1rem 0 0.5rem 0; color: #374151; font-size: 0.875rem; font-weight: 600;"),
                                
                                # Display few-shot example content with better formatting
                                (lambda content:
                                    # Try to extract input/output from the string safely
                                    Div(
                                        *([
                                            Div(
                                                H6("Input:", style="margin: 0.5rem 0 0.25rem 0; color: #4b5563; font-size: 0.8rem; font-weight: 600;"),
                                                Div(
                                                    content.split("'input': '")[1].split("', 'output'")[0] if "'input': '" in content and "', 'output'" in content else content.split("'input': '")[1].split("'}")[0] if "'input': '" in content else content,
                                                    style="background: #f0f9ff; padding: 0.75rem; border-radius: 0.25rem; margin-bottom: 0.5rem; border-left: 3px solid #3b82f6; font-size: 0.8rem; white-space: pre-wrap; word-wrap: break-word;"
                                                )
                                            ),
                                        ] if "'input': '" in content else [
                                            # Fallback - just display the content cleanly
                                            Div(
                                                content.replace('\\n', '\n').replace("\\'", "'"),
                                                style="background: #f3e8ff; padding: 0.75rem; border-radius: 0.25rem; border-left: 3px solid #8b5cf6; font-size: 0.8rem; white-space: pre-wrap; word-wrap: break-word;"
                                            )
                                        ])
                                    )
                                )(example['content']),
                                
                                style="margin-bottom: 1.5rem; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.375rem; background: #fafafa;"
                            ) for example in eval(candidate.get('prompt_text', '').split('|', 1)[1])['examples']
                        ],
                        
                        style="background: #ffffff; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem;"
                    ) for candidate in candidates if candidate and candidate.get('prompt_text', '').startswith('FEWSHOT|')
                ] if any(candidate.get('prompt_text', '').startswith('FEWSHOT|') for candidate in candidates if candidate) else [
                    P("No few-shot examples generated", style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            )
        ),
        
        # Logs Card
        Card(
            header=H3("Optimization Logs"),
            content=Div(
                *[Div(
                    Span(log.get('timestamp', ''), style="color: #6b7280; font-size: 0.875rem; margin-right: 1rem;"),
                    Span(log.get('level', '').upper(), style=f"color: {'#ef4444' if log.get('level') == 'error' else '#10b981' if log.get('level') == 'success' else '#6b7280'}; font-weight: 500; margin-right: 1rem;"),
                    Span(log.get('message', ''), style="color: #1f2937;"),
                    style="display: block; padding: 0.5rem; border-bottom: 1px solid #e5e7eb;"
                ) for log in logs] if logs else [
                    P("No logs available", style="color: #6b7280; text-align: center; padding: 2rem;")
                ]
            )
        ),
        
        # Action Buttons
        Div(
            Button("Delete Optimization", 
                   onclick=f"if(confirm('Are you sure you want to delete this optimization? This will remove all related files and cannot be undone.')) {{ fetch('/optimizations/delete/{optimization_id}', {{method: 'POST'}}).then(() => window.location.href='/optimization'); }}",
                   variant="secondary",
                   style="background: #fee2e2; color: #dc2626; border-color: #fca5a5; margin-right: 1rem;"),
            Button("Back to Optimizations", 
                   onclick="window.location.href='/optimization'",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
            style="margin-top: 2rem;"
        ),
        
        # JavaScript for toggle functionality
        Script("""
            function toggleInfo(elementId) {
                const element = document.getElementById(elementId);
                if (element.style.display === 'none') {
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
            }
            
            function optimizeFurther(optimizationId) {
                if (confirm('Start a new optimization using this optimized prompt as the baseline?')) {
                    fetch(`/optimization/${optimizationId}/optimize-further`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = `/optimization/monitor/${data.new_optimization_id}`;
                        } else {
                            alert('Error: ' + (data.error || 'Failed to start optimization'));
                        }
                    })
                    .catch(error => {
                        alert('Error: ' + error.message);
                    });
                }
            }
        """)
    )
    
    return create_main_layout("Optimization Results", page_content, current_page="optimization")

@app.post("/optimization/{optimization_id}/optimize-further")
async def optimize_further(request):
    """Start a new optimization using the optimized prompt as baseline"""
    optimization_id = request.path_params["optimization_id"]
    
    try:
        # Create fresh database connection to avoid "closed database" errors
        from database import Database
        db_local = Database()
        
        # Get the original optimization details
        optimization = db_local.get_optimization(optimization_id)
        if not optimization:
            return {"success": False, "error": "Optimization not found"}
        
        print(f"🔍 DEBUG - Optimization keys: {list(optimization.keys()) if optimization else 'None'}")
        print(f"🔍 DEBUG - Optimization data: {optimization}")
        
        # Get the optimized prompt from candidates
        candidates = db_local.get_prompt_candidates(optimization_id)
        optimized_candidate = None
        few_shot_examples = []
        
        for candidate in candidates:
            if candidate.get('prompt_text', '').startswith('OPTIMIZED|'):
                optimized_candidate = candidate
            elif candidate.get('prompt_text', '').startswith('FEWSHOT|'):
                # Extract few-shot examples
                try:
                    fewshot_data = json.loads(candidate['prompt_text'].split('|', 1)[1])
                    few_shot_examples = fewshot_data.get('examples', [])
                    print(f"🔍 DEBUG - Found {len(few_shot_examples)} few-shot examples")
                except:
                    print("🔍 DEBUG - Failed to parse few-shot data")
        
        if not optimized_candidate:
            return {"success": False, "error": "No optimized prompt found"}
        
        # Parse the optimized prompt data
        import json
        import ast
        try:
            prompt_text = optimized_candidate['prompt_text']
            print(f"🔍 DEBUG - Raw prompt_text: {prompt_text[:200]}...")
            
            if '|' in prompt_text:
                data_part = prompt_text.split('|', 1)[1]
                print(f"🔍 DEBUG - Data part: {data_part[:200]}...")
                
                # Try JSON first, then Python dict format
                try:
                    optimized_data = json.loads(data_part)
                except json.JSONDecodeError:
                    # It's a Python dict string, use ast.literal_eval
                    optimized_data = ast.literal_eval(data_part)
                    print("🔍 DEBUG - Used ast.literal_eval for Python dict format")
            else:
                print("🔍 DEBUG - No | separator found in prompt_text")
                return {"success": False, "error": "Invalid prompt data format"}
                
        except (json.JSONDecodeError, ValueError, SyntaxError) as e:
            print(f"🔍 DEBUG - Parse error: {e}")
            print(f"🔍 DEBUG - Problematic data: {data_part if 'data_part' in locals() else 'N/A'}")
            return {"success": False, "error": f"Invalid data in optimized prompt: {str(e)}"}
        
        # Create new prompt with optimized content + few-shot examples
        baseline_system = optimized_data.get('system', '')
        baseline_user = optimized_data.get('user', '')
        
        # If we have few-shot examples, format them properly as instructional examples
        if few_shot_examples:
            few_shot_context = "\n\nExample interactions from previous optimization:\n"
            
            for i, example in enumerate(few_shot_examples[:3], 1):  # Limit to first 3
                example_content = example.get('content', str(example))
                
                # Parse the conversation format and extract meaningful examples
                try:
                    import json
                    if isinstance(example_content, str) and example_content.startswith('['):
                        # Parse the JSON conversation format
                        conversation = json.loads(example_content)
                        
                        # Extract user input and assistant response
                        user_input = None
                        assistant_response = None
                        
                        for turn in conversation:
                            if turn.get('role') == 'user':
                                user_content = turn.get('content', [])
                                if user_content and isinstance(user_content, list):
                                    user_input = user_content[0].get('text', '')
                            elif turn.get('role') == 'assistant':
                                assistant_content = turn.get('content', [])
                                if assistant_content and isinstance(assistant_content, list):
                                    assistant_response = assistant_content[0].get('text', '')
                        
                        # Format as instructional example
                        if user_input and assistant_response:
                            # Extract just the core input from the user prompt
                            if 'The input is: [' in user_input:
                                core_input = user_input.split('The input is: [')[1].split(']')[0]
                                few_shot_context += f"\nExample {i}:\n"
                                few_shot_context += f"Input: {core_input[:200]}...\n"
                                few_shot_context += f"Expected Output: {assistant_response}\n"
                
                except (json.JSONDecodeError, KeyError, IndexError):
                    # Fallback: use truncated string representation
                    few_shot_context += f"\nExample {i}: {example_content[:100]}...\n"
            
            baseline_system += few_shot_context
            print(f"🔍 DEBUG - Added {len(few_shot_examples)} few-shot examples as instructional examples")
        
        new_prompt_id = db_local.create_prompt(
            name=f"Optimized from {optimization_id} (with {len(few_shot_examples)} few-shot examples)",
            system_prompt=baseline_system,
            user_prompt=baseline_user
        )
        
        # Find dataset ID from name
        datasets = db_local.get_datasets()
        dataset_name = optimization.get('dataset')
        dataset_id = None
        
        for dataset in datasets:
            if dataset['name'] == dataset_name:
                dataset_id = dataset['id']
                break
        
        if not dataset_id:
            return {"success": False, "error": f"Dataset '{dataset_name}' not found"}
        
        print(f"🔍 DEBUG - Found dataset ID: {dataset_id} for name: {dataset_name}")
        
        # Create new optimization with the new prompt
        new_optimization_id = db_local.create_optimization(
            name=f"Further optimization of '{optimization.get('name', optimization_id)}'",
            prompt_id=new_prompt_id,
            dataset_id=dataset_id,
            metric_id=optimization.get('metric_id')
        )
        
        # Start the optimization process
        from sdk_worker import run_optimization_worker
        import threading
        
        # Try to inherit rate limit from original optimization logs
        original_rate_limit = 60  # Conservative default
        try:
            # Look for rate limit in optimization logs
            logs = db_local.get_optimization_logs(optimization_id)
            for log in logs:
                if 'RPM' in log.get('message', '') and 'rate limit' in log.get('message', '').lower():
                    # Extract rate limit from log message like "Rate limit: 1000 RPM"
                    import re
                    match = re.search(r'(\d+)\s*RPM', log['message'])
                    if match:
                        original_rate_limit = int(match.group(1))
                        print(f"🔍 DEBUG - Inherited rate limit from original optimization: {original_rate_limit} RPM")
                        break
        except Exception as e:
            print(f"🔍 DEBUG - Could not inherit rate limit, using default: {e}")
        
        # Create config for the optimization including few-shot examples
        config = {
            "model_id": "us.amazon.nova-premier-v1:0",
            "rate_limit": original_rate_limit,
            "mode": "pro",
            "baseline_few_shot_examples": few_shot_examples  # Pass few-shot examples
        }
        
        # Start the optimization process in background using asyncio instead of threading
        # to avoid DSPy thread configuration issues
        import asyncio
        import subprocess
        
        # Use subprocess to run optimization in separate process instead of thread
        worker_cmd = [
            sys.executable, "sdk_worker.py", 
            new_optimization_id, 
            json.dumps(config)
        ]
        
        # Start worker process in background
        subprocess.Popen(worker_cmd, cwd=os.path.dirname(__file__))
        
        return {"success": True, "new_optimization_id": new_optimization_id}
        
    except Exception as e:
        print(f"Error in optimize_further: {e}")
        return {"success": False, "error": str(e)}

@app.post("/optimizations/delete/{optimization_id}")
async def delete_optimization(request):
    """Delete an optimization job"""
    optimization_id = request.path_params["optimization_id"]
    
    from database import Database
    db = Database()
    
    # Delete from SQLite database
    deleted = db.delete_optimization(optimization_id)
    
    if deleted:
        print(f"✅ Deleted optimization: {optimization_id}")
        print(f"⚡ Remaining optimizations: {len(db.get_optimizations())}")
    else:
        print(f"❌ Optimization not found: {optimization_id}")
    
    # Redirect back to optimization page with success message
    return RedirectResponse(url="/optimization?deleted=optimization", status_code=302)

# Real optimization routes
@app.post("/optimization/start")
async def start_optimization(request):
    """Start a real optimization run"""
    print("🔍 DEBUG - OPTIMIZATION START ROUTE HIT")
    
    try:
        # Get form data
        form_data = await request.form()
        print(f"🔍 DEBUG - Form data received: {dict(form_data)}")
        
        prompt_id = form_data.get("prompt_id")
        dataset_id = form_data.get("dataset_id")
        metric_id = form_data.get("metric_id")
        optimization_name = form_data.get("name", f"Optimization {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        print(f"🔍 DEBUG - Extracted values:")
        print(f"  - optimization_name: {optimization_name}")
        print(f"  - prompt_id: {prompt_id}")
        print(f"  - dataset_id: {dataset_id}")
        print(f"  - metric_id: {metric_id}")
        
        # Get advanced configuration
        model_mode = form_data.get("model_mode", "lite")  # lite, pro, premier
        train_split = float(form_data.get("train_split", "0.5"))  # 0.5 = 50/50 split
        record_limit = form_data.get("record_limit", "")
        rate_limit = form_data.get("rate_limit", "60")
        
        # Validate required fields
        if not prompt_id or not dataset_id or not metric_id:
            return RedirectResponse(url="/optimization?error=missing_data", status_code=302)
        
        # Debug: Log what we received
        print(f"🔍 Received prompt_id: {prompt_id}")
        print(f"🔍 Received dataset_id: {dataset_id}")
        
        # Verify the prompt exists
        try:
            from database import Database
            db = Database()
            print(f"🔍 Database initialized successfully")
            
            # Use get_prompts method instead of get_prompt
            prompts = db.get_prompts()
            prompt_data = next((p for p in prompts if p["id"] == prompt_id), None)
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
                record_limit_int = max(5, min(10000, record_limit_int))  # Minimum 5 records
            except ValueError:
                record_limit_int = None
        
        # Create optimization record with configuration
        try:
            print(f"🔍 DEBUG - Creating optimization with metric_id: {metric_id}")
            optimization_id = db.create_optimization(optimization_name, prompt_id, dataset_id, metric_id)
            print(f"✅ Created optimization record: {optimization_id}")
            
            # Verify the record was created with metric_id
            created_opt = db.get_optimization_by_id(optimization_id)
            if created_opt:
                print(f"✅ Verified optimization in database: {created_opt['name']} - {created_opt['status']}")
                print(f"🔍 DEBUG - Saved metric_id in database: {created_opt.get('metric_id')}")
            else:
                print("❌ Failed to retrieve created optimization from database")
        except Exception as e:
            print(f"❌ Error creating optimization: {e}")
            return RedirectResponse(url="/optimization?error=start_failed", status_code=302)
        
        # Store configuration in optimization record (we'll need to update the database schema for this)
        optimization_config = {
            "model_mode": model_mode,
            "train_split": train_split,
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
                "sdk_worker.py", 
                optimization_id, 
                config_json
            ]
            
            # Start worker process in background (run from frontend directory)
            frontend_dir = Path(__file__).parent
            subprocess.Popen(worker_cmd, cwd=frontend_dir)
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
    from database import Database
    db = Database()
    candidates = db.get_prompt_candidates(optimization_id)
    return {"candidates": candidates}

@app.get("/optimization/{optimization_id}/prompts")
async def view_prompts(request):
    """View baseline vs optimized prompts"""
    optimization_id = request.path_params['optimization_id']
    from database import Database
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
                            cls="bg-green-50 p-3 rounded text-xs whitespace-pre-wrap border max-h-96 overflow-y-auto"),
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
        
        # Get the original prompt data to show actual content instead of optimizer template
        optimization = db.get_optimization(optimization_id)
        if optimization:
            prompts = db.get_prompts()
            # The optimization table stores prompt name, not ID, so find by name
            original_prompt = next((p for p in prompts if p["name"] == optimization["prompt"]), None)
            if original_prompt:
                # Parse the original prompt variables
                import json
                try:
                    prompt_vars = json.loads(original_prompt["variables"])
                    original_system = prompt_vars.get("system_prompt", "")
                    original_user = prompt_vars.get("user_prompt", "")
                    
                    # Replace optimizer template with actual prompt content for display
                    for c in candidates:
                        if c['iteration'] == 'Trial_1_System' or 'System' in c['iteration']:
                            # Show the actual system prompt instead of optimizer template
                            if original_system and "You are tasked with translating" in c['user_prompt']:
                                c['user_prompt'] = original_system
                        elif c['iteration'] == 'Trial_1_User' or 'User' in c['iteration']:
                            # Show the actual user prompt
                            if original_user:
                                c['user_prompt'] = original_user
                                
                except json.JSONDecodeError:
                    pass
        
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
                            P(f"Improvement: {optimization.get('improvement', 'N/A')}", 
                              style="font-weight: 600; color: #10b981;" if optimization.get('improvement', '').startswith('+') else "font-weight: 600;",
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
                        Div(
                            *[Div(
                                # Candidate header with expand/collapse button
                                Div(
                                    Div(
                                        H5(f"Candidate {i+1}: {candidate['iteration']}", 
                                           style="margin: 0; font-weight: 600; color: #1f2937;"),
                                        P(f"Score: {candidate['score']:.3f}" if candidate["score"] else "Score: N/A", 
                                          style="margin: 0; color: #6b7280; font-size: 0.875rem;"),
                                        style="flex: 1;"
                                    ),
                                    Button("▼ Show Response", 
                                           onclick=f"toggleResponse({i})",
                                           id=f"toggle-btn-{i}",
                                           style="background: #3b82f6; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 0.25rem; font-size: 0.75rem; cursor: pointer;"),
                                    style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; margin-bottom: 0.5rem;"
                                ),
                                
                                # Collapsible response content
                                Div(
                                    Div(
                                        H6("Prompt Text:", style="margin: 0 0 0.5rem 0; font-weight: 500; color: #374151;"),
                                        Pre(candidate["user_prompt"] or "No prompt text", 
                                            style="background: #f1f5f9; padding: 1rem; border-radius: 0.375rem; font-family: 'Monaco', 'Consolas', monospace; font-size: 0.75rem; white-space: pre-wrap; margin-bottom: 1rem; border: 1px solid #e2e8f0;"),
                                        style="margin-bottom: 1rem;"
                                    ),
                                    Div(
                                        H6("Model Response:", style="margin: 0 0 0.5rem 0; font-weight: 500; color: #374151;"),
                                        Div(
                                            P("Loading model response...", 
                                              style="color: #6b7280; font-style: italic;",
                                              id=f"response-content-{i}"),
                                            style="background: #fefefe; padding: 1rem; border-radius: 0.375rem; border: 1px solid #e5e7eb; min-height: 100px;"
                                        ),
                                        style="margin-bottom: 1rem;"
                                    ),
                                    style="padding: 1rem; background: white; border-radius: 0.375rem; border: 1px solid #e5e7eb; display: none;",
                                    id=f"response-{i}"
                                ),
                                style="margin-bottom: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; overflow: hidden;"
                            ) for i, candidate in enumerate(candidates)]
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
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem;"
                ),
                
                # JavaScript for real-time updates
                Script(f"""
                    const optimizationId = '{optimization_id}';
                    let autoRefreshEnabled = true;
                    let refreshInterval;
                    
                    function toggleResponse(candidateIndex) {{
                        const responseDiv = document.getElementById(`response-${{candidateIndex}}`);
                        const toggleBtn = document.getElementById(`toggle-btn-${{candidateIndex}}`);
                        const responseContent = document.getElementById(`response-content-${{candidateIndex}}`);
                        
                        if (responseDiv.style.display === 'none' || responseDiv.style.display === '') {{
                            // Show response
                            responseDiv.style.display = 'block';
                            toggleBtn.textContent = '▲ Hide Response';
                            
                            // Fetch model response if not already loaded
                            if (responseContent.textContent === 'Loading model response...') {{
                                fetchModelResponse(candidateIndex);
                            }}
                        }} else {{
                            // Hide response
                            responseDiv.style.display = 'none';
                            toggleBtn.textContent = '▼ Show Response';
                        }}
                    }}
                    
                    function fetchModelResponse(candidateIndex) {{
                        const responseContent = document.getElementById(`response-content-${{candidateIndex}}`);
                        
                        // Simulate fetching model response (replace with actual API call)
                        setTimeout(() => {{
                            responseContent.innerHTML = `
                                <div style="font-family: monospace; font-size: 0.875rem; line-height: 1.4;">
                                    <p style="margin-bottom: 0.5rem; color: #059669;"><strong>Model Output:</strong></p>
                                    <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 0.25rem; border-left: 3px solid #10b981;">
                                        {{"urgency": "medium", "sentiment": "neutral", "categories": {{"emergency_repair_services": false, "routine_maintenance": true}}}}
                                    </div>
                                    <p style="margin: 0.75rem 0 0.25rem 0; color: #7c3aed;"><strong>Expected Output:</strong></p>
                                    <div style="background: #faf5ff; padding: 0.75rem; border-radius: 0.25rem; border-left: 3px solid #8b5cf6;">
                                        support
                                    </div>
                                    <p style="margin: 0.75rem 0 0.25rem 0; color: #dc2626;"><strong>Evaluation:</strong></p>
                                    <div style="background: #fef2f2; padding: 0.75rem; border-radius: 0.25rem; border-left: 3px solid #ef4444;">
                                        Score: 0.75 (Good match for category classification)
                                    </div>
                                </div>
                            `;
                        }}, 500);
                    }}
                    
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
    
    return create_main_layout(
        f"Monitor: {optimization['name']}",
        Div(*content),
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

# === DATASET GENERATOR API ENDPOINTS ===

@app.post("/datasets/generator/start")
async def start_generator(request):
    """Initialize dataset generator session"""
    try:
        from dataset_conversation import DatasetConversationService
        import uuid
        
        session_id = f"gen_{uuid.uuid4().hex[:8]}"
        conversation_service = DatasetConversationService()
        
        # Store session in memory (in production, use proper session storage)
        if not hasattr(app, 'generator_sessions'):
            app.generator_sessions = {}
        
        app.generator_sessions[session_id] = {
            'conversation_service': conversation_service,
            'step': 'start'
        }
        
        # Start conversation
        response = conversation_service.start_conversation()
        response['session_id'] = session_id
        
        return response
        
    except Exception as e:
        print(f"Error starting generator: {e}")
        return {"success": False, "error": str(e)}

@app.post("/datasets/generator/analyze-prompt")
async def analyze_prompt(request):
    """Analyze selected prompt for dataset generation"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        prompt_id = form_data.get('prompt_id')
        
        if not session_id or session_id not in app.generator_sessions:
            return {"success": False, "error": "Invalid session"}
        
        # Get prompt data
        prompt_data = db.get_prompt(prompt_id)
        if not prompt_data:
            return {"success": False, "error": "Prompt not found"}
        
        # Analyze prompt
        conversation_service = app.generator_sessions[session_id]['conversation_service']
        prompt_text = f"System: {prompt_data.get('system_prompt', '')}\nUser: {prompt_data.get('user_prompt', '')}"
        
        analysis = conversation_service.analyze_prompt(prompt_text)
        
        return {
            "success": True,
            "analysis": analysis,
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"Error analyzing prompt: {e}")
        return {"success": False, "error": str(e)}

@app.post("/datasets/generator/conversation")
async def continue_conversation(request):
    """Continue conversational requirements gathering"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        user_message = form_data.get('message', '')
        
        print(f"🔍 DEBUG - Conversation request: session_id={session_id}, message='{user_message}'")
        
        if not session_id or session_id not in app.generator_sessions:
            print(f"🔍 DEBUG - Invalid session: {session_id}, available sessions: {list(app.generator_sessions.keys())}")
            return {"success": False, "error": "Invalid session"}
        
        conversation_service = app.generator_sessions[session_id]['conversation_service']
        print(f"🔍 DEBUG - Calling conversation service with message: '{user_message}'")
        
        response = conversation_service.start_conversation(user_message)
        print(f"🔍 DEBUG - Conversation service response: {response}")
        
        return {
            "success": True,
            **response
        }
        
    except Exception as e:
        print(f"Error in conversation: {e}")
        return {"success": False, "error": str(e)}

@app.post("/datasets/generator/generate-samples")
async def generate_samples(request):
    """Generate initial 5 samples for review"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        
        if not session_id or session_id not in app.generator_sessions:
            return {"success": False, "error": "Invalid session"}
        
        conversation_service = app.generator_sessions[session_id]['conversation_service']
        generation_config = conversation_service.get_generation_config()
        
        # Initialize sample generator
        from sample_generator import SampleGeneratorService
        sample_generator = SampleGeneratorService()
        
        # Store sample generator in session
        app.generator_sessions[session_id]['sample_generator'] = sample_generator
        
        # Generate samples
        result = sample_generator.generate_initial_samples(generation_config, session_id)
        
        return result
        
    except Exception as e:
        print(f"Error generating samples: {e}")
        return {"success": False, "error": str(e)}

@app.post("/datasets/generator/annotate")
async def process_annotations(request):
    """Process user annotations and iterate on samples"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        
        if not session_id or session_id not in app.generator_sessions:
            return {"success": False, "error": "Invalid session"}
        
        # Parse annotations from form data
        annotations = {}
        for key, value in form_data.items():
            if key.startswith('annotation_'):
                sample_id = key.replace('annotation_', '')
                if value.strip():
                    annotations[sample_id] = [value.strip()]
        
        sample_generator = app.generator_sessions[session_id]['sample_generator']
        result = sample_generator.process_annotations(session_id, annotations)
        
        return result
        
    except Exception as e:
        print(f"Error processing annotations: {e}")
        return {"success": False, "error": str(e)}

@app.post("/datasets/generator/finalize")
async def finalize_dataset(request):
    """Generate and save full dataset"""
    try:
        form_data = await request.form()
        session_id = form_data.get('session_id')
        dataset_name = form_data.get('dataset_name', 'AI Generated Dataset')
        num_records = int(form_data.get('num_records', 50))
        output_format = form_data.get('output_format', 'jsonl')
        
        if not session_id or session_id not in app.generator_sessions:
            return {"success": False, "error": "Invalid session"}
        
        sample_generator = app.generator_sessions[session_id]['sample_generator']
        
        # Generate full dataset
        dataset_result = sample_generator.generate_full_dataset(session_id, num_records, output_format)
        
        if not dataset_result['success']:
            return dataset_result
        
        # Save dataset to file and database
        file_extension = dataset_result['file_extension']
        dataset_content = dataset_result['dataset']
        
        # Create dataset file
        import os
        os.makedirs('uploads', exist_ok=True)
        
        dataset_id = db.create_dataset(
            name=dataset_name,
            file_type=file_extension.upper(),
            file_size=f"{len(dataset_content)} bytes",
            row_count=dataset_result['record_count']
        )
        
        # Save file
        file_path = f"uploads/{dataset_name.replace(' ', '_').lower()}_{dataset_id}.{file_extension}"
        with open(file_path, 'w') as f:
            f.write(dataset_content)
        
        # Clean up session
        if session_id in app.generator_sessions:
            del app.generator_sessions[session_id]
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "record_count": dataset_result['record_count'],
            "format": output_format,
            "file_path": file_path
        }
        
    except Exception as e:
        print(f"Error finalizing dataset: {e}")
        return {"success": False, "error": str(e)}

@app.get("/datasets/generator")
async def dataset_generator_page(request):
    """AI Dataset Generator page"""
    user = await get_current_user(request)
    
    # Get available prompts for optional selection
    db = Database()
    available_prompts = db.get_prompts()
    
    content = [
        H1("AI Dataset Generator", style="margin-bottom: 2rem;"),
        
        # Step indicator
        Div(
            Div("1", cls="step-number active", id="step-1"),
            Div("2", cls="step-number", id="step-2"),
            Div("3", cls="step-number", id="step-3"),
            Div("4", cls="step-number", id="step-4"),
            Div("5", cls="step-number", id="step-5"),
            Div("6", cls="step-number", id="step-6"),
            cls="step-indicator",
            style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem;"
        ),
        
        # Step 1: Prompt Selection (Optional)
        Card(
            header=H3("Step 1: Prompt Selection (Optional)"),
            content=Div(
                P("Do you have an existing prompt you'd like to use as reference for dataset generation?", 
                  style="margin-bottom: 1rem;"),
                
                Div(
                    Select(
                        Option("No prompt - start from scratch", value="", selected=True),
                        *[Option(f"{prompt['name']}", value=prompt["id"]) 
                          for prompt in available_prompts],
                        id="prompt-select",
                        style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                    ),
                    Button("Continue", 
                           onclick="startConversation()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2")
                )
            ),
            id="step-1-card"
        ),
        
        # Step 2: Conversational Requirements (Hidden initially)
        Card(
            header=H3("Step 2: Requirements Gathering"),
            content=Div(
                Div(id="conversation-area", style="min-height: 200px; margin-bottom: 1rem;"),
                Div(
                    Input(type="text", 
                          id="user-input", 
                          placeholder="Type your response here...",
                          style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-right: 0.5rem;"),
                    Button("Send", 
                           onclick="sendMessage()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem;"
                )
            ),
            id="step-2-card",
            style="display: none;"
        ),
        
        # Step 3: Sample Review (Hidden initially)
        Card(
            header=H3("Step 3: Sample Review"),
            content=Div(
                P("Review the generated samples below. You can edit them or generate new ones.", 
                  style="margin-bottom: 1rem;"),
                Div(id="samples-container", style="margin-bottom: 1rem;"),
                Div(
                    Button("Generate More Samples", 
                           onclick="generateMoreSamples()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2",
                           style="margin-right: 0.5rem;"),
                    Button("Finalize Dataset", 
                           onclick="finalizeDataset()",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                    style="display: flex; gap: 0.5rem;"
                )
            ),
            id="step-3-card",
            style="display: none;"
        ),
        
        # Loading indicator
        Div(
            P("🤖 AI is thinking...", style="text-align: center; color: #6b7280;"),
            id="loading-indicator",
            style="display: none; margin: 1rem 0;"
        )
    ]
    
    # Add JavaScript for generator functionality
    content.append(Script("""
        let currentSession = null;
        let currentStep = 1;
        
        async function startConversation() {
            const promptSelect = document.getElementById('prompt-select');
            const selectedPrompt = promptSelect.value;
            
            showLoading();
            
            try {
                // Initialize generator session
                const response = await fetch('/datasets/generator/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: ''
                });
                
                const data = await response.json();
                
                if (data.success !== false) {
                    currentSession = data.session_id;
                    
                    // If prompt selected, analyze it first
                    if (selectedPrompt) {
                        await analyzePrompt(selectedPrompt);
                    }
                    
                    // Show conversation
                    showStep(2);
                    addMessage('ai', data.message);
                    
                } else {
                    alert('Error starting generator: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
            
            hideLoading();
        }
        
        async function analyzePrompt(promptId) {
            const formData = new FormData();
            formData.append('session_id', currentSession);
            formData.append('prompt_id', promptId);
            
            const response = await fetch('/datasets/generator/analyze-prompt', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.success && data.analysis) {
                addMessage('ai', 'I analyzed your prompt and pre-filled some requirements. ' + JSON.stringify(data.analysis.suggestions || []));
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage('user', message);
            input.value = '';
            showLoading();
            
            try {
                const formData = new FormData();
                formData.append('session_id', currentSession);
                formData.append('message', message);
                
                const response = await fetch('/datasets/generator/conversation', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success !== false) {
                    addMessage('ai', data.message);
                    
                    if (data.ready_for_generation) {
                        showGenerateSamplesButton();
                    }
                } else {
                    addMessage('ai', 'Error: ' + data.error);
                }
            } catch (error) {
                addMessage('ai', 'Error: ' + error.message);
            }
            
            hideLoading();
        }
        
        function addMessage(sender, message) {
            const conversationArea = document.getElementById('conversation-area');
            const messageDiv = document.createElement('div');
            messageDiv.style.marginBottom = '1rem';
            messageDiv.style.padding = '0.75rem';
            messageDiv.style.borderRadius = '0.5rem';
            
            if (sender === 'ai') {
                messageDiv.style.backgroundColor = '#f3f4f6';
                messageDiv.innerHTML = '<strong>AI:</strong> ' + message;
            } else {
                messageDiv.style.backgroundColor = '#dbeafe';
                messageDiv.innerHTML = '<strong>You:</strong> ' + message;
            }
            
            conversationArea.appendChild(messageDiv);
            conversationArea.scrollTop = conversationArea.scrollHeight;
        }
        
        function showGenerateSamplesButton() {
            const conversationArea = document.getElementById('conversation-area');
            const buttonDiv = document.createElement('div');
            buttonDiv.style.textAlign = 'center';
            buttonDiv.style.marginTop = '1rem';
            buttonDiv.innerHTML = '<button onclick="generateSamples()" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">Generate Sample Records</button>';
            conversationArea.appendChild(buttonDiv);
        }
        
        async function generateSamples() {
            showLoading();
            
            try {
                const formData = new FormData();
                formData.append('session_id', currentSession);
                
                const response = await fetch('/datasets/generator/generate-samples', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showStep(3);
                    displaySamples(data.samples);
                } else {
                    alert('Error generating samples: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
            
            hideLoading();
        }
        
        function displaySamples(samples) {
            const container = document.getElementById('samples-container');
            if (!container) return;
            
            container.innerHTML = '';
            
            samples.forEach((sample, index) => {
                const sampleDiv = document.createElement('div');
                sampleDiv.className = 'sample-item';
                sampleDiv.style.cssText = 'border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; background: white;';
                
                sampleDiv.innerHTML = `
                    <h4 style="margin: 0 0 0.5rem 0; color: #374151;">Sample ${index + 1}</h4>
                    <div style="margin-bottom: 0.5rem;">
                        <strong>Input:</strong> ${sample.input || 'N/A'}
                    </div>
                    <div>
                        <strong>Output:</strong> ${sample.output || sample.answer || 'N/A'}
                    </div>
                `;
                
                container.appendChild(sampleDiv);
            });
        }
        
        function showStep(stepNumber) {
            // Hide all steps
            for (let i = 1; i <= 6; i++) {
                const card = document.getElementById('step-' + i + '-card');
                const stepIndicator = document.getElementById('step-' + i);
                if (card) card.style.display = 'none';
                if (stepIndicator) stepIndicator.classList.remove('active');
            }
            
            // Show current step
            const currentCard = document.getElementById('step-' + stepNumber + '-card');
            const currentIndicator = document.getElementById('step-' + stepNumber);
            if (currentCard) currentCard.style.display = 'block';
            if (currentIndicator) currentIndicator.classList.add('active');
            
            currentStep = stepNumber;
        }
        
        function generateMoreSamples() {
            // TODO: Implement generate more samples
            alert('Generate more samples functionality coming soon!');
        }
        
        function finalizeDataset() {
            // TODO: Implement finalize dataset
            alert('Finalize dataset functionality coming soon!');
        }
        
        
        function showLoading() {
            document.getElementById('loading-indicator').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading-indicator').style.display = 'none';
        }
        
        // Allow Enter key to send message
        document.addEventListener('DOMContentLoaded', function() {
            const input = document.getElementById('user-input');
            if (input) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
        });
    """))
    
    # Add CSS for step indicator
    content.append(Style("""
        .step-indicator .step-number {
            width: 2rem;
            height: 2rem;
            border-radius: 50%;
            background: #e5e7eb;
            color: #6b7280;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
        }
        
        .step-indicator .step-number.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    """))
    
    return create_main_layout(
        "AI Dataset Generator",
        Div(*content),
        current_page="datasets",
        user=user.to_dict() if user else None
    )

if __name__ == "__main__":
    print("🚀 Starting Nova Prompt Optimizer...")
    
    # Run basic health checks
    try:
        from database import Database
        db_test = Database()
        metrics = db_test.get_metrics()
        datasets = db_test.get_datasets()
        
        if not metrics:
            print("⚠️ No metrics found in database - you can create them in the UI")
            
        if not datasets:
            print("⚠️ No datasets found in database - you can create them in the UI")
            print("💡 Run: python3 setup.py to fix this issue")
            sys.exit(1)
            
        print(f"✅ Database validated: {len(datasets)} datasets, {len(metrics)} metrics")
        
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        print("💡 Run: python3 setup.py to initialize the database")
        sys.exit(1)
    
    # Check required directories
    from pathlib import Path
    required_dirs = ['data', 'uploads', 'optimized_prompts']
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("📁 Starting Nova Prompt Optimizer server...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

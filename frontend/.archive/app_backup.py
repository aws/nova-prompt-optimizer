#!/usr/bin/env python3
"""
Nova Prompt Optimizer - FastHTML Frontend Application

A modern, real-time web interface for prompt optimization with advanced features:
- Prompt management with rich text editing
- Human annotation system with collaboration
- Interactive data visualizations
- Real-time multi-user support
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fasthtml.common import *
from fasthtml import FastHTML
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

# Import configuration and models
from config import get_settings
from models.database import init_database, get_db
from models.user import User, create_user_session

# Simple in-memory storage for datasets (in production, this would be a database)
uploaded_datasets = []

# Import existing components
from components.layout import create_main_layout, create_navigation
from components.navbar import create_navbar, create_navbar_styles
from components.ui import Button, Card, Textarea, Input, FormField, Badge, Alert, create_ui_styles

# Simple auth helper (TODO: move to utils/auth.py)
async def get_current_user(request):
    """Get current user from session"""
    user_id = request.session.get("user_id")
    if not user_id:
        # For now, create a default user for development
        # TODO: Implement proper authentication
        class DefaultUser:
            def __init__(self):
                self.id = 'dev-user'
                self.username = 'Developer'
            
            def to_dict(self):
                return {
                    'id': self.id,
                    'username': self.username
                }
        
        return DefaultUser()
    
    # Return user from session
    class SessionUser:
        def __init__(self, user_id, username):
            self.id = user_id
            self.username = username
        
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username
            }
    
    return SessionUser(user_id, request.session.get("username", "user"))

# TODO: Add these imports when modules are created
# from services.notification_service import NotificationManager
# from routes import dashboard, datasets, prompts, optimization, annotation, results, api
# from utils.auth import require_auth, get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize configuration
settings = get_settings()

# Custom CSS and JavaScript headers
app_headers = [
    # CSS Framework and custom styles
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'),
    Link(rel='stylesheet', href='/static/css/main.css'),
    Link(rel='stylesheet', href='/static/css/components.css'),
    
    # Monaco Editor for rich text editing
    Script(src='https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/loader.js'),
    
    # Chart.js for data visualizations
    Script(src='https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js'),
    
    # Custom JavaScript modules
    Script(src='/static/js/editors.js', type='module'),
    Script(src='/static/js/charts.js', type='module'),
    Script(src='/static/js/collaboration.js', type='module'),
    
    # Favicon
    Link(rel='icon', type='image/svg+xml', href='/static/assets/favicon.svg'),
    
    # Meta tags
    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
    Meta(name='description', content='Nova Prompt Optimizer - Advanced AI Prompt Engineering Platform'),
]

# Initialize FastHTML app
app = FastHTML(
    debug=settings.DEBUG,
    hdrs=app_headers,
    static_path='static',
    secret_key=settings.SECRET_KEY
)

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=settings.SESSION_MAX_AGE
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize notification manager for real-time features (TODO: implement)
# notification_manager = NotificationManager()

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    logger.info("Starting Nova Prompt Optimizer Frontend...")
    
    # Initialize database
    await init_database()
    logger.info("Database initialized")
    
    # TODO: Start notification manager when implemented
    # await notification_manager.start()
    # logger.info("Notification manager started")
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Nova Prompt Optimizer Frontend...")
    
    # TODO: Stop notification manager when implemented
    # await notification_manager.stop()
    # logger.info("Notification manager stopped")
    
    logger.info("Application shutdown complete")

# Root route - Dashboard
@app.get("/")
async def index(request):
    """Main dashboard page"""
    user = await get_current_user(request)
    # Removed authentication check for development
    # if not user:
    #     return RedirectResponse(url="/auth/login")
    
    # Enhanced dashboard with UI components
    return create_main_layout(
        "Dashboard",
        Div(
            # Welcome Section
            Div(
                H1("Nova Prompt Optimizer", style="margin-bottom: 0.5rem; font-size: 2rem; font-weight: 700;"),
                P(f"Welcome back, {user.username if user else 'User'}!", 
                  style="color: #6b7280; margin-bottom: 2rem;"),
                cls="welcome-section"
            ),
            
            # Stats Overview
            Div(
                Card(
                    content=Div(
                        H3(str(len(uploaded_datasets)), style="font-size: 2rem; margin: 0; color: #667eea;"),
                        P("Datasets", style="margin: 0; color: #6b7280; font-weight: 500;"),
                        style="text-align: center;"
                    )
                ),
                Card(
                    content=Div(
                        H3("0", style="font-size: 2rem; margin: 0; color: #10b981;"),
                        P("Prompts", style="margin: 0; color: #6b7280; font-weight: 500;"),
                        style="text-align: center;"
                    )
                ),
                Card(
                    content=Div(
                        H3("0", style="font-size: 2rem; margin: 0; color: #f59e0b;"),
                        P("Optimizations", style="margin: 0; color: #6b7280; font-weight: 500;"),
                        style="text-align: center;"
                    )
                ),
                style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;"
            ),
            
            # Quick Actions Section
            Card(
                header=H3("Quick Actions"),
                content=Div(
                    Div(
                        Button("New Prompt", variant="primary", href="/prompts/new"),
                        Button("Upload Dataset", variant="secondary", href="/datasets/upload"),
                        Button("Start Optimization", variant="outline", href="/optimization/new"),
                        style="display: flex; gap: 1rem; flex-wrap: wrap;"
                    ),
                    style="margin-bottom: 1rem;"
                )
            ),
            
            # Prompt Input Section
            Card(
                header=H3("Quick Prompt Test"),
                content=Div(
                    FormField(
                        "System Prompt",
                        Textarea(
                            placeholder="Enter your system prompt here...",
                            rows=3,
                            name="system_prompt"
                        ),
                        help_text="Define the AI assistant's role and behavior"
                    ),
                    FormField(
                        "User Prompt",
                        Textarea(
                            placeholder="Enter your user prompt here...",
                            rows=4,
                            name="user_prompt"
                        ),
                        help_text="The actual prompt you want to optimize"
                    ),
                    Div(
                        Button("Test Prompt", variant="primary"),
                        Button("Save Draft", variant="ghost"),
                        style="display: flex; gap: 0.5rem;"
                    )
                )
            ),
            
            # System Status Section
            Div(
                Card(
                    header=H3("System Status"),
                    content=Div(
                        Div(
                            Badge("✓ Application Running", variant="success"),
                            Badge("✓ Database Connected", variant="success"),
                            Badge("✓ AWS Configured", variant="success"),
                            style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;"
                        ),
                        Alert(
                            "All systems are operational. Ready for prompt optimization.",
                            variant="success",
                            title="System Healthy"
                        )
                    )
                ),
                
                Card(
                    header=H3("Recent Activity"),
                    content=Div(
                        P("No recent activity", style="color: #6b7280; font-style: italic;"),
                        Button("View All Activity", variant="outline", size="sm")
                    )
                ),
                
                style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;"
            ),
            
            # Getting Started Section
            Card(
                header=H3("Getting Started"),
                content=Div(
                    P("New to Nova Prompt Optimizer? Here's how to get started:", 
                      style="margin-bottom: 1rem;"),
                    Ol(
                        Li("Upload or create a dataset for evaluation"),
                        Li("Create a prompt template with variables"),
                        Li("Configure optimization parameters"),
                        Li("Run optimization and review results"),
                        style="margin-left: 1.5rem; line-height: 1.6;"
                    ),
                    Div(
                        Button("View Documentation", variant="outline"),
                        Button("Watch Tutorial", variant="ghost"),
                        style="display: flex; gap: 0.5rem; margin-top: 1rem;"
                    )
                )
            ),
            
            style="max-width: 1200px; margin: 0 auto; padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem;"
        ),
        current_page="dashboard",
        user=user.to_dict() if user else None
    )

# Authentication routes
@app.get("/auth/login")
async def login_page(request):
    """Login page"""
    return create_main_layout(
        "Login - Nova Prompt Optimizer",
        Div(
            Card(
                H2("Welcome to Nova Prompt Optimizer"),
                P("Please sign in to continue"),
                Form(
                    Input(type="text", name="username", placeholder="Username", required=True),
                    Input(type="password", name="password", placeholder="Password", required=True),
                    Button("Sign In", type="submit", cls="primary"),
                    action="/auth/login",
                    method="post",
                    hx_post="/auth/login",
                    hx_target="#main-content"
                ),
                cls="login-card"
            ),
            cls="login-container"
        )
    )

@app.post("/auth/login")
async def login_submit(request):
    """Handle login submission"""
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    # Simple authentication (replace with proper auth)
    if username and password:
        user = await create_user_session(request, username)
        return RedirectResponse(url="/", status_code=303)
    
    return Div(
        P("Invalid credentials", cls="error"),
        hx_swap_oob="true",
        id="error-message"
    )

@app.get("/auth/logout")
async def logout(request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse(url="/auth/login")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nova-prompt-optimizer-frontend"}

# Favicon route to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon response"""
    from starlette.responses import Response
    # Return a simple 1x1 transparent PNG as favicon
    favicon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(favicon_data, media_type="image/png")

# Handle Chrome DevTools and other well-known requests
@app.get("/.well-known/{path:path}")
async def well_known_handler(path: str):
    """Handle .well-known requests from Chrome DevTools"""
    from starlette.responses import JSONResponse
    return JSONResponse({"error": "Not found"}, status_code=404)

# TODO: Implement WebSocket and SSE endpoints
# WebSocket endpoint for real-time collaboration
# @app.websocket("/ws/{room_id}")
# async def websocket_endpoint(websocket, room_id: str):
#     """WebSocket endpoint for real-time collaboration"""
#     await notification_manager.handle_websocket(websocket, room_id)

# Server-Sent Events for real-time updates
# @app.get("/events/{channel}")
# async def sse_endpoint(request, channel: str):
#     """Server-Sent Events endpoint for real-time updates"""
#     return await notification_manager.handle_sse(request, channel)

# TODO: Include route modules when they're converted to FastHTML
# app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# TODO: Include these routes when modules are created
# app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
# app.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
# app.include_router(optimization.router, prefix="/optimization", tags=["optimization"])
# app.include_router(annotation.router, prefix="/annotation", tags=["annotation"])
# app.include_router(results.router, prefix="/results", tags=["results"])
# app.include_router(api.router, prefix="/api", tags=["api"])

# Authentication routes (placeholder)
@app.get("/auth/login")
async def login_page(request):
    """Login page"""
    return create_main_layout(
        "Login",
        Div(
            Div(
                H1("Sign In", style="text-align: center; margin-bottom: 0.5rem;"),
                P("Welcome to Nova Prompt Optimizer", 
                  style="text-align: center; color: #6b7280; margin-bottom: 2rem;"),
                
                Card(
                    content=Form(
                        FormField(
                            "Username",
                            Input(placeholder="Enter your username", name="username", required=True)
                        ),
                        FormField(
                            "Password",
                            Input(type="password", placeholder="Enter your password", 
                                name="password", required=True)
                        ),
                        Div(
                            Button("Sign In", variant="primary", type="submit", 
                                 style="width: 100%;"),
                            style="margin-top: 0.5rem;"
                        ),
                        method="post",
                        action="/auth/login"
                    )
                ),
                
                Div(
                    P("Don't have an account? ", 
                      A("Contact your administrator", href="#", style="color: #000000;")),
                    style="text-align: center; margin-top: 1rem; font-size: 0.875rem; color: #6b7280;"
                ),
                
                style="max-width: 400px; margin: 0 auto;"
            ),
            style="min-height: 60vh; display: flex; align-items: center; padding: 2rem;"
        ),
        current_page="login",
        show_sidebar=False  # Hide sidebar on login page
    )

@app.post("/auth/login")
async def login_submit(request):
    """Handle login submission"""
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")
    
    # Simple authentication for development
    # TODO: Implement proper authentication with database
    if username and password:  # Accept any non-empty username/password
        request.session["user_id"] = f"user-{username}"
        request.session["username"] = username
        return RedirectResponse(url="/", status_code=302)
    else:
        # Return to login with error
        return create_main_layout(
            "Login",
            Div(
                Div(
                    H1("Sign In", style="text-align: center; margin-bottom: 0.5rem;"),
                    P("Welcome to Nova Prompt Optimizer", 
                      style="text-align: center; color: #6b7280; margin-bottom: 2rem;"),
                    
                    Alert(
                        "Please enter both username and password.",
                        variant="error",
                        title="Login Failed"
                    ),
                    
                    Card(
                        content=Form(
                            FormField(
                                "Username",
                                Input(placeholder="Enter your username", name="username", required=True)
                            ),
                            FormField(
                                "Password",
                                Input(type="password", placeholder="Enter your password", 
                                    name="password", required=True)
                            ),
                            Div(
                                Button("Sign In", variant="primary", type="submit", 
                                     style="width: 100%;"),
                                style="margin-top: 0.5rem;"
                            ),
                            method="post",
                            action="/auth/login"
                        )
                    ),
                    
                    Div(
                        P("For development: Use any username and password", 
                          style="text-align: center; font-size: 0.875rem; color: #6b7280;"),
                        style="text-align: center; margin-top: 1rem;"
                    ),
                    
                    style="max-width: 400px; margin: 0 auto;"
                ),
                style="min-height: 60vh; display: flex; align-items: center; padding: 2rem;"
            ),
            current_page="login",
            show_sidebar=False
        )

@app.get("/auth/logout")
async def logout(request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)

# API endpoint to get datasets count
@app.get("/api/datasets/count")
async def get_datasets_count():
    """Get count of uploaded datasets"""
    return {"count": len(uploaded_datasets)}

# Dataset routes (placeholder)
@app.get("/datasets")
async def datasets_page(request):
    """Datasets main page"""
    user = await get_current_user(request)
    return Html(
        Head(
            Title("Datasets - Nova Prompt Optimizer"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
            create_navbar_styles(),
            create_ui_styles()
        ),
        Body(
            create_navbar("datasets", user.to_dict() if user else None),
            
            Main(
                Div(
                    H1("Datasets", style="margin-bottom: 1rem;"),
                    P("Manage your training and evaluation datasets", 
                      style="color: #6b7280; margin-bottom: 2rem;"),
                    
                    Card(
                        header=H3("Upload New Dataset"),
                        content=Div(
                            P("Upload your training or evaluation datasets to get started with prompt optimization.", 
                              style="color: #6b7280; margin-bottom: 1rem;"),
                            Div(
                                Button("Upload Dataset", variant="primary", 
                                       onclick="openUploadModal()",
                                       style="margin-right: 0.5rem;"),
                                Button("Browse Examples", variant="outline"),
                                style="display: flex; gap: 0.5rem;"
                            )
                        )
                    ),
                    
                    Card(
                        header=H3("Recent Datasets"),
                        content=Div(
                            # Show uploaded datasets if any exist
                            *([
                                Div(
                                    Div(
                                        H4(dataset["name"], style="margin: 0 0 0.5rem 0; color: #1f2937;"),
                                        P(f"File: {dataset['filename']}", style="margin: 0; color: #6b7280; font-size: 0.875rem;"),
                                        P(f"Size: {dataset['size']} bytes", style="margin: 0; color: #6b7280; font-size: 0.875rem;"),
                                        P(f"Uploaded: {dataset['uploaded_at']}", style="margin: 0; color: #6b7280; font-size: 0.875rem;"),
                                        P(dataset["description"], style="margin: 0.5rem 0 0 0; color: #4b5563; font-size: 0.875rem;"),
                                        style="flex: 1;"
                                    ),
                                    Div(
                                        Badge(dataset["status"], variant="success"),
                                        Div(
                                            Button("View", variant="outline", size="sm", style="margin-right: 0.5rem;"),
                                            Button("Delete", variant="ghost", size="sm", style="color: #dc2626;"),
                                            style="margin-top: 0.5rem;"
                                        ),
                                        style="text-align: right;"
                                    ),
                                    style="display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 0.5rem;"
                                ) for dataset in uploaded_datasets
                            ] if uploaded_datasets else [
                                P("No datasets uploaded yet", style="color: #6b7280; font-style: italic;")
                            ]),
                            Button("Browse Examples", variant="outline", size="sm") if not uploaded_datasets else None
                        )
                    ),
                    
                    style="max-width: 800px; margin: 0 auto; padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem;"
                )
            ),
            
            # Upload Modal
            Div(
                Div(
                    Div(
                        # Modal Header
                        Div(
                            H3("Upload Dataset", style="margin: 0; color: #1f2937;"),
                            Button("×", onclick="closeUploadModal()", 
                                   style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280;"),
                            style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid #e5e7eb;"
                        ),
                        
                        # Modal Content (iframe to load upload form)
                        Div(
                            Iframe(src="/datasets/upload/modal", 
                                   style="width: 100%; height: 400px; border: none;",
                                   id="upload-iframe"),
                            style="padding: 0;"
                        ),
                        
                        style="background: white; border-radius: 8px; max-width: 600px; width: 90vw; max-height: 90vh; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);"
                    ),
                    style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: none; align-items: center; justify-content: center; z-index: 1000;",
                    id="upload-modal",
                    onclick="event.target === this && closeUploadModal()"
                )
            ),
            
            # Modal JavaScript
            Script("""
                function openUploadModal() {
                    console.log('Opening upload modal');
                    document.getElementById('upload-modal').style.display = 'flex';
                    // Reload iframe to ensure fresh form
                    document.getElementById('upload-iframe').src = '/datasets/upload/modal';
                }
                
                function closeUploadModal() {
                    console.log('Closing upload modal');
                    document.getElementById('upload-modal').style.display = 'none';
                }
                
                // Listen for successful upload from iframe
                window.addEventListener('message', function(event) {
                    if (event.data === 'upload-success') {
                        closeUploadModal();
                        // Optionally reload the page to show new dataset
                        location.reload();
                    }
                });
                
                // Close modal on Escape key
                document.addEventListener('keydown', function(event) {
                    if (event.key === 'Escape') {
                        closeUploadModal();
                    }
                });
            """)
        )
    )

@app.get("/datasets/upload/modal")
async def dataset_upload_modal(request):
    """Dataset upload form for modal (no navigation)"""
    return Html(
        Head(
            Title("Upload Dataset"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
            create_ui_styles()
        ),
        Body(
            Div(
                Alert(
                    "Upload your training or evaluation dataset to get started with prompt optimization.",
                    variant="info",
                    title="Dataset Upload"
                ),
                
                Card(
                    content=Form(
                        FormField(
                            "Dataset File",
                            Input(type="file", accept=".csv,.json,.jsonl", name="dataset", required=True),
                            help_text="Supported formats: CSV, JSON, JSONL (max 10MB)"
                        ),
                        FormField(
                            "Dataset Name",
                            Input(placeholder="My Training Dataset", name="name", required=True)
                        ),
                        FormField(
                            "Description",
                            Textarea(placeholder="Describe your dataset purpose and content...", 
                                   rows=3, name="description")
                        ),
                        Div(
                            Input(type="submit", value="Upload Dataset", 
                                  style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"),
                            style="display: flex; gap: 0.5rem;"
                        ),
                        method="post",
                        action="/datasets/upload",
                        enctype="multipart/form-data",
                        id="upload-form"
                    )
                ),
                
                style="padding: 1.5rem;"
            ),
            
            # Script to notify parent window on success
            Script("""
                document.addEventListener('DOMContentLoaded', function() {
                    const form = document.getElementById('upload-form');
                    if (form) {
                        form.addEventListener('submit', function(e) {
                            console.log('Form submitted in modal');
                            // After successful submission, notify parent window
                            setTimeout(function() {
                                if (window.parent && window.parent !== window) {
                                    window.parent.postMessage('upload-success', '*');
                                }
                            }, 1000);
                        });
                    }
                });
            """)
        )
    )
@app.get("/datasets/upload")
async def dataset_upload_page(request):
    """Dataset upload page (full page version)"""
    user = await get_current_user(request)
    return create_main_layout(
        "Upload Dataset",
        Div(
            H1("Upload Dataset", style="margin-bottom: 1rem;"),
            
            Alert(
                "Upload your training or evaluation dataset to get started with prompt optimization.",
                variant="info",
                title="Dataset Upload"
            ),
            
            Card(
                content=Form(
                    FormField(
                        "Dataset File",
                        Input(type="file", accept=".csv,.json,.jsonl", name="dataset", required=True),
                        help_text="Supported formats: CSV, JSON, JSONL (max 10MB)"
                    ),
                    FormField(
                        "Dataset Name",
                        Input(placeholder="My Training Dataset", name="name", required=True)
                    ),
                    FormField(
                        "Description",
                        Textarea(placeholder="Describe your dataset purpose and content...", 
                               rows=3, name="description")
                    ),
                    Div(
                        Input(type="submit", value="Upload Dataset", 
                              style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"),
                        A("Back to Datasets", href="/datasets", 
                          style="padding: 0.5rem 1rem; text-decoration: none; color: #666; border: 1px solid #ddd; border-radius: 0.375rem;"),
                        style="display: flex; gap: 0.5rem;"
                    ),
                    method="post",
                    action="/datasets/upload",
                    enctype="multipart/form-data",
                    id="upload-form"
                )
            ),
            
            style="max-width: 600px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="datasets",
        user=user.to_dict() if user else None
    )

@app.post("/datasets/upload")
async def dataset_upload_submit(request):
    """Handle dataset upload submission"""
    print("🔍 DEBUG: POST /datasets/upload route hit!")
    
    try:
        form = await request.form()
        print(f"🔍 DEBUG: Form data received: {dict(form)}")
        
        # Get form data (removed input_column and output_column)
        dataset_file = form.get("dataset")
        name = form.get("name", "")
        description = form.get("description", "")
        
        print(f"🔍 DEBUG: Parsed data - name: {name}, description: {description}")
        print(f"🔍 DEBUG: File: {dataset_file}")
        
    except Exception as e:
        print(f"❌ DEBUG: Error processing form: {e}")
        raise
    
    # Simple validation (only file and name required now)
    if not dataset_file or not name:
        # Check if this is from modal (referer contains modal)
        referer = request.headers.get("referer", "")
        is_modal_request = "modal" in referer or request.headers.get("sec-fetch-dest") == "iframe"
        
        if is_modal_request:
            return Html(
                Head(
                    Title("Upload Error"),
                    Meta(charset="utf-8"),
                    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
                    create_ui_styles()
                ),
                Body(
                    Div(
                        Alert(
                            "Please provide both a dataset file and name.",
                            variant="error",
                            title="Validation Error"
                        ),
                        Button("Try Again", onclick="window.location.reload()", 
                               style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                        style="padding: 1.5rem;"
                    )
                )
            )
        
        # Full page error response for non-modal requests
        user = await get_current_user(request)
        return create_main_layout(
            "Upload Dataset",
            Div(
                H1("Upload Dataset", style="margin-bottom: 1rem;"),
                
                Alert(
                    "Please provide both a dataset file and name.",
                    variant="error",
                    title="Validation Error"
                ),
                
                Card(
                    content=Form(
                        FormField(
                            "Dataset File",
                            Input(type="file", accept=".csv,.json,.jsonl", name="dataset", required=True),
                            help_text="Supported formats: CSV, JSON, JSONL (max 10MB)"
                        ),
                        FormField(
                            "Dataset Name",
                            Input(placeholder="My Training Dataset", name="name", 
                                value=name, required=True)
                        ),
                        FormField(
                            "Description",
                            Textarea(placeholder="Describe your dataset purpose and content...", 
                                   rows=3, name="description", value=description)
                        ),
                        Div(
                            Button("Upload Dataset", variant="primary", type="submit"),
                            Button("Back to Datasets", variant="ghost", href="/datasets"),
                            style="display: flex; gap: 0.5rem;"
                        ),
                        method="post",
                        action="/datasets/upload",
                        enctype="multipart/form-data"
                    )
                ),
                
                style="max-width: 600px; margin: 0 auto; padding: 2rem;"
            ),
            current_page="datasets",
            user=user.to_dict() if user else None
        )
    
    # Get file info (in real app, you'd save the file and process it)
    file_info = {
        "filename": dataset_file.filename if hasattr(dataset_file, 'filename') else "unknown",
        "size": len(await dataset_file.read()) if hasattr(dataset_file, 'read') else 0
    }
    
    # Save dataset info to our in-memory storage
    from datetime import datetime
    dataset_info = {
        "id": len(uploaded_datasets) + 1,
        "name": name,
        "filename": file_info["filename"],
        "size": file_info["size"],
        "description": description or "No description provided",
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Ready"
    }
    uploaded_datasets.append(dataset_info)
    print(f"🔍 DEBUG: Saved dataset: {dataset_info}")
    
    # Check if this is from modal
    referer = request.headers.get("referer", "")
    is_modal_request = "modal" in referer or request.headers.get("sec-fetch-dest") == "iframe"
    
    if is_modal_request:
        # Return modal-friendly success response
        return Html(
            Head(
                Title("Upload Success"),
                Meta(charset="utf-8"),
                Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
                create_ui_styles()
            ),
            Body(
                Div(
                    Alert(
                        f"Your dataset '{name}' has been uploaded successfully!",
                        variant="success",
                        title="Upload Complete"
                    ),
                    
                    Card(
                        header=H4("Dataset Details"),
                        content=Div(
                            P(Strong("Name: "), name),
                            P(Strong("File: "), file_info["filename"]),
                            P(Strong("Size: "), f"{file_info['size']} bytes"),
                            P(Strong("Description: "), description or "None provided"),
                        )
                    ),
                    
                    Div(
                        Button("Close", onclick="if(window.parent) window.parent.postMessage('upload-success', '*');", 
                               style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; margin-right: 0.5rem;"),
                        Button("Upload Another", onclick="window.location.href='/datasets/upload/modal'", 
                               style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                        style="margin-top: 1rem;"
                    ),
                    
                    style="padding: 1.5rem;"
                ),
                
                # Auto-close modal after 3 seconds
                Script("""
                    setTimeout(function() {
                        if (window.parent && window.parent !== window) {
                            window.parent.postMessage('upload-success', '*');
                        }
                    }, 3000);
                """)
            )
        )
    
    # Full page success response for non-modal requests
    user = await get_current_user(request)
    return create_main_layout(
            "Upload Dataset",
            Div(
                H1("Upload Dataset", style="margin-bottom: 1rem;"),
                
                Alert(
                    "Please provide all required fields: dataset file, name, input column, and output column.",
                    variant="error",
                    title="Validation Error"
                ),
                
                Card(
                    content=Form(
                        FormField(
                            "Dataset File",
                            Input(type="file", accept=".csv,.json,.jsonl", name="dataset", required=True),
                            help_text="Supported formats: CSV, JSON, JSONL (max 10MB)"
                        ),
                        FormField(
                            "Dataset Name",
                            Input(placeholder="My Training Dataset", name="name", 
                                value=name, required=True)
                        ),
                        FormField(
                            "Input Column",
                            Input(placeholder="input", name="input_column", 
                                value=input_column, required=True),
                            help_text="Column name containing input data"
                        ),
                        FormField(
                            "Output Column",
                            Input(placeholder="output", name="output_column", 
                                value=output_column, required=True),
                            help_text="Column name containing expected output"
                        ),
                        FormField(
                            "Description",
                            Textarea(placeholder="Describe your dataset purpose and content...", 
                                   rows=3, name="description", value=description)
                        ),
                        Div(
                            Button("Upload Dataset", variant="primary", type="submit"),
                            Button("Back to Datasets", variant="ghost", href="/datasets"),
                            style="display: flex; gap: 0.5rem;"
                        ),
                        method="post",
                        action="/datasets/upload",
                        enctype="multipart/form-data"
                    )
                ),
                
                style="max-width: 600px; margin: 0 auto; padding: 2rem;"
            ),
            current_page="datasets",
            user=user.to_dict() if user else None
        )
    
    # Get file info (in real app, you'd save the file and process it)
    file_info = {
        "filename": dataset_file.filename if hasattr(dataset_file, 'filename') else "unknown",
        "size": len(await dataset_file.read()) if hasattr(dataset_file, 'read') else 0
    }
    
    # Save dataset info to our in-memory storage
    from datetime import datetime
    dataset_info = {
        "id": len(uploaded_datasets) + 1,
        "name": name,
        "filename": file_info["filename"],
        "size": file_info["size"],
        "description": description or "No description provided",
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Ready"
    }
    uploaded_datasets.append(dataset_info)
    print(f"🔍 DEBUG: Saved dataset: {dataset_info}")
    
    # TODO: Process and save the actual file
    # For now, just show success message
    user = await get_current_user(request)
    return create_main_layout(
        "Dataset Uploaded",
        Div(
            H1("Dataset Uploaded Successfully!", style="margin-bottom: 1rem;"),
            
            Alert(
                f"Your dataset '{name}' has been uploaded and is ready for use.",
                variant="success",
                title="Upload Complete"
            ),
            
            Card(
                header=H3("Dataset Details"),
                content=Div(
                    P(Strong("Name: "), name),
                    P(Strong("File: "), file_info["filename"]),
                    P(Strong("Size: "), f"{file_info['size']} bytes"),
                    P(Strong("Description: "), description or "None provided"),
                    Div(
                        Button("Upload Another", variant="primary", href="/datasets/upload"),
                        Button("View All Datasets", variant="secondary", href="/datasets"),
                        Button("Start Optimization", variant="outline", href="/optimization/new"),
                        style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;"
                    )
                )
            ),
            
            style="max-width: 600px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="datasets",
        user=user.to_dict() if user else None
    )

# Prompts routes (placeholder)
@app.get("/prompts")
async def prompts_page(request):
    """Prompts main page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Prompts",
        Div(
            H1("📝 Prompts"),
            P("Create and manage your prompt templates"),
            A("New Prompt", href="/prompts/new", cls="button primary"),
            A("Browse Prompts", href="/prompts/browse", cls="button secondary")
        ),
        current_page="prompts",
        user=user.to_dict() if user else None
    )

@app.get("/prompts/new")
async def prompts_new_page(request):
    """New prompt creation page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Create New Prompt",
        Div(
            H1("Create New Prompt", style="margin-bottom: 1rem;"),
            
            Alert(
                "Create a new prompt template with variables for optimization.",
                variant="info",
                title="Prompt Creation"
            ),
            
            Card(
                content=Form(
                    FormField(
                        "Prompt Name",
                        Input(placeholder="My Optimization Prompt", name="name", required=True)
                    ),
                    FormField(
                        "System Prompt",
                        Textarea(placeholder="You are a helpful AI assistant...", 
                               rows=4, name="system_prompt"),
                        help_text="Optional system-level instructions"
                    ),
                    FormField(
                        "User Prompt Template",
                        Textarea(placeholder="Please analyze: {{input}}", 
                               rows=6, name="user_prompt", required=True),
                        help_text="Use {{variable}} syntax for template variables"
                    ),
                    Div(
                        Button("Create Prompt", variant="primary", type="submit"),
                        Button("Back to Prompts", variant="ghost", href="/prompts"),
                        style="display: flex; gap: 0.5rem;"
                    ),
                    method="post",
                    action="/prompts/create"
                )
            ),
            
            style="max-width: 600px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="prompts",
        user=user.to_dict() if user else None
    )

@app.post("/prompts/create")
async def prompts_create(request):
    """Handle prompt creation"""
    form = await request.form()
    name = form.get("name", "")
    system_prompt = form.get("system_prompt", "")
    user_prompt = form.get("user_prompt", "")
    
    # Simple validation
    if not name or not user_prompt:
        user = await get_current_user(request)
        return create_main_layout(
            "Create New Prompt",
            Div(
                H1("Create New Prompt", style="margin-bottom: 1rem;"),
                
                Alert(
                    "Please provide both a prompt name and user prompt template.",
                    variant="error",
                    title="Validation Error"
                ),
                
                Card(
                    content=Form(
                        FormField(
                            "Prompt Name",
                            Input(placeholder="My Optimization Prompt", name="name", 
                                value=name, required=True)
                        ),
                        FormField(
                            "System Prompt",
                            Textarea(placeholder="You are a helpful AI assistant...", 
                                   rows=4, name="system_prompt", value=system_prompt),
                            help_text="Optional system-level instructions"
                        ),
                        FormField(
                            "User Prompt Template",
                            Textarea(placeholder="Please analyze: {{input}}", 
                                   rows=6, name="user_prompt", value=user_prompt, required=True),
                            help_text="Use {{variable}} syntax for template variables"
                        ),
                        Div(
                            Button("Create Prompt", variant="primary", type="submit"),
                            Button("Back to Prompts", variant="ghost", href="/prompts"),
                            style="display: flex; gap: 0.5rem;"
                        ),
                        method="post",
                        action="/prompts/create"
                    )
                ),
                
                style="max-width: 600px; margin: 0 auto; padding: 2rem;"
            ),
            current_page="prompts",
            user=user.to_dict() if user else None
        )
    
    # TODO: Save to database
    # For now, just show success message
    user = await get_current_user(request)
    return create_main_layout(
        "Prompt Created",
        Div(
            H1("Prompt Created Successfully!", style="margin-bottom: 1rem;"),
            
            Alert(
                f"Your prompt '{name}' has been created successfully.",
                variant="success",
                title="Success"
            ),
            
            Card(
                header=H3("Prompt Details"),
                content=Div(
                    P(Strong("Name: "), name),
                    P(Strong("System Prompt: "), system_prompt or "None"),
                    P(Strong("User Prompt: "), user_prompt),
                    Div(
                        Button("Create Another", variant="primary", href="/prompts/new"),
                        Button("View All Prompts", variant="secondary", href="/prompts"),
                        style="display: flex; gap: 0.5rem; margin-top: 1rem;"
                    )
                )
            ),
            
            style="max-width: 600px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="prompts",
        user=user.to_dict() if user else None
    )

@app.get("/prompts/browse")
async def prompts_browse_page(request):
    """Browse existing prompts page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Browse Prompts",
        Div(
            H1("Browse Prompts", style="margin-bottom: 1rem;"),
            P("View and manage your existing prompt templates", 
              style="color: #6b7280; margin-bottom: 2rem;"),
            
            # Search and filter section
            Card(
                header=H3("Search & Filter"),
                content=Div(
                    Div(
                        Input(placeholder="Search prompts...", name="search"),
                        Button("Search", variant="outline"),
                        style="display: flex; gap: 0.5rem; margin-bottom: 1rem;"
                    ),
                    Div(
                        Button("All", variant="ghost", size="sm"),
                        Button("Recent", variant="ghost", size="sm"),
                        Button("Favorites", variant="ghost", size="sm"),
                        style="display: flex; gap: 0.5rem;"
                    )
                )
            ),
            
            # Prompts list
            Card(
                header=H3("Your Prompts"),
                content=Div(
                    # Sample prompt entries (in real app, these would come from database)
                    Div(
                        Div(
                            H4("Sample Analysis Prompt", style="margin: 0 0 0.5rem 0;"),
                            P("Analyze the following text: {{input}}", 
                              style="color: #6b7280; font-size: 0.875rem; margin: 0 0 0.5rem 0;"),
                            Div(
                                Badge("analysis", variant="default"),
                                Badge("text-processing", variant="default"),
                                style="display: flex; gap: 0.25rem; margin-bottom: 0.5rem;"
                            ),
                            Div(
                                Button("Edit", variant="outline", size="sm"),
                                Button("Use", variant="primary", size="sm"),
                                Button("Delete", variant="ghost", size="sm"),
                                style="display: flex; gap: 0.25rem;"
                            ),
                            style="padding: 1rem; border: 1px solid #e5e5e5; border-radius: 6px; margin-bottom: 1rem;"
                        ),
                        
                        Div(
                            H4("Customer Support Template", style="margin: 0 0 0.5rem 0;"),
                            P("You are a helpful customer support agent. Please respond to: {{query}}", 
                              style="color: #6b7280; font-size: 0.875rem; margin: 0 0 0.5rem 0;"),
                            Div(
                                Badge("support", variant="default"),
                                Badge("customer-service", variant="default"),
                                style="display: flex; gap: 0.25rem; margin-bottom: 0.5rem;"
                            ),
                            Div(
                                Button("Edit", variant="outline", size="sm"),
                                Button("Use", variant="primary", size="sm"),
                                Button("Delete", variant="ghost", size="sm"),
                                style="display: flex; gap: 0.25rem;"
                            ),
                            style="padding: 1rem; border: 1px solid #e5e5e5; border-radius: 6px; margin-bottom: 1rem;"
                        ),
                        
                        # Empty state for when no prompts exist
                        Div(
                            P("No prompts found matching your criteria.", 
                              style="color: #6b7280; font-style: italic; text-align: center; margin: 2rem 0;"),
                            Button("Create Your First Prompt", variant="primary", href="/prompts/new"),
                            style="text-align: center; display: none;"  # Hidden by default, show when no results
                        )
                    )
                )
            ),
            
            # Pagination (placeholder)
            Div(
                Button("Previous", variant="outline", disabled=True),
                Span("Page 1 of 1", style="margin: 0 1rem; color: #6b7280;"),
                Button("Next", variant="outline", disabled=True),
                style="display: flex; align-items: center; justify-content: center; margin-top: 1rem;"
            ),
            
            style="max-width: 800px; margin: 0 auto; padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem;"
        ),
        current_page="prompts",
        user=user.to_dict() if user else None
    )

@app.get("/optimization/recent")
async def optimization_recent_page(request):
    """Recent optimizations page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Recent Optimizations",
        Div(
            H1("Recent Optimizations", style="margin-bottom: 1rem;"),
            P("View your recent optimization runs", 
              style="color: #6b7280; margin-bottom: 2rem;"),
            
            Card(
                header=H3("Recent Runs"),
                content=Div(
                    P("No optimization runs yet", style="color: #6b7280; font-style: italic;"),
                    Button("Start New Optimization", variant="primary", href="/optimization/new")
                )
            ),
            
            style="max-width: 800px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="optimization",
        user=user.to_dict() if user else None
    )

# Optimization routes (placeholder)
@app.get("/optimization")
async def optimization_page(request):
    """Optimization main page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Optimization",
        Div(
            H1("🚀 Optimization"),
            P("Run prompt optimization workflows"),
            A("New Optimization", href="/optimization/new", cls="button primary"),
            A("View History", href="/optimization/history", cls="button secondary")
        ),
        current_page="optimization",
        user=user.to_dict() if user else None
    )

@app.get("/optimization/new")
async def optimization_new_page(request):
    """New optimization page"""
    user = await get_current_user(request)
    return create_main_layout(
        "New Optimization",
        Div(
            H1("🚀 New Optimization"),
            P("Start a new prompt optimization workflow"),
            A("Back to Optimization", href="/optimization", cls="button secondary")
        ),
        current_page="optimization",
        user=user.to_dict() if user else None
    )

# Results routes (placeholder)
@app.get("/results")
async def results_page(request):
    """Results main page"""
    user = await get_current_user(request)
    return create_main_layout(
        "Results",
        Div(
            H1("📈 Results"),
            P("View optimization results and analytics"),
            A("Latest Results", href="/results/latest", cls="button primary"),
            A("Compare Results", href="/results/compare", cls="button secondary")
        ),
        current_page="results",
        user=user.to_dict() if user else None
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 page"""
    return Html(
        Head(Title("404 - Page Not Found")),
        Body(
            H1("404 - Page Not Found"),
            P("The page you're looking for doesn't exist."),
            A("Go to Dashboard", href="/", style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;"),
            style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;"
        )
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Custom 500 page"""
    logger.error(f"Server error: {exc}")
    return Html(
        Head(Title("500 - Server Error")),
        Body(
            H1("500 - Server Error"),
            P("Something went wrong. Please try again later."),
            A("Go to Dashboard", href="/", style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;"),
            style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;"
        )
    )

# Development server
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Prompt Optimizer Frontend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level="info"
    )

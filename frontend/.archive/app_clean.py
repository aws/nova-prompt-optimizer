# Let me create a clean working version
# First, let me copy the working parts and create a minimal dashboard

import os
import json
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
from components.navbar import create_navbar, create_navbar_styles, create_navbar_script
from components.ui import Button, Card, CardContainer, Textarea, Input, FormField, Badge, Alert, create_ui_styles

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
    ]
)

# Root route - Dashboard
@app.get("/")
async def index(request):
    """Main dashboard page"""
    user = await get_current_user(request)
    
    # Mock data for dashboard
    uploaded_datasets = [{"name": "Sample Dataset", "size": 1024}]
    created_prompts = [{"name": "Sample Prompt", "type": "user"}]
    optimization_runs = [{"name": "Sample Run", "status": "Completed"}]
    
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

if __name__ == "__main__":
    print("📁 Starting clean Nova Prompt Optimizer...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

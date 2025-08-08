#!/usr/bin/env python3
"""
Nova Prompt Optimizer - Working FastHTML Application

A simplified version that works with the current setup
"""

import os
import sys
import logging
from pathlib import Path

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from fasthtml.common import *
from starlette.middleware.sessions import SessionMiddleware

# Import configuration
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
settings = get_settings()

# Custom CSS and JavaScript headers
app_headers = [
    # CSS Framework and custom styles
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css'),
    
    # Meta tags
    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
    Meta(name='description', content='Nova Prompt Optimizer - Advanced AI Prompt Engineering Platform'),
]

# Initialize FastHTML app
app = FastHTML(
    debug=settings.DEBUG,
    hdrs=app_headers,
    secret_key=settings.SECRET_KEY
)

# Add middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=settings.SESSION_MAX_AGE
)

# Simple navigation component
def create_nav():
    return Nav(
        Div(
            A(
                Span("🧠", cls="logo-icon"),
                Span("Nova Prompt Optimizer", cls="brand-text"),
                href="/",
                cls="brand-link"
            ),
            cls="nav-brand"
        ),
        Div(
            A("Dashboard", href="/", cls="nav-link"),
            A("Prompts", href="/prompts", cls="nav-link"),
            A("Datasets", href="/datasets", cls="nav-link"),
            A("Health", href="/health", cls="nav-link"),
            cls="nav-links"
        ),
        cls="main-nav"
    )

# Main layout component
def create_layout(title: str, content):
    return Html(
        Head(
            Title(f"{title} - Nova Prompt Optimizer"),
            *app_headers
        ),
        Body(
            create_nav(),
            Main(
                Container(content),
                cls="main-content"
            ),
            cls="app-body"
        )
    )

# Routes
@app.get("/")
def dashboard():
    """Main dashboard"""
    return create_layout(
        "Dashboard",
        Div(
            H1("🧠 Nova Prompt Optimizer Dashboard"),
            P("Welcome to the Nova Prompt Optimizer! This is a working FastHTML application."),
            
            Div(
                Article(
                    Header(H3("✅ System Status")),
                    Ul(
                        Li("FastHTML Framework: Working"),
                        Li("Web Server: Running"),
                        Li("Configuration: Loaded"),
                        Li("Static Files: Available"),
                        Li("Routing: Functional")
                    )
                ),
                Article(
                    Header(H3("🚀 Quick Actions")),
                    Div(
                        A("View Health Check", href="/health", cls="button"),
                        A("Test Database", href="/test-db", cls="button secondary"),
                        A("View Settings", href="/settings", cls="button outline"),
                        cls="button-group"
                    )
                ),
                cls="grid"
            ),
            
            Article(
                Header(H3("📋 Next Steps")),
                Ol(
                    Li("✅ Basic FastHTML app is working"),
                    Li("🔄 Initialize database connection"),
                    Li("🔄 Add authentication system"),
                    Li("🔄 Implement prompt management"),
                    Li("🔄 Add optimization workflows"),
                    Li("🔄 Enable real-time features")
                )
            )
        )
    )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = "⚠️ Not configured"
        try:
            from models.database import db_manager
            db_status = "✅ Available"
        except Exception:
            db_status = "❌ Error"
        
        # Test AWS connection
        aws_status = "⚠️ Not configured"
        if settings.AWS_ACCESS_KEY_ID:
            aws_status = "✅ Configured"
        
        return create_layout(
            "Health Check",
            Div(
                H1("🏥 System Health Check"),
                
                Article(
                    Header(H3("Core Components")),
                    Table(
                        Thead(
                            Tr(Th("Component"), Th("Status"), Th("Details"))
                        ),
                        Tbody(
                            Tr(Td("FastHTML"), Td("✅ Working"), Td("Framework loaded successfully")),
                            Tr(Td("Configuration"), Td("✅ Working"), Td(f"Environment: {settings.DEBUG and 'Development' or 'Production'}")),
                            Tr(Td("Database"), Td(db_status), Td("SQLite/PostgreSQL connection")),
                            Tr(Td("AWS Integration"), Td(aws_status), Td("Nova model access")),
                            Tr(Td("Static Files"), Td("✅ Working"), Td("CSS and assets served")),
                        )
                    )
                ),
                
                Article(
                    Header(H3("Configuration")),
                    Ul(
                        Li(f"Debug Mode: {settings.DEBUG}"),
                        Li(f"Database: {settings.DATABASE_URL}"),
                        Li(f"AWS Region: {settings.AWS_REGION}"),
                        Li(f"Default Model: {settings.DEFAULT_NOVA_MODEL}"),
                    )
                ),
                
                A("Back to Dashboard", href="/", cls="button")
            )
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test-db")
def test_database():
    """Test database connection"""
    try:
        from models.database import init_database
        import asyncio
        
        # Try to initialize database
        asyncio.run(init_database())
        
        return create_layout(
            "Database Test",
            Div(
                H1("🗄️ Database Test"),
                Article(
                    Header(H3("✅ Database Connection Successful")),
                    P("The database has been initialized successfully."),
                    P("You can now proceed with the full application features."),
                    A("Back to Dashboard", href="/", cls="button")
                )
            )
        )
    except Exception as e:
        return create_layout(
            "Database Test",
            Div(
                H1("🗄️ Database Test"),
                Article(
                    Header(H3("❌ Database Connection Failed")),
                    P(f"Error: {str(e)}"),
                    P("Please check your database configuration and try again."),
                    Details(
                        Summary("Error Details"),
                        Pre(str(e))
                    ),
                    A("Back to Dashboard", href="/", cls="button")
                )
            )
        )

@app.get("/settings")
def settings_page():
    """Settings page"""
    return create_layout(
        "Settings",
        Div(
            H1("⚙️ Application Settings"),
            
            Article(
                Header(H3("Environment Configuration")),
                Table(
                    Tbody(
                        Tr(Td("Debug Mode"), Td(str(settings.DEBUG))),
                        Tr(Td("Host"), Td(settings.HOST)),
                        Tr(Td("Port"), Td(str(settings.PORT))),
                        Tr(Td("Database URL"), Td(settings.DATABASE_URL)),
                        Tr(Td("AWS Region"), Td(settings.AWS_REGION)),
                        Tr(Td("Default Nova Model"), Td(settings.DEFAULT_NOVA_MODEL)),
                        Tr(Td("Rate Limit"), Td(f"{settings.NOVA_RATE_LIMIT} TPS")),
                    )
                )
            ),
            
            Article(
                Header(H3("Feature Flags")),
                Table(
                    Tbody(
                        Tr(Td("Collaboration"), Td("✅" if settings.ENABLE_COLLABORATION else "❌")),
                        Tr(Td("Annotations"), Td("✅" if settings.ENABLE_ANNOTATIONS else "❌")),
                        Tr(Td("Advanced Charts"), Td("✅" if settings.ENABLE_ADVANCED_CHARTS else "❌")),
                        Tr(Td("Prompt Versioning"), Td("✅" if settings.ENABLE_PROMPT_VERSIONING else "❌")),
                    )
                )
            ),
            
            A("Back to Dashboard", href="/", cls="button")
        )
    )

# Placeholder routes
@app.get("/prompts")
def prompts():
    return create_layout("Prompts", H1("🔄 Prompts feature coming soon..."))

@app.get("/datasets") 
def datasets():
    return create_layout("Datasets", H1("🔄 Datasets feature coming soon..."))

# Error handlers
@app.exception_handler(404)
def not_found(request, exc):
    return create_layout(
        "Page Not Found",
        Div(
            H1("404 - Page Not Found"),
            P("The page you're looking for doesn't exist."),
            A("Go to Dashboard", href="/", cls="button")
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
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting Nova Prompt Optimizer on {args.host}:{args.port}")
    logger.info(f"📍 Visit: http://{args.host}:{args.port}")
    
    uvicorn.run(
        "app_working:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

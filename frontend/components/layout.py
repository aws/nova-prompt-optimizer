"""
Layout components for Nova Prompt Optimizer Frontend
"""

from typing import Optional, List, Dict, Any
from fasthtml.common import *
from shad4fast import ShadHead, Button, Card
from .navbar import create_navbar, create_navbar_styles, create_navbar_tabs_script
from .ui import create_ui_styles, CardContainer
from config import get_settings

settings = get_settings()


def create_navigation(current_page: str = "", user: Optional[Dict] = None) -> Nav:
    """Create main navigation bar"""
    
    nav_items = [
        {"name": "Dashboard", "path": "/", "icon": "🏠", "key": "dashboard"},
        {"name": "Datasets", "path": "/datasets", "icon": "📊", "key": "datasets"},
        {"name": "Prompts", "path": "/prompts", "icon": "✏️", "key": "prompts"},
        {"name": "Optimization", "path": "/optimization", "icon": "🚀", "key": "optimization"},
        {"name": "Annotation", "path": "/annotation", "icon": "🏷️", "key": "annotation"},
        {"name": "Results", "path": "/results", "icon": "📈", "key": "results"},
    ]
    
    # Create navigation links
    nav_links = []
    for item in nav_items:
        is_active = current_page == item["key"]
        nav_links.append(
            A(
                Span(item["icon"], cls="nav-icon"),
                Span(item["name"], cls="nav-text"),
                href=item["path"],
                cls=f"nav-link {'active' if is_active else ''}",
                hx_get=item["path"],
                hx_target="#main-content",
                hx_push_url="true"
            )
        )
    
    # User menu
    user_menu = Div(
        Button(
            Span("👤", cls="user-icon"),
            Span(user.get("username", "User") if user else "User", cls="user-name"),
            Span("▼", cls="dropdown-arrow"),
            cls="user-menu-button",
            onclick="toggleUserMenu()"
        ),
        Div(
            A("Profile", href="/profile", cls="dropdown-item"),
            A("Settings", href="/settings", cls="dropdown-item"),
            Hr(cls="dropdown-divider"),
            A("Logout", href="/auth/logout", cls="dropdown-item"),
            cls="user-dropdown",
            id="user-dropdown"
        ),
        cls="user-menu"
    ) if user else A("Login", href="/auth/login", cls="login-link")
    
    return Nav(
        Div(
            # Logo and brand
            A(
                Span("🧠", cls="logo-icon"),
                Span("Nova Prompt Optimizer", cls="brand-text"),
                href="/",
                cls="brand-link"
            ),
            cls="nav-brand"
        ),
        
        # Main navigation
        Div(
            *nav_links,
            cls="nav-links"
        ),
        
        # User menu
        user_menu,
        
        cls="main-nav",
        id="main-nav"
    )


def create_sidebar(current_page: str = "", user: Optional[Dict] = None) -> Aside:
    """Create sidebar with contextual content"""
    
    # Default sidebar content
    sidebar_content = [
        H3("Quick Actions", cls="sidebar-title"),
        Div(
            Button("New Prompt", 
                   hx_get="/prompts/new", 
                   hx_target="#main-content",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs"),
            Button("Upload Dataset", 
                   hx_get="/datasets/upload", 
                   hx_target="#main-content",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
            Button("Start Optimization", 
                   hx_get="/optimization/new", 
                   hx_target="#main-content",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs"),
            cls="quick-actions"
        )
    ]
    
    # Page-specific sidebar content
    if current_page == "prompts":
        sidebar_content.extend([
            Hr(),
            H4("Prompt Filters", cls="sidebar-subtitle"),
            Div(
                Label("Status:", cls="filter-label"),
                Select(
                    Option("All", value=""),
                    Option("Draft", value="draft"),
                    Option("Active", value="active"),
                    Option("Optimized", value="optimized"),
                    name="status_filter",
                    hx_get="/prompts/filter",
                    hx_target="#prompts-list",
                    hx_trigger="change"
                ),
                Label("Type:", cls="filter-label"),
                Select(
                    Option("All", value=""),
                    Option("System", value="system"),
                    Option("User", value="user"),
                    Option("Combined", value="combined"),
                    name="type_filter",
                    hx_get="/prompts/filter",
                    hx_target="#prompts-list",
                    hx_trigger="change"
                ),
                cls="filters"
            )
        ])
    
    elif current_page == "optimization":
        sidebar_content.extend([
            Hr(),
            H4("Recent Runs", cls="sidebar-subtitle"),
            Div(
                id="recent-optimizations",
                hx_get="/optimization/recent",
                hx_trigger="load"
            )
        ])
    
    elif current_page == "annotation":
        sidebar_content.extend([
            Hr(),
            H4("Annotation Stats", cls="sidebar-subtitle"),
            Div(
                id="annotation-stats",
                hx_get="/annotation/stats",
                hx_trigger="load"
            )
        ])
    
    return Aside(
        *sidebar_content,
        cls="main-sidebar",
        id="main-sidebar"
    )


def create_breadcrumb(items: List[Dict[str, str]]) -> Nav:
    """Create breadcrumb navigation"""
    
    breadcrumb_items = []
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        
        if is_last:
            breadcrumb_items.append(
                Span(item["name"], cls="breadcrumb-current")
            )
        else:
            breadcrumb_items.append(
                A(item["name"], href=item.get("path", "#"), cls="breadcrumb-link")
            )
            breadcrumb_items.append(
                Span(" / ", cls="breadcrumb-separator")
            )
    
    return Nav(
        *breadcrumb_items,
        cls="breadcrumb",
        aria_label="Breadcrumb"
    )


def create_notification_area() -> Div:
    """Create notification area for real-time updates"""
    
    return Div(
        # Success notifications
        Div(id="success-notifications", cls="notifications success-notifications"),
        
        # Error notifications  
        Div(id="error-notifications", cls="notifications error-notifications"),
        
        # Info notifications
        Div(id="info-notifications", cls="notifications info-notifications"),
        
        # Progress notifications
        Div(id="progress-notifications", cls="notifications progress-notifications"),
        
        cls="notification-area",
        id="notification-area"
    )


def create_loading_overlay() -> Div:
    """Create loading overlay for async operations"""
    
    return Div(
        Div(
            Div(cls="spinner"),
            cls="loading-content"
        ),
        cls="loading-overlay hidden",
        id="loading-overlay"
    )


def create_page_layout(
    title: str,
    content: Any,
    current_page: str = "",
    user: Optional[Dict] = None,
    use_card_container: bool = True
) -> Html:
    """
    Create a page layout with optional nested card container
    
    Args:
        title: Page title
        content: Page content (can be individual cards or other content)
        current_page: Current page identifier
        user: User information
        use_card_container: Whether to wrap content in CardContainer
    
    Returns:
        Complete HTML page
    """
    
    # Wrap content in CardContainer if requested
    if use_card_container:
        if isinstance(content, (list, tuple)):
            # If content is a list/tuple, assume they are cards to be nested
            wrapped_content = Div(
                H1(title.split(" - ")[0], style="margin-bottom: 1rem;"),
                P(f"Manage your {current_page} efficiently", 
                  style="color: #6b7280; margin-bottom: 2rem;"),
                CardContainer(*content),
                cls="card-container",
                style="display: flex; flex-direction: column; gap: 1.5rem;"
            )
        else:
            # Single content item
            wrapped_content = Div(
                content,
                cls="card-container",
                style="display: flex; flex-direction: column; gap: 1.5rem;"
            )
    else:
        wrapped_content = content
    
    return Html(
        Head(
            Title(f"{title} - Nova Prompt Optimizer"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            create_navbar_styles(),
            create_ui_styles(),
            create_navbar_tabs_script(),
            # Delete confirmation functionality
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
        ),
        Body(
            create_navbar(current_page, user),
            Main(wrapped_content),
            cls=f"page-{current_page}" if current_page else ""
        )
    )


def create_navbar_tabs_only(current_page: str = "") -> Div:
    """Create just the navigation tabs without title"""
    nav_items = [
        {"name": "Dashboard", "path": "/", "key": "dashboard"},
        {"name": "Prompts", "path": "/prompts", "key": "prompts"},
        {"name": "Datasets", "path": "/datasets", "key": "datasets"},
        {"name": "Metrics", "path": "/metrics", "key": "metrics"},
        {"name": "Optimization", "path": "/optimization", "key": "optimization"},
    ]
    
    return Div(
        *[A(
            item["name"],
            href=item["path"],
            cls=f"px-4 py-2 text-sm font-medium rounded-md transition-colors {'bg-primary text-primary-foreground' if current_page == item['key'] else 'text-muted-foreground hover:text-foreground hover:bg-muted'}"
        ) for item in nav_items],
        cls="flex items-center gap-2"
    )


def create_main_layout(
    title: str,
    content: Any,
    show_sidebar: bool = False,
    extra_head: Optional[List] = None,
    user: Optional[dict] = None,
    current_page: str = "",
    breadcrumb: Optional[List] = None
) -> Html:
    """Create main page layout"""
    
    # Build head section with official Shad4FastHTML
    head_content = [
        Title(f"{title} - {settings.APP_NAME}"),
        ShadHead(tw_cdn=True, theme_handle=True),
        
        # Global theme toggle function (available on all pages)
        Script("""
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                const toggleButton = document.getElementById('theme-toggle');
                if (toggleButton) {
                    toggleButton.title = newTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
                }
                
                console.log('Theme switched to:', newTheme);
                window.location.reload();
            }
        """),
        
        # Favicon (data URL to avoid 404)
        Link(rel="icon", type="image/png", href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="),
        
        # Essential layout styles that work with Shad4FastHTML
        Style("""
            /* Global dark mode text color fixes */
            [data-theme="dark"] h1,
            [data-theme="dark"] h2, 
            [data-theme="dark"] h3,
            [data-theme="dark"] h4,
            [data-theme="dark"] h5,
            [data-theme="dark"] h6 {
                color: hsl(var(--foreground)) !important;
            }
            
            [data-theme="dark"] [style*="color: #1f2937"],
            [data-theme="dark"] [style*="color: #374151"],
            [data-theme="dark"] [style*="color: #111827"] {
                color: hsl(var(--foreground)) !important;
            }
        """),
        Style("""
            /* Global Layout */
            .main-container {
                max-width: 95%;
                margin: 0 auto;
                padding: 1rem;
            }
            
            /* Card System using Shad4FastHTML variables */
            .card-section {
                background: hsl(var(--background));
                border: 1px solid hsl(var(--border));
                border-radius: 8px;
                margin-bottom: 1.5rem;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            .card-header {
                padding: 1rem 1.5rem;
                border-bottom: 1px solid hsl(var(--border));
                background: hsl(var(--muted) / 0.3);
                font-weight: 600;
            }
            
            .card-content {
                padding: 1.5rem;
            }
            
            .card-nested {
                background: hsl(var(--muted) / 0.1);
                border: 1px solid hsl(var(--border));
                border-radius: 6px;
                margin-bottom: 1rem;
            }
            
            .card-nested .card-header {
                padding: 0.75rem 1rem;
                background: hsl(var(--muted) / 0.2);
            }
            
            .card-nested .card-content {
                padding: 1rem;
            }
            
            /* Navbar styling */
            .main-navbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem 2rem;
                background: hsl(var(--background));
                border-bottom: 1px solid hsl(var(--border));
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            /* Navbar brand */
            .nav-brand {
                display: flex;
                align-items: center;
                min-width: 200px;
                flex: 0 0 auto;
            }
            
            .nav-brand .brand-link {
                color: hsl(var(--foreground));
                text-decoration: none;
                font-weight: 700;
                font-size: 1.25rem;
            }
            
            /* Navbar tabs container */
            .nav-tabs-container {
                flex: 1;
                display: flex;
                justify-content: center;
                max-width: 1200px;
                margin: 0 2rem;
            }
            
            .nav-tab-list {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 2rem;
                width: 100%;
                max-width: 800px;
                background: transparent;
                padding: 0;
                border: none;
            }
            
            /* Tab triggers with separators */
            .nav-tab-trigger {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 12px 24px;
                color: hsl(var(--muted-foreground));
                text-decoration: none;
                font-weight: 500;
                border-radius: 6px;
                transition: all 0.2s ease;
                position: relative;
            }
            
            .nav-tab-trigger:hover {
                background: hsl(var(--accent));
                color: hsl(var(--accent-foreground));
            }
            
            .nav-tab-trigger.active {
                background: hsl(var(--primary));
                color: hsl(var(--primary-foreground));
            }
            
            /* Tab separators - centered between items */
            .nav-tab-trigger:not(:last-child)::after {
                content: '';
                position: absolute;
                right: -1rem;
                top: 50%;
                transform: translateY(-50%);
                width: 1px;
                height: 20px;
                background: hsl(var(--border));
            }
            
            /* User section */
            .user-summary {
                padding: 8px 16px;
                color: hsl(var(--foreground));
                cursor: pointer;
                border-radius: 4px;
                border: 1px solid hsl(var(--border));
                background: hsl(var(--background));
                font-weight: 500;
                font-size: 0.875rem;
                transition: all 0.2s ease;
            }
            
            .user-summary:hover {
                background: hsl(var(--accent));
                color: hsl(var(--accent-foreground));
            }
            
            /* Override CSS variables after ShadHead() */
            :root {
                --destructive: 0 84.2% 60.2% !important;
                --destructive-foreground: 210 40% 98% !important;
            }
        """),
        
        # Navbar styles
        create_navbar_styles(),
        
        # UI component styles
        create_ui_styles(),
        
        # TODO: Add back when static files are created
        # Link(rel="stylesheet", href="/static/css/main.css"),
        # Link(rel="stylesheet", href="/static/css/components.css"),
        
        # JavaScript - Using CDN only for now
        # TODO: Add back when static files are created
        # Script(src="/static/js/utils.js"),
        # Script(src="/static/js/collaboration.js"),
        
        # Global JavaScript functions
        Script("""
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
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    background: ${type === 'success' ? '#10b981' : '#ef4444'};
                `;
                messageDiv.textContent = message;
                document.body.appendChild(messageDiv);
                
                setTimeout(() => {
                    messageDiv.style.opacity = '0';
                    messageDiv.style.transition = 'opacity 0.3s ease';
                    setTimeout(() => messageDiv.remove(), 300);
                }, 3000);
            }
        """),
        
        # HTMX
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
        
        # Tab navigation script
        create_navbar_tabs_script(),
        
        # Defensive JavaScript to prevent classList errors from browser extensions
        Script("""
            // Defensive code to prevent classList errors from browser extensions
            (function() {
                'use strict';
                
                // Wrap common DOM methods to catch classList errors
                const originalQuerySelector = document.querySelector;
                const originalQuerySelectorAll = document.querySelectorAll;
                
                document.querySelector = function(selector) {
                    try {
                        return originalQuerySelector.call(this, selector);
                    } catch (error) {
                        console.warn('Prevented querySelector error:', error.message);
                        return null;
                    }
                };
                
                document.querySelectorAll = function(selector) {
                    try {
                        return originalQuerySelectorAll.call(this, selector);
                    } catch (error) {
                        console.warn('Prevented querySelectorAll error:', error.message);
                        return [];
                    }
                };
                
                // Prevent classList errors by checking element existence
                const originalAddEventListener = document.addEventListener;
                document.addEventListener = function(type, listener, options) {
                    if (typeof listener === 'function') {
                        const wrappedListener = function(event) {
                            try {
                                return listener.call(this, event);
                            } catch (error) {
                                if (error.message && (error.message.includes('classList') || error.message.includes('null'))) {
                                    console.warn('Prevented DOM error from extension:', error.message);
                                    return;
                                }
                                throw error;
                            }
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                console.log('Nova Prompt Optimizer: Defensive JavaScript loaded successfully');
            })();
        """),
        
        # TODO: Add favicon when created
        # Link(rel="icon", type="image/svg+xml", href="/static/assets/favicon.svg")
    ]
    
    if extra_head:
        head_content.extend(extra_head)
    
    # Build body content
    body_content = [
        # Title row with theme toggle
        Div(
            Div(
                H1("Nova Prompt Optimizer", cls="text-2xl font-bold text-foreground"),
                cls="flex-1"
            ),
            Div(
                Button(
                    "◐",
                    onclick="toggleTheme()",
                    id="theme-toggle",
                    title="Toggle theme",
                    cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 w-9"
                ),
                cls="flex-shrink-0"
            ),
            cls="flex items-center justify-between px-6 py-4 border-b border-border bg-background"
        ),
        
        # Navigation row (centered)
        Div(
            create_navbar_tabs_only(current_page),
            cls="flex justify-center px-6 py-3 border-b border-border bg-muted/30"
        ),
        
        # Main container
        Div(
            # Sidebar (if enabled)
            create_sidebar(current_page, user) if show_sidebar else None,
            
            # Main content area
            Main(
                # Breadcrumb (if provided)
                create_breadcrumb(breadcrumb) if breadcrumb else None,
                
                # Page content
                Div(
                    content,
                    cls="page-content",
                    id="main-content"
                ),
                
                cls="main-content"
            ),
            
            cls=f"main-container {'with-sidebar' if show_sidebar else 'no-sidebar'}"
        ),
        
        # Notification area
        create_notification_area(),
        
        # Loading overlay
        create_loading_overlay(),
        
        # JavaScript initialization
        Script("""
            // Initialize HTMX
            document.addEventListener('DOMContentLoaded', function() {
                // Configure HTMX
                htmx.config.globalViewTransitions = true;
                htmx.config.scrollBehavior = 'smooth';
                
                // Add loading indicators
                document.addEventListener('htmx:beforeRequest', function(evt) {
                    showLoading();
                });
                
                document.addEventListener('htmx:afterRequest', function(evt) {
                    hideLoading();
                });
                
                // Initialize real-time features
                if (typeof initializeRealTime === 'function') {
                    initializeRealTime();
                }
            });
            
            // Utility functions
            function showLoading() {
                document.getElementById('loading-overlay').classList.remove('hidden');
            }
            
            function hideLoading() {
                document.getElementById('loading-overlay').classList.add('hidden');
            }
            
            function toggleUserMenu() {
                const dropdown = document.getElementById('user-dropdown');
                dropdown.classList.toggle('show');
            }
            
            // Close user menu when clicking outside
            document.addEventListener('click', function(event) {
                const userMenu = document.querySelector('.user-menu');
                const dropdown = document.getElementById('user-dropdown');
                
                if (userMenu && !userMenu.contains(event.target)) {
                    dropdown.classList.remove('show');
                }
            });
            
            // Show notifications
            function showNotification(message, type = 'info', duration = 5000) {
                const container = document.getElementById(`${type}-notifications`);
                const notification = document.createElement('div');
                notification.className = `notification ${type}`;
                notification.innerHTML = `
                    <span class="notification-message">${message}</span>
                    <button class="notification-close" onclick="this.parentElement.remove()">×</button>
                `;
                
                container.appendChild(notification);
                
                // Auto-remove after duration
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, duration);
            }
        """)
    ]
    
    return Html(
        Head(*head_content),
        Body(*body_content, cls=f"page-{current_page}" if current_page else "")
    )


def create_modal(
    title: str,
    content: Any,
    modal_id: str = "modal",
    size: str = "medium",
    closable: bool = True
) -> Div:
    """Create modal dialog"""
    
    return Div(
        Div(
            Div(
                # Modal header
                Div(
                    H3(title, cls="modal-title"),
                    Button(
                        "×",
                        cls="modal-close",
                        onclick=f"closeModal('{modal_id}')"
                    ) if closable else None,
                    cls="modal-header"
                ),
                
                # Modal body
                Div(
                    content,
                    cls="modal-body"
                ),
                
                cls=f"modal-content {size}"
            ),
            cls="modal-dialog"
        ),
        cls="modal hidden",
        id=modal_id,
        onclick=f"if (event.target === this) closeModal('{modal_id}')"
    )


def create_card(
    title: Optional[str] = None,
    content: Any = None,
    actions: Optional[List] = None,
    cls: str = ""
) -> Div:
    """Create card component"""
    
    card_content = []
    
    if title:
        card_content.append(
            Div(
                H4(title, cls="card-title"),
                cls="card-header"
            )
        )
    
    if content:
        card_content.append(
            Div(
                content,
                cls="card-body"
            )
        )
    
    if actions:
        card_content.append(
            Div(
                *actions,
                cls="card-actions"
            )
        )
    
    return Div(
        *card_content,
        cls=f"card {cls}"
    )


def create_table(
    headers: List[str],
    rows: List[List[Any]],
    actions: Optional[List[Dict]] = None,
    cls: str = ""
) -> Div:
    """Create table component"""
    
    # Create header row
    header_cells = [Th(header) for header in headers]
    if actions:
        header_cells.append(Th("Actions"))
    
    # Create data rows
    table_rows = []
    for i, row in enumerate(rows):
        cells = [Td(cell) for cell in row]
        
        # Add action buttons if provided
        if actions:
            action_buttons = []
            for action in actions:
                action_buttons.append(
                    Button(
                        action["label"],
                        cls=f"btn btn-sm {action.get('class', 'btn-secondary')}",
                        onclick=action["onclick"].replace("{index}", str(i)) if "onclick" in action else None,
                        **{k: v.replace("{index}", str(i)) if isinstance(v, str) else v 
                           for k, v in action.items() if k not in ["label", "class", "onclick"]}
                    )
                )
            cells.append(Td(*action_buttons, cls="actions-cell"))
        
        table_rows.append(Tr(*cells))
    
    return Div(
        Table(
            Thead(Tr(*header_cells)),
            Tbody(*table_rows),
            cls="table"
        ),
        cls=f"table-container {cls}"
    )

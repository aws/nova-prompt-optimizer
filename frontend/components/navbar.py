"""
Navigation bar component for Nova Prompt Optimizer using Shad4FastHTML tabs pattern
"""

from fasthtml.common import *

def create_navbar_tabs(current_page=None, user=None):
    """
    Create a navigation bar using Shad4FastHTML tabs pattern
    
    Args:
        current_page (str): Current page identifier for highlighting active nav item
        user (dict): User information for displaying user menu
    
    Returns:
        Nav element with tab-based navigation
    """
    
    # Navigation items with their routes (no icons)
    nav_items = [
        {"name": "Dashboard", "route": "/", "id": "dashboard"},
        {"name": "Prompts", "route": "/prompts", "id": "prompts"},
        {"name": "Datasets", "route": "/datasets", "id": "datasets"},
        {"name": "Metrics", "route": "/metrics", "id": "metrics"},
        {"name": "Optimization", "route": "/optimization", "id": "optimization"},
    ]
    
    # Create tab triggers (navigation links)
    tab_triggers = []
    for item in nav_items:
        is_active = current_page == item["id"]
        
        tab_triggers.append(
            A(
                item["name"],
                href=item["route"],
                cls="nav-tab-trigger",
                **{
                    "data-tab-trigger": "",
                    "data-value": item["id"],
                    "aria-selected": "true" if is_active else "false",
                    "data-state": "active" if is_active else "",
                    "role": "tab"
                }
            )
        )
    
    # Theme toggle button (separate from user menu)
    theme_toggle = Button(
        "🌙", # Moon icon for dark mode
        id="theme-toggle",
        cls="theme-toggle",
        onclick="toggleTheme()",
        title="Toggle dark/light mode",
        **{"aria-label": "Toggle theme"}
    )
    
    # User menu (if user is logged in)
    user_menu = None
    if user:
        user_menu = Div(
            cls="user-container"
        )
    else:
        user_menu = Div(
            A(
                "Login",
                href="/auth/login",
                cls="login-link"
            ),
            cls="auth-container"
        )
    
    # Main navigation bar with tabs pattern
    return Nav(
        Div(
            # Brand/Logo section
            A(
                "Nova Prompt Optimizer",
                href="/",
                cls="brand-link"
            ),
            cls="nav-brand"
        ),
        
        # Tab navigation container
        Div(
            # Tab list (navigation links)
            Div(
                *tab_triggers,
                cls="nav-tab-list",
                role="tablist",
                **{"aria-label": "Main navigation tabs"}
            ),
            cls="nav-tabs-container",
            **{
                "data-ref": "tabs",
                "data-default-value": current_page or "dashboard"
            }
        ),
        
        # Theme toggle (separate element)
        theme_toggle,
        
        # User menu section
        user_menu,
        
        cls="main-navbar",
        role="navigation",
        **{"aria-label": "Main navigation"}
    )

def create_navbar_tabs_styles():
    """
    Create CSS styles for the tab-based navigation bar (Black & White theme)
    
    Returns:
        Style element with navbar tabs CSS
    """
    return Style("""
        /* CSS Variables for Theme Support */
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --text-primary: #000000;
            --text-secondary: #666666;
            --border-color: #e5e5e5;
            --border-hover: #d1d5db;
            --shadow-color: rgba(0, 0, 0, 0.1);
            --shadow-hover: rgba(0, 0, 0, 0.15);
        }
        
        /* Dark Mode Variables */
        [data-theme="dark"] {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --border-color: #404040;
            --border-hover: #525252;
            --shadow-color: rgba(0, 0, 0, 0.3);
            --shadow-hover: rgba(0, 0, 0, 0.4);
        }
        
        /* Apply theme variables to body */
        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        /* Main Navigation Bar */
        .main-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 2rem;
            background: var(--bg-primary);
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 1000;
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        /* Brand Section */
        .nav-brand {
            display: flex;
            align-items: center;
            min-width: 200px; /* Ensure minimum width */
            flex: 0 0 auto; /* Don't grow or shrink */
            /* Subtle visual indicator for development - remove in production */
            /* border: 1px solid rgba(102, 126, 234, 0.1); */
        }
        
        .nav-brand .brand-link {
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 700;
            font-size: 1.25rem;
            transition: color 0.2s ease;
        }
        
        .nav-brand .brand-link:hover {
            color: var(--text-secondary);
        }
        
        /* Tabs Container - More fluid layout */
        .nav-tabs-container {
            flex: 1;
            display: flex;
            justify-content: center;
            max-width: 1200px; /* Match main page card width */
            margin: 0 2rem;
        }
        
        /* Tab List - Remove bounding box, add separators */
        .nav-tab-list {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            max-width: 800px;
            background: transparent; /* Remove background */
            border-radius: 0; /* Remove border radius */
            padding: 0; /* Remove padding */
            border: none; /* Remove border */
            position: relative;
        }
        
        /* Tab Triggers (Navigation Links) - Clean minimal style */
        .nav-tab-trigger {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px 24px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-weight: 500;
            font-size: 0.875rem;
            white-space: nowrap;
            flex: 1;
            position: relative;
        }
        
        /* Add separator between tabs (except last one) */
        .nav-tab-trigger:not(:last-child)::after {
            content: '';
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 1px;
            height: 20px;
            background: var(--border-color);
            transition: background-color 0.3s ease;
        }
        
        .nav-tab-trigger:hover {
            color: var(--text-primary);
            background: var(--bg-secondary);
            transform: translateY(-1px);
        }
        
        /* Active Tab State - More subtle without box */
        .nav-tab-trigger[data-state="active"],
        .nav-tab-trigger[aria-selected="true"] {
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-weight: 600;
            box-shadow: 0 2px 4px var(--shadow-color);
        }
        
        .nav-tab-trigger[data-state="active"]:hover,
        .nav-tab-trigger[aria-selected="true"]:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
            transform: translateY(-1px);
        }
        
        /* Theme Toggle Button */
        .theme-toggle {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.2s ease;
            margin-right: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 40px;
            height: 36px;
        }
        
        .theme-toggle:hover {
            background: var(--bg-primary);
            border-color: var(--border-hover);
            transform: scale(1.05);
        }
        
        .theme-toggle:active {
            transform: scale(0.95);
        }
        
        /* User Menu */
        .user-container, .auth-container {
            display: flex;
            align-items: center;
            justify-content: flex-end; /* Align content to the right */
            min-width: 200px; /* Match nav-brand minimum width */
            flex: 0 0 auto; /* Don't grow or shrink */
            /* Subtle visual indicator for development - remove in production */
            /* border: 1px solid rgba(102, 126, 234, 0.1); */
        }
        
        .user-menu {
            position: relative;
        }
        
        .user-summary {
            padding: 8px 16px;
            color: var(--text-primary);
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s ease;
            border: 1px solid var(--border-color);
            background: var(--bg-primary);
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .user-summary:hover {
            background: var(--bg-secondary);
            border-color: var(--border-hover);
        }
        
        .user-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            min-width: 12rem;
            background: var(--bg-primary);
            border-radius: 6px;
            box-shadow: 0 4px 12px var(--shadow-hover);
            padding: 8px 0;
            margin-top: 4px;
            z-index: 1001;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .dropdown-item {
            display: block;
            padding: 8px 16px;
            color: var(--text-primary);
            text-decoration: none;
            font-size: 0.875rem;
            transition: background 0.2s ease;
        }
        
        .dropdown-item:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .dropdown-item.logout {
            color: var(--text-primary);
            border-top: 1px solid var(--border-color);
            margin-top: 4px;
            padding-top: 12px;
        }
        
        .dropdown-item.logout:hover {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        /* Login Link */
        .login-link {
            padding: 8px 16px;
            color: var(--text-primary);
            text-decoration: none;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            transition: all 0.2s ease;
            font-weight: 500;
            font-size: 0.875rem;
            background: var(--bg-primary);
        }
        
        .login-link:hover {
            background: var(--bg-secondary);
            border-color: var(--border-hover);
        }
        
        /* Focus States for Accessibility */
        .nav-tab-trigger:focus-visible,
        .theme-toggle:focus-visible {
            outline: 2px solid #3b82f6;
            outline-offset: 2px;
        }
        
        .user-summary:focus-visible,
        .login-link:focus-visible {
            outline: 2px solid #3b82f6;
            outline-offset: 2px;
        }
        
        /* Responsive Design */
        @media (max-width: 1024px) {
            .nav-tabs-container {
                margin: 0 1rem;
                max-width: 900px;
            }
            
            .nav-tab-list {
                max-width: 700px;
            }
            
            /* Maintain matching widths on tablets */
            .nav-brand,
            .user-container, .auth-container {
                min-width: 150px;
            }
        }
        
        @media (max-width: 768px) {
            .main-navbar {
                padding: 0.75rem 1rem;
            }
            
            .nav-tabs-container {
                margin: 0 0.5rem;
                max-width: 600px;
            }
            
            .nav-tab-list {
                max-width: 500px;
            }
            
            .nav-tab-trigger {
                padding: 10px 16px;
                font-size: 0.8rem;
            }
            
            /* Maintain matching widths on mobile */
            .nav-brand,
            .user-container, .auth-container {
                min-width: 120px;
            }
            
            /* Adjust separator height for smaller screens */
            .nav-tab-trigger:not(:last-child)::after {
                height: 16px;
            }
            
            .theme-toggle {
                margin-right: 0.5rem;
                padding: 6px 10px;
                min-width: 36px;
                height: 32px;
                font-size: 0.9rem;
            }
        }
        
        @media (max-width: 480px) {
            .main-navbar {
                padding: 0.5rem 0.75rem;
            }
            
            .nav-tabs-container {
                margin: 0 0.25rem;
            }
            
            .nav-tab-trigger {
                padding: 8px 12px;
                font-size: 0.75rem;
            }
            
            /* Maintain matching widths on small mobile */
            .nav-brand,
            .user-container, .auth-container {
                min-width: 100px;
            }
            
            /* Smaller separator for mobile */
            .nav-tab-trigger:not(:last-child)::after {
                height: 14px;
            }
            
            .theme-toggle {
                margin-right: 0.25rem;
                padding: 4px 8px;
                min-width: 32px;
                height: 28px;
                font-size: 0.8rem;
            }
        }
        
        /* Clean transitions */
        .nav-tab-trigger {
            transition: all 0.15s ease;
        }
        
        /* Remove any remaining icon styles */
        .nav-icon,
        .nav-text,
        .brand-icon,
        .brand-text,
        .user-icon,
        .username,
        .login-icon,
        .login-text {
            /* These classes are no longer used but kept for compatibility */
        }
    """)

def create_navbar_tabs_script():
    """
    Create JavaScript for tab functionality (following Shad4FastHTML pattern)
    
    Returns:
        Script element with tab navigation JavaScript
    """
    return Script("""
        // Theme toggle functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Set the new theme
            document.documentElement.setAttribute('data-theme', newTheme);
            
            // Update the toggle button icon
            const toggleButton = document.getElementById('theme-toggle');
            if (toggleButton) {
                toggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
                toggleButton.title = newTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            }
            
            // Save preference to localStorage
            localStorage.setItem('theme', newTheme);
            
            console.log('Theme switched to:', newTheme);
        }
        
        // Initialize theme on page load
        function initializeTheme() {
            // Check for saved theme preference or default to light
            const savedTheme = localStorage.getItem('theme') || 'light';
            
            // Apply the theme
            document.documentElement.setAttribute('data-theme', savedTheme);
            
            // Update the toggle button
            const toggleButton = document.getElementById('theme-toggle');
            if (toggleButton) {
                toggleButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
                toggleButton.title = savedTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            }
            
            console.log('Theme initialized:', savedTheme);
        }
        
        // Match nav-brand and user-container widths for perfect centering
        function matchNavbarWidths() {
            const navBrand = document.querySelector('.nav-brand');
            const userContainer = document.querySelector('.user-container, .auth-container');
            
            if (!navBrand || !userContainer) {
                console.log('Navbar containers not found, skipping width matching');
                return;
            }
            
            // Reset any previous width settings
            navBrand.style.minWidth = '';
            userContainer.style.minWidth = '';
            
            // Get natural widths
            const brandWidth = navBrand.offsetWidth;
            const userWidth = userContainer.offsetWidth;
            
            // Set both to the larger width
            const maxWidth = Math.max(brandWidth, userWidth);
            
            navBrand.style.minWidth = maxWidth + 'px';
            userContainer.style.minWidth = maxWidth + 'px';
            
            console.log(`Navbar widths matched: ${maxWidth}px (brand: ${brandWidth}px, user: ${userWidth}px)`);
        }
        
        // Tab navigation functionality (Shad4FastHTML pattern)
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize theme first
            initializeTheme();
            
            // Match navbar container widths for perfect centering
            matchNavbarWidths();
            
            // Re-match widths on window resize
            window.addEventListener('resize', matchNavbarWidths);
            
            // Defensive check - only run if tabs container exists
            const tabsContainer = document.querySelector('[data-ref="tabs"]');
            if (!tabsContainer) {
                console.log('No tabs container found, skipping tab navigation setup');
                return;
            }
            
            const triggers = tabsContainer.querySelectorAll('[data-tab-trigger]');
            if (!triggers || triggers.length === 0) {
                console.log('No tab triggers found, skipping tab navigation setup');
                return;
            }
            
            function setActiveTab(value) {
                triggers.forEach(trigger => {
                    // Defensive check for each trigger
                    if (!trigger || !trigger.dataset) return;
                    
                    if (trigger.dataset.value === value) {
                        trigger.setAttribute('aria-selected', 'true');
                        trigger.dataset.state = 'active';
                    } else {
                        trigger.setAttribute('aria-selected', 'false');
                        trigger.dataset.state = '';
                    }
                });
            }
            
            // Handle keyboard navigation
            triggers.forEach((trigger, index) => {
                if (!trigger) return; // Defensive check
                
                trigger.addEventListener('keydown', (event) => {
                    let newIndex = index;
                    
                    switch(event.key) {
                        case 'ArrowLeft':
                            event.preventDefault();
                            newIndex = index > 0 ? index - 1 : triggers.length - 1;
                            break;
                        case 'ArrowRight':
                            event.preventDefault();
                            newIndex = index < triggers.length - 1 ? index + 1 : 0;
                            break;
                        case 'Home':
                            event.preventDefault();
                            newIndex = 0;
                            break;
                        case 'End':
                            event.preventDefault();
                            newIndex = triggers.length - 1;
                            break;
                        default:
                            return;
                    }
                    
                    // Defensive check before focusing
                    if (triggers[newIndex] && triggers[newIndex].focus) {
                        triggers[newIndex].focus();
                    }
                });
            });
            
            // Set initial active tab
            const defaultValue = tabsContainer.dataset ? tabsContainer.dataset.defaultValue : null;
            if (defaultValue) {
                setActiveTab(defaultValue);
            }
            
            console.log('Tab navigation setup complete');
        });
        
        // Keyboard shortcut for theme toggle (Ctrl/Cmd + Shift + T)
        document.addEventListener('keydown', function(event) {
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
                event.preventDefault();
                toggleTheme();
            }
        });
    """)

# Backward compatibility - keep the original function name
def create_navbar(current_page=None, user=None):
    """Backward compatibility wrapper"""
    return create_navbar_tabs(current_page, user)

# Remove the old icon-based styles and update the backward compatibility
def create_navbar_styles():
    """Backward compatibility wrapper"""
    return create_navbar_tabs_styles()

def create_navbar_script():
    """Backward compatibility wrapper for navbar script"""
    return create_navbar_tabs_script()

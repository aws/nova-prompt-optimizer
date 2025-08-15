"""
Navigation bar component for Nova Prompt Optimizer using Shad4FastHTML tabs pattern
"""

from fasthtml.common import *
from shad4fast import Button

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
                cls="nav-tab-trigger" + (" active" if is_active else ""),
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
        "◐", # Half-filled circle icon for theme toggle
        variant="ghost",
        size="sm",
        id="theme-toggle",
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
        Empty style - inherits from layout.py
    """
    return Style("")

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
            
            // Update the toggle button title (no need to change icon since ◐ works for both)
            const toggleButton = document.getElementById('theme-toggle');
            if (toggleButton) {
                toggleButton.title = newTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            }
            
            // Save preference to localStorage
            localStorage.setItem('theme', newTheme);
            
            console.log('Theme switched to:', newTheme);
            
            // Force a page refresh to apply theme changes
            window.location.reload();
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

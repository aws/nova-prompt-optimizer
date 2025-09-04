# Nova Prompt Optimizer - Frontend Styling Guide

## Overview

This document serves as the comprehensive styling reference for the Nova Prompt Optimizer frontend application. Our styling approach uses **ShadHead with Tailwind CSS** for consistent, modern UI components.

## Design Philosophy

### Core Principles
- **Modern & Clean**: Professional appearance with clean lines and modern aesthetics
- **Accessible**: WCAG compliant with proper ARIA labels and semantic HTML
- **Responsive**: Mobile-first design that works across all device sizes
- **Consistent**: Unified design language throughout the application
- **Performance**: Lightweight CSS with minimal dependencies

## Technology Stack

### CSS Framework
- **Primary**: ShadHead with Tailwind CSS (`ShadHead(tw_cdn=True, theme_handle=True)`)
- **Component Library**: Shad4FastHTML components
- **Why This Stack**: Theme-aware components, comprehensive utility classes, consistent design system

### JavaScript Libraries
- **HTMX**: `https://unpkg.com/htmx.org@1.9.10` - Dynamic interactions
- **FastHTML JS**: Built-in FastHTML JavaScript utilities

### Component Architecture
- **FastHTML Components**: Python-based component system
- **ShadHead**: Provides Tailwind CSS and theme handling
- **CSS Classes**: Tailwind utility classes with theme-aware custom properties

## Layout System

### Main Layout Structure
```python
# Location: components/layout.py
def create_main_layout(title, content, current_page="", user=None):
    return Html(
        Head(
            Title(f"{title} - Nova Prompt Optimizer"),
            ShadHead(tw_cdn=True, theme_handle=True),
            # Additional scripts and styles
        ),
        Body(
            # Navigation bar
            create_navbar(current_page, user),
            # Main content
            Main(content, cls="main-content"),
            cls=f"page-{current_page}" if current_page else ""
        )
    )
```

## Component Styling Standards

### Buttons
```python
# Primary Button Classes
cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"

# Secondary Button Classes  
cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"
```

### Form Elements
```python
# Input Fields
cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"

# Textarea Fields
cls="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"

# Select Elements
cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
```

### Cards
```python
# Card Container
cls="bg-card text-card-foreground shadow-sm border rounded-lg"

# Card with Header and Body Structure
Div(
    Div(
        H4("Card Title", cls="card-title"),
        cls="card-header"
    ),
    Div(
        # Card content here
        cls="card-body"
    ),
    cls="card"
)
```

### Typography
```python
# Headings
H1(cls="text-2xl font-bold mb-4")
H2(cls="text-xl font-semibold mb-4") 
H3(cls="text-lg font-semibold mb-2")
H4(cls="font-semibold text-lg mb-2")

# Text Colors
cls="text-muted-foreground"  # Secondary text
cls="text-card-foreground"   # Primary text on cards
cls="text-primary"           # Brand color text
```

## Theme System

### CSS Custom Properties
The ShadHead component provides theme-aware CSS custom properties:

```css
/* Available through ShadHead theming */
--background
--foreground
--card
--card-foreground
--primary
--primary-foreground
--muted
--muted-foreground
--border
--input
--ring
--accent
--accent-foreground
```

### Theme Usage
```python
# Use theme-aware classes instead of hardcoded colors
cls="bg-background text-foreground"     # ✅ Good
cls="bg-white text-black"               # ❌ Avoid

cls="border-border"                     # ✅ Good  
cls="border-gray-200"                   # ❌ Avoid

cls="text-muted-foreground"             # ✅ Good
cls="text-gray-600"                     # ❌ Avoid
```

## Layout Patterns

### Container and Spacing
```python
# Page Container
cls="container mx-auto px-4 py-8"

# Card Container  
cls="max-w-2xl mx-auto"

# Grid Layouts
cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"

# Flexbox Layouts
cls="flex items-center justify-between"
cls="flex flex-col space-y-4"
```

### Responsive Design
```python
# Mobile-first responsive classes
cls="w-full md:w-1/2 lg:w-1/3"
cls="text-sm md:text-base lg:text-lg"
cls="p-4 md:p-6 lg:p-8"
```

## Component Integration

### Avoiding create_main_layout Issues
When `create_main_layout` causes raw HTML display issues, use manual structure:

```python
# ❌ Problematic (can cause raw HTML display)
return create_main_layout(title="Page", content=content)

# ✅ Working alternative
return Html(
    ShadHead(tw_cdn=True, theme_handle=True),
    Body(
        Main(
            Div(
                # Your content here
                cls="container mx-auto px-4 py-8"
            )
        )
    )
)
```

### Form Structure
```python
Form(
    Div(
        Label("Field Label:", cls="block text-sm font-medium mb-2"),
        Input(type="text", name="field", cls="[input-classes]"),
        cls="mb-4"
    ),
    Button("Submit", type="submit", cls="[button-classes]"),
    method="post",
    action="/endpoint"
)
```

## Best Practices

### 1. **Always Use ShadHead**
```python
# Required for proper styling
ShadHead(tw_cdn=True, theme_handle=True)
```

### 2. **Use Theme-Aware Classes**
- Prefer `text-muted-foreground` over `text-gray-600`
- Use `bg-background` instead of `bg-white`
- Use `border-border` instead of `border-gray-200`

### 3. **Consistent Component Classes**
- Copy exact class strings from working components
- Don't modify or shorten the utility class chains
- Include all accessibility and focus classes

### 4. **Avoid Layout Component Issues**
- Test `create_main_layout` first
- Fall back to manual HTML structure if needed
- Always include proper navigation and container structure

### 5. **Form Styling**
- Use consistent label styling: `cls="block text-sm font-medium mb-2"`
- Include proper spacing: `cls="mb-4"` between form groups
- Use full utility class chains for inputs and buttons

## Common Issues and Solutions

### Raw HTML Display
**Problem**: Components showing as raw HTML text instead of rendering
**Solution**: 
1. Ensure `ShadHead(tw_cdn=True, theme_handle=True)` is included
2. Avoid problematic layout components
3. Use manual HTML structure with proper CSS classes

### Missing Styles
**Problem**: Components not styled properly
**Solution**:
1. Include complete utility class chains
2. Use theme-aware classes (`text-muted-foreground` not `text-gray-600`)
3. Ensure ShadHead is loading Tailwind CSS

### Button Styling
**Problem**: Buttons don't match other pages
**Solution**: Use exact class strings from working components:
```python
# Copy this exact string for primary buttons
cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
```

## Quick Reference

### Essential Imports
```python
from fasthtml.common import *
from shad4fast import ShadHead, Button, Card
```

### Page Structure Template
```python
def create_page():
    return Html(
        ShadHead(tw_cdn=True, theme_handle=True),
        Body(
            Main(
                Div(
                    # Page content
                    cls="container mx-auto px-4 py-8"
                )
            )
        )
    )
```

### Form Template
```python
Form(
    Div(
        Label("Label:", cls="block text-sm font-medium mb-2"),
        Input(type="text", name="field", cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"),
        cls="mb-4"
    ),
    Button("Submit", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
    method="post",
    action="/endpoint"
)
```

This styling guide reflects the actual implementation used throughout the Nova Prompt Optimizer application.

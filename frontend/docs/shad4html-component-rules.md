# Shad4FastHTML Component Usage Rules

## Overview
This document establishes rules for using **ONLY** Shad4FastHTML components throughout the Nova Prompt Optimizer frontend. We use a pure Shad4FastHTML approach for consistent, professional styling.

## Styling Architecture

### Shad4FastHTML - Use For EVERYTHING:
- **Page layouts** and containers
- **Typography** (headings, paragraphs, text styling)
- **Interactive components** (buttons, inputs, forms)
- **UI widgets** (cards, badges, alerts)
- **Navigation** elements
- **Modal** and dialog components
- **Data display** components
- **Grid systems** and responsive design
- **Spacing** and margins

## Component Rules

### 1. Button Components
**ALWAYS use Shad4FastHTML Button component with proper classes:**

```python
from components.ui import Button

# Primary actions
Button("Submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2")

# Secondary actions  
Button("Cancel", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2")

# Destructive actions
Button("Delete", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-8 px-3 py-1 text-xs")
```

### 2. Layout Components
**Use Shad4FastHTML classes for page structure:**

```python
# Page containers
Div(cls="container mx-auto px-4")  # Shad4FastHTML container

# Grid layouts
Div(cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6")  # Shad4FastHTML grid

# Typography
H1("Page Title", cls="text-3xl font-bold tracking-tight")  # Shad4FastHTML typography
P("Description text", cls="text-muted-foreground")  # Shad4FastHTML text styling
```

### 3. Card Components
**Use Shad4FastHTML Card for content blocks:**

```python
from components.ui import Card

Card(
    header="Card Title",
    content=Div(
        P("Card content", cls="text-sm text-muted-foreground"),
        cls="p-6"  # Shad4FastHTML padding
    ),
    cls="mb-6"  # Shad4FastHTML spacing
)
```

### 4. Form Components
**Use Shad4FastHTML for all form elements:**

```python
# Form container
Form(
    # Form fields
    Input(
        type="text",
        cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    ),
    
    # Button group
    Div(
        Button("Submit", cls="bg-primary text-primary-foreground hover:bg-primary/90"),
        Button("Cancel", cls="border border-input bg-background hover:bg-accent"),
        cls="flex gap-2"  # Shad4FastHTML layout utilities
    ),
    
    cls="space-y-4"  # Shad4FastHTML form spacing
)
```

## Shad4FastHTML Class System

### Core Classes:
- **Backgrounds**: `.bg-background`, `.bg-primary`, `.bg-secondary`, `.bg-muted`
- **Text**: `.text-foreground`, `.text-primary`, `.text-muted-foreground`
- **Borders**: `.border`, `.border-input`, `.border-primary`
- **Spacing**: `.p-4`, `.px-6`, `.py-2`, `.m-4`, `.mx-auto`, `.space-y-4`
- **Layout**: `.flex`, `.grid`, `.container`, `.mx-auto`
- **Typography**: `.text-sm`, `.text-lg`, `.font-medium`, `.font-bold`

### Button Classes:
- **Primary**: `.bg-primary .text-primary-foreground .hover:bg-primary/90`
- **Secondary**: `.bg-secondary .text-secondary-foreground .hover:bg-secondary/80`
- **Outline**: `.border .border-input .bg-background .hover:bg-accent`
- **Destructive**: `.bg-destructive .text-destructive-foreground .hover:bg-destructive/90`

### Interactive States:
- **Focus**: `.focus-visible:outline-none .focus-visible:ring-2 .focus-visible:ring-ring`
- **Hover**: `.hover:bg-accent`, `.hover:text-accent-foreground`
- **Disabled**: `.disabled:pointer-events-none .disabled:opacity-50`

## Implementation Rules

### DO Use Shad4FastHTML For:
✅ ALL page containers and sections  
✅ ALL grid layouts and responsive design  
✅ ALL typography (headings, paragraphs)  
✅ ALL HTML element styling  
✅ ALL page structure  
✅ ALL buttons and interactive elements  
✅ ALL form inputs and controls  
✅ ALL cards and content blocks  
✅ ALL navigation components  
✅ ALL modals and overlays  

### DON'T Use:
❌ PICO CSS classes (removed completely)
❌ Custom CSS classes where Shad4FastHTML exists
❌ Inline styles where Shad4FastHTML classes work
❌ Bootstrap or other CSS frameworks

## Example Page Structure

```python
# Pure Shad4FastHTML structure
Div(
    # Shad4FastHTML container
    Div(
        # Shad4FastHTML typography
        H1("Page Title", cls="text-3xl font-bold tracking-tight mb-6"),
        P("Page description", cls="text-muted-foreground mb-8"),
        
        # Shad4FastHTML grid
        Div(
            # Shad4FastHTML card
            Card(
                header="Section 1",
                content=Div(
                    P("Content", cls="text-sm text-muted-foreground mb-4"),
                    # Shad4FastHTML button
                    Button("Action", cls="bg-primary text-primary-foreground hover:bg-primary/90")
                )
            ),
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"  # Shad4FastHTML grid
        ),
        cls="container mx-auto px-4 py-8"  # Shad4FastHTML container
    )
)
```

## Benefits of Pure Shad4FastHTML Approach

1. **Consistency**: Single design system throughout
2. **Professional**: Modern, clean appearance
3. **Accessibility**: Built-in ARIA attributes and keyboard navigation
4. **Responsive**: Mobile-first responsive design
5. **Maintainable**: No conflicting CSS frameworks
6. **Performance**: Optimized CSS bundle
7. **Developer Experience**: Predictable class names and behavior

## Migration Strategy

1. **Remove PICO CSS** completely from FastHTML headers
2. **Replace all custom styling** with Shad4FastHTML classes
3. **Use Shad4FastHTML components** for all UI elements
4. **Apply consistent class patterns** across all pages
5. **Remove inline styles** in favor of Shad4FastHTML classes

## Enforcement

- ALL components MUST use Shad4FastHTML classes
- NO PICO CSS references allowed
- NO custom CSS where Shad4FastHTML exists
- Code reviews should enforce pure Shad4FastHTML usage
- Automated linting can check for compliance

This pure Shad4FastHTML approach eliminates conflicts and provides a consistent, professional design system!

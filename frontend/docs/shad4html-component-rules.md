# Hybrid Styling Rules: PICO CSS + Shad4FastHTML

## Overview
This document establishes rules for using PICO CSS for layouts and Shad4FastHTML components for interactive elements in the Nova Prompt Optimizer frontend.

## Styling Architecture

### PICO CSS - Use For:
- **Page layouts** and grid systems
- **Typography** (headings, paragraphs, text styling)
- **Container** and section layouts
- **Spacing** and margins between sections
- **Base styling** for HTML elements
- **Responsive** breakpoints and layout

### Shad4FastHTML - Use For:
- **Interactive components** (buttons, inputs, forms)
- **UI widgets** (cards, badges, alerts)
- **Navigation** elements
- **Modal** and dialog components
- **Data display** components

## Component Rules

### 1. Button Components
**ALWAYS use Shad4FastHTML Button component:**

```python
from components.ui import Button

# Primary actions
Button("Submit", variant="default", size="lg")

# Secondary actions  
Button("Cancel", variant="outline", size="lg")

# Destructive actions
Button("Delete", variant="destructive", size="sm")
```

**Shad4FastHTML Button Classes (Applied Automatically):**
```css
/* Primary */
.bg-primary .text-primary-foreground .hover:bg-primary/90

/* Outline */
.border .border-input .bg-background .hover:bg-accent

/* Destructive */
.bg-destructive .text-destructive-foreground .hover:bg-destructive/90
```

### 2. Layout Components
**Use PICO CSS for page structure:**

```python
# Page containers
Div(cls="container")  # PICO container

# Grid layouts
Div(cls="grid")  # PICO grid system

# Typography
H1("Page Title")  # PICO typography
P("Description text")  # PICO paragraph styling
```

### 3. Card Components
**Use Shad4FastHTML Card for content blocks:**

```python
from components.ui import Card

Card(
    header="Card Title",
    content=Div(
        P("Card content with PICO typography"),
        cls="container"  # PICO spacing inside card
    ),
    cls="mb-6"  # Shad4FastHTML spacing
)
```

### 4. Form Components
**Mix both systems appropriately:**

```python
# Form container - PICO
Form(
    # Form fields - Shad4FastHTML
    Input(
        type="text",
        cls="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-black"
    ),
    
    # Button group - Shad4FastHTML
    Div(
        Button("Submit", variant="default"),
        Button("Cancel", variant="outline"),
        cls="flex gap-2"  # Shad4FastHTML layout utilities
    ),
    
    cls="container"  # PICO form container
)
```

## CSS Class Hierarchy

### PICO CSS Classes (Layout & Typography):
- `.container` - Page containers
- `.grid` - Grid layouts
- Typography classes for H1-H6, P, etc.
- Spacing utilities from PICO

### Shad4FastHTML Classes (Components):
- `.bg-primary`, `.text-primary-foreground` - Button styling
- `.border`, `.border-input` - Input styling
- `.rounded-md`, `.shadow-sm` - Component styling
- `.flex`, `.gap-2`, `.mb-6` - Layout utilities

## Implementation Rules

### DO Use PICO For:
✅ Page containers and sections  
✅ Grid layouts and responsive design  
✅ Typography (headings, paragraphs)  
✅ Base HTML element styling  
✅ Overall page structure  

### DO Use Shad4FastHTML For:
✅ All buttons and interactive elements  
✅ Form inputs and controls  
✅ Cards and content blocks  
✅ Navigation components  
✅ Modals and overlays  

### DON'T Mix:
❌ Don't use PICO button classes with Shad4FastHTML buttons  
❌ Don't use Shad4FastHTML layout classes where PICO handles it  
❌ Don't override Shad4FastHTML component styling with custom CSS  

## Example Page Structure

```python
# PICO layout structure
Div(
    # PICO container
    Div(
        # PICO typography
        H1("Page Title"),
        P("Page description"),
        
        # PICO grid
        Div(
            # Shad4FastHTML card
            Card(
                header="Section 1",
                content=Div(
                    P("Content with PICO typography"),
                    # Shad4FastHTML button
                    Button("Action", variant="default")
                )
            ),
            cls="grid"  # PICO grid
        ),
        cls="container"  # PICO container
    )
)
```

## Benefits of Hybrid Approach

1. **PICO CSS Benefits:**
   - Clean, semantic HTML structure
   - Excellent typography and spacing
   - Responsive layout system
   - Minimal CSS footprint

2. **Shad4FastHTML Benefits:**
   - Professional component styling
   - Built-in accessibility features
   - Consistent interactive elements
   - Modern design system

3. **Combined Benefits:**
   - Best of both worlds
   - Clean separation of concerns
   - Maintainable codebase
   - Professional appearance

## Migration Strategy

1. **Keep PICO** for all existing layout and typography
2. **Replace custom buttons** with Shad4FastHTML Button components
3. **Replace custom cards** with Shad4FastHTML Card components
4. **Keep PICO containers** and grid systems
5. **Use Shad4FastHTML** for all new interactive components

This hybrid approach gives us the clean, semantic structure of PICO CSS with the professional, accessible components of Shad4FastHTML!

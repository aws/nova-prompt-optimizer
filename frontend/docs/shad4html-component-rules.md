# Shad4HTML Component Usage Rules

## Overview
This document establishes rules for consistent usage of shad4html (shadcn) components throughout the Nova Prompt Optimizer frontend.

## Component Rules

### 1. Button Components
**ALWAYS use shad4html Button component with proper variants:**

```python
from components.ui import Button

# Primary action buttons
Button("Submit", variant="default", size="lg")

# Secondary action buttons  
Button("Cancel", variant="outline", size="lg")

# Destructive actions
Button("Delete", variant="destructive", size="sm")

# Ghost buttons for subtle actions
Button("Edit", variant="ghost", size="sm")
```

**Available variants:**
- `default` - Primary black button
- `outline` - White button with border
- `destructive` - Red button for delete/remove actions
- `ghost` - Transparent button
- `secondary` - Gray button

**Available sizes:**
- `sm` - Small button
- `default` - Default size
- `lg` - Large button

### 2. Checkbox Components
**ALWAYS use proper checkbox styling:**

```python
Input(
    type="checkbox", 
    name="field_name", 
    value="value",
    id="checkbox-id",
    cls="h-4 w-4 rounded border-gray-300 text-black focus:ring-black focus:ring-2"
)
```

### 3. Card Components
**ALWAYS use Card component with header/content structure:**

```python
from components.ui import Card

Card(
    header="Card Title",
    content=Div(
        # Card content here
    ),
    cls="mb-6"
)
```

### 4. Input Components
**Use consistent input styling:**

```python
Input(
    type="text",
    name="field_name",
    cls="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:border-black"
)
```

### 5. Textarea Components
**Use consistent textarea styling:**

```python
Textarea(
    content,
    name="field_name",
    rows=4,
    cls="w-full p-3 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-black focus:border-black"
)
```

## Layout Rules

### Button Layouts
**For action button pairs (75%/25% split):**

```python
Div(
    Button("Primary Action", variant="default", size="lg", cls="flex-1 mr-2"),
    Button("Cancel", variant="outline", size="lg", cls="w-1/4"),
    cls="flex"
)
```

**For equal button pairs:**

```python
Div(
    Button("Action 1", variant="default", size="lg", cls="flex-1 mr-2"),
    Button("Action 2", variant="outline", size="lg", cls="flex-1"),
    cls="flex"
)
```

### Card Containers
**Always wrap action buttons in Card containers:**

```python
Card(
    header="Actions",
    content=Div(
        # Buttons here
        cls="flex"
    ),
    cls="mb-6"
)
```

## Color Scheme Rules

### Primary Colors
- **Black**: `#000000` - Primary actions, text
- **White**: `#ffffff` - Backgrounds, secondary actions
- **Gray-50**: `#f9fafb` - Light backgrounds
- **Gray-300**: `#d1d5db` - Borders
- **Gray-600**: `#4b5563` - Secondary text

### Focus States
- **Focus ring**: `focus:ring-2 focus:ring-black focus:border-black`
- **Hover states**: Use shad4html built-in hover states

## Implementation Checklist

### Before Adding New Components:
- [ ] Check if shad4html component exists
- [ ] Use proper variant and size
- [ ] Apply consistent styling classes
- [ ] Test focus and hover states
- [ ] Ensure accessibility compliance

### Code Review Checklist:
- [ ] All buttons use Button component with variants
- [ ] All checkboxes use proper styling
- [ ] All cards use Card component structure
- [ ] Consistent spacing with mb-6, mr-2, etc.
- [ ] Proper flex layouts for button groups
- [ ] Focus states implemented correctly

## Migration Guide

### From Custom Buttons to Shad4HTML:
```python
# OLD - Custom styling
Button("Submit", cls="bg-black text-white px-6 py-2 rounded-md hover:bg-gray-800")

# NEW - Shad4HTML
Button("Submit", variant="default", size="lg")
```

### From Custom Checkboxes to Shad4HTML:
```python
# OLD - Basic checkbox
Input(type="checkbox", cls="mr-2")

# NEW - Shad4HTML styled
Input(type="checkbox", cls="h-4 w-4 rounded border-gray-300 text-black focus:ring-black focus:ring-2")
```

## Benefits

1. **Consistency**: All components follow the same design system
2. **Accessibility**: Built-in ARIA attributes and keyboard navigation
3. **Maintainability**: Centralized styling and behavior
4. **Performance**: Optimized CSS and JavaScript
5. **Developer Experience**: Predictable API and documentation

## Enforcement

- All new components MUST use shad4html variants
- Existing components should be migrated during updates
- Code reviews should enforce these rules
- Automated linting can check for compliance

## Resources

- [Shad4FastHTML Documentation](https://www.shad4fasthtml.com/)
- [Button Component](https://www.shad4fasthtml.com/components/button)
- [Checkbox Component](https://www.shad4fasthtml.com/components/checkbox)
- [Card Component](https://www.shad4fasthtml.com/components/card)

"""
UI Components for Nova Prompt Optimizer using Shad4FastHTML patterns
Clean black and white design system
"""

from fasthtml.common import *
from typing import Optional, List, Dict, Any

def Button(
    content: Any,
    variant: str = "primary",
    size: str = "default",
    disabled: bool = False,
    **kwargs
) -> Any:
    """
    Create a button component following Shad4FastHTML patterns
    
    Args:
        content: Button content (text or elements)
        variant: Button style variant (primary, secondary, outline, ghost)
        size: Button size (sm, default, lg)
        disabled: Whether button is disabled
        **kwargs: Additional HTML attributes
    
    Returns:
        Button element
    """
    
    # Build Shad4FastHTML CSS classes
    base_classes = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    
    # Variant classes
    variant_classes = {
        "primary": "bg-primary text-primary-foreground hover:bg-primary/90",
        "secondary": "bg-secondary text-secondary-foreground hover:bg-secondary/80", 
        "outline": "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        "ghost": "hover:bg-accent hover:text-accent-foreground",
        "destructive": "bg-destructive text-destructive-foreground hover:bg-destructive/90"
    }
    
    # Size classes
    size_classes = {
        "sm": "h-8 px-3 py-1 text-xs",
        "default": "h-10 px-4 py-2",
        "lg": "h-11 px-8"
    }
    
    variant_class = variant_classes.get(variant, variant_classes["primary"])
    size_class = size_classes.get(size, size_classes["default"])
    
    classes = f"{base_classes} {variant_class} {size_class}"
    
    # Merge classes with any existing cls
    existing_cls = kwargs.get("cls", "")
    final_cls = f"{classes} {existing_cls}".strip()
    
    # Set up attributes
    attrs = {
        "cls": final_cls,
        "disabled": disabled,
        **kwargs
    }
    
    # Use the FastHTML Button element
    from fasthtml.common import Button as HTMLButton
    return HTMLButton(content, **attrs)

def Card(
    content: Any = None,
    header: Any = None,
    footer: Any = None,
    nested: bool = False,
    **kwargs
) -> Any:
    """
    Create a card component following Shad4FastHTML patterns
    
    Args:
        content: Main card content
        header: Optional card header
        footer: Optional card footer
        nested: Whether this is a nested card (100% width)
        **kwargs: Additional HTML attributes
    
    Returns:
        Card element (Article)
    """
    
    card_content = []
    
    if header:
        card_content.append(
            Header(header, cls="card-header")
        )
    
    if content:
        card_content.append(
            Div(content, cls="card-content")
        )
    
    if footer:
        card_content.append(
            Footer(footer, cls="card-footer")
        )
    
    # Merge classes
    existing_cls = kwargs.get("cls", "")
    card_cls = "card-nested" if nested else "card"
    final_cls = f"{card_cls} {existing_cls}".strip()
    
    return Article(
        *card_content,
        cls=final_cls,
        **{k: v for k, v in kwargs.items() if k != "cls"}
    )

def CardContainer(*cards, **kwargs):
    """
    Create a main container card that matches navbar width with nested cards inside
    
    Args:
        *cards: Nested card components
        **kwargs: Additional HTML attributes
    
    Returns:
        Container div with nested cards
    """
    existing_cls = kwargs.get("cls", "")
    final_cls = f"card-main-container {existing_cls}".strip()
    
    return Div(
        *cards,
        cls=final_cls,
        **{k: v for k, v in kwargs.items() if k != "cls"}
    )

def Select(*options, **kwargs):
    """Create a select dropdown"""
    from fasthtml.common import Select as HTMLSelect
    return HTMLSelect(*options, **kwargs)

def Option(text, **kwargs):
    """Create an option element"""
    from fasthtml.common import Option as HTMLOption
    return HTMLOption(text, **kwargs)

def Textarea(
    placeholder: str = "",
    rows: int = 4,
    disabled: bool = False,
    required: bool = False,
    **kwargs
) -> Any:
    """
    Create a textarea component following Shad4FastHTML patterns
    
    Args:
        placeholder: Placeholder text
        rows: Number of rows
        disabled: Whether textarea is disabled
        required: Whether textarea is required
        **kwargs: Additional HTML attributes
    
    Returns:
        Textarea element
    """
    
    # Build CSS classes
    base_classes = "textarea"
    disabled_class = "textarea-disabled" if disabled else ""
    
    classes = " ".join(filter(None, [base_classes, disabled_class]))
    
    # Merge classes
    existing_cls = kwargs.get("cls", "")
    final_cls = f"{classes} {existing_cls}".strip()
    
    attrs = {
        "cls": final_cls,
        "placeholder": placeholder,
        "rows": rows,
        "disabled": disabled,
        "required": required,
        **kwargs
    }
    
    # Use the FastHTML Textarea element
    from fasthtml.common import Textarea as HTMLTextarea
    return HTMLTextarea(**attrs)

def Input(
    type: str = "text",
    placeholder: str = "",
    disabled: bool = False,
    required: bool = False,
    **kwargs
) -> Any:
    """
    Create an input component following Shad4FastHTML patterns
    
    Args:
        type: Input type
        placeholder: Placeholder text
        disabled: Whether input is disabled
        required: Whether input is required
        **kwargs: Additional HTML attributes
    
    Returns:
        Input element
    """
    
    # Build CSS classes
    base_classes = "input"
    disabled_class = "input-disabled" if disabled else ""
    
    classes = " ".join(filter(None, [base_classes, disabled_class]))
    
    # Merge classes
    existing_cls = kwargs.get("cls", "")
    final_cls = f"{classes} {existing_cls}".strip()
    
    attrs = {
        "cls": final_cls,
        "type": type,
        "placeholder": placeholder,
        "disabled": disabled,
        "required": required,
        **kwargs
    }
    
    # Use the FastHTML Input element
    from fasthtml.common import Input as HTMLInput
    return HTMLInput(**attrs)

def Label(
    content: Any,
    for_id: Optional[str] = None,
    required: bool = False,
    **kwargs
) -> Any:
    """
    Create a label component following Shad4FastHTML patterns
    
    Args:
        content: Label content
        for_id: ID of associated form element
        required: Whether the associated field is required
        **kwargs: Additional HTML attributes
    
    Returns:
        Label element
    """
    
    label_content = [content]
    
    if required:
        label_content.append(
            Span(" *", cls="label-required")
        )
    
    attrs = {
        "cls": "label",
        **kwargs
    }
    
    if for_id:
        attrs["for"] = for_id
    
    # Use the FastHTML Label element
    from fasthtml.common import Label as HTMLLabel
    return HTMLLabel(*label_content, **attrs)

def FormField(
    label_text: str,
    input_element: Any,
    help_text: Optional[str] = None,
    error_text: Optional[str] = None,
    required: bool = False,
    **kwargs
) -> Any:
    """
    Create a complete form field with label, input, and help text
    
    Args:
        label_text: Label text
        input_element: Input/textarea element
        help_text: Optional help text
        error_text: Optional error message
        required: Whether field is required
        **kwargs: Additional HTML attributes
    
    Returns:
        Form field container
    """
    
    field_id = kwargs.get("id", f"field-{hash(label_text)}")
    
    field_content = [
        Label(label_text, for_id=field_id, required=required),
        input_element
    ]
    
    if help_text:
        field_content.append(
            P(help_text, cls="field-help")
        )
    
    if error_text:
        field_content.append(
            P(error_text, cls="field-error")
        )
    
    return Div(
        *field_content,
        cls="form-field",
        **kwargs
    )

def Badge(
    content: Any,
    variant: str = "default",
    **kwargs
) -> Any:
    """
    Create a badge component
    
    Args:
        content: Badge content
        variant: Badge variant (default, success, warning, error)
        **kwargs: Additional HTML attributes
    
    Returns:
        Badge element
    """
    
    classes = f"badge badge-{variant}"
    existing_cls = kwargs.get("cls", "")
    final_cls = f"{classes} {existing_cls}".strip()
    
    return Span(
        content,
        cls=final_cls,
        **{k: v for k, v in kwargs.items() if k != "cls"}
    )

def Alert(
    content: Any,
    variant: str = "info",
    title: Optional[str] = None,
    dismissible: bool = False,
    **kwargs
) -> Any:
    """
    Create an alert component
    
    Args:
        content: Alert content
        variant: Alert variant (info, success, warning, error)
        title: Optional alert title
        dismissible: Whether alert can be dismissed
        **kwargs: Additional HTML attributes
    
    Returns:
        Alert element
    """
    
    alert_content = []
    
    if title:
        alert_content.append(
            H4(title, cls="alert-title")
        )
    
    alert_content.append(
        Div(content, cls="alert-content")
    )
    
    if dismissible:
        alert_content.append(
            Button(
                "×",
                cls="alert-dismiss",
                **{"aria-label": "Close alert"}
            )
        )
    
    classes = f"alert alert-{variant}"
    existing_cls = kwargs.get("cls", "")
    final_cls = f"{classes} {existing_cls}".strip()
    
    return Div(
        *alert_content,
        cls=final_cls,
        role="alert",
        **{k: v for k, v in kwargs.items() if k != "cls"}
    )

def create_ui_styles():
    """
    Create CSS styles for UI components (Shad4FastHTML theme)
    
    Returns:
        Empty style - Shad4FastHTML handles all styling
    """
    return Style("")

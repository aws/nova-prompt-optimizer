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
    
    # Build CSS classes
    base_classes = "btn"
    variant_class = f"btn-{variant}"
    size_class = f"btn-{size}" if size != "default" else ""
    disabled_class = "btn-disabled" if disabled else ""
    
    classes = " ".join(filter(None, [base_classes, variant_class, size_class, disabled_class]))
    
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
    return Select(*options, **kwargs)

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
    Create CSS styles for UI components (Black & White theme)
    
    Returns:
        Style element with UI component CSS
    """
    return Style("""
        /* Button Components */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 8px 16px;
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1.25;
            border-radius: 6px;
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
            white-space: nowrap;
        }
        
        .btn:disabled,
        .btn-disabled {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }
        
        /* Button Variants */
        .btn-primary {
            background: #000000;
            color: #ffffff;
            border-color: #000000;
        }
        
        .btn-primary:hover:not(:disabled) {
            background: #333333;
            border-color: #333333;
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #000000;
            border-color: #e5e5e5;
        }
        
        .btn-secondary:hover:not(:disabled) {
            background: #e9ecef;
            border-color: #d1d5db;
        }
        
        .btn-outline {
            background: transparent;
            color: #000000;
            border-color: #e5e5e5;
        }
        
        .btn-outline:hover:not(:disabled) {
            background: #f8f9fa;
            border-color: #d1d5db;
        }
        
        .btn-ghost {
            background: transparent;
            color: #000000;
            border-color: transparent;
        }
        
        .btn-ghost:hover:not(:disabled) {
            background: #f8f9fa;
        }
        
        /* Button Sizes */
        .btn-sm {
            padding: 4px 12px;
            font-size: 0.75rem;
        }
        
        .btn-lg {
            padding: 12px 24px;
            font-size: 1rem;
        }
        
        /* Card Components - Aligned with navbar layout */
        .card {
            background: var(--bg-primary, #ffffff);
            border: 1px solid var(--border-color, #e5e5e5);
            border-radius: 8px;
            overflow: hidden;
            transition: box-shadow 0.15s ease, background-color 0.3s ease, border-color 0.3s ease;
            max-width: 1200px; /* Match navbar max-width */
            margin: 0 auto; /* Center align like navbar */
        }
        
        /* Container card that matches navbar width */
        .card-main-container {
            max-width: 800px; /* Match nav-tab-list max-width */
            width: 100%;
            margin: 0 auto;
            background: var(--bg-primary, #ffffff);
            border: 1px solid var(--border-color, #e5e5e5);
            border-radius: 8px;
            overflow: hidden;
            transition: box-shadow 0.15s ease, background-color 0.3s ease, border-color 0.3s ease;
            padding: 1.5rem;
        }
        
        /* Nested cards inside container - 100% width */
        .card-nested {
            width: 100%;
            margin: 0 0 1.5rem 0; /* Only bottom margin */
            background: var(--bg-secondary, #f8f9fa);
            border: 1px solid var(--border-color, #e5e5e5);
            border-radius: 6px;
            overflow: hidden;
            transition: box-shadow 0.15s ease, background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .card-nested:last-child {
            margin-bottom: 0; /* Remove margin from last nested card */
        }
        
        /* Card container for consistent spacing */
        .card-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem; /* Match navbar margins */
        }
        
        .card:hover,
        .card-main-container:hover {
            box-shadow: 0 4px 12px var(--shadow-hover, rgba(0, 0, 0, 0.1));
        }
        
        .card-nested:hover {
            box-shadow: 0 2px 8px var(--shadow-color, rgba(0, 0, 0, 0.08));
        }
        
        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color, #e5e5e5);
            background: var(--bg-secondary, #f8f9fa);
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .card-content {
            padding: 20px;
        }
        
        .card-footer {
            padding: 16px 20px;
            border-top: 1px solid var(--border-color, #e5e5e5);
            background: var(--bg-secondary, #f8f9fa);
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        /* Input Components */
        .input,
        .textarea {
            width: 100%;
            padding: 8px 12px;
            font-size: 0.875rem;
            line-height: 1.25;
            color: #000000;
            background: #ffffff;
            border: 1px solid #e5e5e5;
            border-radius: 6px;
            transition: all 0.15s ease;
        }
        
        .input:focus,
        .textarea:focus {
            outline: none;
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
        }
        
        .input::placeholder,
        .textarea::placeholder {
            color: #9ca3af;
        }
        
        .input:disabled,
        .textarea:disabled,
        .input-disabled,
        .textarea-disabled {
            background: #f8f9fa;
            color: #6b7280;
            cursor: not-allowed;
        }
        
        .textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        /* Label Components */
        .label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: #000000;
            margin-bottom: 4px;
        }
        
        .label-required {
            color: #dc2626;
        }
        
        /* Form Field Components */
        .form-field {
            margin-bottom: 16px;
        }
        
        .field-help {
            margin-top: 4px;
            font-size: 0.75rem;
            color: #6b7280;
        }
        
        .field-error {
            margin-top: 4px;
            font-size: 0.75rem;
            color: #dc2626;
        }
        
        /* Badge Components */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 500;
            border-radius: 12px;
            white-space: nowrap;
        }
        
        .badge-default {
            background: #f8f9fa;
            color: #000000;
        }
        
        .badge-success {
            background: #dcfce7;
            color: #166534;
        }
        
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-error {
            background: #fecaca;
            color: #991b1b;
        }
        
        /* Alert Components */
        .alert {
            padding: 16px;
            border-radius: 8px;
            border: 1px solid;
            margin-bottom: 16px;
            position: relative;
        }
        
        .alert-title {
            margin: 0 0 8px 0;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .alert-content {
            font-size: 0.875rem;
            line-height: 1.5;
        }
        
        .alert-dismiss {
            position: absolute;
            top: 12px;
            right: 12px;
            background: transparent;
            border: none;
            font-size: 1.25rem;
            cursor: pointer;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .alert-info {
            background: #f0f9ff;
            border-color: #bae6fd;
            color: #0c4a6e;
        }
        
        .alert-success {
            background: #f0fdf4;
            border-color: #bbf7d0;
            color: #166534;
        }
        
        .alert-warning {
            background: #fffbeb;
            border-color: #fed7aa;
            color: #92400e;
        }
        
        .alert-error {
            background: #fef2f2;
            border-color: #fecaca;
            color: #991b1b;
        }
        
        /* Focus States for Accessibility */
        .btn:focus-visible,
        .input:focus-visible,
        .textarea:focus-visible {
            outline: 2px solid #000000;
            outline-offset: 2px;
        }
        
        /* Responsive Design */
        @media (max-width: 1024px) {
            .card-container {
                padding: 0 1rem; /* Match navbar responsive margins */
            }
            
            .card-main-container {
                max-width: 700px; /* Match navbar responsive width */
            }
        }
        
        @media (max-width: 768px) {
            .card-container {
                padding: 0 0.5rem; /* Match navbar responsive margins */
            }
            
            .card-main-container {
                max-width: 500px; /* Match navbar responsive width */
                padding: 1rem;
            }
            
            .card-header,
            .card-content,
            .card-footer {
                padding: 12px 16px;
            }
            
            .btn {
                padding: 6px 12px;
                font-size: 0.8rem;
            }
            
            .btn-lg {
                padding: 10px 20px;
                font-size: 0.9rem;
            }
        }
        
        @media (max-width: 480px) {
            .card-container {
                padding: 0 0.25rem; /* Match navbar responsive margins */
            }
            
            .card-main-container {
                padding: 0.75rem;
            }
            
            .card-header,
            .card-content,
            .card-footer {
                padding: 10px 14px;
            }
        }
    """)

"""
UI Components for Optimized Prompt Builder
"""

from fasthtml.common import *
from typing import Dict, List, Any, Optional
from services.prompt_builder import OptimizedPromptBuilder, ValidationResult


def builder_form_section(builder_data: Optional[Dict[str, Any]] = None) -> Div:
    """Main prompt builder form section"""
    data = builder_data or {}
    
    return Div(
        # Task Section
        task_input_section(data.get("task", "")),
        
        # Context Section  
        context_builder_section(data.get("context", [])),
        
        # Instructions Section
        instructions_builder_section(data.get("instructions", [])),
        
        # Response Format Section
        response_format_section(data.get("response_format", [])),
        
        # Variables Section
        variables_manager_section(data.get("variables", [])),
        
        # Action Buttons
        Div(
            Button("Preview Prompt", 
                   type="button", 
                   onclick="previewPrompt()",
                   cls="px-4 py-2 text-sm font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700 mr-2"),
            Button("Validate", 
                   type="button", 
                   onclick="validatePrompt()",
                   cls="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 mr-2"),
            Button("Build Prompt", 
                   type="submit",
                   cls="px-4 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90"),
            cls="flex gap-2 mt-6"
        ),
        
        id="prompt-builder-form",
        cls="space-y-6"
    )


def task_input_section(task: str = "") -> Div:
    """Task description input section"""
    return Div(
        Label("Task Description", cls="block text-sm font-medium mb-2"),
        Textarea(
            task,
            name="task",
            id="task-input",
            placeholder="Describe what you want the AI to accomplish (e.g., 'Analyze customer feedback sentiment')",
            required=True,
            rows="3",
            cls="w-full p-2 border border-input rounded-md"
        ),
        P("Clear, specific task descriptions lead to better prompts", 
          cls="text-sm text-muted-foreground mt-1"),
        cls="mb-4"
    )


def context_builder_section(context_items: List[str] = None) -> Div:
    """Context items builder section"""
    context_items = context_items or []
    
    context_list = Div(
        *[context_item_row(i, item) for i, item in enumerate(context_items)],
        id="context-list",
        cls="space-y-2"
    )
    
    return Div(
        Label("Context Information", cls="block text-sm font-medium mb-2"),
        P("Provide background information that helps the AI understand the task", 
          cls="text-sm text-muted-foreground mb-3"),
        
        context_list,
        
        Button("+ Add Context", 
               type="button", 
               onclick="addContextItem()",
               cls="mt-2 px-3 py-1 text-sm border border-input rounded-md hover:bg-accent"),
        
        # Hidden template for new context items
        Div(
            context_item_row(-1, "", template=True),
            id="context-template",
            style="display: none;"
        ),
        
        cls="mb-6"
    )


def context_item_row(index: int, value: str = "", template: bool = False) -> Div:
    """Individual context item row"""
    return Div(
        Div(
            Input(
                type="text",
                name=f"context_{index}" if not template else "context_template",
                value=value,
                placeholder="Enter context information (e.g., 'Customer support emails and chat logs')",
                cls="flex-1 p-2 border border-input rounded-md"
            ),
            Button("Remove", 
                   type="button", 
                   onclick=f"removeContextItem({index})" if not template else "removeContextItem(this)",
                   cls="ml-2 px-2 py-1 text-sm text-destructive border border-destructive rounded-md hover:bg-destructive/10"),
            cls="flex items-center"
        ),
        cls="context-item" + (" template" if template else ""),
        **{"data-index": index} if not template else {}
    )


def instructions_builder_section(instructions: List[str] = None) -> Div:
    """Instructions builder section"""
    instructions = instructions or []
    
    instructions_list = Div(
        *[instruction_item_row(i, item) for i, item in enumerate(instructions)],
        id="instructions-list",
        cls="space-y-2"
    )
    
    return Div(
        Label("Instructions", cls="block text-sm font-medium mb-2"),
        P("Specific rules and requirements for the AI. Use strong directive language (MUST, DO NOT)", 
          cls="text-sm text-muted-foreground mb-3"),
        
        instructions_list,
        
        Button("+ Add Instruction", 
               type="button", 
               onclick="addInstruction()",
               cls="mt-2 px-3 py-1 text-sm border border-input rounded-md hover:bg-accent"),
        
        # Hidden template
        Div(
            instruction_item_row(-1, "", template=True),
            id="instruction-template",
            cls="hidden"
        ),
        
        cls="mb-4"
    )


def instruction_item_row(index: int, value: str = "", template: bool = False) -> Div:
    """Individual instruction item row"""
    return Div(
        Div(
            Input(
                type="text",
                name=f"instruction_{index}" if not template else "instruction_template",
                value=value,
                placeholder="Enter instruction (e.g., 'MUST classify sentiment as positive, negative, or neutral')",
                cls="flex-1 p-2 border border-input rounded-md"
            ),
            Button("Remove", 
                   type="button", 
                   onclick=f"removeInstruction({index})" if not template else "removeInstruction(this)",
                   cls="ml-2 px-2 py-1 text-sm text-destructive border border-destructive rounded-md hover:bg-destructive/10"),
            cls="flex items-center"
        ),
        cls="instruction-item" + (" template" if template else ""),
        **{"data-index": index} if not template else {}
    )


def response_format_section(formats: List[str] = None) -> Div:
    """Response format builder section"""
    formats = formats or []
    
    format_list = Div(
        *[format_item_row(i, item) for i, item in enumerate(formats)],
        id="format-list",
        cls="space-y-2"
    )
    
    return Div(
        Label("Response Format", cls="block text-sm font-medium mb-2"),
        P("Specify how the AI should structure its response", 
          cls="text-sm text-muted-foreground mb-3"),
        
        format_list,
        
        Button("+ Add Format Requirement", 
               type="button", 
               onclick="addFormatItem()",
               cls="mt-2 px-3 py-1 text-sm border border-input rounded-md hover:bg-accent"),
        
        # Hidden template
        Div(
            format_item_row(-1, "", template=True),
            id="format-template",
            cls="hidden"
        ),
        
        cls="mb-4"
    )


def format_item_row(index: int, value: str = "", template: bool = False) -> Div:
    """Individual format item row"""
    return Div(
        Div(
            Input(
                type="text",
                name=f"format_{index}" if not template else "format_template",
                value=value,
                placeholder="Enter format requirement (e.g., 'JSON format with sentiment and confidence fields')",
                cls="flex-1 p-2 border border-input rounded-md"
            ),
            Button("Remove", 
                   type="button", 
                   onclick=f"removeFormatItem({index})" if not template else "removeFormatItem(this)",
                   cls="ml-2 px-2 py-1 text-sm text-destructive border border-destructive rounded-md hover:bg-destructive/10"),
            cls="flex items-center"
        ),
        cls="format-item" + (" template" if template else ""),
        **{"data-index": index} if not template else {}
    )


def variables_manager_section(variables: List[str] = None) -> Div:
    """Variables manager section"""
    variables = variables or []
    
    variables_list = Div(
        *[variable_item_row(i, var) for i, var in enumerate(variables)],
        id="variables-list",
        cls="space-y-2"
    )
    
    return Div(
        Label("Template Variables", cls="block text-sm font-medium mb-2"),
        P("Variables that will be replaced with actual values when using the prompt", 
          cls="text-sm text-muted-foreground mb-3"),
        
        variables_list,
        
        Button("+ Add Variable", 
               type="button", 
               onclick="addVariable()",
               cls="mt-2 px-3 py-1 text-sm border border-input rounded-md hover:bg-accent"),
        
        # Hidden template
        Div(
            variable_item_row(-1, "", template=True),
            id="variable-template",
            cls="hidden"
        ),
        
        cls="mb-4"
    )


def variable_item_row(index: int, value: str = "", template: bool = False) -> Div:
    """Individual variable item row"""
    return Div(
        Div(
            Input(
                type="text",
                name=f"variable_{index}" if not template else "variable_template",
                value=value,
                placeholder="Enter variable name (e.g., 'customer_feedback', 'product_name')",
                cls="flex-1 p-2 border border-input rounded-md"
            ),
            Button("Remove", 
                   type="button", 
                   onclick=f"removeVariable({index})" if not template else "removeVariable(this)",
                   cls="ml-2 px-2 py-1 text-sm text-destructive border border-destructive rounded-md hover:bg-destructive/10"),
            cls="flex items-center"
        ),
        cls="variable-item" + (" template" if template else ""),
        **{"data-index": index} if not template else {}
    )


def preview_panel(system_prompt: str = "", user_prompt: str = "") -> Div:
    """Preview panel for generated prompts"""
    return Div(
        H3("Generated Prompt Preview", cls="text-lg font-medium text-gray-900 mb-4"),
        
        # System Prompt Preview
        Div(
            H4("System Prompt", cls="text-md font-medium text-gray-700 mb-2"),
            Textarea(
                system_prompt,
                readonly=True,
                rows="10",
                cls="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md font-mono text-sm"
            ),
            cls="mb-4"
        ),
        
        # User Prompt Preview
        Div(
            H4("User Prompt", cls="text-md font-medium text-gray-700 mb-2"),
            Textarea(
                user_prompt,
                readonly=True,
                rows="5",
                cls="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md font-mono text-sm"
            ),
            cls="mb-4"
        ),
        
        id="preview-panel",
        cls="bg-white p-6 border border-gray-200 rounded-lg"
    )


def validation_panel(validation: Optional[ValidationResult] = None) -> Div:
    """Validation results panel"""
    if not validation:
        return Div(
            P("Click 'Validate' to check your prompt against Nova best practices", 
              cls="text-gray-500 text-center py-8"),
            id="validation-panel",
            cls="bg-white p-6 border border-gray-200 rounded-lg"
        )
    
    # Status indicator
    if validation.is_valid:
        status_div = Div(
            Span("✅", cls="text-green-500 text-xl mr-2"),
            Span("Prompt is valid and ready to build!", cls="text-green-700 font-medium"),
            cls="flex items-center mb-4 p-3 bg-green-50 border border-green-200 rounded-md"
        )
    else:
        status_div = Div(
            Span("⚠️", cls="text-yellow-500 text-xl mr-2"),
            Span(f"{len(validation.issues)} issues found", cls="text-yellow-700 font-medium"),
            cls="flex items-center mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md"
        )
    
    # Issues section
    issues_section = Div()
    if validation.issues:
        issues_section = Div(
            H4("Issues to Fix", cls="text-md font-medium text-red-700 mb-2"),
            Ul(
                *[Li(issue, cls="text-red-600") for issue in validation.issues],
                cls="list-disc list-inside space-y-1 mb-4"
            )
        )
    
    # Suggestions section
    suggestions_section = Div()
    if validation.suggestions:
        suggestions_section = Div(
            H4("Suggestions for Improvement", cls="text-md font-medium text-blue-700 mb-2"),
            Ul(
                *[Li(suggestion, cls="text-blue-600") for suggestion in validation.suggestions],
                cls="list-disc list-inside space-y-1 mb-4"
            )
        )
    
    # Best practices checklist
    practices_section = Div()
    if validation.best_practices:
        practices_items = []
        for practice, passed in validation.best_practices.items():
            icon = "✅" if passed else "❌"
            color = "text-green-600" if passed else "text-red-600"
            label = practice.replace("_", " ").title()
            practices_items.append(
                Li(
                    Span(icon, cls="mr-2"),
                    Span(label, cls=color),
                    cls="flex items-center"
                )
            )
        
        practices_section = Div(
            H4("Best Practices Check", cls="text-md font-medium text-gray-700 mb-2"),
            Ul(*practices_items, cls="space-y-1")
        )
    
    return Div(
        H3("Validation Results", cls="text-lg font-medium text-gray-900 mb-4"),
        status_div,
        issues_section,
        suggestions_section,
        practices_section,
        id="validation-panel",
        cls="bg-white p-6 border border-gray-200 rounded-lg"
    )


def template_selector(templates: List[Dict[str, Any]] = None) -> Div:
    """Template selector dropdown"""
    templates = templates or []
    
    options = [Option("Select a template...", value="", selected=True)]
    for template in templates:
        options.append(
            Option(
                f"{template['name']} - {template.get('description', 'No description')[:50]}...",
                value=template['id']
            )
        )
    
    return Div(
        Label("Load from Template", cls="block text-sm font-medium mb-2"),
        Select(
            *options,
            name="template_id",
            id="template-selector",
            onchange="loadTemplate(this.value)",
            cls="w-full p-2 border border-input rounded-md"
        ),
        cls="mb-4"
    )


def save_template_form() -> Div:
    """Save template form"""
    return Div(
        H3("Save as Template", cls="text-lg font-medium text-gray-900 mb-4"),
        
        Div(
            Label("Template Name", cls="block text-sm font-medium text-gray-700 mb-2"),
            Input(
                type="text",
                name="template_name",
                placeholder="Enter template name",
                required=True,
                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ),
            cls="mb-4"
        ),
        
        Div(
            Label("Description", cls="block text-sm font-medium text-gray-700 mb-2"),
            Textarea(
                name="template_description",
                placeholder="Optional description of this template",
                rows="3",
                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ),
            cls="mb-4"
        ),
        
        Div(
            Button("Save Template", 
                   type="button",
                   onclick="saveTemplate()",
                   cls="px-4 py-2 text-sm font-medium rounded-md bg-green-600 text-white hover:bg-green-700 mr-2"),
            Button("Cancel", 
                   type="button",
                   onclick="hideSaveTemplateForm()",
                   cls="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"),
            cls="flex gap-2"
        ),
        
        id="save-template-form",
        cls="bg-white p-6 border border-gray-200 rounded-lg",
        style="display: none;"
    )

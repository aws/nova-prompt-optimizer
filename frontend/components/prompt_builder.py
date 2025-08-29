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
        # Instructions Toggle
        Div(
            Div(
                H3("Nova SDK Optimized Prompt Builder", cls="text-lg font-semibold text-orange-700 mb-2"),
                P("This builder integrates with Nova's NovaPromptOptimizer and TextPromptAdapter for proven optimization results", 
                  cls="text-sm text-orange-600 mb-4"),
            ),
            Button("Show/Hide Instructions", 
                   type="button",
                   onclick="toggleInstructions()",
                   cls="mb-4 px-3 py-2 text-sm font-medium rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"),
            cls="mb-6"
        ),
        
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


def create_help_section(field_name: str, instruction: str, reasoning: str, example: str) -> Div:
    """Create a toggleable help section for a field"""
    return Div(
        Div(
            Div(
                H4("Nova SDK Best Practice", cls="text-sm font-semibold text-orange-700 mb-2"),
                P("This field follows proven Nova optimization patterns from the SDK", cls="text-sm text-orange-600 mb-3"),
                
                H4("Instructions", cls="text-sm font-semibold text-blue-700 mb-2"),
                P(instruction, cls="text-sm text-gray-700 mb-3"),
                
                H4("Why This Matters", cls="text-sm font-semibold text-green-700 mb-2"),
                P(reasoning, cls="text-sm text-gray-700 mb-3"),
                
                H4("Example", cls="text-sm font-semibold text-purple-700 mb-2"),
                Div(
                    Code(example, cls="text-sm"),
                    cls="bg-gray-50 p-3 rounded-md border"
                )
            ),
            cls="bg-gradient-to-r from-orange-50 to-blue-50 border border-orange-200 rounded-md p-4 mt-2"
        ),
        id=f"{field_name}-help",
        cls="help-section",
        style="display: none;"
    )


def task_input_section(task: str = "") -> Div:
    """Task description input section"""
    return Div(
        Label("Task Description", cls="block text-sm font-medium mb-2"),
        
        create_help_section(
            "task",
            "Clearly describe what you want the AI to accomplish. This creates the foundation for Nova's TextPromptAdapter and NovaPromptOptimizer. Be specific about the action, input type, and desired outcome.",
            "Nova SDK's optimization engine works best with well-defined tasks. Clear task definitions improve optimization results by giving the NovaPromptOptimizer better baseline understanding and evaluation targets.",
            "Nova Optimized: 'Analyze customer support emails and classify them as urgent, normal, or low priority based on sentiment and keywords'\nPoor for optimization: 'Look at emails and categorize them'\n\nNova Pattern: Action verb + specific input + measurable output"
        ),
        
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
        
        create_help_section(
            "context",
            "Add background information, constraints, or domain-specific knowledge that helps the AI understand the situation better. Each context item should provide relevant details.",
            "Context helps the AI make better decisions by providing domain knowledge, constraints, and background information. Good context reduces ambiguity and improves accuracy.",
            "Examples:\n• 'You are a financial advisor with 10 years of experience'\n• 'The company follows strict GDPR compliance requirements'\n• 'Responses should be appropriate for a technical audience'\n• 'Consider seasonal trends in retail data'"
        ),
        
        context_list,
        
        Button("+ Add Context", 
               type="button", 
               onclick="addContextItem()",
               cls="mt-2 px-3 py-1 text-sm border border-dashed border-gray-300 rounded-md hover:border-gray-400"),
        
        P("Context helps the AI understand the domain and constraints", 
          cls="text-sm text-muted-foreground mt-2"),
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
        
        create_help_section(
            "context",
            "Add background information, constraints, or domain-specific knowledge that helps the AI understand the situation better. Each context item should provide relevant details.",
            "Context helps the AI make better decisions by providing domain knowledge, constraints, and background information. Good context reduces ambiguity and improves accuracy.",
            "Examples:\n• 'You are a financial advisor with 10 years of experience'\n• 'The company follows strict GDPR compliance requirements'\n• 'Responses should be appropriate for a technical audience'\n• 'Consider seasonal trends in retail data'"
        ),
        
        context_list,
        
        Button("+ Add Context", 
               type="button", 
               onclick="addContextItem()",
               cls="mt-2 px-3 py-1 text-sm border border-dashed border-gray-300 rounded-md hover:border-gray-400"),
        
        P("Context helps the AI understand the domain and constraints", 
          cls="text-sm text-muted-foreground mt-2"),
        cls="mb-4"
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
        
        create_help_section(
            "instructions",
            "Provide specific rules, requirements, and behavioral guidelines that work with Nova's optimization engine. Use clear, directive language that the NovaPromptOptimizer can effectively evaluate and improve.",
            "Nova SDK's optimization process relies on measurable, specific instructions. Clear behavioral rules help the Evaluator component assess performance improvements and guide the optimization toward better results.",
            "Nova Instruction Patterns:\n• Measurable Requirements: 'ALWAYS provide confidence scores (0-100) with analysis'\n• Clear Boundaries: 'DO NOT include personal information in summaries'\n• Format Specifications: 'MUST format dates as YYYY-MM-DD'\n• Error Handling: 'If uncertain, respond with \"INSUFFICIENT_DATA\"'\n• Length Constraints: 'Keep responses under 200 words for optimization'"
        ),
        
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
        
        create_help_section(
            "response-format",
            "Define the structure, style, and format that works best with Nova's evaluation metrics. Consistent formatting helps the MetricAdapter and Evaluator measure optimization improvements accurately.",
            "Nova SDK's optimization process requires measurable outputs. Well-defined response formats enable the Evaluator to assess improvements and help the NovaPromptOptimizer generate better prompt variations.",
            "Nova Format Patterns:\n• Structured Output: 'Respond in JSON: {\"summary\": \"\", \"sentiment\": \"\", \"confidence\": 0-100}'\n• Measurable Elements: 'Include confidence score (0-100) for evaluation'\n• Consistent Structure: 'Format as: Problem | Analysis | Recommendation'\n• Length Constraints: 'Maximum 150 words for optimization efficiency'\n• Error Formats: 'Use \"ERROR: [reason]\" for invalid inputs'"
        ),
        
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
        
        create_help_section(
            "variables",
            "Define placeholder variables that integrate with Nova's TextPromptAdapter for dynamic, reusable prompts. Variables enable the same optimized prompt to work across different datasets and use cases.",
            "Nova SDK's TextPromptAdapter supports variable substitution, making optimized prompts reusable. This reduces the need to re-optimize similar prompts and maintains consistency across different applications.",
            "Nova Variable Patterns:\n• Input Variables: {user_input} - Main content for analysis\n• Context Variables: {domain_context} - Specific domain information\n• Constraint Variables: {max_length} - Dynamic length limits\n• Format Variables: {output_format} - Flexible response formatting\n• Evaluation Variables: {confidence_threshold} - Measurable criteria"
        ),
        
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
            Span("PASS", cls="text-green-500 text-sm font-semibold mr-2"),
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
            icon = "PASS" if passed else "FAIL"
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

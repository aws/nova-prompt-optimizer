"""
Routes for Optimized Prompt Builder
"""

import json
from fasthtml.common import *
from typing import Dict, Any, Optional
from shad4fast import Button
from database import Database
from services.prompt_builder import OptimizedPromptBuilder, NovaPromptTemplate
from components.prompt_builder import (
    builder_form_section, preview_panel, validation_panel, 
    template_selector, save_template_form
)
from components.layout import create_main_layout, create_card
from components.ui import CardContainer


def setup_prompt_builder_routes(app):
    """Setup all prompt builder routes"""
    
    @app.get("/prompt-builder")
    async def prompt_builder_page(request):
        """Main prompt builder page"""
        
        # Get available templates
        db = Database()
        templates = db.list_prompt_templates(limit=20)
        
        content = [
            # Header Section
            create_card(
                title="Optimized Prompt Builder",
                content=Div(
                    P("Create high-quality prompts using Nova best practices", 
                      cls="text-muted-foreground mb-4"),
                    
                    # Template Selector
                    template_selector(templates)
                )
            ),
            
            # Main Builder Form
            create_card(
                title="Build Your Prompt",
                content=Form(
                    builder_form_section(),
                    method="post",
                    action="/prompt-builder/build"
                )
            ),
            
            # Actions Section
            create_card(
                title="Actions",
                content=Div(
                    Button("Save as Template", 
                           type="button",
                           onclick="showSaveTemplateForm()",
                           variant="outline",
                           cls="mr-2"),
                    Button("Preview Prompt", 
                           type="button",
                           onclick="previewPrompt()",
                           variant="secondary")
                )
            ),
            
            # Save Template Form (hidden)
            save_template_form(),
            
            # Preview Container
            Div(id="preview-container", cls="hidden mt-6"),
            
            # Validation Container
            Div(id="validation-container", cls="hidden mt-6"),
            
            # JavaScript
            Script(src="/static/js/prompt_builder.js")
        ]
        
        return create_main_layout(
            "Prompt Builder - FIXED LAYOUT",
            Div(*content),
            current_page="prompts"
        )
    
    @app.post("/prompt-builder/preview")
    async def preview_prompt(request):
        """Generate prompt preview"""
        try:
            # Parse request data
            if request.headers.get('content-type') == 'application/json':
                data = await request.json()
            else:
                form_data = await request.form()
                data = dict(form_data)
            
            # Create builder from data
            builder = OptimizedPromptBuilder.from_dict(data)
            
            # Generate preview
            prompts = builder.preview()
            
            return preview_panel(
                system_prompt=prompts.get("system_prompt", ""),
                user_prompt=prompts.get("user_prompt", "")
            )
            
        except Exception as e:
            return Div(
                P(f"Error generating preview: {str(e)}", 
                  cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md"),
                cls="bg-white p-6 border border-gray-200 rounded-lg"
            )
    
    @app.post("/prompt-builder/validate")
    async def validate_prompt(request):
        """Validate prompt against best practices"""
        try:
            # Parse request data
            if request.headers.get('content-type') == 'application/json':
                data = await request.json()
            else:
                form_data = await request.form()
                data = dict(form_data)
            
            # Create builder from data
            builder = OptimizedPromptBuilder.from_dict(data)
            
            # Validate
            validation = builder.validate()
            
            return validation_panel(validation)
            
        except Exception as e:
            return Div(
                P(f"Error validating prompt: {str(e)}", 
                  cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md"),
                cls="bg-white p-6 border border-gray-200 rounded-lg"
            )
    
    @app.post("/prompt-builder/build")
    async def build_prompt(request):
        """Build final prompt and save to database"""
        try:
            # Parse request data
            if request.headers.get('content-type') == 'application/json':
                data = await request.json()
            else:
                form_data = await request.form()
                data = dict(form_data)
            
            # Create builder from data
            builder = OptimizedPromptBuilder.from_dict(data)
            
            # Validate before building
            validation = builder.validate()
            if not validation.is_valid:
                return Response(
                    json.dumps({"error": f"Cannot build invalid prompt: {', '.join(validation.issues)}"}),
                    status_code=400,
                    headers={"content-type": "application/json"}
                )
            
            # Build prompt adapter
            adapter = builder.build()
            
            # Save as prompt in database
            db = Database()
            
            # Generate name from task
            task = builder.task[:50] + "..." if len(builder.task) > 50 else builder.task
            prompt_name = f"Generated: {task}"
            
            # Create prompt in database
            prompt_id = db.create_prompt(
                name=prompt_name,
                type="system_user",
                variables={
                    "system_prompt": adapter.system_prompt,
                    "user_prompt": adapter.user_prompt
                }
            )
            
            return Response(
                json.dumps({
                    "success": True,
                    "prompt_id": prompt_id,
                    "message": "Prompt built and saved successfully!",
                    "redirect": f"/prompts"
                }),
                headers={"content-type": "application/json"}
            )
            
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status_code=500,
                headers={"content-type": "application/json"}
            )
    
    @app.post("/prompt-builder/save-template")
    async def save_template(request):
        """Save prompt as template"""
        try:
            # Parse request data
            if request.headers.get('content-type') == 'application/json':
                data = await request.json()
            else:
                form_data = await request.form()
                data = dict(form_data)
            
            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
            builder_data = data.get("builder_data", {})
            
            if not name:
                return Response(
                    json.dumps({"error": "Template name is required"}),
                    status_code=400,
                    headers={"content-type": "application/json"}
                )
            
            # Save template
            db = Database()
            template_id = db.create_prompt_template(
                name=name,
                description=description,
                builder_data=builder_data
            )
            
            return Response(
                json.dumps({
                    "success": True,
                    "template_id": template_id,
                    "message": f"Template '{name}' saved successfully!"
                }),
                headers={"content-type": "application/json"}
            )
            
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status_code=500,
                headers={"content-type": "application/json"}
            )
    
    @app.get("/prompt-builder/templates")
    async def list_templates():
        """List available templates"""
        try:
            db = Database()
            templates = db.list_prompt_templates()
            
            return Response(
                json.dumps(templates),
                headers={"content-type": "application/json"}
            )
            
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status_code=500,
                headers={"content-type": "application/json"}
            )
    
    @app.get("/prompt-builder/template/{template_id}")
    async def load_template(template_id: str):
        """Load specific template"""
        try:
            db = Database()
            template = db.get_prompt_template(template_id)
            
            if not template:
                return Response(
                    json.dumps({"error": "Template not found"}),
                    status_code=404,
                    headers={"content-type": "application/json"}
                )
            
            return Response(
                json.dumps(template),
                headers={"content-type": "application/json"}
            )
            
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                status_code=500,
                headers={"content-type": "application/json"}
            )

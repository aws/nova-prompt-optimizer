"""
Simple generator routes - extracted from app.py
"""

from fasthtml.common import *
from services.simple_dataset_generator import SimpleDatasetGenerator
from database import Database
from components.generator_components import create_generator_form, create_sample_display, create_generator_styles


def register_simple_generator_routes(app):
    """Register simple generator routes with the app"""
    
    @app.get("/simple-generator")
    def simple_generator_page():
        """Simple dataset generation page"""
        
        # Get available prompts
        db = Database()
        prompts = db.get_prompts()
        
        return Html(
            Head(
                Title("Simple Dataset Generator"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                create_generator_styles()
            ),
            Body(
                Div(
                    H1("Simple Dataset Generator"),
                    create_generator_form(prompts),
                    Div(id="results"),
                    cls="container"
                )
            )
        )
    
    @app.post("/simple-generator/generate")
    async def generate_simple_dataset(request):
        """Generate dataset using simple approach"""
        
        form_data = await request.form()
        prompt_id = form_data.get('prompt_id')
        num_samples = int(form_data.get('num_samples', 3))
        
        # Get prompt content
        db = Database()
        prompt_data = db.get_prompt(prompt_id)
        
        if not prompt_data:
            return Div("Error: Prompt not found", cls="error")
        
        variables = prompt_data.get('variables', {})
        system_prompt = variables.get('system_prompt', '')
        user_prompt = variables.get('user_prompt', '')
        
        full_prompt = f"System: {system_prompt}\nUser: {user_prompt}"
        
        # Generate samples
        generator = SimpleDatasetGenerator()
        result = generator.generate_dataset(full_prompt, num_samples)
        
        # Display results using component
        return create_sample_display(
            result.get("samples", []), 
            result.get("errors", [])
        )

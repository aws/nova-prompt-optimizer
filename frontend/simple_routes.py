"""
Simple routes for dataset generation - no complexity
"""

from fasthtml.common import *
from simple_dataset_generator import SimpleDatasetGenerator
from database import Database


def create_simple_generator_routes(app):
    """Add simple dataset generation routes to the app"""
    
    @app.get("/simple-generator")
    def simple_generator_page():
        """Simple dataset generation page"""
        
        # Get available prompts
        db = Database()
        prompts = db.get_prompts()
        
        prompt_options = []
        for prompt in prompts:
            variables = prompt.get('variables', {})
            system_prompt = variables.get('system_prompt', '')
            if system_prompt:
                prompt_options.append(
                    Option(prompt['name'], value=prompt['id'])
                )
        
        return Html(
            Head(
                Title("Simple Dataset Generator"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style("""
                    body { font-family: system-ui; margin: 2rem; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .form-group { margin: 1rem 0; }
                    label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
                    select, input, button { padding: 0.5rem; font-size: 1rem; }
                    button { background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    .sample { border: 1px solid #ddd; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
                    .error { color: red; }
                    .success { color: green; }
                    pre { background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto; }
                """)
            ),
            Body(
                Div(
                    H1("Simple Dataset Generator"),
                    
                    Form(
                        Div(
                            Label("Select Prompt:", for_="prompt-select"),
                            Select(
                                *prompt_options,
                                id="prompt-select",
                                name="prompt_id",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        
                        Div(
                            Label("Number of Samples:", for_="num-samples"),
                            Input(
                                type="number",
                                id="num-samples", 
                                name="num_samples",
                                value="3",
                                min="1",
                                max="10"
                            ),
                            cls="form-group"
                        ),
                        
                        Button("Generate Dataset", type="submit"),
                        
                        method="post",
                        action="/simple-generator/generate"
                    ),
                    
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
        
        if not result["success"]:
            return Div(
                H3("Generation Failed", cls="error"),
                P("No samples were generated successfully."),
                *[P(error, cls="error") for error in result["errors"]]
            )
        
        # Display results
        sample_divs = []
        for i, sample in enumerate(result["samples"], 1):
            sample_divs.append(
                Div(
                    H4(f"Sample {i}"),
                    P(Strong("Input: "), sample.get('input', 'N/A')),
                    P(Strong("Output:")),
                    Pre(sample.get('output', 'N/A')),
                    cls="sample"
                )
            )
        
        return Div(
            H3(f"Generated {result['total_generated']} samples", cls="success"),
            *sample_divs,
            *([P(f"Errors: {len(result['errors'])}", cls="error")] if result["errors"] else [])
        )

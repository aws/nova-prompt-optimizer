"""
Generator-specific UI components
"""

from fasthtml.common import *


def create_generator_form(prompts, action_url="/simple-generator/generate"):
    """Create a generator form component"""
    
    prompt_options = []
    for prompt in prompts:
        variables = prompt.get('variables', {})
        system_prompt = variables.get('system_prompt', '')
        if system_prompt:
            prompt_options.append(
                Option(prompt['name'], value=prompt['id'])
            )
    
    return Form(
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
        action=action_url
    )


def create_sample_display(samples, errors=None):
    """Create sample display component"""
    
    if not samples:
        return Div(
            H3("Generation Failed", cls="error"),
            P("No samples were generated successfully."),
            *([P(error, cls="error") for error in errors] if errors else [])
        )
    
    sample_divs = []
    for i, sample in enumerate(samples, 1):
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
        H3(f"Generated {len(samples)} samples", cls="success"),
        *sample_divs,
        *([P(f"Errors: {len(errors)}", cls="error")] if errors else [])
    )


def create_generator_styles():
    """Create generator-specific styles"""
    
    return Style("""
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

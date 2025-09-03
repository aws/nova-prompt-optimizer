"""
Simple routes for dataset generation - flexible format handling
"""

import json
import time
import os
from fasthtml.common import *
from shad4fast import ShadHead, Button, Card
from flexible_generator import FlexibleGenerator

# Simple progress tracking
simple_progress = {}

def update_simple_progress(session_id: str, current: int, total: int, status: str):
    """Update progress for simple generator"""
    try:
        simple_progress[session_id] = {
            'current': current,
            'total': total,
            'status': status,
            'timestamp': time.time()
        }
    except Exception as e:
        pass

def create_simple_generator_routes(app):
    """Setup simple dataset generation routes"""
    
    @app.get("/simple-generator")
    async def simple_generator_page(request):
        """Simple dataset generator page"""
        
        # Get available prompts from database
        from database import Database
        db = Database()
        prompts = db.get_prompts()
        
        # Create prompt options
        prompt_options = []
        for prompt in prompts:
            prompt_options.append(Option(prompt['name'], value=prompt['id']))
        
        return Html(
            ShadHead(tw_cdn=True, theme_handle=True),
            Body(
                # Navigation
                Nav(
                    Div(
                        Div(
                            A("Nova Prompt Optimizer", href="/", cls="navbar-brand"),
                            cls="flex items-center"
                        ),
                        Div(
                            A("Dashboard", href="/", cls="nav-link"),
                            A("Prompts", href="/prompts", cls="nav-link"),
                            A("Datasets", href="/datasets", cls="nav-link active"),
                            A("Metrics", href="/metrics", cls="nav-link"),
                            A("Optimization", href="/optimization", cls="nav-link"),
                            cls="navbar-nav"
                        ),
                        cls="flex justify-between items-center max-w-7xl mx-auto"
                    ),
                    cls="navbar"
                ),
                
                # Main content
                Div(
                    Div(
                    Div(
                        Div(
                            H4("Simple Dataset Generator", cls="card-title"),
                            cls="card-header"
                        ),
                        Div(
                            P("Automatically detects and follows any output format specified in your prompt (XML, JSON, text, etc.)", cls="text-muted-foreground mb-6"),
                                
                                Form(
                                    Div(
                                        Label("Select Prompt:", cls="block text-sm font-medium mb-2"),
                                        Select(*prompt_options, name="prompt_id", required=True, cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"),
                                        cls="mb-4"
                                    ),
                                    
                                    Div(
                                        Label("Describe Your Use Case:", cls="block text-sm font-medium mb-2"),
                                        Textarea(
                                            name="use_case_description",
                                            placeholder="Briefly describe what this dataset will be used for (e.g., 'customer support ticket classification', 'product review sentiment analysis', 'FAQ generation for e-commerce')",
                                            rows="3",
                                            cls="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                        ),
                                        P("This helps generate more relevant and diverse examples", cls="text-sm text-gray-500 mb-4"),
                                        cls="mb-4"
                                    ),
                                    
                                    Div(
                                        Label("Number of Samples:", cls="block text-sm font-medium mb-2"),
                                        Input(type="number", name="num_samples", value="3", min="1", max="100", cls="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"),
                                        cls="mb-6"
                                    ),
                                    
                                    Button("Generate Dataset", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full"),
                                    
                                    method="post",
                                    action="/simple-generator/generate"
                                ),
                                cls="card-body"
                            ),
                            cls="card"
                        ),
                        cls="max-w-2xl mx-auto"
                    ),
                    cls="container mx-auto px-4 py-8"
                )
            )
        )

    @app.post("/simple-generator/generate")
    async def generate_simple_dataset(request):
        """Generate dataset using flexible generator"""
        
        form_data = await request.form()
        prompt_id = form_data.get('prompt_id')
        use_case_description = form_data.get('use_case_description', '').strip()
        model_id = form_data.get('model_id', 'us.amazon.nova-pro-v1:0')
        num_samples = int(form_data.get('num_samples', 3))
        
        # Create session ID for progress tracking
        session_id = f"simple_{int(time.time() * 1000)}"
        
        # Get prompt from database
        from database import Database
        db = Database()
        prompt_data = db.get_prompt(prompt_id)
        
        if not prompt_data:
            update_simple_progress(session_id, 0, num_samples, "error")
            return Div("Error: Prompt not found", cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md")
        
        variables = prompt_data.get('variables', {})
        system_prompt = variables.get('system_prompt', '')
        user_prompt = variables.get('user_prompt', '')
        
        # Enhance prompt with use case context
        if use_case_description:
            enhanced_system_prompt = f"{system_prompt}\n\nUSE CASE CONTEXT: This dataset will be used for: {use_case_description}\nPlease generate examples that are relevant and diverse for this specific use case."
        else:
            enhanced_system_prompt = system_prompt
        
        # Combine system and user prompts
        full_prompt = f"{enhanced_system_prompt}\n\n{user_prompt}"
        
        # Update progress - generating
        update_simple_progress(session_id, 0, num_samples, "generating")
        
        # Generate samples using flexible generator
        generator = FlexibleGenerator(model_id=model_id)
        result = generator.generate_dataset(full_prompt, num_samples)
        
        # Mark as completed
        update_simple_progress(session_id, num_samples, num_samples, "completed")
        
        if not result["success"]:
            # Store error result in temp file
            import json
            import os
            
            temp_dir = os.path.join(os.path.dirname(__file__), 'temp_results')
            os.makedirs(temp_dir, exist_ok=True)
            
            session_id = request.session.get('session_id', str(time.time()).replace('.', ''))
            request.session['session_id'] = session_id
            
            temp_file = os.path.join(temp_dir, f"result_{session_id}.json")
            with open(temp_file, 'w') as f:
                json.dump({
                    'result': result,
                    'prompt_data': prompt_data
                }, f)
            
            from starlette.responses import RedirectResponse
            return RedirectResponse(url="/simple-generator/results", status_code=302)
        
        # Store results in a temporary file with session ID
        import json
        import tempfile
        import os
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_results')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Use session ID or create one
        session_id = request.session.get('session_id', str(time.time()).replace('.', ''))
        request.session['session_id'] = session_id
        
        # Store results in temp file
        temp_file = os.path.join(temp_dir, f"result_{session_id}.json")
        with open(temp_file, 'w') as f:
            json.dump({
                'result': result,
                'prompt_data': prompt_data
            }, f)
        
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/simple-generator/results", status_code=302)

    @app.get("/simple-generator/results")
    async def show_generation_results(request):
        """Display generation results with annotation capabilities"""
        
        # Get results from temp file
        import json
        import os
        
        session_id = request.session.get('session_id')
        if not session_id:
            return HTMLResponse('<script>alert("No results found"); window.location.href="/simple-generator";</script>')
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_results')
        temp_file = os.path.join(temp_dir, f"result_{session_id}.json")
        
        if not os.path.exists(temp_file):
            return HTMLResponse('<script>alert("No results found"); window.location.href="/simple-generator";</script>')
        
        try:
            with open(temp_file, 'r') as f:
                data = json.load(f)
            result = data['result']
            prompt_data = data['prompt_data']
        except Exception as e:
            return HTMLResponse('<script>alert("Error loading results"); window.location.href="/simple-generator";</script>')
        
        # Handle error results
        if not result.get("success"):
            error_message = result.get("error", "Unknown error occurred")
            return Html(
                Head(
                    Title("Dataset Generation Failed"),
                    Link(rel="stylesheet", href="https://cdn.tailwindcss.com"),
                ),
                Body(
                    Div(
                        H1("Dataset Generation Failed", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"❌ {error_message}", cls="text-red-600 mb-4"),
                        Button("Try Again", onclick="window.location.href='/simple-generator'", cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"),
                        cls="max-w-4xl mx-auto p-6"
                    )
                )
            )
        
        # Display successful results
        sample_divs = []
        for i, sample in enumerate(result["samples"], 1):
            formatted_output = str(sample.get('output', 'N/A'))
            
            sample_divs.append(
                Div(
                    H3(f"Sample {i}", cls="text-lg font-semibold mb-2"),
                    Button(f"Annotate Sample {i}", 
                           onclick=f"toggleAnnotation({i})", 
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mb-2"),
                    Div(
                        P("Input:", cls="font-medium text-sm mb-1"),
                        P(sample.get('input', 'N/A'), cls="text-sm text-gray-600 mb-3 p-2 bg-gray-50 rounded"),
                        P("Output:", cls="font-medium text-sm mb-1"),
                        Textarea(
                            formatted_output,
                            readonly=True,
                            rows="4",
                            cls="w-full p-2 bg-gray-50 rounded text-sm font-mono border mb-2"
                        ),
                        # Annotation box (hidden by default)
                        Div(
                            P("Annotation for this sample:", cls="font-medium text-sm mb-1 mt-3"),
                            Textarea(
                                placeholder="Enter specific feedback for this sample...",
                                name=f"annotation_{i}",
                                id=f"annotation_{i}",
                                rows="3",
                                cls="w-full p-2 border rounded text-sm"
                            ),
                            id=f"annotation_box_{i}",
                            style="display: none;"
                        ),
                        cls="mb-4"
                    ),
                    cls="bg-white p-4 border rounded-lg mb-4 shadow-sm"
                )
            )
        
        return Html(
            ShadHead(tw_cdn=True, theme_handle=True),
            Body(
                # Navigation
                Nav(
                    Div(
                        Div(
                            A("Nova Prompt Optimizer", href="/", cls="navbar-brand"),
                            cls="flex items-center"
                        ),
                        Div(
                            A("Dashboard", href="/", cls="nav-link"),
                            A("Prompts", href="/prompts", cls="nav-link"),
                            A("Datasets", href="/datasets", cls="nav-link active"),
                            A("Metrics", href="/metrics", cls="nav-link"),
                            A("Optimization", href="/optimization", cls="nav-link"),
                            cls="navbar-nav"
                        ),
                        cls="flex justify-between items-center max-w-7xl mx-auto"
                    ),
                    cls="navbar"
                ),
                
                # Main content
                Div(
                    # Success message and save form
                    Div(
                        Div(
                            H4("Dataset Generation Complete", cls="card-title"),
                            cls="card-header"
                        ),
                        Div(
                            P(f"✅ Generated {result['total_generated']} samples successfully", cls="text-green-600 font-semibold mb-2"),
                            P(f"Detected Format: {result.get('detected_format', 'Unknown')}", cls="text-gray-600 mb-4"),
                            
                            Form(
                                Input(type="hidden", name="samples_data", value=str(result["samples"])),
                                Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                                Div(
                                    Input(
                                        type="text",
                                        name="dataset_name",
                                        placeholder="Enter dataset name (e.g., 'Customer Support Samples')",
                                        required=True,
                                        cls="flex-1 p-2 border border-gray-300 rounded-md mr-2"
                                    ),
                                    Button("Save as Dataset", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                                    cls="flex"
                                ),
                                method="post",
                                action="/simple-generator/save-dataset"
                            ),
                            cls="card-body"
                        ),
                        cls="card mb-6"
                    ),
                    
                    # Generated samples
                    Div(
                        Div(
                            H4("Generated Samples", cls="card-title"),
                            cls="card-header"
                        ),
                        Div(
                            *sample_divs,
                            cls="card-body"
                        ),
                        cls="card mb-6"
                    ),
                    
                    # Regeneration section
                    Div(
                        Div(
                            H4("Refine Dataset", cls="card-title"),
                            cls="card-header"
                        ),
                        Div(
                            Form(
                                Input(type="hidden", name="original_samples", value=str(result["samples"])),
                                Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                                Div(
                                    P("General guidance for dataset improvement:", cls="font-medium text-sm mb-2"),
                                    Textarea(
                                        placeholder="Enter general instructions to improve the entire dataset...",
                                        name="general_guidance",
                                        id="general_guidance",
                                        rows="4",
                                        cls="w-full p-2 border border-gray-300 rounded-md text-sm mb-4"
                                    ),
                                    Button("Regenerate Dataset with Annotations", 
                                           type="submit",
                                           onclick="collectAnnotations()",
                                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
                                ),
                                method="post",
                                action="/simple-generator/regenerate",
                                id="regenerate_form"
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    
                    cls="container mx-auto px-4 py-8 max-w-6xl"
                ),
                
                # JavaScript for annotation functionality
                Script(f"""
                function toggleAnnotation(sampleNum) {{
                    const box = document.getElementById('annotation_box_' + sampleNum);
                    if (box.style.display === 'none' || box.style.display === '') {{
                        box.style.display = 'block';
                    }} else {{
                        box.style.display = 'none';
                    }}
                }}
                
                function collectAnnotations() {{
                    const form = document.getElementById('regenerate_form');
                    const annotations = {{}};
                    
                    for (let i = 1; i <= {len(result["samples"])}; i++) {{
                        const annotation = document.getElementById('annotation_' + i);
                        if (annotation && annotation.value.trim()) {{
                            annotations[i] = annotation.value.trim();
                        }}
                    }}
                    
                    const annotationsInput = document.createElement('input');
                    annotationsInput.type = 'hidden';
                    annotationsInput.name = 'annotations';
                    annotationsInput.value = JSON.stringify(annotations);
                    form.appendChild(annotationsInput);
                }}
                """)
            )
        )

    @app.post("/simple-generator/save-dataset")
    async def save_generated_dataset(request):
        """Save generated samples as a CSV dataset"""
        
        form_data = await request.form()
        dataset_name = form_data.get('dataset_name')
        samples_data = form_data.get('samples_data')
        prompt_name = form_data.get('prompt_name', 'Generated Dataset')
        
        try:
            import ast
            samples = ast.literal_eval(samples_data)
            
            # Create CSV content
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['input', 'output'])
            
            # Write samples
            for sample in samples:
                writer.writerow([sample.get('input', ''), sample.get('output', '')])
            
            csv_content = output.getvalue()
            
            # Save to database
            from database import Database
            db = Database()
            
            # Count rows in CSV
            row_count = len(samples)
            file_size = f"{len(csv_content)} bytes"
            
            dataset_id = db.create_dataset(
                name=dataset_name,
                file_type="csv",
                file_size=file_size,
                row_count=row_count
            )
            
            return HTMLResponse('<script>alert("Dataset saved successfully!"); window.location.href="/datasets";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error saving dataset: {str(e)}"); window.history.back();</script>')

    @app.post("/simple-generator/regenerate")
    async def regenerate_dataset(request):
        """Regenerate dataset with annotations and general guidance"""
        
        form_data = await request.form()
        original_samples = form_data.get('original_samples')
        prompt_name = form_data.get('prompt_name', 'Generated Dataset')
        general_guidance = form_data.get('general_guidance', '').strip()
        annotations_json = form_data.get('annotations', '{}')
        
        try:
            import json
            import ast
            
            # Parse original samples and annotations
            original_samples = ast.literal_eval(original_samples)
            annotations = json.loads(annotations_json)
            
            # Build refinement instructions
            refinement_instructions = []
            
            if general_guidance:
                refinement_instructions.append(f"General guidance: {general_guidance}")
            
            if annotations:
                refinement_instructions.append("Specific sample feedback:")
                for sample_num, annotation in annotations.items():
                    refinement_instructions.append(f"- Sample {sample_num}: {annotation}")
            
            if not refinement_instructions:
                return HTMLResponse('<script>alert("Please provide either general guidance or sample annotations"); window.history.back();</script>')
            
            # Create refined prompt with original samples and refinement instructions
            refined_prompt = f"""
Based on the following original dataset samples, generate an improved version incorporating these refinements:

{chr(10).join(refinement_instructions)}

Original samples for reference:
{json.dumps(original_samples[:3], indent=2)}...

Generate {len(original_samples)} improved samples that address the feedback while maintaining the same structure and format.
"""
            
            # Use the flexible generator to create refined samples
            generator = FlexibleGenerator()
            refined_results = []
            
            for i in range(len(original_samples)):
                result = generator.generate_sample(refined_prompt, i + 1)
                if result.get('success'):
                    refined_results.append(result['sample'])
                else:
                    # Fallback to original sample if generation fails
                    refined_results.append(original_samples[i])
            
            # Return results in the same format as original generation
            refined_result = {
                "success": True,
                "samples": refined_results,
                "total_generated": len(refined_results),
                "detected_format": "Refined dataset"
            }
            
            # Store refined result in temp file
            import os
            temp_dir = os.path.join(os.path.dirname(__file__), 'temp_results')
            os.makedirs(temp_dir, exist_ok=True)
            
            session_id = request.session.get('session_id', str(time.time()).replace('.', ''))
            request.session['session_id'] = session_id
            
            temp_file = os.path.join(temp_dir, f"result_{session_id}.json")
            with open(temp_file, 'w') as f:
                json.dump({
                    'result': refined_result,
                    'prompt_data': {'name': f"{prompt_name} (Refined)"}
                }, f)
            
            from starlette.responses import RedirectResponse
            return RedirectResponse(url="/simple-generator/results", status_code=302)
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error regenerating dataset: {str(e)}"); window.history.back();</script>')

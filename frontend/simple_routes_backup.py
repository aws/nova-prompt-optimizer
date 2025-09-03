"""
Simple routes for dataset generation - flexible format handling
"""

import json
import time
import os
from fasthtml.common import *
from shad4fast import Button, Input, Textarea
from flexible_generator import FlexibleGenerator
from database import Database
from components.layout import create_main_layout


def update_simple_progress(session_id: str, current: int, total: int, status: str):
    """Update progress for simple generator"""
    os.makedirs("data", exist_ok=True)
    progress_file = f"data/simple_progress_{session_id}.json"
    
    progress_data = {
        "current": current,
        "total": total,
        "status": status,
        "timestamp": time.time()
    }
    
    try:
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
    except Exception as e:
        print(f"Error updating simple progress: {e}")


def create_simple_generator_routes(app):
    """Add simple dataset generation routes to the app"""
    
    @app.get("/simple-generator")
    def simple_generator_page():
        """Simple dataset generation page"""
        
        # Get available prompts - build options differently
        db = Database()
        prompts = db.get_prompts()
        
        print(f"🔍 DEBUG - Found {len(prompts)} prompts in database")
        
        # Build prompt options as a list of Option elements
        prompt_option_elements = [Option("-- Select a Prompt --", value="", disabled=True, selected=True)]
        for prompt in prompts:
            variables = prompt.get('variables', {})
            system_prompt = variables.get('system_prompt', '')
            if system_prompt:
                prompt_option_elements.append(Option(prompt['name'], value=prompt['id']))
        
        print(f"🔍 DEBUG - Created {len(prompt_option_elements)} prompt option elements")
        
        content = Div(
            Div(
                H3("Simple Dataset Generator", cls="text-2xl font-semibold mb-4"),
                P("Automatically detects and follows any output format specified in your prompt (XML, JSON, text, etc.)", 
                  cls="text-sm text-muted-foreground bg-blue-50 p-4 rounded-md mb-6"),
                
                Form(
                    Div(
                        Label("Select Prompt:", cls="block text-sm font-medium mb-2"),
                        Select(
                            Option("Choose a prompt...", value="", disabled=True, selected=True),
                            *[Option(prompt['name'], value=prompt['id']) 
                              for prompt in prompts if prompt.get('variables', {}).get('system_prompt', '')],
                            name="prompt_id",
                            required=True,
                            cls="w-full p-2 border border-input rounded-md mb-4"
                        ),
                        cls="mb-4"
                    ),
                    
                    Div(
                        Label("Describe Your Use Case:", cls="block text-sm font-medium mb-2"),
                        Textarea(
                            name="use_case_description",
                            placeholder="Briefly describe what this dataset will be used for (e.g., 'customer support ticket classification', 'product review sentiment analysis', 'FAQ generation for e-commerce')",
                            rows="3",
                            cls="w-full p-2 border border-input rounded-md mb-4"
                        ),
                        P("This helps generate more relevant and diverse examples", cls="text-sm text-muted-foreground mb-4"),
                        cls="mb-4"
                    ),
                    
                    Div(
                        Label("Select Model:", cls="block text-sm font-medium mb-2"),
                        Select(
                            Option("Nova Pro", value="us.amazon.nova-pro-v1:0", selected=True),
                            Option("Nova Lite", value="us.amazon.nova-lite-v1:0"),
                            Option("Nova Premier", value="us.amazon.nova-premier-v1:0"),
                            name="model_id",
                            required=True,
                            cls="w-full p-2 border border-input rounded-md mb-4"
                        ),
                        cls="mb-4"
                    ),
                    
                    Div(
                        Label("Number of Samples:", cls="block text-sm font-medium mb-2"),
                        Input(
                            type="number",
                            name="num_samples",
                            value="3",
                            min="1",
                            max="100",
                            cls="w-full p-2 border border-input rounded-md mb-4"
                        ),
                        cls="mb-6"
                    ),
                    
                    Button("Generate Dataset", type="button", 
                           onclick="generateWithProgress()",
                           cls="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"),
                    
                    method="post",
                    action="/simple-generator/generate"
                ),
                cls="bg-background border border-border rounded-lg p-6 shadow-sm"
            ),
            
            # Progress bar (hidden initially)
            Div(
                Div(
                    H3("Generating Dataset", cls="text-lg font-semibold mb-4"),
                    Div(
                        Div("Progress", cls="flex justify-between text-sm text-gray-600 mb-1"),
                        Div(
                            Span("0 / 0 samples", id="simple-progress-text"),
                            cls="text-sm text-gray-600"
                        )
                    ),
                    Div(
                        Div(id="simple-progress-bar", cls="bg-blue-600 h-2 rounded-full transition-all duration-300", style="width: 0%"),
                        cls="w-full bg-gray-200 rounded-full h-2 mb-4"
                    ),
                    Div("Starting generation...", id="simple-generation-status", cls="text-sm text-gray-600"),
                    cls="bg-background border border-border rounded-lg p-6 shadow-sm"
                ),
                id="simple-progress-container",
                cls="hidden mt-6"
            ),
            
            Div(id="results", cls="mt-6"),
            
            # JavaScript for progress tracking
            Script("""
                let simpleProgressInterval = null;

                async function generateWithProgress() {
                    const form = document.querySelector('form');
                    const formData = new FormData(form);
                    const numSamples = parseInt(formData.get('num_samples') || '3');
                    
                    // Show progress bar
                    document.getElementById('simple-progress-container').classList.remove('hidden');
                    document.getElementById('results').innerHTML = '';
                    
                    // Start fake progress animation
                    startFakeProgress(numSamples);
                    
                    try {
                        const response = await fetch('/simple-generator/generate', {
                            method: 'POST',
                            body: formData
                        });
                        
                        // Always redirect to results page after fetch completes
                        window.location.href = '/simple-generator/results';
                        
                        const result = await response.text();
                        
                        stopFakeProgress();
                        updateSimpleProgressBar(numSamples, numSamples, 'completed');
                        
                        // Small delay to show completion, then hide progress bar
                        setTimeout(() => {
                            document.getElementById('simple-progress-container').classList.add('hidden');
                            document.getElementById('results').innerHTML = result;
                        }, 1000);
                        
                    } catch (error) {
                        stopFakeProgress();
                        document.getElementById('simple-generation-status').innerHTML = `<span class="text-red-600">Error: ${error.message}</span>`;
                    }
                }

                function startFakeProgress(numSamples) {
                    let current = 0;
                    const total = numSamples;
                    
                    updateSimpleProgressBar(0, total, 'starting');
                    
                    // Slower progress - estimate ~30-60 seconds per sample for realistic timing
                    const estimatedTimePerSample = 45000; // 45 seconds per sample
                    const totalTime = estimatedTimePerSample * numSamples;
                    const updateInterval = totalTime / (total * 10); // 10 updates per sample
                    
                    let progress = 0;
                    
                    simpleProgressInterval = setInterval(() => {
                        progress += 1;
                        const currentSample = Math.floor((progress / 10)) + 1;
                        const isComplete = currentSample > total;
                        
                        if (!isComplete) {
                            updateSimpleProgressBar(Math.min(currentSample, total), total, 'generating');
                        }
                    }, updateInterval);
                }

                function stopFakeProgress() {
                    if (simpleProgressInterval) {
                        clearInterval(simpleProgressInterval);
                        simpleProgressInterval = null;
                    }
                }

                function updateSimpleProgressBar(current, total, status) {
                    const progressBar = document.getElementById('simple-progress-bar');
                    const progressText = document.getElementById('simple-progress-text');
                    const statusDiv = document.getElementById('simple-generation-status');
                    
                    if (total > 0) {
                        const percentage = Math.round((current / total) * 100);
                        progressBar.style.width = `${percentage}%`;
                        progressText.textContent = `${current} / ${total} samples`;
                        
                        if (status === 'completed') {
                            statusDiv.innerHTML = '<span class="text-green-600">Generation completed!</span>';
                        } else if (status === 'error') {
                            statusDiv.innerHTML = '<span class="text-red-600">Generation failed</span>';
                        } else if (status === 'starting') {
                            statusDiv.textContent = 'Starting generation...';
                        } else {
                            statusDiv.textContent = `Generating sample ${current}/${total}...`;
                        }
                    }
                }
            """)
        )
        
        return create_main_layout(
            "Simple Dataset Generator",
            content,
            current_page="datasets"
        )
    
    @app.get("/simple-generator/progress/{session_id}")
    async def get_simple_progress(session_id: str):
        """Get generation progress for simple generator"""
        try:
            progress_file = f"data/simple_progress_{session_id}.json"
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                return progress
            else:
                return {"current": 0, "total": 0, "status": "not_started"}
        except Exception as e:
            return {"current": 0, "total": 0, "status": "error", "error": str(e)}

    @app.post("/simple-generator/generate")
    async def generate_simple_dataset(request):
        """Generate dataset using flexible approach"""
        
        form_data = await request.form()
        prompt_id = form_data.get('prompt_id')
        model_id = form_data.get('model_id', 'us.amazon.nova-pro-v1:0')
        num_samples = int(form_data.get('num_samples', 3))
        use_case_description = form_data.get('use_case_description', '').strip()
        session_id = form_data.get('session_id', f'simple_{int(time.time())}')
        
        # Initialize progress
        update_simple_progress(session_id, 0, num_samples, "starting")
        
        # Get prompt content
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
            enhanced_system_prompt = f"""Use Case Context: {use_case_description}

{system_prompt}

Generate diverse, realistic examples that are specifically relevant to the described use case. Vary the scenarios, language styles, and complexity levels to create a comprehensive dataset."""
        else:
            enhanced_system_prompt = system_prompt
        
        full_prompt = f"System: {enhanced_system_prompt}\nUser: {user_prompt}"
        
        # Update progress - generating
        update_simple_progress(session_id, 0, num_samples, "generating")
        
        # Generate samples using flexible generator
        generator = FlexibleGenerator(model_id=model_id)
        result = generator.generate_dataset(full_prompt, num_samples)
        
        # Mark as completed
        update_simple_progress(session_id, num_samples, num_samples, "completed")
        
        if not result["success"]:
            update_simple_progress(session_id, 0, num_samples, "error")
            error_type = result.get("error_type", "general")
            error_message = result.get("error", "Unknown error occurred")
            
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
        
        print(f"🔍 DEBUG - Stored results in temp file: {temp_file}")
        
        from starlette.responses import RedirectResponse
        return RedirectResponse(url="/simple-generator/results", status_code=302)

    @app.get("/simple-generator/results")
    async def show_generation_results(request):
        """Display generation results with annotation capabilities"""
        
        from components.layout import create_main_layout, create_card
        
        # Get results from temp file
        import json
        import os
        
        session_id = request.session.get('session_id')
        if not session_id:
            print("🔍 DEBUG - No session ID found")
            return HTMLResponse('<script>alert("No results found"); window.location.href="/simple-generator";</script>')
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_results')
        temp_file = os.path.join(temp_dir, f"result_{session_id}.json")
        
        if not os.path.exists(temp_file):
            print(f"🔍 DEBUG - Temp file not found: {temp_file}")
            return HTMLResponse('<script>alert("No results found"); window.location.href="/simple-generator";</script>')
        
        try:
            with open(temp_file, 'r') as f:
                data = json.load(f)
            result = data['result']
            prompt_data = data['prompt_data']
            print(f"🔍 DEBUG - Loaded results from temp file: {len(result.get('samples', []))} samples")
        except Exception as e:
            print(f"🔍 DEBUG - Error loading temp file: {e}")
            return HTMLResponse('<script>alert("Error loading results"); window.location.href="/simple-generator";</script>')
        
        # Handle error results
        if not result.get("success"):
            error_message = result.get("error", "Unknown error occurred")
            return create_main_layout(
                title="Dataset Generation Failed",
                content=[
                    create_card(
                        title="Generation Error",
                        content=Div(
                            P(f"❌ Generation Failed: {error_message}", cls="text-red-600 font-semibold mb-4"),
                            P(f"Detected Format: {result.get('detected_format', 'Unknown')}", cls="text-gray-600 mb-4"),
                            Button("Try Again", onclick="window.location.href='/simple-generator'", cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700")
                        )
                    )
                ],
                current_page="datasets"
            )
        
        # Display successful results with annotation capabilities
        sample_divs = []
        for i, sample in enumerate(result["samples"], 1):
            formatted_xml = str(sample.get('output', 'N/A'))
            
            sample_divs.append(
                Div(
                    H4(f"Sample {i}", cls="font-semibold text-lg mb-2"),
                    Button(f"Annotate Sample {i}", 
                           onclick=f"toggleAnnotation({i})", 
                           cls="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm mb-2"),
                    Div(
                        P("Input:", cls="font-medium text-sm text-gray-700 mb-1"),
                        P(sample.get('input', 'N/A'), cls="text-sm text-gray-600 mb-3 p-2 bg-gray-50 rounded"),
                        P("Output:", cls="font-medium text-sm text-gray-700 mb-1"),
                        Textarea(
                            formatted_xml,
                            readonly=True,
                            rows=str(max(3, min(10, formatted_xml.count('\n') + 2))),
                            cls="w-full p-2 bg-gray-50 rounded text-sm font-mono border"
                        ),
                        # Annotation box (hidden by default)
                        Div(
                            P("Annotation for this sample:", cls="font-medium text-sm text-gray-700 mb-1 mt-3"),
                            Textarea(
                                placeholder="Enter specific feedback for this sample...",
                                name=f"annotation_{i}",
                                id=f"annotation_{i}",
                                rows="3",
                                cls="w-full p-2 border rounded text-sm"
                            ),
                            id=f"annotation_box_{i}",
                            style="display: none;"
                        )
                    ),
                    cls="bg-white p-4 border rounded-lg mb-4 shadow-sm"
                )
            )
        
        content = [
            # Success message and save form
            create_card(
                title="Dataset Generation Complete",
                content=Div(
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
                                cls="flex-1 p-2 border rounded mr-2"
                            ),
                            Button("Save as Dataset", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"),
                            cls="flex"
                        ),
                        method="post",
                        action="/simple-generator/save-dataset"
                    )
                )
            ),
            
            # Generated samples
            create_card(
                title="Generated Samples",
                content=Div(*sample_divs)
            ),
            
            # Regeneration section
            create_card(
                title="Refine Dataset",
                content=Form(
                    Input(type="hidden", name="original_samples", value=str(result["samples"])),
                    Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                    Div(
                        P("General guidance for dataset improvement:", cls="font-medium text-sm text-gray-700 mb-2"),
                        Textarea(
                            placeholder="Enter general instructions to improve the entire dataset...",
                            name="general_guidance",
                            id="general_guidance",
                            rows="4",
                            cls="w-full p-2 border rounded text-sm mb-4"
                        ),
                        Button("Regenerate Dataset with Annotations", 
                               type="submit",
                               onclick="collectAnnotations()",
                               cls="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"),
                        cls="mb-4"
                    ),
                    method="post",
                    action="/simple-generator/regenerate",
                    id="regenerate_form"
                )
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
        ]
        
        return create_main_layout(
            title="Dataset Generation Results",
            content=content,
            current_page="datasets"
        )

    @app.post("/simple-generator/save-dataset")
            print(f"🔍 DEBUG - Displaying sample {i}: input={sample.get('input', 'N/A')[:50]}...")
            
            # Format XML for better readability
            output_xml = str(sample.get('output', 'N/A'))
            try:
                import xml.dom.minidom
                # Parse and pretty-print the XML
                dom = xml.dom.minidom.parseString(output_xml)
                formatted_xml = dom.toprettyxml(indent="  ")
                # Remove empty lines and XML declaration
                formatted_xml = '\n'.join([line for line in formatted_xml.split('\n') if line.strip() and not line.startswith('<?xml')])
            except:
                # If XML parsing fails, just use the original
                formatted_xml = output_xml
            
            sample_divs.append(
                Div(
                    H4(f"Sample {i}", style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;"),
                    Button(f"Annotate Sample {i}", 
                           onclick=f"toggleAnnotation({i})", 
                           cls="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm mb-2"),
                    Div(
                        P("Input:", style="font-weight: 600; margin-bottom: 0.5rem;"),
                        P(sample.get('input', 'N/A'), style="background: #f9fafb; padding: 0.75rem; border-radius: 0.375rem; margin-bottom: 1rem;")
                    ),
                    Div(
                        P("Output:", style="font-weight: 600; margin-bottom: 0.5rem;"),
                        Textarea(
                            formatted_xml,
                            readonly=True,
                            style="background: #f9fafb; padding: 0.75rem; border-radius: 0.375rem; font-size: 0.875rem; font-family: monospace; border: 1px solid #e5e7eb; width: 100%; resize: both; min-height: 100px; height: auto; overflow: auto;",
                            rows=str(max(3, min(20, formatted_xml.count('\n') + 2)))
                        )
                    ),
                    # Annotation box (hidden by default)
                    Div(
                        P("Annotation for this sample:", style="font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;"),
                        Textarea(
                            placeholder="Enter specific feedback for this sample (e.g., 'Make the tone more professional', 'Add more technical details', etc.)",
                            name=f"annotation_{i}",
                            id=f"annotation_{i}",
                            rows="3",
                            style="width: 100%; padding: 0.5rem; border: 1px solid #e5e7eb; border-radius: 0.375rem; font-size: 0.875rem;"
                        ),
                        id=f"annotation_box_{i}",
                        style="display: none; margin-top: 0.5rem;"
                    ),
                    style="background: white; padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                )
            )
        
        from components.layout import create_main_layout, create_card
        
        content = [
            # Success message
            create_card(
                title="Dataset Generation Complete",
                content=Div(
                    P(f"✅ Generated {result['total_generated']} samples successfully", 
                      cls="text-green-600 font-semibold mb-2"),
                    P(f"Detected Format: {result.get('detected_format', 'Unknown')}", 
                      cls="text-gray-600 mb-4"),
                    
                    # Save as Dataset form
                    Form(
                        Input(type="hidden", name="samples_data", value=str(result["samples"])),
                        Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                        Div(
                            Input(
                                type="text",
                                name="dataset_name",
                                placeholder="Enter dataset name (e.g., 'Customer Support Samples')",
                                required=True,
                                cls="flex-1 p-2 border rounded mr-2"
                            ),
                            Button("Save as Dataset", type="submit",
                                   cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"),
                            cls="flex"
                        ),
                        method="post",
                        action="/simple-generator/save-dataset"
                    )
                )
            ),
            
            # Generated samples
            create_card(
                title="Generated Samples",
                content=Div(*sample_divs)
            ),
            
            # Regeneration section
            create_card(
                title="Refine Dataset",
                content=Div(
                    Form(
                        Input(type="hidden", name="original_samples", value=str(result["samples"])),
                        Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                        Div(
                            P("General guidance for dataset improvement:", cls="font-medium text-sm text-gray-700 mb-2"),
                            Textarea(
                                placeholder="Enter general instructions to improve the entire dataset (e.g., 'Make all responses more concise', 'Add more variety in scenarios', 'Focus on edge cases', etc.)",
                                name="general_guidance",
                                id="general_guidance",
                                rows="4",
                                cls="w-full p-2 border rounded text-sm mb-4"
                            ),
                            Button("Regenerate Dataset with Annotations", 
                                   type="submit",
                                   onclick="collectAnnotations()",
                                   cls="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"),
                            cls="mb-4"
                        ),
                        method="post",
                        action="/simple-generator/regenerate",
                        id="regenerate_form"
                    ),
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
        ]
        
        return create_main_layout(
            title="Dataset Generation Results",
            content=content,
            current_page="datasets"
        )
    
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
            generator = FlexibleSampleGenerator()
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
            
            # Store refined result in session for display
            request.session['generation_result'] = refined_result
            request.session['prompt_data'] = {'name': f"{prompt_name} (Refined)"}
            
            from starlette.responses import RedirectResponse
            return RedirectResponse(url="/simple-generator/results", status_code=302)
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error regenerating dataset: {str(e)}"); window.history.back();</script>')

    @app.post("/simple-generator/save-dataset")
    async def save_generated_dataset(request):
        """Save generated samples as a CSV dataset"""
        
        form_data = await request.form()
        dataset_name = form_data.get('dataset_name')
        samples_data = form_data.get('samples_data')
        prompt_name = form_data.get('prompt_name', 'Generated Dataset')
        
        try:
            # Parse the samples data
            import ast
            samples = ast.literal_eval(samples_data)
            
            # Create CSV content
            import csv
            import io
            
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            
            # Write header
            writer.writerow(['input', 'output'])
            
            # Write samples
            for sample in samples:
                input_text = sample.get('input', '')
                output_text = sample.get('output', '')
                writer.writerow([input_text, output_text])
            
            csv_content = csv_buffer.getvalue()
            
            # Save to database
            db = Database()
            
            # Create temporary CSV file
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(csv_content)
                temp_file_path = f.name
            
            # Calculate file size and row count
            file_size = f"{os.path.getsize(temp_file_path) / 1024:.1f} KB"
            row_count = len(samples)
            
            dataset_id = db.create_dataset(
                name=dataset_name,
                file_type="CSV",
                file_size=file_size,
                row_count=row_count,
                file_path=temp_file_path
            )
            
            return Div(
                P(f"✅ Dataset '{dataset_name}' saved successfully!", 
                  style="color: #059669; font-weight: 600; background: #ecfdf5; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem;"),
                P(f"Dataset ID: {dataset_id}", 
                  style="background: #f0f8ff; padding: 0.5rem; border-radius: 0.375rem; margin-bottom: 1rem;"),
                P(f"Rows: {len(samples)} samples with input/output columns", 
                  style="color: #6b7280; margin-bottom: 1rem;"),
                Div(
                    Button("View Datasets", 
                           onclick="window.location.href='/datasets'",
                           cls="bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                           style="margin-right: 0.5rem;"),
                    Button("Generate More", 
                           onclick="window.location.href='/simple-generator'",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                    style="margin-top: 1rem;"
                )
            )
            
        except Exception as e:
            return Div(
                P(f"❌ Error saving dataset: {str(e)}", 
                  style="color: #dc2626; font-weight: 600; background: #fee; padding: 1rem; border-radius: 0.375rem;")
            )

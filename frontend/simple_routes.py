"""
Simple routes for dataset generation - flexible format handling
"""

from fasthtml.common import *
from flexible_generator import FlexibleGenerator
from database import Database
from components.layout import create_main_layout


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
                H3("Flexible Dataset Generator", style="margin-bottom: 1rem; font-size: 1.5rem; font-weight: 600;"),
                P("Automatically detects and follows any output format specified in your prompt (XML, JSON, text, etc.)", 
                  style="margin-bottom: 2rem; color: #6b7280; background: #f0f8ff; padding: 1rem; border-radius: 0.5rem;"),
                
                Form(
                    Div(
                        Label("Select Prompt:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Select(
                            Option("Choose a prompt...", value="", disabled=True, selected=True),
                            *[Option(prompt['name'], value=prompt['id']) 
                              for prompt in prompts if prompt.get('variables', {}).get('system_prompt', '')],
                            name="prompt_id",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    
                    Div(
                        Label("Select Model:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Select(
                            Option("Nova Pro", value="us.amazon.nova-pro-v1:0", selected=True),
                            Option("Nova Lite", value="us.amazon.nova-lite-v1:0"),
                            Option("Nova Premier", value="us.amazon.nova-premier-v1:0"),
                            name="model_id",
                            required=True,
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1rem;"
                    ),
                    
                    Div(
                        Label("Number of Samples:", style="display: block; margin-bottom: 0.5rem; font-weight: 500;"),
                        Input(
                            type="number",
                            name="num_samples",
                            value="3",
                            min="1",
                            max="100",
                            style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-bottom: 1rem;"
                        ),
                        style="margin-bottom: 1.5rem;"
                    ),
                    
                    Button("Generate Dataset", type="submit", 
                           style="background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.375rem; font-weight: 500; cursor: pointer; width: 100%;"),
                    
                    method="post",
                    action="/simple-generator/generate"
                ),
                style="background: white; padding: 2rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
            ),
            
            Div(id="results", style="margin-top: 2rem;")
        )
        
        return create_main_layout(
            "Flexible Dataset Generator",
            content,
            current_page="datasets"
        )
    
    @app.post("/simple-generator/generate")
    async def generate_simple_dataset(request):
        """Generate dataset using flexible approach"""
        
        form_data = await request.form()
        prompt_id = form_data.get('prompt_id')
        model_id = form_data.get('model_id', 'us.amazon.nova-pro-v1:0')
        num_samples = int(form_data.get('num_samples', 3))
        
        # Get prompt content
        db = Database()
        prompt_data = db.get_prompt(prompt_id)
        
        if not prompt_data:
            return Div("Error: Prompt not found", style="color: red; padding: 1rem; background: #fee; border: 1px solid #fcc; border-radius: 0.375rem;")
        
        variables = prompt_data.get('variables', {})
        system_prompt = variables.get('system_prompt', '')
        user_prompt = variables.get('user_prompt', '')
        
        full_prompt = f"System: {system_prompt}\nUser: {user_prompt}"
        
        # Generate samples using flexible generator
        generator = FlexibleGenerator(model_id=model_id)
        result = generator.generate_dataset(full_prompt, num_samples)
        
        if not result["success"]:
            error_type = result.get("error_type", "general")
            error_message = result.get("error", "Unknown error occurred")
            
            return Div(
                P(f"Generation Failed: {error_message}", style="color: #dc2626; font-weight: 600; margin-bottom: 1rem;"),
                P(f"Detected Format: {result.get('detected_format', 'Unknown')}", 
                  style="background: #f0f8ff; padding: 0.5rem; border-radius: 0.375rem;"),
                style="background: #fee; padding: 1rem; border: 1px solid #fcc; border-radius: 0.375rem; margin-top: 1rem;"
            )
        
        # Display results
        sample_divs = []
        for i, sample in enumerate(result["samples"], 1):
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
                    style="background: white; padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
                )
            )
        
        return Div(
            P(f"✅ Generated {result['total_generated']} samples successfully", 
              style="color: #059669; font-weight: 600; background: #ecfdf5; padding: 1rem; border-radius: 0.375rem; margin-bottom: 1rem;"),
            P(f"Detected Format: {result.get('detected_format', 'Unknown')}", 
              style="background: #f0f8ff; padding: 0.5rem; border-radius: 0.375rem; margin-bottom: 1rem;"),
            
            # Save as Dataset button
            Form(
                Input(type="hidden", name="samples_data", value=str(result["samples"])),
                Input(type="hidden", name="prompt_name", value=prompt_data.get('name', 'Generated Dataset')),
                Div(
                    Input(
                        type="text",
                        name="dataset_name",
                        placeholder="Enter dataset name (e.g., 'Customer Support Samples')",
                        required=True,
                        style="flex: 1; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.375rem; margin-right: 0.5rem;"
                    ),
                    Button("Save as Dataset", type="submit",
                           style="background: #059669; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"),
                    style="display: flex; margin-bottom: 2rem;"
                ),
                method="post",
                action="/simple-generator/save-dataset"
            ),
            
            *sample_divs
        )
    
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
            dataset_id = db.create_dataset(
                name=dataset_name,
                description=f"Generated from prompt: {prompt_name}",
                csv_content=csv_content,
                rows=len(samples)
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
                           style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 500; cursor: pointer; margin-right: 0.5rem;"),
                    Button("Generate More", 
                           onclick="window.location.href='/simple-generator'",
                           style="background: #6b7280; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.375rem; font-weight: 500; cursor: pointer;"),
                    style="margin-top: 1rem;"
                )
            )
            
        except Exception as e:
            return Div(
                P(f"❌ Error saving dataset: {str(e)}", 
                  style="color: #dc2626; font-weight: 600; background: #fee; padding: 1rem; border-radius: 0.375rem;")
            )

"""
Infer from Assets Routes - Multi-step workflow for advanced metric inference
Step 1: Dataset sampling configuration
Step 2: Metric analysis and selection
Step 3: Output format validation
Step 4: Code generation
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
from services.metric_service import MetricService
import json


def setup_infer_assets_routes(app):
    """Setup infer from assets routes"""
    
    @app.get("/infer-assets")
    async def infer_assets_step1(request):
        """Step 1: Dataset sampling configuration"""
        
        db = Database()
        datasets = db.get_datasets()
        prompts = db.get_prompts()
        
        # Create dataset options
        dataset_options = [Option("Choose a dataset...", value="", selected=True, disabled=True)]
        for dataset in datasets:
            dataset_options.append(
                Option(f"{dataset['name']} ({dataset.get('rows', 'N/A')} rows)", value=str(dataset['id']))
            )
        
        # Create prompt options
        prompt_options = [Option("No prompt selected", value="", selected=True)]
        for prompt in prompts:
            prompt_options.append(
                Option(prompt['name'], value=str(prompt['id']))
            )
        
        content = [
            create_card(
                title="Step 1: Configure Dataset Sampling",
                content=Div(
                    P("Select your dataset and configure how many records to analyze. We'll randomly sample from your dataset for efficient analysis.", cls="text-muted-foreground mb-4"),
                    P("Smaller samples (50-200 records) provide faster analysis while maintaining accuracy.", cls="text-sm text-gray-600 mb-4")
                )
            ),
            
            create_card(
                title="Dataset & Sampling Configuration",
                content=Form(
                    Div(
                        Label("Select Dataset", cls="block text-sm font-medium mb-1"),
                        Select(*dataset_options, name="dataset_id", required=True, cls="w-full p-2 border rounded mb-3", onchange="updateSampleSize()")
                    ),
                    Div(
                        Label("Select Prompt (Optional)", cls="block text-sm font-medium mb-1"),
                        Select(*prompt_options, name="prompt_id", cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("Sample Size", cls="block text-sm font-medium mb-1"),
                        Select(
                            Option("50 records (Fast)", value="50"),
                            Option("100 records (Balanced)", value="100", selected=True),
                            Option("200 records (Thorough)", value="200"),
                            Option("500 records (Comprehensive)", value="500"),
                            name="sample_size", cls="w-full p-2 border rounded mb-3"
                        )
                    ),
                    Div(
                        Label("Analysis Focus (Optional)", cls="block text-sm font-medium mb-1"),
                        Textarea(name="focus_description", rows="2", placeholder="Specific aspects to focus on (e.g., 'accuracy vs speed tradeoff', 'semantic understanding')", cls="w-full p-2 border rounded mb-3")
                    ),
                    Button("Analyze Dataset & Continue", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                    Button("Back to Metrics", onclick="window.location.href='/metrics'", type="button", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                    method="post",
                    action="/infer-assets/analyze"
                )
            )
        ]
        
        return create_main_layout(
            "Infer from Assets - Step 1",
            Div(*content),
            current_page="metrics"
        )

    @app.post("/infer-assets/analyze")
    async def analyze_assets_step2(request):
        """Step 2: Analyze assets and show suggested metrics"""
        try:
            form_data = await request.form()
            dataset_id = form_data.get('dataset_id')
            prompt_id = form_data.get('prompt_id')
            sample_size = int(form_data.get('sample_size', 100))
            focus_description = form_data.get('focus_description', '').strip()
            
            if not dataset_id:
                return HTMLResponse('<script>alert("Please select a dataset"); window.history.back();</script>')
            
            db = Database()
            dataset = db.get_dataset(dataset_id)
            prompt = db.get_prompt(prompt_id) if prompt_id else None
            
            if not dataset:
                return HTMLResponse('<script>alert("Dataset not found"); window.history.back();</script>')
            
            # Analyze assets and suggest metrics
            metric_service = MetricService()
            dataset_path = db.get_dataset_file_path(dataset_id)
            analysis_result = metric_service.analyze_dataset_for_metrics(
                dataset_path=dataset_path,
                prompt_data=prompt,
                sample_size=sample_size,
                focus_description=focus_description
            )
            
            if not analysis_result['success']:
                return HTMLResponse(f'<script>alert("Analysis failed: {analysis_result["error"]}"); window.history.back();</script>')
            
            # Store analysis in session for next step
            session_data = {
                'dataset_id': dataset_id,
                'prompt_id': prompt_id,
                'sample_size': sample_size,
                'focus_description': focus_description,
                'analysis': analysis_result
            }
            
            content = [
                create_card(
                    title="Step 2: Review Suggested Metrics",
                    content=Div(
                        P("Based on your dataset and prompt analysis, here are the suggested evaluation metrics. Uncheck any metrics you don't need.", cls="text-muted-foreground mb-4"),
                        P(f"Analysis based on {sample_size} sample records from '{dataset['name']}'", cls="text-sm text-gray-600 mb-4")
                    )
                ),
                
                create_card(
                    title="Dataset Analysis Summary",
                    content=Div(
                        P(analysis_result['dataset_summary'], cls="text-gray-700 mb-4"),
                        P(f"Task Type: {analysis_result['task_type']}", cls="font-medium mb-2"),
                        P(f"Recommended Metrics: {len(analysis_result['suggested_metrics'])}", cls="text-sm text-gray-600")
                    )
                ),
                
                create_card(
                    title="Select Metrics to Generate",
                    content=Form(
                        Div(
                            *[
                                Div(
                                    Input(type="checkbox", name="selected_metrics", value=str(i), checked=True, cls="mr-2"),
                                    Label(
                                        Div(
                                            Strong(metric['name'], cls="block mb-1"),
                                            P(metric['description'], cls="text-sm text-gray-700 mb-2"),
                                            P(f"📋 What this measures in your data: {metric.get('plain_explanation', 'Evaluates your specific dataset')}", cls="text-sm text-blue-700 bg-blue-50 p-2 rounded mb-2"),
                                            P(f"Type: {metric['type']} | Complexity: {metric['complexity']}", cls="text-xs text-gray-500")
                                        ),
                                        cls="cursor-pointer"
                                    ),
                                    cls="flex items-start p-3 border rounded mb-3 hover:bg-gray-50"
                                )
                                for i, metric in enumerate(analysis_result['suggested_metrics'])
                            ],
                            cls="space-y-2 mb-4"
                        ),
                        
                        Input(type="hidden", name="session_data", value=json.dumps(session_data)),
                        
                        Button("Continue to Format Validation", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Back to Step 1", onclick="window.location.href='/infer-assets'", type="button", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/infer-assets/validate-format"
                    )
                )
            ]
            
            return create_main_layout(
                "Infer from Assets - Step 2",
                Div(*content),
                current_page="metrics"
            )
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error: {str(e)}"); window.history.back();</script>')

    @app.post("/infer-assets/validate-format")
    async def validate_format_step3(request):
        """Step 3: Validate output format requirements"""
        try:
            form_data = await request.form()
            session_data = json.loads(form_data.get('session_data', '{}'))
            selected_metrics = form_data.getlist('selected_metrics')
            
            if not selected_metrics:
                return HTMLResponse('<script>alert("Please select at least one metric"); window.history.back();</script>')
            
            # Get selected metrics from analysis
            analysis = session_data['analysis']
            selected_metric_objects = [analysis['suggested_metrics'][int(i)] for i in selected_metrics]
            
            content = [
                create_card(
                    title="Step 3: Validate Output Format",
                    content=Div(
                        P("Specify any output format requirements for your metrics. This ensures the generated code matches your expected data types and structures.", cls="text-muted-foreground mb-4"),
                        P(f"Generating {len(selected_metric_objects)} metrics", cls="text-sm text-gray-600 mb-4")
                    )
                ),
                
                create_card(
                    title="Selected Metrics",
                    content=Div(
                        *[
                            Div(
                                Strong(metric['name'], cls="block mb-1"),
                                P(metric['description'], cls="text-sm text-gray-600"),
                                cls="p-3 bg-gray-50 rounded mb-2"
                            )
                            for metric in selected_metric_objects
                        ]
                    )
                ),
                
                create_card(
                    title="Output Format Validation",
                    content=Form(
                        Div(
                            Label("Expected Output Format", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("Auto-detect from data", value="auto", selected=True),
                                Option("Numeric score (0-1)", value="numeric_01"),
                                Option("Numeric score (0-100)", value="numeric_100"),
                                Option("Percentage (%)", value="percentage"),
                                Option("Boolean (True/False)", value="boolean"),
                                Option("Classification labels", value="classification"),
                                Option("JSON object", value="json"),
                                Option("XML structure", value="xml"),
                                Option("List/Array", value="list"),
                                Option("Dictionary/Map", value="dictionary"),
                                Option("Multi-dimensional (nested)", value="multidimensional"),
                                Option("Custom format", value="custom"),
                                name="output_format", cls="w-full p-2 border rounded mb-3",
                                onchange="toggleCustomFormat()"
                            )
                        ),
                        Div(
                            Label("Custom Format Description", cls="block text-sm font-medium mb-1"),
                            Textarea(name="custom_format", rows="4", placeholder="Describe your expected output format with examples:\n\nFor XML: <result><score>0.85</score><confidence>high</confidence></result>\nFor JSON: {\"accuracy\": 0.85, \"precision\": 0.92, \"recall\": 0.78}\nFor nested: {\"overall\": 0.85, \"breakdown\": {\"semantic\": 0.9, \"syntax\": 0.8}}", cls="w-full p-2 border rounded mb-3 font-mono text-sm"),
                            id="custom-format-field",
                            style="display: none;"
                        ),
                        Div(
                            Label("Output Parsing Strategy", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("Extract key metrics automatically", value="auto_extract"),
                                Option("Parse structured format (XML/JSON)", value="structured_parse"),
                                Option("Pattern matching (regex)", value="pattern_match"),
                                Option("Custom parsing logic", value="custom_parse"),
                                name="parsing_strategy", cls="w-full p-2 border rounded mb-3",
                                onchange="toggleParsingDetails()"
                            ),
                            id="parsing-strategy-field",
                            style="display: none;"
                        ),
                        Div(
                            Label("Parsing Details", cls="block text-sm font-medium mb-1"),
                            Textarea(name="parsing_details", rows="3", placeholder="Specify parsing logic:\n\nFor XML: Extract <score> tag value\nFor JSON: Get 'accuracy' field\nFor regex: Match pattern \\d+\\.\\d+\nFor custom: Describe extraction method", cls="w-full p-2 border rounded mb-3 font-mono text-sm"),
                            id="parsing-details-field",
                            style="display: none;"
                        ),
                        Div(
                            Label("Additional Requirements", cls="block text-sm font-medium mb-1"),
                            Textarea(name="additional_requirements", rows="3", placeholder="Any specific requirements for the metric implementation (e.g., 'Handle missing values gracefully', 'Use case-insensitive comparison')", cls="w-full p-2 border rounded mb-3")
                        ),
                        
                        Input(type="hidden", name="session_data", value=json.dumps({**session_data, 'selected_metrics': selected_metric_objects})),
                        
                        Div(
                            Label("Composite Metric Name", cls="block text-sm font-medium mb-1"),
                            Input(type="text", name="composite_name", placeholder="e.g., 'Customer Support Evaluation Suite'", cls="w-full p-2 border rounded mb-2"),
                            P("Multiple metrics will be combined into a single composite metric with this name", cls="text-sm text-gray-600 mb-3")
                        ),
                        
                        Button("Generate Metric Code", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Back to Metric Selection", onclick="window.history.back()", type="button", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/infer-assets/generate-code"
                    )
                ),
                
                Script("""
                    function toggleCustomFormat() {
                        const format = document.querySelector('select[name="output_format"]').value;
                        const customField = document.getElementById('custom-format-field');
                        customField.style.display = format === 'custom' ? 'block' : 'none';
                    }
                """)
            ]
            
            return create_main_layout(
                "Infer from Assets - Step 3",
                Div(*content),
                current_page="metrics"
            )
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error: {str(e)}"); window.history.back();</script>')

    @app.post("/infer-assets/generate-code")
    async def generate_code_step4(request):
        """Step 4: Generate final metric code"""
        try:
            form_data = await request.form()
            session_data = json.loads(form_data.get('session_data', '{}'))
            output_format = form_data.get('output_format', 'auto')
            custom_format = form_data.get('custom_format', '').strip()
            additional_requirements = form_data.get('additional_requirements', '').strip()
            composite_name = form_data.get('composite_name', '').strip()
            
            # Generate code for selected metrics
            metric_service = MetricService()
            generated_metrics = []
            
            # Check if we should create a composite metric
            if len(session_data['selected_metrics']) > 1:
                # Multiple metrics - create composite only
                composite_name = composite_name or f"Composite: {', '.join([m['name'] for m in session_data['selected_metrics']])}"
                
                # Remove try/catch to see full traceback
                try:
                    composite_code = metric_service.generate_composite_metric_code(
                        session_data['selected_metrics']
                    )
                except Exception as e:
                    # Log the full traceback to console
                    import traceback
                    print(f"🔥 FULL ERROR TRACEBACK:")
                    print("=" * 80)
                    traceback.print_exc()
                    print("=" * 80)
                    print(f"🔥 ERROR TYPE: {type(e).__name__}")
                    print(f"🔥 ERROR MESSAGE: {str(e)}")
                    
                    # Re-raise to see in browser too
                    raise e
                
                # If we get here, the code was generated and saved successfully
                print(f"✅ Composite metric generated and saved successfully")
                
                # Save composite metric (even if fallback)
                db = Database()
                composite_id = db.create_metric(
                    name=composite_name,
                    description=f"Composite metric combining: {', '.join([m['name'] for m in session_data['selected_metrics']])}",
                    dataset_format="composite",
                    scoring_criteria=f"Weighted combination of {len(session_data['selected_metrics'])} metrics",
                    generated_code=composite_code
                )
                
                generated_metrics.append({
                    'id': composite_id,
                    'name': composite_name,
                    'code': composite_code,
                    'description': f"Composite of {len(session_data['selected_metrics'])} metrics: {', '.join([m['name'] for m in session_data['selected_metrics']])}",
                    'is_composite': True
                })
                
            else:
                # Single metric - generate individual metric
                metric = session_data['selected_metrics'][0]
                criteria = {
                    'description': metric['description'],
                    'type': metric['type'],
                    'complexity': metric['complexity'],
                    'output_format': output_format,
                    'custom_format': custom_format,
                    'additional_requirements': additional_requirements
                }
                
                try:
                    generated_code = metric_service.generate_metric_code(
                        name=metric['name'],
                        criteria=criteria
                    )
                    
                    # Save to database
                    db = Database()
                    metric_id = db.create_metric(
                        name=metric['name'],
                        description=metric['description'],
                        dataset_format="asset_inferred",
                        scoring_criteria=f"Type: {metric['type']}, Complexity: {metric['complexity']}",
                        generated_code=generated_code
                    )
                    
                    generated_metrics.append({
                        'id': metric_id,
                        'name': metric['name'],
                        'code': generated_code,
                        'description': metric['description']
                    })
                    
                except Exception as e:
                    generated_metrics.append({
                        'name': metric['name'],
                        'error': str(e)
                    })
            
            content = [
                create_card(
                    title="✅ Metrics Generated Successfully!",
                    content=Div(
                        P(f"Generated {len([m for m in generated_metrics if 'code' in m])} metrics from your asset analysis", cls="text-green-600 font-semibold mb-4"),
                        P(f"Dataset: {session_data['analysis']['dataset_summary'][:100]}...", cls="text-sm text-gray-600 mb-4")
                    )
                ),
                
                *[
                    create_card(
                        title=f"📊 {metric['name']}" + (" (Composite)" if metric.get('is_composite') else ""),
                        content=Div(
                            P(metric.get('description', ''), cls="text-gray-700 mb-4") if 'description' in metric else None,
                            Div(
                                H4("Generated MetricAdapter Code:", cls="font-semibold mb-2"),
                                Pre(metric['code'], cls="bg-gray-50 p-3 rounded text-sm mb-4 whitespace-pre-wrap overflow-x-auto overflow-y-auto max-h-96"),
                                cls="mb-4"
                            ) if 'code' in metric else Div(
                                P(f"❌ Error generating code: {metric['error']}", cls="text-red-600"),
                                cls="mb-4"
                            ),
                            Div(
                                Span("🎯 Composite Metric", cls="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"),
                                cls="mb-2"
                            ) if metric.get('is_composite') else None
                        )
                    )
                    for metric in generated_metrics
                ],
                
                create_card(
                    title="Next Steps",
                    content=Div(
                        P("Your metrics have been saved and are ready to use in optimizations.", cls="mb-4"),
                        Div(
                            Button("View All Metrics", onclick="window.location.href='/metrics'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                            Button("Start New Analysis", onclick="window.location.href='/infer-assets'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"),
                            Button("Run Optimization", onclick="window.location.href='/optimization'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                            cls="flex gap-2"
                        )
                    )
                )
            ]
            
            return create_main_layout(
                "Infer from Assets - Complete",
                Div(*content),
                current_page="metrics"
            )
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error: {str(e)}"); window.history.back();</script>')

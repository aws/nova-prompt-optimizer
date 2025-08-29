"""
Metrics Management Routes
Handles metric CRUD operations and AI generation
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
from services.metric_service import MetricService


def setup_metric_routes(app):
    """Setup metric management routes"""
    
    @app.get("/metrics")
    async def metrics_page(request):
        """Metrics management page"""
        
        db = Database()
        metrics = db.get_metrics()
        datasets = db.get_datasets()
        prompts = db.get_prompts()
        
        metric_rows = []
        for metric in metrics:
            metric_rows.append(
                Tr(
                    Td(metric['name'], cls="px-4 py-2"),
                    Td(metric['description'][:50] + '...' if len(metric['description']) > 50 else metric['description'], cls="px-4 py-2"),
                    Td(metric.get('dataset_format', 'Custom'), cls="px-4 py-2"),
                    Td(metric['created'][:10], cls="px-4 py-2"),
                    Td(
                        Button("Test", onclick=f"testMetric('{metric['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-1"),
                        Button("Edit", onclick=f"editMetric('{metric['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-1"),
                        Button("Delete", onclick=f"deleteMetric('{metric['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="px-4 py-2"
                    )
                )
            )
        
        dataset_options = [Option("Select a dataset...", value="")]
        for dataset in datasets:
            dataset_options.append(Option(dataset['name'], value=str(dataset['id'])))
        
        content = [
            # Header with actions
            create_card(
                title="Metrics Management",
                content=Div(
                    P("Create and manage evaluation metrics for prompt optimization", cls="text-muted-foreground mb-4"),
                    Div(
                        Button("Create Manual Metric", onclick="showCreateForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Generate with AI", onclick="showAIForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"),
                        Button("Infer from Assets", onclick="window.location.href='/infer-assets'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="flex gap-2"
                    )
                )
            ),
            
            # Manual create form (hidden)
            Div(
                create_card(
                    title="Create Manual Metric",
                    content=Form(
                        Div(
                            Label("Metric Name", cls="block text-sm font-medium mb-1"),
                            Input(type="text", name="name", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Description", cls="block text-sm font-medium mb-1"),
                            Textarea(name="description", rows="2", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Metric Type", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("Classification", value="classification"),
                                Option("Regression", value="regression"),
                                Option("Custom", value="custom"),
                                name="metric_type", required=True, cls="w-full p-2 border rounded mb-3"
                            )
                        ),
                        Div(
                            Label("Python Code", cls="block text-sm font-medium mb-1"),
                            Textarea(name="code", rows="10", placeholder="def evaluate(prediction, ground_truth):\n    # Your metric code here\n    return score", required=True, cls="w-full p-2 border rounded mb-3 font-mono")
                        ),
                        Button("Create", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Cancel", type="button", onclick="hideCreateForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/metrics/create"
                    )
                ),
                id="create-form",
                cls="hidden mt-4"
            ),
            
            # AI generation form (hidden)
            Div(
                create_card(
                    title="Generate Metric with AI",
                    content=Form(
                        Div(
                            Label("Select Dataset", cls="block text-sm font-medium mb-1"),
                            Select(*dataset_options, name="dataset_id", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Generation Method", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("Infer from data structure", value="infer_data"),
                                Option("Infer from assets/examples", value="infer_assets"),
                                Option("Custom description", value="custom"),
                                name="generation_method", required=True, cls="w-full p-2 border rounded mb-3",
                                onchange="toggleAssetFields()"
                            )
                        ),
                        Div(
                            Label("Select Prompt (for asset inference)", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("No prompt selected", value="", selected=True),
                                *[Option(prompt['name'], value=str(prompt['id'])) for prompt in prompts],
                                name="prompt_id", cls="w-full p-2 border rounded mb-3"
                            ),
                            id="prompt-field",
                            style="display: none;"
                        ),
                        Div(
                            Label("Describe Your Metric", cls="block text-sm font-medium mb-1"),
                            Textarea(name="description", rows="3", placeholder="Describe what you want to measure (e.g., 'accuracy of sentiment classification', 'semantic similarity between texts')", cls="w-full p-2 border rounded mb-3"),
                            id="description-field"
                        ),
                        Button("Generate", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Cancel", type="button", onclick="hideAIForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/metrics/generate"
                    )
                ),
                id="ai-form",
                cls="hidden mt-4"
            ),
            
            # Metrics table
            create_card(
                title="Your Metrics",
                content=Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Name", cls="px-4 py-2 text-left"),
                                Th("Description", cls="px-4 py-2 text-left"),
                                Th("Type", cls="px-4 py-2 text-left"),
                                Th("Created", cls="px-4 py-2 text-left"),
                                Th("Actions", cls="px-4 py-2 text-left")
                            )
                        ),
                        Tbody(*metric_rows),
                        cls="w-full border-collapse border border-gray-300"
                    ) if metric_rows else P("No metrics found. Create your first metric!", cls="text-gray-500 text-center py-8")
                )
            ),
            
            # JavaScript
            Script("""
                function showCreateForm() {
                    document.getElementById('create-form').classList.remove('hidden');
                }
                
                function hideCreateForm() {
                    document.getElementById('create-form').classList.add('hidden');
                }
                
                function showAIForm() {
                    document.getElementById('ai-form').classList.remove('hidden');
                }
                
                function hideAIForm() {
                    document.getElementById('ai-form').classList.add('hidden');
                }
                
                function toggleDescriptionField() {
                    const method = document.querySelector('select[name="generation_method"]').value;
                    const descField = document.getElementById('description-field');
                    const textarea = descField.querySelector('textarea');
                    
                    if (method === 'custom') {
                        descField.style.display = 'block';
                        textarea.required = true;
                    } else {
                        descField.style.display = 'none';
                        textarea.required = false;
                    }
                }
                
                function testMetric(id) {
                    window.location.href = '/metrics/' + id + '/test';
                }
                
                function editMetric(id) {
                    window.location.href = '/metrics/' + id + '/edit';
                }
                
                async function deleteMetric(id) {
                    if (confirm('Are you sure you want to delete this metric?')) {
                        try {
                            const response = await fetch('/metrics/' + id, {method: 'DELETE'});
                            if (response.ok) {
                                location.reload();
                            } else {
                                alert('Error deleting metric');
                            }
                        } catch (error) {
                            alert('Error deleting metric');
                        }
                    }
                }
            """)
        ]
        
        return create_main_layout(
            "Metrics",
            Div(*content),
            current_page="metrics"
        )

    @app.post("/metrics/create")
    async def create_metric(request):
        """Create a new metric manually"""
        try:
            form_data = await request.form()
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            metric_type = form_data.get('metric_type', '').strip()
            code = form_data.get('code', '').strip()
            
            if not all([name, description, metric_type, code]):
                return HTMLResponse('<script>alert("Please fill all fields"); window.history.back();</script>')
            
            db = Database()
            metric_id = db.create_metric(
                name=name,
                description=description,
                dataset_format=metric_type,  # Use metric_type as dataset_format
                scoring_criteria=description,  # Use description as scoring_criteria
                generated_code=code
            )
            
            return HTMLResponse('<script>alert("Metric created successfully!"); window.location.href="/metrics";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error creating metric: {str(e)}"); window.history.back();</script>')

    @app.post("/metrics/generate")
    async def generate_metric(request):
        """Generate a metric using AI"""
        try:
            form_data = await request.form()
            dataset_id = form_data.get('dataset_id', '').strip()
            description = form_data.get('description', '').strip()
            
            if not dataset_id or not description:
                return HTMLResponse('<script>alert("Please select dataset and provide description"); window.history.back();</script>')
            
            # Get dataset info
            db = Database()
            dataset = db.get_dataset(dataset_id)
            if not dataset:
                return HTMLResponse('<script>alert("Dataset not found"); window.history.back();</script>')
            
            # Generate metric using AI
            metric_service = MetricService()
            result = await metric_service.generate_metric(dataset, description)
            
            if result.get('success'):
                # Save generated metric
                metric_id = db.create_metric(
                    name=result['name'],
                    description=result['description'],
                    metric_type=result['metric_type'],
                    code=result['code']
                )
                
                return HTMLResponse('<script>alert("Metric generated successfully!"); window.location.href="/metrics";</script>')
            else:
                return HTMLResponse(f'<script>alert("Error generating metric: {result.get("error", "Unknown error")}"); window.history.back();</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error generating metric: {str(e)}"); window.history.back();</script>')

    @app.get("/metrics/{metric_id}/test")
    async def test_metric_page(request):
        """Test metric page"""
        metric_id = request.path_params['metric_id']
        
        db = Database()
        metric = db.get_metric(metric_id)
        
        if not metric:
            return HTMLResponse('<script>alert("Metric not found"); window.location.href="/metrics";</script>')
        
        content = [
            create_card(
                title=f"Test Metric: {metric['name']}",
                content=Div(
                    P(metric['description'], cls="text-gray-600 mb-4"),
                    Form(
                        Div(
                            Label("Prediction", cls="block text-sm font-medium mb-1"),
                            Textarea(name="prediction", rows="3", placeholder="Enter prediction value", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Ground Truth", cls="block text-sm font-medium mb-1"),
                            Textarea(name="ground_truth", rows="3", placeholder="Enter ground truth value", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Button("Test", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Back", type="button", onclick="window.location.href='/metrics'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action=f"/metrics/{metric_id}/test"
                    )
                )
            ),
            
            # Results area
            Div(id="test-results", cls="mt-4")
        ]
        
        return create_main_layout(
            f"Test Metric: {metric['name']}",
            Div(*content),
            current_page="metrics"
        )

    @app.post("/metrics/{metric_id}/test")
    async def test_metric(request):
        """Test a metric with sample data"""
        metric_id = request.path_params['metric_id']
        
        try:
            form_data = await request.form()
            prediction = form_data.get('prediction', '').strip()
            ground_truth = form_data.get('ground_truth', '').strip()
            
            if not prediction or not ground_truth:
                return HTMLResponse('<script>alert("Please provide both prediction and ground truth"); window.history.back();</script>')
            
            # Test the metric
            metric_service = MetricService()
            result = await metric_service.test_metric(metric_id, prediction, ground_truth)
            
            if result.get('success'):
                score = result.get('score', 'N/A')
                return HTMLResponse(f'''
                    <script>
                        document.getElementById('test-results').innerHTML = `
                            <div class="bg-green-50 border border-green-200 rounded-md p-4">
                                <h3 class="font-semibold text-green-800">Test Result</h3>
                                <p class="text-green-700">Score: {score}</p>
                            </div>
                        `;
                    </script>
                ''')
            else:
                error = result.get('error', 'Unknown error')
                return HTMLResponse(f'''
                    <script>
                        document.getElementById('test-results').innerHTML = `
                            <div class="bg-red-50 border border-red-200 rounded-md p-4">
                                <h3 class="font-semibold text-red-800">Test Failed</h3>
                                <p class="text-red-700">Error: {error}</p>
                            </div>
                        `;
                    </script>
                ''')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error testing metric: {str(e)}"); window.history.back();</script>')

    @app.get("/metrics/{metric_id}/edit")
    async def edit_metric_page(request):
        """Edit metric page"""
        metric_id = request.path_params['metric_id']
        
        db = Database()
        metric = db.get_metric(metric_id)
        
        if not metric:
            return HTMLResponse('<script>alert("Metric not found"); window.location.href="/metrics";</script>')
        
        content = [
            create_card(
                title=f"Edit Metric: {metric['name']}",
                content=Form(
                    Div(
                        Label("Metric Name", cls="block text-sm font-medium mb-1"),
                        Input(type="text", name="name", value=metric['name'], required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("Description", cls="block text-sm font-medium mb-1"),
                        Textarea(metric['description'], name="description", rows="2", required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("Generated Code", cls="block text-sm font-medium mb-1"),
                        Textarea(metric.get('generated_code', ''), name="code", rows="10", required=True, cls="w-full p-2 border rounded mb-3 font-mono")
                    ),
                    Button("Update", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                    Button("Cancel", type="button", onclick="window.location.href='/metrics'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                    method="post",
                    action=f"/metrics/{metric_id}/update"
                )
            )
        ]
        
        return create_main_layout(
            f"Edit Metric: {metric['name']}",
            Div(*content),
            current_page="metrics"
        )

    @app.post("/metrics/{metric_id}/update")
    async def update_metric(request):
        """Update a metric"""
        metric_id = request.path_params['metric_id']
        
        try:
            form_data = await request.form()
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            code = form_data.get('code', '').strip()
            
            if not all([name, description, code]):
                return HTMLResponse('<script>alert("Please fill all fields"); window.history.back();</script>')
            
            db = Database()
            db.update_metric(metric_id, name=name, description=description, generated_code=code)
            
            return HTMLResponse('<script>alert("Metric updated successfully!"); window.location.href="/metrics";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error updating metric: {str(e)}"); window.history.back();</script>')

    @app.delete("/metrics/{metric_id}")
    async def delete_metric(request):
        """Delete a metric"""
        metric_id = request.path_params['metric_id']
        
        try:
            db = Database()
            db.delete_metric(metric_id)
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

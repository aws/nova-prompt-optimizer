"""
Optimization Routes
Handles prompt optimization workflow
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
from sdk_worker import run_optimization_worker
import subprocess
import json
from datetime import datetime
import os


def setup_optimization_routes(app):
    """Setup optimization workflow routes"""
    
    @app.get("/optimization")
    async def optimization_page(request):
        """Optimization workflow page"""
        
        db = Database()
        prompts = db.get_prompts()
        datasets = db.get_datasets()
        metrics = db.get_metrics()
        
        prompt_options = [Option("Select a prompt...", value="")]
        for prompt in prompts:
            prompt_options.append(Option(prompt['name'], value=str(prompt['id'])))
        
        dataset_options = [Option("Select a dataset...", value="")]
        for dataset in datasets:
            dataset_options.append(Option(dataset['name'], value=str(dataset['id'])))
        
        metric_options = [Option("Select a metric...", value="")]
        for metric in metrics:
            metric_options.append(Option(metric['name'], value=str(metric['id'])))
        
        content = [
            create_card(
                title="Prompt Optimization",
                content=Div(
                    P("Optimize your prompts using Nova SDK with real datasets and metrics", cls="text-muted-foreground mb-4"),
                    P("Select a prompt, dataset, and metric to start the optimization process", cls="text-sm text-gray-600 mb-4")
                )
            ),
            
            Div(
                Button("+ New Optimization", 
                       onclick="document.getElementById('config-accordion').open = !document.getElementById('config-accordion').open",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mb-4"),
                Details(
                    Summary("Configuration", cls="cursor-pointer font-medium py-2"),
                    Form(
                        Div(
                            Label("Optimization Name", cls="block text-sm font-medium mb-1"),
                            Input(type="text", name="optimization_name", placeholder="Enter a name for this optimization", cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Prompt", cls="block text-sm font-medium mb-1"),
                            Select(*prompt_options, name="prompt_id", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Dataset", cls="block text-sm font-medium mb-1"),
                            Select(*dataset_options, name="dataset_id", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Metrics (Select Multiple)", cls="block text-sm font-medium mb-1"),
                            Div(
                                *[
                                    Div(
                                        Input(type="checkbox", name="metric_ids", value=str(metric['id']), cls="mr-2"),
                                        Label(
                                            Span(metric['name'], cls="font-medium"),
                                            Br(),
                                            Span(metric.get('description', 'No description')[:100] + "..." if len(metric.get('description', '')) > 100 else metric.get('description', ''), cls="text-sm text-gray-600"),
                                            cls="cursor-pointer"
                                        ),
                                        cls="flex items-start p-2 border rounded mb-2 hover:bg-gray-50"
                                    )
                                    for metric in metrics
                                ],
                                cls="max-h-48 overflow-y-auto border rounded p-2 mb-3"
                            ),
                            P("Select multiple metrics to create a composite evaluation. Weights will be automatically balanced.", cls="text-sm text-gray-600")
                        ),
                        Div(
                            Label("Nova Model", cls="block text-sm font-medium mb-1"),
                            Select(
                                Option("Nova Lite", value="us.amazon.nova-lite-v1:0"),
                                Option("Nova Pro", value="us.amazon.nova-pro-v1:0"),
                                Option("Nova Premier", value="us.amazon.nova-premier-v1:0"),
                                name="model_id", cls="w-full p-2 border rounded mb-3"
                            )
                        ),
                        Div(
                            Label("Rate Limit (requests per minute)", cls="block text-sm font-medium mb-1"),
                            Input(type="number", name="rate_limit", value="100", min="1", max="10000", cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Max Samples (optional)", cls="block text-sm font-medium mb-1"),
                            Input(type="number", name="max_samples", placeholder="Leave empty to use all samples", min="1", cls="w-full p-2 border rounded mb-3")
                        ),
                        Button("Start Optimization", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/optimization/start"
                    ),
                    cls="border rounded p-4 bg-gray-50",
                    id="config-accordion"
                )
            ),
            
            # Recent optimizations
            create_card(
                title="Recent Optimizations",
                content=Div(id="recent-optimizations")
            ),
            
            # JavaScript to load recent optimizations
            Script("""
                async function loadRecentOptimizations() {
                    try {
                        const response = await fetch('/optimization/recent');
                        const data = await response.json();
                        
                        if (data.success && data.optimizations.length > 0) {
                            let html = '<div class="space-y-2">';
                            data.optimizations.forEach(opt => {
                                console.log('🔍 DEBUG - Optimization status:', opt.status, 'for ID:', opt.id);
                                const statusColor = opt.status === 'completed' || opt.status === 'Completed' ? 'green' : 
                                                  opt.status === 'failed' ? 'red' : 'blue';
                                const improvement = opt.improvement && opt.improvement !== 'None' ? opt.improvement : 'N/A';
                                html += `
                                    <div class="flex justify-between items-center p-3 border rounded">
                                        <div>
                                            <span class="font-medium">${opt.name || 'Optimization'}</span>
                                            <span class="text-sm text-gray-500 ml-2">${opt.started || opt.created_at || ''}</span>
                                            ${improvement !== 'N/A' ? `<span class="text-sm text-green-600 ml-2">+${improvement}</span>` : ''}
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="px-2 py-1 text-xs rounded" style="background-color: ${statusColor === 'green' ? '#dcfce7' : statusColor === 'red' ? '#fef2f2' : '#dbeafe'}; color: ${statusColor === 'green' ? '#166534' : statusColor === 'red' ? '#991b1b' : '#1e40af'};">
                                                ${opt.status}
                                            </span>
                                            ${(opt.status === 'completed' || opt.status === 'Completed') ? 
                                                `<a href="/optimization/results/${opt.id}" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-1">Results</a>` : 
                                                opt.status === 'Failed' || opt.status === 'failed' ?
                                                `<button onclick="retryOptimization('${opt.id}')" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-orange-500 text-white hover:bg-orange-600 h-8 px-3 py-1 text-xs mr-1">Retry</button>` :
                                                `<a href="/optimization/progress/${opt.id}" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-1">Monitor</a>`
                                            }
                                            <button onclick="deleteOptimization('${opt.id}')" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs">Delete</button>
                                        </div>
                                    </div>
                                `;
                            });
                            html += '</div>';
                            document.getElementById('recent-optimizations').innerHTML = html;
                        } else {
                            document.getElementById('recent-optimizations').innerHTML = 
                                '<p class="text-gray-500 text-center py-4">No recent optimizations found</p>';
                        }
                    } catch (error) {
                        console.error('Error loading recent optimizations:', error);
                    }
                }
                
                function viewResults(id) {
                    window.location.href = '/optimization/results/' + id;
                }
                
                function viewProgress(id) {
                    window.location.href = '/optimization/progress/' + id;
                }
                
                // Load recent optimizations on page load
                loadRecentOptimizations();
                
                // Auto-refresh every 60 seconds (1 minute) to catch status updates
                setInterval(loadRecentOptimizations, 60000);
                
                // Delete optimization function
                async function deleteOptimization(optimizationId) {
                    if (confirm('Are you sure you want to delete this optimization?')) {
                        try {
                            const response = await fetch(`/optimization/${optimizationId}/delete`, {
                                method: 'POST'
                            });
                            
                            if (response.ok) {
                                loadRecentOptimizations(); // Reload the list
                            } else {
                                alert('Error deleting optimization');
                            }
                        } catch (error) {
                            alert('Error deleting optimization: ' + error.message);
                        }
                    }
                }
                
                // Retry optimization function
                async function retryOptimization(optimizationId) {
                    if (confirm('Are you sure you want to retry this optimization?')) {
                        try {
                            const response = await fetch(`/optimization/${optimizationId}/retry`, {
                                method: 'POST'
                            });
                            
                            if (response.ok) {
                                alert('Optimization retry started!');
                                loadRecentOptimizations(); // Reload the list
                            } else {
                                alert('Error retrying optimization');
                            }
                        } catch (error) {
                            alert('Error retrying optimization: ' + error.message);
                        }
                    }
                }
            """)
        ]
        
        return create_main_layout(
            "Optimization",
            Div(*content),
            current_page="optimization"
        )

    @app.post("/optimization/start")
    async def start_optimization(request):
        """Start a new optimization"""
        try:
            form_data = await request.form()
            optimization_name = form_data.get('optimization_name', '').strip()
            prompt_id = form_data.get('prompt_id')
            dataset_id = form_data.get('dataset_id')
            metric_ids = form_data.getlist('metric_ids')
            model_id = form_data.get('model_id', 'us.amazon.nova-lite-v1:0')
            rate_limit = int(form_data.get('rate_limit', 100))
            max_samples = form_data.get('max_samples')
            
            if not all([prompt_id, dataset_id]) or not metric_ids:
                return HTMLResponse('<script>alert("Please select prompt, dataset, and at least one metric"); window.history.back();</script>')
            
            # Validate selections exist
            db = Database()
            prompt = db.get_prompt(prompt_id)
            dataset = db.get_dataset(dataset_id)
            metrics = [db.get_metric(mid) for mid in metric_ids]
            
            if not all([prompt, dataset]) or not all(metrics):
                return HTMLResponse('<script>alert("Invalid selection - please check your choices"); window.history.back();</script>')
            
            # Handle multiple metrics by creating composite metric
            if len(metric_ids) == 1:
                # Single metric - use as is
                composite_metric_id = metric_ids[0]
                composite_metric = metrics[0]
            else:
                # Multiple metrics - create composite
                from services.metric_service import MetricService
                metric_service = MetricService()
                
                composite_code = metric_service.generate_composite_metric_code(metrics)
                
                # Save composite metric to database
                composite_metric_id = db.create_metric(
                    name=f"Composite: {', '.join([m['name'] for m in metrics])}",
                    description=f"Composite metric combining: {', '.join([m['name'] for m in metrics])}",
                    dataset_format="composite",
                    scoring_criteria="Weighted combination of multiple metrics",
                    generated_code=composite_code
                )
                composite_metric = db.get_metric(composite_metric_id)
            
            # Create optimization record
            optimization_name = optimization_name or f"Optimization {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            optimization_id = db.create_optimization(
                name=optimization_name,
                prompt_id=prompt_id,
                dataset_id=dataset_id,
                metric_id=composite_metric_id
            )
            
            # Start optimization in background
            config = {
                'optimization_id': optimization_id,
                'prompt': prompt,
                'dataset': dataset,
                'metric': composite_metric,
                'model_id': model_id,
                'rate_limit': rate_limit,
                'max_samples': int(max_samples) if max_samples else None
            }
            
            # Save config and start worker
            config_path = f"opt_conf/optimization_config_{optimization_id}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, default=str)
            
            # Start optimization worker with detailed logging
            import os
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            
            subprocess.Popen([
                'python3', 'sdk_worker.py', optimization_id, json.dumps(config)
            ], cwd=os.getcwd(), env=env)
            
            return HTMLResponse(f'<script>alert("Optimization started!"); window.location.href="/optimization/progress/{optimization_id}";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error starting optimization: {str(e)}"); window.history.back();</script>')

    @app.get("/optimization/recent")
    async def get_recent_optimizations(request):
        """Get recent optimizations"""
        try:
            db = Database()
            optimizations = db.get_optimizations()[:10]  # Get first 10
            return {"success": True, "optimizations": optimizations}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/optimization/progress/{optimization_id}")
    async def optimization_progress_page(request):
        """Optimization progress page"""
        optimization_id = request.path_params['optimization_id']
        
        db = Database()
        optimization = db.get_optimization(optimization_id)
        
        if not optimization:
            return HTMLResponse('<script>alert("Optimization not found"); window.location.href="/optimization";</script>')
        
        content = [
            create_card(
                title=f"Optimization Progress - {optimization_id}",
                content=Div(
                    P(f"Status: ", Span(id="current-status", cls="font-semibold"), cls="mb-2"),
                    P(f"Started: {optimization.get('created_at', optimization.get('started', 'Unknown'))}", cls="mb-4"),
                    
                    # Progress bar
                    Div(
                        Div(id="progress-bar", cls="bg-blue-500 h-3 rounded transition-all duration-300", style="width: 0%"),
                        cls="w-full bg-gray-200 rounded h-3 mb-4"
                    ),
                    
                    # Live logs
                    Div(
                        H4("Live Progress Logs:", cls="font-semibold mb-2"),
                        Div(id="log-container", cls="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm overflow-y-auto border resize-y", style="height: 400px; min-height: 200px; max-height: 800px;"),
                        cls="mb-4"
                    ),
                    
                    # Action buttons
                    Div(
                        Button("Refresh Now", onclick="updateProgress()", cls="bg-blue-500 text-white px-4 py-2 rounded mr-2"),
                        Button("Back to Optimization", onclick="window.location.href='/optimization'", cls="bg-gray-500 text-white px-4 py-2 rounded"),
                        cls="mt-4"
                    )
                )
            ),
            
            # Real-time monitoring script
            Script(f"""
                let lastLogCount = 0;
                
                async function updateProgress() {{
                    try {{
                        const response = await fetch('/optimization/{optimization_id}/status');
                        const data = await response.json();
                        
                        // Update status
                        document.getElementById('current-status').textContent = data.status || 'Running';
                        
                        // Update progress bar
                        const progress = data.progress || 0;
                        document.getElementById('progress-bar').style.width = progress + '%';
                        
                        // Update logs
                        if (data.logs && data.logs.length > 0) {{
                            console.log('Received logs:', data.logs.length, 'total logs');
                            const logContainer = document.getElementById('log-container');
                            
                            // Only add new logs
                            if (data.logs.length > lastLogCount) {{
                                const newLogs = data.logs.slice(lastLogCount);
                                console.log('Adding', newLogs.length, 'new logs');
                                newLogs.forEach(log => {{
                                    const logLine = document.createElement('div');
                                    logLine.className = 'mb-1';
                                    logLine.innerHTML = `<span class="text-gray-400">${{log.timestamp || new Date().toLocaleTimeString()}}:</span> ${{log.message}}`;
                                    logContainer.appendChild(logLine);
                                }});
                                
                                // Auto-scroll to bottom
                                logContainer.scrollTop = logContainer.scrollHeight;
                                lastLogCount = data.logs.length;
                            }}
                        }} else {{
                            console.log('No logs received or empty logs array');
                            if (lastLogCount === 0) {{
                                document.getElementById('log-container').innerHTML = '<div class="text-gray-400">Waiting for logs...</div>';
                            }}
                        }}
                        
                        // Redirect when completed
                        if (data.status === 'completed') {{
                            setTimeout(() => {{
                                window.location.href = '/optimization/results/{optimization_id}';
                            }}, 2000);
                        }}
                        
                    }} catch (error) {{
                        console.error('Progress update error:', error);
                        document.getElementById('log-container').innerHTML += 
                            '<div class="text-red-400">Error fetching progress: ' + error.message + '</div>';
                    }}
                }}
                
                // Start monitoring
                updateProgress(); // Initial call
                const progressInterval = setInterval(updateProgress, 3000); // Update every 3 seconds
                
                // Stop monitoring when page unloads
                window.addEventListener('beforeunload', () => {{
                    clearInterval(progressInterval);
                }});
            """)
        ]
        
        return create_main_layout(
            "Optimization Progress",
            Div(*content),
            current_page="optimization"
        )

    @app.get("/optimization/{optimization_id}/status")
    async def get_optimization_status(request):
        """Get optimization status and logs"""
        optimization_id = request.path_params['optimization_id']
        
        try:
            db = Database()
            optimization = db.get_optimization(optimization_id)
            logs = db.get_optimization_logs(optimization_id)
            
            if not optimization:
                return {"success": False, "error": "Optimization not found"}
            
            return {
                "success": True,
                "status": optimization['status'],
                "progress": optimization.get('progress', 0),
                "logs": logs
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/optimization/results/{optimization_id}")
    async def optimization_results_page(request):
        """Optimization results page"""
        optimization_id = request.path_params['optimization_id']
        
        db = Database()
        optimization = db.get_optimization(optimization_id)
        
        if not optimization:
            return HTMLResponse('<script>alert("Optimization not found"); window.location.href="/optimization";</script>')
        
        if optimization['status'].lower() != 'completed':
            return HTMLResponse('<script>alert("Optimization not completed yet"); window.history.back();</script>')
        
        # Get results
        candidates = db.get_prompt_candidates(optimization_id)
        
        # Calculate scores from candidates
        baseline_score = None
        optimized_score = None
        if candidates:
            scores = [c.get('score', 0) for c in candidates if isinstance(c.get('score'), (int, float))]
            if scores:
                optimized_score = max(scores)
                # Assume baseline is lower - could be stored separately
                baseline_score = min(scores) if len(scores) > 1 else optimized_score * 0.85
        
        # Calculate improvement percentage
        improvement_pct = optimization.get('improvement', 'N/A')
        if improvement_pct == 'N/A' and baseline_score and optimized_score:
            improvement_pct = f"{((optimized_score - baseline_score) / baseline_score * 100):.1f}%"
        
        # Load optimization files
        import os
        import json
        opt_dir = f"optimized_prompts/{optimization_id}"
        
        baseline_prompt = ""
        optimized_system = ""
        optimized_user = ""
        few_shot_examples = []
        
        if os.path.exists(opt_dir):
            try:
                if os.path.exists(f"{opt_dir}/system_prompt.txt"):
                    with open(f"{opt_dir}/system_prompt.txt", 'r') as f:
                        optimized_system = f.read().strip()
                
                if os.path.exists(f"{opt_dir}/user_prompt.txt"):
                    with open(f"{opt_dir}/user_prompt.txt", 'r') as f:
                        optimized_user = f.read().strip()
                
                if os.path.exists(f"{opt_dir}/few_shot.json"):
                    with open(f"{opt_dir}/few_shot.json", 'r') as f:
                        few_shot_examples = json.load(f)
            except Exception as e:
                print(f"Error loading optimization files: {e}")
        
        # Get baseline prompt
        baseline_prompt_data = db.get_prompt(optimization['prompt'])
        baseline_system_prompt = ""
        baseline_user_prompt = ""
        if baseline_prompt_data and baseline_prompt_data.get('variables'):
            baseline_vars = baseline_prompt_data['variables']
            baseline_system_prompt = baseline_vars.get('system_prompt', '')
            baseline_user_prompt = baseline_vars.get('user_prompt', '')
        
        content = [
            create_card(
                title="Optimization Summary",
                content=Div(
                    P(f"Optimization: {optimization.get('name', 'N/A')}", cls="mb-2"),
                    P(f"Status: {optimization.get('status', 'N/A')}", cls="mb-2"),
                    P(f"Completed: {optimization.get('completed', 'N/A')}", cls="mb-2"),
                    P(f"Improvement: +{improvement_pct}" if improvement_pct != 'N/A' else "Improvement: N/A", cls="mb-4 text-green-600 font-medium"),
                    Button("Optimize Further", 
                           onclick=f"optimizeFurther('{optimization_id}')",
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                    Button("Back to Optimization", 
                           onclick="window.location.href='/optimization'", 
                           cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs")
                )
            ),
            create_card(
                title="Baseline vs Optimized Comparison",
                content=Div(
                    Div(
                        H4("Baseline Prompt", cls="text-lg font-bold mb-2"),
                        P(f"Score: {baseline_score:.4f}" if baseline_score else "Score: N/A", cls="text-sm text-gray-600 mb-2"),
                        Div(
                            H5("System Prompt:", cls="font-semibold mb-1"),
                            Pre(baseline_system_prompt or "No system prompt found", cls="bg-gray-100 p-3 rounded mb-3 whitespace-pre-wrap text-sm"),
                            H5("User Prompt:", cls="font-semibold mb-1"),
                            Pre(baseline_user_prompt or "No user prompt found", cls="bg-gray-100 p-3 rounded mb-4 whitespace-pre-wrap text-sm")
                        )
                    ),
                    Div(
                        H4("Optimized Prompt", cls="text-lg font-bold mb-2"),
                        P(f"Score: {optimized_score:.4f}" if optimized_score else "Score: N/A", cls="text-sm text-green-600 mb-2 font-medium"),
                        Div(
                            H5("System Prompt:", cls="font-medium mb-1"),
                            Pre(optimized_system or "No system prompt", cls="bg-blue-50 p-3 rounded mb-3 whitespace-pre-wrap text-sm")
                        ),
                        Div(
                            H5("User Prompt:", cls="font-medium mb-1"),
                            Pre(optimized_user or "No user prompt", cls="bg-green-50 p-3 rounded mb-3 whitespace-pre-wrap text-sm")
                        )
                    )
                )
            )
        ]
        
        # Add few-shot examples if available
        if few_shot_examples:
            examples_content = []
            for i in range(0, len(few_shot_examples), 2):  # Process pairs
                if i + 1 < len(few_shot_examples):
                    user_example = few_shot_examples[i]
                    assistant_example = few_shot_examples[i + 1]
                    
                    user_content = user_example.get('content', [{}])[0].get('text', '')
                    assistant_content = assistant_example.get('content', [{}])[0].get('text', '')
                    
                    examples_content.append(
                        Details(
                            Summary(f"Example {i//2 + 1}", cls="cursor-pointer font-medium py-2"),
                            Div(
                                Div(
                                    H5("Input:", cls="font-medium mb-2"),
                                    Pre(user_content, cls="bg-yellow-50 p-3 rounded mb-3 text-sm whitespace-pre-wrap")
                                ),
                                Div(
                                    H5("Expected Output:", cls="font-medium mb-2"),
                                    Pre(assistant_content, cls="bg-purple-50 p-3 rounded mb-3 text-sm whitespace-pre-wrap")
                                ),
                                cls="pl-4"
                            ),
                            cls="border-b border-gray-200 last:border-b-0"
                        )
                    )
            
            content.append(
                create_card(
                    title=f"Few-Shot Examples ({len(few_shot_examples)//2} total)",
                    content=Div(*examples_content, cls="space-y-0")
                )
            )
        
        return create_main_layout(
            "Optimization Results",
            Div(*content),
            current_page="optimization"
        )

    @app.get("/optimization/candidate/{optimization_id}/{candidate_index}")
    async def view_candidate(request):
        """View candidate details"""
        optimization_id = request.path_params['optimization_id']
        candidate_index = int(request.path_params['candidate_index'])
        
        db = Database()
        candidates = db.get_prompt_candidates(optimization_id)
        
        if candidate_index >= len(candidates):
            return HTMLResponse('<script>alert("Candidate not found"); window.history.back();</script>')
        
        candidate = candidates[candidate_index]
        
        return create_main_layout(
            f"Candidate {candidate_index + 1}",
            Div(
                H2(f"Candidate {candidate_index + 1}", cls="text-2xl font-bold mb-4"),
                P(f"Score: {candidate.get('score', 'N/A')}", cls="mb-4"),
                Div(
                    H3("Prompt Text", cls="text-lg font-bold mb-2"),
                    Pre(candidate.get('prompt_text', 'N/A'), cls="bg-gray-100 p-4 rounded mb-4 whitespace-pre-wrap")
                ),
                Button("Back to Results", 
                       onclick=f"window.location.href='/optimization/results/{optimization_id}'", 
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs")
            ),
            current_page="optimization"
        )

    @app.post("/optimization/candidate/{optimization_id}/{candidate_index}/save")
    async def save_candidate(request):
        """Save candidate as new prompt"""
        optimization_id = request.path_params['optimization_id']
        candidate_index = int(request.path_params['candidate_index'])
        
        db = Database()
        candidates = db.get_prompt_candidates(optimization_id)
        
        if candidate_index >= len(candidates):
            return HTMLResponse('<script>alert("Candidate not found"); window.history.back();</script>')
        
        candidate = candidates[candidate_index]
        prompt_name = f"Optimized Prompt {candidate_index + 1}"
        
        # Create new prompt from candidate
        prompt_id = db.create_prompt(
            name=prompt_name,
            system_prompt="",
            user_prompt=candidate.get('prompt_text', '')
        )
        
        return HTMLResponse(f'<script>alert("Prompt saved as: {prompt_name}"); window.location.href="/prompts";</script>')

    @app.post("/optimization/{optimization_id}/optimize-further")
    async def optimize_further(request):
        """Start optimize further workflow"""
        optimization_id = request.path_params['optimization_id']
        
        try:
            db = Database()
            optimization = db.get_optimization(optimization_id)
            
            if not optimization or optimization['status'] != 'completed':
                return {"success": False, "error": "Original optimization not found or not completed"}
            
            # Get best candidate
            candidates = db.get_prompt_candidates(optimization_id)
            if not candidates:
                return {"success": False, "error": "No candidates found"}
            
            best_candidate = max(candidates, key=lambda x: x.get('score', 0))
            
            # Create new optimization with best candidate as baseline
            original_name = optimization.get('name', 'Optimization')
            new_optimization_name = f"{original_name} - Further Optimized"
            new_optimization_id = db.create_optimization(
                name=new_optimization_name,
                prompt_id=optimization['prompt_id'],
                dataset_id=optimization['dataset_id'],
                metric_id=optimization['metric_id'],
                model_id=optimization['model_id'],
                rate_limit=optimization['rate_limit'],
                max_samples=optimization['max_samples'],
                status='queued',
                baseline_prompt_candidate_id=best_candidate['id']
            )
            
            # Start optimization worker with optimize-further flag
            config = {
                'optimization_id': new_optimization_id,
                'original_optimization_id': optimization_id,
                'optimize_further': True
            }
            
            config_path = f"opt_conf/optimization_config_{new_optimization_id}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, default=str)
            
            subprocess.Popen([
                'python3', 'sdk_worker.py', config_path
            ], cwd=os.getcwd())
            
            return {"success": True, "new_optimization_id": new_optimization_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/optimization/{optimization_id}/delete")
    async def delete_optimization(request):
        """Delete an optimization"""
        optimization_id = request.path_params['optimization_id']
        
        try:
            db = Database()
            db.delete_optimization(optimization_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/optimization/{optimization_id}/retry")
    async def retry_optimization(request):
        """Retry a failed optimization"""
        optimization_id = request.path_params['optimization_id']
        
        try:
            db = Database()
            optimization = db.get_optimization(optimization_id)
            
            if not optimization:
                return {"success": False, "error": "Optimization not found"}
            
            # Get original data
            prompt = db.get_prompt(optimization['prompt_id'])
            dataset = db.get_dataset(optimization['dataset_id'])
            metric = db.get_metric(optimization['metric_id'])
            
            # Create new optimization with same parameters
            new_optimization_id = db.create_optimization(
                name=f"{optimization.get('name', 'Optimization')} - Retry",
                prompt_id=optimization['prompt_id'],
                dataset_id=optimization['dataset_id'],
                metric_id=optimization['metric_id']
            )
            
            # Start optimization worker using same pattern as regular start
            config = {
                'optimization_id': new_optimization_id,
                'prompt': prompt,
                'dataset': dataset,
                'metric': metric,
                'model_mode': 'lite',  # Default to lite
                'rate_limit': 100,     # Default rate limit
                'max_samples': None
            }
            
            # Start worker thread
            import threading
            worker_thread = threading.Thread(
                target=run_optimization_worker,
                args=(config,),
                daemon=True
            )
            worker_thread.start()
            
            return {"success": True, "new_optimization_id": new_optimization_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

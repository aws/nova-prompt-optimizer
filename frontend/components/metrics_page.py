"""
Metrics page component for Nova Prompt Optimizer
"""

from fasthtml.common import *
from components.ui import *

def create_metrics_page(metrics, datasets=None):
    """Create the metrics management page"""
    if datasets is None:
        datasets = []
    
    return Div(
        # Header section
        create_metrics_header(),
        
        # Create metric section (hidden by default)
        create_metric_creation_section(datasets),
        
        # Metrics list section (at bottom)
        create_metrics_list_section(metrics),
        
        # JavaScript for functionality
        Script("""
            // Tab switching
            document.addEventListener('DOMContentLoaded', function() {
                const tabTriggers = document.querySelectorAll('.tab-trigger');
                const tabPanels = document.querySelectorAll('.tab-panel');
                
                tabTriggers.forEach(trigger => {
                    trigger.addEventListener('click', function() {
                        const targetTab = this.getAttribute('data-tab');
                        
                        // Remove active class from all triggers and panels
                        tabTriggers.forEach(t => t.classList.remove('active'));
                        tabPanels.forEach(p => p.classList.remove('active'));
                        
                        // Add active class to clicked trigger
                        this.classList.add('active');
                        
                        // Show corresponding panel
                        const targetPanel = document.querySelector(`[data-tab-panel="${targetTab}"]`);
                        if (targetPanel) {
                            targetPanel.classList.add('active');
                        }
                    });
                });
            });
            
            function showCreateForm() {
                document.getElementById('create-metric-section').style.display = 'block';
                document.getElementById('create-metric-btn').style.display = 'none';
            }
            
            function hideCreateForm() {
                document.getElementById('create-metric-section').style.display = 'none';
                document.getElementById('create-metric-btn').style.display = 'block';
                // Reset form
                document.querySelector('[data-field="metric-name"]').value = '';
                document.querySelector('[data-field="metric-description"]').value = '';
                document.querySelector('[data-field="natural-language-input"]').value = '';
                document.querySelector('[data-field="model-selection"]').value = '';
                // Hide preview
                document.getElementById('code-preview-container').style.display = 'none';
                document.getElementById('code-actions').style.display = 'none';
            }
            
            function previewMetricCode() {
                const name = document.querySelector('[data-field="metric-name"]').value;
                const description = document.querySelector('[data-field="metric-description"]').value;
                const naturalLanguage = document.querySelector('[data-field="natural-language-input"]').value;
                const modelId = document.querySelector('[data-field="model-selection"]').value;
                
                if (!name || !naturalLanguage || !modelId) {
                    alert('Please fill in metric name, description, and select a model');
                    return;
                }
                
                fetch('/metrics/preview', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams({
                        name: name,
                        description: description,
                        natural_language: naturalLanguage,
                        model_id: modelId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        document.getElementById('code-preview').textContent = data.code;
                        document.getElementById('code-preview-container').style.display = 'block';
                        document.getElementById('code-actions').style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Error generating preview: ' + error);
                });
            }
            
            function editDescription() {
                document.getElementById('code-preview-container').style.display = 'none';
                document.getElementById('code-actions').style.display = 'none';
            }
            
            function createMetric() {
                const name = document.querySelector('[data-field="metric-name"]').value;
                const description = document.querySelector('[data-field="metric-description"]').value;
                const naturalLanguage = document.querySelector('[data-field="natural-language-input"]').value;
                const modelId = document.querySelector('[data-field="model-selection"]').value;
                
                if (!name || !naturalLanguage || !modelId) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                // Determine if we're editing or creating
                const isEditing = window.editingMetricId;
                const url = isEditing ? `/metrics/update/${window.editingMetricId}` : '/metrics/create';
                const successMessage = isEditing ? 'Metric updated successfully!' : 'Metric created successfully!';
                
                fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams({
                        name: name,
                        description: description,
                        natural_language: naturalLanguage,
                        model_id: modelId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Error: ' + data.error);
                    } else {
                        alert(successMessage);
                        // Reset form and hide
                        hideCreateForm();
                        window.editingMetricId = null;
                        // Reload page to show updated list
                        window.location.reload();
                    }
                })
                .catch(error => {
                    alert('Error saving metric: ' + error);
                });
            }
            
            function editMetric(metricId) {
                // Get metric data and populate form
                fetch(`/metrics/${metricId}`)
                    .then(response => response.json())
                    .then(metric => {
                        // Show create form
                        showCreateForm();
                        
                        // Populate form fields
                        document.querySelector('[data-field="metric-name"]').value = metric.name;
                        document.querySelector('[data-field="metric-description"]').value = metric.description || '';
                        document.querySelector('[data-field="natural-language-input"]').value = metric.natural_language_input || '';
                        
                        // Update createMetric function to handle updates
                        window.editingMetricId = metricId;
                    })
                    .catch(error => {
                        alert('Error loading metric: ' + error);
                    });
            }
            
            function deleteMetric(metricId, metricName) {
                if (confirm(`Are you sure you want to delete "${metricName}"?`)) {
                    fetch(`/metrics/delete/${metricId}`, {
                        method: 'POST'
                    })
                    .then(response => {
                        if (response.ok) {
                            alert('Metric deleted successfully!');
                            window.location.reload();
                        } else {
                            alert('Error deleting metric');
                        }
                    })
                    .catch(error => {
                        alert('Error deleting metric: ' + error);
                    });
                }
            }
        """),
        
        cls="metrics-page"
    )

def create_metrics_header():
    """Create the metrics page header"""
    
    return Div(
        Div(
            H1("Metrics", cls="text-2xl font-bold"),
            P("Create and manage custom evaluation metrics for your prompts", 
              cls="text-muted-foreground mt-2"),
            cls="flex-1"
        ),
        
        Button("+ Create New Metric", 
               onclick="showCreateForm()",
               id="create-metric-btn",
               cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"),
        
        cls="flex items-center justify-between mb-6"
    )

def create_metric_creation_section(datasets=None):
    """Create the metric creation section (hidden by default)"""
    if datasets is None:
        datasets = []
    
    return Div(
        Div(
            Button("Cancel", 
                   onclick="hideCreateForm()",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 mb-4"),
            
            # Tab system
            create_metric_tabs(datasets),
            
            cls="bg-white p-6 rounded-lg border"
        ),
        
        style="display: none;",
        id="create-metric-section",
        cls="mb-8"
    )

def create_metrics_list_section(metrics):
    """Create the metrics list section with optimization-style layout"""
    
    return Div(
        H2("Your Metrics", cls="text-xl font-semibold mb-4"),
        
        Div(
            *[create_metric_list_item(metric) for metric in metrics] if metrics else [
                P("No metrics created yet. Click 'Create New Metric' to get started!", 
                  cls="text-gray-500 text-center py-8")
            ]
        ),
        
        cls="metrics-list-section"
    )

def create_metric_list_item(metric):
    """Create a single metric list item similar to optimization jobs"""
    
    return Div(
        Div(
            Div(
                H4(metric['name'], cls="font-semibold text-lg mb-1"),
                P(metric['description'] or "No description", 
                  cls="text-gray-600 text-sm mb-2"),
                P(f"Format: {metric['dataset_format'].upper()} • Created: {metric['created'][:10]}", 
                  cls="text-gray-500 text-xs"),
                cls="flex-1"
            ),
            
            Div(
                Button("Edit", 
                       onclick=f"editMetric('{metric['id']}')",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"
                ),
                Button("Delete", 
                       onclick=f"deleteMetric('{metric['id']}', '{metric['name']}')",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-8 px-3 py-1 text-xs"
                ),
                cls="flex gap-2"
            ),
            
            cls="flex justify-between items-start"
        ),
        
        cls="p-4 border rounded-lg mb-3 hover:bg-gray-50"
    )

def create_metrics_list(metrics):
    """Create the metrics list section"""
    
    if not metrics:
        return create_empty_metrics_state()
    
    metric_cards = [create_metric_card(metric) for metric in metrics]
    
    return Div(
        H2("Your Metrics", cls="text-xl font-semibold mb-4"),
        
        Div(
            *metric_cards,
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        ),
        
        cls="metrics-list"
    )

def create_empty_metrics_state():
    """Create empty state when no metrics exist"""
    
    return Div(
        Div(
            Div("📏", cls="text-6xl mb-4"),
            H3("No metrics yet", cls="text-xl font-semibold mb-2"),
            P("Create your first custom evaluation metric to get started", 
              cls="text-muted-foreground mb-6"),
            cls="text-center"
        ),
        cls="flex items-center justify-center min-h-96 bg-muted/50 rounded-lg border-2 border-dashed"
    )

def create_metric_card(metric):
    """Create a single metric card"""
    
    # Format usage info
    usage_text = f"Used {metric['usage_count']} times"
    if metric['last_used']:
        usage_text += f" • Last used {metric['last_used'][:10]}"
    
    return Article(
        Header(
            H3(metric['name'], cls="font-semibold text-lg"),
            P(metric['description'] or "No description", 
              cls="text-sm text-muted-foreground mt-1"),
        ),
        
        Div(
            Span(metric['dataset_format'].upper(), 
                 cls="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary"),
            P(usage_text, cls="text-xs text-muted-foreground mt-2"),
            cls="mt-4"
        ),
        
        Footer(
            Div(
                Button("Edit", 
                       onclick=f"editMetric('{metric['id']}')",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs",
                       **{"data-action": "edit-metric", "data-metric-id": metric['id']}),
                Button("Delete", 
                       onclick=f"deleteMetric('{metric['id']}', '{metric['name']}')",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-8 px-3 py-1 text-xs ml-2",
                       **{"data-action": "delete-metric", "data-metric-id": metric['id']}),
                cls="flex gap-2"
            ),
            cls="mt-4 pt-4 border-t"
        ),
        
        cls="metric-card bg-card p-4 rounded-lg border hover:shadow-md transition-shadow"
    )

def create_metric_modal(datasets=None):
    """Create the metric creation/editing modal"""
    if datasets is None:
        datasets = []
    
    return Div(
        Div(
            # Modal header
            Div(
                H2("Create New Metric", cls="text-xl font-semibold"),
                Button("×", cls="text-2xl hover:bg-muted rounded p-1",
                       **{"data-action": "close-modal"}),
                cls="flex justify-between items-center mb-6"
            ),
            
            # Tab system
            create_metric_tabs(datasets),
            
            # Modal footer
            Div(
                Button("Cancel", 
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2",
                       **{"data-action": "close-modal"}),
                Button("Create Metric", 
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 ml-3",
                       **{"data-action": "save-metric"}),
                cls="flex justify-end gap-3 mt-6 pt-6 border-t"
            ),
            
            cls="bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        ),
        
        cls="metric-modal fixed inset-0 bg-black/50 flex items-center justify-center z-50 hidden",
        **{"data-ref": "metric-modal"}
    )

def create_metric_tabs(datasets=None):
    """Create the single-tab interface for metric creation - Infer from Assets only"""
    if datasets is None:
        datasets = []
    
    return Div(
        # Single tab header
        Div(
            H4("Infer Metrics from Assets", cls="text-lg font-medium text-gray-900 mb-4"),
            P("Analyze your dataset and prompts to automatically generate appropriate evaluation metrics.", 
              cls="text-sm text-gray-600 mb-6"),
            cls="border-b pb-4 mb-6"
        ),
        
        # Tab content - only infer from dataset
        Div(
            create_infer_dataset_tab(datasets),
            cls="tab-content"
        ),
        
        cls="metric-tabs"
    )

def create_infer_dataset_tab(datasets=None):
    """Create the infer from dataset tab"""
    if datasets is None:
        datasets = []
    
    # Get prompts for the prompt selection dropdown
    from database import Database
    db = Database()
    prompts = db.get_prompts()
    
    # Create dataset options
    dataset_options = [Option("Choose a dataset...", value="", selected=True, disabled=True)]
    for dataset in datasets:
        dataset_options.append(
            Option(f"{dataset['name']} ({dataset['rows']} rows)", value=dataset['id'])
        )
    
    # Create prompt options
    prompt_options = [Option("No prompt selected", value="", selected=True)]
    for prompt in prompts:
        prompt_options.append(
            Option(f"{prompt['name']}", value=prompt['id'])
        )
    
    return Div(
        H3("Infer Metrics from Assets", cls="text-xl font-semibold mb-4"),
        P("AI will analyze your dataset and prompt to suggest appropriate evaluation metrics based on the data structure, content, and task intent.", 
          cls="text-gray-600 mb-6"),
        
        Form(
            Div(
                Label("Metric Name", cls="block text-sm font-medium mb-2"),
                Input(
                    type="text",
                    name="metric_name",
                    placeholder="e.g., Dataset Quality Metrics",
                    required=True,
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                cls="mb-6"
            ),
            
            Div(
                Label("Select Dataset", cls="block text-sm font-medium mb-2"),
                Select(
                    *dataset_options,
                    name="dataset_id",
                    required=True,
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                cls="mb-6"
            ),
            
            Div(
                Label("Select Prompt (Optional)", cls="block text-sm font-medium mb-2"),
                P("Analyzing the original prompt helps understand the intended task and evaluation criteria.", cls="text-sm text-gray-600 mb-2"),
                Select(
                    *prompt_options,
                    name="prompt_id",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                cls="mb-6"
            ),
            
            Div(
                Label("Analysis Depth", cls="block text-sm font-medium mb-2"),
                Select(
                    Option("Quick Analysis (5 samples)", value="quick"),
                    Option("Standard Analysis (20 samples)", value="standard", selected=True),
                    Option("Deep Analysis (50 samples)", value="deep"),
                    name="analysis_depth",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                cls="mb-6"
            ),
            
            Div(
                Label("Model Selection", cls="block text-sm font-medium mb-2"),
                Select(
                    Option("Amazon Nova Premier (Best Quality)", value="us.amazon.nova-premier-v1:0", selected=True),
                    Option("Amazon Nova Pro (Balanced)", value="us.amazon.nova-pro-v1:0"),
                    Option("Amazon Nova Lite (Fastest)", value="us.amazon.nova-lite-v1:0"),
                    name="model_id",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                cls="mb-6"
            ),
            
            Div(
                Label("API Rate Limit (RPM)", cls="block text-sm font-medium mb-2"),
                Input(
                    type="number",
                    name="rate_limit",
                    value="60",
                    min="1",
                    max="1000",
                    placeholder="60",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                ),
                P("Enter requests per minute (1-1000). Lower values reduce throttling risk.", 
                  cls="text-sm text-gray-500 mt-1"),
                cls="mb-6"
            ),
            
            Button(
                "Analyze Dataset & Generate Metrics",
                type="submit",
                id="generate-btn",
                cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 w-full"
            ),
            
            # Simplified JavaScript - just log, don't interfere
            Script("""
                document.addEventListener('DOMContentLoaded', function() {
                    const form = document.querySelector('form[action="/metrics/infer-from-dataset"]');
                    if (form) {
                        form.addEventListener('submit', function(e) {
                            console.log('📤 Form submitting to:', this.action);
                            const btn = document.getElementById('generate-btn');
                            if (btn) {
                                btn.innerHTML = 'Processing... Please wait';
                                btn.disabled = true;
                            }
                        });
                    }
                });
            """),
            
            method="post",
            action="/metrics/infer-from-dataset",
            cls="space-y-4"
        ),
        
        cls="tab-panel",
        id="infer-assets",
        style="display: none;"
    )

# Natural language tab removed - focusing only on "Infer from Assets"

def create_code_preview_section():
    """Create the code preview section"""
    
    return Div(
        H4("Generated Code Preview:", cls="font-medium mb-2"),
        Pre(
            Code(
                "# Metric code will appear here after you describe your evaluation criteria...",
                cls="text-sm",
                **{"data-ref": "code-preview"}
            ),
            cls="bg-gray-100 p-4 rounded border text-sm overflow-x-auto max-h-64"
        ),
        
        cls="code-preview-section"
    )

# Add the import to app.py
def add_metrics_import():
    """Helper to add the import statement"""
    return "from components.metrics_page import create_metrics_page"

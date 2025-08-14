"""
Metrics page component for Nova Prompt Optimizer
"""

from fasthtml.common import *
from components.ui import *

def create_metrics_styles():
    """Create CSS styles for metrics page"""
    return Style("""
        .metrics-page {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .metric-card {
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .tab-trigger {
            padding: 0.75rem 1.5rem;
            border-bottom: 2px solid transparent;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            color: #64748b;
            transition: all 0.2s ease;
        }
        
        .tab-trigger.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-trigger:hover {
            color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .tab-panel {
            display: none;
        }
        
        .tab-panel.active {
            display: block;
        }
            display: block;
        }
        
        .example-prompt {
            padding: 0.5rem 1rem;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 0.375rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .example-prompt:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            transition: border-color 0.2s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .button-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .button-secondary {
            background: transparent;
            color: #667eea;
            border: 1px solid #667eea;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .button-secondary:hover {
            background: #667eea;
            color: white;
        }
        
        @media (max-width: 768px) {
            .metrics-page {
                padding: 1rem;
            }
            
            .flex {
                flex-direction: column;
                gap: 1rem;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
        }
    """)

def create_metrics_page(metrics, datasets=None):
    """Create the metrics management page"""
    if datasets is None:
        datasets = []
    
    return Div(
        # Add styles
        create_metrics_styles(),
        
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
    """Create the two-tab interface for metric creation"""
    if datasets is None:
        datasets = []
    
    # Add CSS for full width card content
    style_tag = Style("""
        .card-content {
            width: 100% !important;
            max-width: none !important;
        }
    """)
    
    return Div(
        style_tag,
        # Tab triggers
        Div(
            A("Natural Language", 
              cls="nav-tab-trigger active",
              **{"data-tab": "natural-language", "role": "tab", "aria-selected": "true"}),
            Div(cls="border-l border-gray-300 h-6"),  # Separator
            A("Infer from Assets",
              cls="nav-tab-trigger",
              **{"data-tab": "infer-assets", "role": "tab", "aria-selected": "false"}),
            cls="flex items-center gap-4 border-b mb-6",
            style="display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 1.5rem;"
        ),
        
        # Tab contents
        Div(
            # Natural Language tab
            create_natural_language_tab(),
            
            # Infer from Dataset tab
            create_infer_dataset_tab(datasets),
            
            cls="tab-content"
        ),
        
        # Add JavaScript for tab functionality
        Script("""
            // Tab switching functionality for metrics tabs only
            document.addEventListener('DOMContentLoaded', function() {
                const metricTabTriggers = document.querySelectorAll('.nav-tab-trigger[data-tab]');
                const tabPanels = document.querySelectorAll('.tab-panel');
                
                console.log('Found metric tab triggers:', metricTabTriggers.length);
                console.log('Found tab panels:', tabPanels.length);
                
                metricTabTriggers.forEach(trigger => {
                    trigger.addEventListener('click', function(e) {
                        e.preventDefault();
                        const targetTab = this.getAttribute('data-tab');
                        
                        if (!targetTab) return; // Skip if no data-tab attribute
                        
                        console.log('Switching to tab:', targetTab);
                        
                        // Remove active class from metric tab triggers only
                        metricTabTriggers.forEach(t => {
                            t.classList.remove('active');
                            t.setAttribute('aria-selected', 'false');
                        });
                        tabPanels.forEach(p => {
                            p.classList.remove('active');
                            p.style.display = 'none';
                        });
                        
                        // Add active class to clicked trigger
                        this.classList.add('active');
                        this.setAttribute('aria-selected', 'true');
                        
                        // Show corresponding panel
                        const targetPanel = document.getElementById(targetTab);
                        console.log('Target panel:', targetPanel);
                        if (targetPanel) {
                            targetPanel.classList.add('active');
                            targetPanel.style.display = 'block';
                            console.log('Showed panel:', targetTab);
                        }
                    });
                });
            });
        """),
        
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

def create_natural_language_tab():
    """Create the natural language input tab"""
    
    return Div(
        Div(
            Label("Metric Name", cls="block text-sm font-medium mb-2"),
            Input(type="text", placeholder="e.g., Sentiment Analysis Metric",
                  cls="form-input w-full", name="name", **{"data-field": "metric-name"}),
            cls="mb-4"
        ),
        
        Div(
            Label("Description (Optional)", cls="block text-sm font-medium mb-2"),
            Input(type="text", placeholder="Brief description of what this metric evaluates",
                  cls="form-input w-full", name="description", **{"data-field": "metric-description"}),
            cls="mb-4"
        ),
        
        Div(
            Label("Model Selection", cls="block text-sm font-medium mb-2"),
            Select(
                Option("Select a model...", value="", disabled=True, selected=True),
                Option("Amazon Nova Premier", value="us.amazon.nova-premier-v1:0"),
                Option("Amazon Nova Pro", value="us.amazon.nova-pro-v1:0"),
                Option("Amazon Nova Lite", value="us.amazon.nova-lite-v1:0"),
                name="model_id",
                cls="form-input w-full",
                **{"data-field": "model-selection"}
            ),
            cls="mb-4"
        ),
        
        Div(
            Label("Natural Language Description", cls="block text-sm font-medium mb-2"),
            Textarea(
                placeholder="Describe how you want to evaluate your outputs...\n\nExamples:\n• Score based on correct sentiment and urgency classification\n• Evaluate JSON output for category accuracy and completeness\n• Check if response contains required fields and proper format",
                rows="8",
                cls="form-input w-full",
                name="natural_language",
                **{"data-field": "natural-language-input"}
            ),
            cls="mb-4"
        ),
        
        # Preview button
        Div(
            Button("Preview Generated Code", 
                   type="button",
                   onclick="previewMetricCode()",
                   cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-full"),
            cls="mb-4"
        ),
        
        # Code preview area (initially hidden)
        Div(
            Label("Generated Code Preview", cls="block text-sm font-medium mb-2"),
            Pre(
                Code("", id="code-preview", cls="language-python"),
                cls="bg-gray-100 p-4 rounded border max-h-96 overflow-y-auto",
                style="display: none;",
                id="code-preview-container"
            ),
            Div(
                Button("Accept & Create Metric", 
                       type="button",
                       onclick="createMetric()",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mr-2"),
                Button("Edit Description", 
                       type="button",
                       onclick="editDescription()",
                       cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"),
                style="display: none;",
                id="code-actions"
            ),
            cls="mb-4"
        ),
        cls="natural-language-tab tab-panel active",
        id="natural-language",
        style="display: block;"
    )

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

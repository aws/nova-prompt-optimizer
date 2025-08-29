"""
Dataset Generator Routes
Handles AI-powered dataset generation
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
from sample_generator import SampleGeneratorService as SampleGenerator
import json


def setup_dataset_generator_routes(app):
    """Setup dataset generator routes"""
    
    @app.get("/datasets/generator")
    async def dataset_generator_page(request):
        """AI Dataset Generator page"""
        
        content = [
            create_card(
                title="AI Dataset Generator",
                content=Div(
                    P("Generate synthetic datasets using conversational AI", cls="text-muted-foreground mb-4"),
                    P("Describe your dataset needs and let AI create realistic sample data for prompt optimization", cls="text-sm text-gray-600")
                )
            ),
            
            create_card(
                title="Start Conversation",
                content=Div(
                    Div(id="conversation-container", cls="mb-4"),
                    Div(
                        Input(
                            placeholder="Describe the dataset you need (e.g., 'customer support emails with sentiment labels')",
                            id="user-input",
                            cls="flex-1 p-2 border border-input rounded-md mr-2"
                        ),
                        Button("Send", onclick="sendMessage()", cls="px-4 py-2 bg-primary text-primary-foreground rounded-md"),
                        cls="flex"
                    ),
                    id="conversation-section"
                )
            ),
            
            # Model Selection (hidden initially)
            Div(
                create_card(
                    title="Select AI Model",
                    content=Div(
                        P("Choose the AI model for dataset generation:", cls="mb-3"),
                        Div(
                            *[
                                Label(
                                    Input(type="radio", name="model", value=model, cls="mr-2"),
                                    model,
                                    cls="block mb-2 cursor-pointer"
                                ) for model in ["us.amazon.nova-micro-v1:0", "us.amazon.nova-lite-v1:0", "us.amazon.nova-pro-v1:0"]
                            ]
                        ),
                        Button("Continue", onclick="proceedToGeneration()", cls="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"),
                        id="model-selection-content"
                    )
                ),
                id="model-selection",
                cls="hidden"
            ),
            
            # Sample Generation (hidden initially)
            Div(
                create_card(
                    title="Generating Dataset Samples",
                    content=Div(
                        Div(
                            Div("Progress", cls="flex justify-between text-sm text-gray-600 mb-1"),
                            Div(
                                Span("0 / 0 samples", id="progress-text"),
                                cls="text-sm text-gray-600"
                            )
                        ),
                        Div(
                            Div(id="progress-bar", cls="bg-blue-600 h-2 rounded-full transition-all duration-300", style="width: 0%"),
                            cls="w-full bg-gray-200 rounded-full h-2 mb-4"
                        ),
                        Div("Starting generation...", id="generation-status", cls="text-sm text-gray-600"),
                        id="progress-container"
                    )
                ),
                id="sample-generation", 
                cls="hidden"
            ),
            
            # JavaScript
            Script("""
                let currentSessionId = null;
                let progressInterval = null;

                async function sendMessage() {
                    const input = document.getElementById('user-input');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    addMessageToConversation('user', message);
                    input.value = '';
                    
                    try {
                        const response = await fetch('/datasets/generator/start-conversation', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: `message=${encodeURIComponent(message)}`
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            currentSessionId = result.session_id;
                            addMessageToConversation('assistant', result.response);
                            
                            if (result.ready_for_generation) {
                                showModelSelection();
                            }
                        } else {
                            addMessageToConversation('assistant', 'Error: ' + result.error);
                        }
                    } catch (error) {
                        addMessageToConversation('assistant', 'Error: ' + error.message);
                    }
                }

                function addMessageToConversation(role, message) {
                    const container = document.getElementById('conversation-container');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `mb-3 p-3 rounded-md ${role === 'user' ? 'bg-blue-50 ml-8' : 'bg-gray-50 mr-8'}`;
                    messageDiv.innerHTML = `<strong>${role === 'user' ? 'You' : 'AI'}:</strong> ${message}`;
                    container.appendChild(messageDiv);
                    container.scrollTop = container.scrollHeight;
                }

                function showModelSelection() {
                    document.getElementById('model-selection').classList.remove('hidden');
                }

                async function proceedToGeneration() {
                    const selectedModel = document.querySelector('input[name="model"]:checked');
                    if (!selectedModel) {
                        alert('Please select a model');
                        return;
                    }
                    
                    // Show progress bar
                    document.getElementById('sample-generation').classList.remove('hidden');
                    
                    // Start progress monitoring
                    startProgressMonitoring();
                    
                    try {
                        const response = await fetch('/datasets/generator/generate-samples', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: `session_id=${currentSessionId}&model_id=${selectedModel.value}`
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            stopProgressMonitoring();
                            updateProgressBar(100, 100, 'completed');
                        } else {
                            stopProgressMonitoring();
                            document.getElementById('generation-status').innerHTML = `<span class="text-red-600">Error: ${result.error}</span>`;
                        }
                    } catch (error) {
                        stopProgressMonitoring();
                        document.getElementById('generation-status').innerHTML = `<span class="text-red-600">Error: ${error.message}</span>`;
                    }
                }

                function startProgressMonitoring() {
                    progressInterval = setInterval(async () => {
                        try {
                            const response = await fetch(`/datasets/generator/progress/${currentSessionId}`);
                            const progress = await response.json();
                            
                            updateProgressBar(progress.current || 0, progress.total || 100, progress.status || 'generating');
                        } catch (error) {
                            console.error('Error fetching progress:', error);
                        }
                    }, 1000);
                }

                function stopProgressMonitoring() {
                    if (progressInterval) {
                        clearInterval(progressInterval);
                        progressInterval = null;
                    }
                }

                function updateProgressBar(current, total, status) {
                    const progressBar = document.getElementById('progress-bar');
                    const progressText = document.getElementById('progress-text');
                    const statusDiv = document.getElementById('generation-status');
                    
                    if (total > 0) {
                        const percentage = Math.round((current / total) * 100);
                        progressBar.style.width = `${percentage}%`;
                        progressText.textContent = `${current} / ${total} samples`;
                        
                        if (status === 'completed') {
                            statusDiv.innerHTML = '<span class="text-green-600">Generation completed!</span>';
                        } else if (status === 'error') {
                            statusDiv.innerHTML = '<span class="text-red-600">Generation failed</span>';
                        } else {
                            statusDiv.textContent = `${status}... (${current}/${total})`;
                        }
                    }
                }

                // Allow Enter key to send message
                document.addEventListener('DOMContentLoaded', function() {
                    const input = document.getElementById('user-input');
                    if (input) {
                        input.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                sendMessage();
                            }
                        });
                    }
                });
            """)
        ]
        
        return create_main_layout(
            "AI Dataset Generator",
            Div(*content),
            current_page="datasets"
        )

    @app.post("/datasets/generator/start-conversation")
    async def start_conversation(request):
        """Start AI conversation for dataset requirements"""
        try:
            form_data = await request.form()
            user_message = form_data.get('message', '').strip()
            
            if not user_message:
                return {"success": False, "error": "Please provide a message"}
            
            # Initialize conversation with sample generator
            generator = SampleGenerator()
            session_id = f"conv_{hash(user_message) % 100000}"
            
            # Start conversation
            response = await generator.start_conversation(user_message, session_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "ai_response": response.get("ai_response", ""),
                "ready_for_generation": response.get("ready_for_generation", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/datasets/generator/continue-conversation")
    async def continue_conversation(request):
        """Continue AI conversation"""
        try:
            form_data = await request.form()
            session_id = form_data.get('session_id', '')
            user_message = form_data.get('message', '').strip()
            
            if not session_id or not user_message:
                return {"success": False, "error": "Missing session or message"}
            
            generator = SampleGenerator()
            response = await generator.continue_conversation(session_id, user_message)
            
            return {
                "success": True,
                "ai_response": response.get("ai_response", ""),
                "ready_for_generation": response.get("ready_for_generation", False)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/datasets/generator/progress/{session_id}")
    async def get_generation_progress(session_id: str):
        """Get generation progress for a session"""
        try:
            # Check if there's a progress file for this session
            progress_file = f"data/generation_progress_{session_id}.json"
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                return progress
            else:
                return {"current": 0, "total": 0, "status": "not_started"}
        except Exception as e:
            return {"current": 0, "total": 0, "status": "error", "error": str(e)}

    @app.post("/datasets/generator/generate-samples")
    async def generate_samples(request):
        """Generate initial samples"""
        try:
            form_data = await request.form()
            session_id = form_data.get('session_id', '')
            model_id = form_data.get('model_id', 'us.amazon.nova-micro-v1:0')
            
            if not session_id:
                return {"success": False, "error": "Missing session ID"}
            
            generator = SampleGenerator(model_id=model_id)
            
            # Get generation config from conversation
            generation_config = generator.get_generation_config(session_id)
            if not generation_config:
                return {"success": False, "error": "No generation configuration found"}
            
            # Generate samples
            result = generator.generate_initial_samples(generation_config, session_id)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/datasets/generator/improve-samples")
    async def improve_samples(request):
        """Improve samples based on user feedback"""
        try:
            form_data = await request.form()
            session_id = form_data.get('session_id', '')
            annotations_json = form_data.get('annotations', '[]')
            
            if not session_id:
                return {"success": False, "error": "Missing session ID"}
            
            annotations = json.loads(annotations_json)
            if not annotations:
                return {"success": False, "error": "No annotations provided"}
            
            generator = SampleGenerator()
            result = generator.improve_samples(session_id, annotations)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/datasets/generator/generate-more")
    async def generate_more_samples(request):
        """Generate additional samples"""
        try:
            form_data = await request.form()
            session_id = form_data.get('session_id', '')
            num_samples = int(form_data.get('num_samples', 5))
            
            if not session_id:
                return {"success": False, "error": "Missing session ID"}
            
            generator = SampleGenerator()
            result = generator.generate_more_samples(session_id, num_samples)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/datasets/generator/finalize")
    async def finalize_dataset(request):
        """Finalize and save generated dataset"""
        try:
            form_data = await request.form()
            session_id = form_data.get('session_id', '')
            dataset_name = form_data.get('dataset_name', '').strip()
            
            if not session_id or not dataset_name:
                return {"success": False, "error": "Missing session ID or dataset name"}
            
            generator = SampleGenerator()
            result = generator.finalize_dataset(session_id, dataset_name)
            
            if result.get("success"):
                # Save to database
                db = Database()
                
                # Get file info
                file_path = result.get("file_path", "")
                file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB" if file_path and os.path.exists(file_path) else "0 KB"
                row_count = len(result.get("samples", []))
                
                dataset_id = db.create_dataset(
                    name=dataset_name,
                    file_type="CSV",
                    file_size=file_size,
                    row_count=row_count,
                    file_path=file_path
                )
                
                return {
                    "success": True,
                    "dataset_id": dataset_id,
                    "message": "Dataset saved successfully"
                }
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

"""
Simple Optimizer Routes
Handles prompt optimization without datasets
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
import json
import boto3


def setup_simple_optimizer_routes(app):
    """Setup simple optimizer routes"""
    
    @app.get("/simple-optimizer")
    async def simple_optimizer_page(request):
        """Simple prompt optimizer page"""
        
        # Get existing prompts for loading
        db = Database()
        existing_prompts = db.get_prompts()[:50]  # Get first 50
        
        prompt_options = [Option("Select a prompt to load...", value="", selected=True)]
        for prompt in existing_prompts:
            variables = prompt.get('variables', {})
            
            # Handle both dictionary and list formats for variables
            if isinstance(variables, dict):
                system_prompt = variables.get('system_prompt', '')
            else:
                # Legacy format - variables is a list
                system_prompt = ', '.join(variables) if variables else ''
                
            preview = system_prompt[:50] + '...' if len(system_prompt) > 50 else system_prompt
            prompt_options.append(Option(f"{prompt['name']} - {preview}", value=str(prompt['id'])))
        
        content = [
            # Header
            create_card(
                title="Simple Prompt Optimizer",
                content=Div(
                    P("Transform any prompt to follow Nova SDK best practices without requiring a dataset", 
                      cls="text-muted-foreground mb-4"),
                    P("Load an existing prompt or paste a new one, then optimize it using Nova's proven patterns", 
                      cls="text-sm text-gray-600")
                )
            ),
            
            # Input Section
            create_card(
                title="Your Current Prompt",
                content=Div(
                    # Load existing prompt option
                    Div(
                        Label("Load Existing Prompt (Optional)", cls="block text-sm font-medium mb-2"),
                        Select(
                            *prompt_options,
                            id="existing-prompt-select",
                            cls="w-full p-2 border border-input rounded-md mb-4",
                            onchange="loadExistingPrompt()"
                        ),
                        cls="mb-4"
                    ),
                    
                    # Manual input form
                    Form(
                        Input(type="hidden", name="existing_prompt_id", id="existing-prompt-id", value=""),
                        Label("System Prompt", cls="block text-sm font-medium mb-2"),
                        Textarea(
                            placeholder="Enter system instructions (optional)...",
                            name="system_prompt",
                            id="system-prompt",
                            rows="4",
                            cls="w-full p-3 border border-input rounded-md mb-4"
                        ),
                        Label("User Prompt", cls="block text-sm font-medium mb-2"),
                        Textarea(
                            placeholder="Enter user prompt template...",
                            name="user_prompt",
                            id="user-prompt",
                            rows="6",
                            cls="w-full p-3 border border-input rounded-md mb-4"
                        ),
                        Button("Optimize Prompt", 
                               type="submit",
                               id="optimize-btn",
                               cls="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"),
                        method="post",
                        action="/simple-optimizer/optimize"
                    )
                )
            ),
            
            # Results Section (initially hidden)
            Div(id="optimization-results", cls="hidden"),
            
            # JavaScript for loading existing prompts
            Script("""
                async function loadExistingPrompt() {
                    const select = document.getElementById('existing-prompt-select');
                    const systemPrompt = document.getElementById('system-prompt');
                    const userPrompt = document.getElementById('user-prompt');
                    const hiddenId = document.getElementById('existing-prompt-id');
                    
                    if (select.value) {
                        hiddenId.value = select.value;
                        try {
                            const response = await fetch(`/prompts/${select.value}`);
                            const data = await response.json();
                            
                            if (data.success) {
                                const prompt = data.prompt;
                                let fullPrompt = '';
                                
                                if (prompt.system_prompt) {
                                    fullPrompt += 'SYSTEM: ' + prompt.system_prompt + '\\n\\n';
                                }
                                if (prompt.user_prompt) {
                                    fullPrompt += 'USER: ' + prompt.user_prompt;
                                }
                                
                                systemPrompt.value = prompt.system_prompt || '';
                                userPrompt.value = prompt.user_prompt || '';
                            }
                        } catch (error) {
                            console.error('Error loading prompt:', error);
                            alert('Error loading prompt');
                        }
                    } else {
                        hiddenId.value = '';
                        systemPrompt.value = '';
                        userPrompt.value = '';
                    }
                }
                
                // Handle form submission with processing state
                document.addEventListener('DOMContentLoaded', function() {
                    const form = document.querySelector('form[method="post"]');
                    const btn = document.getElementById('optimize-btn');
                    
                    if (form && btn) {
                        form.addEventListener('submit', function() {
                            btn.textContent = 'Optimizing...';
                            btn.disabled = true;
                            btn.classList.add('opacity-50', 'cursor-not-allowed');
                        });
                    }
                });
            """)
        ]
        
        return create_main_layout(
            "Simple Prompt Optimizer",
            Div(*content),
            current_page="prompts"
        )

    @app.post("/simple-optimizer/optimize")
    async def optimize_simple_prompt(request):
        """Optimize a prompt using Nova best practices"""
        try:
            form_data = await request.form()
            system_prompt = form_data.get('system_prompt', '').strip()
            user_prompt = form_data.get('user_prompt', '').strip()
            existing_prompt_id = form_data.get('existing_prompt_id', '').strip()
            
            # If using existing prompt, load it from database
            if existing_prompt_id and not system_prompt and not user_prompt:
                db = Database()
                existing_prompt = db.get_prompt(existing_prompt_id)
                if existing_prompt:
                    variables = existing_prompt.get('variables', {})
                    if isinstance(variables, dict):
                        system_prompt = variables.get('system_prompt', '')
                        user_prompt = variables.get('user_prompt', '')
            
            if not system_prompt and not user_prompt:
                return HTMLResponse('<script>alert("Please provide at least one prompt (system or user)"); history.back();</script>')
            
            # Combine prompts for optimization
            original_prompt = ""
            if system_prompt:
                original_prompt += f"SYSTEM: {system_prompt}\n\n"
            if user_prompt:
                original_prompt += f"USER: {user_prompt}"
            
            # Simple prompt optimization using AI
            try:
                print(f"Starting optimization for prompt: {original_prompt[:100]}...")
                optimized_result = await optimize_prompt_structure(original_prompt)
                print(f"Optimization completed: {optimized_result}")
            except Exception as e:
                print(f"Optimization error: {e}")
                return HTMLResponse('<script>alert("Error during optimization. Please try again."); history.back();</script>')
            
            # Return optimized prompt with analysis and save option
            results_html = create_optimization_results(original_prompt, optimized_result)
            
            return HTMLResponse(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Optimization Results</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-50 p-8">
                    <div class="max-w-4xl mx-auto">
                        <h1 class="text-2xl font-bold mb-6">Prompt Optimization Results</h1>
                        {results_html}
                        <div class="mt-6">
                            <a href="/simple-optimizer" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                ← Back to Optimizer
                            </a>
                        </div>
                    </div>
                </body>
                </html>
            """)
            
        except Exception as e:
            return HTMLResponse(f"""
                <script>
                    alert('Error optimizing prompt: {str(e)}');
                </script>
            """)

    @app.post("/simple-optimizer/save")
    async def save_optimized_prompt(request):
        """Save optimized prompt to database"""
        try:
            form_data = await request.form()
            prompt_name = form_data.get('prompt_name', '').strip()
            system_prompt = form_data.get('system_prompt', '').strip()
            user_prompt = form_data.get('user_prompt', '').strip()
            
            if not prompt_name or (not system_prompt and not user_prompt):
                return {"success": False, "error": "Please provide both name and at least one prompt"}
            
            # Save to database
            db = Database()
            prompt_id = db.create_prompt(
                name=prompt_name,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            return HTMLResponse(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Prompt Saved</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-50 p-8">
                    <div class="max-w-4xl mx-auto">
                        <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                            <h1 class="text-xl font-bold text-green-800 mb-2">✅ Prompt Saved Successfully!</h1>
                            <p class="text-green-700">Your optimized prompt "{prompt_name}" has been saved to the database.</p>
                        </div>
                        <div class="space-x-4">
                            <a href="/simple-optimizer" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                                ← Back to Optimizer
                            </a>
                            <a href="/prompts" class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
                                View All Prompts
                            </a>
                        </div>
                    </div>
                </body>
                </html>
            """)
            
        except Exception as e:
            return HTMLResponse(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Save Error</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-50 p-8">
                    <div class="max-w-4xl mx-auto">
                        <div class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                            <h1 class="text-xl font-bold text-red-800 mb-2">❌ Error Saving Prompt</h1>
                            <p class="text-red-700">{str(e)}</p>
                        </div>
                        <a href="/simple-optimizer" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                            ← Back to Optimizer
                        </a>
                    </div>
                </body>
                </html>
            """)


async def optimize_prompt_structure(original_prompt: str) -> dict:
    """Use AI to restructure prompt following Nova best practices"""
    
    optimization_prompt = f"""
    You are a Nova SDK prompt optimization expert. Analyze this prompt and restructure it to follow Nova's best practices:

    ORIGINAL PROMPT:
    {original_prompt}

    NOVA OPTIMIZATION REQUIREMENTS:
    1. TASK: Clear, specific action with measurable outcome
    2. CONTEXT: Domain knowledge, constraints, audience specification  
    3. INSTRUCTIONS: Specific behavioral rules using directive language
    4. RESPONSE FORMAT: Structured output requirements
    5. VARIABLES: Reusable placeholders where applicable

    Provide your response in this JSON format:
    {{
        "optimized_prompt": "The restructured prompt following Nova patterns",
        "improvements": [
            "List of specific improvements made",
            "Each improvement should explain the Nova principle applied"
        ],
        "structure_analysis": {{
            "task": "Extracted/improved task definition",
            "context": ["Context elements identified/added"],
            "instructions": ["Behavioral rules identified/added"], 
            "response_format": "Output format requirements",
            "variables": ["Variables that could be used"]
        }}
    }}
    """
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        response = bedrock.invoke_model(
            modelId='us.amazon.nova-pro-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": optimization_prompt}]}],
                "inferenceConfig": {"maxTokens": 2000, "temperature": 0.3}
            })
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['output']['message']['content'][0]['text']
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            clean_response = ai_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.startswith('```'):
                clean_response = clean_response[3:]   # Remove ```
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]  # Remove trailing ```
            clean_response = clean_response.strip()
            
            return json.loads(clean_response)
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return {
                "optimized_prompt": ai_response,
                "improvements": ["AI response was not in expected JSON format"],
                "explanation": "The AI provided optimization suggestions but not in the expected structured format."
            }
        
    except Exception as e:
        print(f"Error in prompt optimization: {e}")
        return {
            "optimized_prompt": "Error occurred during optimization",
            "improvements": ["Unable to optimize prompt"],
            "structure_analysis": {}
        }


def create_optimization_results(original: str, result: dict) -> str:
    """Create HTML for optimization results with save option"""
    
    improvements_html = "".join([f"<li class='mb-2'>{imp}</li>" for imp in result.get('improvements', [])])
    optimized_prompt = result.get('optimized_prompt', '')
    
    # Parse original prompt to separate SYSTEM and USER parts
    original_system = ""
    original_user = ""
    if "SYSTEM:" in original and "USER:" in original:
        parts = original.split("USER:", 1)
        original_system = parts[0].replace("SYSTEM:", "").strip()
        original_user = parts[1].strip()
    elif "SYSTEM:" in original:
        original_system = original.replace("SYSTEM:", "").strip()
    else:
        original_user = original.strip()
    
    # Parse optimized prompt to separate SYSTEM and USER parts
    opt_system = ""
    opt_user = ""
    if "SYSTEM:" in optimized_prompt and "USER:" in optimized_prompt:
        parts = optimized_prompt.split("USER:", 1)
        opt_system = parts[0].replace("SYSTEM:", "").strip()
        opt_user = parts[1].strip()
    elif "SYSTEM:" in optimized_prompt:
        opt_system = optimized_prompt.replace("SYSTEM:", "").strip()
    else:
        opt_user = optimized_prompt.strip()
    
    # Build HTML sections
    original_system_html = ""
    if original_system:
        original_system_html = f'''
        <div class="mb-4">
            <h5 class="text-sm font-medium text-gray-600 mb-2">SYSTEM:</h5>
            <div class="bg-red-50 border border-red-200 rounded-md p-3">
                <pre class="whitespace-pre-wrap text-sm">{original_system}</pre>
            </div>
        </div>'''
    
    original_user_html = ""
    if original_user:
        original_user_html = f'''
        <div>
            <h5 class="text-sm font-medium text-gray-600 mb-2">USER:</h5>
            <div class="bg-red-50 border border-red-200 rounded-md p-3">
                <pre class="whitespace-pre-wrap text-sm">{original_user}</pre>
            </div>
        </div>'''
    
    opt_system_html = ""
    if opt_system:
        opt_system_html = f'''
        <div class="mb-4">
            <h5 class="text-sm font-medium text-gray-600 mb-2">SYSTEM:</h5>
            <div class="bg-green-50 border border-green-200 rounded-md p-3">
                <pre class="whitespace-pre-wrap text-sm">{opt_system}</pre>
            </div>
        </div>'''
    
    opt_user_html = ""
    if opt_user:
        opt_user_html = f'''
        <div>
            <h5 class="text-sm font-medium text-gray-600 mb-2">USER:</h5>
            <div class="bg-green-50 border border-green-200 rounded-md p-3">
                <pre class="whitespace-pre-wrap text-sm">{opt_user}</pre>
            </div>
        </div>'''
    
    return f"""
    <div class="space-y-6">
        <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Prompt Comparison</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-medium mb-3 text-red-700">Original Prompt</h4>
                    {original_system_html}
                    {original_user_html}
                </div>
                
                <div>
                    <h4 class="font-medium mb-3 text-green-700">Optimized Prompt</h4>
                    {opt_system_html}
                    {opt_user_html}
                </div>
            </div>
            
            <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                <h4 class="font-medium mb-3">Save Optimized Prompt</h4>
                <form method="post" action="/simple-optimizer/save" class="space-y-3">
                    <div>
                        <label class="block text-sm font-medium mb-1">Prompt Name</label>
                        <input type="text" name="prompt_name" required 
                               placeholder="Enter a name for this optimized prompt"
                               class="w-full p-2 border border-input rounded-md text-sm">
                    </div>
                    <input type="hidden" name="system_prompt" value="{opt_system.replace('"', '&quot;')}">
                    <input type="hidden" name="user_prompt" value="{opt_user.replace('"', '&quot;')}">
                    <button type="submit" 
                            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm">
                        Save to Database
                    </button>
                </form>
            </div>
        </div>
        
        <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Nova Improvements Applied</h3>
            <ul class="list-disc list-inside space-y-1 text-sm">
                {improvements_html}
            </ul>
        </div>
    </div>
    """

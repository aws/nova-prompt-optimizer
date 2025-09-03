"""
Prompt Generator Routes
AI-powered prompt generation from datasets using Nova SDK best practices
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
from services.prompt_generator_service import PromptGeneratorService


def setup_prompt_generator_routes(app):
    """Setup prompt generator routes"""
    
    @app.get("/prompt-generator")
    async def prompt_generator_page(request):
        """Prompt Generator page"""
        
        db = Database()
        datasets = db.get_datasets()
        
        content = [
            create_card(
                title="AI Prompt Generator",
                content=Div(
                    P("Generate optimized prompts from your datasets using Nova SDK best practices", cls="text-muted-foreground mb-4"),
                    P("The AI analyzes your dataset structure and creates prompts optimized for your specific use case", cls="text-sm text-gray-600")
                )
            ),
            
            create_card(
                title="Generate Optimized Prompt",
                content=Form(
                    Div(
                        Label("Select Dataset", cls="block text-sm font-medium mb-1"),
                        Select(
                            Option("Choose a dataset...", value="", disabled=True, selected=True),
                            *[Option(dataset['name'], value=str(dataset['id'])) for dataset in datasets],
                            name="dataset_id", required=True, cls="w-full p-2 border rounded mb-3"
                        )
                    ),
                    Div(
                        Label("Prompt Name", cls="block text-sm font-medium mb-1"),
                        Input(type="text", name="prompt_name", placeholder="e.g., 'Customer Support Classifier'", required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("Task Description", cls="block text-sm font-medium mb-1"),
                        Textarea(name="task_description", rows="3", placeholder="Describe what this prompt should accomplish (e.g., 'classify customer support emails by urgency and category')", required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Button("Generate Prompt", type="submit", cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"),
                    Button("Back to Prompts", onclick="window.location.href='/prompts'", type="button", cls="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"),
                    method="post",
                    action="/prompt-generator/generate"
                )
            ),
            
            Div(id="results", cls="mt-6")
        ]
        
        return create_main_layout(
            "AI Prompt Generator",
            Div(*content),
            current_page="prompts"
        )

    @app.post("/prompt-generator/generate")
    async def generate_prompt(request):
        """Generate optimized prompt from dataset"""
        try:
            form_data = await request.form()
            dataset_id = form_data.get('dataset_id')
            prompt_name = form_data.get('prompt_name', '').strip()
            task_description = form_data.get('task_description', '').strip()
            
            if not dataset_id or not prompt_name or not task_description:
                return Div("Please fill in all fields", cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md")
            
            db = Database()
            dataset = db.get_dataset(dataset_id)
            
            if not dataset:
                return Div("Dataset not found", cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md")
            
            # Generate optimized prompt
            generator = PromptGeneratorService()
            result = generator.generate_optimized_prompt(
                dataset_path=dataset['file_path'],
                task_description=task_description,
                prompt_name=prompt_name
            )
            
            if result['success']:
                # Save generated prompt
                prompt_id = db.create_prompt(
                    name=prompt_name,
                    system_prompt=result['system_prompt'],
                    user_prompt=result['user_prompt']
                )
                
                return create_card(
                    title="✅ Prompt Generated Successfully!",
                    content=Div(
                        P(f"Generated optimized prompt: '{prompt_name}'", cls="text-green-600 font-semibold mb-4"),
                        
                        Div(
                            H4("System Prompt:", cls="font-semibold mb-2"),
                            Pre(result['system_prompt'], cls="bg-gray-50 p-3 rounded text-sm mb-4 whitespace-pre-wrap")
                        ),
                        
                        Div(
                            H4("User Prompt:", cls="font-semibold mb-2"),
                            Pre(result['user_prompt'], cls="bg-gray-50 p-3 rounded text-sm mb-4 whitespace-pre-wrap")
                        ),
                        
                        Div(
                            Button("View All Prompts", onclick="window.location.href='/prompts'", cls="px-4 py-2 bg-primary text-primary-foreground rounded mr-2"),
                            Button("Generate Another", onclick="window.location.href='/prompt-generator'", cls="px-4 py-2 border rounded"),
                            cls="mt-4"
                        )
                    )
                )
            else:
                return Div(f"Error generating prompt: {result['error']}", cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md")
                
        except Exception as e:
            return Div(f"Error: {str(e)}", cls="text-red-600 p-4 bg-red-50 border border-red-200 rounded-md")

"""
Prompt Management Routes
Handles prompt CRUD operations
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card


def setup_prompt_routes(app):
    """Setup prompt management routes"""
    
    @app.get("/prompts")
    async def prompts_page(request):
        """Prompts management page"""
        
        db = Database()
        prompts = db.get_prompts()
        
        prompt_rows = []
        for prompt in prompts:
            variables = prompt.get('variables', {})
            
            # Handle both dictionary and list formats for variables
            if isinstance(variables, dict):
                system_prompt = variables.get('system_prompt', '')
                user_prompt = variables.get('user_prompt', '')
            else:
                # Legacy format - variables is a list
                system_prompt = ''
                user_prompt = ', '.join(variables) if variables else ''
            
            prompt_rows.append(
                Tr(
                    Td(prompt['name'], cls="px-4 py-2"),
                    Td(prompt['created'], cls="px-4 py-2"),
                    Td(
                        Button("Edit", onclick=f"editPrompt('{prompt['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-1"),
                        Button("Delete", onclick=f"deletePrompt('{prompt['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="px-4 py-2"
                    )
                )
            )
        
        content = [
            # Header with actions
            create_card(
                title="Prompt Management",
                content=Div(
                    P("Create and manage prompts for optimization", cls="text-muted-foreground mb-4"),
                    Div(
                        Button("Add Existing Prompt", onclick="showCreateForm('prompt')", id="create-prompt-btn", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Prompt Builder", onclick="window.location.href='/prompt-builder'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"),
                        Button("Prompt Generator", onclick="window.location.href='/prompt-generator'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"),
                        Button("Simple Optimizer", onclick="window.location.href='/simple-optimizer'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="flex gap-2"
                    )
                )
            ),
            
            # Create form (hidden)
            Div(
                create_card(
                    title="Create New Prompt",
                    content=Form(
                        Div(
                            Label("Prompt Name", cls="block text-sm font-medium mb-1"),
                            Input(type="text", name="name", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("System Prompt", cls="block text-sm font-medium mb-1"),
                            Textarea(name="system_prompt", rows="4", placeholder="System instructions for the AI", cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("User Prompt", cls="block text-sm font-medium mb-1"),
                            Textarea(name="user_prompt", rows="4", placeholder="User prompt template (use {variables} for placeholders)", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Description", cls="block text-sm font-medium mb-1"),
                            Textarea(name="description", rows="2", placeholder="Optional description", cls="w-full p-2 border rounded mb-3")
                        ),
                        Button("Create", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Cancel", type="button", onclick="hideCreateForm('prompt')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/prompts/create"
                    )
                ),
                id="create-prompt-form",
                cls="hidden mt-4"
            ),
            
            # Prompts table
            create_card(
                title="Your Prompts",
                content=Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Name", cls="px-4 py-2 text-left"),
                                Th("Created", cls="px-4 py-2 text-left"),
                                Th("Actions", cls="px-4 py-2 text-left")
                            )
                        ),
                        Tbody(*prompt_rows),
                        cls="w-full border-collapse border border-gray-300"
                    ) if prompt_rows else P("No prompts found. Create your first prompt!", cls="text-gray-500 text-center py-8")
                )
            ),
            
            # JavaScript
            Script("""
                function showCreateForm(type) {
                    document.getElementById('create-' + type + '-form').classList.remove('hidden');
                    document.getElementById('create-' + type + '-btn').style.display = 'none';
                }
                
                function hideCreateForm(type) {
                    document.getElementById('create-' + type + '-form').classList.add('hidden');
                    document.getElementById('create-' + type + '-btn').style.display = 'inline-block';
                }
                
                function editPrompt(id) {
                    window.location.href = '/prompts/' + id + '/edit';
                }
                
                async function deletePrompt(id) {
                    if (confirm('Are you sure you want to delete this prompt?')) {
                        try {
                            const response = await fetch('/prompts/' + id, {method: 'DELETE'});
                            if (response.ok) {
                                location.reload();
                            } else {
                                alert('Error deleting prompt');
                            }
                        } catch (error) {
                            alert('Error deleting prompt');
                        }
                    }
                }
            """)
        ]
        
        return create_main_layout(
            "Prompts",
            Div(*content),
            current_page="prompts"
        )

    @app.post("/prompts/create")
    async def create_prompt(request):
        """Create a new prompt"""
        try:
            form_data = await request.form()
            name = form_data.get('name', '').strip()
            system_prompt = form_data.get('system_prompt', '').strip()
            user_prompt = form_data.get('user_prompt', '').strip()
            description = form_data.get('description', '').strip()
            
            if not name or not user_prompt:
                return HTMLResponse('<script>alert("Please provide name and user prompt"); window.history.back();</script>')
            
            db = Database()
            prompt_id = db.create_prompt(
                name=name,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            return HTMLResponse('<script>alert("Prompt created successfully!"); window.location.href="/prompts";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error creating prompt: {str(e)}"); window.history.back();</script>')

    @app.get("/prompts/{prompt_id}")
    async def get_prompt(request):
        """Get prompt details (API endpoint)"""
        prompt_id = request.path_params['prompt_id']
        
        try:
            db = Database()
            prompt = db.get_prompt(prompt_id)
            
            if not prompt:
                return {"success": False, "error": "Prompt not found"}
            
            return {"success": True, "prompt": prompt}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/prompts/{prompt_id}/edit")
    async def edit_prompt_page(request):
        """Edit prompt page"""
        prompt_id = request.path_params['prompt_id']
        
        db = Database()
        prompt = db.get_prompt(prompt_id)
        
        if not prompt:
            return HTMLResponse('<script>alert("Prompt not found"); window.location.href="/prompts";</script>')
        
        # Extract variables from database structure
        variables = prompt.get('variables', {})
        system_prompt = variables.get('system_prompt', '')
        user_prompt = variables.get('user_prompt', '')
        
        content = [
            create_card(
                title=f"Edit Prompt: {prompt['name']}",
                content=Form(
                    Div(
                        Label("Prompt Name", cls="block text-sm font-medium mb-1"),
                        Input(type="text", name="name", value=prompt['name'], required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("System Prompt", cls="block text-sm font-medium mb-1"),
                        Textarea(system_prompt, name="system_prompt", rows="4", cls="w-full p-2 border rounded mb-3")
                    ),
                    Div(
                        Label("User Prompt", cls="block text-sm font-medium mb-1"),
                        Textarea(user_prompt, name="user_prompt", rows="4", required=True, cls="w-full p-2 border rounded mb-3")
                    ),
                    Button("Update", type="submit", cls="px-4 py-2 bg-primary text-primary-foreground rounded mr-2"),
                    Button("Cancel", type="button", onclick="window.location.href='/prompts'", cls="px-4 py-2 border rounded"),
                    method="post",
                    action=f"/prompts/{prompt_id}/update"
                )
            )
        ]
        
        return create_main_layout(
            f"Edit Prompt: {prompt['name']}",
            Div(*content),
            current_page="prompts"
        )

    @app.post("/prompts/{prompt_id}/update")
    async def update_prompt(request):
        """Update a prompt"""
        prompt_id = request.path_params['prompt_id']
        
        try:
            form_data = await request.form()
            name = form_data.get('name', '').strip()
            system_prompt = form_data.get('system_prompt', '').strip()
            user_prompt = form_data.get('user_prompt', '').strip()
            
            if not name or not user_prompt:
                return HTMLResponse('<script>alert("Please provide name and user prompt"); window.history.back();</script>')
            
            db = Database()
            db.update_prompt(
                prompt_id=prompt_id,
                name=name,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            return HTMLResponse('<script>alert("Prompt updated successfully!"); window.location.href="/prompts";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error updating prompt: {str(e)}"); window.history.back();</script>')

    @app.delete("/prompts/{prompt_id}")
    async def delete_prompt(request):
        """Delete a prompt"""
        prompt_id = request.path_params['prompt_id']
        
        try:
            db = Database()
            db.delete_prompt(prompt_id)
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

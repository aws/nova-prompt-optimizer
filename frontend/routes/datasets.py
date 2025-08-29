"""
Dataset Management Routes
Handles dataset CRUD operations
"""

from fasthtml.common import *
from database import Database
from components.layout import create_main_layout, create_card
import csv
import os
import json


def setup_dataset_routes(app):
    """Setup dataset management routes"""
    
    @app.get("/datasets")
    async def datasets_page(request):
        """Datasets management page"""
        
        db = Database()
        datasets = db.get_datasets()
        
        dataset_rows = []
        for dataset in datasets:
            dataset_rows.append(
                Tr(
                    Td(dataset['name'], cls="px-4 py-2"),
                    Td(dataset.get('type', 'No description'), cls="px-4 py-2"),
                    Td(str(dataset.get('rows', 0)), cls="px-4 py-2"),
                    Td(dataset['created'], cls="px-4 py-2"),
                    Td(
                        Button("View", onclick=f"viewDataset('{dataset['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-1"),
                        Button("Delete", onclick=f"deleteDataset('{dataset['id']}')", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="px-4 py-2"
                    )
                )
            )
        
        content = [
            # Header with actions
            create_card(
                title="Dataset Management",
                content=Div(
                    P("Manage your datasets for prompt optimization", cls="text-muted-foreground mb-4"),
                    Div(
                        Button("Upload Dataset", onclick="showUploadForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Generate with AI", onclick="window.location.href='/datasets/generator'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs mr-2"),
                        Button("Simple Generator", onclick="window.location.href='/simple-generator'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        cls="flex gap-2"
                    )
                )
            ),
            
            # Upload form (hidden)
            Div(
                create_card(
                    title="Upload Dataset",
                    content=Form(
                        Div(
                            Label("Dataset Name", cls="block text-sm font-medium mb-1"),
                            Input(type="text", name="name", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Description", cls="block text-sm font-medium mb-1"),
                            Textarea(name="description", rows="2", cls="w-full p-2 border rounded mb-3")
                        ),
                        Div(
                            Label("Dataset File (CSV or JSONL)", cls="block text-sm font-medium mb-1"),
                            Input(type="file", name="file", accept=".csv,.jsonl", required=True, cls="w-full p-2 border rounded mb-3")
                        ),
                        Button("Upload", type="submit", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-3 py-1 text-xs mr-2"),
                        Button("Cancel", type="button", onclick="hideUploadForm()", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs"),
                        method="post",
                        action="/datasets/upload",
                        enctype="multipart/form-data"
                    )
                ),
                id="upload-form",
                cls="hidden mt-4"
            ),
            
            # Datasets table
            create_card(
                title="Your Datasets",
                content=Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Name", cls="px-4 py-2 text-left"),
                                Th("Description", cls="px-4 py-2 text-left"),
                                Th("Columns", cls="px-4 py-2 text-left"),
                                Th("Created", cls="px-4 py-2 text-left"),
                                Th("Actions", cls="px-4 py-2 text-left")
                            )
                        ),
                        Tbody(*dataset_rows),
                        cls="w-full border-collapse border border-gray-300"
                    ) if dataset_rows else P("No datasets found. Upload or generate your first dataset!", cls="text-gray-500 text-center py-8")
                )
            ),
            
            # JavaScript
            Script("""
                function showUploadForm() {
                    document.getElementById('upload-form').classList.remove('hidden');
                }
                
                function hideUploadForm() {
                    document.getElementById('upload-form').classList.add('hidden');
                }
                
                function viewDataset(id) {
                    window.location.href = '/datasets/' + id;
                }
                
                async function deleteDataset(id) {
                    if (confirm('Are you sure you want to delete this dataset?')) {
                        try {
                            const response = await fetch('/datasets/' + id, {method: 'DELETE'});
                            if (response.ok) {
                                location.reload();
                            } else {
                                alert('Error deleting dataset');
                            }
                        } catch (error) {
                            alert('Error deleting dataset');
                        }
                    }
                }
            """)
        ]
        
        return create_main_layout(
            "Datasets",
            Div(*content),
            current_page="datasets"
        )

    @app.post("/datasets/upload")
    async def upload_dataset(request):
        """Upload a new dataset"""
        try:
            form_data = await request.form()
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            file = form_data.get('file')
            
            if not name or not file:
                return HTMLResponse('<script>alert("Please provide name and file"); window.history.back();</script>')
            
            # Determine file type from filename
            filename = file.filename.lower()
            if filename.endswith('.csv'):
                file_type = "CSV"
                file_extension = ".csv"
            elif filename.endswith('.jsonl'):
                file_type = "JSONL"
                file_extension = ".jsonl"
            else:
                return HTMLResponse('<script>alert("Only CSV and JSONL files are supported"); window.history.back();</script>')
            
            # Save uploaded file
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, f"{name.replace(' ', '_')}{file_extension}")
            
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            
            # Get file info
            file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB"
            
            # Count rows based on file type
            if file_type == "CSV":
                with open(file_path, 'r') as f:
                    row_count = sum(1 for line in f) - 1  # Subtract header
            else:  # JSONL
                with open(file_path, 'r') as f:
                    row_count = sum(1 for line in f if line.strip())  # Count non-empty lines
            
            # Save to database
            db = Database()
            dataset_id = db.create_dataset(
                name=name,
                file_type=file_type,
                file_size=file_size,
                row_count=row_count,
                file_path=file_path
            )
            
            return HTMLResponse('<script>alert("Dataset uploaded successfully!"); window.location.href="/datasets";</script>')
            
        except Exception as e:
            return HTMLResponse(f'<script>alert("Error uploading dataset: {str(e)}"); window.history.back();</script>')

    @app.get("/datasets/{dataset_id}")
    async def view_dataset(request):
        """View dataset details"""
        dataset_id = request.path_params['dataset_id']
        
        db = Database()
        dataset = db.get_dataset(dataset_id)
        
        if not dataset:
            return HTMLResponse('<script>alert("Dataset not found"); window.location.href="/datasets";</script>')
        
        # Load sample data from content field
        sample_data = []
        if dataset.get('content'):
            try:
                # Parse JSONL content
                lines = dataset['content'].strip().split('\n')[:10]  # First 10 lines
                for line in lines:
                    if line.strip():
                        sample_data.append(json.loads(line))
            except Exception as e:
                print(f"Error parsing dataset content: {e}")
                sample_data = []
        
        content = [
            create_card(
                title=f"Dataset: {dataset['name']}",
                content=Div(
                    P(dataset.get('type', 'No description'), cls="text-gray-600 mb-4"),
                    P(f"Rows: {dataset.get('rows', 0)}", cls="text-sm mb-2"),
                    P(f"Size: {dataset.get('size', 'Unknown')}", cls="text-sm mb-2"),
                    P(f"Created: {dataset['created']}", cls="text-sm mb-4"),
                    Button("Back to Datasets", onclick="window.location.href='/datasets'", cls="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1 text-xs")
                )
            )
        ]
        
        if sample_data:
            # Create sample data table
            headers = list(sample_data[0].keys()) if sample_data else []
            header_row = Tr(*[Th(h, cls="px-4 py-2 text-left border") for h in headers])
            
            data_rows = []
            for row in sample_data:
                data_rows.append(
                    Tr(*[Td(str(row.get(h, '')), cls="px-4 py-2 border") for h in headers])
                )
            
            content.append(
                create_card(
                    title="Sample Data (First 10 rows)",
                    content=Table(
                        Thead(header_row),
                        Tbody(*data_rows),
                        cls="w-full border-collapse"
                    )
                )
            )
        
        return create_main_layout(
            f"Dataset: {dataset['name']}",
            Div(*content),
            current_page="datasets"
        )

    @app.delete("/datasets/{dataset_id}")
    async def delete_dataset(request):
        """Delete a dataset"""
        dataset_id = request.path_params['dataset_id']
        
        try:
            db = Database()
            dataset = db.get_dataset(dataset_id)
            
            if dataset:
                # Delete file if exists
                if dataset.get('file_path') and os.path.exists(dataset['file_path']):
                    os.remove(dataset['file_path'])
                
                # Delete from database
                db.delete_dataset(dataset_id)
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

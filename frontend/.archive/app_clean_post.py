@app.post("/datasets/upload")
async def dataset_upload_submit(request):
    """Handle dataset upload submission"""
    print("🔍 DEBUG: POST /datasets/upload route hit!")
    
    try:
        form = await request.form()
        print(f"🔍 DEBUG: Form data received: {dict(form)}")
        
        # Get form data (removed input_column and output_column)
        dataset_file = form.get("dataset")
        name = form.get("name", "")
        description = form.get("description", "")
        
        print(f"🔍 DEBUG: Parsed data - name: {name}, description: {description}")
        print(f"🔍 DEBUG: File: {dataset_file}")
        
    except Exception as e:
        print(f"❌ DEBUG: Error processing form: {e}")
        raise
    
    # Simple validation (only file and name required now)
    if not dataset_file or not name:
        # Check if this is from modal (referer contains modal)
        referer = request.headers.get("referer", "")
        is_modal_request = "modal" in referer or request.headers.get("sec-fetch-dest") == "iframe"
        
        if is_modal_request:
            return Html(
                Head(
                    Title("Upload Error"),
                    Meta(charset="utf-8"),
                    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
                    create_ui_styles()
                ),
                Body(
                    Div(
                        Alert(
                            "Please provide both a dataset file and name.",
                            variant="error",
                            title="Validation Error"
                        ),
                        Button("Try Again", onclick="window.location.reload()", 
                               style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                        style="padding: 1.5rem;"
                    )
                )
            )
        
        # Full page error response for non-modal requests
        user = await get_current_user(request)
        return create_main_layout(
            "Upload Dataset",
            Div(
                H1("Upload Dataset", style="margin-bottom: 1rem;"),
                
                Alert(
                    "Please provide both a dataset file and name.",
                    variant="error",
                    title="Validation Error"
                ),
                
                Card(
                    content=Form(
                        FormField(
                            "Dataset File",
                            Input(type="file", accept=".csv,.json,.jsonl", name="dataset", required=True),
                            help_text="Supported formats: CSV, JSON, JSONL (max 10MB)"
                        ),
                        FormField(
                            "Dataset Name",
                            Input(placeholder="My Training Dataset", name="name", 
                                value=name, required=True)
                        ),
                        FormField(
                            "Description",
                            Textarea(placeholder="Describe your dataset purpose and content...", 
                                   rows=3, name="description", value=description)
                        ),
                        Div(
                            Button("Upload Dataset", variant="primary", type="submit"),
                            Button("Back to Datasets", variant="ghost", href="/datasets"),
                            style="display: flex; gap: 0.5rem;"
                        ),
                        method="post",
                        action="/datasets/upload",
                        enctype="multipart/form-data"
                    )
                ),
                
                style="max-width: 600px; margin: 0 auto; padding: 2rem;"
            ),
            current_page="datasets",
            user=user.to_dict() if user else None
        )
    
    # Get file info (in real app, you'd save the file and process it)
    file_info = {
        "filename": dataset_file.filename if hasattr(dataset_file, 'filename') else "unknown",
        "size": len(await dataset_file.read()) if hasattr(dataset_file, 'read') else 0
    }
    
    # Save dataset info to our in-memory storage
    from datetime import datetime
    dataset_info = {
        "id": len(uploaded_datasets) + 1,
        "name": name,
        "filename": file_info["filename"],
        "size": file_info["size"],
        "description": description or "No description provided",
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Ready"
    }
    uploaded_datasets.append(dataset_info)
    print(f"🔍 DEBUG: Saved dataset: {dataset_info}")
    
    # Check if this is from modal
    referer = request.headers.get("referer", "")
    is_modal_request = "modal" in referer or request.headers.get("sec-fetch-dest") == "iframe"
    
    if is_modal_request:
        # Return modal-friendly success response
        return Html(
            Head(
                Title("Upload Success"),
                Meta(charset="utf-8"),
                Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
                create_ui_styles()
            ),
            Body(
                Div(
                    Alert(
                        f"Your dataset '{name}' has been uploaded successfully!",
                        variant="success",
                        title="Upload Complete"
                    ),
                    
                    Card(
                        header=H4("Dataset Details"),
                        content=Div(
                            P(Strong("Name: "), name),
                            P(Strong("File: "), file_info["filename"]),
                            P(Strong("Size: "), f"{file_info['size']} bytes"),
                            P(Strong("Description: "), description or "None provided"),
                        )
                    ),
                    
                    Div(
                        Button("Close", onclick="if(window.parent) window.parent.postMessage('upload-success', '*');", 
                               style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; margin-right: 0.5rem;"),
                        Button("Upload Another", onclick="window.location.href='/datasets/upload/modal'", 
                               style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem;"),
                        style="margin-top: 1rem;"
                    ),
                    
                    style="padding: 1.5rem;"
                ),
                
                # Auto-close modal after 3 seconds
                Script("""
                    setTimeout(function() {
                        if (window.parent && window.parent !== window) {
                            window.parent.postMessage('upload-success', '*');
                        }
                    }, 3000);
                """)
            )
        )
    
    # Full page success response for non-modal requests  
    user = await get_current_user(request)
    return create_main_layout(
        "Dataset Uploaded",
        Div(
            H1("Dataset Uploaded Successfully!", style="margin-bottom: 1rem;"),
            
            Alert(
                f"Your dataset '{name}' has been uploaded and is ready for use.",
                variant="success",
                title="Upload Complete"
            ),
            
            Card(
                header=H3("Dataset Details"),
                content=Div(
                    P(Strong("Name: "), name),
                    P(Strong("File: "), file_info["filename"]),
                    P(Strong("Size: "), f"{file_info['size']} bytes"),
                    P(Strong("Description: "), description or "None provided"),
                    Div(
                        Button("Upload Another", variant="primary", href="/datasets/upload"),
                        Button("View All Datasets", variant="secondary", href="/datasets"),
                        Button("Start Optimization", variant="outline", href="/optimization/new"),
                        style="display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap;"
                    )
                )
            ),
            
            style="max-width: 600px; margin: 0 auto; padding: 2rem;"
        ),
        current_page="datasets",
        user=user.to_dict() if user else None
    )

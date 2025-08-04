/**
 * Nova Prompt Optimizer - Main Application
 * Lightweight vanilla JavaScript implementation
 */

class NovaOptimizerApp {
    constructor() {
        this.currentView = 'datasets';
        
        // Preserve existing datasets if they exist
        if (window.datasets && window.datasets.size > 0) {
            console.log('🔄 Preserving existing datasets in app constructor');
            this.datasets = new Map(window.datasets);
        } else {
            this.datasets = new Map();
        }
        
        this.prompts = new Map();
        this.optimizations = new Map();
        this.websockets = new Map();
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing Nova Prompt Optimizer');
        
        try {
            this.setupNavigation();
            this.setupEventListeners();
            await this.loadInitialData();
            
            console.log('✅ Application initialized');
            
            // Create initialization promise for other modules to wait on
            this.initPromise = Promise.resolve();
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.initPromise = Promise.reject(error);
            throw error;
        }
    }
    
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.showView(view);
            });
        });
    }
    
    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // File upload drag and drop - with retry logic
        this.setupFileUploadListeners();
        
        // Modal close on background click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.active');
                if (activeModal) {
                    this.closeModal(activeModal);
                }
            }
        });
        
        console.log('✅ Event listeners setup completed');
    }
    
    setupFileUploadListeners() {
        const setupListeners = () => {
            const uploadArea = document.getElementById('upload-area');
            const fileInput = document.getElementById('file-input');
            
            console.log('🔍 Looking for file upload elements...');
            console.log('Upload area found:', !!uploadArea);
            console.log('File input found:', !!fileInput);
            console.log('File input element:', fileInput);
            
            if (uploadArea && fileInput) {
                console.log('🔧 Setting up file upload listeners...');
                
                // Clear any existing listeners first by cloning the element
                const newFileInput = fileInput.cloneNode(true);
                fileInput.parentNode.replaceChild(newFileInput, fileInput);
                
                // Get the fresh element reference
                const currentFileInput = document.getElementById('file-input');
                console.log('Fresh file input element:', currentFileInput);
                
                if (!currentFileInput) {
                    console.error('❌ Failed to get fresh file input element');
                    return false;
                }
                
                // Drag and drop events
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                    console.log('📥 Drag over detected');
                });
                
                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                    console.log('📤 Drag leave detected');
                });
                
                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    console.log('📁 Drop detected');
                    
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        console.log('📁 File dropped:', files[0].name);
                        this.handleFileSelect(files[0]);
                    }
                });
                
                // File input change event - using the fresh element
                try {
                    currentFileInput.addEventListener('change', (e) => {
                        console.log('📁 File input change event triggered');
                        console.log('Files selected:', e.target.files ? e.target.files.length : 'undefined');
                        console.log('Event target:', e.target);
                        console.log('Files object:', e.target.files);
                        
                        if (e.target.files && e.target.files.length > 0) {
                            console.log('📁 File selected via input:', e.target.files[0].name);
                            this.handleFileSelect(e.target.files[0]);
                        } else {
                            console.warn('⚠️ No files found in change event');
                        }
                    });
                    console.log('✅ Primary change event listener attached');
                } catch (error) {
                    console.error('❌ Error attaching primary change listener:', error);
                }
                
                // Enhance the global openFileDialog function with better event handling
                const originalOpenFileDialog = window.openFileDialog;
                window.openFileDialog = () => {
                    console.log('🖱️ openFileDialog called (enhanced)');
                    const fileInput = document.getElementById('file-input');
                    
                    if (fileInput) {
                        console.log('📁 Triggering file input click (enhanced)');
                        console.log('File input properties:', {
                            type: fileInput.type,
                            accept: fileInput.accept,
                            hidden: fileInput.hidden,
                            disabled: fileInput.disabled,
                            style: fileInput.style.display
                        });
                        
                        // Use both onchange and addEventListener for maximum compatibility
                        const handleFileSelection = (e) => {
                            console.log('📁 Enhanced change event triggered');
                            console.log('Event target:', e.target);
                            console.log('Files:', e.target.files);
                            
                            if (e.target.files && e.target.files.length > 0) {
                                console.log('📁 File selected (enhanced):', e.target.files[0].name);
                                
                                if (window.app && window.app.handleFileSelect) {
                                    window.app.handleFileSelect(e.target.files[0]);
                                } else {
                                    console.error('❌ App instance not available');
                                    // Fallback to original function
                                    if (originalOpenFileDialog !== window.openFileDialog) {
                                        originalOpenFileDialog();
                                    }
                                }
                            } else {
                                console.warn('⚠️ No files in enhanced change event');
                            }
                        };
                        
                        // Set both onchange and addEventListener
                        fileInput.onchange = handleFileSelection;
                        
                        // Also add event listener (remove any existing first)
                        fileInput.removeEventListener('change', handleFileSelection);
                        fileInput.addEventListener('change', handleFileSelection);
                        
                        try {
                            fileInput.click();
                            console.log('✅ Enhanced file input click executed');
                        } catch (error) {
                            console.error('❌ Error clicking file input:', error);
                        }
                    } else {
                        console.error('❌ File input element not found in enhanced function');
                        // Fallback to original function
                        if (originalOpenFileDialog !== window.openFileDialog) {
                            originalOpenFileDialog();
                        }
                    }
                };
                
                console.log('✅ File upload listeners set up successfully');
                return true;
            } else {
                console.warn('⚠️ File upload elements not found, retrying...');
                return false;
            }
        };
        
        // Try to set up listeners immediately
        if (!setupListeners()) {
            // If elements not found, retry after a short delay
            console.log('⏳ Retrying listener setup in 500ms...');
            setTimeout(() => {
                if (!setupListeners()) {
                    console.error('❌ Failed to set up file upload listeners after first retry');
                    
                    // Try one more time after a longer delay
                    console.log('⏳ Final retry in 2000ms...');
                    setTimeout(() => {
                        if (!setupListeners()) {
                            console.error('❌ Failed to set up file upload listeners after all retries');
                        }
                    }, 2000);
                }
            }, 500);
        }
    }
    
    async loadInitialData() {
        try {
            // Load data with individual error handling
            const promises = [
                this.loadDatasets().catch(error => {
                    console.warn('Failed to load datasets:', error);
                    return []; // Return empty array on failure
                }),
                this.loadPrompts().catch(error => {
                    console.warn('Failed to load prompts:', error);
                    return []; // Return empty array on failure
                }),
                this.loadOptimizations().catch(error => {
                    console.warn('Failed to load optimizations:', error);
                    return []; // Return empty array on failure
                })
            ];
            
            await Promise.allSettled(promises);
            console.log('✅ Initial data loading completed');
            
        } catch (error) {
            console.error('❌ Critical error during initial data loading:', error);
            // Don't throw here - let the app continue with empty data
            this.showToast('Some data failed to load. You can still use the application.', 'warning');
        }
    }
    
    showView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
        
        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        document.getElementById(`${viewName}-view`).classList.add('active');
        
        this.currentView = viewName;
        
        // Load view-specific data
        this.onViewChange(viewName);
    }
    
    async onViewChange(viewName) {
        switch (viewName) {
            case 'datasets':
                await this.loadDatasets();
                break;
            case 'prompts':
                await this.loadPrompts();
                break;
            case 'optimization':
                await this.loadOptimizationOptions();
                break;
            case 'results':
                await this.loadResults();
                break;
        }
    }
    
    // Dataset Management
    async loadDatasets() {
        try {
            const response = await fetch('/api/datasets');
            const data = await response.json();
            
            // Store in both app instance and global window for compatibility
            this.datasets.clear();
            window.datasets = window.datasets || new Map();
            window.datasets.clear();
            
            data.datasets.forEach(dataset => {
                this.datasets.set(dataset.id, dataset);
                window.datasets.set(dataset.id, dataset);
            });
            
            console.log(`📊 App loaded ${data.datasets.length} datasets`);
            
            // Use standalone rendering to avoid conflicts
            if (typeof window.renderDatasetsStandalone === 'function') {
                window.renderDatasetsStandalone();
            } else {
                // Fallback to app rendering if standalone not available
                this.renderDatasets();
            }
        } catch (error) {
            console.error('Failed to load datasets:', error);
            this.showToast('Failed to load datasets', 'error');
        }
    }
    
    renderDatasets() {
        const container = document.getElementById('datasets-container');
        
        if (this.datasets.size === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <h4>No datasets yet</h4>
                    <p>Upload your first dataset to get started</p>
                </div>
            `;
            return;
        }
        
        const datasetsHtml = Array.from(this.datasets.values()).map(dataset => `
            <div class="dataset-item">
                <div class="item-header">
                    <div>
                        <div class="item-title">${dataset.name}</div>
                        <div class="item-meta">${dataset.row_count} rows • ${dataset.columns.length} columns</div>
                    </div>
                    <div class="item-actions">
                        <button class="btn btn-secondary" onclick="app.viewDataset('${dataset.id}')">
                            👁️ View
                        </button>
                        <button class="btn btn-error" onclick="app.deleteDataset('${dataset.id}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                <p class="item-description">${dataset.description || 'No description'}</p>
                <div class="item-meta">
                    <small>Created: ${new Date(dataset.created_at).toLocaleDateString()}</small>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = datasetsHtml;
    }
    
    handleFileSelect(file) {
        console.log('📁 handleFileSelect called with file:', file.name);
        console.log('📊 File details:', {
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: new Date(file.lastModified).toLocaleString()
        });
        
        // Validate file type
        const validTypes = ['.csv', '.jsonl', '.json'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        console.log('🔍 File extension:', fileExtension);
        console.log('✅ Valid types:', validTypes);
        
        if (!validTypes.includes(fileExtension)) {
            console.error('❌ Invalid file type:', fileExtension);
            this.showToast('Please select a CSV or JSONL file', 'error');
            return;
        }
        
        console.log('✅ File type validation passed');
        
        // Show upload form
        const uploadArea = document.getElementById('upload-area');
        const uploadForm = document.getElementById('upload-form');
        
        console.log('🔄 Switching to upload form...');
        console.log('Upload area found:', !!uploadArea);
        console.log('Upload form found:', !!uploadForm);
        
        if (uploadArea && uploadForm) {
            uploadArea.style.display = 'none';
            uploadForm.style.display = 'block';
            console.log('✅ Upload form displayed');
        } else {
            console.error('❌ Could not find upload area or form elements');
        }
        
        // Store file for upload
        this.selectedFile = file;
        console.log('💾 File stored for upload');
        
        // Pre-fill name
        const nameInput = document.getElementById('dataset-name');
        if (nameInput) {
            const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
            nameInput.value = fileName;
            console.log('✅ Pre-filled dataset name:', fileName);
        } else {
            console.error('❌ Could not find dataset name input');
        }
    }
    
    async uploadDataset() {
        if (!this.selectedFile) {
            this.showToast('No file selected', 'error');
            return;
        }
        
        const name = document.getElementById('dataset-name').value;
        const description = document.getElementById('dataset-description').value;
        
        if (!name.trim()) {
            this.showToast('Please enter a dataset name', 'error');
            return;
        }
        
        try {
            this.showLoading('Uploading dataset...');
            
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('name', name);
            formData.append('description', description);
            
            const response = await fetch('/api/datasets/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            
            const dataset = await response.json();
            this.datasets.set(dataset.id, dataset);
            
            this.hideLoading();
            this.showToast('Dataset uploaded successfully!', 'success');
            this.cancelUpload();
            this.renderDatasets();
            
        } catch (error) {
            this.hideLoading();
            console.error('Upload failed:', error);
            this.showToast(`Upload failed: ${error.message}`, 'error');
        }
    }
    
    cancelUpload() {
        document.getElementById('upload-area').style.display = 'block';
        document.getElementById('upload-form').style.display = 'none';
        document.getElementById('dataset-name').value = '';
        document.getElementById('dataset-description').value = '';
        document.getElementById('file-input').value = '';
        this.selectedFile = null;
    }
    
    async deleteDataset(datasetId) {
        if (!confirm('Are you sure you want to delete this dataset?')) {
            return;
        }
        
        try {
            // For now, just remove from local storage
            // In a real implementation, you'd call DELETE /api/datasets/{id}
            this.datasets.delete(datasetId);
            this.renderDatasets();
            this.showToast('Dataset deleted', 'success');
        } catch (error) {
            console.error('Failed to delete dataset:', error);
            this.showToast('Failed to delete dataset', 'error');
        }
    }
    
    // Prompt Management
    async loadPrompts() {
        try {
            const response = await fetch('/api/prompts');
            const data = await response.json();
            
            this.prompts.clear();
            data.prompts.forEach(prompt => {
                this.prompts.set(prompt.id, prompt);
            });
            
            this.renderPrompts();
        } catch (error) {
            console.error('Failed to load prompts:', error);
            this.showToast('Failed to load prompts', 'error');
        }
    }
    
    renderPrompts() {
        const container = document.getElementById('prompts-container');
        
        if (this.prompts.size === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✏️</div>
                    <h4>No prompts yet</h4>
                    <p>Create your first prompt to begin optimization</p>
                </div>
            `;
            return;
        }
        
        const promptsHtml = Array.from(this.prompts.values()).map(prompt => `
            <div class="prompt-item">
                <div class="item-header">
                    <div>
                        <div class="item-title">${prompt.name}</div>
                        <div class="item-meta">${prompt.variables.length} variables</div>
                    </div>
                    <div class="item-actions">
                        <button class="btn btn-secondary" onclick="app.editPrompt('${prompt.id}')">
                            ✏️ Edit
                        </button>
                        <button class="btn btn-error" onclick="app.deletePrompt('${prompt.id}')">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                <p class="item-description">${prompt.description || 'No description'}</p>
                <div class="variables-list">
                    ${prompt.variables.map(v => `<span class="variable-tag">${v}</span>`).join('')}
                </div>
                <div class="item-meta">
                    <small>Created: ${new Date(prompt.created_at).toLocaleDateString()}</small>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = promptsHtml;
    }
    
    // Optimization Management
    async loadOptimizations() {
        try {
            // For now, we'll just initialize an empty optimizations map
            // In a real implementation, this would load from /api/optimizations
            console.log('📊 Optimizations loaded (placeholder)');
        } catch (error) {
            console.error('Failed to load optimizations:', error);
            this.showToast('Failed to load optimizations', 'error');
        }
    }
    
    async loadOptimizationOptions() {
        // Populate dataset and prompt dropdowns
        const datasetSelect = document.getElementById('opt-dataset');
        const promptSelect = document.getElementById('opt-prompt');
        
        // Clear existing options
        datasetSelect.innerHTML = '<option value="">Choose a dataset...</option>';
        promptSelect.innerHTML = '<option value="">Choose a prompt...</option>';
        
        // Add datasets
        this.datasets.forEach(dataset => {
            const option = document.createElement('option');
            option.value = dataset.id;
            option.textContent = dataset.name;
            datasetSelect.appendChild(option);
        });
        
        // Add prompts
        this.prompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            promptSelect.appendChild(option);
        });
    }
    
    async startOptimization() {
        const datasetId = document.getElementById('opt-dataset').value;
        const promptId = document.getElementById('opt-prompt').value;
        const mode = document.getElementById('opt-mode').value;
        
        if (!datasetId || !promptId) {
            this.showToast('Please select both a dataset and prompt', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/optimization/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dataset_id: datasetId,
                    prompt_id: promptId,
                    mode: mode
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to start optimization: ${response.statusText}`);
            }
            
            const optimization = await response.json();
            this.optimizations.set(optimization.id, optimization);
            
            // Show progress section
            document.querySelector('.optimization-setup').style.display = 'none';
            document.getElementById('optimization-progress').style.display = 'block';
            
            // Connect to WebSocket for real-time updates
            this.connectToOptimization(optimization.id);
            
            this.showToast('Optimization started!', 'success');
            
        } catch (error) {
            console.error('Failed to start optimization:', error);
            this.showToast(`Failed to start optimization: ${error.message}`, 'error');
        }
    }
    
    connectToOptimization(optimizationId) {
        const wsUrl = `ws://${window.location.host}/ws/optimization/${optimizationId}`;
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log(`Connected to optimization ${optimizationId}`);
            this.websockets.set(optimizationId, ws);
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleOptimizationUpdate(data);
        };
        
        ws.onclose = () => {
            console.log(`Disconnected from optimization ${optimizationId}`);
            this.websockets.delete(optimizationId);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showToast('Connection error during optimization', 'error');
        };
    }
    
    handleOptimizationUpdate(data) {
        const { type, optimization_id, progress, current_step, results, error } = data;
        
        switch (type) {
            case 'progress':
                this.updateProgress(progress, current_step);
                break;
                
            case 'completed':
                this.handleOptimizationComplete(optimization_id, results);
                break;
                
            case 'error':
                this.handleOptimizationError(optimization_id, error);
                break;
        }
    }
    
    updateProgress(progress, currentStep) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressPercent = document.getElementById('progress-percent');
        const startedValue = document.getElementById('started-value');
        
        if (progressFill) progressFill.style.width = `${progress * 100}%`;
        if (progressText) progressText.textContent = currentStep;
        if (progressPercent) progressPercent.textContent = `${Math.round(progress * 100)}%`;
        if (startedValue && startedValue.textContent === '-') {
            startedValue.textContent = new Date().toLocaleTimeString();
        }
    }
    
    handleOptimizationComplete(optimizationId, results) {
        this.showToast('Optimization completed successfully!', 'success');
        
        // Update progress to 100%
        this.updateProgress(1.0, 'Completed');
        
        // Store results
        if (this.optimizations.has(optimizationId)) {
            this.optimizations.get(optimizationId).results = results;
        }
        
        // Show results
        setTimeout(() => {
            this.showView('results');
            this.displayResults(results);
        }, 2000);
    }
    
    handleOptimizationError(optimizationId, error) {
        this.showToast(`Optimization failed: ${error}`, 'error');
        
        // Reset UI
        document.querySelector('.optimization-setup').style.display = 'block';
        document.getElementById('optimization-progress').style.display = 'none';
    }
    
    // Results
    async loadResults() {
        // This would typically load from API
        // For now, we'll use the in-memory optimizations
        this.renderResults();
    }
    
    renderResults() {
        const container = document.getElementById('results-container');
        
        const completedOptimizations = Array.from(this.optimizations.values())
            .filter(opt => opt.status === 'completed' && opt.results);
        
        if (completedOptimizations.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📈</div>
                    <h4>No results yet</h4>
                    <p>Run an optimization to see results here</p>
                </div>
            `;
            return;
        }
        
        const resultsHtml = completedOptimizations.map(opt => {
            const results = opt.results;
            const improvement = ((results.optimized_score - results.original_score) / results.original_score * 100).toFixed(1);
            
            return `
                <div class="card">
                    <h3>Optimization Results</h3>
                    <div class="grid grid-3">
                        <div class="metric-card">
                            <div class="metric-label">Original Score</div>
                            <div class="metric-value">${results.original_score.toFixed(3)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Optimized Score</div>
                            <div class="metric-value">${results.optimized_score.toFixed(3)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Improvement</div>
                            <div class="metric-value">+${improvement}%</div>
                        </div>
                    </div>
                    <div class="optimized-prompt">
                        <h4>Optimized Prompt</h4>
                        <div class="prompt-section">
                            <strong>System:</strong>
                            <pre>${results.optimized_prompt.system_prompt}</pre>
                        </div>
                        <div class="prompt-section">
                            <strong>User:</strong>
                            <pre>${results.optimized_prompt.user_prompt}</pre>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = resultsHtml;
    }
    
    displayResults(results) {
        // This is called when optimization completes
        this.renderResults();
    }
    
    // Utility methods
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }
    
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const text = document.querySelector('.loading-text');
        
        if (text) text.textContent = message;
        if (overlay) overlay.style.display = 'flex';
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';
    }
    
    closeModal(modal) {
        modal.classList.remove('active');
    }
}

// Global functions for HTML onclick handlers
window.app = null;

window.uploadDataset = () => {
    console.log('📤 uploadDataset called');
    
    // Try to use app instance first
    if (window.app && window.app.uploadDataset) {
        console.log('✅ Using app instance for upload');
        return window.app.uploadDataset();
    }
    
    // Fallback to standalone upload
    console.log('🔄 Using standalone upload');
    
    const selectedFile = window.selectedFile;
    if (!selectedFile) {
        alert('No file selected. Please select a file first.');
        console.error('❌ No file selected');
        return;
    }
    
    const name = document.getElementById('dataset-name').value;
    const description = document.getElementById('dataset-description').value;
    
    if (!name.trim()) {
        alert('Please enter a dataset name');
        console.error('❌ No dataset name provided');
        return;
    }
    
    console.log('📤 Starting standalone upload...');
    console.log('File:', selectedFile.name);
    console.log('Name:', name);
    console.log('Description:', description);
    
    // Show loading state
    const uploadButton = document.querySelector('button[onclick="uploadDataset()"]');
    if (uploadButton) {
        uploadButton.textContent = 'Uploading...';
        uploadButton.disabled = true;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('name', name);
    formData.append('description', description);
    
    // Upload to server
    fetch('/api/datasets/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('📤 Upload response status:', response.status);
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        return response.json();
    })
    .then(dataset => {
        console.log('✅ Upload successful:', dataset);
        alert('Dataset uploaded successfully!');
        
        // Reset form
        document.getElementById('upload-area').style.display = 'block';
        document.getElementById('upload-form').style.display = 'none';
        document.getElementById('dataset-name').value = '';
        document.getElementById('dataset-description').value = '';
        document.getElementById('file-input').value = '';
        window.selectedFile = null;
        
        // Reload datasets if app is available
        if (window.app && window.app.loadDatasets) {
            console.log('🔄 Reloading datasets via app instance');
            window.app.loadDatasets();
        } else {
            console.log('🔄 App not available, reloading datasets manually');
            // Manual dataset reload
            loadDatasetsStandalone();
        }
    })
    .catch(error => {
        console.error('❌ Upload failed:', error);
        alert(`Upload failed: ${error.message}`);
    })
    .finally(() => {
        // Reset button
        if (uploadButton) {
            uploadButton.textContent = 'Upload';
            uploadButton.disabled = false;
        }
    });
};
window.cancelUpload = () => {
    console.log('❌ cancelUpload called');
    
    // Try to use app instance first
    if (window.app && window.app.cancelUpload) {
        console.log('✅ Using app instance for cancel');
        return window.app.cancelUpload();
    }
    
    // Fallback to standalone cancel
    console.log('🔄 Using standalone cancel');
    
    document.getElementById('upload-area').style.display = 'block';
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('dataset-name').value = '';
    document.getElementById('dataset-description').value = '';
    document.getElementById('file-input').value = '';
    window.selectedFile = null;
    
    console.log('✅ Upload cancelled');
};
// Standalone prompt management functions
window.createNewPrompt = () => {
    console.log('✏️ Create new prompt');
    
    if (window.app && window.app.createNewPrompt) {
        return window.app.createNewPrompt();
    }
    
    // Standalone prompt creation
    showPromptModal();
};

window.closePromptModal = () => {
    console.log('❌ Close prompt modal');
    
    if (window.app && window.app.closePromptModal) {
        return window.app.closePromptModal();
    }
    
    // Standalone modal close
    const modal = document.getElementById('prompt-modal');
    if (modal) {
        modal.classList.remove('active');
    }
};

window.savePrompt = async () => {
    console.log('💾 Save prompt');
    
    if (window.app && window.app.savePrompt) {
        return window.app.savePrompt();
    }
    
    // Standalone prompt save
    await savePromptStandalone();
};

// Show prompt modal
const showPromptModal = () => {
    console.log('🎨 Showing prompt modal');
    
    const modal = document.getElementById('prompt-modal');
    if (modal) {
        // Clear form
        document.getElementById('prompt-name').value = '';
        document.getElementById('prompt-description').value = '';
        document.getElementById('system-prompt').value = '';
        document.getElementById('user-prompt').value = '';
        document.getElementById('variables-detected').style.display = 'none';
        
        // Show modal
        modal.classList.add('active');
        
        // Setup variable detection
        const userPromptTextarea = document.getElementById('user-prompt');
        if (userPromptTextarea) {
            userPromptTextarea.addEventListener('input', detectVariables);
        }
    } else {
        console.error('❌ Prompt modal not found');
    }
};

// Detect variables in prompt
const detectVariables = () => {
    const userPrompt = document.getElementById('user-prompt').value;
    const variables = extractVariables(userPrompt);
    
    const variablesSection = document.getElementById('variables-detected');
    const variablesList = document.getElementById('variables-list');
    
    if (variables.length > 0) {
        variablesSection.style.display = 'block';
        variablesList.innerHTML = variables
            .map(variable => `<span class="variable-tag">${variable}</span>`)
            .join('');
        console.log('🔍 Variables detected:', variables);
    } else {
        variablesSection.style.display = 'none';
    }
};

// Extract variables from text
const extractVariables = (text) => {
    const variableRegex = /\{\{([^}]+)\}\}/g;
    const variables = new Set();
    let match;
    
    while ((match = variableRegex.exec(text)) !== null) {
        const variable = match[1].trim();
        if (variable) {
            variables.add(variable);
        }
    }
    
    return Array.from(variables);
};

// Save prompt standalone
const savePromptStandalone = async () => {
    const name = document.getElementById('prompt-name').value.trim();
    const description = document.getElementById('prompt-description').value.trim();
    const systemPrompt = document.getElementById('system-prompt').value.trim();
    const userPrompt = document.getElementById('user-prompt').value.trim();
    
    // Validation
    if (!name) {
        alert('Please enter a prompt name');
        return;
    }
    
    if (!userPrompt) {
        alert('Please enter a user prompt');
        return;
    }
    
    // Extract variables
    const variables = extractVariables(userPrompt);
    
    const promptData = {
        name,
        description,
        system_prompt: systemPrompt,
        user_prompt: userPrompt,
        variables
    };
    
    console.log('💾 Saving prompt:', promptData);
    
    try {
        const response = await fetch('/api/prompts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(promptData)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to save prompt: ${response.statusText}`);
        }
        
        const savedPrompt = await response.json();
        console.log('✅ Prompt saved:', savedPrompt);
        
        // Store globally
        if (!window.prompts) {
            window.prompts = new Map();
        }
        window.prompts.set(savedPrompt.id, savedPrompt);
        
        // Close modal
        window.closePromptModal();
        
        // Reload prompts
        await loadPromptsStandalone();
        
        alert('Prompt created successfully!');
        
    } catch (error) {
        console.error('❌ Failed to save prompt:', error);
        alert(`Failed to save prompt: ${error.message}`);
    }
};

// Load prompts standalone
const loadPromptsStandalone = async () => {
    console.log('📝 Loading prompts standalone...');
    
    try {
        const response = await fetch('/api/prompts');
        console.log('📝 Prompts API response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📝 Prompts API response data:', data);
        
        console.log('📝 Prompts loaded:', data.prompts.length);
        
        // Store prompts globally
        window.prompts = new Map();
        data.prompts.forEach(prompt => {
            window.prompts.set(prompt.id, prompt);
        });
        
        // Render prompts
        renderPromptsStandalone();
        
    } catch (error) {
        console.error('❌ Failed to load prompts:', error);
        
        // Initialize empty prompts if API fails
        window.prompts = new Map();
        renderPromptsStandalone();
    }
};

// Render prompts standalone
const renderPromptsStandalone = () => {
    console.log('🎨 Rendering prompts standalone...');
    
    const container = document.getElementById('prompts-container');
    if (!container) {
        console.error('❌ Prompts container not found');
        return;
    }
    
    if (!window.prompts || window.prompts.size === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">✏️</div>
                <h4>No prompts yet</h4>
                <p>Create your first prompt to begin optimization</p>
            </div>
        `;
        console.log('📝 No prompts to display');
        return;
    }
    
    const promptsHtml = Array.from(window.prompts.values()).map(prompt => `
        <div class="prompt-item">
            <div class="item-header">
                <div>
                    <div class="item-title">${prompt.name}</div>
                    <div class="item-meta">${prompt.variables.length} variables</div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="editPrompt('${prompt.id}')">
                        ✏️ Edit
                    </button>
                    <button class="btn btn-error" onclick="deletePrompt('${prompt.id}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
            <p class="item-description">${prompt.description || 'No description'}</p>
            <div class="variables-list">
                ${prompt.variables.map(v => `<span class="variable-tag">${v}</span>`).join('')}
            </div>
            <div class="item-meta">
                <small>Created: ${new Date(prompt.created_at).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = promptsHtml;
    console.log('✅ Prompts rendered:', window.prompts.size);
};

// Edit and delete prompt functions
window.editPrompt = (promptId) => {
    console.log('✏️ Edit prompt:', promptId);
    
    // Get the prompt data
    const prompt = window.prompts?.get(promptId);
    if (!prompt) {
        alert('Prompt not found!');
        return;
    }
    
    // Fill the modal with existing data
    document.getElementById('prompt-modal-title').textContent = 'Edit Prompt';
    document.getElementById('prompt-name').value = prompt.name || '';
    document.getElementById('prompt-description').value = prompt.description || '';
    document.getElementById('system-prompt').value = prompt.system_prompt || '';
    document.getElementById('user-prompt').value = prompt.user_prompt || '';
    
    // Store the prompt ID for saving
    document.getElementById('prompt-modal').dataset.promptId = promptId;
    
    // Show the modal
    document.getElementById('prompt-modal').style.display = 'block';
};

window.deletePrompt = async (promptId) => {
    console.log('🗑️ Delete prompt:', promptId);
    
    if (!confirm('Are you sure you want to delete this prompt?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/prompts/${promptId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Remove from local storage
            window.prompts?.delete(promptId);
            
            // Re-render prompts
            if (typeof window.renderPromptsStandalone === 'function') {
                window.renderPromptsStandalone();
            } else {
                // Fallback: reload prompts
                if (typeof window.loadPromptsStandalone === 'function') {
                    await window.loadPromptsStandalone();
                }
            }
            
            console.log('✅ Prompt deleted successfully');
            alert('Prompt deleted successfully!');
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Failed to delete prompt:', error);
        alert('Failed to delete prompt. Please try again.');
    }
};

// Create new prompt function
window.createNewPrompt = () => {
    console.log('➕ Create new prompt');
    
    // Clear the modal
    document.getElementById('prompt-modal-title').textContent = 'Create New Prompt';
    document.getElementById('prompt-name').value = '';
    document.getElementById('prompt-description').value = '';
    document.getElementById('system-prompt').value = '';
    document.getElementById('user-prompt').value = '';
    
    // Remove any stored prompt ID
    delete document.getElementById('prompt-modal').dataset.promptId;
    
    // Show the modal
    document.getElementById('prompt-modal').style.display = 'block';
};

// Close prompt modal
window.closePromptModal = () => {
    console.log('❌ Close prompt modal');
    document.getElementById('prompt-modal').style.display = 'none';
};

// Save prompt function
window.savePrompt = async () => {
    console.log('💾 Save prompt');
    
    const modal = document.getElementById('prompt-modal');
    const promptId = modal.dataset.promptId;
    const isEdit = !!promptId;
    
    // Get form data
    const promptData = {
        name: document.getElementById('prompt-name').value.trim(),
        description: document.getElementById('prompt-description').value.trim(),
        system_prompt: document.getElementById('system-prompt').value.trim(),
        user_prompt: document.getElementById('user-prompt').value.trim()
    };
    
    // Validate required fields
    if (!promptData.name) {
        alert('Please enter a prompt name');
        return;
    }
    
    if (!promptData.system_prompt && !promptData.user_prompt) {
        alert('Please enter either a system prompt or user prompt');
        return;
    }
    
    try {
        let response;
        
        if (isEdit) {
            // Update existing prompt
            response = await fetch(`/api/prompts/${promptId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(promptData)
            });
        } else {
            // Create new prompt
            response = await fetch('/api/prompts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(promptData)
            });
        }
        
        if (response.ok) {
            const savedPrompt = await response.json();
            
            // Update local storage
            if (!window.prompts) {
                window.prompts = new Map();
            }
            window.prompts.set(savedPrompt.id, savedPrompt);
            
            // Re-render prompts
            if (typeof window.renderPromptsStandalone === 'function') {
                window.renderPromptsStandalone();
            } else {
                // Fallback: reload prompts
                if (typeof window.loadPromptsStandalone === 'function') {
                    await window.loadPromptsStandalone();
                }
            }
            
            // Close modal
            closePromptModal();
            
            console.log(`✅ Prompt ${isEdit ? 'updated' : 'created'} successfully`);
            alert(`Prompt ${isEdit ? 'updated' : 'created'} successfully!`);
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`❌ Failed to ${isEdit ? 'update' : 'create'} prompt:`, error);
        alert(`Failed to ${isEdit ? 'update' : 'create'} prompt. Please try again.`);
    }
};
window.startOptimization = async () => {
    console.log('🚀 Start optimization');
    
    if (window.app && window.app.startOptimization) {
        return window.app.startOptimization();
    }
    
    // Standalone optimization
    await startOptimizationStandalone();
};

// Start optimization standalone
const startOptimizationStandalone = async () => {
    const datasetId = document.getElementById('opt-dataset').value;
    const promptId = document.getElementById('opt-prompt').value;
    const mode = document.getElementById('opt-mode').value;
    
    if (!datasetId || !promptId) {
        alert('Please select both a dataset and prompt');
        return;
    }
    
    console.log('🚀 Starting optimization:', { datasetId, promptId, mode });
    
    try {
        const response = await fetch('/api/optimization/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataset_id: datasetId,
                prompt_id: promptId,
                mode: mode
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to start optimization: ${response.statusText}`);
        }
        
        const optimization = await response.json();
        console.log('✅ Optimization started:', optimization);
        
        // Show progress section
        document.querySelector('.optimization-setup').style.display = 'none';
        document.getElementById('optimization-progress').style.display = 'block';
        
        // Connect to WebSocket for real-time updates
        connectToOptimizationStandalone(optimization.id);
        
        alert('Optimization started! Check the progress below.');
        
    } catch (error) {
        console.error('❌ Failed to start optimization:', error);
        alert(`Failed to start optimization: ${error.message}`);
    }
};

// Connect to optimization WebSocket standalone
const connectToOptimizationStandalone = (optimizationId) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/optimization/${optimizationId}`;
    
    console.log('🔌 Connecting to optimization WebSocket:', wsUrl);
    
    try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log(`✅ Connected to optimization ${optimizationId}`);
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Optimization update:', data);
                handleOptimizationUpdateStandalone(data);
            } catch (error) {
                console.error('❌ Failed to parse WebSocket message:', error);
            }
        };
        
        ws.onclose = (event) => {
            console.log(`🔌 Disconnected from optimization ${optimizationId}`, event.code);
        };
        
        ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('❌ Failed to create WebSocket connection:', error);
    }
};

// Handle optimization updates standalone
const handleOptimizationUpdateStandalone = (data) => {
    const { type, optimization_id, progress, current_step, results, error } = data;
    
    switch (type) {
        case 'progress':
            updateProgressStandalone(progress, current_step);
            break;
            
        case 'completed':
            handleOptimizationCompleteStandalone(optimization_id, results);
            break;
            
        case 'error':
            handleOptimizationErrorStandalone(optimization_id, error);
            break;
            
        default:
            console.warn('Unknown optimization update type:', type);
    }
};

// Update progress standalone
const updateProgressStandalone = (progress, currentStep) => {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressPercent = document.getElementById('progress-percent');
    const startedValue = document.getElementById('started-value');
    
    if (progressFill) {
        progressFill.style.width = `${Math.max(0, Math.min(100, progress * 100))}%`;
    }
    
    if (progressText) {
        progressText.textContent = currentStep || 'Processing...';
    }
    
    if (progressPercent) {
        progressPercent.textContent = `${Math.round(Math.max(0, Math.min(100, progress * 100)))}%`;
    }
    
    if (startedValue && startedValue.textContent === '-') {
        startedValue.textContent = new Date().toLocaleTimeString();
    }
    
    console.log(`📊 Progress: ${Math.round(progress * 100)}% - ${currentStep}`);
};

// Handle optimization complete standalone
const handleOptimizationCompleteStandalone = (optimizationId, results) => {
    console.log('🎉 Optimization completed:', results);
    
    // Update progress to 100%
    updateProgressStandalone(1.0, 'Completed');
    
    alert('Optimization completed successfully! Check the Results section.');
    
    // Store results globally
    if (!window.optimizationResults) {
        window.optimizationResults = new Map();
    }
    window.optimizationResults.set(optimizationId, results);
    
    // Show results after a delay
    setTimeout(() => {
        // Switch to results view
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector('[data-view="results"]').classList.add('active');
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById('results-view').classList.add('active');
        
        // Render results
        renderResultsStandalone();
    }, 2000);
};

// Handle optimization error standalone
const handleOptimizationErrorStandalone = (optimizationId, error) => {
    console.error('❌ Optimization failed:', error);
    alert(`Optimization failed: ${error}`);
    
    // Reset UI
    document.querySelector('.optimization-setup').style.display = 'block';
    document.getElementById('optimization-progress').style.display = 'none';
};

// Render results standalone
const renderResultsStandalone = () => {
    console.log('📈 Rendering results standalone...');
    
    const container = document.getElementById('results-container');
    if (!container) {
        console.error('❌ Results container not found');
        return;
    }
    
    if (!window.optimizationResults || window.optimizationResults.size === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📈</div>
                <h4>No results yet</h4>
                <p>Run an optimization to see results here</p>
            </div>
        `;
        return;
    }
    
    const resultsHtml = Array.from(window.optimizationResults.values()).map(results => {
        const improvement = ((results.optimized_score - results.original_score) / results.original_score * 100).toFixed(1);
        
        return `
            <div class="card">
                <h3>🎉 Optimization Results</h3>
                <div class="grid grid-3">
                    <div class="metric-card">
                        <div class="metric-label">Original Score</div>
                        <div class="metric-value">${results.original_score.toFixed(3)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Optimized Score</div>
                        <div class="metric-value">${results.optimized_score.toFixed(3)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Improvement</div>
                        <div class="metric-value">+${improvement}%</div>
                    </div>
                </div>
                <div class="optimized-prompt">
                    <h4>✨ Optimized Prompt</h4>
                    <div class="prompt-section">
                        <strong>System Prompt:</strong>
                        <pre>${results.optimized_prompt.system_prompt}</pre>
                    </div>
                    <div class="prompt-section">
                        <strong>User Prompt:</strong>
                        <pre>${results.optimized_prompt.user_prompt}</pre>
                    </div>
                </div>
                <div style="margin-top: 1.5rem;">
                    <button class="btn btn-primary" onclick="copyOptimizedPrompt()">
                        📋 Copy Optimized Prompt
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = resultsHtml;
    console.log('✅ Results rendered');
};

// Copy optimized prompt
window.copyOptimizedPrompt = () => {
    if (window.optimizationResults && window.optimizationResults.size > 0) {
        const results = Array.from(window.optimizationResults.values())[0];
        const promptText = `System Prompt:\n${results.optimized_prompt.system_prompt}\n\nUser Prompt:\n${results.optimized_prompt.user_prompt}`;
        
        navigator.clipboard.writeText(promptText).then(() => {
            alert('Optimized prompt copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy prompt. Please copy manually from the display.');
        });
    }
};

// Load optimization options standalone
const loadOptimizationOptionsStandalone = () => {
    console.log('⚙️ Loading optimization options...');
    
    const datasetSelect = document.getElementById('opt-dataset');
    const promptSelect = document.getElementById('opt-prompt');
    
    if (!datasetSelect || !promptSelect) {
        console.error('❌ Optimization select elements not found');
        return;
    }
    
    // Clear existing options
    datasetSelect.innerHTML = '<option value="">Choose a dataset...</option>';
    promptSelect.innerHTML = '<option value="">Choose a prompt...</option>';
    
    // Add datasets
    if (window.datasets) {
        window.datasets.forEach(dataset => {
            const option = document.createElement('option');
            option.value = dataset.id;
            option.textContent = dataset.name;
            datasetSelect.appendChild(option);
        });
    }
    
    // Add prompts
    if (window.prompts) {
        window.prompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            promptSelect.appendChild(option);
        });
    }
    
    console.log('✅ Optimization options loaded');
};

// Make optimization function globally available
window.loadOptimizationOptionsStandalone = loadOptimizationOptionsStandalone;

// Define openFileDialog globally to prevent "not defined" errors
window.openFileDialog = () => {
    console.log('🖱️ openFileDialog called (global fallback)');
    const fileInput = document.getElementById('file-input');
    
    if (fileInput) {
        console.log('📁 Triggering file input click (global)');
        
        // Simple approach using onchange property
        fileInput.onchange = (e) => {
            console.log('📁 File selected via onchange (global)');
            console.log('Files:', e.target.files);
            
            if (e.target.files && e.target.files.length > 0) {
                const file = e.target.files[0];
                console.log('📁 Processing file:', file.name);
                
                // Try to use the app instance, but fall back to standalone handling
                const handleFile = (file) => {
                    if (window.app && window.app.handleFileSelect) {
                        console.log('✅ Using app instance to handle file');
                        window.app.handleFileSelect(file);
                    } else {
                        console.log('🔄 App not ready, using standalone file handling');
                        handleFileStandalone(file);
                    }
                };
                
                // Standalone file handling function
                const handleFileStandalone = (file) => {
                    console.log('📁 handleFileStandalone called with file:', file.name);
                    
                    // Validate file type
                    const validTypes = ['.csv', '.jsonl', '.json'];
                    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                    
                    console.log('🔍 File extension:', fileExtension);
                    
                    if (!validTypes.includes(fileExtension)) {
                        console.error('❌ Invalid file type:', fileExtension);
                        alert('Please select a CSV or JSONL file');
                        return;
                    }
                    
                    console.log('✅ File type validation passed');
                    
                    // Show upload form
                    const uploadArea = document.getElementById('upload-area');
                    const uploadForm = document.getElementById('upload-form');
                    
                    console.log('🔄 Switching to upload form...');
                    console.log('Upload area found:', !!uploadArea);
                    console.log('Upload form found:', !!uploadForm);
                    
                    if (uploadArea && uploadForm) {
                        uploadArea.style.display = 'none';
                        uploadForm.style.display = 'block';
                        console.log('✅ Upload form displayed');
                        
                        // Store file globally for later use
                        window.selectedFile = file;
                        console.log('💾 File stored globally');
                        
                        // Pre-fill name
                        const nameInput = document.getElementById('dataset-name');
                        if (nameInput) {
                            const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
                            nameInput.value = fileName;
                            console.log('✅ Pre-filled dataset name:', fileName);
                        } else {
                            console.error('❌ Could not find dataset name input');
                        }
                        
                        // Show success message
                        console.log('🎉 File processing completed successfully!');
                        
                    } else {
                        console.error('❌ Could not find upload area or form elements');
                        alert('Upload form not found. Please refresh the page and try again.');
                    }
                };
                
                // Try app first, then fallback
                handleFile(file);
            } else {
                console.warn('⚠️ No files found');
            }
        };
        
        fileInput.click();
    } else {
        console.error('❌ File input element not found');
        alert('File input not found. Please refresh the page.');
    }
};

// Standalone dataset loading function
const loadDatasetsStandalone = async () => {
    console.log('📊 Loading datasets standalone...');
    
    try {
        const response = await fetch('/api/datasets');
        const data = await response.json();
        
        console.log('📊 Datasets loaded:', data.datasets.length);
        
        // Store datasets globally
        window.datasets = new Map();
        data.datasets.forEach(dataset => {
            window.datasets.set(dataset.id, dataset);
        });
        
        // Render datasets
        renderDatasetsStandalone();
        
    } catch (error) {
        console.error('❌ Failed to load datasets:', error);
    }
};

// Standalone dataset rendering function
const renderDatasetsStandalone = () => {
    console.log('🎨 Rendering datasets standalone...');
    
    const container = document.getElementById('datasets-container');
    if (!container) {
        console.error('❌ Datasets container not found');
        return;
    }
    
    if (!window.datasets || window.datasets.size === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h4>No datasets yet</h4>
                <p>Upload your first dataset to get started</p>
            </div>
        `;
        console.log('📊 No datasets to display');
        return;
    }
    
    const datasetsHtml = Array.from(window.datasets.values()).map(dataset => `
        <div class="dataset-item">
            <div class="item-header">
                <div>
                    <div class="item-title">${dataset.name}</div>
                    <div class="item-meta">${dataset.row_count} rows • ${dataset.columns.length} columns</div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-secondary" onclick="viewDataset('${dataset.id}')">
                        👁️ View
                    </button>
                    <button class="btn btn-error" onclick="deleteDataset('${dataset.id}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
            <p class="item-description">${dataset.description || 'No description'}</p>
            <div class="item-meta">
                <small>Created: ${new Date(dataset.created_at).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = datasetsHtml;
    console.log('✅ Datasets rendered:', window.datasets.size);
};

// Make standalone functions globally available
window.loadDatasetsStandalone = loadDatasetsStandalone;
window.renderDatasetsStandalone = renderDatasetsStandalone;
window.loadPromptsStandalone = loadPromptsStandalone;
window.renderPromptsStandalone = renderPromptsStandalone;

// Global functions for dataset actions
window.viewDataset = async (datasetId) => {
    console.log('👁️ View dataset:', datasetId);
    
    if (window.app && window.app.viewDataset) {
        return window.app.viewDataset(datasetId);
    }
    
    // Enhanced standalone dataset viewer
    const dataset = window.datasets?.get(datasetId);
    if (!dataset) {
        alert('Dataset not found');
        return;
    }
    
    console.log('📊 Loading dataset contents for:', dataset.name);
    
    try {
        // Fetch dataset preview from server
        const response = await fetch(`/api/datasets/${datasetId}/preview?limit=50`);
        
        if (!response.ok) {
            throw new Error(`Failed to load dataset: ${response.statusText}`);
        }
        
        const previewData = await response.json();
        console.log('📊 Dataset preview loaded:', previewData);
        
        // Create and show dataset viewer modal
        showDatasetViewer(dataset, previewData);
        
    } catch (error) {
        console.error('❌ Failed to load dataset contents:', error);
        
        // Fallback: show basic info
        alert(`Dataset: ${dataset.name}\nRows: ${dataset.row_count}\nColumns: ${dataset.columns.join(', ')}\n\nError loading contents: ${error.message}`);
    }
};

// Dataset viewer modal function
const showDatasetViewer = (dataset, previewData) => {
    console.log('🎨 Showing dataset viewer for:', dataset.name);
    
    // Create modal HTML
    const modalHtml = `
        <div id="dataset-viewer-modal" class="modal active">
            <div class="modal-content" style="max-width: 90vw; max-height: 90vh;">
                <div class="modal-header">
                    <h3>📊 Dataset: ${dataset.name}</h3>
                    <button class="modal-close" onclick="closeDatasetViewer()">&times;</button>
                </div>
                <div class="modal-body" style="overflow: auto;">
                    <div class="dataset-info">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                            <div class="info-card">
                                <strong>Rows:</strong> ${dataset.row_count}
                            </div>
                            <div class="info-card">
                                <strong>Columns:</strong> ${dataset.columns.length}
                            </div>
                            <div class="info-card">
                                <strong>File:</strong> ${dataset.filename}
                            </div>
                            <div class="info-card">
                                <strong>Created:</strong> ${new Date(dataset.created_at).toLocaleDateString()}
                            </div>
                        </div>
                        ${dataset.description ? `<p><strong>Description:</strong> ${dataset.description}</p>` : ''}
                    </div>
                    
                    <div class="dataset-contents">
                        <h4>Dataset Contents ${previewData.preview ? `(First ${previewData.preview.length} rows)` : ''}</h4>
                        <div id="dataset-table-container">
                            ${createDatasetTable(previewData.preview || [], dataset.columns)}
                        </div>
                        ${previewData.preview && previewData.preview.length < dataset.row_count ? 
                            `<p style="margin-top: 1rem; color: #666; font-style: italic;">
                                Showing ${previewData.preview.length} of ${dataset.row_count} rows
                            </p>` : ''
                        }
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeDatasetViewer()">Close</button>
                    <button class="btn btn-primary" onclick="downloadDataset('${dataset.id}')">📥 Download</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const existingModal = document.getElementById('dataset-viewer-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Add CSS for the modal if not already present
    if (!document.getElementById('dataset-viewer-styles')) {
        const styles = `
            <style id="dataset-viewer-styles">
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                }
                .modal.active {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .modal-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    width: 90%;
                    max-width: 1200px;
                    max-height: 90vh;
                    display: flex;
                    flex-direction: column;
                }
                .modal-header {
                    padding: 1.5rem;
                    border-bottom: 1px solid #e5e7eb;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .modal-body {
                    padding: 1.5rem;
                    flex: 1;
                    overflow: auto;
                }
                .modal-footer {
                    padding: 1.5rem;
                    border-top: 1px solid #e5e7eb;
                    display: flex;
                    justify-content: flex-end;
                    gap: 1rem;
                }
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                    color: #666;
                }
                .modal-close:hover {
                    color: #000;
                }
                .info-card {
                    padding: 0.75rem;
                    background: #f8fafc;
                    border-radius: 4px;
                    border: 1px solid #e5e7eb;
                }
                .dataset-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 1rem;
                    font-size: 0.875rem;
                }
                .dataset-table th,
                .dataset-table td {
                    padding: 0.75rem;
                    text-align: left;
                    border-bottom: 1px solid #e5e7eb;
                    max-width: 300px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .dataset-table th {
                    background: #f8fafc;
                    font-weight: 600;
                    position: sticky;
                    top: 0;
                }
                .dataset-table td:hover {
                    white-space: normal;
                    word-wrap: break-word;
                }
            </style>
        `;
        document.head.insertAdjacentHTML('beforeend', styles);
    }
};

// Create dataset table HTML
const createDatasetTable = (data, columns) => {
    if (!data || data.length === 0) {
        return '<p>No data to display</p>';
    }
    
    // Use provided columns or extract from first row
    const tableColumns = columns && columns.length > 0 ? columns : Object.keys(data[0]);
    
    const headerHtml = tableColumns.map(col => `<th>${col}</th>`).join('');
    
    const rowsHtml = data.map(row => {
        const cellsHtml = tableColumns.map(col => {
            const value = row[col];
            const displayValue = value !== null && value !== undefined ? String(value) : '';
            return `<td title="${displayValue}">${displayValue}</td>`;
        }).join('');
        return `<tr>${cellsHtml}</tr>`;
    }).join('');
    
    return `
        <table class="dataset-table">
            <thead>
                <tr>${headerHtml}</tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
};

// Close dataset viewer
window.closeDatasetViewer = () => {
    const modal = document.getElementById('dataset-viewer-modal');
    if (modal) {
        modal.remove();
    }
};

// Download dataset
window.downloadDataset = async (datasetId) => {
    console.log('📥 Download dataset:', datasetId);
    
    try {
        const response = await fetch(`/api/datasets/${datasetId}/export?format=csv`);
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dataset_${datasetId}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✅ Dataset download initiated');
        
    } catch (error) {
        console.error('❌ Download failed:', error);
        alert(`Download failed: ${error.message}`);
    }
};

window.deleteDataset = (datasetId) => {
    console.log('🗑️ Delete dataset:', datasetId);
    if (window.app && window.app.deleteDataset) {
        return window.app.deleteDataset(datasetId);
    }
    // Fallback: simple delete
    if (confirm('Are you sure you want to delete this dataset?')) {
        window.datasets?.delete(datasetId);
        renderDatasetsStandalone();
        console.log('✅ Dataset deleted (local only)');
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🚀 Starting Nova Prompt Optimizer initialization');
        
        // Setup standalone navigation first
        setupNavigationStandalone();
        
        // Load datasets immediately for standalone functionality
        await loadDatasetsStandalone();
        
        // Load prompts immediately for standalone functionality
        try {
            await loadPromptsStandalone();
        } catch (error) {
            console.error('❌ Failed to load prompts during initialization:', error);
        }
        
        // Initialize main app
        window.app = new NovaOptimizerApp();
        
        // Wait for app to be fully initialized
        await window.app.initPromise;
        
        // Force reload datasets after app initialization to ensure they're visible
        console.log('🔄 Force reloading datasets after app init...');
        setTimeout(async () => {
            await loadDatasetsStandalone();
            console.log('✅ Datasets force-reloaded after app initialization');
        }, 100);
        
        console.log('✅ Application fully initialized and ready');
        
    } catch (error) {
        console.error('❌ Failed to initialize application:', error);
        
        // Even if app fails, ensure standalone functionality works
        console.log('🔄 Setting up standalone functionality...');
        
        try {
            setupNavigationStandalone();
            await loadDatasetsStandalone();
            await loadPromptsStandalone();
            console.log('✅ Standalone functionality ready');
        } catch (standaloneError) {
            console.error('❌ Standalone setup also failed:', standaloneError);
        }
        
        document.body.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: #d32f2f;">
                <h2>⚠️ Application Initialization Error</h2>
                <p>Failed to initialize the application: ${error.message}</p>
                <p>Some features may still work. Try refreshing the page.</p>
                <button onclick="location.reload()" style="padding: 0.5rem 1rem; margin-top: 1rem;">
                    🔄 Refresh Page
                </button>
            </div>
        `;
    }
});

// Standalone navigation system
const setupNavigationStandalone = () => {
    console.log('🧭 Setting up standalone navigation...');
    
    const navButtons = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');
    
    console.log('Nav buttons found:', navButtons.length);
    console.log('Views found:', views.length);
    
    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetView = e.target.dataset.view;
            console.log('🧭 Navigation clicked:', targetView);
            
            // Update navigation buttons
            navButtons.forEach(navBtn => navBtn.classList.remove('active'));
            e.target.classList.add('active');
            
            // Update views
            views.forEach(view => view.classList.remove('active'));
            const targetViewElement = document.getElementById(`${targetView}-view`);
            if (targetViewElement) {
                targetViewElement.classList.add('active');
                console.log('✅ Switched to view:', targetView);
            } else {
                console.error('❌ Target view not found:', `${targetView}-view`);
            }
            
            // Handle view-specific loading
            handleViewChange(targetView);
        });
    });
    
    console.log('✅ Standalone navigation setup complete');
};

// Handle view changes
const handleViewChange = async (viewName) => {
    console.log('🔄 Handling view change to:', viewName);
    
    switch (viewName) {
        case 'datasets':
            await loadDatasetsStandalone();
            break;
        case 'prompts':
            await loadPromptsStandalone();
            break;
        case 'optimization':
            loadOptimizationOptionsStandalone();
            break;
        case 'results':
            renderResultsStandalone();
            break;
    }
};
// Debug function to test prompts functionality
window.debugPrompts = () => {
    console.log('🔍 Debug prompts functionality');
    console.log('Prompts container:', document.getElementById('prompts-container'));
    console.log('Prompt modal:', document.getElementById('prompt-modal'));
    console.log('New prompt button:', document.querySelector('button[onclick="createNewPrompt()"]'));
    console.log('Window prompts:', window.prompts);
    console.log('createNewPrompt function:', window.createNewPrompt);
    
    // Test loading prompts
    loadPromptsStandalone();
};

/**
 * Nova Prompt Optimizer - Main Application
 * Lightweight vanilla JavaScript implementation
 */

class NovaOptimizerApp {
    constructor() {
        this.currentView = 'datasets';
        this.datasets = new Map();
        this.prompts = new Map();
        this.optimizations = new Map();
        this.websockets = new Map();
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing Nova Prompt Optimizer');
        
        this.setupNavigation();
        this.setupEventListeners();
        await this.loadInitialData();
        
        console.log('✅ Application initialized');
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
        // File upload drag and drop
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelect(files[0]);
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }
        
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
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadDatasets(),
                this.loadPrompts(),
                this.loadOptimizations()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showToast('Failed to load application data', 'error');
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
            
            this.datasets.clear();
            data.datasets.forEach(dataset => {
                this.datasets.set(dataset.id, dataset);
            });
            
            this.renderDatasets();
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
        // Validate file type
        const validTypes = ['.csv', '.jsonl', '.json'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileExtension)) {
            this.showToast('Please select a CSV or JSONL file', 'error');
            return;
        }
        
        // Show upload form
        document.getElementById('upload-area').style.display = 'none';
        document.getElementById('upload-form').style.display = 'block';
        
        // Store file for upload
        this.selectedFile = file;
        
        // Pre-fill name
        const nameInput = document.getElementById('dataset-name');
        nameInput.value = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
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
    
    // Optimization
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

window.uploadDataset = () => window.app?.uploadDataset();
window.cancelUpload = () => window.app?.cancelUpload();
window.createNewPrompt = () => window.app?.createNewPrompt();
window.closePromptModal = () => window.app?.closePromptModal();
window.savePrompt = () => window.app?.savePrompt();
window.startOptimization = () => window.app?.startOptimization();

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new NovaOptimizerApp();
});

// Export for module use
export default NovaOptimizerApp;

/**
 * Nova Prompt Optimizer - Prompt Management Module
 * Handles prompt creation, editing, and variable detection
 */

class PromptManager {
    constructor(app) {
        this.app = app;
        this.currentPromptId = null;
        this.setupPromptEditor();
    }
    
    setupPromptEditor() {
        // Variable detection on user prompt changes
        const userPromptTextarea = document.getElementById('user-prompt');
        if (userPromptTextarea) {
            userPromptTextarea.addEventListener('input', () => {
                this.detectVariables();
            });
        }
    }
    
    createNewPrompt() {
        this.currentPromptId = null;
        this.clearPromptForm();
        
        document.getElementById('prompt-modal-title').textContent = 'Create New Prompt';
        document.getElementById('prompt-modal').classList.add('active');
    }
    
    async editPrompt(promptId) {
        this.currentPromptId = promptId;
        const prompt = this.app.prompts.get(promptId);
        
        if (!prompt) {
            this.app.showToast('Prompt not found', 'error');
            return;
        }
        
        // Populate form
        document.getElementById('prompt-name').value = prompt.name;
        document.getElementById('prompt-description').value = prompt.description || '';
        document.getElementById('system-prompt').value = prompt.system_prompt || '';
        document.getElementById('user-prompt').value = prompt.user_prompt || '';
        
        // Update modal title
        document.getElementById('prompt-modal-title').textContent = 'Edit Prompt';
        
        // Detect variables
        this.detectVariables();
        
        // Show modal
        document.getElementById('prompt-modal').classList.add('active');
    }
    
    async savePrompt() {
        const name = document.getElementById('prompt-name').value.trim();
        const description = document.getElementById('prompt-description').value.trim();
        const systemPrompt = document.getElementById('system-prompt').value.trim();
        const userPrompt = document.getElementById('user-prompt').value.trim();
        
        // Validation
        if (!name) {
            this.app.showToast('Please enter a prompt name', 'error');
            return;
        }
        
        if (!userPrompt) {
            this.app.showToast('Please enter a user prompt', 'error');
            return;
        }
        
        // Extract variables
        const variables = this.extractVariables(userPrompt);
        
        const promptData = {
            name,
            description,
            system_prompt: systemPrompt,
            user_prompt: userPrompt,
            variables
        };
        
        try {
            this.app.showLoading('Saving prompt...');
            
            let response;
            if (this.currentPromptId) {
                // Update existing prompt
                response = await fetch(`/api/prompts/${this.currentPromptId}`, {
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
            
            if (!response.ok) {
                throw new Error(`Failed to save prompt: ${response.statusText}`);
            }
            
            const savedPrompt = await response.json();
            this.app.prompts.set(savedPrompt.id, savedPrompt);
            
            this.app.hideLoading();
            this.app.showToast(
                this.currentPromptId ? 'Prompt updated successfully!' : 'Prompt created successfully!',
                'success'
            );
            
            this.closePromptModal();
            this.app.renderPrompts();
            
        } catch (error) {
            this.app.hideLoading();
            console.error('Failed to save prompt:', error);
            this.app.showToast(`Failed to save prompt: ${error.message}`, 'error');
        }
    }
    
    async deletePrompt(promptId) {
        if (!confirm('Are you sure you want to delete this prompt?')) {
            return;
        }
        
        try {
            // For now, just remove from local storage
            // In a real implementation, you'd call DELETE /api/prompts/{id}
            this.app.prompts.delete(promptId);
            this.app.renderPrompts();
            this.app.showToast('Prompt deleted', 'success');
        } catch (error) {
            console.error('Failed to delete prompt:', error);
            this.app.showToast('Failed to delete prompt', 'error');
        }
    }
    
    detectVariables() {
        const userPrompt = document.getElementById('user-prompt').value;
        const variables = this.extractVariables(userPrompt);
        
        const variablesSection = document.getElementById('variables-detected');
        const variablesList = document.getElementById('variables-list');
        
        if (variables.length > 0) {
            variablesSection.style.display = 'block';
            variablesList.innerHTML = variables
                .map(variable => `<span class="variable-tag">${variable}</span>`)
                .join('');
        } else {
            variablesSection.style.display = 'none';
        }
    }
    
    extractVariables(text) {
        // Extract variables in {{variable}} format
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
    }
    
    clearPromptForm() {
        document.getElementById('prompt-name').value = '';
        document.getElementById('prompt-description').value = '';
        document.getElementById('system-prompt').value = '';
        document.getElementById('user-prompt').value = '';
        document.getElementById('variables-detected').style.display = 'none';
    }
    
    closePromptModal() {
        document.getElementById('prompt-modal').classList.remove('active');
        this.currentPromptId = null;
    }
    
    // Prompt validation helpers
    validatePrompt(promptData) {
        const errors = [];
        
        if (!promptData.name || !promptData.name.trim()) {
            errors.push('Prompt name is required');
        }
        
        if (!promptData.user_prompt || !promptData.user_prompt.trim()) {
            errors.push('User prompt is required');
        }
        
        // Check for unmatched braces
        const userPrompt = promptData.user_prompt || '';
        const openBraces = (userPrompt.match(/\{\{/g) || []).length;
        const closeBraces = (userPrompt.match(/\}\}/g) || []).length;
        
        if (openBraces !== closeBraces) {
            errors.push('Unmatched braces in user prompt - check your variable syntax');
        }
        
        return errors;
    }
    
    // Prompt preview functionality
    previewPrompt(promptData, sampleData = {}) {
        let preview = promptData.user_prompt || '';
        
        // Replace variables with sample data
        const variables = this.extractVariables(preview);
        variables.forEach(variable => {
            const value = sampleData[variable] || `[${variable}]`;
            const regex = new RegExp(`\\{\\{\\s*${variable}\\s*\\}\\}`, 'g');
            preview = preview.replace(regex, value);
        });
        
        return {
            system_prompt: promptData.system_prompt || '',
            user_prompt: preview,
            variables_used: variables,
            missing_variables: variables.filter(v => !(v in sampleData))
        };
    }
    
    // Export prompt functionality
    exportPrompt(promptId) {
        const prompt = this.app.prompts.get(promptId);
        if (!prompt) {
            this.app.showToast('Prompt not found', 'error');
            return;
        }
        
        const exportData = {
            name: prompt.name,
            description: prompt.description,
            system_prompt: prompt.system_prompt,
            user_prompt: prompt.user_prompt,
            variables: prompt.variables,
            exported_at: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${prompt.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_prompt.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.app.showToast('Prompt exported successfully', 'success');
    }
    
    // Import prompt functionality
    async importPrompt(file) {
        try {
            const text = await file.text();
            const promptData = JSON.parse(text);
            
            // Validate imported data
            const requiredFields = ['name', 'user_prompt'];
            const missingFields = requiredFields.filter(field => !promptData[field]);
            
            if (missingFields.length > 0) {
                throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
            }
            
            // Create new prompt from imported data
            const newPromptData = {
                name: `${promptData.name} (Imported)`,
                description: promptData.description || 'Imported prompt',
                system_prompt: promptData.system_prompt || '',
                user_prompt: promptData.user_prompt,
                variables: promptData.variables || this.extractVariables(promptData.user_prompt)
            };
            
            const response = await fetch('/api/prompts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newPromptData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to import prompt: ${response.statusText}`);
            }
            
            const savedPrompt = await response.json();
            this.app.prompts.set(savedPrompt.id, savedPrompt);
            this.app.renderPrompts();
            
            this.app.showToast('Prompt imported successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to import prompt:', error);
            this.app.showToast(`Failed to import prompt: ${error.message}`, 'error');
        }
    }
}

// Extend the main app with prompt management
function initializePromptManager() {
    if (window.app && window.app.initPromise) {
        window.app.initPromise.then(() => {
            window.app.promptManager = new PromptManager(window.app);
            
            // Add methods to main app
            window.app.createNewPrompt = () => window.app.promptManager.createNewPrompt();
            window.app.editPrompt = (id) => window.app.promptManager.editPrompt(id);
            window.app.savePrompt = () => window.app.promptManager.savePrompt();
            window.app.deletePrompt = (id) => window.app.promptManager.deletePrompt(id);
            window.app.closePromptModal = () => window.app.promptManager.closePromptModal();
            window.app.exportPrompt = (id) => window.app.promptManager.exportPrompt(id);
            
            console.log('✅ Prompt manager initialized');
        }).catch(error => {
            console.error('❌ Failed to initialize prompt manager:', error);
        });
    } else {
        // Retry after a short delay if app isn't ready
        setTimeout(initializePromptManager, 100);
    }
}

// Initialize when this module loads
initializePromptManager();

// Global functions for HTML onclick handlers
window.createNewPrompt = () => window.app?.createNewPrompt();
window.editPrompt = (id) => window.app?.editPrompt(id);
window.savePrompt = () => window.app?.savePrompt();
window.deletePrompt = (id) => window.app?.deletePrompt(id);
window.closePromptModal = () => window.app?.closePromptModal();
window.exportPrompt = (id) => window.app?.exportPrompt(id);

export default PromptManager;

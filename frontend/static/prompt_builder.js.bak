/**
 * JavaScript for Prompt Builder Interactive Functionality
 */

// Global counter for dynamic elements
let contextCounter = 0;
let instructionCounter = 0;
let formatCounter = 0;
let variableCounter = 0;

// Initialize counters based on existing elements
document.addEventListener('DOMContentLoaded', function() {
    contextCounter = document.querySelectorAll('.context-item:not(.template)').length;
    instructionCounter = document.querySelectorAll('.instruction-item:not(.template)').length;
    formatCounter = document.querySelectorAll('.format-item:not(.template)').length;
    variableCounter = document.querySelectorAll('.variable-item:not(.template)').length;
});

// Context Management
function addContextItem() {
    const template = document.getElementById('context-template').querySelector('.context-item');
    const clone = template.cloneNode(true);
    
    // Update attributes
    clone.classList.remove('template');
    clone.setAttribute('data-index', contextCounter);
    
    const input = clone.querySelector('input');
    input.name = `context_${contextCounter}`;
    input.value = '';
    
    const button = clone.querySelector('button');
    button.onclick = () => removeContextItem(contextCounter);
    
    document.getElementById('context-list').appendChild(clone);
    contextCounter++;
    
    // Focus on new input
    input.focus();
}

function removeContextItem(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
}

// Instructions Management
function addInstruction() {
    const template = document.getElementById('instruction-template').querySelector('.instruction-item');
    const clone = template.cloneNode(true);
    
    clone.classList.remove('template');
    clone.setAttribute('data-index', instructionCounter);
    
    const input = clone.querySelector('input');
    input.name = `instruction_${instructionCounter}`;
    input.value = '';
    
    const button = clone.querySelector('button');
    button.onclick = () => removeInstruction(instructionCounter);
    
    document.getElementById('instructions-list').appendChild(clone);
    instructionCounter++;
    
    input.focus();
}

function removeInstruction(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
}

// Format Management
function addFormatItem() {
    const template = document.getElementById('format-template').querySelector('.format-item');
    const clone = template.cloneNode(true);
    
    clone.classList.remove('template');
    clone.setAttribute('data-index', formatCounter);
    
    const input = clone.querySelector('input');
    input.name = `format_${formatCounter}`;
    input.value = '';
    
    const button = clone.querySelector('button');
    button.onclick = () => removeFormatItem(formatCounter);
    
    document.getElementById('format-list').appendChild(clone);
    formatCounter++;
    
    input.focus();
}

function removeFormatItem(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
}

// Variables Management
function addVariable() {
    const template = document.getElementById('variable-template').querySelector('.variable-item');
    const clone = template.cloneNode(true);
    
    clone.classList.remove('template');
    clone.setAttribute('data-index', variableCounter);
    
    const input = clone.querySelector('input');
    input.name = `variable_${variableCounter}`;
    input.value = '';
    
    const button = clone.querySelector('button');
    button.onclick = () => removeVariable(variableCounter);
    
    document.getElementById('variables-list').appendChild(clone);
    variableCounter++;
    
    input.focus();
}

function removeVariable(index) {
    const item = document.querySelector(`[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
}

// Form Data Collection
function collectFormData() {
    const formData = {
        task: document.getElementById('task-input').value,
        context: [],
        instructions: [],
        response_format: [],
        variables: [],
        metadata: {}
    };
    
    // Collect context items
    document.querySelectorAll('.context-item:not(.template) input').forEach(input => {
        if (input.value.trim()) {
            formData.context.push(input.value.trim());
        }
    });
    
    // Collect instructions
    document.querySelectorAll('.instruction-item:not(.template) input').forEach(input => {
        if (input.value.trim()) {
            formData.instructions.push(input.value.trim());
        }
    });
    
    // Collect format requirements
    document.querySelectorAll('.format-item:not(.template) input').forEach(input => {
        if (input.value.trim()) {
            formData.response_format.push(input.value.trim());
        }
    });
    
    // Collect variables
    document.querySelectorAll('.variable-item:not(.template) input').forEach(input => {
        if (input.value.trim()) {
            formData.variables.push(input.value.trim());
        }
    });
    
    return formData;
}

// Preview Functionality
async function previewPrompt() {
    const formData = collectFormData();
    
    try {
        const response = await fetch('/prompt-builder/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.text();
            document.getElementById('preview-container').innerHTML = result;
            document.getElementById('preview-container').style.display = 'block';
        } else {
            showError('Failed to generate preview');
        }
    } catch (error) {
        showError('Error generating preview: ' + error.message);
    }
}

// Validation Functionality
async function validatePrompt() {
    const formData = collectFormData();
    
    try {
        const response = await fetch('/prompt-builder/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.text();
            document.getElementById('validation-container').innerHTML = result;
            document.getElementById('validation-container').style.display = 'block';
        } else {
            showError('Failed to validate prompt');
        }
    } catch (error) {
        showError('Error validating prompt: ' + error.message);
    }
}

// Template Management
async function loadTemplate(templateId) {
    if (!templateId) return;
    
    try {
        const response = await fetch(`/prompt-builder/template/${templateId}`);
        
        if (response.ok) {
            const template = await response.json();
            populateForm(template.builder_data);
            showSuccess(`Template "${template.name}" loaded successfully`);
        } else {
            showError('Failed to load template');
        }
    } catch (error) {
        showError('Error loading template: ' + error.message);
    }
}

function populateForm(builderData) {
    // Clear existing form
    clearForm();
    
    // Populate task
    document.getElementById('task-input').value = builderData.task || '';
    
    // Populate context items
    (builderData.context || []).forEach(item => {
        addContextItem();
        const inputs = document.querySelectorAll('.context-item:not(.template) input');
        inputs[inputs.length - 1].value = item;
    });
    
    // Populate instructions
    (builderData.instructions || []).forEach(item => {
        addInstruction();
        const inputs = document.querySelectorAll('.instruction-item:not(.template) input');
        inputs[inputs.length - 1].value = item;
    });
    
    // Populate response format
    (builderData.response_format || []).forEach(item => {
        addFormatItem();
        const inputs = document.querySelectorAll('.format-item:not(.template) input');
        inputs[inputs.length - 1].value = item;
    });
    
    // Populate variables
    (builderData.variables || []).forEach(item => {
        addVariable();
        const inputs = document.querySelectorAll('.variable-item:not(.template) input');
        inputs[inputs.length - 1].value = item;
    });
}

function clearForm() {
    // Clear task
    document.getElementById('task-input').value = '';
    
    // Clear dynamic lists
    document.getElementById('context-list').innerHTML = '';
    document.getElementById('instructions-list').innerHTML = '';
    document.getElementById('format-list').innerHTML = '';
    document.getElementById('variables-list').innerHTML = '';
    
    // Reset counters
    contextCounter = 0;
    instructionCounter = 0;
    formatCounter = 0;
    variableCounter = 0;
    
    // Hide preview and validation
    document.getElementById('preview-container').style.display = 'none';
    document.getElementById('validation-container').style.display = 'none';
}

// Save Template Functionality
function showSaveTemplateForm() {
    document.getElementById('save-template-form').style.display = 'block';
}

function hideSaveTemplateForm() {
    document.getElementById('save-template-form').style.display = 'none';
    document.querySelector('input[name="template_name"]').value = '';
    document.querySelector('textarea[name="template_description"]').value = '';
}

async function saveTemplate() {
    const formData = collectFormData();
    const templateName = document.querySelector('input[name="template_name"]').value;
    const templateDescription = document.querySelector('textarea[name="template_description"]').value;
    
    if (!templateName.trim()) {
        showError('Template name is required');
        return;
    }
    
    try {
        const response = await fetch('/prompt-builder/save-template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: templateName,
                description: templateDescription,
                builder_data: formData
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showSuccess(`Template "${templateName}" saved successfully`);
            hideSaveTemplateForm();
            
            // Refresh template selector
            location.reload();
        } else {
            showError('Failed to save template');
        }
    } catch (error) {
        showError('Error saving template: ' + error.message);
    }
}

// Utility Functions
function showError(message) {
    // Create or update error message
    let errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error-message';
        errorDiv.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50';
        document.body.appendChild(errorDiv);
    }
    
    errorDiv.innerHTML = `
        <span class="block sm:inline">${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-red-700 hover:text-red-900">×</button>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    // Create or update success message
    let successDiv = document.getElementById('success-message');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = 'success-message';
        successDiv.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50';
        document.body.appendChild(successDiv);
    }
    
    successDiv.innerHTML = `
        <span class="block sm:inline">${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-2 text-green-700 hover:text-green-900">×</button>
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (successDiv.parentElement) {
            successDiv.remove();
        }
    }, 3000);
}

// Form Submission Handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prompt-builder-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = collectFormData();
            
            try {
                const response = await fetch('/prompt-builder/build', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    showSuccess('Prompt built successfully!');
                    
                    // Redirect to prompts page or show success
                    if (result.redirect) {
                        window.location.href = result.redirect;
                    }
                } else {
                    const error = await response.json();
                    showError(error.message || 'Failed to build prompt');
                }
            } catch (error) {
                showError('Error building prompt: ' + error.message);
            }
        });
    }
});

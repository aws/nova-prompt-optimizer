/**
 * Metrics page JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeMetricsPage();
});

function initializeMetricsPage() {
    // Modal functionality
    initializeModal();
    
    // Tab functionality
    initializeTabs();
    
    // Form functionality
    initializeForm();
    
    // Example prompts
    initializeExamplePrompts();
}

function initializeModal() {
    const modal = document.querySelector('[data-ref="metric-modal"]');
    if (!modal) return;
    
    // Open modal buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-action="create-metric"]')) {
            e.preventDefault();
            showModal();
        }
        
        if (e.target.matches('[data-action="close-modal"]')) {
            e.preventDefault();
            hideModal();
        }
    });
    
    // Close modal on backdrop click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideModal();
        }
    });
}

function showModal() {
    const modal = document.querySelector('[data-ref="metric-modal"]');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal() {
    const modal = document.querySelector('[data-ref="metric-modal"]');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
        
        // Reset form
        resetForm();
    }
}

function initializeTabs() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-tab]')) {
            e.preventDefault();
            switchTab(e.target.dataset.tab);
        }
    });
}

function switchTab(tabName) {
    // Update tab triggers
    document.querySelectorAll('.tab-trigger').forEach(trigger => {
        trigger.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.add('hidden');
        panel.classList.remove('active');
    });
    
    const activePanel = document.querySelector(`[data-tab-panel="${tabName}"]`);
    if (activePanel) {
        activePanel.classList.remove('hidden');
        activePanel.classList.add('active');
    }
}

function initializeForm() {
    // Auto-preview on natural language input
    const nlInput = document.querySelector('[data-field="natural-language-input"]');
    const nameInput = document.querySelector('[data-field="metric-name"]');
    
    if (nlInput) {
        let previewTimeout;
        nlInput.addEventListener('input', function() {
            clearTimeout(previewTimeout);
            previewTimeout = setTimeout(() => {
                if (nlInput.value.trim()) {
                    previewMetric();
                }
            }, 1000); // Debounce 1 second
        });
    }
    
    // Save metric button
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-action="save-metric"]')) {
            e.preventDefault();
            saveMetric();
        }
    });
}

function initializeExamplePrompts() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.example-prompt')) {
            e.preventDefault();
            const exampleText = e.target.dataset.example;
            const nlInput = document.querySelector('[data-field="natural-language-input"]');
            if (nlInput) {
                nlInput.value = exampleText;
                previewMetric();
            }
        }
    });
}

async function previewMetric() {
    const nameInput = document.querySelector('[data-field="metric-name"]');
    const nlInput = document.querySelector('[data-field="natural-language-input"]');
    const codePreview = document.querySelector('[data-ref="code-preview"]');
    
    if (!nlInput || !codePreview) return;
    
    const formData = new FormData();
    formData.append('name', nameInput?.value || 'Untitled Metric');
    formData.append('natural_language', nlInput.value);
    
    try {
        codePreview.textContent = 'Generating preview...';
        
        const response = await fetch('/metrics/preview', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            codePreview.textContent = result.code;
        } else {
            codePreview.textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        codePreview.textContent = `Error: ${error.message}`;
    }
}

async function saveMetric() {
    const nameInput = document.querySelector('[data-field="metric-name"]');
    const descInput = document.querySelector('[data-field="metric-description"]');
    const nlInput = document.querySelector('[data-field="natural-language-input"]');
    
    if (!nameInput || !nlInput) return;
    
    const name = nameInput.value.trim();
    const description = descInput?.value.trim() || '';
    const naturalLanguage = nlInput.value.trim();
    
    if (!name || !naturalLanguage) {
        alert('Please provide a name and natural language description');
        return;
    }
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('natural_language', naturalLanguage);
    
    try {
        const response = await fetch('/metrics/create', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Metric created successfully!');
            hideModal();
            // Reload page to show new metric
            window.location.reload();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function resetForm() {
    // Clear all form inputs
    document.querySelectorAll('[data-field]').forEach(input => {
        input.value = '';
    });
    
    // Clear code preview
    const codePreview = document.querySelector('[data-ref="code-preview"]');
    if (codePreview) {
        codePreview.textContent = '# Metric code will appear here after you describe your evaluation criteria...';
    }
    
    // Reset to first tab
    switchTab('natural-language');
}

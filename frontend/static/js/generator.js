let currentSessionId = null;
let progressInterval = null;

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to conversation
    addMessageToConversation('user', message);
    input.value = '';
    
    try {
        const response = await fetch('/datasets/generator/start-conversation', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `message=${encodeURIComponent(message)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentSessionId = result.session_id;
            addMessageToConversation('assistant', result.response);
            
            if (result.ready_for_generation) {
                showModelSelection();
            }
        } else {
            addMessageToConversation('assistant', 'Error: ' + result.error);
        }
    } catch (error) {
        addMessageToConversation('assistant', 'Error: ' + error.message);
    }
}

function addMessageToConversation(role, message) {
    const container = document.getElementById('conversation-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-3 p-3 rounded-md ${role === 'user' ? 'bg-blue-50 ml-8' : 'bg-gray-50 mr-8'}`;
    messageDiv.innerHTML = `<strong>${role === 'user' ? 'You' : 'AI'}:</strong> ${message}`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showModelSelection() {
    document.getElementById('model-selection').classList.remove('hidden');
}

async function proceedToGeneration() {
    const selectedModel = document.querySelector('input[name="model"]:checked');
    if (!selectedModel) {
        alert('Please select a model');
        return;
    }
    
    // Show generation section with progress bar
    const generationDiv = document.getElementById('sample-generation');
    generationDiv.innerHTML = `
        <div class="bg-white border border-gray-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Generating Dataset Samples</h3>
            <div class="mb-4">
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span id="progress-text">0 / 0 samples</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div id="progress-bar" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
            </div>
            <div id="generation-status" class="text-sm text-gray-600">Starting generation...</div>
        </div>
    `;
    generationDiv.classList.remove('hidden');
    
    // Start generation
    try {
        const response = await fetch('/datasets/generator/generate-samples', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `session_id=${currentSessionId}&model_id=${selectedModel.value}`
        });
        
        // Start progress monitoring
        startProgressMonitoring();
        
        const result = await response.json();
        
        if (result.success) {
            stopProgressMonitoring();
            showGeneratedSamples(result);
        } else {
            stopProgressMonitoring();
            document.getElementById('generation-status').innerHTML = `<span class="text-red-600">Error: ${result.error}</span>`;
        }
    } catch (error) {
        stopProgressMonitoring();
        document.getElementById('generation-status').innerHTML = `<span class="text-red-600">Error: ${error.message}</span>`;
    }
}

function startProgressMonitoring() {
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/datasets/generator/progress/${currentSessionId}`);
            const progress = await response.json();
            
            updateProgressBar(progress.current || 0, progress.total || 0, progress.status || 'generating');
        } catch (error) {
            console.error('Error fetching progress:', error);
        }
    }, 1000);
}

function stopProgressMonitoring() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function updateProgressBar(current, total, status) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const statusDiv = document.getElementById('generation-status');
    
    if (total > 0) {
        const percentage = Math.round((current / total) * 100);
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${current} / ${total} samples`;
        
        if (status === 'completed') {
            statusDiv.innerHTML = '<span class="text-green-600">Generation completed!</span>';
            stopProgressMonitoring();
        } else if (status === 'error') {
            statusDiv.innerHTML = '<span class="text-red-600">Generation failed</span>';
            stopProgressMonitoring();
        } else {
            statusDiv.textContent = `Generating samples... (${current}/${total})`;
        }
    }
}

function showGeneratedSamples(result) {
    // Implementation for showing generated samples
    // This would display the samples and allow editing/saving
    console.log('Generated samples:', result);
}

// Allow Enter key to send message
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('user-input');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

describe('Complete Optimization Workflow', () => {
  beforeEach(() => {
    // Mock API responses
    cy.intercept('POST', '/api/datasets/upload', {
      fixture: 'dataset-response.json'
    }).as('uploadDataset')
    
    cy.intercept('POST', '/api/prompts', {
      fixture: 'prompt-response.json'
    }).as('createPrompt')
    
    cy.intercept('POST', '/api/optimize/start', {
      fixture: 'optimization-task.json'
    }).as('startOptimization')
    
    cy.intercept('GET', '/api/optimize/*/status', {
      fixture: 'optimization-status.json'
    }).as('getOptimizationStatus')
    
    cy.intercept('GET', '/api/optimize/*/results', {
      fixture: 'optimization-results.json'
    }).as('getOptimizationResults')
  })

  it('completes full optimization workflow', () => {
    // Step 1: Upload dataset
    cy.uploadDataset('sample-dataset.csv', ['input'], ['output'])
    cy.wait('@uploadDataset')
    
    // Verify dataset was uploaded
    cy.get('[data-testid="dataset-list"]').should('contain', 'sample-dataset.csv')
    
    // Step 2: Create prompt
    cy.createPrompt(
      'Test Optimization Prompt',
      'You are a helpful assistant.',
      'Answer the following question: {{input}}'
    )
    cy.wait('@createPrompt')
    
    // Verify prompt was created
    cy.get('[data-testid="prompt-list"]').should('contain', 'Test Optimization Prompt')
    
    // Step 3: Start optimization
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    cy.wait('@startOptimization')
    
    // Step 4: Monitor progress
    cy.get('[data-testid="optimization-progress"]').should('be.visible')
    cy.get('[data-testid="progress-bar"]').should('exist')
    
    // Wait for completion
    cy.waitForOptimization('task-123')
    cy.wait('@getOptimizationResults')
    
    // Step 5: View results
    cy.get('[data-testid="optimization-results"]').should('be.visible')
    cy.get('[data-testid="original-prompt"]').should('contain', 'You are a helpful assistant')
    cy.get('[data-testid="optimized-prompt"]').should('be.visible')
    cy.get('[data-testid="performance-metrics"]').should('be.visible')
    
    // Verify improvement metrics
    cy.get('[data-testid="accuracy-improvement"]').should('contain', '%')
    cy.get('[data-testid="metrics-chart"]').should('be.visible')
  })

  it('handles optimization errors gracefully', () => {
    // Mock error response
    cy.intercept('POST', '/api/optimize/start', {
      statusCode: 400,
      body: { detail: 'Invalid configuration' }
    }).as('optimizationError')
    
    cy.visit('/optimization')
    
    // Try to start optimization with invalid config
    cy.get('[data-testid="start-optimization"]').click()
    cy.wait('@optimizationError')
    
    // Verify error is displayed
    cy.get('[data-testid="error-message"]').should('contain', 'Invalid configuration')
    cy.get('[data-testid="error-alert"]').should('be.visible')
  })

  it('allows canceling running optimization', () => {
    cy.intercept('POST', '/api/optimize/*/cancel', {
      body: { message: 'Optimization cancelled' }
    }).as('cancelOptimization')
    
    // Start optimization
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    
    // Cancel optimization
    cy.get('[data-testid="cancel-optimization"]').click()
    cy.get('[data-testid="confirm-cancel"]').click()
    cy.wait('@cancelOptimization')
    
    // Verify cancellation
    cy.get('[data-testid="optimization-status"]').should('contain', 'cancelled')
  })

  it('displays real-time progress updates', () => {
    // Mock WebSocket connection for real-time updates
    cy.window().then((win) => {
      // Mock WebSocket
      const mockWs = {
        send: cy.stub(),
        close: cy.stub(),
        addEventListener: cy.stub()
      }
      
      win.WebSocket = cy.stub().returns(mockWs)
    })
    
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    
    // Verify WebSocket connection
    cy.window().its('WebSocket').should('have.been.called')
    
    // Verify progress updates are displayed
    cy.get('[data-testid="current-step"]').should('be.visible')
    cy.get('[data-testid="estimated-completion"]').should('be.visible')
  })

  it('exports optimization results', () => {
    // Complete optimization first
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    
    cy.waitForOptimization('task-123')
    
    // Mock export endpoint
    cy.intercept('GET', '/api/optimize/*/export?format=json', {
      fixture: 'optimization-export.json'
    }).as('exportResults')
    
    // Export results
    cy.get('[data-testid="export-results"]').click()
    cy.get('[data-testid="export-format-json"]').click()
    cy.get('[data-testid="confirm-export"]').click()
    
    cy.wait('@exportResults')
    
    // Verify download
    cy.readFile('cypress/downloads/optimization_results_task-123.json').should('exist')
  })

  it('navigates between workflow steps', () => {
    // Test navigation
    cy.visit('/')
    
    // Navigate to datasets
    cy.navigateToStep('datasets')
    cy.get('[data-testid="dataset-upload"]').should('be.visible')
    
    // Navigate to prompts
    cy.navigateToStep('prompts')
    cy.get('[data-testid="prompt-editor"]').should('be.visible')
    
    // Navigate to optimization
    cy.navigateToStep('optimization')
    cy.get('[data-testid="optimization-config"]').should('be.visible')
    
    // Navigate to results
    cy.navigateToStep('results')
    cy.get('[data-testid="results-analysis"]').should('be.visible')
  })

  it('maintains state across page refreshes', () => {
    // Start optimization
    cy.startOptimization({
      datasetId: 'dataset-123',
      promptId: 'prompt-123',
      optimizerType: 'nova',
      modelName: 'nova-pro'
    })
    
    // Refresh page
    cy.reload()
    
    // Verify state is maintained
    cy.get('[data-testid="optimization-task-id"]').should('contain', 'task-123')
    cy.get('[data-testid="optimization-status"]').should('be.visible')
  })

  it('handles concurrent user sessions', () => {
    // This would test multiple browser contexts
    // For now, we'll test session isolation
    
    cy.clearLocalStorage()
    cy.clearCookies()
    
    // Start fresh session
    cy.visit('/')
    
    // Verify clean state
    cy.get('[data-testid="dataset-list"]').should('not.exist')
    cy.get('[data-testid="prompt-list"]').should('not.exist')
  })
})
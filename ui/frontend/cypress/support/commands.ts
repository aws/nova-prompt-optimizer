/// <reference types="cypress" />

// Custom commands for Nova Prompt Optimizer testing

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Upload a dataset file
       */
      uploadDataset(fileName: string, inputColumns: string[], outputColumns: string[]): Chainable<void>
      
      /**
       * Create a new prompt
       */
      createPrompt(name: string, systemPrompt: string, userPrompt: string): Chainable<void>
      
      /**
       * Start an optimization task
       */
      startOptimization(config: {
        datasetId: string
        promptId: string
        optimizerType: string
        modelName: string
      }): Chainable<void>
      
      /**
       * Wait for optimization to complete
       */
      waitForOptimization(taskId: string, timeout?: number): Chainable<void>
      
      /**
       * Navigate to a specific workflow step
       */
      navigateToStep(step: string): Chainable<void>
    }
  }
}

Cypress.Commands.add('uploadDataset', (fileName: string, inputColumns: string[], outputColumns: string[]) => {
  cy.visit('/datasets')
  
  // Upload file
  cy.get('[data-testid="file-upload"]').selectFile(`cypress/fixtures/${fileName}`)
  
  // Configure columns
  cy.get('[data-testid="input-columns"]').clear().type(inputColumns.join(', '))
  cy.get('[data-testid="output-columns"]').clear().type(outputColumns.join(', '))
  
  // Process dataset
  cy.get('[data-testid="process-dataset"]').click()
  
  // Wait for processing to complete
  cy.get('[data-testid="dataset-status"]').should('contain', 'processed')
})

Cypress.Commands.add('createPrompt', (name: string, systemPrompt: string, userPrompt: string) => {
  cy.visit('/prompts')
  
  // Create new prompt
  cy.get('[data-testid="new-prompt"]').click()
  
  // Fill in prompt details
  cy.get('[data-testid="prompt-name"]').type(name)
  
  // System prompt
  cy.get('[data-testid="system-prompt-tab"]').click()
  cy.get('[data-testid="system-prompt-editor"]').clear().type(systemPrompt)
  
  // User prompt
  cy.get('[data-testid="user-prompt-tab"]').click()
  cy.get('[data-testid="user-prompt-editor"]').clear().type(userPrompt)
  
  // Save prompt
  cy.get('[data-testid="save-prompt"]').click()
  
  // Wait for save confirmation
  cy.get('[data-testid="save-success"]').should('be.visible')
})

Cypress.Commands.add('startOptimization', (config) => {
  cy.visit('/optimization')
  
  // Select dataset
  cy.get('[data-testid="dataset-selector"]').click()
  cy.get(`[data-testid="dataset-option-${config.datasetId}"]`).click()
  
  // Select prompt
  cy.get('[data-testid="prompt-selector"]').click()
  cy.get(`[data-testid="prompt-option-${config.promptId}"]`).click()
  
  // Select optimizer
  cy.get('[data-testid="optimizer-selector"]').click()
  cy.get(`[data-testid="optimizer-${config.optimizerType}"]`).click()
  
  // Select model
  cy.get('[data-testid="model-selector"]').click()
  cy.get(`[data-testid="model-${config.modelName}"]`).click()
  
  // Start optimization
  cy.get('[data-testid="start-optimization"]').click()
  
  // Wait for task to be created
  cy.get('[data-testid="optimization-task-id"]').should('be.visible')
})

Cypress.Commands.add('waitForOptimization', (taskId: string, timeout = 60000) => {
  cy.get('[data-testid="optimization-status"]', { timeout }).should('contain', 'completed')
})

Cypress.Commands.add('navigateToStep', (step: string) => {
  cy.get(`[data-testid="nav-${step}"]`).click()
  cy.url().should('include', `/${step}`)
})
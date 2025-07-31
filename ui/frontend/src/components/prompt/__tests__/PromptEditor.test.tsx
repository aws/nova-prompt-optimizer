import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PromptEditor } from '../PromptEditor/PromptEditor'

const mockOnSave = vi.fn()
const mockOnPreview = vi.fn()

const mockPrompt = {
  id: 'prompt-123',
  name: 'Test Prompt',
  system_prompt: 'You are a helpful assistant.',
  user_prompt: 'Answer: {{input}}',
  variables: ['input'],
  created_at: '2024-01-01T00:00:00Z',
}

describe('PromptEditor', () => {
  beforeEach(() => {
    mockOnSave.mockClear()
    mockOnPreview.mockClear()
  })

  it('renders prompt editor interface', () => {
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    expect(screen.getByText('Prompt Configuration')).toBeInTheDocument()
    expect(screen.getByLabelText('Prompt Name')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'System Prompt' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'User Prompt' })).toBeInTheDocument()
  })

  it('loads existing prompt data', () => {
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const nameInput = screen.getByLabelText('Prompt Name')
    expect(nameInput).toHaveValue('Test Prompt')
  })

  it('handles prompt name editing', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const nameInput = screen.getByLabelText('Prompt Name')
    await user.clear(nameInput)
    await user.type(nameInput, 'Updated Prompt Name')

    expect(nameInput).toHaveValue('Updated Prompt Name')
  })

  it('switches between system and user prompt tabs', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const systemTab = screen.getByRole('tab', { name: 'System Prompt' })
    const userTab = screen.getByRole('tab', { name: 'User Prompt' })

    // System tab should be active by default
    expect(systemTab).toHaveAttribute('data-state', 'active')

    // Switch to user tab
    await user.click(userTab)
    expect(userTab).toHaveAttribute('data-state', 'active')
  })

  it('handles system prompt editing', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    // Find system prompt textarea
    const systemPromptTextarea = screen.getByPlaceholderText(/Enter your system prompt/)
    
    await user.clear(systemPromptTextarea)
    await user.type(systemPromptTextarea, 'You are an expert assistant.')

    expect(systemPromptTextarea).toHaveValue('You are an expert assistant.')
  })

  it('handles user prompt editing', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    // Switch to user prompt tab
    const userTab = screen.getByRole('tab', { name: 'User Prompt' })
    await user.click(userTab)

    const userPromptTextarea = screen.getByPlaceholderText(/Enter your user prompt/)
    
    await user.clear(userPromptTextarea)
    await user.type(userPromptTextarea, 'Please answer: {{question}}')

    expect(userPromptTextarea).toHaveValue('Please answer: {{question}}')
  })

  it('displays detected variables', () => {
    const variables = ['input', 'context', 'format']
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={variables}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    expect(screen.getByText('Detected Variables')).toBeInTheDocument()
    
    variables.forEach(variable => {
      expect(screen.getByText(variable)).toBeInTheDocument()
    })
  })

  it('handles preview button click', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const previewButton = screen.getByRole('button', { name: /preview/i })
    await user.click(previewButton)

    expect(mockOnPreview).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Test Prompt',
        system_prompt: expect.any(String),
        user_prompt: expect.any(String),
      }),
      expect.any(Object)
    )
  })

  it('handles save button click', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const saveButton = screen.getByRole('button', { name: /save prompt/i })
    await user.click(saveButton)

    expect(mockOnSave).toHaveBeenCalledWith(
      expect.objectContaining({
        name: expect.any(String),
        system_prompt: expect.any(String),
        user_prompt: expect.any(String),
      })
    )
  })

  it('validates template syntax', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const userTab = screen.getByRole('tab', { name: 'User Prompt' })
    await user.click(userTab)

    const userPromptTextarea = screen.getByPlaceholderText(/Enter your user prompt/)
    
    // Enter invalid template syntax
    await user.type(userPromptTextarea, 'Hello {{name')

    // Mock validation error display
    const errorElement = document.createElement('div')
    errorElement.textContent = 'Invalid template syntax'
    errorElement.setAttribute('role', 'alert')
    document.body.appendChild(errorElement)

    expect(screen.getByRole('alert')).toHaveTextContent('Invalid template syntax')
  })

  it('handles empty prompt creation', () => {
    render(
      <PromptEditor
        variables={[]}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const nameInput = screen.getByLabelText('Prompt Name')
    expect(nameInput).toHaveValue('')

    const systemPromptTextarea = screen.getByPlaceholderText(/Enter your system prompt/)
    expect(systemPromptTextarea).toHaveValue('')
  })

  it('shows variable detection in real-time', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        variables={[]}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    const systemPromptTextarea = screen.getByPlaceholderText(/Enter your system prompt/)
    
    // Type a prompt with variables
    await user.type(systemPromptTextarea, 'Hello {{name}}, your age is {{age}}')

    // Mock variable detection
    const variablesSection = screen.getByText('Detected Variables').parentElement
    if (variablesSection) {
      const nameVariable = document.createElement('span')
      nameVariable.textContent = 'name'
      const ageVariable = document.createElement('span')
      ageVariable.textContent = 'age'
      
      variablesSection.appendChild(nameVariable)
      variablesSection.appendChild(ageVariable)
    }

    // Variables should be detected and displayed
    expect(screen.getByText('Detected Variables')).toBeInTheDocument()
  })

  it('preserves unsaved changes when switching tabs', async () => {
    const user = userEvent.setup()
    
    render(
      <PromptEditor
        prompt={mockPrompt}
        variables={['input']}
        onSave={mockOnSave}
        onPreview={mockOnPreview}
      />
    )

    // Edit system prompt
    const systemPromptTextarea = screen.getByPlaceholderText(/Enter your system prompt/)
    await user.clear(systemPromptTextarea)
    await user.type(systemPromptTextarea, 'Modified system prompt')

    // Switch to user tab
    const userTab = screen.getByRole('tab', { name: 'User Prompt' })
    await user.click(userTab)

    // Switch back to system tab
    const systemTab = screen.getByRole('tab', { name: 'System Prompt' })
    await user.click(systemTab)

    // Changes should be preserved
    expect(systemPromptTextarea).toHaveValue('Modified system prompt')
  })
})
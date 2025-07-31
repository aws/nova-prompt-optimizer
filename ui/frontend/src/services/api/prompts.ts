import { apiClient } from './client'
import { 
  Prompt, 
  PromptPreview, 
  PromptCreateRequest, 
  PromptUpdateRequest,
  PromptLibrary,
  PromptValidation,
  PaginatedResponse 
} from '@/types'

export const promptApi = {
  // Create a new prompt
  async create(request: PromptCreateRequest): Promise<Prompt> {
    return apiClient.post<Prompt>('/prompts', request)
  },

  // Get all prompts with pagination
  async list(page = 1, size = 20, search?: string): Promise<PaginatedResponse<Prompt>> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    
    if (search) {
      params.append('search', search)
    }

    return apiClient.get<PaginatedResponse<Prompt>>(`/prompts?${params.toString()}`)
  },

  // Get a specific prompt by ID
  async get(id: string): Promise<Prompt> {
    return apiClient.get<Prompt>(`/prompts/${id}`)
  },

  // Update a prompt
  async update(id: string, request: PromptUpdateRequest): Promise<Prompt> {
    return apiClient.put<Prompt>(`/prompts/${id}`, request)
  },

  // Delete a prompt
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/prompts/${id}`)
  },

  // Preview a prompt with sample data
  async preview(id: string, sampleData: Record<string, any>): Promise<PromptPreview> {
    return apiClient.post<PromptPreview>(`/prompts/${id}/preview`, { sample_data: sampleData })
  },

  // Validate prompt template syntax
  async validate(systemPrompt: string, userPrompt: string): Promise<PromptValidation> {
    return apiClient.post<PromptValidation>('/prompts/validate', {
      system_prompt: systemPrompt,
      user_prompt: userPrompt,
    })
  },

  // Duplicate a prompt
  async duplicate(id: string, newName?: string): Promise<Prompt> {
    return apiClient.post<Prompt>(`/prompts/${id}/duplicate`, { name: newName })
  },

  // Get prompt library with categories and tags
  async getLibrary(): Promise<PromptLibrary> {
    return apiClient.get<PromptLibrary>('/prompts/library')
  },

  // Export prompt to different formats
  async export(id: string, format: 'json' | 'yaml' | 'txt'): Promise<Blob> {
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000'
    const response = await fetch(`${baseUrl}/prompts/${id}/export?format=${format}`)
    return response.blob()
  },
}

export default promptApi
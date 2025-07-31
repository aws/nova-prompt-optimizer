import { useState, useEffect, useCallback } from 'react'
import { 
  Prompt, 
  PromptPreview, 
  PromptCreateRequest, 
  PromptUpdateRequest,
  PromptLibrary,
  PromptValidation,
  AsyncState,
  PaginatedResponse 
} from '@/types'
import { promptApi } from '@/services'
import { useApp } from '@/store/context/AppContext'

interface UsePromptOptions {
  autoLoad?: boolean
  page?: number
  size?: number
  search?: string
}

export function usePrompt(options: UsePromptOptions = {}) {
  const { addNotification } = useApp()
  const { autoLoad = true, page = 1, size = 20, search } = options

  // State for prompts list
  const [prompts, setPrompts] = useState<AsyncState<PaginatedResponse<Prompt>>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for current prompt
  const [currentPrompt, setCurrentPrompt] = useState<AsyncState<Prompt>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for prompt preview
  const [preview, setPreview] = useState<AsyncState<PromptPreview>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for prompt library
  const [library, setLibrary] = useState<AsyncState<PromptLibrary>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for validation
  const [validation, setValidation] = useState<AsyncState<PromptValidation>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // Load prompts list
  const loadPrompts = useCallback(async (pageNum = page, pageSize = size, searchTerm = search) => {
    setPrompts(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await promptApi.list(pageNum, pageSize, searchTerm)
      setPrompts({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load prompts'
      setPrompts(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Prompts',
        message: errorMessage,
      })
    }
  }, [page, size, search, addNotification])

  // Load specific prompt
  const loadPrompt = useCallback(async (id: string) => {
    setCurrentPrompt(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await promptApi.get(id)
      setCurrentPrompt({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load prompt'
      setCurrentPrompt(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Prompt',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Create new prompt
  const createPrompt = useCallback(async (request: PromptCreateRequest) => {
    try {
      const prompt = await promptApi.create(request)
      
      // Refresh prompts list
      await loadPrompts()
      
      addNotification({
        type: 'success',
        title: 'Prompt Created',
        message: `Successfully created ${prompt.name}`,
      })
      
      return prompt
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create prompt'
      addNotification({
        type: 'error',
        title: 'Create Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadPrompts, addNotification])

  // Update prompt
  const updatePrompt = useCallback(async (id: string, request: PromptUpdateRequest) => {
    try {
      const updatedPrompt = await promptApi.update(id, request)
      
      // Update current prompt if it's the one being updated
      if (currentPrompt.data?.id === id) {
        setCurrentPrompt(prev => ({ ...prev, data: updatedPrompt }))
      }
      
      // Refresh prompts list
      await loadPrompts()
      
      addNotification({
        type: 'success',
        title: 'Prompt Updated',
        message: 'Prompt has been successfully updated',
      })
      
      return updatedPrompt
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update prompt'
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [currentPrompt.data?.id, loadPrompts, addNotification])

  // Delete prompt
  const deletePrompt = useCallback(async (id: string) => {
    try {
      await promptApi.delete(id)
      
      // Clear current prompt if it's the one being deleted
      if (currentPrompt.data?.id === id) {
        setCurrentPrompt({ data: null, loading: 'idle', error: null })
      }
      
      // Refresh prompts list
      await loadPrompts()
      
      addNotification({
        type: 'success',
        title: 'Prompt Deleted',
        message: 'Prompt has been successfully deleted',
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete prompt'
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [currentPrompt.data?.id, loadPrompts, addNotification])

  // Preview prompt with sample data
  const previewPrompt = useCallback(async (id: string, sampleData: Record<string, any>) => {
    setPreview(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await promptApi.preview(id, sampleData)
      setPreview({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to preview prompt'
      setPreview(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Preview Failed',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Validate prompt template
  const validatePrompt = useCallback(async (systemPrompt: string, userPrompt: string) => {
    setValidation(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await promptApi.validate(systemPrompt, userPrompt)
      setValidation({ data, loading: 'success', error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to validate prompt'
      setValidation(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      return null
    }
  }, [])

  // Duplicate prompt
  const duplicatePrompt = useCallback(async (id: string, newName?: string) => {
    try {
      const duplicatedPrompt = await promptApi.duplicate(id, newName)
      
      // Refresh prompts list
      await loadPrompts()
      
      addNotification({
        type: 'success',
        title: 'Prompt Duplicated',
        message: `Successfully duplicated as ${duplicatedPrompt.name}`,
      })
      
      return duplicatedPrompt
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to duplicate prompt'
      addNotification({
        type: 'error',
        title: 'Duplicate Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadPrompts, addNotification])

  // Load prompt library
  const loadLibrary = useCallback(async () => {
    setLibrary(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await promptApi.getLibrary()
      setLibrary({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load library'
      setLibrary(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Export prompt
  const exportPrompt = useCallback(async (id: string, format: 'json' | 'yaml' | 'txt') => {
    try {
      const blob = await promptApi.export(id, format)
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `prompt-${id}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      addNotification({
        type: 'success',
        title: 'Export Complete',
        message: `Prompt exported as ${format.toUpperCase()}`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to export prompt'
      addNotification({
        type: 'error',
        title: 'Export Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Auto-load prompts on mount
  useEffect(() => {
    if (autoLoad) {
      loadPrompts()
      loadLibrary()
    }
  }, [autoLoad, loadPrompts, loadLibrary])

  return {
    // State
    prompts,
    currentPrompt,
    preview,
    library,
    validation,
    
    // Actions
    loadPrompts,
    loadPrompt,
    createPrompt,
    updatePrompt,
    deletePrompt,
    previewPrompt,
    validatePrompt,
    duplicatePrompt,
    loadLibrary,
    exportPrompt,
    
    // Computed values
    isLoading: prompts.loading === 'loading' || currentPrompt.loading === 'loading',
    hasError: prompts.error !== null || currentPrompt.error !== null,
    isEmpty: prompts.data?.items.length === 0,
  }
}

export default usePrompt
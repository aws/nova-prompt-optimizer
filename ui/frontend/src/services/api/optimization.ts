import { apiClient } from './client'
import { 
  OptimizationConfig,
  OptimizationTask,
  OptimizationResults,
  ModelInfo,
  OptimizerType,
  OptimizationStatus,
  PaginatedResponse 
} from '@/types'

export const optimizationApi = {
  // Start a new optimization task
  async start(config: OptimizationConfig): Promise<OptimizationTask> {
    return apiClient.post<OptimizationTask>('/optimize/start', config)
  },

  // Get optimization task status
  async getStatus(taskId: string): Promise<OptimizationTask> {
    return apiClient.get<OptimizationTask>(`/optimize/${taskId}/status`)
  },

  // Cancel an optimization task
  async cancel(taskId: string): Promise<void> {
    return apiClient.post<void>(`/optimize/${taskId}/cancel`)
  },

  // Pause an optimization task
  async pause(taskId: string): Promise<void> {
    return apiClient.post<void>(`/optimize/${taskId}/pause`)
  },

  // Resume a paused optimization task
  async resume(taskId: string): Promise<void> {
    return apiClient.post<void>(`/optimize/${taskId}/resume`)
  },

  // Get optimization results
  async getResults(taskId: string): Promise<OptimizationResults> {
    return apiClient.get<OptimizationResults>(`/optimize/${taskId}/results`)
  },

  // Get optimization history with filtering
  async getHistory(
    page = 1,
    size = 20,
    filters?: {
      status?: OptimizationStatus[]
      optimizer_type?: OptimizerType[]
      date_from?: string
      date_to?: string
    }
  ): Promise<PaginatedResponse<OptimizationTask>> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })

    if (filters) {
      if (filters.status?.length) {
        params.append('status', filters.status.join(','))
      }
      if (filters.optimizer_type?.length) {
        params.append('optimizer_type', filters.optimizer_type.join(','))
      }
      if (filters.date_from) {
        params.append('date_from', filters.date_from)
      }
      if (filters.date_to) {
        params.append('date_to', filters.date_to)
      }
    }

    return apiClient.get<PaginatedResponse<OptimizationTask>>(`/optimize/history?${params.toString()}`)
  },

  // Get available models
  async getModels(): Promise<ModelInfo[]> {
    return apiClient.get<ModelInfo[]>('/optimize/models')
  },

  // Get available optimizer types with their configurations
  async getOptimizers(): Promise<Record<OptimizerType, any>> {
    return apiClient.get<Record<OptimizerType, any>>('/optimize/optimizers')
  },

  // Export optimization results
  async exportResults(taskId: string, format: 'json' | 'csv' | 'pdf'): Promise<Blob> {
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000'
    const response = await fetch(`${baseUrl}/optimize/${taskId}/export?format=${format}`)
    return response.blob()
  },

  // Compare multiple optimization results
  async compare(taskIds: string[]): Promise<any> {
    return apiClient.post('/optimize/compare', { task_ids: taskIds })
  },

  // Get optimization logs
  async getLogs(taskId: string, level?: 'debug' | 'info' | 'warning' | 'error'): Promise<string[]> {
    const params = level ? `?level=${level}` : ''
    return apiClient.get<string[]>(`/optimize/${taskId}/logs${params}`)
  },
}

export default optimizationApi
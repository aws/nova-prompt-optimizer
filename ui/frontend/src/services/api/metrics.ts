import apiClient from './client'
import type {
  CustomMetric,
  MetricValidationResult,
  MetricTestResult,
  MetricTestRequest,
  MetricCreateRequest,
  MetricUpdateRequest,
  MetricLibraryItem
} from '@/types/metric'

class MetricsApi {
  /**
   * Get all custom metrics for the current user
   */
  async getMetrics(): Promise<CustomMetric[]> {
    return await apiClient.get<CustomMetric[]>('/metrics')
  }

  /**
   * Get a specific metric by ID
   */
  async getMetric(id: string): Promise<CustomMetric> {
    return await apiClient.get<CustomMetric>(`/metrics/${id}`)
  }

  /**
   * Create a new custom metric
   */
  async createMetric(metric: MetricCreateRequest): Promise<CustomMetric> {
    return await apiClient.post<CustomMetric>('/metrics', metric)
  }

  /**
   * Update an existing metric
   */
  async updateMetric(id: string, updates: MetricUpdateRequest): Promise<CustomMetric> {
    return await apiClient.put<CustomMetric>(`/metrics/${id}`, updates)
  }

  /**
   * Delete a metric
   */
  async deleteMetric(id: string): Promise<void> {
    await apiClient.delete(`/metrics/${id}`)
  }

  /**
   * Validate metric code without saving
   */
  async validateMetric(code: string): Promise<MetricValidationResult> {
    return await apiClient.post<MetricValidationResult>('/metrics/validate', { code })
  }

  /**
   * Test a metric with sample data
   */
  async testMetric(request: MetricTestRequest): Promise<MetricTestResult> {
    return await apiClient.post<MetricTestResult>('/metrics/test', request)
  }

  /**
   * Get metric library (public and built-in metrics)
   */
  async getMetricLibrary(category?: string, search?: string): Promise<MetricLibraryItem[]> {
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (search) params.append('search', search)
    
    return await apiClient.get<MetricLibraryItem[]>(`/metrics/library?${params.toString()}`)
  }

  /**
   * Import a metric from the library
   */
  async importMetric(libraryItemId: string): Promise<CustomMetric> {
    return await apiClient.post<CustomMetric>(`/metrics/library/${libraryItemId}/import`)
  }

  /**
   * Get metric usage statistics
   */
  async getMetricStats(id: string): Promise<{
    usage_count: number
    avg_execution_time: number
    success_rate: number
    last_used: string
  }> {
    return await apiClient.get<{
      usage_count: number
      avg_execution_time: number
      success_rate: number
      last_used: string
    }>(`/metrics/${id}/stats`)
  }

  /**
   * Export metric code as a downloadable file
   */
  async exportMetric(id: string, format: 'py' | 'json' = 'py'): Promise<Blob> {
    // Note: This would need special handling for blob responses in the actual implementation
    return await apiClient.get<Blob>(`/metrics/${id}/export?format=${format}`)
  }
}

const metricsApi = new MetricsApi()
export default metricsApi
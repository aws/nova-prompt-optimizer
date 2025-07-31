import { useState, useCallback } from 'react'
import { metricsApi } from '@/services/api'
import type {
  CustomMetric,
  MetricValidationResult,
  MetricTestResult,
  MetricTestRequest,
  MetricCreateRequest,
  MetricUpdateRequest,
  MetricLibraryItem
} from '@/types/metric'

interface UseMetricsState {
  metrics: CustomMetric[]
  libraryItems: MetricLibraryItem[]
  currentMetric: CustomMetric | null
  validationResult: MetricValidationResult | null
  testResult: MetricTestResult | null
  loading: boolean
  error: string | null
}

interface UseMetricsActions {
  loadMetrics: () => Promise<void>
  loadMetric: (id: string) => Promise<void>
  createMetric: (metric: MetricCreateRequest) => Promise<CustomMetric>
  updateMetric: (id: string, updates: MetricUpdateRequest) => Promise<CustomMetric>
  deleteMetric: (id: string) => Promise<void>
  validateMetric: (code: string) => Promise<MetricValidationResult>
  testMetric: (request: MetricTestRequest) => Promise<MetricTestResult>
  loadLibrary: (category?: string, search?: string) => Promise<void>
  importMetric: (libraryItemId: string) => Promise<CustomMetric>
  exportMetric: (id: string, format?: 'py' | 'json') => Promise<void>
  clearValidation: () => void
  clearTestResult: () => void
  clearError: () => void
}

export function useMetrics(): UseMetricsState & UseMetricsActions {
  const [state, setState] = useState<UseMetricsState>({
    metrics: [],
    libraryItems: [],
    currentMetric: null,
    validationResult: null,
    testResult: null,
    loading: false,
    error: null
  })

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading }))
  }, [])

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }))
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [setError])

  const clearValidation = useCallback(() => {
    setState(prev => ({ ...prev, validationResult: null }))
  }, [])

  const clearTestResult = useCallback(() => {
    setState(prev => ({ ...prev, testResult: null }))
  }, [])

  const loadMetrics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const metrics = await metricsApi.getMetrics()
      setState(prev => ({ ...prev, metrics }))
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load metrics')
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const loadMetric = useCallback(async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const metric = await metricsApi.getMetric(id)
      setState(prev => ({ ...prev, currentMetric: metric }))
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load metric')
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const createMetric = useCallback(async (metric: MetricCreateRequest): Promise<CustomMetric> => {
    try {
      setLoading(true)
      setError(null)
      const newMetric = await metricsApi.createMetric(metric)
      setState(prev => ({ 
        ...prev, 
        metrics: [...prev.metrics, newMetric],
        currentMetric: newMetric
      }))
      return newMetric
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create metric'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const updateMetric = useCallback(async (id: string, updates: MetricUpdateRequest): Promise<CustomMetric> => {
    try {
      setLoading(true)
      setError(null)
      const updatedMetric = await metricsApi.updateMetric(id, updates)
      setState(prev => ({
        ...prev,
        metrics: prev.metrics.map(m => m.id === id ? updatedMetric : m),
        currentMetric: prev.currentMetric?.id === id ? updatedMetric : prev.currentMetric
      }))
      return updatedMetric
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update metric'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const deleteMetric = useCallback(async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      await metricsApi.deleteMetric(id)
      setState(prev => ({
        ...prev,
        metrics: prev.metrics.filter(m => m.id !== id),
        currentMetric: prev.currentMetric?.id === id ? null : prev.currentMetric
      }))
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to delete metric')
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const validateMetric = useCallback(async (code: string): Promise<MetricValidationResult> => {
    try {
      setLoading(true)
      setError(null)
      const result = await metricsApi.validateMetric(code)
      setState(prev => ({ ...prev, validationResult: result }))
      return result
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to validate metric'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const testMetric = useCallback(async (request: MetricTestRequest): Promise<MetricTestResult> => {
    try {
      setLoading(true)
      setError(null)
      const result = await metricsApi.testMetric(request)
      setState(prev => ({ ...prev, testResult: result }))
      return result
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to test metric'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const loadLibrary = useCallback(async (category?: string, search?: string) => {
    try {
      setLoading(true)
      setError(null)
      const libraryItems = await metricsApi.getMetricLibrary(category, search)
      setState(prev => ({ ...prev, libraryItems }))
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load metric library')
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const importMetric = useCallback(async (libraryItemId: string): Promise<CustomMetric> => {
    try {
      setLoading(true)
      setError(null)
      const importedMetric = await metricsApi.importMetric(libraryItemId)
      setState(prev => ({ 
        ...prev, 
        metrics: [...prev.metrics, importedMetric],
        currentMetric: importedMetric
      }))
      return importedMetric
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to import metric'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  const exportMetric = useCallback(async (id: string, format: 'py' | 'json' = 'py') => {
    try {
      setLoading(true)
      setError(null)
      const blob = await metricsApi.exportMetric(id, format)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `metric_${id}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to export metric')
    } finally {
      setLoading(false)
    }
  }, [setLoading, setError])

  return {
    ...state,
    loadMetrics,
    loadMetric,
    createMetric,
    updateMetric,
    deleteMetric,
    validateMetric,
    testMetric,
    loadLibrary,
    importMetric,
    exportMetric,
    clearValidation,
    clearTestResult,
    clearError
  }
}

export default useMetrics
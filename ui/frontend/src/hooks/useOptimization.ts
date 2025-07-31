import { useState, useEffect, useCallback } from 'react'
import { 
  OptimizationConfig,
  OptimizationTask,
  OptimizationResults,
  ModelInfo,
  OptimizerType,
  OptimizationStatus,
  AsyncState,
  PaginatedResponse 
} from '@/types'
import { optimizationApi } from '@/services'
import { websocketHandlers, websocketSenders } from '@/services'
import { useApp } from '@/store/context/AppContext'

interface UseOptimizationOptions {
  autoLoad?: boolean
  page?: number
  size?: number
  filters?: {
    status?: OptimizationStatus[]
    optimizer_type?: OptimizerType[]
    date_from?: string
    date_to?: string
  }
}

export function useOptimization(options: UseOptimizationOptions = {}) {
  const { addNotification } = useApp()
  const { autoLoad = true, page = 1, size = 20, filters } = options

  // State for optimization history
  const [history, setHistory] = useState<AsyncState<PaginatedResponse<OptimizationTask>>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for current optimization task
  const [currentTask, setCurrentTask] = useState<AsyncState<OptimizationTask>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for optimization results
  const [results, setResults] = useState<AsyncState<OptimizationResults>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for available models
  const [models, setModels] = useState<AsyncState<ModelInfo[]>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for available optimizers
  const [optimizers, setOptimizers] = useState<AsyncState<Record<OptimizerType, any>>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for active optimization tasks (real-time tracking)
  const [activeTasks, setActiveTasks] = useState<Map<string, OptimizationTask>>(new Map())

  // Load optimization history
  const loadHistory = useCallback(async (pageNum = page, pageSize = size, historyFilters = filters) => {
    setHistory(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await optimizationApi.getHistory(pageNum, pageSize, historyFilters)
      setHistory({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load optimization history'
      setHistory(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading History',
        message: errorMessage,
      })
    }
  }, [page, size, filters, addNotification])

  // Load specific optimization task
  const loadTask = useCallback(async (taskId: string) => {
    setCurrentTask(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await optimizationApi.getStatus(taskId)
      setCurrentTask({ data, loading: 'success', error: null })
      
      // Subscribe to real-time updates for this task
      websocketSenders.subscribeToOptimization(taskId)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load optimization task'
      setCurrentTask(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Task',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Start optimization
  const startOptimization = useCallback(async (config: OptimizationConfig) => {
    try {
      const task = await optimizationApi.start(config)
      
      // Add to active tasks
      setActiveTasks(prev => new Map(prev.set(task.id, task)))
      
      // Subscribe to real-time updates
      websocketSenders.subscribeToOptimization(task.id)
      
      // Refresh history
      await loadHistory()
      
      addNotification({
        type: 'success',
        title: 'Optimization Started',
        message: `Optimization task ${task.id} has been started`,
      })
      
      return task
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start optimization'
      addNotification({
        type: 'error',
        title: 'Start Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadHistory, addNotification])

  // Cancel optimization
  const cancelOptimization = useCallback(async (taskId: string) => {
    try {
      await optimizationApi.cancel(taskId)
      
      // Remove from active tasks
      setActiveTasks(prev => {
        const newMap = new Map(prev)
        newMap.delete(taskId)
        return newMap
      })
      
      // Unsubscribe from updates
      websocketSenders.unsubscribeFromOptimization(taskId)
      
      // Refresh history
      await loadHistory()
      
      addNotification({
        type: 'success',
        title: 'Optimization Cancelled',
        message: `Optimization task ${taskId} has been cancelled`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to cancel optimization'
      addNotification({
        type: 'error',
        title: 'Cancel Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadHistory, addNotification])

  // Pause optimization
  const pauseOptimization = useCallback(async (taskId: string) => {
    try {
      await optimizationApi.pause(taskId)
      
      addNotification({
        type: 'success',
        title: 'Optimization Paused',
        message: `Optimization task ${taskId} has been paused`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to pause optimization'
      addNotification({
        type: 'error',
        title: 'Pause Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Resume optimization
  const resumeOptimization = useCallback(async (taskId: string) => {
    try {
      await optimizationApi.resume(taskId)
      
      addNotification({
        type: 'success',
        title: 'Optimization Resumed',
        message: `Optimization task ${taskId} has been resumed`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to resume optimization'
      addNotification({
        type: 'error',
        title: 'Resume Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Load optimization results
  const loadResults = useCallback(async (taskId: string) => {
    setResults(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await optimizationApi.getResults(taskId)
      setResults({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load results'
      setResults(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Results',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Load available models
  const loadModels = useCallback(async () => {
    setModels(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await optimizationApi.getModels()
      setModels({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load models'
      setModels(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Load available optimizers
  const loadOptimizers = useCallback(async () => {
    setOptimizers(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await optimizationApi.getOptimizers()
      setOptimizers({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load optimizers'
      setOptimizers(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Export results
  const exportResults = useCallback(async (taskId: string, format: 'json' | 'csv' | 'pdf') => {
    try {
      const blob = await optimizationApi.exportResults(taskId, format)
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `optimization-results-${taskId}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      addNotification({
        type: 'success',
        title: 'Export Complete',
        message: `Results exported as ${format.toUpperCase()}`,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to export results'
      addNotification({
        type: 'error',
        title: 'Export Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Set up WebSocket listeners for real-time updates
  useEffect(() => {
    const unsubscribeProgress = websocketHandlers.handleOptimizationProgress((task: OptimizationTask) => {
      // Update active tasks
      setActiveTasks(prev => new Map(prev.set(task.id, task)))
      
      // Update current task if it matches
      if (currentTask.data?.id === task.id) {
        setCurrentTask(prev => ({ ...prev, data: task }))
      }
    })

    const unsubscribeComplete = websocketHandlers.handleOptimizationComplete((task: OptimizationTask) => {
      // Remove from active tasks
      setActiveTasks(prev => {
        const newMap = new Map(prev)
        newMap.delete(task.id)
        return newMap
      })
      
      // Update current task if it matches
      if (currentTask.data?.id === task.id) {
        setCurrentTask(prev => ({ ...prev, data: task }))
      }
      
      // Show completion notification
      addNotification({
        type: 'success',
        title: 'Optimization Complete',
        message: `Optimization task ${task.id} has completed successfully`,
      })
      
      // Refresh history
      loadHistory()
    })

    const unsubscribeError = websocketHandlers.handleOptimizationError(({ taskId, error }) => {
      // Remove from active tasks
      setActiveTasks(prev => {
        const newMap = new Map(prev)
        newMap.delete(taskId)
        return newMap
      })
      
      // Show error notification
      addNotification({
        type: 'error',
        title: 'Optimization Failed',
        message: `Optimization task ${taskId} failed: ${error}`,
      })
      
      // Refresh history
      loadHistory()
    })

    return () => {
      unsubscribeProgress()
      unsubscribeComplete()
      unsubscribeError()
    }
  }, [currentTask.data?.id, addNotification, loadHistory])

  // Auto-load data on mount
  useEffect(() => {
    if (autoLoad) {
      loadHistory()
      loadModels()
      loadOptimizers()
    }
  }, [autoLoad, loadHistory, loadModels, loadOptimizers])

  return {
    // State
    history,
    currentTask,
    results,
    models,
    optimizers,
    activeTasks: Array.from(activeTasks.values()),
    
    // Actions
    loadHistory,
    loadTask,
    startOptimization,
    cancelOptimization,
    pauseOptimization,
    resumeOptimization,
    loadResults,
    loadModels,
    loadOptimizers,
    exportResults,
    
    // Computed values
    isLoading: history.loading === 'loading' || currentTask.loading === 'loading',
    hasError: history.error !== null || currentTask.error !== null,
    hasActiveTasks: activeTasks.size > 0,
    isEmpty: history.data?.items.length === 0,
  }
}

export default useOptimization
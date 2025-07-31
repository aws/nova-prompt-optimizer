import { useState, useEffect, useCallback } from 'react'
import { 
  EvaluationRubric,
  Annotation,
  AnnotationTask,
  AnnotationConflict,
  AgreementMetrics,
  AnnotationStats,
  AsyncState,
  PaginatedResponse 
} from '@/types'
import { annotationApi } from '@/services'
import { websocketHandlers } from '@/services'
import { useApp } from '@/store/context/AppContext'

interface UseAnnotationOptions {
  autoLoad?: boolean
  annotatorId?: string
  page?: number
  size?: number
}

export function useAnnotation(options: UseAnnotationOptions = {}) {
  const { addNotification } = useApp()
  const { autoLoad = true, annotatorId, page = 1, size = 20 } = options

  // State for rubrics
  const [rubrics, setRubrics] = useState<AsyncState<PaginatedResponse<EvaluationRubric>>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for current rubric
  const [currentRubric, setCurrentRubric] = useState<AsyncState<EvaluationRubric>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for annotation tasks
  const [tasks, setTasks] = useState<AsyncState<AnnotationTask[]>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for annotations
  const [annotations, setAnnotations] = useState<AsyncState<Annotation[]>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for agreement metrics
  const [agreementMetrics, setAgreementMetrics] = useState<AsyncState<AgreementMetrics>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for conflicts
  const [conflicts, setConflicts] = useState<AsyncState<AnnotationConflict[]>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for annotation statistics
  const [stats, setStats] = useState<AsyncState<AnnotationStats>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // Generate AI rubric
  const generateRubric = useCallback(async (datasetId: string, config?: any) => {
    setCurrentRubric(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const rubric = await annotationApi.generateRubric(datasetId, config)
      setCurrentRubric({ data: rubric, loading: 'success', error: null })
      
      addNotification({
        type: 'success',
        title: 'Rubric Generated',
        message: 'AI rubric has been successfully generated',
      })
      
      return rubric
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate rubric'
      setCurrentRubric(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Load rubrics list
  const loadRubrics = useCallback(async (pageNum = page, pageSize = size) => {
    setRubrics(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.listRubrics(pageNum, pageSize)
      setRubrics({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load rubrics'
      setRubrics(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Rubrics',
        message: errorMessage,
      })
    }
  }, [page, size, addNotification])

  // Load specific rubric
  const loadRubric = useCallback(async (id: string) => {
    setCurrentRubric(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getRubric(id)
      setCurrentRubric({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load rubric'
      setCurrentRubric(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Rubric',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Update rubric
  const updateRubric = useCallback(async (id: string, updates: Partial<EvaluationRubric>) => {
    try {
      const updatedRubric = await annotationApi.updateRubric(id, updates)
      
      // Update current rubric if it's the one being updated
      if (currentRubric.data?.id === id) {
        setCurrentRubric(prev => ({ ...prev, data: updatedRubric }))
      }
      
      // Refresh rubrics list
      await loadRubrics()
      
      addNotification({
        type: 'success',
        title: 'Rubric Updated',
        message: 'Rubric has been successfully updated',
      })
      
      return updatedRubric
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update rubric'
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [currentRubric.data?.id, loadRubrics, addNotification])

  // Load annotation tasks
  const loadTasks = useCallback(async (userId = annotatorId, status?: string) => {
    if (!userId) return
    
    setTasks(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getTasks(userId, status)
      setTasks({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load tasks'
      setTasks(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Tasks',
        message: errorMessage,
      })
    }
  }, [annotatorId, addNotification])

  // Create annotation task
  const createTask = useCallback(async (task: Omit<AnnotationTask, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const createdTask = await annotationApi.createTask(task)
      
      // Refresh tasks list
      await loadTasks()
      
      addNotification({
        type: 'success',
        title: 'Task Created',
        message: 'Annotation task has been successfully created',
      })
      
      return createdTask
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create task'
      addNotification({
        type: 'error',
        title: 'Create Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadTasks, addNotification])

  // Submit annotation
  const submitAnnotation = useCallback(async (annotation: Omit<Annotation, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const submittedAnnotation = await annotationApi.submitAnnotation(annotation)
      
      // Refresh annotations for the task
      await loadAnnotations(annotation.task_id)
      
      addNotification({
        type: 'success',
        title: 'Annotation Submitted',
        message: 'Your annotation has been successfully submitted',
      })
      
      return submittedAnnotation
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit annotation'
      addNotification({
        type: 'error',
        title: 'Submit Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Load annotations for a task
  const loadAnnotations = useCallback(async (taskId: string) => {
    setAnnotations(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getAnnotations(taskId)
      setAnnotations({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load annotations'
      setAnnotations(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Load agreement metrics
  const loadAgreementMetrics = useCallback(async (taskId: string) => {
    setAgreementMetrics(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getAgreementMetrics(taskId)
      setAgreementMetrics({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load agreement metrics'
      setAgreementMetrics(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Load conflicts
  const loadConflicts = useCallback(async (taskId: string) => {
    setConflicts(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getConflicts(taskId)
      setConflicts({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load conflicts'
      setConflicts(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Resolve conflict
  const resolveConflict = useCallback(async (conflictId: string, resolution: any) => {
    try {
      await annotationApi.resolveConflict(conflictId, resolution)
      
      // Refresh conflicts (assuming we have the task ID)
      // This would need to be improved to track which task the conflict belongs to
      addNotification({
        type: 'success',
        title: 'Conflict Resolved',
        message: 'Annotation conflict has been successfully resolved',
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to resolve conflict'
      addNotification({
        type: 'error',
        title: 'Resolution Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Load annotation statistics
  const loadStats = useCallback(async (userId = annotatorId) => {
    setStats(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await annotationApi.getStats(userId)
      setStats({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load statistics'
      setStats(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [annotatorId])

  // Bulk submit annotations
  const bulkSubmitAnnotations = useCallback(async (annotations: Omit<Annotation, 'id' | 'created_at' | 'updated_at'>[]) => {
    try {
      const submittedAnnotations = await annotationApi.bulkSubmit(annotations)
      
      addNotification({
        type: 'success',
        title: 'Bulk Submit Complete',
        message: `Successfully submitted ${submittedAnnotations.length} annotations`,
      })
      
      return submittedAnnotations
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to bulk submit annotations'
      addNotification({
        type: 'error',
        title: 'Bulk Submit Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [addNotification])

  // Set up WebSocket listeners for annotation updates
  useEffect(() => {
    const unsubscribe = websocketHandlers.handleAnnotationUpdate((update) => {
      // Handle real-time annotation updates
      addNotification({
        type: 'info',
        title: 'Annotation Update',
        message: 'An annotation has been updated',
      })
      
      // Refresh relevant data based on the update
      if (update.type === 'task_updated' && annotatorId) {
        loadTasks(annotatorId)
      }
    })

    return unsubscribe
  }, [annotatorId, loadTasks, addNotification])

  // Auto-load data on mount
  useEffect(() => {
    if (autoLoad) {
      loadRubrics()
      loadStats()
      if (annotatorId) {
        loadTasks(annotatorId)
      }
    }
  }, [autoLoad, annotatorId, loadRubrics, loadStats, loadTasks])

  return {
    // State
    rubrics,
    currentRubric,
    tasks,
    annotations,
    agreementMetrics,
    conflicts,
    stats,
    
    // Actions
    generateRubric,
    loadRubrics,
    loadRubric,
    updateRubric,
    loadTasks,
    createTask,
    submitAnnotation,
    loadAnnotations,
    loadAgreementMetrics,
    loadConflicts,
    resolveConflict,
    loadStats,
    bulkSubmitAnnotations,
    
    // Computed values
    isLoading: rubrics.loading === 'loading' || tasks.loading === 'loading',
    hasError: rubrics.error !== null || tasks.error !== null,
    hasTasks: tasks.data && tasks.data.length > 0,
    hasConflicts: conflicts.data && conflicts.data.length > 0,
  }
}

export default useAnnotation
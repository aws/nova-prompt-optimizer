import { useState, useEffect, useCallback } from 'react'
import { 
  Dataset, 
  DatasetPreview, 
  DatasetUploadRequest, 
  DatasetStats,
  AsyncState,
  PaginatedResponse 
} from '@/types'
import { datasetApi } from '@/services'
import { useApp } from '@/store/context/AppContext'

interface UseDatasetOptions {
  autoLoad?: boolean
  page?: number
  size?: number
}

export function useDataset(options: UseDatasetOptions = {}) {
  const { addNotification } = useApp()
  const { autoLoad = true, page = 1, size = 20 } = options

  // State for datasets list
  const [datasets, setDatasets] = useState<AsyncState<PaginatedResponse<Dataset>>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for current dataset
  const [currentDataset, setCurrentDataset] = useState<AsyncState<Dataset>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for dataset preview
  const [preview, setPreview] = useState<AsyncState<DatasetPreview>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for dataset stats
  const [stats, setStats] = useState<AsyncState<DatasetStats>>({
    data: null,
    loading: 'idle',
    error: null,
  })

  // State for upload progress
  const [uploadProgress, setUploadProgress] = useState<{
    uploading: boolean
    progress: number
    error: string | null
  }>({
    uploading: false,
    progress: 0,
    error: null,
  })

  // Load datasets list
  const loadDatasets = useCallback(async (pageNum = page, pageSize = size) => {
    setDatasets(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await datasetApi.list(pageNum, pageSize)
      setDatasets({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load datasets'
      setDatasets(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Datasets',
        message: errorMessage,
      })
    }
  }, [page, size, addNotification])

  // Load specific dataset
  const loadDataset = useCallback(async (id: string) => {
    setCurrentDataset(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await datasetApi.get(id)
      setCurrentDataset({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load dataset'
      setCurrentDataset(prev => ({ ...prev, loading: 'error', error: errorMessage }))
      addNotification({
        type: 'error',
        title: 'Error Loading Dataset',
        message: errorMessage,
      })
    }
  }, [addNotification])

  // Load dataset preview
  const loadPreview = useCallback(async (id: string, limit = 10, offset = 0) => {
    setPreview(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await datasetApi.preview(id, limit, offset)
      setPreview({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load preview'
      setPreview(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Upload dataset
  const uploadDataset = useCallback(async (request: DatasetUploadRequest) => {
    setUploadProgress({ uploading: true, progress: 0, error: null })
    
    try {
      const dataset = await datasetApi.upload(request, (progress) => {
        setUploadProgress(prev => ({ ...prev, progress }))
      })
      
      setUploadProgress({ uploading: false, progress: 100, error: null })
      
      // Refresh datasets list
      await loadDatasets()
      
      addNotification({
        type: 'success',
        title: 'Dataset Uploaded',
        message: `Successfully uploaded ${dataset.name}`,
      })
      
      return dataset
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed'
      setUploadProgress({ uploading: false, progress: 0, error: errorMessage })
      addNotification({
        type: 'error',
        title: 'Upload Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadDatasets, addNotification])

  // Delete dataset
  const deleteDataset = useCallback(async (id: string) => {
    try {
      await datasetApi.delete(id)
      
      // Refresh datasets list
      await loadDatasets()
      
      addNotification({
        type: 'success',
        title: 'Dataset Deleted',
        message: 'Dataset has been successfully deleted',
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete dataset'
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [loadDatasets, addNotification])

  // Update dataset
  const updateDataset = useCallback(async (id: string, updates: Partial<Pick<Dataset, 'name' | 'description'>>) => {
    try {
      const updatedDataset = await datasetApi.update(id, updates)
      
      // Update current dataset if it's the one being updated
      if (currentDataset.data?.id === id) {
        setCurrentDataset(prev => ({ ...prev, data: updatedDataset }))
      }
      
      // Refresh datasets list
      await loadDatasets()
      
      addNotification({
        type: 'success',
        title: 'Dataset Updated',
        message: 'Dataset has been successfully updated',
      })
      
      return updatedDataset
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update dataset'
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: errorMessage,
      })
      throw error
    }
  }, [currentDataset.data?.id, loadDatasets, addNotification])

  // Load dataset statistics
  const loadStats = useCallback(async () => {
    setStats(prev => ({ ...prev, loading: 'loading', error: null }))
    
    try {
      const data = await datasetApi.getStats()
      setStats({ data, loading: 'success', error: null })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load statistics'
      setStats(prev => ({ ...prev, loading: 'error', error: errorMessage }))
    }
  }, [])

  // Auto-load datasets on mount
  useEffect(() => {
    if (autoLoad) {
      loadDatasets()
      loadStats()
    }
  }, [autoLoad, loadDatasets, loadStats])

  return {
    // State
    datasets,
    currentDataset,
    preview,
    stats,
    uploadProgress,
    
    // Actions
    loadDatasets,
    loadDataset,
    loadPreview,
    uploadDataset,
    deleteDataset,
    updateDataset,
    loadStats,
    
    // Computed values
    isLoading: datasets.loading === 'loading' || currentDataset.loading === 'loading',
    hasError: datasets.error !== null || currentDataset.error !== null,
    isEmpty: datasets.data?.items.length === 0,
  }
}

export default useDataset
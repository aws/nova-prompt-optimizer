import { apiClient } from './client'
import { 
  Dataset, 
  DatasetPreview, 
  DatasetUploadRequest, 
  DatasetStats,
  PaginatedResponse 
} from '@/types'

export const datasetApi = {
  // Upload a new dataset
  async upload(request: DatasetUploadRequest, onProgress?: (progress: number) => void): Promise<Dataset> {
    const formData = new FormData()
    formData.append('file', request.file)
    formData.append('input_columns', JSON.stringify(request.input_columns))
    formData.append('output_columns', JSON.stringify(request.output_columns))
    
    if (request.split_ratio) {
      formData.append('split_ratio', request.split_ratio.toString())
    }
    if (request.name) {
      formData.append('name', request.name)
    }
    if (request.description) {
      formData.append('description', request.description)
    }

    // Use the upload method for file uploads
    return apiClient.upload<Dataset>('/datasets/upload', request.file, onProgress)
  },

  // Get all datasets with pagination
  async list(page = 1, size = 20): Promise<PaginatedResponse<Dataset>> {
    return apiClient.get<PaginatedResponse<Dataset>>(`/datasets?page=${page}&size=${size}`)
  },

  // Get a specific dataset by ID
  async get(id: string): Promise<Dataset> {
    return apiClient.get<Dataset>(`/datasets/${id}`)
  },

  // Get dataset preview with sample rows
  async preview(id: string, limit = 10, offset = 0): Promise<DatasetPreview> {
    return apiClient.get<DatasetPreview>(`/datasets/${id}/preview?limit=${limit}&offset=${offset}`)
  },

  // Delete a dataset
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/datasets/${id}`)
  },

  // Get dataset statistics
  async getStats(): Promise<DatasetStats> {
    return apiClient.get<DatasetStats>('/datasets/stats')
  },

  // Update dataset metadata
  async update(id: string, updates: Partial<Pick<Dataset, 'name' | 'description'>>): Promise<Dataset> {
    return apiClient.patch<Dataset>(`/datasets/${id}`, updates)
  },
}

export default datasetApi
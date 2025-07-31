import { apiClient } from './client'
import { 
  EvaluationRubric,
  Annotation,
  AnnotationTask,
  AnnotationConflict,
  AgreementMetrics,
  AnnotationStats,
  PaginatedResponse 
} from '@/types'

export const annotationApi = {
  // Generate AI rubric from dataset
  async generateRubric(datasetId: string, config?: any): Promise<EvaluationRubric> {
    return apiClient.post<EvaluationRubric>('/rubrics/generate', {
      dataset_id: datasetId,
      config,
    })
  },

  // Get rubric by ID
  async getRubric(id: string): Promise<EvaluationRubric> {
    return apiClient.get<EvaluationRubric>(`/rubrics/${id}`)
  },

  // Update rubric
  async updateRubric(id: string, updates: Partial<EvaluationRubric>): Promise<EvaluationRubric> {
    return apiClient.put<EvaluationRubric>(`/rubrics/${id}`, updates)
  },

  // List all rubrics
  async listRubrics(page = 1, size = 20): Promise<PaginatedResponse<EvaluationRubric>> {
    return apiClient.get<PaginatedResponse<EvaluationRubric>>(`/rubrics?page=${page}&size=${size}`)
  },

  // Delete rubric
  async deleteRubric(id: string): Promise<void> {
    return apiClient.delete<void>(`/rubrics/${id}`)
  },

  // Create annotation task
  async createTask(task: Omit<AnnotationTask, 'id' | 'created_at' | 'updated_at'>): Promise<AnnotationTask> {
    return apiClient.post<AnnotationTask>('/annotations/tasks', task)
  },

  // Get annotation tasks for annotator
  async getTasks(annotatorId: string, status?: string): Promise<AnnotationTask[]> {
    const params = status ? `?status=${status}` : ''
    return apiClient.get<AnnotationTask[]>(`/annotations/tasks/${annotatorId}${params}`)
  },

  // Submit annotation
  async submitAnnotation(annotation: Omit<Annotation, 'id' | 'created_at' | 'updated_at'>): Promise<Annotation> {
    return apiClient.post<Annotation>('/annotations', annotation)
  },

  // Get annotations for a task
  async getAnnotations(taskId: string): Promise<Annotation[]> {
    return apiClient.get<Annotation[]>(`/annotations/task/${taskId}`)
  },

  // Get agreement metrics for a task
  async getAgreementMetrics(taskId: string): Promise<AgreementMetrics> {
    return apiClient.get<AgreementMetrics>(`/annotations/agreement/${taskId}`)
  },

  // Get annotation conflicts
  async getConflicts(taskId: string): Promise<AnnotationConflict[]> {
    return apiClient.get<AnnotationConflict[]>(`/annotations/conflicts/${taskId}`)
  },

  // Resolve annotation conflict
  async resolveConflict(conflictId: string, resolution: any): Promise<void> {
    return apiClient.post<void>(`/annotations/conflicts/${conflictId}/resolve`, resolution)
  },

  // Get annotation statistics
  async getStats(annotatorId?: string): Promise<AnnotationStats> {
    const params = annotatorId ? `?annotator_id=${annotatorId}` : ''
    return apiClient.get<AnnotationStats>(`/annotations/stats${params}`)
  },

  // Update annotation
  async updateAnnotation(id: string, updates: Partial<Annotation>): Promise<Annotation> {
    return apiClient.patch<Annotation>(`/annotations/${id}`, updates)
  },

  // Delete annotation
  async deleteAnnotation(id: string): Promise<void> {
    return apiClient.delete<void>(`/annotations/${id}`)
  },

  // Bulk submit annotations
  async bulkSubmit(annotations: Omit<Annotation, 'id' | 'created_at' | 'updated_at'>[]): Promise<Annotation[]> {
    return apiClient.post<Annotation[]>('/annotations/bulk', { annotations })
  },
}

export default annotationApi
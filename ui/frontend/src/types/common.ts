// Common types used across the application
export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  message: string
  code?: string
  details?: Record<string, any>
}

export interface ApiResponse<T = any> {
  data?: T
  error?: ApiError
  success: boolean
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  data: T | null
  loading: LoadingState
  error: string | null
}

export interface FileUpload {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: string
}

export interface WebSocketState {
  connected: boolean
  connecting: boolean
  error: string | null
  lastMessage: WebSocketMessage | null
}
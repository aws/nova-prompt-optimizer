// API-specific types and interfaces
export interface ApiConfig {
  baseUrl: string
  timeout: number
  retries: number
  headers: Record<string, string>
}

export interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  headers?: Record<string, string>
  body?: any
  timeout?: number
  retries?: number
}

export interface ApiClient {
  get<T>(url: string, options?: Omit<RequestOptions, 'method'>): Promise<T>
  post<T>(url: string, data?: any, options?: Omit<RequestOptions, 'method'>): Promise<T>
  put<T>(url: string, data?: any, options?: Omit<RequestOptions, 'method'>): Promise<T>
  delete<T>(url: string, options?: Omit<RequestOptions, 'method'>): Promise<T>
  patch<T>(url: string, data?: any, options?: Omit<RequestOptions, 'method'>): Promise<T>
  upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T>
}

export interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
}

export interface WebSocketClient {
  connect(): void
  disconnect(): void
  send(message: any): void
  subscribe(eventType: string, handler: (data: any) => void): () => void
  isConnected(): boolean
}
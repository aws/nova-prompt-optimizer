import { ApiClient, ApiConfig, RequestOptions, ApiError } from '@/types'

class HttpApiClient implements ApiClient {
  private config: ApiConfig
  private abortControllers: Map<string, AbortController> = new Map()

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    }
  }

  private async makeRequest<T>(
    url: string,
    options: RequestOptions
  ): Promise<T> {
    const fullUrl = `${this.config.baseUrl}${url}`
    const requestId = `${options.method}-${url}-${Date.now()}`
    
    // Create abort controller for this request
    const controller = new AbortController()
    this.abortControllers.set(requestId, controller)

    const requestOptions: RequestInit = {
      method: options.method,
      headers: {
        ...this.config.headers,
        ...options.headers,
      },
      signal: controller.signal,
      body: options.body ? JSON.stringify(options.body) : undefined,
    }

    let lastError: Error | null = null
    const maxRetries = options.retries ?? this.config.retries

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Set timeout
        const timeoutId = setTimeout(() => {
          controller.abort()
        }, options.timeout ?? this.config.timeout)

        const response = await fetch(fullUrl, requestOptions)
        clearTimeout(timeoutId)

        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response)
          throw new ApiClientError(
            errorData.message || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData
          )
        }

        const data = await response.json()
        this.abortControllers.delete(requestId)
        
        return data
      } catch (error) {
        lastError = error as Error
        
        // Don't retry on abort or client errors (4xx)
        if (
          error instanceof DOMException && error.name === 'AbortError' ||
          error instanceof ApiClientError && error.status && error.status >= 400 && error.status < 500
        ) {
          break
        }

        // Wait before retry (exponential backoff)
        if (attempt < maxRetries) {
          await this.delay(Math.pow(2, attempt) * 1000)
        }
      }
    }

    this.abortControllers.delete(requestId)
    throw lastError || new Error('Request failed after all retries')
  }

  private async parseErrorResponse(response: Response): Promise<ApiError> {
    try {
      const data = await response.json()
      return {
        message: data.message || data.detail || 'An error occurred',
        code: data.code,
        details: data.details || data,
      }
    } catch {
      return {
        message: `HTTP ${response.status}: ${response.statusText}`,
      }
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async get<T>(url: string, options: Omit<RequestOptions, 'method'> = {}): Promise<T> {
    return this.makeRequest<T>(url, { ...options, method: 'GET' })
  }

  async post<T>(url: string, data?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<T> {
    return this.makeRequest<T>(url, { ...options, method: 'POST', body: data })
  }

  async put<T>(url: string, data?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<T> {
    return this.makeRequest<T>(url, { ...options, method: 'PUT', body: data })
  }

  async delete<T>(url: string, options: Omit<RequestOptions, 'method'> = {}): Promise<T> {
    return this.makeRequest<T>(url, { ...options, method: 'DELETE' })
  }

  async patch<T>(url: string, data?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<T> {
    return this.makeRequest<T>(url, { ...options, method: 'PATCH', body: data })
  }

  async upload<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const fullUrl = `${this.config.baseUrl}${url}`
    const formData = new FormData()
    formData.append('file', file)

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100
            onProgress(progress)
          }
        })
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (error) {
            reject(new Error('Invalid JSON response'))
          }
        } else {
          reject(new ApiClientError(
            `Upload failed: ${xhr.statusText}`,
            xhr.status
          ))
        }
      })

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'))
      })

      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload timeout'))
      })

      xhr.timeout = this.config.timeout
      xhr.open('POST', fullUrl)
      
      // Add headers except Content-Type (let browser set it for FormData)
      Object.entries(this.config.headers).forEach(([key, value]) => {
        if (key.toLowerCase() !== 'content-type') {
          xhr.setRequestHeader(key, value)
        }
      })

      xhr.send(formData)
    })
  }

  // Cancel all pending requests
  cancelAllRequests(): void {
    this.abortControllers.forEach(controller => controller.abort())
    this.abortControllers.clear()
  }
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

// Create singleton instance
export const apiClient = new HttpApiClient()

export default apiClient
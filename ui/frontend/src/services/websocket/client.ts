import { WebSocketClient, WebSocketConfig, WebSocketMessage } from '@/types'

class WebSocketClientImpl implements WebSocketClient {
  private ws: WebSocket | null = null
  private config: WebSocketConfig
  private reconnectAttempts = 0
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null
  private eventHandlers: Map<string, Set<(data: any) => void>> = new Map()
  private connectionPromise: Promise<void> | null = null
  private isManuallyDisconnected = false

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      url: config.url || process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
      reconnectInterval: config.reconnectInterval || 5000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      heartbeatInterval: config.heartbeatInterval || 30000,
    }
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.isManuallyDisconnected = false
    this.connectionPromise = this.establishConnection()
  }

  private async establishConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.stopHeartbeat()
          
          if (!this.isManuallyDisconnected && this.shouldReconnect()) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.isManuallyDisconnected = true
    this.clearReconnectTimer()
    this.stopHeartbeat()
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect')
      this.ws = null
    }
  }

  send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message)
    }
  }

  subscribe(eventType: string, handler: (data: any) => void): () => void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set())
    }
    
    this.eventHandlers.get(eventType)!.add(handler)

    // Return unsubscribe function
    return () => {
      const handlers = this.eventHandlers.get(eventType)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.eventHandlers.delete(eventType)
        }
      }
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.eventHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.payload)
        } catch (error) {
          console.error('Error in WebSocket message handler:', error)
        }
      })
    }

    // Also trigger generic message handlers
    const genericHandlers = this.eventHandlers.get('*')
    if (genericHandlers) {
      genericHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in generic WebSocket message handler:', error)
        }
      })
    }
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.config.maxReconnectAttempts
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return
    }

    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    )

    console.log(`Scheduling WebSocket reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      this.reconnectTimer = null
      this.connect()
    }, delay)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()
    
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping', timestamp: new Date().toISOString() })
      }
    }, this.config.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  // Get connection state for debugging
  getConnectionState(): {
    connected: boolean
    connecting: boolean
    reconnectAttempts: number
    readyState?: number
  } {
    return {
      connected: this.isConnected(),
      connecting: this.connectionPromise !== null && !this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      readyState: this.ws?.readyState,
    }
  }
}

// Create singleton instance
export const wsClient = new WebSocketClientImpl()

export default wsClient
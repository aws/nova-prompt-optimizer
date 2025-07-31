// Re-export WebSocket client and utilities
export { default as wsClient } from './client'
export { websocketHandlers, websocketSenders } from './handlers'

// Re-export the main client for direct usage
export { wsClient as default } from './client'
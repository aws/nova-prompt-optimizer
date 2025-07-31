import { wsClient } from './client'
import { OptimizationTask, WebSocketMessage } from '@/types'

// WebSocket message handlers for different event types
export const websocketHandlers = {
  // Optimization progress updates
  handleOptimizationProgress: (callback: (task: OptimizationTask) => void) => {
    return wsClient.subscribe('optimization_progress', callback)
  },

  // Optimization completion
  handleOptimizationComplete: (callback: (task: OptimizationTask) => void) => {
    return wsClient.subscribe('optimization_complete', callback)
  },

  // Optimization error
  handleOptimizationError: (callback: (error: { taskId: string; error: string }) => void) => {
    return wsClient.subscribe('optimization_error', callback)
  },

  // Dataset upload progress
  handleDatasetUploadProgress: (callback: (progress: { id: string; progress: number }) => void) => {
    return wsClient.subscribe('dataset_upload_progress', callback)
  },

  // Annotation task updates
  handleAnnotationUpdate: (callback: (update: any) => void) => {
    return wsClient.subscribe('annotation_update', callback)
  },

  // System notifications
  handleSystemNotification: (callback: (notification: { type: string; message: string }) => void) => {
    return wsClient.subscribe('system_notification', callback)
  },

  // Generic message handler for debugging
  handleAllMessages: (callback: (message: WebSocketMessage) => void) => {
    return wsClient.subscribe('*', callback)
  },
}

// Helper functions for sending WebSocket messages
export const websocketSenders = {
  // Subscribe to optimization task updates
  subscribeToOptimization: (taskId: string) => {
    wsClient.send({
      type: 'subscribe_optimization',
      payload: { task_id: taskId }
    })
  },

  // Unsubscribe from optimization task updates
  unsubscribeFromOptimization: (taskId: string) => {
    wsClient.send({
      type: 'unsubscribe_optimization',
      payload: { task_id: taskId }
    })
  },

  // Subscribe to dataset upload progress
  subscribeToDatasetUpload: (uploadId: string) => {
    wsClient.send({
      type: 'subscribe_dataset_upload',
      payload: { upload_id: uploadId }
    })
  },

  // Join annotation room
  joinAnnotationRoom: (taskId: string) => {
    wsClient.send({
      type: 'join_annotation_room',
      payload: { task_id: taskId }
    })
  },

  // Leave annotation room
  leaveAnnotationRoom: (taskId: string) => {
    wsClient.send({
      type: 'leave_annotation_room',
      payload: { task_id: taskId }
    })
  },
}

export default { websocketHandlers, websocketSenders }
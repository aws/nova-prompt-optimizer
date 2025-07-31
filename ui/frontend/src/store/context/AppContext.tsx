import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { WebSocketState } from '@/types'
import { wsClient } from '@/services'

// App-wide state interface
interface AppState {
  // WebSocket connection state
  websocket: WebSocketState
  
  // Global loading states
  globalLoading: boolean
  
  // User preferences
  theme: 'light' | 'dark' | 'system'
  
  // Navigation state
  currentWorkflowStep: string
  
  // Notifications
  notifications: Notification[]
}

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
}

// Action types
type AppAction =
  | { type: 'SET_WEBSOCKET_STATE'; payload: Partial<WebSocketState> }
  | { type: 'SET_GLOBAL_LOADING'; payload: boolean }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' | 'system' }
  | { type: 'SET_WORKFLOW_STEP'; payload: string }
  | { type: 'ADD_NOTIFICATION'; payload: Omit<Notification, 'id' | 'timestamp' | 'read'> }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'CLEAR_NOTIFICATIONS' }

// Initial state
const initialState: AppState = {
  websocket: {
    connected: false,
    connecting: false,
    error: null,
    lastMessage: null,
  },
  globalLoading: false,
  theme: 'system',
  currentWorkflowStep: 'dashboard',
  notifications: [],
}

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_WEBSOCKET_STATE':
      return {
        ...state,
        websocket: { ...state.websocket, ...action.payload },
      }
    
    case 'SET_GLOBAL_LOADING':
      return {
        ...state,
        globalLoading: action.payload,
      }
    
    case 'SET_THEME':
      return {
        ...state,
        theme: action.payload,
      }
    
    case 'SET_WORKFLOW_STEP':
      return {
        ...state,
        currentWorkflowStep: action.payload,
      }
    
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [
          {
            ...action.payload,
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            read: false,
          },
          ...state.notifications,
        ],
      }
    
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(notification =>
          notification.id === action.payload
            ? { ...notification, read: true }
            : notification
        ),
      }
    
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        ),
      }
    
    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        notifications: [],
      }
    
    default:
      return state
  }
}

// Context
interface AppContextType {
  state: AppState
  dispatch: React.Dispatch<AppAction>
  
  // Helper functions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void
  markNotificationRead: (id: string) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  setWorkflowStep: (step: string) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

// Provider component
interface AppProviderProps {
  children: ReactNode
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      dispatch({ type: 'SET_WEBSOCKET_STATE', payload: { connecting: true } })
      
      try {
        wsClient.connect()
        
        // Handle connection state changes
        const checkConnection = () => {
          const connectionState = wsClient.getConnectionState()
          dispatch({
            type: 'SET_WEBSOCKET_STATE',
            payload: {
              connected: connectionState.connected,
              connecting: connectionState.connecting,
              error: null,
            },
          })
        }

        // Check connection state periodically
        const interval = setInterval(checkConnection, 1000)
        
        // Handle WebSocket messages
        const unsubscribe = wsClient.subscribe('*', (message) => {
          dispatch({
            type: 'SET_WEBSOCKET_STATE',
            payload: { lastMessage: message },
          })
        })

        return () => {
          clearInterval(interval)
          unsubscribe()
          wsClient.disconnect()
        }
      } catch (error) {
        dispatch({
          type: 'SET_WEBSOCKET_STATE',
          payload: {
            connected: false,
            connecting: false,
            error: error instanceof Error ? error.message : 'WebSocket connection failed',
          },
        })
      }
    }

    const cleanup = connectWebSocket()
    return cleanup
  }, [])

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null
    if (savedTheme) {
      dispatch({ type: 'SET_THEME', payload: savedTheme })
    }
  }, [])

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement
    
    if (state.theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const applySystemTheme = () => {
        root.classList.toggle('dark', mediaQuery.matches)
      }
      
      applySystemTheme()
      mediaQuery.addEventListener('change', applySystemTheme)
      
      return () => mediaQuery.removeEventListener('change', applySystemTheme)
    } else {
      root.classList.toggle('dark', state.theme === 'dark')
    }
  }, [state.theme])

  // Helper functions
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    dispatch({ type: 'ADD_NOTIFICATION', payload: notification })
  }

  const markNotificationRead = (id: string) => {
    dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id })
  }

  const removeNotification = (id: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id })
  }

  const clearNotifications = () => {
    dispatch({ type: 'CLEAR_NOTIFICATIONS' })
  }

  const setTheme = (theme: 'light' | 'dark' | 'system') => {
    localStorage.setItem('theme', theme)
    dispatch({ type: 'SET_THEME', payload: theme })
  }

  const setWorkflowStep = (step: string) => {
    dispatch({ type: 'SET_WORKFLOW_STEP', payload: step })
  }

  const contextValue: AppContextType = {
    state,
    dispatch,
    addNotification,
    markNotificationRead,
    removeNotification,
    clearNotifications,
    setTheme,
    setWorkflowStep,
  }

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  )
}

// Hook to use the app context
export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

export default AppContext
import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  FileText, 
  Download, 
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Terminal
} from 'lucide-react'

interface LogViewerProps {
  taskId: string
  maxHeight?: number
  autoScroll?: boolean
  refreshInterval?: number
}

type LogLevel = 'debug' | 'info' | 'warning' | 'error'

interface LogEntry {
  timestamp: string
  level: LogLevel
  message: string
  component?: string
}

const LOG_LEVEL_COLORS = {
  debug: 'text-gray-500',
  info: 'text-blue-600 dark:text-blue-400',
  warning: 'text-yellow-600 dark:text-yellow-400',
  error: 'text-red-600 dark:text-red-400'
}

const LOG_LEVEL_BADGES = {
  debug: 'outline',
  info: 'secondary',
  warning: 'default',
  error: 'destructive'
}

// Mock log data for demonstration
const generateMockLogs = (): LogEntry[] => {
  const logs: LogEntry[] = []
  const now = new Date()
  
  const messages = [
    { level: 'info' as LogLevel, message: 'Starting optimization process', component: 'optimizer' },
    { level: 'info' as LogLevel, message: 'Loading dataset and prompt configuration', component: 'data' },
    { level: 'debug' as LogLevel, message: 'Initializing Nova Prompt Optimizer', component: 'optimizer' },
    { level: 'info' as LogLevel, message: 'Beginning iteration 1 of 10', component: 'optimizer' },
    { level: 'debug' as LogLevel, message: 'Generating candidate prompts', component: 'generator' },
    { level: 'info' as LogLevel, message: 'Evaluating 5 candidate prompts', component: 'evaluator' },
    { level: 'debug' as LogLevel, message: 'Running inference on test dataset', component: 'inference' },
    { level: 'info' as LogLevel, message: 'Iteration 1 complete - best score: 0.742', component: 'optimizer' },
    { level: 'info' as LogLevel, message: 'Beginning iteration 2 of 10', component: 'optimizer' },
    { level: 'warning' as LogLevel, message: 'Rate limit encountered, retrying in 2s', component: 'inference' },
    { level: 'debug' as LogLevel, message: 'Applying meta-prompting techniques', component: 'meta-prompter' },
    { level: 'info' as LogLevel, message: 'Iteration 2 complete - best score: 0.758', component: 'optimizer' }
  ]
  
  messages.forEach((msg, index) => {
    logs.push({
      timestamp: new Date(now.getTime() - (messages.length - index) * 30000).toISOString(),
      level: msg.level,
      message: msg.message,
      component: msg.component
    })
  })
  
  return logs
}

export const LogViewer: React.FC<LogViewerProps> = ({
  taskId,
  maxHeight = 400,
  autoScroll = true,
  refreshInterval = 5000
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([])
  const [selectedLevel, setSelectedLevel] = useState<LogLevel | 'all'>('all')
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Load logs (using mock data for now)
  const loadLogs = async () => {
    setIsLoading(true)
    try {
      // In a real implementation, this would call the API
      // const logs = await optimizationApi.getLogs(taskId, selectedLevel === 'all' ? undefined : selectedLevel)
      const mockLogs = generateMockLogs()
      setLogs(mockLogs)
    } catch (error) {
      console.error('Failed to load logs:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Filter logs by level
  useEffect(() => {
    if (selectedLevel === 'all') {
      setFilteredLogs(logs)
    } else {
      setFilteredLogs(logs.filter(log => log.level === selectedLevel))
    }
  }, [logs, selectedLevel])

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [filteredLogs, autoScroll])

  // Load logs on mount and set up refresh interval
  useEffect(() => {
    loadLogs()
    
    if (refreshInterval > 0) {
      const interval = setInterval(loadLogs, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [taskId, refreshInterval])

  const handleDownloadLogs = () => {
    const logText = filteredLogs.map(log => 
      `[${new Date(log.timestamp).toLocaleString()}] ${log.level.toUpperCase()} ${log.component ? `[${log.component}]` : ''} ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `optimization-logs-${taskId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            <CardTitle>Optimization Logs</CardTitle>
            <Badge variant="outline" className="text-xs">
              {filteredLogs.length} entries
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedLevel} onValueChange={(value) => setSelectedLevel(value as LogLevel | 'all')}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="debug">Debug</SelectItem>
                <SelectItem value="info">Info</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="sm"
              onClick={loadLogs}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadLogs}
              disabled={filteredLogs.length === 0}
            >
              <Download className="h-4 w-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </div>
        <CardDescription>
          Real-time logs from the optimization process
        </CardDescription>
      </CardHeader>
      
      {(isExpanded || filteredLogs.length === 0) && (
        <CardContent>
          <ScrollArea 
            ref={scrollAreaRef}
            className="w-full rounded-md border"
            style={{ height: maxHeight }}
          >
            <div className="p-4 space-y-2">
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, index) => (
                  <div key={index} className="flex items-start gap-3 text-sm font-mono">
                    <span className="text-muted-foreground text-xs whitespace-nowrap">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    
                    <Badge 
                      variant={LOG_LEVEL_BADGES[log.level] as any}
                      className="text-xs min-w-[60px] justify-center"
                    >
                      {log.level.toUpperCase()}
                    </Badge>
                    
                    {log.component && (
                      <Badge variant="outline" className="text-xs">
                        {log.component}
                      </Badge>
                    )}
                    
                    <span className={`flex-1 ${LOG_LEVEL_COLORS[log.level]}`}>
                      {log.message}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No logs available yet</p>
                  <p className="text-xs">Logs will appear here as the optimization progresses</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      )}
    </Card>
  )
}
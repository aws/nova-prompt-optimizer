import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { 
  Play, 
  Pause, 
  Square, 
  Clock, 
  Zap, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react'
import { ProgressTracker } from './ProgressTracker'
import { LogViewer } from './LogViewer'
import { OptimizationTask, OptimizationStatus } from '@/types'
import { useOptimization } from '@/hooks'

interface OptimizationProgressProps {
  task: OptimizationTask
  onCancel?: (taskId: string) => void
  onPause?: (taskId: string) => void
  onResume?: (taskId: string) => void
  showLogs?: boolean
  autoRefresh?: boolean
}

const getStatusIcon = (status: OptimizationStatus) => {
  switch (status) {
    case 'running':
      return <Loader2 className="h-4 w-4 animate-spin" />
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-500" />
    case 'failed':
      return <XCircle className="h-4 w-4 text-red-500" />
    case 'cancelled':
      return <XCircle className="h-4 w-4 text-gray-500" />
    case 'pending':
      return <Clock className="h-4 w-4 text-yellow-500" />
    default:
      return <AlertCircle className="h-4 w-4" />
  }
}

const getStatusColor = (status: OptimizationStatus) => {
  switch (status) {
    case 'running':
      return 'default'
    case 'completed':
      return 'default'
    case 'failed':
      return 'destructive'
    case 'cancelled':
      return 'secondary'
    case 'pending':
      return 'secondary'
    default:
      return 'outline'
  }
}

const formatDuration = (startTime: string, endTime?: string) => {
  const start = new Date(startTime)
  const end = endTime ? new Date(endTime) : new Date()
  const duration = end.getTime() - start.getTime()
  
  const hours = Math.floor(duration / (1000 * 60 * 60))
  const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((duration % (1000 * 60)) / 1000)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds}s`
  } else {
    return `${seconds}s`
  }
}

const estimateTimeRemaining = (task: OptimizationTask) => {
  if (task.status !== 'running' || task.progress === 0) {
    return null
  }
  
  const elapsed = new Date().getTime() - new Date(task.start_time).getTime()
  const totalEstimated = elapsed / task.progress
  const remaining = totalEstimated - elapsed
  
  if (remaining <= 0) {
    return 'Almost done'
  }
  
  const minutes = Math.floor(remaining / (1000 * 60))
  const seconds = Math.floor((remaining % (1000 * 60)) / 1000)
  
  if (minutes > 0) {
    return `~${minutes}m ${seconds}s remaining`
  } else {
    return `~${seconds}s remaining`
  }
}

export const OptimizationProgress: React.FC<OptimizationProgressProps> = ({
  task,
  onCancel,
  onPause,
  onResume,
  showLogs = true,
  autoRefresh = true
}) => {
  const { pauseOptimization, resumeOptimization, cancelOptimization } = useOptimization({ autoLoad: false })
  const [isActionLoading, setIsActionLoading] = useState<string | null>(null)
  const [, setCurrentTime] = useState(new Date())

  // Update current time for duration calculation
  useEffect(() => {
    if (task.status === 'running' && autoRefresh) {
      const interval = setInterval(() => {
        setCurrentTime(new Date())
      }, 1000)
      
      return () => clearInterval(interval)
    }
  }, [task.status, autoRefresh])

  const handleAction = async (action: 'pause' | 'resume' | 'cancel') => {
    setIsActionLoading(action)
    
    try {
      switch (action) {
        case 'pause':
          await pauseOptimization(task.id)
          onPause?.(task.id)
          break
        case 'resume':
          await resumeOptimization(task.id)
          onResume?.(task.id)
          break
        case 'cancel':
          await cancelOptimization(task.id)
          onCancel?.(task.id)
          break
      }
    } catch (error) {
      console.error(`Failed to ${action} optimization:`, error)
    } finally {
      setIsActionLoading(null)
    }
  }

  const progressPercentage = Math.round(task.progress * 100)
  const timeRemaining = estimateTimeRemaining(task)
  const duration = formatDuration(task.start_time, task.end_time)

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getStatusIcon(task.status)}
              <span>Optimization Progress</span>
            </div>
            <Badge variant={getStatusColor(task.status) as any}>
              {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
            </Badge>
          </CardTitle>
          <CardDescription>
            Task ID: {task.id}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span className="font-medium">{progressPercentage}%</span>
            </div>
            <Progress value={progressPercentage} className="w-full" />
            {timeRemaining && (
              <p className="text-sm text-muted-foreground text-center">
                {timeRemaining}
              </p>
            )}
          </div>

          {/* Current Step */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Current Step</span>
            </div>
            <p className="text-sm text-muted-foreground ml-6">
              {task.current_step || 'Initializing...'}
            </p>
          </div>

          <Separator />

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Duration:</span>
              <div className="font-medium">{duration}</div>
            </div>
            <div>
              <span className="text-muted-foreground">Steps:</span>
              <div className="font-medium">
                {Math.floor(task.progress * task.total_steps)} / {task.total_steps}
              </div>
            </div>
          </div>

          {/* Configuration Summary */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Configuration</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-muted-foreground">Optimizer:</span>
                <Badge variant="outline" className="ml-1 text-xs">
                  {task.config.optimizer_type}
                </Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Model:</span>
                <Badge variant="outline" className="ml-1 text-xs">
                  {task.config.model_name}
                </Badge>
              </div>
              <div>
                <span className="text-muted-foreground">Max Iterations:</span>
                <span className="ml-1 font-medium">{task.config.max_iterations}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Metric:</span>
                <span className="ml-1 font-medium">{task.config.evaluation_metric}</span>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {task.error_message && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <div className="flex items-start gap-2">
                <XCircle className="h-4 w-4 text-red-500 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-sm font-medium text-red-800 dark:text-red-200">
                    Optimization Failed
                  </p>
                  <p className="text-sm text-red-700 dark:text-red-300">
                    {task.error_message}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {task.status === 'running' && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction('pause')}
                disabled={isActionLoading !== null}
              >
                {isActionLoading === 'pause' ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Pause className="mr-2 h-4 w-4" />
                )}
                Pause
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleAction('cancel')}
                disabled={isActionLoading !== null}
              >
                {isActionLoading === 'cancel' ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Square className="mr-2 h-4 w-4" />
                )}
                Cancel
              </Button>
            </div>
          )}

          {task.status === 'pending' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleAction('resume')}
              disabled={isActionLoading !== null}
            >
              {isActionLoading === 'resume' ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Resume
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Progress Tracker */}
      <ProgressTracker task={task} />

      {/* Logs */}
      {showLogs && (
        <LogViewer taskId={task.id} />
      )}
    </div>
  )
}
import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, Target, Zap, Clock } from 'lucide-react'
import { OptimizationTask } from '@/types'

interface ProgressTrackerProps {
  task: OptimizationTask
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ task }) => {
  const currentStep = Math.floor(task.progress * task.total_steps)

  // Mock optimization history for visualization
  const optimizationSteps = Array.from({ length: Math.min(currentStep, 10) }, (_, i) => ({
    step: i + 1,
    score: 0.6 + (Math.random() * 0.3) + (i * 0.02), // Simulate improving scores
    improvement: i === 0 ? 0 : Math.random() * 0.05,
    timestamp: new Date(Date.now() - (10 - i) * 60000).toISOString(),
    status: i < currentStep - 1 ? 'completed' : i === currentStep - 1 ? 'current' : 'pending'
  }))

  const bestScore = Math.max(...optimizationSteps.map(s => s.score), 0)
  const totalImprovement = optimizationSteps.length > 1 
    ? ((bestScore - optimizationSteps[0].score) / optimizationSteps[0].score * 100)
    : 0

  return (
    <div className="space-y-4">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Best Score</p>
                <p className="text-lg font-semibold">
                  {bestScore > 0 ? bestScore.toFixed(3) : '--'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Improvement</p>
                <p className="text-lg font-semibold">
                  {totalImprovement > 0 ? `+${totalImprovement.toFixed(1)}%` : '--'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Iterations</p>
                <p className="text-lg font-semibold">
                  {currentStep} / {task.config.max_iterations}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Optimization Steps
          </CardTitle>
          <CardDescription>
            Progress through optimization iterations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {optimizationSteps.length > 0 ? (
            <div className="space-y-3">
              {optimizationSteps.map((step) => (
                <div key={step.step} className="flex items-center gap-4 p-3 rounded-lg border">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step.status === 'completed' 
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                        : step.status === 'current'
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                        : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                    }`}>
                      {step.step}
                    </div>
                  </div>

                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Iteration {step.step}
                      </span>
                      <Badge variant={
                        step.status === 'completed' ? 'default' :
                        step.status === 'current' ? 'secondary' : 'outline'
                      } className="text-xs">
                        {step.status === 'current' ? 'In Progress' : 
                         step.status === 'completed' ? 'Complete' : 'Pending'}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Score: {step.score.toFixed(3)}</span>
                      {step.improvement > 0 && (
                        <span className="text-green-600 dark:text-green-400">
                          +{(step.improvement * 100).toFixed(1)}%
                        </span>
                      )}
                      <span>{new Date(step.timestamp).toLocaleTimeString()}</span>
                    </div>

                    {step.status === 'current' && (
                      <div className="mt-2">
                        <Progress value={75} className="h-1" />
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Remaining Steps Preview */}
              {currentStep < task.config.max_iterations && (
                <div className="flex items-center gap-4 p-3 rounded-lg border border-dashed">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium bg-gray-100 text-gray-400 dark:bg-gray-800">
                      ...
                    </div>
                  </div>
                  <div className="flex-1">
                    <span className="text-sm text-muted-foreground">
                      {task.config.max_iterations - currentStep} more iterations planned
                    </span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Optimization steps will appear here as they complete</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
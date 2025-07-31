import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  TrendingUp, 
  Download, 
  Share, 
  BarChart3, 
  FileText, 
  Zap,
  CheckCircle,
  ArrowRight
} from 'lucide-react'
import { ResultsComparison } from './ResultsComparison'
import { MetricsVisualization } from './MetricsVisualization'
import { OptimizationResults as OptimizationResultsType, OptimizationTask } from '@/types'
import { useOptimization } from '@/hooks'

interface OptimizationResultsProps {
  results: OptimizationResultsType
  task?: OptimizationTask
  onExport?: (format: 'json' | 'csv' | 'pdf') => void
  onAnnotate?: (results: OptimizationResultsType) => void
  onShare?: (results: OptimizationResultsType) => void
  showActions?: boolean
}

export const OptimizationResults: React.FC<OptimizationResultsProps> = ({
  results,
  task,
  onExport,
  onAnnotate,
  onShare,
  showActions = true
}) => {
  const { exportResults } = useOptimization({ autoLoad: false })
  const [isExporting, setIsExporting] = useState<string | null>(null)

  const handleExport = async (format: 'json' | 'csv' | 'pdf') => {
    setIsExporting(format)
    
    try {
      if (onExport) {
        onExport(format)
      } else {
        await exportResults(results.task_id, format)
      }
    } catch (error) {
      console.error(`Failed to export results as ${format}:`, error)
    } finally {
      setIsExporting(null)
    }
  }

  const improvementPercentage = results.improvement_percentage
  const isImprovement = improvementPercentage > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Optimization Complete
          </CardTitle>
          <CardDescription>
            Task ID: {results.task_id}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Performance Improvement */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TrendingUp className={`h-4 w-4 ${isImprovement ? 'text-green-500' : 'text-red-500'}`} />
                <span className="text-sm font-medium">Performance Change</span>
              </div>
              <div className={`text-2xl font-bold ${isImprovement ? 'text-green-600' : 'text-red-600'}`}>
                {isImprovement ? '+' : ''}{improvementPercentage.toFixed(1)}%
              </div>
              <p className="text-sm text-muted-foreground">
                {isImprovement ? 'Improvement achieved' : 'Performance decreased'}
              </p>
            </div>

            {/* Metric Scores */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">Best Score</span>
              </div>
              <div className="text-2xl font-bold">
                {Object.values(results.performance_metrics)[0]?.toFixed(3) || '--'}
              </div>
              <p className="text-sm text-muted-foreground">
                {task?.config.evaluation_metric || 'Primary metric'}
              </p>
            </div>

            {/* Optimization Steps */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">Iterations</span>
              </div>
              <div className="text-2xl font-bold">
                {results.optimization_history.length}
              </div>
              <p className="text-sm text-muted-foreground">
                Steps completed
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          {showActions && (
            <>
              <Separator className="my-4" />
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('json')}
                  disabled={isExporting !== null}
                >
                  <Download className="mr-2 h-4 w-4" />
                  {isExporting === 'json' ? 'Exporting...' : 'Export JSON'}
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('csv')}
                  disabled={isExporting !== null}
                >
                  <Download className="mr-2 h-4 w-4" />
                  {isExporting === 'csv' ? 'Exporting...' : 'Export CSV'}
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('pdf')}
                  disabled={isExporting !== null}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  {isExporting === 'pdf' ? 'Exporting...' : 'Export Report'}
                </Button>
                
                {onShare && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onShare(results)}
                  >
                    <Share className="mr-2 h-4 w-4" />
                    Share Results
                  </Button>
                )}
                
                {onAnnotate && (
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => onAnnotate(results)}
                  >
                    <ArrowRight className="mr-2 h-4 w-4" />
                    Start Annotation
                  </Button>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Detailed Results */}
      <Tabs defaultValue="comparison" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="comparison">Prompt Comparison</TabsTrigger>
          <TabsTrigger value="metrics">Performance Metrics</TabsTrigger>
          <TabsTrigger value="history">Optimization History</TabsTrigger>
        </TabsList>
        
        <TabsContent value="comparison" className="space-y-4">
          <ResultsComparison results={results} />
        </TabsContent>
        
        <TabsContent value="metrics" className="space-y-4">
          <MetricsVisualization results={results} />
        </TabsContent>
        
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimization History</CardTitle>
              <CardDescription>
                Step-by-step progress through the optimization process
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.optimization_history.map((step) => (
                  <div key={step.step} className="flex items-center gap-4 p-4 rounded-lg border">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="text-sm font-medium text-primary">
                          {step.step}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">
                          Iteration {step.step}
                        </span>
                        <Badge variant="outline">
                          Score: {step.score.toFixed(3)}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        {step.improvement > 0 && (
                          <span className="text-green-600 dark:text-green-400">
                            +{(step.improvement * 100).toFixed(1)}% improvement
                          </span>
                        )}
                        <span>
                          {new Date(step.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
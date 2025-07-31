import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  BarChart3, 
  TrendingUp, 
  Target,
  Zap,
  Award,
  LineChart
} from 'lucide-react'
import { OptimizationResults } from '@/types'

interface PerformanceMetricsChartProps {
  results: OptimizationResults[]
}

interface MetricComparison {
  name: string
  displayName: string
  values: Array<{
    taskId: string
    score: number
    improvement: number
    optimizerType: string
  }>
  average: number
  best: number
  worst: number
}

export const PerformanceMetricsChart: React.FC<PerformanceMetricsChartProps> = ({
  results
}) => {
  const [selectedMetric, setSelectedMetric] = useState<string>('')
  const [chartType, setChartType] = useState<'bar' | 'line' | 'radar'>('bar')

  // Process metrics data
  const processMetricsData = (): MetricComparison[] => {
    if (results.length === 0) return []

    // Get all unique metrics across all results
    const allMetrics = new Set<string>()
    results.forEach(result => {
      Object.keys(result.performance_metrics).forEach(metric => {
        allMetrics.add(metric)
      })
    })

    return Array.from(allMetrics).map(metric => {
      const values = results.map(result => {
        const score = result.performance_metrics[metric] || 0
        // Calculate improvement (assuming original was 10% lower for demo)
        const originalScore = score * 0.9
        const improvement = ((score - originalScore) / originalScore) * 100

        return {
          taskId: result.task_id,
          score,
          improvement,
          optimizerType: 'nova' // This would come from the task config
        }
      })

      const scores = values.map(v => v.score)
      
      return {
        name: metric,
        displayName: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        values,
        average: scores.reduce((sum, score) => sum + score, 0) / scores.length,
        best: Math.max(...scores),
        worst: Math.min(...scores)
      }
    })
  }

  const metricsData = processMetricsData()
  const currentMetric = selectedMetric 
    ? metricsData.find(m => m.name === selectedMetric)
    : metricsData[0]

  // Calculate overall statistics
  const overallStats = {
    totalExperiments: results.length,
    averageImprovement: results.reduce((sum, r) => sum + r.improvement_percentage, 0) / results.length,
    bestImprovement: Math.max(...results.map(r => r.improvement_percentage)),
    successfulOptimizations: results.filter(r => r.improvement_percentage > 0).length
  }

  const renderBarChart = (metric: MetricComparison) => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3">
        {metric.values.map((value, index) => (
          <div key={value.taskId} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Experiment {index + 1}</span>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {value.optimizerType.toUpperCase()}
                </Badge>
                <span className="font-medium">{value.score.toFixed(3)}</span>
              </div>
            </div>
            <div className="relative">
              <Progress value={(value.score / metric.best) * 100} className="h-3" />
              <div className="absolute inset-0 flex items-center justify-end pr-2">
                <span className={`text-xs font-medium ${
                  value.improvement > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {value.improvement > 0 ? '+' : ''}{value.improvement.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderLineChart = (metric: MetricComparison) => (
    <div className="space-y-4">
      <div className="relative h-64 border rounded-lg p-4">
        <div className="absolute inset-4">
          {/* Simple line chart visualization */}
          <div className="h-full flex items-end justify-between">
            {metric.values.map((value, index) => (
              <div key={value.taskId} className="flex flex-col items-center gap-2">
                <div 
                  className="bg-primary rounded-t"
                  style={{ 
                    height: `${(value.score / metric.best) * 100}%`,
                    width: '20px'
                  }}
                />
                <span className="text-xs text-muted-foreground">
                  {index + 1}
                </span>
              </div>
            ))}
          </div>
          
          {/* Y-axis labels */}
          <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-muted-foreground">
            <span>{metric.best.toFixed(2)}</span>
            <span>{((metric.best + metric.worst) / 2).toFixed(2)}</span>
            <span>{metric.worst.toFixed(2)}</span>
          </div>
        </div>
      </div>
      
      <div className="text-center text-sm text-muted-foreground">
        Experiment Progression
      </div>
    </div>
  )

  const renderMetricSummary = (metric: MetricComparison) => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="text-center space-y-1">
        <div className="text-2xl font-bold text-blue-600">
          {metric.average.toFixed(3)}
        </div>
        <div className="text-sm text-muted-foreground">Average</div>
      </div>
      
      <div className="text-center space-y-1">
        <div className="text-2xl font-bold text-green-600">
          {metric.best.toFixed(3)}
        </div>
        <div className="text-sm text-muted-foreground">Best</div>
      </div>
      
      <div className="text-center space-y-1">
        <div className="text-2xl font-bold text-red-600">
          {metric.worst.toFixed(3)}
        </div>
        <div className="text-sm text-muted-foreground">Worst</div>
      </div>
      
      <div className="text-center space-y-1">
        <div className="text-2xl font-bold text-purple-600">
          {((metric.best - metric.worst) / metric.worst * 100).toFixed(1)}%
        </div>
        <div className="text-sm text-muted-foreground">Range</div>
      </div>
    </div>
  )

  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="pt-8 pb-8 text-center">
          <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">
            No results selected for analysis
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Experiments</p>
                <p className="text-lg font-semibold">
                  {overallStats.totalExperiments}
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
                <p className="text-sm text-muted-foreground">Avg Improvement</p>
                <p className="text-lg font-semibold">
                  {overallStats.averageImprovement > 0 ? '+' : ''}
                  {overallStats.averageImprovement.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Award className="h-4 w-4 text-yellow-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Best Improvement</p>
                <p className="text-lg font-semibold">
                  +{overallStats.bestImprovement.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-purple-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-lg font-semibold">
                  {((overallStats.successfulOptimizations / overallStats.totalExperiments) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Interactive Charts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Performance Metrics Visualization
          </CardTitle>
          <CardDescription>
            Interactive charts showing performance across selected experiments
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Controls */}
            <div className="flex items-center gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Metric</label>
                <Select
                  value={selectedMetric || metricsData[0]?.name || ''}
                  onValueChange={setSelectedMetric}
                >
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Select metric" />
                  </SelectTrigger>
                  <SelectContent>
                    {metricsData.map(metric => (
                      <SelectItem key={metric.name} value={metric.name}>
                        {metric.displayName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Chart Type</label>
                <div className="flex gap-1">
                  <Button
                    variant={chartType === 'bar' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType('bar')}
                  >
                    <BarChart3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={chartType === 'line' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setChartType('line')}
                  >
                    <LineChart className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Chart Content */}
            {currentMetric && (
              <Tabs defaultValue="chart" className="w-full">
                <TabsList>
                  <TabsTrigger value="chart">Chart</TabsTrigger>
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                </TabsList>
                
                <TabsContent value="chart" className="space-y-4">
                  <div className="space-y-4">
                    <h4 className="font-medium">{currentMetric.displayName}</h4>
                    {chartType === 'bar' && renderBarChart(currentMetric)}
                    {chartType === 'line' && renderLineChart(currentMetric)}
                  </div>
                </TabsContent>
                
                <TabsContent value="summary" className="space-y-4">
                  <h4 className="font-medium">{currentMetric.displayName} Summary</h4>
                  {renderMetricSummary(currentMetric)}
                </TabsContent>
                
                <TabsContent value="details" className="space-y-4">
                  <h4 className="font-medium">Detailed Breakdown</h4>
                  <div className="space-y-3">
                    {currentMetric.values.map((value, index) => (
                      <div key={value.taskId} className="flex items-center justify-between p-3 rounded-lg border">
                        <div className="space-y-1">
                          <div className="font-medium">Experiment {index + 1}</div>
                          <div className="text-sm text-muted-foreground">
                            Task ID: {value.taskId.slice(0, 8)}...
                          </div>
                        </div>
                        
                        <div className="text-right space-y-1">
                          <div className="font-medium">{value.score.toFixed(3)}</div>
                          <div className={`text-sm ${
                            value.improvement > 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {value.improvement > 0 ? '+' : ''}{value.improvement.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
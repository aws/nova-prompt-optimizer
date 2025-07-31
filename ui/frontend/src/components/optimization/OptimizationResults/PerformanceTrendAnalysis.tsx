import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  LineChart,
  Target,
  Zap,
  Award,
  Filter
} from 'lucide-react'
import { OptimizationResults, OptimizationTask } from '@/types'

interface PerformanceTrendAnalysisProps {
  tasks: OptimizationTask[]
  selectedResults?: OptimizationResults[]
}

interface TrendDataPoint {
  date: string
  timestamp: number
  taskId: string
  optimizerType: string
  modelName: string
  averageScore: number
  improvement: number
  metricScores: Record<string, number>
}

interface TrendAnalysis {
  overallTrend: 'improving' | 'declining' | 'stable'
  trendStrength: number
  bestPeriod: string
  worstPeriod: string
  averageImprovement: number
  consistencyScore: number
}

export const PerformanceTrendAnalysis: React.FC<PerformanceTrendAnalysisProps> = ({
  tasks
}) => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d')
  const [groupBy, setGroupBy] = useState<'day' | 'week' | 'month'>('day')
  const [metricFilter, setMetricFilter] = useState<string>('all')
  const [optimizerFilter, setOptimizerFilter] = useState<string>('all')

  // Process trend data
  const processTrendData = (): TrendDataPoint[] => {
    const now = new Date()
    const cutoffDate = new Date()
    
    switch (timeRange) {
      case '7d':
        cutoffDate.setDate(now.getDate() - 7)
        break
      case '30d':
        cutoffDate.setDate(now.getDate() - 30)
        break
      case '90d':
        cutoffDate.setDate(now.getDate() - 90)
        break
      case 'all':
        cutoffDate.setFullYear(2020) // Far in the past
        break
    }

    return tasks
      .filter(task => task.results && new Date(task.created_at) >= cutoffDate)
      .filter(task => optimizerFilter === 'all' || task.config.optimizer_type === optimizerFilter)
      .map(task => {
        const results = task.results!
        const metricScores = results.performance_metrics
        const averageScore = Object.values(metricScores).reduce((sum, score) => sum + score, 0) / Object.keys(metricScores).length

        return {
          date: new Date(task.created_at).toISOString().split('T')[0],
          timestamp: new Date(task.created_at).getTime(),
          taskId: task.id,
          optimizerType: task.config.optimizer_type,
          modelName: task.config.model_name,
          averageScore,
          improvement: results.improvement_percentage,
          metricScores
        }
      })
      .sort((a, b) => a.timestamp - b.timestamp)
  }

  const trendData = processTrendData()

  // Analyze trends
  const analyzeTrends = (): TrendAnalysis => {
    if (trendData.length < 2) {
      return {
        overallTrend: 'stable',
        trendStrength: 0,
        bestPeriod: 'N/A',
        worstPeriod: 'N/A',
        averageImprovement: 0,
        consistencyScore: 0
      }
    }

    const scores = trendData.map(d => d.averageScore)
    const improvements = trendData.map(d => d.improvement)
    
    // Calculate trend direction
    const firstHalf = scores.slice(0, Math.floor(scores.length / 2))
    const secondHalf = scores.slice(Math.floor(scores.length / 2))
    
    const firstHalfAvg = firstHalf.reduce((sum, score) => sum + score, 0) / firstHalf.length
    const secondHalfAvg = secondHalf.reduce((sum, score) => sum + score, 0) / secondHalf.length
    
    const trendDirection = secondHalfAvg > firstHalfAvg ? 'improving' : 
                          secondHalfAvg < firstHalfAvg ? 'declining' : 'stable'
    
    const trendStrength = Math.abs(secondHalfAvg - firstHalfAvg) / firstHalfAvg * 100

    // Find best and worst periods
    const bestIndex = scores.indexOf(Math.max(...scores))
    const worstIndex = scores.indexOf(Math.min(...scores))
    
    const averageImprovement = improvements.reduce((sum, imp) => sum + imp, 0) / improvements.length
    
    // Calculate consistency (lower standard deviation = higher consistency)
    const mean = scores.reduce((sum, score) => sum + score, 0) / scores.length
    const variance = scores.reduce((sum, score) => sum + Math.pow(score - mean, 2), 0) / scores.length
    const stdDev = Math.sqrt(variance)
    const consistencyScore = Math.max(0, 100 - (stdDev / mean * 100))

    return {
      overallTrend: trendDirection,
      trendStrength,
      bestPeriod: trendData[bestIndex]?.date || 'N/A',
      worstPeriod: trendData[worstIndex]?.date || 'N/A',
      averageImprovement,
      consistencyScore
    }
  }

  const trendAnalysis = analyzeTrends()

  // Group data by time period
  const groupDataByPeriod = () => {
    const grouped: Record<string, TrendDataPoint[]> = {}
    
    trendData.forEach(point => {
      const date = new Date(point.timestamp)
      let key: string
      
      switch (groupBy) {
        case 'day':
          key = date.toISOString().split('T')[0]
          break
        case 'week':
          const weekStart = new Date(date)
          weekStart.setDate(date.getDate() - date.getDay())
          key = weekStart.toISOString().split('T')[0]
          break
        case 'month':
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
          break
        default:
          key = date.toISOString().split('T')[0]
      }
      
      if (!grouped[key]) {
        grouped[key] = []
      }
      grouped[key].push(point)
    })

    return Object.entries(grouped).map(([period, points]) => ({
      period,
      count: points.length,
      averageScore: points.reduce((sum, p) => sum + p.averageScore, 0) / points.length,
      averageImprovement: points.reduce((sum, p) => sum + p.improvement, 0) / points.length,
      bestScore: Math.max(...points.map(p => p.averageScore)),
      worstScore: Math.min(...points.map(p => p.averageScore)),
      optimizerTypes: [...new Set(points.map(p => p.optimizerType))]
    })).sort((a, b) => a.period.localeCompare(b.period))
  }

  const groupedData = groupDataByPeriod()

  // Get all unique metrics
  const allMetrics = new Set<string>()
  trendData.forEach(point => {
    Object.keys(point.metricScores).forEach(metric => allMetrics.add(metric))
  })

  const renderTrendChart = () => (
    <div className="space-y-4">
      <div className="relative h-64 border rounded-lg p-4">
        <div className="absolute inset-4">
          <div className="h-full flex items-end justify-between">
            {groupedData.map((group) => (
              <div key={group.period} className="flex flex-col items-center gap-2">
                <div 
                  className="bg-primary rounded-t transition-all hover:bg-primary/80"
                  style={{ 
                    height: `${(group.averageScore / Math.max(...groupedData.map(g => g.averageScore))) * 100}%`,
                    width: '20px'
                  }}
                  title={`${group.period}: ${group.averageScore.toFixed(3)}`}
                />
                <span className="text-xs text-muted-foreground transform -rotate-45 origin-left">
                  {group.period}
                </span>
              </div>
            ))}
          </div>
          
          {/* Y-axis labels */}
          <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-muted-foreground">
            <span>{Math.max(...groupedData.map(g => g.averageScore)).toFixed(2)}</span>
            <span>{(Math.max(...groupedData.map(g => g.averageScore)) / 2).toFixed(2)}</span>
            <span>0.00</span>
          </div>
        </div>
      </div>
      
      <div className="text-center text-sm text-muted-foreground">
        Performance Over Time ({groupBy === 'day' ? 'Daily' : groupBy === 'week' ? 'Weekly' : 'Monthly'} Average)
      </div>
    </div>
  )

  const renderMetricTrends = () => {
    const selectedMetric = metricFilter === 'all' ? Array.from(allMetrics)[0] : metricFilter
    if (!selectedMetric) return null

    const metricTrendData = trendData.map(point => ({
      date: point.date,
      score: point.metricScores[selectedMetric] || 0
    }))

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium">
            {selectedMetric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Trend
          </h4>
          <Select value={metricFilter} onValueChange={setMetricFilter}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Metrics</SelectItem>
              {Array.from(allMetrics).map(metric => (
                <SelectItem key={metric} value={metric}>
                  {metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          {metricTrendData.map((point) => (
            <div key={point.date} className="flex items-center gap-4">
              <div className="w-20 text-sm text-muted-foreground">
                {point.date}
              </div>
              <div className="flex-1">
                <Progress value={point.score * 100} className="h-3" />
              </div>
              <div className="w-16 text-sm font-medium text-right">
                {point.score.toFixed(3)}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderOptimizerComparison = () => {
    const optimizerStats = tasks.reduce((acc, task) => {
      if (!task.results) return acc
      
      const type = task.config.optimizer_type
      if (!acc[type]) {
        acc[type] = {
          count: 0,
          totalImprovement: 0,
          totalScore: 0,
          bestImprovement: -Infinity,
          worstImprovement: Infinity
        }
      }
      
      acc[type].count++
      acc[type].totalImprovement += task.results.improvement_percentage
      
      const avgScore = Object.values(task.results.performance_metrics).reduce((sum, score) => sum + score, 0) / Object.keys(task.results.performance_metrics).length
      acc[type].totalScore += avgScore
      acc[type].bestImprovement = Math.max(acc[type].bestImprovement, task.results.improvement_percentage)
      acc[type].worstImprovement = Math.min(acc[type].worstImprovement, task.results.improvement_percentage)
      
      return acc
    }, {} as Record<string, any>)

    return (
      <div className="space-y-4">
        {Object.entries(optimizerStats).map(([optimizer, stats]) => (
          <Card key={optimizer}>
            <CardContent className="pt-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{optimizer.toUpperCase()}</h4>
                  <Badge variant="outline">{stats.count} experiments</Badge>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold">
                      {(stats.totalImprovement / stats.count).toFixed(1)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Avg Improvement</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-lg font-semibold">
                      {(stats.totalScore / stats.count).toFixed(3)}
                    </div>
                    <div className="text-xs text-muted-foreground">Avg Score</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">
                      +{stats.bestImprovement.toFixed(1)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Best</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-lg font-semibold text-red-600">
                      {stats.worstImprovement.toFixed(1)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Worst</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Trend Analysis Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              {trendAnalysis.overallTrend === 'improving' ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : trendAnalysis.overallTrend === 'declining' ? (
                <TrendingDown className="h-4 w-4 text-red-500" />
              ) : (
                <BarChart3 className="h-4 w-4 text-gray-500" />
              )}
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Overall Trend</p>
                <p className="text-lg font-semibold capitalize">
                  {trendAnalysis.overallTrend}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Avg Improvement</p>
                <p className="text-lg font-semibold">
                  {trendAnalysis.averageImprovement > 0 ? '+' : ''}
                  {trendAnalysis.averageImprovement.toFixed(1)}%
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
                <p className="text-sm text-muted-foreground">Consistency</p>
                <p className="text-lg font-semibold">
                  {trendAnalysis.consistencyScore.toFixed(0)}%
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
                <p className="text-sm text-muted-foreground">Experiments</p>
                <p className="text-lg font-semibold">
                  {trendData.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Analysis Controls
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Time Range</label>
              <Select value={timeRange} onValueChange={(value: '7d' | '30d' | '90d' | 'all') => setTimeRange(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                  <SelectItem value="all">All time</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Group By</label>
              <Select value={groupBy} onValueChange={(value: 'day' | 'week' | 'month') => setGroupBy(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="day">Day</SelectItem>
                  <SelectItem value="week">Week</SelectItem>
                  <SelectItem value="month">Month</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Optimizer</label>
              <Select value={optimizerFilter} onValueChange={setOptimizerFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Optimizers</SelectItem>
                  <SelectItem value="nova">Nova</SelectItem>
                  <SelectItem value="miprov2">MIPROv2</SelectItem>
                  <SelectItem value="meta-prompter">Meta Prompter</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Data Points</label>
              <div className="text-sm text-muted-foreground pt-2">
                {trendData.length} experiments
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trend Visualizations */}
      <Tabs defaultValue="timeline" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="metrics">Metric Trends</TabsTrigger>
          <TabsTrigger value="optimizers">Optimizer Comparison</TabsTrigger>
        </TabsList>
        
        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Performance Timeline
              </CardTitle>
              <CardDescription>
                Average performance scores over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              {groupedData.length > 0 ? (
                renderTrendChart()
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No data available for the selected time range
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Individual Metric Trends
              </CardTitle>
              <CardDescription>
                Track specific metrics over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              {allMetrics.size > 0 ? (
                renderMetricTrends()
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No metric data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="optimizers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Optimizer Performance Comparison
              </CardTitle>
              <CardDescription>
                Compare performance across different optimization algorithms
              </CardDescription>
            </CardHeader>
            <CardContent>
              {renderOptimizerComparison()}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
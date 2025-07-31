import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  BarChart3, 
  TrendingUp, 
  Filter,
  Search,
  Download,
  RefreshCw,
  Eye,
  ArrowUpDown,
  Target,
  Zap
} from 'lucide-react'
import { useOptimization } from '@/hooks'
import { OptimizationResults, OptimizerType } from '@/types'
import { PerformanceMetricsChart } from '@/components/optimization/OptimizationResults/PerformanceMetricsChart'
import { PromptComparisonAnalysis } from '@/components/optimization/OptimizationResults/PromptComparisonAnalysis'
import { IndividualPredictionAnalysis } from '@/components/optimization/OptimizationResults/IndividualPredictionAnalysis'
import { PerformanceTrendAnalysis } from '@/components/optimization/OptimizationResults/PerformanceTrendAnalysis'

interface ResultsAnalysisFilters {
  optimizer_type?: OptimizerType
  date_range?: [string, string]
  min_improvement?: number
  search_query?: string
}

export const ResultsAnalysis: React.FC = () => {
  const { optimizationHistory, getOptimizationHistory, isLoading } = useOptimization({ autoLoad: false })
  const [selectedResults, setSelectedResults] = useState<OptimizationResults[]>([])
  const [filters, setFilters] = useState<ResultsAnalysisFilters>({})
  const [sortBy, setSortBy] = useState<'date' | 'performance' | 'improvement'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    loadOptimizationHistory()
  }, [])

  const loadOptimizationHistory = async () => {
    try {
      await getOptimizationHistory(1, 100, {
        status: ['completed'],
        optimizer_type: filters.optimizer_type ? [filters.optimizer_type] : undefined,
        date_from: filters.date_range?.[0],
        date_to: filters.date_range?.[1]
      })
    } catch (error) {
      console.error('Failed to load optimization history:', error)
    }
  }

  const handleFilterChange = (key: keyof ResultsAnalysisFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleApplyFilters = () => {
    loadOptimizationHistory()
  }

  const handleSelectResults = (results: OptimizationResults) => {
    setSelectedResults(prev => {
      const exists = prev.find(r => r.task_id === results.task_id)
      if (exists) {
        return prev.filter(r => r.task_id !== results.task_id)
      } else {
        return [...prev, results]
      }
    })
  }

  const handleSelectAllResults = () => {
    const allResults = optimizationHistory?.items
      .filter((task: any) => task.results)
      .map((task: any) => task.results!) || []
    
    if (selectedResults.length === allResults.length) {
      setSelectedResults([])
    } else {
      setSelectedResults(allResults)
    }
  }

  const sortedTasks = optimizationHistory?.items
    .filter((task: any) => task.results)
    .sort((a: any, b: any) => {
      const aResults = a.results!
      const bResults = b.results!
      
      let comparison = 0
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'performance':
          const aAvgScore = Object.values(aResults.performance_metrics).reduce((sum: number, score: any) => sum + score, 0) / Object.keys(aResults.performance_metrics).length
          const bAvgScore = Object.values(bResults.performance_metrics).reduce((sum: number, score: any) => sum + score, 0) / Object.keys(bResults.performance_metrics).length
          comparison = aAvgScore - bAvgScore
          break
        case 'improvement':
          comparison = aResults.improvement_percentage - bResults.improvement_percentage
          break
      }
      
      return sortOrder === 'desc' ? -comparison : comparison
    }) || []

  const filteredTasks = sortedTasks.filter((task: any) => {
    if (!task.results) return false
    
    if (filters.optimizer_type && task.config.optimizer_type !== filters.optimizer_type) {
      return false
    }
    
    if (filters.min_improvement && task.results.improvement_percentage < filters.min_improvement) {
      return false
    }
    
    if (filters.search_query) {
      const query = filters.search_query.toLowerCase()
      const searchableText = [
        task.config.dataset_id,
        task.config.prompt_id,
        task.config.model_name,
        task.config.evaluation_metric
      ].join(' ').toLowerCase()
      
      if (!searchableText.includes(query)) {
        return false
      }
    }
    
    return true
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Results Analysis</h1>
          <p className="text-muted-foreground">
            Comprehensive analysis and visualization of optimization results
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadOptimizationHistory}
            disabled={isLoading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          {selectedResults.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {/* Export selected results */}}
            >
              <Download className="mr-2 h-4 w-4" />
              Export ({selectedResults.length})
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search experiments..."
                  className="pl-10"
                  value={filters.search_query || ''}
                  onChange={(e) => handleFilterChange('search_query', e.target.value)}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Optimizer Type</Label>
              <Select
                value={filters.optimizer_type || ''}
                onValueChange={(value) => handleFilterChange('optimizer_type', value || undefined)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All optimizers" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All optimizers</SelectItem>
                  <SelectItem value="nova">Nova Prompt Optimizer</SelectItem>
                  <SelectItem value="miprov2">MIPROv2</SelectItem>
                  <SelectItem value="meta-prompter">Meta Prompter</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Min Improvement (%)</Label>
              <Input
                type="number"
                placeholder="0"
                value={filters.min_improvement || ''}
                onChange={(e) => handleFilterChange('min_improvement', e.target.value ? parseFloat(e.target.value) : undefined)}
              />
            </div>
            
            <div className="space-y-2">
              <Label>Sort By</Label>
              <div className="flex gap-2">
                <Select
                  value={sortBy}
                  onValueChange={(value: 'date' | 'performance' | 'improvement') => setSortBy(value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="date">Date</SelectItem>
                    <SelectItem value="performance">Performance</SelectItem>
                    <SelectItem value="improvement">Improvement</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                >
                  <ArrowUpDown className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end mt-4">
            <Button onClick={handleApplyFilters} disabled={isLoading}>
              Apply Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Experiments</p>
                <p className="text-lg font-semibold">
                  {filteredTasks.length}
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
                  {filteredTasks.length > 0 
                    ? (filteredTasks.reduce((sum: number, task: any) => sum + task.results!.improvement_percentage, 0) / filteredTasks.length).toFixed(1)
                    : '0'
                  }%
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
                <p className="text-sm text-muted-foreground">Selected</p>
                <p className="text-lg font-semibold">
                  {selectedResults.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-orange-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Best Score</p>
                <p className="text-lg font-semibold">
                  {filteredTasks.length > 0 
                    ? Math.max(...filteredTasks.map((task: any) => 
                        Math.max(...Object.values(task.results!.performance_metrics).map((v: any) => Number(v)))
                      )).toFixed(3)
                    : '--'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analysis Interface */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="comparison">Prompt Comparison</TabsTrigger>
          <TabsTrigger value="predictions">Prediction Analysis</TabsTrigger>
          <TabsTrigger value="trends">Performance Trends</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <div className="space-y-4">
            {/* Experiment Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Optimization Experiments</span>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleSelectAllResults}
                    >
                      {selectedResults.length === filteredTasks.length ? 'Deselect All' : 'Select All'}
                    </Button>
                    <Badge variant="outline">
                      {filteredTasks.length} experiments
                    </Badge>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {filteredTasks.map((task: any) => (
                    <div
                      key={task.id}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedResults.find(r => r.task_id === task.id)
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:bg-muted/50'
                      }`}
                      onClick={() => handleSelectResults(task.results!)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">
                              {task.config.optimizer_type.toUpperCase()}
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {task.config.model_name}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Dataset: {task.config.dataset_id} • Metric: {task.config.evaluation_metric}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(task.created_at).toLocaleString()}
                          </div>
                        </div>
                        
                        <div className="text-right space-y-1">
                          <div className={`text-lg font-semibold ${
                            task.results!.improvement_percentage > 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {task.results!.improvement_percentage > 0 ? '+' : ''}
                            {task.results!.improvement_percentage.toFixed(1)}%
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Score: {Object.values(task.results!.performance_metrics)[0] ? Number(Object.values(task.results!.performance_metrics)[0]).toFixed(3) : '--'}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {filteredTasks.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No optimization experiments found matching your filters.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Performance Metrics Chart */}
            {selectedResults.length > 0 && (
              <PerformanceMetricsChart results={selectedResults} />
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="comparison" className="space-y-4">
          {selectedResults.length > 0 ? (
            <PromptComparisonAnalysis results={selectedResults} />
          ) : (
            <Card>
              <CardContent className="pt-8 pb-8 text-center">
                <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  Select optimization experiments to compare prompts
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        <TabsContent value="predictions" className="space-y-4">
          {selectedResults.length > 0 ? (
            <IndividualPredictionAnalysis results={selectedResults} />
          ) : (
            <Card>
              <CardContent className="pt-8 pb-8 text-center">
                <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  Select optimization experiments to analyze individual predictions
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        <TabsContent value="trends" className="space-y-4">
          {filteredTasks.length > 0 ? (
            <PerformanceTrendAnalysis 
              tasks={filteredTasks}
              selectedResults={selectedResults}
            />
          ) : (
            <Card>
              <CardContent className="pt-8 pb-8 text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  No data available for trend analysis
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  Target,
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  MessageSquare
} from 'lucide-react'
import { OptimizationResults, EvaluationDetail } from '@/types'

interface IndividualPredictionAnalysisProps {
  results: OptimizationResults[]
}

interface PredictionFilter {
  search?: string
  scoreRange?: [number, number]
  improvementType?: 'improved' | 'degraded' | 'unchanged' | 'all'
  sortBy?: 'score' | 'improvement' | 'input_length'
  sortOrder?: 'asc' | 'desc'
}

interface EnhancedEvaluationDetail extends EvaluationDetail {
  taskId: string
  experimentIndex: number
  scoreImprovement: number
  improvementPercentage: number
}

export const IndividualPredictionAnalysis: React.FC<IndividualPredictionAnalysisProps> = ({
  results
}) => {
  const [filters, setFilters] = useState<PredictionFilter>({
    improvementType: 'all',
    sortBy: 'improvement',
    sortOrder: 'desc'
  })
  const [selectedPrediction, setSelectedPrediction] = useState<EnhancedEvaluationDetail | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  // Combine all evaluation details from all results
  const allPredictions: EnhancedEvaluationDetail[] = results.flatMap((result, experimentIndex) =>
    result.evaluation_details.map(detail => ({
      ...detail,
      taskId: result.task_id,
      experimentIndex,
      scoreImprovement: detail.optimized_score - detail.original_score,
      improvementPercentage: ((detail.optimized_score - detail.original_score) / detail.original_score) * 100
    }))
  )

  // Apply filters
  const filteredPredictions = allPredictions.filter(prediction => {
    // Search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase()
      const searchableText = [
        prediction.input,
        prediction.expected_output,
        prediction.original_output,
        prediction.optimized_output
      ].join(' ').toLowerCase()
      
      if (!searchableText.includes(searchTerm)) {
        return false
      }
    }

    // Score range filter
    if (filters.scoreRange) {
      const [min, max] = filters.scoreRange
      if (prediction.optimized_score < min || prediction.optimized_score > max) {
        return false
      }
    }

    // Improvement type filter
    if (filters.improvementType && filters.improvementType !== 'all') {
      const improvement = prediction.scoreImprovement
      switch (filters.improvementType) {
        case 'improved':
          if (improvement <= 0.01) return false
          break
        case 'degraded':
          if (improvement >= -0.01) return false
          break
        case 'unchanged':
          if (Math.abs(improvement) > 0.01) return false
          break
      }
    }

    return true
  })

  // Sort predictions
  const sortedPredictions = [...filteredPredictions].sort((a, b) => {
    let comparison = 0
    
    switch (filters.sortBy) {
      case 'score':
        comparison = a.optimized_score - b.optimized_score
        break
      case 'improvement':
        comparison = a.scoreImprovement - b.scoreImprovement
        break
      case 'input_length':
        comparison = a.input.length - b.input.length
        break
      default:
        comparison = a.scoreImprovement - b.scoreImprovement
    }
    
    return filters.sortOrder === 'desc' ? -comparison : comparison
  })

  // Paginate results
  const totalPages = Math.ceil(sortedPredictions.length / itemsPerPage)
  const paginatedPredictions = sortedPredictions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  // Calculate statistics
  const stats = {
    total: allPredictions.length,
    improved: allPredictions.filter(p => p.scoreImprovement > 0.01).length,
    degraded: allPredictions.filter(p => p.scoreImprovement < -0.01).length,
    unchanged: allPredictions.filter(p => Math.abs(p.scoreImprovement) <= 0.01).length,
    averageImprovement: allPredictions.reduce((sum, p) => sum + p.improvementPercentage, 0) / allPredictions.length,
    bestImprovement: Math.max(...allPredictions.map(p => p.improvementPercentage)),
    worstImprovement: Math.min(...allPredictions.map(p => p.improvementPercentage))
  }

  const getScoreChangeIcon = (improvement: number) => {
    if (improvement > 0.01) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (improvement < -0.01) return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getScoreChangeColor = (improvement: number) => {
    if (improvement > 0.01) return 'text-green-600 dark:text-green-400'
    if (improvement < -0.01) return 'text-red-600 dark:text-red-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  const getImprovementBadge = (improvement: number) => {
    if (improvement > 0.01) return <Badge variant="default" className="text-xs">Improved</Badge>
    if (improvement < -0.01) return <Badge variant="destructive" className="text-xs">Degraded</Badge>
    return <Badge variant="secondary" className="text-xs">Unchanged</Badge>
  }

  const renderPredictionCard = (prediction: EnhancedEvaluationDetail, index: number) => (
    <Card 
      key={`${prediction.taskId}-${index}`}
      className={`cursor-pointer transition-colors ${
        selectedPrediction === prediction ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
      }`}
      onClick={() => setSelectedPrediction(prediction)}
    >
      <CardContent className="pt-4">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                Exp {prediction.experimentIndex + 1}
              </Badge>
              {getImprovementBadge(prediction.scoreImprovement)}
            </div>
            
            <div className="flex items-center gap-2">
              {getScoreChangeIcon(prediction.scoreImprovement)}
              <span className={`text-sm font-medium ${getScoreChangeColor(prediction.scoreImprovement)}`}>
                {prediction.improvementPercentage > 0 ? '+' : ''}
                {prediction.improvementPercentage.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Input */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Input</h4>
            <p className="text-sm bg-muted p-3 rounded overflow-hidden" style={{ 
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {prediction.input}
            </p>
          </div>

          {/* Score Comparison */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Original Score</div>
              <div className="font-medium">{prediction.original_score.toFixed(3)}</div>
            </div>
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Optimized Score</div>
              <div className="font-medium">{prediction.optimized_score.toFixed(3)}</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Performance</span>
              <span>{(prediction.optimized_score * 100).toFixed(0)}%</span>
            </div>
            <Progress value={prediction.optimized_score * 100} className="h-2" />
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderDetailedView = (prediction: EnhancedEvaluationDetail) => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Prediction Analysis</span>
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              Experiment {prediction.experimentIndex + 1}
            </Badge>
            {getImprovementBadge(prediction.scoreImprovement)}
          </div>
        </CardTitle>
        <CardDescription>
          Detailed breakdown of prediction performance and outputs
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="comparison" className="w-full">
          <TabsList>
            <TabsTrigger value="comparison">Output Comparison</TabsTrigger>
            <TabsTrigger value="metrics">Score Breakdown</TabsTrigger>
            <TabsTrigger value="insights">Analysis</TabsTrigger>
          </TabsList>
          
          <TabsContent value="comparison" className="space-y-4">
            {/* Input */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Input</h4>
              <ScrollArea className="h-24 w-full rounded-md border p-3">
                <p className="text-sm">{prediction.input}</p>
              </ScrollArea>
            </div>

            {/* Expected Output */}
            {prediction.expected_output && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Expected Output</h4>
                <ScrollArea className="h-24 w-full rounded-md border p-3 bg-blue-50 dark:bg-blue-900/20">
                  <p className="text-sm">{prediction.expected_output}</p>
                </ScrollArea>
              </div>
            )}

            {/* Output Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium">Original Output</h4>
                  <Badge variant="outline">
                    Score: {prediction.original_score.toFixed(3)}
                  </Badge>
                </div>
                <ScrollArea className="h-32 w-full rounded-md border p-3 bg-red-50 dark:bg-red-900/20">
                  <p className="text-sm">{prediction.original_output}</p>
                </ScrollArea>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium">Optimized Output</h4>
                  <Badge variant="outline">
                    Score: {prediction.optimized_score.toFixed(3)}
                  </Badge>
                </div>
                <ScrollArea className="h-32 w-full rounded-md border p-3 bg-green-50 dark:bg-green-900/20">
                  <p className="text-sm">{prediction.optimized_output}</p>
                </ScrollArea>
              </div>
            </div>

            {/* Improvement Summary */}
            <div className="flex items-center justify-center gap-2 pt-4">
              {getScoreChangeIcon(prediction.scoreImprovement)}
              <span className={`font-medium ${getScoreChangeColor(prediction.scoreImprovement)}`}>
                {prediction.improvementPercentage > 0 ? '+' : ''}
                {prediction.improvementPercentage.toFixed(1)}% change
              </span>
              <span className="text-muted-foreground">
                ({prediction.scoreImprovement > 0 ? '+' : ''}{prediction.scoreImprovement.toFixed(3)} points)
              </span>
            </div>
          </TabsContent>
          
          <TabsContent value="metrics" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(prediction.metrics).map(([metric, score]) => (
                <div key={metric} className="p-4 rounded-lg border">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium capitalize">
                      {metric.replace('_', ' ')}
                    </h4>
                    <div className="text-2xl font-bold">
                      {score.toFixed(3)}
                    </div>
                    <Progress value={score * 100} className="h-2" />
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="insights" className="space-y-4">
            <div className="space-y-4">
              <div className="p-4 rounded-lg border">
                <div className="flex items-start gap-3">
                  <Lightbulb className="h-5 w-5 text-yellow-500 mt-0.5" />
                  <div className="space-y-1">
                    <h4 className="font-medium">Key Insights</h4>
                    <p className="text-sm text-muted-foreground">
                      {prediction.scoreImprovement > 0.1 
                        ? "Significant improvement achieved through optimization. The optimized prompt produced a more accurate and relevant response."
                        : prediction.scoreImprovement > 0
                        ? "Moderate improvement observed. The optimization made subtle but meaningful enhancements to the output quality."
                        : prediction.scoreImprovement < -0.1
                        ? "Performance degradation detected. The original prompt may have been better suited for this specific input."
                        : "Minimal change in performance. Both prompts performed similarly for this input."
                      }
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-lg border">
                <div className="flex items-start gap-3">
                  <MessageSquare className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div className="space-y-1">
                    <h4 className="font-medium">Output Quality Analysis</h4>
                    <p className="text-sm text-muted-foreground">
                      The optimized output shows {prediction.optimized_output.length > prediction.original_output.length ? 'more detailed' : 'more concise'} responses 
                      with {prediction.optimized_score > prediction.original_score ? 'improved' : 'similar'} alignment to the expected outcome.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Predictions</p>
                <p className="text-lg font-semibold">{stats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Improved</p>
                <p className="text-lg font-semibold">
                  {stats.improved} ({((stats.improved / stats.total) * 100).toFixed(0)}%)
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Degraded</p>
                <p className="text-lg font-semibold">
                  {stats.degraded} ({((stats.degraded / stats.total) * 100).toFixed(0)}%)
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-purple-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Avg Improvement</p>
                <p className="text-lg font-semibold">
                  {stats.averageImprovement > 0 ? '+' : ''}{stats.averageImprovement.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
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
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search predictions..."
                  className="pl-10"
                  value={filters.search || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Improvement Type</label>
              <Select
                value={filters.improvementType}
                onValueChange={(value: 'improved' | 'degraded' | 'unchanged' | 'all') => 
                  setFilters(prev => ({ ...prev, improvementType: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="improved">Improved</SelectItem>
                  <SelectItem value="degraded">Degraded</SelectItem>
                  <SelectItem value="unchanged">Unchanged</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Sort By</label>
              <Select
                value={filters.sortBy}
                onValueChange={(value: 'score' | 'improvement' | 'input_length') => 
                  setFilters(prev => ({ ...prev, sortBy: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="improvement">Improvement</SelectItem>
                  <SelectItem value="score">Score</SelectItem>
                  <SelectItem value="input_length">Input Length</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Order</label>
              <Select
                value={filters.sortOrder}
                onValueChange={(value: 'asc' | 'desc') => 
                  setFilters(prev => ({ ...prev, sortOrder: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">Descending</SelectItem>
                  <SelectItem value="asc">Ascending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Predictions List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">
              Predictions ({filteredPredictions.length})
            </h3>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>

          <div className="space-y-3">
            {paginatedPredictions.map((prediction, index) => 
              renderPredictionCard(prediction, index)
            )}
            
            {paginatedPredictions.length === 0 && (
              <Card>
                <CardContent className="pt-8 pb-8 text-center">
                  <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    No predictions found matching your filters
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Detailed View */}
        <div className="space-y-4">
          {selectedPrediction ? (
            renderDetailedView(selectedPrediction)
          ) : (
            <Card>
              <CardContent className="pt-8 pb-8 text-center">
                <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  Select a prediction to view detailed analysis
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
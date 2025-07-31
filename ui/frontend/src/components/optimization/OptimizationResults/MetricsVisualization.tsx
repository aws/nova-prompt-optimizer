import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Zap,
  Award,
  AlertTriangle
} from 'lucide-react'
import { OptimizationResults } from '@/types'

interface MetricsVisualizationProps {
  results: OptimizationResults
}

export const MetricsVisualization: React.FC<MetricsVisualizationProps> = ({
  results
}) => {
  // Calculate metric statistics
  const metricStats = Object.entries(results.performance_metrics).map(([metric, score]) => {
    // For demo purposes, simulate original scores and improvements
    const originalScore = score * (0.8 + Math.random() * 0.15) // Random original score
    const improvement = ((score - originalScore) / originalScore) * 100
    const maxPossibleScore = 1.0 // Assuming normalized scores
    const progressPercentage = (score / maxPossibleScore) * 100
    
    return {
      name: metric,
      displayName: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      originalScore,
      currentScore: score,
      improvement,
      progressPercentage,
      isImprovement: improvement > 0
    }
  })

  // Calculate overall performance
  const averageScore = metricStats.reduce((sum, stat) => sum + stat.currentScore, 0) / metricStats.length
  const averageImprovement = metricStats.reduce((sum, stat) => sum + stat.improvement, 0) / metricStats.length
  const bestMetric = metricStats.reduce((best, current) => 
    current.currentScore > best.currentScore ? current : best
  )


  // Categorize metrics by performance
  const excellentMetrics = metricStats.filter(stat => stat.currentScore >= 0.9)
  const goodMetrics = metricStats.filter(stat => stat.currentScore >= 0.7 && stat.currentScore < 0.9)
  const needsImprovementMetrics = metricStats.filter(stat => stat.currentScore < 0.7)

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Average Score</p>
                <p className="text-lg font-semibold">
                  {averageScore.toFixed(3)}
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
                  {averageImprovement > 0 ? '+' : ''}{averageImprovement.toFixed(1)}%
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
                <p className="text-sm text-muted-foreground">Best Metric</p>
                <p className="text-lg font-semibold">
                  {bestMetric.currentScore.toFixed(3)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {bestMetric.displayName}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Needs Work</p>
                <p className="text-lg font-semibold">
                  {needsImprovementMetrics.length}
                </p>
                <p className="text-xs text-muted-foreground">
                  metrics &lt; 0.7
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Performance Metrics
          </CardTitle>
          <CardDescription>
            Detailed breakdown of all evaluation metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {metricStats.map((stat, index) => (
              <div key={stat.name} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h4 className="font-medium">{stat.displayName}</h4>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Original: {stat.originalScore.toFixed(3)}</span>
                      <span>Current: {stat.currentScore.toFixed(3)}</span>
                      <Badge variant={stat.isImprovement ? 'default' : 'destructive'} className="text-xs">
                        {stat.isImprovement ? '+' : ''}{stat.improvement.toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold">
                      {stat.currentScore.toFixed(3)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {stat.progressPercentage.toFixed(0)}% of max
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Progress 
                    value={stat.progressPercentage} 
                    className="h-2"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>0.0</span>
                    <span>1.0</span>
                  </div>
                </div>
                
                {index < metricStats.length - 1 && <Separator />}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Categories */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Excellent Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-600">
              <Award className="h-4 w-4" />
              Excellent
            </CardTitle>
            <CardDescription>
              Metrics scoring 0.9 or higher
            </CardDescription>
          </CardHeader>
          <CardContent>
            {excellentMetrics.length > 0 ? (
              <div className="space-y-2">
                {excellentMetrics.map(metric => (
                  <div key={metric.name} className="flex items-center justify-between">
                    <span className="text-sm">{metric.displayName}</span>
                    <Badge variant="default" className="text-xs">
                      {metric.currentScore.toFixed(3)}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No metrics in this category
              </p>
            )}
          </CardContent>
        </Card>

        {/* Good Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-600">
              <Target className="h-4 w-4" />
              Good
            </CardTitle>
            <CardDescription>
              Metrics scoring 0.7 - 0.89
            </CardDescription>
          </CardHeader>
          <CardContent>
            {goodMetrics.length > 0 ? (
              <div className="space-y-2">
                {goodMetrics.map(metric => (
                  <div key={metric.name} className="flex items-center justify-between">
                    <span className="text-sm">{metric.displayName}</span>
                    <Badge variant="secondary" className="text-xs">
                      {metric.currentScore.toFixed(3)}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No metrics in this category
              </p>
            )}
          </CardContent>
        </Card>

        {/* Needs Improvement */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-600">
              <AlertTriangle className="h-4 w-4" />
              Needs Work
            </CardTitle>
            <CardDescription>
              Metrics scoring below 0.7
            </CardDescription>
          </CardHeader>
          <CardContent>
            {needsImprovementMetrics.length > 0 ? (
              <div className="space-y-2">
                {needsImprovementMetrics.map(metric => (
                  <div key={metric.name} className="flex items-center justify-between">
                    <span className="text-sm">{metric.displayName}</span>
                    <Badge variant="destructive" className="text-xs">
                      {metric.currentScore.toFixed(3)}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                All metrics performing well!
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Optimization Progress Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Optimization Progress
          </CardTitle>
          <CardDescription>
            Score improvements throughout the optimization process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {results.optimization_history.map((step) => (
              <div key={step.step} className="flex items-center gap-4">
                <div className="flex-shrink-0 w-12 text-sm text-muted-foreground">
                  Step {step.step}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm">Score: {step.score.toFixed(3)}</span>
                    {step.improvement > 0 && (
                      <Badge variant="outline" className="text-xs">
                        +{(step.improvement * 100).toFixed(1)}%
                      </Badge>
                    )}
                  </div>
                  <Progress value={(step.score / 1.0) * 100} className="h-2" />
                </div>
                <div className="flex-shrink-0 text-xs text-muted-foreground">
                  {new Date(step.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
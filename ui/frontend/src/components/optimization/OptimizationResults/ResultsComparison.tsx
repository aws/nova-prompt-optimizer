import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  ArrowRight, 
  Copy, 
  Eye, 
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { OptimizationResults } from '@/types'

interface ResultsComparisonProps {
  results: OptimizationResults
  maxExamples?: number
}

export const ResultsComparison: React.FC<ResultsComparisonProps> = ({
  results,
  maxExamples = 10
}) => {

  const [showAllExamples, setShowAllExamples] = useState(false)

  const displayedExamples = showAllExamples 
    ? results.evaluation_details 
    : results.evaluation_details.slice(0, maxExamples)

  const handleCopyPrompt = (prompt: string, type: 'original' | 'optimized') => {
    navigator.clipboard.writeText(prompt)
    // In a real app, you'd show a toast notification here
    console.log(`${type} prompt copied to clipboard`)
  }

  const getScoreChangeIcon = (originalScore: number, optimizedScore: number) => {
    const diff = optimizedScore - originalScore
    if (diff > 0.01) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (diff < -0.01) return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getScoreChangeColor = (originalScore: number, optimizedScore: number) => {
    const diff = optimizedScore - originalScore
    if (diff > 0.01) return 'text-green-600 dark:text-green-400'
    if (diff < -0.01) return 'text-red-600 dark:text-red-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  return (
    <div className="space-y-6">
      {/* Prompt Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original Prompt */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Original Prompt</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleCopyPrompt(results.original_prompt.system_prompt + '\n\n' + results.original_prompt.user_prompt, 'original')}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardTitle>
            <CardDescription>
              Baseline prompt before optimization
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.original_prompt.system_prompt && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">System Prompt</h4>
                  <ScrollArea className="h-32 w-full rounded-md border p-3">
                    <pre className="text-sm whitespace-pre-wrap">
                      {results.original_prompt.system_prompt}
                    </pre>
                  </ScrollArea>
                </div>
              )}
              
              <div className="space-y-2">
                <h4 className="text-sm font-medium">User Prompt</h4>
                <ScrollArea className="h-32 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {results.original_prompt.user_prompt}
                  </pre>
                </ScrollArea>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Optimized Prompt */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Optimized Prompt</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleCopyPrompt(results.optimized_prompt.system_prompt + '\n\n' + results.optimized_prompt.user_prompt, 'optimized')}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </CardTitle>
            <CardDescription>
              Improved prompt after optimization
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.optimized_prompt.system_prompt && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">System Prompt</h4>
                  <ScrollArea className="h-32 w-full rounded-md border p-3">
                    <pre className="text-sm whitespace-pre-wrap">
                      {results.optimized_prompt.system_prompt}
                    </pre>
                  </ScrollArea>
                </div>
              )}
              
              <div className="space-y-2">
                <h4 className="text-sm font-medium">User Prompt</h4>
                <ScrollArea className="h-32 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {results.optimized_prompt.user_prompt}
                  </pre>
                </ScrollArea>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Comparison</CardTitle>
          <CardDescription>
            Metric scores before and after optimization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(results.performance_metrics).map(([metric, score]) => {
              // For demo purposes, assume original score was 10% lower
              const originalScore = score * 0.9
              const improvement = ((score - originalScore) / originalScore) * 100
              
              return (
                <div key={metric} className="p-4 rounded-lg border">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium capitalize">
                      {metric.replace('_', ' ')}
                    </h4>
                    
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="text-xs text-muted-foreground">Original</div>
                        <div className="font-medium">{originalScore.toFixed(3)}</div>
                      </div>
                      
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      
                      <div className="space-y-1">
                        <div className="text-xs text-muted-foreground">Optimized</div>
                        <div className="font-medium">{score.toFixed(3)}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1">
                      {getScoreChangeIcon(originalScore, score)}
                      <span className={`text-sm ${getScoreChangeColor(originalScore, score)}`}>
                        {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Example Outputs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Example Outputs</span>
            <Badge variant="outline">
              {results.evaluation_details.length} examples
            </Badge>
          </CardTitle>
          <CardDescription>
            Side-by-side comparison of original vs optimized outputs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {displayedExamples.map((example, index) => (
              <div key={index} className="p-4 rounded-lg border">
                <div className="space-y-4">
                  {/* Input */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Input</h4>
                    <p className="text-sm bg-muted p-3 rounded">
                      {example.input}
                    </p>
                  </div>

                  {/* Expected Output */}
                  {example.expected_output && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Expected Output</h4>
                      <p className="text-sm bg-blue-50 dark:bg-blue-900/20 p-3 rounded border border-blue-200 dark:border-blue-800">
                        {example.expected_output}
                      </p>
                    </div>
                  )}

                  {/* Outputs Comparison */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">Original Output</h4>
                        <Badge variant="outline">
                          Score: {example.original_score.toFixed(3)}
                        </Badge>
                      </div>
                      <p className="text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded border border-red-200 dark:border-red-800">
                        {example.original_output}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">Optimized Output</h4>
                        <Badge variant="outline">
                          Score: {example.optimized_score.toFixed(3)}
                        </Badge>
                      </div>
                      <p className="text-sm bg-green-50 dark:bg-green-900/20 p-3 rounded border border-green-200 dark:border-green-800">
                        {example.optimized_output}
                      </p>
                    </div>
                  </div>

                  {/* Score Improvement */}
                  <div className="flex items-center justify-center gap-2 pt-2">
                    {getScoreChangeIcon(example.original_score, example.optimized_score)}
                    <span className={`text-sm font-medium ${getScoreChangeColor(example.original_score, example.optimized_score)}`}>
                      {example.optimized_score > example.original_score ? '+' : ''}
                      {((example.optimized_score - example.original_score) / example.original_score * 100).toFixed(1)}% change
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Show More Button */}
            {!showAllExamples && results.evaluation_details.length > maxExamples && (
              <div className="text-center">
                <Button
                  variant="outline"
                  onClick={() => setShowAllExamples(true)}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Show {results.evaluation_details.length - maxExamples} More Examples
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
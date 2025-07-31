import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

import { 
  Copy, 
  ArrowRight, 
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  FileText,
  Diff,
  Lightbulb,
  Target
} from 'lucide-react'
import { OptimizationResults } from '@/types'

interface PromptComparisonAnalysisProps {
  results: OptimizationResults[]
}

interface PromptDiff {
  type: 'added' | 'removed' | 'modified'
  content: string
  line: number
}

export const PromptComparisonAnalysis: React.FC<PromptComparisonAnalysisProps> = ({
  results
}) => {
  const [selectedResult, setSelectedResult] = useState<OptimizationResults>(results[0])
  const [comparisonMode, setComparisonMode] = useState<'side-by-side' | 'diff' | 'overlay'>('side-by-side')
  const [promptType, setPromptType] = useState<'system' | 'user' | 'both'>('both')

  const handleCopyPrompt = (prompt: string, type: 'original' | 'optimized') => {
    navigator.clipboard.writeText(prompt)
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

  const calculatePromptDiff = (original: string, optimized: string): PromptDiff[] => {
    // Simple diff calculation for demonstration
    const originalLines = original.split('\n')
    const optimizedLines = optimized.split('\n')
    const diffs: PromptDiff[] = []

    // This is a simplified diff - in a real implementation you'd use a proper diff algorithm
    const maxLines = Math.max(originalLines.length, optimizedLines.length)
    
    for (let i = 0; i < maxLines; i++) {
      const originalLine = originalLines[i] || ''
      const optimizedLine = optimizedLines[i] || ''
      
      if (originalLine !== optimizedLine) {
        if (!originalLine) {
          diffs.push({ type: 'added', content: optimizedLine, line: i + 1 })
        } else if (!optimizedLine) {
          diffs.push({ type: 'removed', content: originalLine, line: i + 1 })
        } else {
          diffs.push({ type: 'modified', content: `${originalLine} → ${optimizedLine}`, line: i + 1 })
        }
      }
    }

    return diffs
  }

  const renderSideBySideComparison = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Original Prompt */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Original Prompt</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleCopyPrompt(
                (selectedResult.original_prompt.system_prompt || '') + '\n\n' + selectedResult.original_prompt.user_prompt, 
                'original'
              )}
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
            {(promptType === 'system' || promptType === 'both') && selectedResult.original_prompt.system_prompt && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">System Prompt</h4>
                <ScrollArea className="h-48 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {selectedResult.original_prompt.system_prompt}
                  </pre>
                </ScrollArea>
              </div>
            )}
            
            {(promptType === 'user' || promptType === 'both') && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">User Prompt</h4>
                <ScrollArea className="h-48 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {selectedResult.original_prompt.user_prompt}
                  </pre>
                </ScrollArea>
              </div>
            )}
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
              onClick={() => handleCopyPrompt(
                (selectedResult.optimized_prompt.system_prompt || '') + '\n\n' + selectedResult.optimized_prompt.user_prompt, 
                'optimized'
              )}
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
            {(promptType === 'system' || promptType === 'both') && selectedResult.optimized_prompt.system_prompt && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">System Prompt</h4>
                <ScrollArea className="h-48 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {selectedResult.optimized_prompt.system_prompt}
                  </pre>
                </ScrollArea>
              </div>
            )}
            
            {(promptType === 'user' || promptType === 'both') && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">User Prompt</h4>
                <ScrollArea className="h-48 w-full rounded-md border p-3">
                  <pre className="text-sm whitespace-pre-wrap">
                    {selectedResult.optimized_prompt.user_prompt}
                  </pre>
                </ScrollArea>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderDiffView = () => {
    const systemDiffs = selectedResult.original_prompt.system_prompt && selectedResult.optimized_prompt.system_prompt
      ? calculatePromptDiff(selectedResult.original_prompt.system_prompt, selectedResult.optimized_prompt.system_prompt)
      : []
    
    const userDiffs = calculatePromptDiff(
      selectedResult.original_prompt.user_prompt, 
      selectedResult.optimized_prompt.user_prompt
    )

    return (
      <div className="space-y-6">
        {(promptType === 'system' || promptType === 'both') && systemDiffs.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Diff className="h-5 w-5" />
                System Prompt Changes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {systemDiffs.map((diff, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border-l-4 ${
                      diff.type === 'added' 
                        ? 'bg-green-50 dark:bg-green-900/20 border-l-green-500'
                        : diff.type === 'removed'
                        ? 'bg-red-50 dark:bg-red-900/20 border-l-red-500'
                        : 'bg-yellow-50 dark:bg-yellow-900/20 border-l-yellow-500'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="text-xs">
                        Line {diff.line}
                      </Badge>
                      <Badge variant={
                        diff.type === 'added' ? 'default' : 
                        diff.type === 'removed' ? 'destructive' : 'secondary'
                      } className="text-xs">
                        {diff.type}
                      </Badge>
                    </div>
                    <pre className="text-sm whitespace-pre-wrap">
                      {diff.content}
                    </pre>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {(promptType === 'user' || promptType === 'both') && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Diff className="h-5 w-5" />
                User Prompt Changes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {userDiffs.length > 0 ? (
                  userDiffs.map((diff, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border-l-4 ${
                        diff.type === 'added' 
                          ? 'bg-green-50 dark:bg-green-900/20 border-l-green-500'
                          : diff.type === 'removed'
                          ? 'bg-red-50 dark:bg-red-900/20 border-l-red-500'
                          : 'bg-yellow-50 dark:bg-yellow-900/20 border-l-yellow-500'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs">
                          Line {diff.line}
                        </Badge>
                        <Badge variant={
                          diff.type === 'added' ? 'default' : 
                          diff.type === 'removed' ? 'destructive' : 'secondary'
                        } className="text-xs">
                          {diff.type}
                        </Badge>
                      </div>
                      <pre className="text-sm whitespace-pre-wrap">
                        {diff.content}
                      </pre>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No changes detected in user prompt
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  const renderKeyInsights = () => {
    const insights = [
      {
        type: 'improvement',
        title: 'Performance Improvement',
        description: `${selectedResult.improvement_percentage.toFixed(1)}% improvement in overall performance`,
        icon: <TrendingUp className="h-4 w-4 text-green-500" />
      },
      {
        type: 'structure',
        title: 'Structural Changes',
        description: 'Optimized prompt structure for better clarity and instruction following',
        icon: <FileText className="h-4 w-4 text-blue-500" />
      },
      {
        type: 'specificity',
        title: 'Increased Specificity',
        description: 'Added more specific instructions and examples for better guidance',
        icon: <Target className="h-4 w-4 text-purple-500" />
      },
      {
        type: 'optimization',
        title: 'Optimization Strategy',
        description: 'Applied systematic prompt engineering techniques for enhanced performance',
        icon: <Lightbulb className="h-4 w-4 text-yellow-500" />
      }
    ]

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {insights.map((insight, index) => (
          <Card key={index}>
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                {insight.icon}
                <div className="space-y-1">
                  <h4 className="font-medium">{insight.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {insight.description}
                  </p>
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
      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Prompt Comparison Analysis</CardTitle>
          <CardDescription>
            Detailed comparison of original vs optimized prompts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Experiment</label>
              <Select
                value={selectedResult.task_id}
                onValueChange={(taskId) => {
                  const result = results.find(r => r.task_id === taskId)
                  if (result) setSelectedResult(result)
                }}
              >
                <SelectTrigger className="w-64">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {results.map((result, index) => (
                    <SelectItem key={result.task_id} value={result.task_id}>
                      Experiment {index + 1} ({result.improvement_percentage.toFixed(1)}% improvement)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">View</label>
              <Select
                value={comparisonMode}
                onValueChange={(value: 'side-by-side' | 'diff' | 'overlay') => setComparisonMode(value)}
              >
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="side-by-side">Side by Side</SelectItem>
                  <SelectItem value="diff">Diff View</SelectItem>
                  <SelectItem value="overlay">Overlay</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Prompt Type</label>
              <Select
                value={promptType}
                onValueChange={(value: 'system' | 'user' | 'both') => setPromptType(value)}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="both">Both</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Impact</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(selectedResult.performance_metrics).map(([metric, score]) => {
              const originalScore = score * 0.9 // Demo calculation
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

      {/* Main Comparison View */}
      <Tabs defaultValue="comparison" className="w-full">
        <TabsList>
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="insights">Key Insights</TabsTrigger>
        </TabsList>
        
        <TabsContent value="comparison" className="space-y-4">
          {comparisonMode === 'side-by-side' && renderSideBySideComparison()}
          {comparisonMode === 'diff' && renderDiffView()}
          {comparisonMode === 'overlay' && (
            <Card>
              <CardContent className="pt-8 pb-8 text-center">
                <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  Overlay view coming soon
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        <TabsContent value="insights" className="space-y-4">
          {renderKeyInsights()}
        </TabsContent>
      </Tabs>
    </div>
  )
}
import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
// import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Eye, 
  EyeOff, 
  Copy,
  CheckCircle
} from 'lucide-react'
import { OptimizationResults } from '@/types/optimization'

interface ResultViewerProps {
  result: OptimizationResults
}

export const ResultViewer: React.FC<ResultViewerProps> = ({ result }) => {
  const [showDetails, setShowDetails] = useState(false)
  const [copiedText, setCopiedText] = useState<string | null>(null)

  const handleCopy = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (error) {
      console.error('Failed to copy text:', error)
    }
  }

  const getImprovementIcon = (improvement: number) => {
    if (improvement > 0) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (improvement < 0) return <TrendingDown className="h-4 w-4 text-red-500" />
    return <Minus className="h-4 w-4 text-gray-500" />
  }

  const getImprovementColor = (improvement: number) => {
    if (improvement > 0) return 'text-green-600'
    if (improvement < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <div className="space-y-4">
      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Performance Summary</CardTitle>
            <Badge 
              variant={result.improvement_percentage > 0 ? 'default' : 'secondary'}
              className="flex items-center gap-1"
            >
              {getImprovementIcon(result.improvement_percentage)}
              {result.improvement_percentage > 0 ? '+' : ''}{result.improvement_percentage.toFixed(1)}%
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(result.performance_metrics).map(([metric, value]) => (
              <div key={metric} className="text-center">
                <div className="text-2xl font-bold">{value.toFixed(3)}</div>
                <div className="text-sm text-muted-foreground capitalize">
                  {metric.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Prompt Comparison */}
      <Tabs defaultValue="comparison" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="original">Original</TabsTrigger>
          <TabsTrigger value="optimized">Optimized</TabsTrigger>
        </TabsList>

        <TabsContent value="comparison" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Original Prompt */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center justify-between">
                  Original Prompt
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(
                      `${result.original_prompt.system_prompt}\n\n${result.original_prompt.user_prompt}`,
                      'original'
                    )}
                  >
                    {copiedText === 'original' ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48">
                  <div className="space-y-2 text-sm">
                    {result.original_prompt.system_prompt && (
                      <div>
                        <Badge variant="outline" className="mb-2">System</Badge>
                        <p className="whitespace-pre-wrap font-mono text-xs bg-muted p-2 rounded">
                          {result.original_prompt.system_prompt}
                        </p>
                      </div>
                    )}
                    <div>
                      <Badge variant="outline" className="mb-2">User</Badge>
                      <p className="whitespace-pre-wrap font-mono text-xs bg-muted p-2 rounded">
                        {result.original_prompt.user_prompt}
                      </p>
                    </div>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Optimized Prompt */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center justify-between">
                  Optimized Prompt
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(
                      `${result.optimized_prompt.system_prompt}\n\n${result.optimized_prompt.user_prompt}`,
                      'optimized'
                    )}
                  >
                    {copiedText === 'optimized' ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48">
                  <div className="space-y-2 text-sm">
                    {result.optimized_prompt.system_prompt && (
                      <div>
                        <Badge variant="outline" className="mb-2">System</Badge>
                        <p className="whitespace-pre-wrap font-mono text-xs bg-muted p-2 rounded">
                          {result.optimized_prompt.system_prompt}
                        </p>
                      </div>
                    )}
                    <div>
                      <Badge variant="outline" className="mb-2">User</Badge>
                      <p className="whitespace-pre-wrap font-mono text-xs bg-muted p-2 rounded">
                        {result.optimized_prompt.user_prompt}
                      </p>
                    </div>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="original">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Original Prompt
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(
                    `${result.original_prompt.system_prompt}\n\n${result.original_prompt.user_prompt}`,
                    'original-full'
                  )}
                >
                  {copiedText === 'original-full' ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.original_prompt.system_prompt && (
                  <div>
                    <Badge variant="outline" className="mb-2">System Prompt</Badge>
                    <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded">
                      {result.original_prompt.system_prompt}
                    </div>
                  </div>
                )}
                <div>
                  <Badge variant="outline" className="mb-2">User Prompt</Badge>
                  <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded">
                    {result.original_prompt.user_prompt}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimized">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Optimized Prompt
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(
                    `${result.optimized_prompt.system_prompt}\n\n${result.optimized_prompt.user_prompt}`,
                    'optimized-full'
                  )}
                >
                  {copiedText === 'optimized-full' ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.optimized_prompt.system_prompt && (
                  <div>
                    <Badge variant="outline" className="mb-2">System Prompt</Badge>
                    <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded">
                      {result.optimized_prompt.system_prompt}
                    </div>
                  </div>
                )}
                <div>
                  <Badge variant="outline" className="mb-2">User Prompt</Badge>
                  <div className="whitespace-pre-wrap font-mono text-sm bg-muted p-4 rounded">
                    {result.optimized_prompt.user_prompt}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Detailed Results Toggle */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Sample Outputs</h4>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowDetails(!showDetails)}
        >
          {showDetails ? (
            <>
              <EyeOff className="mr-2 h-4 w-4" />
              Hide Details
            </>
          ) : (
            <>
              <Eye className="mr-2 h-4 w-4" />
              Show Details
            </>
          )}
        </Button>
      </div>

      {/* Sample Evaluation Details */}
      {showDetails && (
        <div className="space-y-4">
          {result.evaluation_details.slice(0, 3).map((detail, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-sm">Sample {index + 1}</CardTitle>
                <CardDescription className="text-xs">
                  Original: {detail.original_score.toFixed(3)} → 
                  Optimized: {detail.optimized_score.toFixed(3)}
                  <span className={`ml-2 ${getImprovementColor(detail.optimized_score - detail.original_score)}`}>
                    ({detail.optimized_score > detail.original_score ? '+' : ''}
                    {(detail.optimized_score - detail.original_score).toFixed(3)})
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Badge variant="outline" className="mb-1">Input</Badge>
                  <p className="text-xs bg-muted p-2 rounded">{detail.input}</p>
                </div>
                <div>
                  <Badge variant="outline" className="mb-1">Expected</Badge>
                  <p className="text-xs bg-muted p-2 rounded">{detail.expected_output}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <Badge variant="outline" className="mb-1">Original Output</Badge>
                    <p className="text-xs bg-muted p-2 rounded">{detail.original_output}</p>
                  </div>
                  <div>
                    <Badge variant="outline" className="mb-1">Optimized Output</Badge>
                    <p className="text-xs bg-muted p-2 rounded">{detail.optimized_output}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
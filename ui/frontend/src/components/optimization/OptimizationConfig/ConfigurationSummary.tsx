import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Database, FileText, Zap, Settings, Clock, Target } from 'lucide-react'
import { Dataset, Prompt, OptimizationConfig, ModelInfo, OptimizerType } from '@/types'

interface ConfigurationSummaryProps {
  dataset?: Dataset
  prompt?: Prompt
  config: Partial<OptimizationConfig>
  models?: ModelInfo[]
  optimizers?: Record<OptimizerType, any>
}

export const ConfigurationSummary: React.FC<ConfigurationSummaryProps> = ({
  dataset,
  prompt,
  config,
  models = [],
  optimizers = {}
}) => {
  const selectedModel = models.find(m => m.name === config.model_name)
  const selectedOptimizer = config.optimizer_type ? optimizers[config.optimizer_type] : null

  const estimateRuntime = () => {
    if (!config.max_iterations) return 'Unknown'
    
    const baseTime = 2 // minutes per iteration
    const iterations = config.max_iterations
    const totalMinutes = baseTime * iterations
    
    if (totalMinutes < 60) {
      return `~${totalMinutes} minutes`
    } else {
      const hours = Math.floor(totalMinutes / 60)
      const minutes = totalMinutes % 60
      return `~${hours}h ${minutes}m`
    }
  }

  const getCompletionStatus = () => {
    const required = [dataset, prompt, config.optimizer_type, config.model_name, config.evaluation_metric]
    const completed = required.filter(Boolean).length
    return { completed, total: required.length }
  }

  const { completed, total } = getCompletionStatus()
  const isComplete = completed === total

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Configuration Summary
        </CardTitle>
        <CardDescription>
          Review your optimization setup
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Completion Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Configuration Progress</span>
          <Badge variant={isComplete ? 'default' : 'secondary'}>
            {completed}/{total} Complete
          </Badge>
        </div>

        <Separator />

        {/* Dataset */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Dataset</span>
          </div>
          {dataset ? (
            <div className="ml-6 space-y-1">
              <div className="font-medium">{dataset.name}</div>
              <div className="text-sm text-muted-foreground">
                {dataset.row_count?.toLocaleString()} rows • {dataset.input_columns?.join(', ')} → {dataset.output_columns?.join(', ')}
              </div>
            </div>
          ) : (
            <div className="ml-6 text-sm text-muted-foreground">
              No dataset selected
            </div>
          )}
        </div>

        {/* Prompt */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Prompt</span>
          </div>
          {prompt ? (
            <div className="ml-6 space-y-1">
              <div className="font-medium">{prompt.name}</div>
              <div className="text-sm text-muted-foreground">
                {prompt.variables?.length ? `${prompt.variables.length} variables` : 'No variables'}
              </div>
            </div>
          ) : (
            <div className="ml-6 text-sm text-muted-foreground">
              No prompt selected
            </div>
          )}
        </div>

        <Separator />

        {/* Optimizer */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Optimizer</span>
          </div>
          {config.optimizer_type ? (
            <div className="ml-6 space-y-1">
              <div className="font-medium capitalize">
                {config.optimizer_type.replace('-', ' ')}
              </div>
              {selectedOptimizer?.description && (
                <div className="text-sm text-muted-foreground">
                  {selectedOptimizer.description}
                </div>
              )}
            </div>
          ) : (
            <div className="ml-6 text-sm text-muted-foreground">
              No optimizer selected
            </div>
          )}
        </div>

        {/* Model */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Model</span>
          </div>
          {selectedModel ? (
            <div className="ml-6 space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">{selectedModel.name}</span>
                <Badge variant="outline" className="text-xs">
                  {selectedModel.provider}
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground">
                {selectedModel.max_tokens.toLocaleString()} tokens • 
                {selectedModel.supports_system_prompt ? ' System prompt supported' : ' User prompt only'}
              </div>
            </div>
          ) : (
            <div className="ml-6 text-sm text-muted-foreground">
              No model selected
            </div>
          )}
        </div>

        <Separator />

        {/* Parameters */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Settings className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Parameters</span>
          </div>
          <div className="ml-6 space-y-2">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Max Iterations:</span>
                <div className="font-medium">{config.max_iterations || 'Not set'}</div>
              </div>
              <div>
                <span className="text-muted-foreground">Evaluation:</span>
                <div className="font-medium capitalize">
                  {config.evaluation_metric?.replace('_', ' ') || 'Not set'}
                </div>
              </div>
            </div>

            {config.parameters && Object.keys(config.parameters).length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">Advanced Parameters:</div>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(config.parameters).map(([key, value]) => (
                    <Badge key={key} variant="outline" className="text-xs">
                      {key}: {typeof value === 'number' ? value.toFixed(2) : String(value)}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {config.custom_metrics && config.custom_metrics.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">Custom Metrics:</div>
                <div className="flex flex-wrap gap-1">
                  {config.custom_metrics.map((metric, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {metric}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <Separator />

        {/* Estimated Runtime */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Estimated Runtime</span>
          </div>
          <div className="ml-6">
            <div className="font-medium">{estimateRuntime()}</div>
            <div className="text-sm text-muted-foreground">
              Based on {config.max_iterations || 0} iterations
            </div>
          </div>
        </div>

        {/* Warnings */}
        {!isComplete && (
          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              Complete all required fields to start optimization.
            </p>
          </div>
        )}

        {config.max_iterations && config.max_iterations > 20 && (
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>Note:</strong> High iteration counts may take significant time to complete.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
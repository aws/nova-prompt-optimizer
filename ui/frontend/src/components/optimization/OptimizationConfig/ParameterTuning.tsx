import React from 'react'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { HelpCircle } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { OptimizationConfig, OptimizerType } from '@/types'

interface ParameterTuningProps {
  config: Partial<OptimizationConfig>
  optimizerType?: OptimizerType
  onChange: (updates: Partial<OptimizationConfig>) => void
  disabled?: boolean
}

const EVALUATION_METRICS = [
  { value: 'accuracy', label: 'Accuracy', description: 'Overall correctness of responses' },
  { value: 'f1_score', label: 'F1 Score', description: 'Harmonic mean of precision and recall' },
  { value: 'bleu', label: 'BLEU Score', description: 'Text similarity metric' },
  { value: 'rouge', label: 'ROUGE Score', description: 'Recall-oriented text similarity' },
  { value: 'semantic_similarity', label: 'Semantic Similarity', description: 'Meaning-based similarity' },
  { value: 'custom', label: 'Custom Metric', description: 'Use your own evaluation metric' }
]

interface ParameterConfig {
  min: number
  max: number
  step: number
  default: number | boolean
  description: string
}

const OPTIMIZER_PARAMETERS: Record<OptimizerType, Record<string, ParameterConfig>> = {
  nova: {
    temperature: { min: 0, max: 2, step: 0.1, default: 0.7, description: 'Controls randomness in generation' },
    top_p: { min: 0, max: 1, step: 0.05, default: 0.9, description: 'Nucleus sampling parameter' },
    meta_prompt_iterations: { min: 1, max: 5, step: 1, default: 3, description: 'Number of meta-prompting iterations' },
    few_shot_examples: { min: 0, max: 20, step: 1, default: 5, description: 'Number of few-shot examples to use' }
  },
  miprov2: {
    temperature: { min: 0, max: 2, step: 0.1, default: 0.7, description: 'Controls randomness in generation' },
    top_p: { min: 0, max: 1, step: 0.05, default: 0.9, description: 'Nucleus sampling parameter' },
    num_candidates: { min: 1, max: 10, step: 1, default: 5, description: 'Number of candidate prompts to generate' },
    bootstrap_examples: { min: 5, max: 50, step: 5, default: 20, description: 'Number of bootstrap examples' }
  },
  'meta-prompter': {
    temperature: { min: 0, max: 2, step: 0.1, default: 0.7, description: 'Controls randomness in generation' },
    learning_rate: { min: 0.001, max: 0.1, step: 0.001, default: 0.01, description: 'Meta-learning rate' },
    adaptation_steps: { min: 1, max: 10, step: 1, default: 5, description: 'Number of adaptation steps' }
  }
}

export const ParameterTuning: React.FC<ParameterTuningProps> = ({
  config,
  optimizerType,
  onChange,
  disabled = false
}) => {
  const handleBasicParameterChange = (field: keyof OptimizationConfig, value: any) => {
    onChange({ [field]: value })
  }

  const handleAdvancedParameterChange = (paramName: string, value: any) => {
    const currentParams = config.parameters || {}
    onChange({
      parameters: {
        ...currentParams,
        [paramName]: value
      }
    })
  }

  const optimizerParams = optimizerType ? OPTIMIZER_PARAMETERS[optimizerType] : {}

  return (
    <div className="space-y-6">
      {/* Basic Parameters */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="max-iterations">Max Iterations</Label>
          <div className="space-y-2">
            <Slider
              id="max-iterations"
              min={1}
              max={50}
              step={1}
              value={[config.max_iterations || 10]}
              onValueChange={([value]) => handleBasicParameterChange('max_iterations', value)}
              disabled={disabled}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>1</span>
              <span className="font-medium">{config.max_iterations || 10} iterations</span>
              <span>50</span>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Number of optimization iterations to perform. More iterations may improve results but take longer.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="evaluation-metric">Evaluation Metric</Label>
          <Select
            value={config.evaluation_metric}
            onValueChange={(value) => handleBasicParameterChange('evaluation_metric', value)}
            disabled={disabled}
          >
            <SelectTrigger id="evaluation-metric">
              <SelectValue placeholder="Select evaluation metric" />
            </SelectTrigger>
            <SelectContent>
              {EVALUATION_METRICS.map((metric) => (
                <SelectItem key={metric.value} value={metric.value}>
                  <div className="space-y-1">
                    <div className="font-medium">{metric.label}</div>
                    <div className="text-sm text-muted-foreground">{metric.description}</div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {config.evaluation_metric === 'custom' && (
          <div className="space-y-2">
            <Label htmlFor="custom-metrics">Custom Metrics</Label>
            <Textarea
              id="custom-metrics"
              placeholder="Enter custom metric names, one per line"
              value={config.custom_metrics?.join('\n') || ''}
              onChange={(e) => {
                const metrics = e.target.value.split('\n').filter(m => m.trim())
                handleBasicParameterChange('custom_metrics', metrics)
              }}
              disabled={disabled}
              rows={3}
            />
            <p className="text-sm text-muted-foreground">
              List the names of custom metrics you've defined in the Metric Workbench.
            </p>
          </div>
        )}
      </div>

      <Separator />

      {/* Advanced Parameters */}
      {optimizerType && Object.keys(optimizerParams).length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <h4 className="font-medium">Advanced Parameters</h4>
            <Badge variant="outline" className="text-xs">
              {optimizerType.toUpperCase()}
            </Badge>
          </div>

          <div className="grid gap-4">
            {Object.entries(optimizerParams).map(([paramName, paramConfig]) => {
              const currentValue = config.parameters?.[paramName] ?? paramConfig.default
              
              return (
                <div key={paramName} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor={paramName} className="capitalize">
                      {paramName.replace(/_/g, ' ')}
                    </Label>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="max-w-xs">{paramConfig.description}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>

                  {typeof paramConfig.default === 'boolean' ? (
                    <div className="flex items-center space-x-2">
                      <Switch
                        id={paramName}
                        checked={currentValue}
                        onCheckedChange={(checked) => handleAdvancedParameterChange(paramName, checked)}
                        disabled={disabled}
                      />
                      <Label htmlFor={paramName} className="text-sm text-muted-foreground">
                        {currentValue ? 'Enabled' : 'Disabled'}
                      </Label>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Slider
                        id={paramName}
                        min={paramConfig.min}
                        max={paramConfig.max}
                        step={paramConfig.step}
                        value={[currentValue]}
                        onValueChange={([value]) => handleAdvancedParameterChange(paramName, value)}
                        disabled={disabled}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{paramConfig.min}</span>
                        <span className="font-medium">{currentValue}</span>
                        <span>{paramConfig.max}</span>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Parameter Presets */}
      <Card className="border-muted">
        <CardHeader>
          <CardTitle className="text-sm">Parameter Presets</CardTitle>
          <CardDescription className="text-xs">
            Quick configurations for common use cases
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            <button
              className="p-2 text-xs border rounded hover:bg-muted transition-colors disabled:opacity-50"
              onClick={() => {
                const fastPreset = {
                  max_iterations: 5,
                  parameters: {
                    temperature: 0.3,
                    top_p: 0.8,
                    ...(optimizerType === 'nova' && { meta_prompt_iterations: 2, few_shot_examples: 3 }),
                    ...(optimizerType === 'miprov2' && { num_candidates: 3, bootstrap_examples: 10 })
                  }
                }
                onChange(fastPreset)
              }}
              disabled={disabled}
            >
              <div className="font-medium">Fast</div>
              <div className="text-muted-foreground">Quick results</div>
            </button>

            <button
              className="p-2 text-xs border rounded hover:bg-muted transition-colors disabled:opacity-50"
              onClick={() => {
                const balancedPreset = {
                  max_iterations: 10,
                  parameters: {
                    temperature: 0.7,
                    top_p: 0.9,
                    ...(optimizerType === 'nova' && { meta_prompt_iterations: 3, few_shot_examples: 5 }),
                    ...(optimizerType === 'miprov2' && { num_candidates: 5, bootstrap_examples: 20 })
                  }
                }
                onChange(balancedPreset)
              }}
              disabled={disabled}
            >
              <div className="font-medium">Balanced</div>
              <div className="text-muted-foreground">Good trade-off</div>
            </button>

            <button
              className="p-2 text-xs border rounded hover:bg-muted transition-colors disabled:opacity-50"
              onClick={() => {
                const thoroughPreset = {
                  max_iterations: 20,
                  parameters: {
                    temperature: 0.8,
                    top_p: 0.95,
                    ...(optimizerType === 'nova' && { meta_prompt_iterations: 5, few_shot_examples: 10 }),
                    ...(optimizerType === 'miprov2' && { num_candidates: 8, bootstrap_examples: 40 })
                  }
                }
                onChange(thoroughPreset)
              }}
              disabled={disabled}
            >
              <div className="font-medium">Thorough</div>
              <div className="text-muted-foreground">Best quality</div>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
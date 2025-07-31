import React from 'react'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Cpu, Zap, Gauge } from 'lucide-react'
import { ModelInfo, OptimizerType } from '@/types'

interface ModelSelectorProps {
  value?: string
  models?: ModelInfo[]
  optimizerType?: OptimizerType
  onChange: (model: string) => void
  disabled?: boolean
}

const getModelIcon = (provider: string) => {
  switch (provider.toLowerCase()) {
    case 'amazon':
      return Zap
    case 'anthropic':
      return Cpu
    default:
      return Gauge
  }
}

const getModelBadgeVariant = (name: string) => {
  if (name.toLowerCase().includes('nova')) {
    return 'default'
  }
  if (name.toLowerCase().includes('pro') || name.toLowerCase().includes('large')) {
    return 'secondary'
  }
  return 'outline'
}

const isModelRecommended = (model: ModelInfo, optimizerType?: OptimizerType) => {
  // Nova models are recommended for Nova optimizer
  if (optimizerType === 'nova' && model.name.toLowerCase().includes('nova')) {
    return true
  }
  
  // High-capability models are generally recommended
  if (model.max_tokens >= 100000 || model.name.toLowerCase().includes('pro')) {
    return true
  }
  
  return false
}

const filterModelsForOptimizer = (models: ModelInfo[], optimizerType?: OptimizerType) => {
  if (!optimizerType) return models
  
  // All models are compatible with all optimizers for now
  // In the future, we might filter based on specific requirements
  return models
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  value,
  models = [],
  optimizerType,
  onChange,
  disabled = false
}) => {
  const filteredModels = filterModelsForOptimizer(models, optimizerType)
  const selectedModel = filteredModels.find(model => model.name === value)

  const handleChange = (newValue: string) => {
    onChange(newValue)
  }

  return (
    <div className="space-y-3">
      <Label htmlFor="model-select">Model</Label>
      
      <Select
        value={value}
        onValueChange={handleChange}
        disabled={disabled}
      >
        <SelectTrigger id="model-select">
          <SelectValue placeholder="Select a model" />
        </SelectTrigger>
        <SelectContent>
          {filteredModels.map((model) => {
            const Icon = getModelIcon(model.provider)
            const isRecommended = isModelRecommended(model, optimizerType)
            
            return (
              <SelectItem key={model.name} value={model.name}>
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <span>{model.name}</span>
                  <Badge variant={getModelBadgeVariant(model.name)} className="text-xs">
                    {model.provider}
                  </Badge>
                  {isRecommended && (
                    <Badge variant="secondary" className="text-xs">
                      Recommended
                    </Badge>
                  )}
                </div>
              </SelectItem>
            )
          })}
        </SelectContent>
      </Select>

      {/* Model Details */}
      {selectedModel && (
        <Card className="border-muted">
          <CardContent className="pt-4">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                {React.createElement(getModelIcon(selectedModel.provider), {
                  className: "h-5 w-5 mt-0.5 text-primary"
                })}
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{selectedModel.name}</h4>
                    <Badge variant={getModelBadgeVariant(selectedModel.name)} className="text-xs">
                      {selectedModel.provider}
                    </Badge>
                    {isModelRecommended(selectedModel, optimizerType) && (
                      <Badge variant="secondary" className="text-xs">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {selectedModel.description}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Max Tokens:</span>
                  <div className="font-medium">
                    {selectedModel.max_tokens.toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-muted-foreground">System Prompt:</span>
                  <div className="font-medium">
                    {selectedModel.supports_system_prompt ? 'Supported' : 'Not Supported'}
                  </div>
                </div>
              </div>

              {/* Compatibility Warning */}
              {optimizerType && !selectedModel.supports_system_prompt && (
                <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    <strong>Note:</strong> This model doesn't support system prompts. 
                    The optimizer will combine system and user prompts into a single user prompt.
                  </p>
                </div>
              )}

              {/* Performance Hint */}
              {selectedModel.max_tokens < 50000 && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    <strong>Tip:</strong> For complex optimization tasks, consider using a model with higher token limits.
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Models Available */}
      {filteredModels.length === 0 && (
        <Card className="border-muted">
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground text-center">
              No models available for the selected optimizer.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
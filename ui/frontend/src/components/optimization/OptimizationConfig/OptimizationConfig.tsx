import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Play, Settings, AlertCircle } from 'lucide-react'
import { OptimizerSelector } from './OptimizerSelector'
import { ModelSelector } from './ModelSelector'
import { ParameterTuning } from './ParameterTuning'
import { ConfigurationSummary } from './ConfigurationSummary'
import { 
  OptimizationConfig as OptimizationConfigType,
  Dataset,
  Prompt
} from '@/types'
import { useOptimization } from '@/hooks'

interface OptimizationConfigProps {
  dataset?: Dataset
  prompt?: Prompt
  onStart: (config: OptimizationConfigType) => void
  onConfigChange?: (config: Partial<OptimizationConfigType>) => void
  disabled?: boolean
}

export const OptimizationConfig: React.FC<OptimizationConfigProps> = ({
  dataset,
  prompt,
  onStart,
  onConfigChange,
  disabled = false
}) => {
  const { models, optimizers, loadModels, loadOptimizers } = useOptimization({ autoLoad: false })
  
  const [config, setConfig] = useState<Partial<OptimizationConfigType>>({
    optimizer_type: 'nova',
    model_name: '',
    max_iterations: 10,
    evaluation_metric: 'accuracy',
    parameters: {}
  })
  
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // Load models and optimizers on mount
  useEffect(() => {
    loadModels()
    loadOptimizers()
  }, [loadModels, loadOptimizers])

  // Update config when dataset or prompt changes
  useEffect(() => {
    if (dataset && prompt) {
      const updatedConfig = {
        ...config,
        dataset_id: dataset.id,
        prompt_id: prompt.id
      }
      setConfig(updatedConfig)
      onConfigChange?.(updatedConfig)
    }
  }, [dataset, prompt])

  // Handle configuration changes
  const handleConfigChange = (updates: Partial<OptimizationConfigType>) => {
    const updatedConfig = { ...config, ...updates }
    setConfig(updatedConfig)
    onConfigChange?.(updatedConfig)
    
    // Clear validation errors when config changes
    if (validationErrors.length > 0) {
      validateConfiguration(updatedConfig)
    }
  }

  // Validate configuration
  const validateConfiguration = (configToValidate = config): string[] => {
    const errors: string[] = []

    if (!dataset) {
      errors.push('Please select a dataset')
    }

    if (!prompt) {
      errors.push('Please select a prompt')
    }

    if (!configToValidate.optimizer_type) {
      errors.push('Please select an optimizer type')
    }

    if (!configToValidate.model_name) {
      errors.push('Please select a model')
    }

    if (!configToValidate.evaluation_metric) {
      errors.push('Please select an evaluation metric')
    }

    if (configToValidate.max_iterations && (configToValidate.max_iterations < 1 || configToValidate.max_iterations > 100)) {
      errors.push('Max iterations must be between 1 and 100')
    }

    setValidationErrors(errors)
    return errors
  }

  // Handle start optimization
  const handleStart = () => {
    const errors = validateConfiguration()
    
    if (errors.length > 0) {
      return
    }

    if (!dataset || !prompt) {
      return
    }

    const fullConfig: OptimizationConfigType = {
      dataset_id: dataset.id,
      prompt_id: prompt.id,
      optimizer_type: config.optimizer_type!,
      model_name: config.model_name!,
      max_iterations: config.max_iterations!,
      evaluation_metric: config.evaluation_metric!,
      custom_metrics: config.custom_metrics || [],
      parameters: config.parameters || {}
    }

    onStart(fullConfig)
  }

  const isValid = validationErrors.length === 0 && dataset && prompt && config.optimizer_type && config.model_name
  const isLoading = models.loading === 'loading' || optimizers.loading === 'loading'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="h-6 w-6" />
          Optimization Configuration
        </h2>
        <p className="text-muted-foreground">
          Configure your optimization parameters and start the process
        </p>
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              <p className="font-medium">Please fix the following issues:</p>
              <ul className="list-disc list-inside space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index} className="text-sm">{error}</li>
                ))}
              </ul>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Optimizer Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Optimizer Configuration</CardTitle>
              <CardDescription>
                Choose the optimization algorithm and model
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <OptimizerSelector
                value={config.optimizer_type}
                optimizers={optimizers.data || undefined}
                onChange={(optimizer_type) => handleConfigChange({ optimizer_type })}
                disabled={disabled || isLoading}
              />
              
              <ModelSelector
                value={config.model_name}
                models={models.data || undefined}
                optimizerType={config.optimizer_type}
                onChange={(model_name) => handleConfigChange({ model_name })}
                disabled={disabled || isLoading}
              />
            </CardContent>
          </Card>

          {/* Parameter Tuning */}
          <Card>
            <CardHeader>
              <CardTitle>Optimization Parameters</CardTitle>
              <CardDescription>
                Fine-tune the optimization process
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ParameterTuning
                config={config}
                optimizerType={config.optimizer_type}
                onChange={handleConfigChange}
                disabled={disabled || isLoading}
              />
            </CardContent>
          </Card>
        </div>

        {/* Summary Panel */}
        <div className="space-y-6">
          <ConfigurationSummary
            dataset={dataset}
            prompt={prompt}
            config={config}
            models={models.data || undefined}
            optimizers={optimizers.data || undefined}
          />

          {/* Start Button */}
          <Card>
            <CardContent className="pt-6">
              <Button
                onClick={handleStart}
                disabled={!isValid || disabled || isLoading}
                className="w-full"
                size="lg"
              >
                <Play className="mr-2 h-4 w-4" />
                Start Optimization
              </Button>
              
              {!isValid && (
                <p className="text-sm text-muted-foreground mt-2 text-center">
                  Complete the configuration to start optimization
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
import { BaseEntity } from './common'
import { Prompt } from './prompt'

export type OptimizerType = 'nova' | 'miprov2' | 'meta-prompter'
export type OptimizationStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface OptimizationConfig {
  dataset_id: string
  prompt_id: string
  optimizer_type: OptimizerType
  model_name: string
  max_iterations: number
  evaluation_metric: string
  custom_metrics?: string[]
  parameters: Record<string, any>
}

export interface OptimizationTask extends BaseEntity {
  config: OptimizationConfig
  status: OptimizationStatus
  progress: number
  current_step: string
  total_steps: number
  start_time: string
  end_time?: string
  error_message?: string
  results?: OptimizationResults
}

export interface OptimizationResults {
  task_id: string
  original_prompt: Prompt
  optimized_prompt: Prompt
  performance_metrics: Record<string, number>
  improvement_percentage: number
  evaluation_details: EvaluationDetail[]
  optimization_history: OptimizationStep[]
}

export interface EvaluationDetail {
  input: string
  expected_output: string
  original_output: string
  optimized_output: string
  original_score: number
  optimized_score: number
  metrics: Record<string, number>
}

export interface OptimizationStep {
  step: number
  prompt_version: string
  score: number
  improvement: number
  timestamp: string
}

export interface ModelInfo {
  name: string
  provider: string
  description: string
  max_tokens: number
  supports_system_prompt: boolean
}

export interface OptimizationHistory {
  tasks: OptimizationTask[]
  total: number
  filters: {
    status: OptimizationStatus[]
    optimizer_type: OptimizerType[]
    date_range: [string, string]
  }
}
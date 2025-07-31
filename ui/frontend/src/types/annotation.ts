import { BaseEntity } from './common'
import { OptimizationResults } from './optimization'

export interface EvaluationRubric extends BaseEntity {
  name: string
  description: string
  dimensions: RubricDimension[]
  scoring_scale: ScoringScale
  dataset_id: string
  generated_by_ai: boolean
}

export interface RubricDimension {
  id: string
  name: string
  description: string
  weight: number
  criteria: RubricCriteria[]
}

export interface RubricCriteria {
  score: number
  description: string
  examples?: string[]
}

export interface ScoringScale {
  min_score: number
  max_score: number
  scale_type: 'numeric' | 'categorical'
  labels?: string[]
}

export interface Annotation extends BaseEntity {
  task_id: string
  annotator_id: string
  result_id: string
  rubric_id: string
  scores: Record<string, number>
  comments: string
  confidence: number
  time_spent: number
}

export interface AnnotationTask extends BaseEntity {
  name: string
  description: string
  rubric_id: string
  results: OptimizationResults[]
  assigned_annotators: string[]
  status: 'pending' | 'in_progress' | 'completed'
  deadline?: string
}

export interface AnnotationConflict {
  result_id: string
  annotations: Annotation[]
  disagreement_score: number
  conflicting_dimensions: string[]
  resolution_status: 'pending' | 'resolved'
  resolution?: AnnotationResolution
}

export interface AnnotationResolution {
  resolved_by: string
  resolution_method: 'consensus' | 'expert_decision' | 'majority_vote'
  final_scores: Record<string, number>
  rationale: string
  timestamp: string
}

export interface AgreementMetrics {
  overall_agreement: number
  dimension_agreement: Record<string, number>
  annotator_consistency: Record<string, number>
  conflicts: AnnotationConflict[]
}

export interface AnnotationStats {
  total_annotations: number
  completed_annotations: number
  pending_annotations: number
  average_agreement: number
  annotator_performance: Record<string, number>
}
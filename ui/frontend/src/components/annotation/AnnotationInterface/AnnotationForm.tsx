import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Save, AlertCircle } from 'lucide-react'
import { EvaluationRubric, Annotation } from '@/types/annotation'

interface AnnotationFormProps {
  rubric: EvaluationRubric
  existingAnnotation?: Annotation
  onSubmit: (scores: Record<string, number>, comments: string, confidence: number) => void
  isSubmitting: boolean
}

export const AnnotationForm: React.FC<AnnotationFormProps> = ({
  rubric,
  existingAnnotation,
  onSubmit,
  isSubmitting
}) => {
  const [scores, setScores] = useState<Record<string, number>>({})
  const [comments, setComments] = useState('')
  const [confidence, setConfidence] = useState(5)
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (existingAnnotation) {
      setScores(existingAnnotation.scores)
      setComments(existingAnnotation.comments)
      setConfidence(existingAnnotation.confidence)
    } else {
      // Initialize with default scores
      const defaultScores: Record<string, number> = {}
      rubric.dimensions.forEach(dimension => {
        defaultScores[dimension.id] = Math.floor((rubric.scoring_scale.min_score + rubric.scoring_scale.max_score) / 2)
      })
      setScores(defaultScores)
      setComments('')
      setConfidence(5)
    }
  }, [rubric, existingAnnotation])

  const handleScoreChange = (dimensionId: string, value: number[]) => {
    setScores(prev => ({
      ...prev,
      [dimensionId]: value[0]
    }))
    
    // Clear error for this dimension
    if (errors[dimensionId]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[dimensionId]
        return newErrors
      })
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Check all dimensions have scores
    rubric.dimensions.forEach(dimension => {
      if (scores[dimension.id] === undefined || scores[dimension.id] === null) {
        newErrors[dimension.id] = 'Score is required'
      }
    })

    // Check confidence is set
    if (confidence < 1 || confidence > 10) {
      newErrors.confidence = 'Confidence must be between 1 and 10'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = () => {
    if (!validateForm()) {
      return
    }

    onSubmit(scores, comments, confidence)
  }

  const getScoreLabel = (dimension: any, score: number) => {
    const criteria = dimension.criteria.find((c: any) => c.score === score)
    return criteria ? criteria.description : `Score ${score}`
  }

  const calculateWeightedScore = () => {
    let totalWeightedScore = 0
    let totalWeight = 0

    rubric.dimensions.forEach(dimension => {
      const score = scores[dimension.id]
      if (score !== undefined) {
        totalWeightedScore += score * dimension.weight
        totalWeight += dimension.weight
      }
    })

    return totalWeight > 0 ? totalWeightedScore / totalWeight : 0
  }

  const isFormComplete = rubric.dimensions.every(dimension => 
    scores[dimension.id] !== undefined && scores[dimension.id] !== null
  )

  return (
    <div className="space-y-6">
      {/* Overall Score Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Overall Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold">
              {calculateWeightedScore().toFixed(1)}
            </span>
            <Badge variant={isFormComplete ? 'default' : 'secondary'}>
              {isFormComplete ? 'Complete' : 'In Progress'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Dimension Scoring */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Evaluation Dimensions</h3>
        
        {rubric.dimensions.map((dimension) => (
          <Card key={dimension.id} className={errors[dimension.id] ? 'border-red-500' : ''}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{dimension.name}</CardTitle>
                <Badge variant="outline">Weight: {dimension.weight}</Badge>
              </div>
              <CardDescription>{dimension.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Score</Label>
                  <span className="text-sm font-medium">
                    {scores[dimension.id] || rubric.scoring_scale.min_score}
                  </span>
                </div>
                
                <Slider
                  value={[scores[dimension.id] || rubric.scoring_scale.min_score]}
                  onValueChange={(value) => handleScoreChange(dimension.id, value)}
                  min={rubric.scoring_scale.min_score}
                  max={rubric.scoring_scale.max_score}
                  step={1}
                  className="w-full"
                />
                
                <div className="text-xs text-muted-foreground">
                  {getScoreLabel(dimension, scores[dimension.id] || rubric.scoring_scale.min_score)}
                </div>
              </div>

              {errors[dimension.id] && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{errors[dimension.id]}</AlertDescription>
                </Alert>
              )}

              {/* Criteria Reference */}
              <div className="space-y-1">
                <Label className="text-xs">Scoring Guide:</Label>
                <div className="grid grid-cols-1 gap-1 text-xs">
                  {dimension.criteria.map((criteria) => (
                    <div 
                      key={criteria.score}
                      className={`p-2 rounded ${
                        scores[dimension.id] === criteria.score 
                          ? 'bg-primary/10 border border-primary/20' 
                          : 'bg-muted/50'
                      }`}
                    >
                      <span className="font-medium">{criteria.score}:</span> {criteria.description}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Separator />

      {/* Comments Section */}
      <div className="space-y-2">
        <Label htmlFor="comments">Additional Comments</Label>
        <Textarea
          id="comments"
          placeholder="Provide any additional feedback or observations about this result..."
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          rows={4}
        />
      </div>

      {/* Confidence Rating */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>Confidence in Evaluation</Label>
          <span className="text-sm font-medium">{confidence}/10</span>
        </div>
        <Slider
          value={[confidence]}
          onValueChange={(value) => setConfidence(value[0])}
          min={1}
          max={10}
          step={1}
          className="w-full"
        />
        <div className="text-xs text-muted-foreground">
          How confident are you in your evaluation of this result?
        </div>
        {errors.confidence && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{errors.confidence}</AlertDescription>
          </Alert>
        )}
      </div>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={!isFormComplete || isSubmitting}
        className="w-full"
        size="lg"
      >
        <Save className="mr-2 h-4 w-4" />
        {isSubmitting ? 'Submitting...' : existingAnnotation ? 'Update Annotation' : 'Submit Annotation'}
      </Button>

      {!isFormComplete && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Please provide scores for all evaluation dimensions before submitting.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}